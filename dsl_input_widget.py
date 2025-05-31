"""
Enhanced DSL Input Widget for Moveworks DSL expressions.

This widget provides specialized input handling for DSL expressions with:
- Clear DSL context indicators
- Real-time validation
- DSL builder integration
- Auto-completion suggestions
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QFrame, QToolButton, QMenu, QCompleter,
    QTextEdit, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Signal, Qt, QStringListModel
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QAction
from typing import List, Optional

from dsl_validator import dsl_validator, is_dsl_expression
from dsl_builder_widget import DSLBuilderWidget


class DSLInputWidget(QWidget):
    """
    Enhanced input widget for DSL expressions with validation and builder integration.

    Features:
    - Clear DSL context indication
    - Real-time validation
    - DSL builder button
    - Auto-completion
    - Visual feedback
    """

    value_changed = Signal(str)  # Emitted when the DSL value changes
    validation_changed = Signal(bool, list)  # Emitted when validation status changes

    def __init__(self, field_name: str = "", placeholder: str = "", parent=None):
        super().__init__(parent)
        self.field_name = field_name
        self.placeholder = placeholder or f"Enter DSL expression for '{field_name}'"
        self._setup_ui()
        self._setup_auto_completion()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the DSL input widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # DSL indicator label
        self.dsl_indicator = QLabel("DSL:")
        self.dsl_indicator.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 4px 8px;
                border: 1px solid #bbdefb;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        self.dsl_indicator.setToolTip("This field expects a Moveworks DSL expression")
        layout.addWidget(self.dsl_indicator)

        # Main input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(self.placeholder)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                background-color: white;
            }
            QLineEdit[validation_status="valid"] {
                border-color: #4caf50;
            }
            QLineEdit[validation_status="invalid"] {
                border-color: #f44336;
            }
            QLineEdit[validation_status="warning"] {
                border-color: #ff9800;
            }
        """)
        layout.addWidget(self.input_field)

        # DSL builder button
        self.builder_btn = QToolButton()
        self.builder_btn.setText("🔧")
        self.builder_btn.setToolTip("Open DSL Builder")
        self.builder_btn.setStyleSheet("""
            QToolButton {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.builder_btn.clicked.connect(self._open_dsl_builder)
        layout.addWidget(self.builder_btn)

        # Quick templates button
        self.templates_btn = QToolButton()
        self.templates_btn.setText("📋")
        self.templates_btn.setToolTip("Quick DSL Templates")
        self.templates_btn.setStyleSheet(self.builder_btn.styleSheet())
        self.templates_btn.setPopupMode(QToolButton.InstantPopup)
        self._setup_templates_menu()
        layout.addWidget(self.templates_btn)

        # Validation indicator
        self.validation_indicator = QLabel()
        self.validation_indicator.setFixedSize(16, 16)
        self.validation_indicator.setStyleSheet("border: none;")
        layout.addWidget(self.validation_indicator)

        # Set stretch factors
        layout.setStretchFactor(self.input_field, 1)

    def _setup_auto_completion(self):
        """Set up auto-completion for common DSL patterns."""
        common_patterns = [
            "data.",
            "meta_info.user.email",
            "meta_info.user.name",
            "meta_info.user.id",
            "$CONCAT([",
            "$IF(",
            "$SPLIT(",
            "$TEXT(",
            "$UPPER(",
            "$LOWER(",
            "== ",
            "!= ",
            ">= ",
            "<= ",
            "&& ",
            "|| ",
        ]

        self.completer = QCompleter(common_patterns)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.input_field.setCompleter(self.completer)

    def _setup_templates_menu(self):
        """Set up the quick templates menu."""
        menu = QMenu(self)

        # Common templates
        templates = [
            ("Data Field", "data.field_name"),
            ("User Email", "meta_info.user.email"),
            ("User Name", "meta_info.user.name"),
            ("Concatenate", "$CONCAT([data.first, ' ', data.last])"),
            ("Conditional", "$IF(data.condition, 'true_value', 'false_value')"),
            ("Equal Check", "data.field == 'value'"),
            ("Not Null", "data.field != null"),
            ("Greater Than", "data.number >= 18"),
        ]

        for name, template in templates:
            action = QAction(f"{name}: {template}", self)
            action.triggered.connect(lambda checked, t=template: self._insert_template(t))
            menu.addAction(action)

        self.templates_btn.setMenu(menu)

    def _connect_signals(self):
        """Connect widget signals."""
        self.input_field.textChanged.connect(self._on_text_changed)
        self.input_field.editingFinished.connect(self._on_editing_finished)

    def _on_text_changed(self, text: str):
        """Handle text changes with real-time validation."""
        # Emit value change
        self.value_changed.emit(text)

        # Perform real-time validation
        if text.strip():
            self._validate_expression(text)
        else:
            self._clear_validation()

    def _on_editing_finished(self):
        """Handle when editing is finished."""
        text = self.input_field.text().strip()
        if text:
            self._validate_expression(text)

    def _validate_expression(self, expression: str):
        """Validate the DSL expression and update UI."""
        if not expression:
            self._clear_validation()
            return

        # Check if it looks like a DSL expression
        if not is_dsl_expression(expression):
            # Might be a regular value
            self._set_validation_status("neutral", "This appears to be a regular value, not a DSL expression")
            self.validation_changed.emit(True, [])
            return

        # Validate DSL expression
        result = dsl_validator.validate_dsl_expression(expression)

        if result.is_valid:
            if result.warnings:
                self._set_validation_status("warning", f"Valid with warnings: {'; '.join(result.warnings[:2])}")
                self.validation_changed.emit(True, result.warnings)
            else:
                self._set_validation_status("valid", "Valid DSL expression")
                self.validation_changed.emit(True, [])
        else:
            error_msg = '; '.join(result.errors[:2])
            self._set_validation_status("invalid", f"Invalid: {error_msg}")
            self.validation_changed.emit(False, result.errors)

    def _set_validation_status(self, status: str, tooltip: str):
        """Set the validation status and update UI."""
        self.input_field.setProperty("validation_status", status)
        self.input_field.style().polish(self.input_field)

        # Update validation indicator
        if status == "valid":
            self.validation_indicator.setText("✅")
            self.validation_indicator.setStyleSheet("color: #4caf50;")
        elif status == "invalid":
            self.validation_indicator.setText("❌")
            self.validation_indicator.setStyleSheet("color: #f44336;")
        elif status == "warning":
            self.validation_indicator.setText("⚠️")
            self.validation_indicator.setStyleSheet("color: #ff9800;")
        else:  # neutral
            self.validation_indicator.setText("ℹ️")
            self.validation_indicator.setStyleSheet("color: #2196f3;")

        self.validation_indicator.setToolTip(tooltip)

    def _clear_validation(self):
        """Clear validation status."""
        self.input_field.setProperty("validation_status", "")
        self.input_field.style().polish(self.input_field)
        self.validation_indicator.setText("")
        self.validation_indicator.setToolTip("")

    def _insert_template(self, template: str):
        """Insert a template into the input field."""
        current_text = self.input_field.text()
        if current_text.strip():
            # Replace selection or append
            cursor_pos = self.input_field.cursorPosition()
            new_text = current_text[:cursor_pos] + template + current_text[cursor_pos:]
            self.input_field.setText(new_text)
        else:
            self.input_field.setText(template)

        self.input_field.setFocus()

    def _open_dsl_builder(self):
        """Open the DSL builder dialog."""
        dialog = DSLBuilderDialog(self.input_field.text(), self)
        if dialog.exec() == QDialog.Accepted:
            expression = dialog.get_expression()
            if expression:
                self.input_field.setText(expression)
                self._validate_expression(expression)

    def set_value(self, value: str):
        """Set the input value."""
        self.input_field.setText(value)
        if value:
            self._validate_expression(value)

    def get_value(self) -> str:
        """Get the current input value."""
        return self.input_field.text()

    def set_field_context(self, field_name: str, field_type: str = ""):
        """Set the field context for better DSL suggestions."""
        self.field_name = field_name

        # Update placeholder based on field type
        if field_type == "condition":
            self.input_field.setPlaceholderText(f"Enter DSL expression for condition (e.g., data.status == 'active')")
        elif field_type == "output_mapper":
            self.input_field.setPlaceholderText(f"Enter DSL expression to transform output (e.g., data.result.value)")
        elif field_type == "iterator":
            self.input_field.setPlaceholderText(f"Enter DSL expression for array iteration (e.g., data.items)")
        else:
            self.input_field.setPlaceholderText(f"Enter DSL expression for '{field_name}'")


class DSLBuilderDialog(QDialog):
    """Dialog wrapper for the DSL builder widget."""

    def __init__(self, initial_expression: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("DSL Expression Builder")
        self.setModal(True)
        self.resize(800, 600)
        self._setup_ui(initial_expression)

    def _setup_ui(self, initial_expression: str):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # DSL builder widget
        self.builder_widget = DSLBuilderWidget()
        if initial_expression:
            self.builder_widget.set_expression(initial_expression)
        layout.addWidget(self.builder_widget)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect builder signal
        self.builder_widget.expression_built.connect(self.accept)

    def get_expression(self) -> str:
        """Get the built expression."""
        return self.builder_widget.get_expression()
