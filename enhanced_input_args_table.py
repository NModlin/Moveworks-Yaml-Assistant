"""
Enhanced Input Arguments Table for the Moveworks YAML Assistant.

This module provides an enhanced table widget for input arguments with:
- Auto-completion for argument names based on action catalog
- Auto-suggestion for data paths from previous steps
- Drag-and-drop support from JSON Path Selector
- Real-time validation with visual indicators
- Array-type input handling with proper formatting
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QCompleter, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QMenu, QMessageBox, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QStringListModel, QTimer
from PySide6.QtGui import QAction, QFont, QDragEnterEvent, QDropEvent

from mw_actions_catalog import MW_ACTIONS_CATALOG, get_action_by_name
from core_structures import Workflow, ActionStep, ScriptStep

logger = logging.getLogger(__name__)


class InputArgsSuggestionEngine:
    """
    Engine for generating input argument suggestions based on:
    - Selected action's required/optional parameters from MW_ACTIONS_CATALOG
    - JSON structure from previous steps' outputs
    - Common data path patterns
    """
    
    def __init__(self):
        self.workflow = None
        self.current_step_index = -1
        
    def set_context(self, workflow: Workflow, current_step_index: int):
        """Set the workflow context for suggestions."""
        self.workflow = workflow
        self.current_step_index = current_step_index
        
    def get_action_parameter_suggestions(self, action_name: str) -> List[Dict[str, Any]]:
        """Get parameter suggestions for a specific action."""
        suggestions = []
        
        # Get action from catalog
        action = get_action_by_name(action_name)
        if action and action.input_args:
            for arg_spec in action.input_args:
                suggestions.append({
                    'name': arg_spec.name,
                    'type': arg_spec.type,
                    'required': arg_spec.required,
                    'description': arg_spec.description,
                    'default_value': arg_spec.default_value,
                    'source': 'action_catalog'
                })
                
        return suggestions
        
    def get_data_path_suggestions(self) -> List[Dict[str, Any]]:
        """Get data path suggestions from previous steps and input variables."""
        suggestions = []

        if not self.workflow:
            return suggestions

        # Add input variables first (highest priority)
        if hasattr(self.workflow, 'input_variables') and self.workflow.input_variables:
            for var in self.workflow.input_variables:
                suggestions.append({
                    'value': f'data.{var.name}',
                    'description': var.description or f'Input variable ({var.data_type})',
                    'type': var.data_type,
                    'source': 'input_variable'
                })

        # Add common meta_info paths
        meta_suggestions = [
            {'path': 'meta_info.user.email', 'description': 'Current user email'},
            {'path': 'meta_info.user.first_name', 'description': 'Current user first name'},
            {'path': 'meta_info.user.last_name', 'description': 'Current user last name'},
            {'path': 'meta_info.user.department', 'description': 'Current user department'},
        ]

        for meta in meta_suggestions:
            suggestions.append({
                'value': meta['path'],
                'description': meta['description'],
                'type': 'string',
                'source': 'meta_info'
            })
            
        # Add data paths from previous steps
        for i, step in enumerate(self.workflow.steps):
            if i >= self.current_step_index and self.current_step_index >= 0:
                break  # Don't include current step or later steps
                
            if hasattr(step, 'output_key') and step.output_key:
                output_key = step.output_key
                
                # Add basic step output reference
                suggestions.append({
                    'value': f'data.{output_key}',
                    'description': f'Full output from step {i+1}',
                    'type': 'object',
                    'source': f'step_{i+1}'
                })
                
                # Add specific field suggestions if JSON is available
                if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                    field_suggestions = self._extract_json_field_suggestions(
                        step.parsed_json_output, f'data.{output_key}', f'step_{i+1}'
                    )
                    suggestions.extend(field_suggestions)
                    
        return suggestions
        
    def _extract_json_field_suggestions(self, json_data: Any, path_prefix: str, source: str) -> List[Dict[str, Any]]:
        """Extract field suggestions from JSON data."""
        suggestions = []
        
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                field_path = f"{path_prefix}.{key}"
                field_type = type(value).__name__
                
                suggestions.append({
                    'value': field_path,
                    'description': f'{key} field from {source}',
                    'type': field_type,
                    'source': source
                })
                
                # Recursively add nested fields (limited depth)
                if isinstance(value, dict) and len(field_path.split('.')) < 5:
                    nested_suggestions = self._extract_json_field_suggestions(
                        value, field_path, source
                    )
                    suggestions.extend(nested_suggestions[:3])  # Limit nested suggestions
                    
        elif isinstance(json_data, list) and json_data:
            # Add array access patterns
            suggestions.append({
                'value': f"{path_prefix}[0]",
                'description': f'First item from {source} array',
                'type': 'array_item',
                'source': source
            })
            
            # If array contains objects, suggest common fields
            if isinstance(json_data[0], dict):
                for key in list(json_data[0].keys())[:3]:  # Limit to first 3 keys
                    suggestions.append({
                        'value': f"{path_prefix}[0].{key}",
                        'description': f'{key} from first item in {source}',
                        'type': 'array_field',
                        'source': source
                    })
                    
        return suggestions


class EnhancedInputArgsTable(QTableWidget):
    """
    Enhanced table widget for input arguments with auto-completion,
    suggestions, and drag-drop support.
    """
    
    # Signals
    suggestions_requested = Signal(str)  # Emitted when user requests suggestions
    validation_changed = Signal(bool, list)  # Emitted when validation status changes
    
    def __init__(self, step_type: str = "action", parent=None):
        super().__init__(0, 2, parent)
        self.step_type = step_type
        self.workflow = None
        self.current_step = None
        self.current_step_index = -1
        
        # Initialize suggestion engine
        self.suggestion_engine = InputArgsSuggestionEngine()
        
        # Setup table properties
        self._setup_table()
        self._setup_drag_drop()
        
        # Validation timer for debounced validation
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_all_args)
        
        logger.debug(f"EnhancedInputArgsTable initialized for {step_type} steps")
        
    def _setup_table(self):
        """Setup table properties and styling."""
        # Set headers
        self.setHorizontalHeaderLabels(["Argument Name", "Value"])
        
        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 150)  # Fixed width for argument name column
        
        # Enable sorting and selection
        self.setSortingEnabled(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Set minimum size
        self.setMinimumHeight(120)
        self.setMaximumHeight(300)
        
        # Connect signals
        self.itemChanged.connect(self._on_item_changed)
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)
        
    def _setup_drag_drop(self):
        """Setup drag and drop functionality."""
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableWidget.DropOnly)
        
    def set_context(self, workflow: Workflow, current_step: Any, current_step_index: int):
        """Set the workflow context for suggestions."""
        self.workflow = workflow
        self.current_step = current_step
        self.current_step_index = current_step_index
        
        # Update suggestion engine context
        self.suggestion_engine.set_context(workflow, current_step_index)
        
        logger.debug(f"Context set for step {current_step_index}")
        
    def _on_item_changed(self, item: QTableWidgetItem):
        """Handle item changes with validation."""
        # Start validation timer (debounced)
        self.validation_timer.start(300)
        
    def _on_cell_double_clicked(self, row: int, column: int):
        """Handle cell double-click to show suggestions."""
        if column == 0:  # Argument name column
            self._show_argument_suggestions(row)
        elif column == 1:  # Value column
            self._show_value_suggestions(row)
            
    def _show_argument_suggestions(self, row: int):
        """Show argument name suggestions for the given row."""
        if not self.current_step:
            return
            
        suggestions = []
        
        # Get action-specific suggestions if this is an action step
        if isinstance(self.current_step, ActionStep) and self.current_step.action_name:
            action_suggestions = self.suggestion_engine.get_action_parameter_suggestions(
                self.current_step.action_name
            )
            suggestions.extend(action_suggestions)
            
        # Show suggestions in a context menu or dialog
        self._show_suggestions_menu(row, 0, suggestions, "argument_names")
        
    def _show_value_suggestions(self, row: int):
        """Show value suggestions for the given row."""
        data_path_suggestions = self.suggestion_engine.get_data_path_suggestions()
        self._show_suggestions_menu(row, 1, data_path_suggestions, "data_paths")
        
    def _show_suggestions_menu(self, row: int, column: int, suggestions: List[Dict], suggestion_type: str):
        """Show a context menu with suggestions."""
        if not suggestions:
            QMessageBox.information(
                self, 
                "No Suggestions", 
                f"No {suggestion_type.replace('_', ' ')} suggestions available."
            )
            return
            
        menu = QMenu(self)
        
        for suggestion in suggestions[:10]:  # Limit to 10 suggestions
            if suggestion_type == "argument_names":
                text = f"{suggestion['name']} ({suggestion['type']})"
                if suggestion['required']:
                    text += " *"
                action = QAction(text, self)
                action.setToolTip(suggestion.get('description', ''))
                action.triggered.connect(
                    lambda checked, s=suggestion: self._apply_argument_suggestion(row, s)
                )
            else:  # data_paths
                text = suggestion['value']
                action = QAction(text, self)
                action.setToolTip(suggestion.get('description', ''))
                action.triggered.connect(
                    lambda checked, s=suggestion: self._apply_value_suggestion(row, s)
                )
                
            menu.addAction(action)
            
        # Show menu at cursor position
        menu.exec(self.mapToGlobal(self.visualItemRect(self.item(row, column)).center()))
        
    def _apply_argument_suggestion(self, row: int, suggestion: Dict):
        """Apply an argument name suggestion."""
        item = self.item(row, 0)
        if item:
            item.setText(suggestion['name'])
            
    def _apply_value_suggestion(self, row: int, suggestion: Dict):
        """Apply a value suggestion."""
        item = self.item(row, 1)
        if item:
            item.setText(suggestion['value'])
            
    def _validate_all_args(self):
        """Validate all input arguments."""
        errors = []
        warnings = []
        
        for row in range(self.rowCount()):
            key_item = self.item(row, 0)
            value_item = self.item(row, 1)
            
            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                
                if key:  # Only validate non-empty keys
                    row_errors, row_warnings = self._validate_argument_pair(key, value, row)
                    errors.extend(row_errors)
                    warnings.extend(row_warnings)
                    
        # Emit validation status
        is_valid = len(errors) == 0
        all_issues = errors + warnings
        self.validation_changed.emit(is_valid, all_issues)
        
    def _validate_argument_pair(self, key: str, value: str, row: int) -> Tuple[List[str], List[str]]:
        """Validate a single argument key-value pair."""
        errors = []
        warnings = []
        
        # Validate key format (snake_case)
        import re
        if not re.match(r'^[a-z][a-z0-9_]*$', key):
            errors.append(f"Row {row + 1}: Argument name '{key}' must use lowercase_snake_case")
            
        # Validate value format for DSL expressions
        if value and (value.startswith('data.') or value.startswith('meta_info.')):
            # This is a DSL expression, validate it
            from dsl_validator import dsl_validator
            result = dsl_validator.validate_dsl_expression(value)
            
            if not result.is_valid:
                errors.extend([f"Row {row + 1}: {error}" for error in result.errors])
            if result.warnings:
                warnings.extend([f"Row {row + 1}: {warning}" for warning in result.warnings])
                
        return errors, warnings
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        if event.mimeData().hasText():
            # Get the drop position
            item = self.itemAt(event.position().toPoint())
            if item:
                row = item.row()
                col = item.column()
                
                # If dropping on the value column (column 1), set the text
                if col == 1:
                    dropped_text = event.mimeData().text()
                    item.setText(dropped_text)
                    event.acceptProposedAction()
                    
                    # Trigger validation
                    self.validation_timer.start(300)
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def populate_from_step(self, step):
        """Populate the table from a step's input_args."""
        self.setRowCount(0)  # Clear existing rows

        if hasattr(step, 'input_args') and step.input_args:
            for key, value in step.input_args.items():
                self.add_argument_row(key, str(value))

    def add_argument_row(self, key: str = "", value: str = ""):
        """Add a new argument row to the table."""
        row = self.rowCount()
        self.insertRow(row)

        # Create items
        key_item = QTableWidgetItem(key)
        value_item = QTableWidgetItem(value)

        # Set items
        self.setItem(row, 0, key_item)
        self.setItem(row, 1, value_item)

        # Set tooltips
        key_item.setToolTip("Double-click for argument name suggestions")
        value_item.setToolTip("Double-click for data path suggestions or drag from JSON Path Selector")

        return row

    def remove_selected_row(self):
        """Remove the currently selected row."""
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
            # Trigger validation after removal
            self.validation_timer.start(300)

    def get_input_args_dict(self) -> Dict[str, str]:
        """Get the current input arguments as a dictionary."""
        input_args = {}

        for row in range(self.rowCount()):
            key_item = self.item(row, 0)
            value_item = self.item(row, 1)

            if key_item and value_item and key_item.text().strip():
                input_args[key_item.text().strip()] = value_item.text().strip()

        return input_args

    def clear_all_arguments(self):
        """Clear all arguments from the table."""
        self.setRowCount(0)

    def auto_populate_from_action(self, action_name: str):
        """Auto-populate required arguments for a given action."""
        if not action_name:
            return

        # Get action suggestions
        suggestions = self.suggestion_engine.get_action_parameter_suggestions(action_name)

        # Add required arguments
        required_args = [s for s in suggestions if s.get('required', False)]

        for arg in required_args:
            # Check if argument already exists
            existing_keys = [self.item(row, 0).text() for row in range(self.rowCount())
                           if self.item(row, 0)]

            if arg['name'] not in existing_keys:
                self.add_argument_row(arg['name'], "")

        logger.debug(f"Auto-populated {len(required_args)} required arguments for {action_name}")

    def show_json_input_dialog(self):
        """Show dialog for inputting JSON to auto-suggest arguments."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QLabel

        dialog = QDialog(self)
        dialog.setWindowTitle("JSON Input for Auto-Suggestions")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel(
            "Paste JSON output example below to automatically detect and suggest input argument fields:"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # JSON input area
        json_input = QTextEdit()
        json_input.setPlaceholderText("Paste JSON here...")
        layout.addWidget(json_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            json_text = json_input.toPlainText().strip()
            if json_text:
                self._process_json_for_suggestions(json_text)

    def _process_json_for_suggestions(self, json_text: str):
        """Process JSON text to generate argument suggestions."""
        try:
            json_data = json.loads(json_text)

            # Extract potential argument names from JSON structure
            suggestions = self._extract_argument_suggestions_from_json(json_data)

            if suggestions:
                self._show_json_suggestions_dialog(suggestions)
            else:
                QMessageBox.information(
                    self,
                    "No Suggestions",
                    "No argument suggestions could be generated from the provided JSON."
                )

        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Invalid JSON",
                f"The provided JSON is invalid: {str(e)}"
            )

    def _extract_argument_suggestions_from_json(self, json_data: Any, prefix: str = "") -> List[Dict[str, str]]:
        """Extract potential argument names from JSON structure."""
        suggestions = []

        if isinstance(json_data, dict):
            for key, value in json_data.items():
                # Convert camelCase to snake_case for argument names
                snake_case_key = self._camel_to_snake(key)

                suggestion = {
                    'name': snake_case_key,
                    'original_key': key,
                    'type': type(value).__name__,
                    'sample_value': str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                }
                suggestions.append(suggestion)

                # Recursively process nested objects (limited depth)
                if isinstance(value, dict) and len(prefix.split('.')) < 2:
                    nested_prefix = f"{prefix}.{key}" if prefix else key
                    nested_suggestions = self._extract_argument_suggestions_from_json(
                        value, nested_prefix
                    )
                    suggestions.extend(nested_suggestions[:3])  # Limit nested suggestions

        return suggestions

    def _camel_to_snake(self, camel_str: str) -> str:
        """Convert camelCase to snake_case."""
        import re
        # Insert underscore before uppercase letters
        snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        return snake_str

    def _show_json_suggestions_dialog(self, suggestions: List[Dict[str, str]]):
        """Show dialog with JSON-based argument suggestions."""
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
            QDialogButtonBox, QLabel, QPushButton, QCheckBox
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Argument Suggestions from JSON")
        dialog.setModal(True)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel(
            "Select the arguments you want to add to your input arguments table:"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Suggestions list
        suggestions_list = QListWidget()

        for suggestion in suggestions:
            item_text = f"{suggestion['name']} ({suggestion['type']}) - {suggestion['sample_value']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, suggestion)
            item.setCheckState(Qt.Unchecked)
            suggestions_list.addItem(item)

        layout.addWidget(suggestions_list)

        # Select all/none buttons
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_none_btn = QPushButton("Select None")

        def select_all():
            for i in range(suggestions_list.count()):
                suggestions_list.item(i).setCheckState(Qt.Checked)

        def select_none():
            for i in range(suggestions_list.count()):
                suggestions_list.item(i).setCheckState(Qt.Unchecked)

        select_all_btn.clicked.connect(select_all)
        select_none_btn.clicked.connect(select_none)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(select_none_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            # Add selected suggestions to the table
            for i in range(suggestions_list.count()):
                item = suggestions_list.item(i)
                if item.checkState() == Qt.Checked:
                    suggestion = item.data(Qt.UserRole)
                    self.add_argument_row(suggestion['name'], "")

            logger.debug(f"Added suggestions to input arguments table")
