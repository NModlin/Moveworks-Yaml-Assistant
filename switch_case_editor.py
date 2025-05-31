"""
Switch Case Editor Dialog for the Moveworks YAML Assistant.

This module provides a comprehensive dialog for creating and editing switch cases
with DSL condition builder and step management functionality.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QGroupBox, QFormLayout, QListWidget, QListWidgetItem,
    QMessageBox, QSplitter, QTabWidget, QWidget, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List, Optional

from core_structures import SwitchCase, DefaultCase, ActionStep, ScriptStep
from dsl_builder_widget import DSLBuilderWidget
from dsl_validator import dsl_validator


class StepBuilderWidget(QWidget):
    """Widget for building steps within switch cases."""
    
    steps_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.steps = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the step builder UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Steps to Execute:")
        header_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(header_label)
        
        # Add step button
        add_step_btn = QPushButton("Add Step")
        add_step_btn.clicked.connect(self._add_step)
        add_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        header_layout.addWidget(add_step_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Steps list
        self.steps_list = QListWidget()
        self.steps_list.setMaximumHeight(150)
        layout.addWidget(self.steps_list)
        
        # Step controls
        controls_layout = QHBoxLayout()
        
        edit_step_btn = QPushButton("Edit Step")
        edit_step_btn.clicked.connect(self._edit_step)
        controls_layout.addWidget(edit_step_btn)
        
        remove_step_btn = QPushButton("Remove Step")
        remove_step_btn.clicked.connect(self._remove_step)
        remove_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        controls_layout.addWidget(remove_step_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
    def _add_step(self):
        """Add a new step."""
        # For now, create a simple action step
        # In a full implementation, this would open a step type selection dialog
        step = ActionStep(
            action_name="new_action",
            output_key="new_output",
            description="New action step"
        )
        self.steps.append(step)
        self._update_steps_list()
        self.steps_changed.emit()
        
    def _edit_step(self):
        """Edit the selected step."""
        current_row = self.steps_list.currentRow()
        if current_row >= 0 and current_row < len(self.steps):
            # For now, just show a message
            # In a full implementation, this would open a step editor dialog
            QMessageBox.information(self, "Edit Step", "Step editing functionality would be implemented here.")
            
    def _remove_step(self):
        """Remove the selected step."""
        current_row = self.steps_list.currentRow()
        if current_row >= 0 and current_row < len(self.steps):
            del self.steps[current_row]
            self._update_steps_list()
            self.steps_changed.emit()
            
    def _update_steps_list(self):
        """Update the steps list display."""
        self.steps_list.clear()
        for i, step in enumerate(self.steps):
            if isinstance(step, ActionStep):
                text = f"{i+1}. Action: {step.action_name}"
            elif isinstance(step, ScriptStep):
                text = f"{i+1}. Script: {step.output_key}"
            else:
                text = f"{i+1}. {type(step).__name__}"
                
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, i)
            self.steps_list.addItem(item)
            
    def set_steps(self, steps: List):
        """Set the steps list."""
        self.steps = steps.copy() if steps else []
        self._update_steps_list()
        
    def get_steps(self) -> List:
        """Get the current steps list."""
        return self.steps.copy()


class SwitchCaseEditorDialog(QDialog):
    """Dialog for editing switch cases with DSL condition builder."""
    
    def __init__(self, case: Optional[SwitchCase] = None, parent=None):
        super().__init__(parent)
        self.case = case
        self.setWindowTitle("Edit Switch Case" if case else "Add Switch Case")
        self.setModal(True)
        self.resize(800, 600)
        self._setup_ui()
        
        if case:
            self._populate_from_case(case)
            
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_label = QLabel("Switch Case Configuration")
        header_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin-bottom: 16px;")
        layout.addWidget(header_label)
        
        # Main content in tabs
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Condition tab
        condition_tab = QWidget()
        condition_layout = QVBoxLayout(condition_tab)
        
        # Condition input section
        condition_group = QGroupBox("Condition")
        condition_group_layout = QVBoxLayout(condition_group)
        
        condition_help = QLabel("Enter a boolean expression that will be evaluated to determine if this case should execute:")
        condition_help.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        condition_help.setWordWrap(True)
        condition_group_layout.addWidget(condition_help)
        
        # Condition text edit
        self.condition_edit = QTextEdit()
        self.condition_edit.setMaximumHeight(80)
        self.condition_edit.setPlaceholderText("e.g., data.user.role == 'admin' or data.status == 'active'")
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.condition_edit.setFont(font)
        self.condition_edit.textChanged.connect(self._validate_condition)
        condition_group_layout.addWidget(self.condition_edit)
        
        # Validation feedback
        self.validation_label = QLabel("Enter a condition to validate...")
        self.validation_label.setStyleSheet("color: #666; font-size: 10px; margin-top: 4px;")
        condition_group_layout.addWidget(self.validation_label)
        
        condition_layout.addWidget(condition_group)
        
        # DSL Builder
        dsl_group = QGroupBox("DSL Expression Builder")
        dsl_layout = QVBoxLayout(dsl_group)
        
        self.dsl_builder = DSLBuilderWidget()
        self.dsl_builder.expression_built.connect(self._use_dsl_expression)
        dsl_layout.addWidget(self.dsl_builder)
        
        condition_layout.addWidget(dsl_group)
        
        tab_widget.addTab(condition_tab, "Condition")
        
        # Steps tab
        steps_tab = QWidget()
        steps_layout = QVBoxLayout(steps_tab)
        
        steps_help = QLabel("Define the steps that will be executed when this condition is true:")
        steps_help.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        steps_help.setWordWrap(True)
        steps_layout.addWidget(steps_help)
        
        self.step_builder = StepBuilderWidget()
        steps_layout.addWidget(self.step_builder)
        
        tab_widget.addTab(steps_tab, "Steps")
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._accept_case)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        buttons_layout.addWidget(self.ok_btn)
        
        layout.addLayout(buttons_layout)
        
    def _populate_from_case(self, case: SwitchCase):
        """Populate the dialog from an existing case."""
        self.condition_edit.setPlainText(case.condition)
        self.step_builder.set_steps(case.steps)
        
    def _validate_condition(self):
        """Validate the condition expression."""
        condition = self.condition_edit.toPlainText().strip()
        
        if not condition:
            self.validation_label.setText("Enter a condition to validate...")
            self.validation_label.setStyleSheet("color: #666; font-size: 10px;")
            self.ok_btn.setEnabled(False)
            return
            
        # Validate using DSL validator
        result = dsl_validator.validate_dsl_expression(condition)
        
        if result.is_valid:
            self.validation_label.setText("✓ Valid condition")
            self.validation_label.setStyleSheet("color: #4caf50; font-size: 10px; font-weight: bold;")
            self.ok_btn.setEnabled(True)
        else:
            error_msg = "; ".join(result.errors[:2])  # Show first 2 errors
            self.validation_label.setText(f"✗ {error_msg}")
            self.validation_label.setStyleSheet("color: #f44336; font-size: 10px; font-weight: bold;")
            self.ok_btn.setEnabled(False)
            
    def _use_dsl_expression(self, expression: str):
        """Use the DSL expression from the builder."""
        self.condition_edit.setPlainText(expression)
        
    def _accept_case(self):
        """Accept the case and close the dialog."""
        condition = self.condition_edit.toPlainText().strip()
        steps = self.step_builder.get_steps()
        
        if not condition:
            QMessageBox.warning(self, "Invalid Condition", "Please enter a valid condition.")
            return
            
        self.case = SwitchCase(condition=condition, steps=steps)
        self.accept()
        
    def get_case(self) -> Optional[SwitchCase]:
        """Get the configured case."""
        return self.case


class DefaultCaseEditorDialog(QDialog):
    """Dialog for editing default cases."""
    
    def __init__(self, default_case: Optional[DefaultCase] = None, parent=None):
        super().__init__(parent)
        self.default_case = default_case
        self.setWindowTitle("Edit Default Case")
        self.setModal(True)
        self.resize(600, 400)
        self._setup_ui()
        
        if default_case:
            self._populate_from_case(default_case)
            
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_label = QLabel("Default Case Configuration")
        header_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin-bottom: 16px;")
        layout.addWidget(header_label)
        
        # Help text
        help_label = QLabel("Define the steps that will be executed when no other conditions match:")
        help_label.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 16px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        # Step builder
        self.step_builder = StepBuilderWidget()
        layout.addWidget(self.step_builder)
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._accept_case)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
        
    def _populate_from_case(self, default_case: DefaultCase):
        """Populate the dialog from an existing default case."""
        self.step_builder.set_steps(default_case.steps)
        
    def _accept_case(self):
        """Accept the case and close the dialog."""
        steps = self.step_builder.get_steps()
        self.default_case = DefaultCase(steps=steps)
        self.accept()
        
    def get_default_case(self) -> Optional[DefaultCase]:
        """Get the configured default case."""
        return self.default_case
