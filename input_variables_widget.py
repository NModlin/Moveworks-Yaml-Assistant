"""
Input Variables Widget for the Moveworks YAML Assistant.

This module provides a comprehensive UI component for managing input variables
in Moveworks Compound Action workflows with validation, auto-completion,
and integration with the existing PySide6 architecture.
"""

import re
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QLineEdit, QCheckBox, QTextEdit,
    QGroupBox, QLabel, QMessageBox, QCompleter, QAbstractItemView,
    QMenu, QDialog, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QStringListModel
from PySide6.QtGui import QAction

from core_structures import InputVariable, Workflow


class InputVariableDialog(QDialog):
    """Dialog for adding/editing input variables."""
    
    def __init__(self, parent=None, variable: InputVariable = None):
        super().__init__(parent)
        self.variable = variable
        self.is_edit_mode = variable is not None
        
        self.setWindowTitle("Edit Input Variable" if self.is_edit_mode else "Add Input Variable")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
        self._setup_validation()
        
        if self.is_edit_mode:
            self._populate_fields()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        # Variable name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., user_email")
        self.name_edit.textChanged.connect(self._validate_name)
        form_layout.addRow("Variable Name:", self.name_edit)
        
        # Data type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "string", "number", "integer", "boolean", "array", "object",
            "List[string]", "List[number]", "List[integer]", "List[boolean]", 
            "List[object]", "User", "List[User]"
        ])
        form_layout.addRow("Data Type:", self.type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Optional description of the variable")
        form_layout.addRow("Description:", self.description_edit)
        
        # Required checkbox
        self.required_checkbox = QCheckBox("Required")
        self.required_checkbox.setChecked(True)
        form_layout.addRow("", self.required_checkbox)
        
        # Default value
        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("Optional default value")
        form_layout.addRow("Default Value:", self.default_edit)
        
        layout.addLayout(form_layout)
        
        # Validation message
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 12px;
                padding: 4px;
                background-color: #fdf2f2;
                border: 1px solid #e74c3c;
                border-radius: 4px;
            }
        """)
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
    
    def _setup_validation(self):
        """Setup validation timer."""
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_form)
        self.validation_timer.setInterval(300)  # 300ms debounce
    
    def _validate_name(self):
        """Validate variable name with debouncing."""
        self.validation_timer.stop()
        self.validation_timer.start()
    
    def _validate_form(self):
        """Validate the entire form."""
        name = self.name_edit.text().strip()
        
        # Validate name
        if not name:
            self._show_validation_error("Variable name is required")
            return
        
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            self._show_validation_error("Variable name must be lowercase_snake_case (start with letter, only lowercase letters, numbers, and underscores)")
            return
        
        # Clear validation error
        self._clear_validation_error()
        self.ok_button.setEnabled(True)
    
    def _show_validation_error(self, message: str):
        """Show validation error message."""
        self.validation_label.setText(message)
        self.validation_label.show()
        self.ok_button.setEnabled(False)
    
    def _clear_validation_error(self):
        """Clear validation error message."""
        self.validation_label.hide()
        self.ok_button.setEnabled(True)
    
    def _populate_fields(self):
        """Populate fields when editing."""
        if self.variable:
            self.name_edit.setText(self.variable.name)
            self.type_combo.setCurrentText(self.variable.data_type)
            if self.variable.description:
                self.description_edit.setPlainText(self.variable.description)
            self.required_checkbox.setChecked(self.variable.required)
            if self.variable.default_value is not None:
                self.default_edit.setText(str(self.variable.default_value))
    
    def _accept(self):
        """Accept dialog and create/update variable."""
        try:
            name = self.name_edit.text().strip()
            data_type = self.type_combo.currentText()
            description = self.description_edit.toPlainText().strip() or None
            required = self.required_checkbox.isChecked()
            default_value = self.default_edit.text().strip() or None
            
            # Convert default value based on type
            if default_value and data_type in ['number', 'integer']:
                try:
                    default_value = int(default_value) if data_type == 'integer' else float(default_value)
                except ValueError:
                    self._show_validation_error(f"Invalid {data_type} value for default")
                    return
            elif default_value and data_type == 'boolean':
                default_value = default_value.lower() in ['true', '1', 'yes', 'on']
            
            self.variable = InputVariable(
                name=name,
                data_type=data_type,
                description=description,
                required=required,
                default_value=default_value
            )
            
            self.accept()
            
        except ValueError as e:
            self._show_validation_error(str(e))
    
    def get_variable(self) -> Optional[InputVariable]:
        """Get the created/edited variable."""
        return self.variable


class InputVariablesWidget(QWidget):
    """
    Widget for managing input variables in Moveworks workflows.
    
    Provides table-based interface for adding, editing, and removing
    input variables with validation and auto-completion support.
    """
    
    variables_changed = Signal()  # Emitted when variables are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow = None
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("📝 Input Variables")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 6px;
            }
        """)
        header_layout.addWidget(header_label)
        
        # Add button
        self.add_button = QPushButton("➕ Add Variable")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.add_button.clicked.connect(self._add_variable)
        header_layout.addWidget(self.add_button)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Required", "Default", "Description"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Required
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Default
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.itemDoubleClicked.connect(self._edit_variable)
        
        # Style table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.table)
    
    def _setup_connections(self):
        """Setup signal connections."""
        pass
    
    def set_workflow(self, workflow: Workflow):
        """Set the workflow and update the table."""
        self.workflow = workflow
        self._refresh_table()
    
    def _refresh_table(self):
        """Refresh the table with current input variables."""
        if not self.workflow:
            self.table.setRowCount(0)
            return
        
        variables = self.workflow.input_variables
        self.table.setRowCount(len(variables))
        
        for row, var in enumerate(variables):
            # Name
            name_item = QTableWidgetItem(var.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(var.data_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, type_item)
            
            # Required
            required_item = QTableWidgetItem("Yes" if var.required else "No")
            required_item.setFlags(required_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, required_item)
            
            # Default
            default_item = QTableWidgetItem(str(var.default_value) if var.default_value is not None else "")
            default_item.setFlags(default_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, default_item)
            
            # Description
            desc_item = QTableWidgetItem(var.description or "")
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, desc_item)
    
    def _add_variable(self):
        """Add a new input variable."""
        dialog = InputVariableDialog(self)
        if dialog.exec() == QDialog.Accepted:
            variable = dialog.get_variable()
            if variable and self.workflow:
                if self.workflow.add_input_variable(variable):
                    self._refresh_table()
                    self.variables_changed.emit()
                else:
                    QMessageBox.warning(
                        self,
                        "Duplicate Variable",
                        f"A variable named '{variable.name}' already exists."
                    )
    
    def _edit_variable(self, item):
        """Edit the selected variable."""
        row = item.row()
        if self.workflow and 0 <= row < len(self.workflow.input_variables):
            variable = self.workflow.input_variables[row]
            dialog = InputVariableDialog(self, variable)
            if dialog.exec() == QDialog.Accepted:
                updated_variable = dialog.get_variable()
                if updated_variable:
                    # Check for name conflicts (excluding current variable)
                    existing_names = [v.name for i, v in enumerate(self.workflow.input_variables) if i != row]
                    if updated_variable.name in existing_names:
                        QMessageBox.warning(
                            self,
                            "Duplicate Variable",
                            f"A variable named '{updated_variable.name}' already exists."
                        )
                        return
                    
                    self.workflow.input_variables[row] = updated_variable
                    self._refresh_table()
                    self.variables_changed.emit()
    
    def _show_context_menu(self, position):
        """Show context menu for table operations."""
        if self.table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Edit Variable", self)
        edit_action.triggered.connect(lambda: self._edit_variable(self.table.itemAt(position)))
        menu.addAction(edit_action)
        
        delete_action = QAction("🗑️ Delete Variable", self)
        delete_action.triggered.connect(lambda: self._delete_variable(self.table.itemAt(position)))
        menu.addAction(delete_action)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def _delete_variable(self, item):
        """Delete the selected variable."""
        row = item.row()
        if self.workflow and 0 <= row < len(self.workflow.input_variables):
            variable = self.workflow.input_variables[row]
            
            reply = QMessageBox.question(
                self,
                "Delete Variable",
                f"Are you sure you want to delete the variable '{variable.name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.workflow.input_variables[row]
                self._refresh_table()
                self.variables_changed.emit()
    
    def get_variable_names(self) -> List[str]:
        """Get list of current variable names for auto-completion."""
        if self.workflow:
            return self.workflow.get_input_variable_names()
        return []
