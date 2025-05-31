"""
Real-time validation widgets for the Moveworks YAML Assistant.

This module provides enhanced input widgets with immediate validation feedback,
building upon the existing validation infrastructure to provide comprehensive
real-time user experience improvements.
"""

import re
from typing import Optional, List, Dict, Any, Callable
from PySide6.QtWidgets import (
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QWidget, QHBoxLayout,
    QLabel, QToolTip, QCompleter, QFrame
)
from PySide6.QtCore import Signal, QTimer, Qt, QPoint
from PySide6.QtGui import QValidator, QPalette, QFont

from dsl_validator import dsl_validator, is_dsl_expression
from mw_actions_catalog import MW_ACTIONS_CATALOG


class ValidationState:
    """Constants for validation states."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"
    NEUTRAL = "neutral"


class EnhancedValidationMixin:
    """Mixin class providing enhanced validation capabilities to input widgets."""

    def __init__(self):
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._perform_validation)
        self.validation_state = ValidationState.NEUTRAL
        self.validation_message = ""
        self.validation_callback = None
        self.debounce_delay = 300  # ms

    def set_validation_callback(self, callback: Callable[[str], tuple]):
        """Set the validation callback function that returns (is_valid, message, suggestions)."""
        self.validation_callback = callback

    def _trigger_validation(self):
        """Trigger validation with debouncing."""
        self.validation_timer.stop()
        self.validation_timer.start(self.debounce_delay)

    def _perform_validation(self):
        """Perform the actual validation."""
        if not self.validation_callback:
            return

        try:
            value = self.text() if hasattr(self, 'text') else str(self.currentText() if hasattr(self, 'currentText') else self.value())
            is_valid, message, suggestions = self.validation_callback(value)

            if is_valid:
                self._set_validation_state(ValidationState.VALID, message)
            else:
                self._set_validation_state(ValidationState.INVALID, message)

        except Exception as e:
            self._set_validation_state(ValidationState.INVALID, f"Validation error: {str(e)}")

    def _set_validation_state(self, state: str, message: str):
        """Set the validation state and update UI."""
        self.validation_state = state
        self.validation_message = message
        self._update_validation_ui()

    def _update_validation_ui(self):
        """Update the UI based on validation state."""
        colors = {
            ValidationState.VALID: "#4caf50",
            ValidationState.INVALID: "#f44336",
            ValidationState.WARNING: "#ff9800",
            ValidationState.PENDING: "#2196f3",
            ValidationState.NEUTRAL: "#e0e0e0"
        }

        border_color = colors.get(self.validation_state, colors[ValidationState.NEUTRAL])

        if self.validation_state == ValidationState.INVALID:
            background_color = "#ffebee"
        elif self.validation_state == ValidationState.WARNING:
            background_color = "#fff3e0"
        elif self.validation_state == ValidationState.VALID:
            background_color = "#e8f5e8"
        else:
            background_color = "white"

        self.setStyleSheet(f"""
            border: 2px solid {border_color};
            border-radius: 4px;
            padding: 4px;
            background-color: {background_color};
        """)

        # Set tooltip with validation message
        if self.validation_message:
            self.setToolTip(self.validation_message)


class ValidatedLineEdit(QLineEdit, EnhancedValidationMixin):
    """Enhanced QLineEdit with real-time validation."""

    validation_changed = Signal(str, str, str)  # state, message, value

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        EnhancedValidationMixin.__init__(self)
        self.textChanged.connect(self._trigger_validation)
        self.editingFinished.connect(self._perform_validation)

    def _set_validation_state(self, state: str, message: str):
        """Override to emit validation changed signal."""
        super()._set_validation_state(state, message)
        self.validation_changed.emit(state, message, self.text())


class SnakeCaseLineEdit(ValidatedLineEdit):
    """Line edit that validates snake_case naming conventions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_validation_callback(self._validate_snake_case)
        self.setPlaceholderText("use_lowercase_snake_case")

    def _validate_snake_case(self, value: str) -> tuple:
        """Validate snake_case naming convention."""
        if not value.strip():
            return True, "Field name required", []

        # Check for snake_case pattern
        snake_case_pattern = r'^[a-z][a-z0-9_]*$'

        if re.match(snake_case_pattern, value):
            return True, "✓ Valid snake_case format", []

        # Provide specific feedback
        issues = []
        suggestions = []

        if value[0].isupper():
            issues.append("starts with uppercase letter")
            suggestions.append(f"Change to: {value.lower()}")

        if ' ' in value:
            issues.append("contains spaces")
            suggestions.append(f"Change to: {value.replace(' ', '_').lower()}")

        if '-' in value:
            issues.append("contains hyphens")
            suggestions.append(f"Change to: {value.replace('-', '_').lower()}")

        if re.search(r'[A-Z]', value):
            issues.append("contains uppercase letters")
            # Convert camelCase to snake_case
            snake_case = re.sub(r'([A-Z])', r'_\1', value).lower().lstrip('_')
            suggestions.append(f"Change to: {snake_case}")

        if not issues:
            issues.append("invalid format")
            suggestions.append("Use lowercase letters, numbers, and underscores only")

        message = f"Invalid snake_case: {', '.join(issues)}"
        return False, message, suggestions


class NumericRangeEdit(ValidatedLineEdit):
    """Line edit that validates numeric values within a specified range."""

    def __init__(self, min_value: int = 0, max_value: int = 4294967295, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.set_validation_callback(self._validate_numeric_range)
        self.setPlaceholderText(f"Enter number ({min_value}-{max_value})")

    def _validate_numeric_range(self, value: str) -> tuple:
        """Validate numeric value within range."""
        if not value.strip():
            return True, "Optional numeric value", []

        try:
            num_value = int(value)

            if self.min_value <= num_value <= self.max_value:
                return True, f"✓ Valid number: {num_value}", []
            else:
                message = f"Number must be between {self.min_value} and {self.max_value}"
                suggestions = [
                    f"Minimum value: {self.min_value}",
                    f"Maximum value: {self.max_value}"
                ]
                return False, message, suggestions

        except ValueError:
            return False, "Invalid number format", ["Enter a valid integer"]


class BooleanComboBox(QComboBox, EnhancedValidationMixin):
    """ComboBox for boolean values with validation."""

    validation_changed = Signal(str, str, str)  # state, message, value

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        EnhancedValidationMixin.__init__(self)

        # Add boolean options
        self.addItems(["", "true", "false"])
        self.setEditable(True)

        self.currentTextChanged.connect(self._trigger_validation)
        self.set_validation_callback(self._validate_boolean)

    def _validate_boolean(self, value: str) -> tuple:
        """Validate boolean value."""
        if not value.strip():
            return True, "Optional boolean value", []

        value_lower = value.lower().strip()
        valid_true = ["true", "yes", "1", "on", "enabled"]
        valid_false = ["false", "no", "0", "off", "disabled"]

        if value_lower in valid_true:
            return True, f"✓ Boolean true value: {value}", []
        elif value_lower in valid_false:
            return True, f"✓ Boolean false value: {value}", []
        else:
            suggestions = [
                "Valid true values: true, yes, 1",
                "Valid false values: false, no, 0"
            ]
            return False, f"Invalid boolean value: {value}", suggestions

    def _set_validation_state(self, state: str, message: str):
        """Override to emit validation changed signal."""
        super()._set_validation_state(state, message)
        self.validation_changed.emit(state, message, self.currentText())


class ActionNameComboBox(QComboBox, EnhancedValidationMixin):
    """ComboBox for action names with auto-completion and validation."""

    validation_changed = Signal(str, str, str)  # state, message, value

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        EnhancedValidationMixin.__init__(self)

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        # Populate with known actions
        self._populate_actions()

        self.currentTextChanged.connect(self._trigger_validation)
        self.set_validation_callback(self._validate_action_name)

    def _populate_actions(self):
        """Populate with actions from MW_ACTIONS_CATALOG."""
        self.addItem("")  # Empty option

        # Add all known actions
        for action in MW_ACTIONS_CATALOG:
            self.addItem(action.action_name)

        # Set up auto-completion
        action_names = [self.itemText(i) for i in range(1, self.count())]
        completer = QCompleter(action_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(completer)

    def _validate_action_name(self, value: str) -> tuple:
        """Validate action name."""
        if not value.strip():
            return True, "Action name required", []

        # Check if it's a known action
        known_actions = [action.action_name for action in MW_ACTIONS_CATALOG]

        if value in known_actions:
            return True, f"✓ Known Moveworks action: {value}", []

        # Check for similar actions (typo detection)
        similar_actions = [action for action in known_actions if value.lower() in action.lower()]

        if similar_actions:
            suggestions = [f"Did you mean: {action}" for action in similar_actions[:3]]
            return False, f"Unknown action: {value}", suggestions
        else:
            return False, f"Unknown action: {value}", ["Check action name spelling", "Browse available actions"]

    def _set_validation_state(self, state: str, message: str):
        """Override to emit validation changed signal."""
        super()._set_validation_state(state, message)
        self.validation_changed.emit(state, message, self.currentText())


class DSLExpressionEdit(ValidatedLineEdit):
    """Line edit specifically for DSL expressions with enhanced validation."""

    def __init__(self, field_context: str = "", parent=None):
        super().__init__(parent)
        self.field_context = field_context
        self.set_validation_callback(self._validate_dsl_expression)
        self._setup_dsl_placeholder()

    def _setup_dsl_placeholder(self):
        """Set context-appropriate placeholder."""
        placeholders = {
            "condition": "Enter DSL condition (e.g., data.status == 'active')",
            "input_arg": "Enter DSL expression (e.g., data.user_info.email)",
            "output_mapper": "Enter DSL transformation (e.g., $CONCAT([data.first, data.last]))",
            "iterator": "Enter DSL array expression (e.g., data.items)"
        }

        placeholder = placeholders.get(self.field_context, "Enter DSL expression")
        self.setPlaceholderText(placeholder)

    def _validate_dsl_expression(self, value: str) -> tuple:
        """Validate DSL expression using the DSL validator."""
        if not value.strip():
            return True, "Optional DSL expression", []

        # Check if it looks like a DSL expression
        if not is_dsl_expression(value):
            # Might be a regular value
            return True, "Regular value (not DSL)", []

        # Validate using DSL validator
        result = dsl_validator.validate_dsl_expression(value)

        if result.is_valid:
            if result.warnings:
                warning_msg = "; ".join(result.warnings[:2])
                return True, f"✓ Valid DSL with warnings: {warning_msg}", result.suggestions
            else:
                return True, "✓ Valid DSL expression", result.suggestions
        else:
            error_msg = "; ".join(result.errors[:2])
            return False, f"Invalid DSL: {error_msg}", result.suggestions


class TimeUnitComboBox(QComboBox, EnhancedValidationMixin):
    """ComboBox for time units with validation."""

    validation_changed = Signal(str, str, str)  # state, message, value

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        EnhancedValidationMixin.__init__(self)

        # Add time unit options
        self.addItems(["", "seconds", "minutes"])
        self.setEditable(True)

        self.currentTextChanged.connect(self._trigger_validation)
        self.set_validation_callback(self._validate_time_unit)

    def _validate_time_unit(self, value: str) -> tuple:
        """Validate time unit."""
        if not value.strip():
            return True, "Optional time unit", []

        valid_units = ["seconds", "minutes", "hours", "days"]

        if value.lower() in valid_units:
            return True, f"✓ Valid time unit: {value}", []
        else:
            suggestions = [f"Valid units: {', '.join(valid_units)}"]
            return False, f"Invalid time unit: {value}", suggestions

    def _set_validation_state(self, state: str, message: str):
        """Override to emit validation changed signal."""
        super()._set_validation_state(state, message)
        self.validation_changed.emit(state, message, self.currentText())


class ValidationIndicator(QLabel):
    """Visual indicator for validation status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #ccc; border-radius: 10px; background-color: #f5f5f5;")
        self.set_state(ValidationState.NEUTRAL)

    def set_state(self, state: str, message: str = ""):
        """Set the validation state and update appearance."""
        icons = {
            ValidationState.VALID: "✓",
            ValidationState.INVALID: "✗",
            ValidationState.WARNING: "⚠",
            ValidationState.PENDING: "⏳",
            ValidationState.NEUTRAL: ""
        }

        colors = {
            ValidationState.VALID: "#4caf50",
            ValidationState.INVALID: "#f44336",
            ValidationState.WARNING: "#ff9800",
            ValidationState.PENDING: "#2196f3",
            ValidationState.NEUTRAL: "#e0e0e0"
        }

        self.setText(icons.get(state, ""))
        color = colors.get(state, colors[ValidationState.NEUTRAL])

        self.setStyleSheet(f"""
            border: 1px solid {color};
            border-radius: 10px;
            background-color: {color}20;
            color: {color};
            font-weight: bold;
        """)

        if message:
            self.setToolTip(message)


class ValidatedInputGroup(QWidget):
    """Widget that combines an input widget with a validation indicator."""

    validation_changed = Signal(str, str, str)  # state, message, value

    def __init__(self, input_widget, label_text: str = "", parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        self.validation_indicator = ValidationIndicator()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label_text:
            label = QLabel(label_text)
            label.setMinimumWidth(100)
            layout.addWidget(label)

        layout.addWidget(input_widget, 1)
        layout.addWidget(self.validation_indicator)

        # Connect validation signals
        if hasattr(input_widget, 'validation_changed'):
            input_widget.validation_changed.connect(self._on_validation_changed)

    def _on_validation_changed(self, state: str, message: str, value: str):
        """Handle validation changes from the input widget."""
        self.validation_indicator.set_state(state, message)
        self.validation_changed.emit(state, message, value)

    def get_value(self):
        """Get the current value from the input widget."""
        if hasattr(self.input_widget, 'text'):
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'currentText'):
            return self.input_widget.currentText()
        elif hasattr(self.input_widget, 'value'):
            return self.input_widget.value()
        return ""

    def set_value(self, value):
        """Set the value in the input widget."""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value))
        elif hasattr(self.input_widget, 'setCurrentText'):
            self.input_widget.setCurrentText(str(value))
        elif hasattr(self.input_widget, 'setValue'):
            self.input_widget.setValue(value)
