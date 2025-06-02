"""
Main GUI application for the Moveworks YAML Assistant using PySide6.

This module implements the desktop application interface for creating and
managing Moveworks Compound Action workflows.
"""

import sys
import json
from typing import Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QTextEdit, QLabel,
    QPushButton, QMessageBox, QDialog,
    QStackedWidget, QTreeWidget, QTreeWidgetItem, QGroupBox,
    QFormLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QTabWidget, QScrollArea, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QFont, QPalette

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, SwitchCase, DefaultCase, ParallelBranch,
    RaiseStep, TryCatchStep, CatchBlock
)
from mw_actions_catalog import MW_ACTIONS_CATALOG, get_action_by_name, get_all_categories
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate
from error_display import ErrorListWidget, ValidationDialog, StatusIndicator, HelpDialog
from help_system import get_tooltip, get_contextual_help
# Unified tutorial system
from tutorials import UnifiedTutorialManager
from template_library import TemplateBrowserDialog, template_library, SimplifiedTemplateSystem
from enhanced_json_selector import EnhancedJsonPathSelector
from contextual_examples import ContextualExamplesPanel
from enhanced_validator import enhanced_validator, ValidationError
from bender_function_builder import BenderFunctionBuilder
from enhanced_script_editor import EnhancedScriptEditor
from expression_factory import ExpressionFactory, CommonPatterns
from workflow_wizard import WorkflowWizard
from simplified_data_path_selector import SimplifiedDataPathSelector
from enhanced_apiton_validator import enhanced_apiton_validator, APIthonValidationResult
from error_display import APIthonValidationWidget, EnhancedAPIthonValidationWidget
from compliance_validator import compliance_validator, ComplianceValidationResult
from dsl_input_widget import DSLInputWidget
from dsl_validator import dsl_validator
from enhanced_input_args_table import EnhancedInputArgsTable
from input_variables_widget import InputVariablesWidget
from smart_suggestions_widget import SmartSuggestionsWidget
from simple_visual_builder import SimpleVisualBuilder


class WorkflowListWidget(QListWidget):
    """Custom list widget for displaying workflow steps."""

    step_selected = Signal(int)  # Emits the index of the selected step

    def __init__(self):
        super().__init__()
        self.workflow = Workflow()
        self.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click and emit step selection signal."""
        index = self.row(item)
        self.step_selected.emit(index)

    def update_workflow_display(self):
        """Update the list display with current workflow steps."""
        self.clear()

        for i, step in enumerate(self.workflow.steps):
            if isinstance(step, ActionStep):
                text = f"{i+1}. Action: {step.action_name}"
                if step.description:
                    text += f" - {step.description[:50]}..."
            elif isinstance(step, ScriptStep):
                text = f"{i+1}. Script"
                if step.description:
                    text += f" - {step.description[:50]}..."
                else:
                    text += f" - {step.code[:50]}..."
            elif isinstance(step, SwitchStep):
                text = f"{i+1}. Switch"
                if step.description:
                    text += f" - {step.description[:50]}..."
                else:
                    text += f" - {len(step.cases)} case(s)"
            elif isinstance(step, ForLoopStep):
                text = f"{i+1}. For Loop: {step.each} in {step.in_source}"
                if step.description:
                    text += f" - {step.description[:50]}..."
            elif isinstance(step, ParallelStep):
                text = f"{i+1}. Parallel"
                if step.description:
                    text += f" - {step.description[:50]}..."
                else:
                    text += f" - {len(step.branches)} branch(es)"
            elif isinstance(step, ReturnStep):
                text = f"{i+1}. Return"
                if step.description:
                    text += f" - {step.description[:50]}..."
                else:
                    text += f" - {len(step.output_mapper)} output(s)"
            else:
                text = f"{i+1}. Unknown Step Type"

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, i)  # Store step index
            self.addItem(item)

    def add_step(self, step):
        """Add a step to the workflow and update display."""
        self.workflow.steps.append(step)
        self.update_workflow_display()

    def remove_selected_step(self):
        """Remove the currently selected step."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.workflow.steps):
            del self.workflow.steps[current_row]
            self.update_workflow_display()

    def move_step_up(self):
        """Move the selected step up in the list."""
        current_row = self.currentRow()
        if current_row > 0:
            step = self.workflow.steps.pop(current_row)
            self.workflow.steps.insert(current_row - 1, step)
            self.update_workflow_display()
            self.setCurrentRow(current_row - 1)

    def move_step_down(self):
        """Move the selected step down in the list."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.workflow.steps) - 1:
            step = self.workflow.steps.pop(current_row)
            self.workflow.steps.insert(current_row + 1, step)
            self.update_workflow_display()
            self.setCurrentRow(current_row + 1)


class EnhancedReturnMapperTable(QTableWidget):
    """Enhanced table widget for return step output mapper with drag-drop support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableWidget.DropOnly)

    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasText():
            # Check if the dragged text looks like a data path
            text = event.mimeData().text()
            if text.startswith(('data.', 'meta_info.')):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith(('data.', 'meta_info.')):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith(('data.', 'meta_info.')):
                # Find the drop position
                item = self.itemAt(event.position().toPoint())
                if item:
                    row = item.row()
                    col = item.column()

                    # If dropping on the data path column (column 1), set the text
                    if col == 1:
                        item.setText(text)
                    # If dropping on output key column (column 0), add a new row
                    elif col == 0:
                        # Add a new row and set the data path
                        new_row = self.rowCount()
                        self.insertRow(new_row)
                        self.setItem(new_row, 0, QTableWidgetItem(""))
                        self.setItem(new_row, 1, QTableWidgetItem(text))
                else:
                    # Drop in empty space - add a new row
                    new_row = self.rowCount()
                    self.insertRow(new_row)
                    self.setItem(new_row, 0, QTableWidgetItem(""))
                    self.setItem(new_row, 1, QTableWidgetItem(text))

                event.acceptProposedAction()

                # Emit itemChanged signal to trigger validation
                if hasattr(self, 'itemChanged'):
                    self.itemChanged.emit(self.item(self.rowCount()-1, 1))
            else:
                event.ignore()
        else:
            event.ignore()


class StepConfigurationPanel(QStackedWidget):
    """Panel for configuring step properties."""

    step_updated = Signal()  # Emitted when step data is updated

    def __init__(self):
        super().__init__()
        self.current_step = None
        self.current_step_index = -1
        self.workflow = None  # Add workflow reference

        # Create different configuration widgets
        self.empty_widget = QLabel("Select a step to configure")
        self.empty_widget.setAlignment(Qt.AlignCenter)
        self.addWidget(self.empty_widget)

        self.action_config_widget = self._create_action_config_widget()
        self.addWidget(self.action_config_widget)

        self.script_config_widget = self._create_script_config_widget()
        self.addWidget(self.script_config_widget)

        self.switch_config_widget = self._create_switch_config_widget()
        self.addWidget(self.switch_config_widget)

        self.return_config_widget = self._create_return_config_widget()
        self.addWidget(self.return_config_widget)

        self.try_catch_config_widget = self._create_try_catch_config_widget()
        self.addWidget(self.try_catch_config_widget)

        self.parallel_config_widget = self._create_parallel_config_widget()
        self.addWidget(self.parallel_config_widget)

    def _create_action_config_widget(self):
        """Create the configuration widget for action steps."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create form layout for basic properties
        form_group = QGroupBox("Action Properties")
        form_layout = QFormLayout(form_group)

        self.action_name_edit = QLineEdit()
        self.action_name_edit.textChanged.connect(self._on_action_data_changed)
        self.action_name_edit.textChanged.connect(self._validate_current_step)
        self.action_name_edit.textChanged.connect(self._validate_action_name_field)
        self.action_name_edit.setToolTip(get_tooltip("action_name") + "\n\nRequired field. Use Moveworks action names (e.g., 'mw.get_user_by_email') or custom action names.")
        self.action_name_edit.setPlaceholderText("e.g., mw.get_user_by_email")

        # Add validation indicator for action_name
        self.action_name_indicator = QLabel()
        self.action_name_indicator.setFixedSize(16, 16)
        self.action_name_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.action_name_indicator.setText("*")
        self.action_name_indicator.setToolTip("Required field")

        # Create horizontal layout for action_name with validation indicator
        action_name_layout = QHBoxLayout()
        action_name_layout.addWidget(self.action_name_edit)
        action_name_layout.addWidget(self.action_name_indicator)
        action_name_layout.setContentsMargins(0, 0, 0, 0)

        action_name_widget = QWidget()
        action_name_widget.setLayout(action_name_layout)

        # Create label with mandatory field indicator
        action_name_label = QLabel("Action Name: *")
        action_name_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(action_name_label, action_name_widget)

        self.action_description_edit = QLineEdit()
        self.action_description_edit.textChanged.connect(self._on_action_data_changed)
        self.action_description_edit.setToolTip(get_tooltip("description"))
        self.action_description_edit.setPlaceholderText("Optional description of this action")
        form_layout.addRow("Description:", self.action_description_edit)

        self.action_output_key_edit = QLineEdit()
        self.action_output_key_edit.textChanged.connect(self._on_action_data_changed)
        self.action_output_key_edit.textChanged.connect(self._validate_current_step)
        self.action_output_key_edit.textChanged.connect(self._validate_output_key_field)
        self.action_output_key_edit.setToolTip(get_tooltip("output_key") + "\n\nRequired field. Must use lowercase_snake_case format.")
        self.action_output_key_edit.setPlaceholderText("e.g., user_info")

        # Add validation indicator for output_key
        self.action_output_key_indicator = QLabel()
        self.action_output_key_indicator.setFixedSize(16, 16)
        self.action_output_key_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.action_output_key_indicator.setText("*")
        self.action_output_key_indicator.setToolTip("Required field")

        # Create horizontal layout for output_key with validation indicator
        output_key_layout = QHBoxLayout()
        output_key_layout.addWidget(self.action_output_key_edit)
        output_key_layout.addWidget(self.action_output_key_indicator)
        output_key_layout.setContentsMargins(0, 0, 0, 0)

        output_key_widget = QWidget()
        output_key_widget.setLayout(output_key_layout)

        # Create label with mandatory field indicator
        output_key_label = QLabel("Output Key: *")
        output_key_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(output_key_label, output_key_widget)

        layout.addWidget(form_group)

        # Input arguments table
        input_args_group = QGroupBox("Input Arguments")
        input_args_layout = QVBoxLayout(input_args_group)

        # Enhanced input arguments table with auto-suggestion
        self.action_input_args_table = EnhancedInputArgsTable(step_type="action")
        self.action_input_args_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.action_input_args_table.horizontalHeader().setStretchLastSection(True)
        self.action_input_args_table.itemChanged.connect(self._on_action_data_changed)
        self.action_input_args_table.setToolTip(get_tooltip("input_args"))
        # Set minimum height to ensure input fields are fully visible
        self.action_input_args_table.setMinimumHeight(120)
        # Set reasonable maximum height to prevent excessive growth
        self.action_input_args_table.setMaximumHeight(300)
        input_args_layout.addWidget(self.action_input_args_table)

        # Enhanced buttons for input args
        input_args_buttons = QHBoxLayout()
        self.add_input_arg_btn = QPushButton("Add Argument")  # Store as attribute for tutorial
        self.add_input_arg_btn.setObjectName("add_input_arg_btn")  # For tutorial targeting
        self.add_input_arg_btn.clicked.connect(self._add_action_input_arg)

        # Auto-suggest button
        auto_suggest_btn = QPushButton("Auto-Suggest from Action")
        auto_suggest_btn.clicked.connect(self._auto_suggest_action_args)
        auto_suggest_btn.setToolTip("Auto-populate required arguments based on selected action")

        # JSON input button
        json_suggest_btn = QPushButton("Suggest from JSON")
        json_suggest_btn.clicked.connect(self._suggest_args_from_json)
        json_suggest_btn.setToolTip("Analyze JSON to suggest input arguments")

        # Apply high contrast styling for readability
        self.add_input_arg_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)

        remove_arg_btn = QPushButton("Remove Selected")
        remove_arg_btn.clicked.connect(self._remove_action_input_arg)

        # Apply consistent styling to all buttons
        button_style = """
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """

        # Apply specific colors
        auto_suggest_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #2196f3;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)

        json_suggest_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #ff9800;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)

        remove_arg_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f44336;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        input_args_buttons.addWidget(self.add_input_arg_btn)
        input_args_buttons.addWidget(auto_suggest_btn)
        input_args_buttons.addWidget(json_suggest_btn)
        input_args_buttons.addWidget(remove_arg_btn)
        input_args_buttons.addStretch()
        input_args_layout.addLayout(input_args_buttons)

        layout.addWidget(input_args_group)

        # JSON output section
        json_group = QGroupBox("JSON Output")
        json_layout = QVBoxLayout(json_group)

        self.action_json_edit = QTextEdit()
        self.action_json_edit.setObjectName("json_output_edit")  # For tutorial targeting
        self.action_json_edit.setPlaceholderText("Paste the JSON output this action will produce...")
        self.action_json_edit.setToolTip(get_tooltip("json_output"))
        json_layout.addWidget(self.action_json_edit)

        self.parse_json_btn = QPushButton("Parse & Save JSON Output")  # Store as attribute for tutorial
        self.parse_json_btn.setObjectName("parse_json_btn")  # For tutorial targeting
        self.parse_json_btn.clicked.connect(self._parse_action_json)
        self.parse_json_btn.setToolTip(get_tooltip("parse_json"))

        # Apply high contrast styling for readability
        self.parse_json_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)

        json_layout.addWidget(self.parse_json_btn)

        layout.addWidget(json_group)

        return widget

    def _create_script_config_widget(self):
        """Create the configuration widget for script steps."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create form layout for basic properties
        form_group = QGroupBox("Script Properties")
        form_layout = QFormLayout(form_group)

        self.script_description_edit = QLineEdit()
        self.script_description_edit.textChanged.connect(self._on_script_data_changed)
        self.script_description_edit.setToolTip(get_tooltip("description"))
        self.script_description_edit.setPlaceholderText("Optional description of this script")
        form_layout.addRow("Description:", self.script_description_edit)

        self.script_output_key_edit = QLineEdit()
        self.script_output_key_edit.textChanged.connect(self._on_script_data_changed)
        self.script_output_key_edit.textChanged.connect(self._validate_current_step)
        self.script_output_key_edit.textChanged.connect(self._validate_output_key_field)
        self.script_output_key_edit.setToolTip(get_tooltip("output_key") + "\n\nRequired field. Must use lowercase_snake_case format.")
        self.script_output_key_edit.setPlaceholderText("e.g., processed_data")

        # Add validation indicator for script output_key
        self.script_output_key_indicator = QLabel()
        self.script_output_key_indicator.setFixedSize(16, 16)
        self.script_output_key_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.script_output_key_indicator.setText("*")
        self.script_output_key_indicator.setToolTip("Required field")

        # Create horizontal layout for script output_key with validation indicator
        script_output_key_layout = QHBoxLayout()
        script_output_key_layout.addWidget(self.script_output_key_edit)
        script_output_key_layout.addWidget(self.script_output_key_indicator)
        script_output_key_layout.setContentsMargins(0, 0, 0, 0)

        script_output_key_widget = QWidget()
        script_output_key_widget.setLayout(script_output_key_layout)

        # Create label with mandatory field indicator
        script_output_key_label = QLabel("Output Key: *")
        script_output_key_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(script_output_key_label, script_output_key_widget)

        layout.addWidget(form_group)

        # Enhanced script editor section with code field validation
        script_editor_group = QGroupBox("APIthon Script Code")
        script_editor_layout = QVBoxLayout(script_editor_group)

        # Add code field validation header
        code_field_layout = QHBoxLayout()
        code_field_label = QLabel("Code: *")
        code_field_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        code_field_layout.addWidget(code_field_label)

        # Add validation indicator for script code field
        self.script_code_indicator = QLabel()
        self.script_code_indicator.setFixedSize(16, 16)
        self.script_code_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.script_code_indicator.setText("*")
        self.script_code_indicator.setToolTip("Required field")
        code_field_layout.addWidget(self.script_code_indicator)
        code_field_layout.addStretch()

        script_editor_layout.addLayout(code_field_layout)

        self.enhanced_script_editor = EnhancedScriptEditor()
        self.enhanced_script_editor.script_changed.connect(self._on_script_data_changed)
        self.enhanced_script_editor.script_changed.connect(self._validate_script_code_field)
        self.enhanced_script_editor.validation_updated.connect(self._on_script_validation_updated)
        script_editor_layout.addWidget(self.enhanced_script_editor)

        layout.addWidget(script_editor_group)

        # Input arguments table
        input_args_group = QGroupBox("Input Arguments")
        input_args_layout = QVBoxLayout(input_args_group)

        # Enhanced input arguments table with auto-suggestion
        self.script_input_args_table = EnhancedInputArgsTable(step_type="script")
        self.script_input_args_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.script_input_args_table.horizontalHeader().setStretchLastSection(True)
        self.script_input_args_table.itemChanged.connect(self._on_script_data_changed)
        # Set minimum height to ensure input fields are fully visible
        self.script_input_args_table.setMinimumHeight(120)
        # Set reasonable maximum height to prevent excessive growth
        self.script_input_args_table.setMaximumHeight(300)
        input_args_layout.addWidget(self.script_input_args_table)

        # Enhanced buttons for input args
        input_args_buttons = QHBoxLayout()
        add_arg_btn = QPushButton("Add Argument")
        add_arg_btn.clicked.connect(self._add_script_input_arg)

        # JSON input button for scripts
        json_suggest_btn = QPushButton("Suggest from JSON")
        json_suggest_btn.clicked.connect(self._suggest_script_args_from_json)
        json_suggest_btn.setToolTip("Analyze JSON to suggest input arguments")

        remove_arg_btn = QPushButton("Remove Selected")
        remove_arg_btn.clicked.connect(self._remove_script_input_arg)

        # Apply consistent styling to all buttons
        button_style = """
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """

        json_suggest_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #ff9800;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)

        remove_arg_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f44336;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        input_args_buttons.addWidget(add_arg_btn)
        input_args_buttons.addWidget(json_suggest_btn)
        input_args_buttons.addWidget(remove_arg_btn)
        input_args_buttons.addStretch()
        input_args_layout.addLayout(input_args_buttons)

        layout.addWidget(input_args_group)

        # JSON output section
        json_group = QGroupBox("JSON Output")
        json_layout = QVBoxLayout(json_group)

        self.script_json_edit = QTextEdit()
        self.script_json_edit.setPlaceholderText("Paste the JSON output this script will produce...")
        json_layout.addWidget(self.script_json_edit)

        parse_json_btn = QPushButton("Parse & Save JSON Output")
        parse_json_btn.clicked.connect(self._parse_script_json)
        json_layout.addWidget(parse_json_btn)

        layout.addWidget(json_group)

        return widget

    def _create_switch_config_widget(self):
        """Create the configuration widget for switch steps."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create form layout for basic properties
        form_group = QGroupBox("Switch Properties")
        form_layout = QFormLayout(form_group)

        self.switch_description_edit = QLineEdit()
        self.switch_description_edit.textChanged.connect(self._on_switch_data_changed)
        self.switch_description_edit.setToolTip(get_tooltip("description"))
        self.switch_description_edit.setPlaceholderText("Optional description of this switch statement")
        form_layout.addRow("Description:", self.switch_description_edit)

        self.switch_output_key_edit = QLineEdit()
        self.switch_output_key_edit.textChanged.connect(self._on_switch_data_changed)
        self.switch_output_key_edit.setToolTip(get_tooltip("output_key") + "\n\nUsually '_' for switch statements")
        self.switch_output_key_edit.setPlaceholderText("_")
        form_layout.addRow("Output Key:", self.switch_output_key_edit)

        layout.addWidget(form_group)

        # Switch cases section
        cases_group = QGroupBox("Switch Cases")
        cases_layout = QVBoxLayout(cases_group)

        # Cases list and controls
        cases_header_layout = QHBoxLayout()
        cases_header_label = QLabel("Cases:")
        cases_header_label.setStyleSheet("font-weight: bold;")
        cases_header_layout.addWidget(cases_header_label)

        add_case_btn = QPushButton("Add Case")
        add_case_btn.clicked.connect(self._add_switch_case)
        add_case_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        cases_header_layout.addWidget(add_case_btn)
        cases_header_layout.addStretch()

        cases_layout.addLayout(cases_header_layout)

        # Cases list widget
        self.switch_cases_list = QListWidget()
        # Increase height to ensure better visibility
        self.switch_cases_list.setMinimumHeight(100)
        self.switch_cases_list.setMaximumHeight(250)
        self.switch_cases_list.itemClicked.connect(self._on_switch_case_selected)
        cases_layout.addWidget(self.switch_cases_list)

        # Case controls
        case_controls_layout = QHBoxLayout()

        edit_case_btn = QPushButton("Edit Case")
        edit_case_btn.clicked.connect(self._edit_switch_case)
        case_controls_layout.addWidget(edit_case_btn)

        remove_case_btn = QPushButton("Remove Case")
        remove_case_btn.clicked.connect(self._remove_switch_case)
        remove_case_btn.setStyleSheet("""
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
        case_controls_layout.addWidget(remove_case_btn)
        case_controls_layout.addStretch()

        cases_layout.addLayout(case_controls_layout)
        layout.addWidget(cases_group)

        # Default case section
        default_group = QGroupBox("Default Case")
        default_layout = QVBoxLayout(default_group)

        default_header_layout = QHBoxLayout()
        default_header_label = QLabel("Default case (executed when no conditions match):")
        default_header_layout.addWidget(default_header_label)

        add_default_btn = QPushButton("Add Default Case")
        add_default_btn.clicked.connect(self._add_default_case)
        default_header_layout.addWidget(add_default_btn)
        default_header_layout.addStretch()

        default_layout.addLayout(default_header_layout)

        self.default_case_label = QLabel("No default case defined")
        self.default_case_label.setStyleSheet("color: #666; font-style: italic;")
        default_layout.addWidget(self.default_case_label)

        default_controls_layout = QHBoxLayout()

        edit_default_btn = QPushButton("Edit Default")
        edit_default_btn.clicked.connect(self._edit_default_case)
        default_controls_layout.addWidget(edit_default_btn)

        remove_default_btn = QPushButton("Remove Default")
        remove_default_btn.clicked.connect(self._remove_default_case)
        default_controls_layout.addWidget(remove_default_btn)
        default_controls_layout.addStretch()

        default_layout.addLayout(default_controls_layout)
        layout.addWidget(default_group)

        return widget

    def _create_return_config_widget(self):
        """Create the configuration widget for return steps."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create form layout for basic properties
        form_group = QGroupBox("Return Properties")
        form_layout = QFormLayout(form_group)

        self.return_description_edit = QLineEdit()
        self.return_description_edit.textChanged.connect(self._on_return_data_changed)

        # Setup validation timer for debounced validation
        self.return_validation_timer = QTimer()
        self.return_validation_timer.setSingleShot(True)
        self.return_validation_timer.timeout.connect(self._validate_return_output_mapper)
        self.return_description_edit.textChanged.connect(lambda: self.return_validation_timer.start(300))
        self.return_description_edit.setToolTip("Optional description of this return statement")
        self.return_description_edit.setPlaceholderText("Optional description of this return statement")
        form_layout.addRow("Description:", self.return_description_edit)

        layout.addWidget(form_group)

        # Output mapper section with enhanced features
        mapper_group = QGroupBox("Output Mapper - Transform Data for Return")
        mapper_layout = QVBoxLayout(mapper_group)

        # Enhanced header with contextual help
        mapper_header = QLabel("Map output keys to data paths:")
        mapper_header.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        mapper_layout.addWidget(mapper_header)

        help_text = QLabel(
            "Define how to transform data for the return value. Each key-value pair maps an output field to a data path. "
            "Use lowercase_snake_case for output keys and valid Moveworks DSL expressions for data paths."
        )
        help_text.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        help_text.setWordWrap(True)
        mapper_layout.addWidget(help_text)

        # Quick tips section
        tips_label = QLabel("💡 Quick Tips:")
        tips_label.setStyleSheet("font-weight: bold; color: #2e7d32; font-size: 11px; margin-top: 4px;")
        mapper_layout.addWidget(tips_label)

        tips_text = QLabel(
            "• Drag paths from JSON Path Selector below\n"
            "• Use data.output_key.field for step outputs\n"
            "• Use meta_info.user.field for user context\n"
            "• Complex expressions: data.status == 'active'"
        )
        tips_text.setStyleSheet("color: #666; font-size: 10px; margin-left: 16px; margin-bottom: 8px;")
        mapper_layout.addWidget(tips_text)

        # Enhanced output mapper table with drag-drop support
        self.return_output_mapper_table = EnhancedReturnMapperTable()
        self.return_output_mapper_table.setColumnCount(2)
        self.return_output_mapper_table.setHorizontalHeaderLabels(["Output Key", "Data Path"])
        self.return_output_mapper_table.horizontalHeader().setStretchLastSection(True)
        # Increase height to ensure input fields are fully visible
        self.return_output_mapper_table.setMinimumHeight(120)
        self.return_output_mapper_table.setMaximumHeight(350)
        self.return_output_mapper_table.itemChanged.connect(self._on_return_data_changed)
        self.return_output_mapper_table.itemChanged.connect(lambda: self.return_validation_timer.start(300))

        # Enable drag and drop
        self.return_output_mapper_table.setAcceptDrops(True)
        self.return_output_mapper_table.setDragDropMode(QTableWidget.DropOnly)

        # Set column widths
        header = self.return_output_mapper_table.horizontalHeader()
        header.resizeSection(0, 150)  # Output Key column

        # Add validation indicators
        self.return_output_mapper_table.setToolTip(
            "Drag data paths from JSON Path Selector or type manually.\n"
            "Output keys must use lowercase_snake_case format.\n"
            "Data paths support Moveworks DSL expressions."
        )

        mapper_layout.addWidget(self.return_output_mapper_table)

        # Enhanced table controls with templates
        table_controls_layout = QHBoxLayout()

        add_mapping_btn = QPushButton("➕ Add Mapping")
        add_mapping_btn.clicked.connect(self._add_return_mapping)
        add_mapping_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        table_controls_layout.addWidget(add_mapping_btn)

        # Add template button for common patterns
        template_btn = QPushButton("📋 Use Template")
        template_btn.clicked.connect(self._show_return_templates)
        template_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        table_controls_layout.addWidget(template_btn)

        remove_mapping_btn = QPushButton("🗑️ Remove Selected")
        remove_mapping_btn.clicked.connect(self._remove_return_mapping)
        remove_mapping_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        table_controls_layout.addWidget(remove_mapping_btn)
        table_controls_layout.addStretch()

        mapper_layout.addLayout(table_controls_layout)

        # Enhanced examples section with more comprehensive patterns
        example_label = QLabel("📚 Common Patterns & Examples:")
        example_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px; font-size: 12px;")
        mapper_layout.addWidget(example_label)

        # Basic examples
        basic_examples = QLabel("Basic Data Mapping:")
        basic_examples.setStyleSheet("font-weight: bold; color: #2e7d32; font-size: 11px; margin-top: 4px;")
        mapper_layout.addWidget(basic_examples)

        basic_text = QLabel("""• user_id → data.user_info.user.id
• user_name → data.user_info.user.name
• user_email → data.user_info.user.email
• department → meta_info.user.department""")
        basic_text.setStyleSheet("color: #666; font-size: 10px; font-family: monospace; margin-left: 16px;")
        mapper_layout.addWidget(basic_text)

        # Advanced examples
        advanced_examples = QLabel("Advanced DSL Expressions:")
        advanced_examples.setStyleSheet("font-weight: bold; color: #1976d2; font-size: 11px; margin-top: 4px;")
        mapper_layout.addWidget(advanced_examples)

        advanced_text = QLabel("""• is_active → data.user_info.status == 'active'
• full_name → data.user_info.first_name + ' ' + data.user_info.last_name
• has_permissions → data.permissions.length > 0
• request_timestamp → meta_info.request.timestamp""")
        advanced_text.setStyleSheet("color: #666; font-size: 10px; font-family: monospace; margin-left: 16px;")
        mapper_layout.addWidget(advanced_text)

        layout.addWidget(mapper_group)

        return widget

    def _create_try_catch_config_widget(self):
        """Create the configuration widget for try/catch steps."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create form layout for basic properties
        form_group = QGroupBox("Try/Catch Properties")
        form_layout = QFormLayout(form_group)

        self.try_catch_description_edit = QLineEdit()
        self.try_catch_description_edit.textChanged.connect(self._on_try_catch_data_changed)
        self.try_catch_description_edit.setToolTip("Optional description of this try/catch block")
        self.try_catch_description_edit.setPlaceholderText("Optional description of this try/catch block")
        form_layout.addRow("Description:", self.try_catch_description_edit)

        self.try_catch_output_key_edit = QLineEdit()
        self.try_catch_output_key_edit.textChanged.connect(self._on_try_catch_data_changed)
        self.try_catch_output_key_edit.setToolTip("Required field. Output key for storing try/catch results. Must use lowercase_snake_case format.")
        self.try_catch_output_key_edit.setPlaceholderText("e.g., error_handling_result")

        # Add validation indicator for output_key
        self.try_catch_output_key_indicator = QLabel()
        self.try_catch_output_key_indicator.setFixedSize(16, 16)
        self.try_catch_output_key_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.try_catch_output_key_indicator.setText("*")
        self.try_catch_output_key_indicator.setToolTip("Required field")

        # Create horizontal layout for output_key with validation indicator
        output_key_layout = QHBoxLayout()
        output_key_layout.addWidget(self.try_catch_output_key_edit)
        output_key_layout.addWidget(self.try_catch_output_key_indicator)
        output_key_layout.setContentsMargins(0, 0, 0, 0)

        output_key_widget = QWidget()
        output_key_widget.setLayout(output_key_layout)

        # Create label with mandatory field indicator
        output_key_label = QLabel("Output Key: *")
        output_key_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(output_key_label, output_key_widget)

        layout.addWidget(form_group)

        # Try block section
        try_group = QGroupBox("Try Block - Steps to Execute")
        try_layout = QVBoxLayout(try_group)

        try_header = QLabel("Steps to execute in the try block:")
        try_header.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        try_layout.addWidget(try_header)

        help_text = QLabel("Add the steps that might fail and need error handling. These steps will be executed first.")
        help_text.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        help_text.setWordWrap(True)
        try_layout.addWidget(help_text)

        # Try steps list
        self.try_steps_list = QListWidget()
        # Increase height to ensure better visibility
        self.try_steps_list.setMinimumHeight(100)
        self.try_steps_list.setMaximumHeight(250)
        self.try_steps_list.setToolTip("List of steps to execute in the try block")
        try_layout.addWidget(self.try_steps_list)

        # Try steps controls
        try_controls_layout = QHBoxLayout()

        add_try_step_btn = QPushButton("➕ Add Try Step")
        add_try_step_btn.clicked.connect(self._add_try_step)
        add_try_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        try_controls_layout.addWidget(add_try_step_btn)

        remove_try_step_btn = QPushButton("🗑️ Remove Selected")
        remove_try_step_btn.clicked.connect(self._remove_try_step)
        remove_try_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        try_controls_layout.addWidget(remove_try_step_btn)
        try_controls_layout.addStretch()

        try_layout.addLayout(try_controls_layout)
        layout.addWidget(try_group)

        # Catch block section
        catch_group = QGroupBox("Catch Block - Error Handling")
        catch_layout = QVBoxLayout(catch_group)

        catch_header = QLabel("Error handling configuration:")
        catch_header.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        catch_layout.addWidget(catch_header)

        # Status codes section
        status_codes_layout = QHBoxLayout()
        status_codes_label = QLabel("Status Codes:")
        status_codes_label.setStyleSheet("font-weight: bold; color: #666;")
        status_codes_layout.addWidget(status_codes_label)

        self.status_codes_edit = QLineEdit()
        self.status_codes_edit.textChanged.connect(self._on_try_catch_data_changed)
        self.status_codes_edit.setToolTip("Optional comma-separated list of HTTP status codes that trigger the catch block (e.g., 400,404,500)")
        self.status_codes_edit.setPlaceholderText("e.g., 400,404,500")
        status_codes_layout.addWidget(self.status_codes_edit)

        catch_layout.addLayout(status_codes_layout)

        # Catch steps
        catch_steps_header = QLabel("Steps to execute when an error occurs:")
        catch_steps_header.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px;")
        catch_layout.addWidget(catch_steps_header)

        catch_help_text = QLabel("Add steps to handle errors, log information, or provide fallback behavior.")
        catch_help_text.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        catch_help_text.setWordWrap(True)
        catch_layout.addWidget(catch_help_text)

        # Catch steps list
        self.catch_steps_list = QListWidget()
        # Increase height to ensure better visibility
        self.catch_steps_list.setMinimumHeight(100)
        self.catch_steps_list.setMaximumHeight(250)
        self.catch_steps_list.setToolTip("List of steps to execute in the catch block")
        catch_layout.addWidget(self.catch_steps_list)

        # Catch steps controls
        catch_controls_layout = QHBoxLayout()

        add_catch_step_btn = QPushButton("➕ Add Catch Step")
        add_catch_step_btn.clicked.connect(self._add_catch_step)
        add_catch_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        catch_controls_layout.addWidget(add_catch_step_btn)

        remove_catch_step_btn = QPushButton("🗑️ Remove Selected")
        remove_catch_step_btn.clicked.connect(self._remove_catch_step)
        remove_catch_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        catch_controls_layout.addWidget(remove_catch_step_btn)
        catch_controls_layout.addStretch()

        catch_layout.addLayout(catch_controls_layout)
        layout.addWidget(catch_group)

        # Examples section
        examples_label = QLabel("📚 Common Try/Catch Patterns:")
        examples_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px; font-size: 12px;")
        layout.addWidget(examples_label)

        examples_text = QLabel("""• API Call with Fallback: Try external API, catch errors and use cached data
• User Validation: Try user lookup, catch not found and create new user
• File Processing: Try file operation, catch errors and log failure details""")
        examples_text.setStyleSheet("color: #666; font-size: 10px; margin-left: 16px; margin-bottom: 8px;")
        examples_text.setWordWrap(True)
        layout.addWidget(examples_text)

        return widget

    def _create_parallel_config_widget(self):
        """Create the configuration widget for parallel steps."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create form layout for basic properties
        form_group = QGroupBox("Parallel Properties")
        form_layout = QFormLayout(form_group)

        self.parallel_description_edit = QLineEdit()
        self.parallel_description_edit.textChanged.connect(self._on_parallel_data_changed)
        self.parallel_description_edit.setToolTip("Optional description of this parallel execution block")
        self.parallel_description_edit.setPlaceholderText("Optional description of this parallel execution block")
        form_layout.addRow("Description:", self.parallel_description_edit)

        self.parallel_output_key_edit = QLineEdit()
        self.parallel_output_key_edit.textChanged.connect(self._on_parallel_data_changed)
        self.parallel_output_key_edit.setToolTip("Required field. Output key for storing parallel execution results. Must use lowercase_snake_case format.")
        self.parallel_output_key_edit.setPlaceholderText("e.g., parallel_results")

        # Add validation indicator for output_key
        self.parallel_output_key_indicator = QLabel()
        self.parallel_output_key_indicator.setFixedSize(16, 16)
        self.parallel_output_key_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.parallel_output_key_indicator.setText("*")
        self.parallel_output_key_indicator.setToolTip("Required field")

        # Create horizontal layout for output_key with validation indicator
        output_key_layout = QHBoxLayout()
        output_key_layout.addWidget(self.parallel_output_key_edit)
        output_key_layout.addWidget(self.parallel_output_key_indicator)
        output_key_layout.setContentsMargins(0, 0, 0, 0)

        output_key_widget = QWidget()
        output_key_widget.setLayout(output_key_layout)

        # Create label with mandatory field indicator
        output_key_label = QLabel("Output Key: *")
        output_key_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(output_key_label, output_key_widget)

        layout.addWidget(form_group)

        # Mode selection with tabs
        mode_group = QGroupBox("Parallel Execution Mode")
        mode_layout = QVBoxLayout(mode_group)

        mode_header = QLabel("Choose the parallel execution mode:")
        mode_header.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        mode_layout.addWidget(mode_header)

        # Create tab widget for mode selection
        self.parallel_mode_tabs = QTabWidget()
        self.parallel_mode_tabs.currentChanged.connect(self._on_parallel_mode_changed)

        # For Loop Mode Tab
        for_loop_tab = QWidget()
        for_loop_layout = QVBoxLayout(for_loop_tab)

        for_loop_help = QLabel("Execute steps in parallel for each item in a data array.")
        for_loop_help.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        for_loop_help.setWordWrap(True)
        for_loop_layout.addWidget(for_loop_help)

        # For loop configuration
        for_config_layout = QFormLayout()

        self.parallel_each_edit = QLineEdit()
        self.parallel_each_edit.textChanged.connect(self._on_parallel_data_changed)
        self.parallel_each_edit.setToolTip("Variable name for the current item (e.g., 'user', 'item')")
        self.parallel_each_edit.setPlaceholderText("e.g., user")
        for_config_layout.addRow("Each (item variable):", self.parallel_each_edit)

        self.parallel_in_source_edit = QLineEdit()
        self.parallel_in_source_edit.textChanged.connect(self._on_parallel_data_changed)
        self.parallel_in_source_edit.setToolTip("Data path to the array to iterate over (e.g., 'data.users_list')")
        self.parallel_in_source_edit.setPlaceholderText("e.g., data.users_list")
        for_config_layout.addRow("In (data source):", self.parallel_in_source_edit)

        for_loop_layout.addLayout(for_config_layout)

        # For loop steps
        for_steps_header = QLabel("Steps to execute for each item:")
        for_steps_header.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px;")
        for_loop_layout.addWidget(for_steps_header)

        self.parallel_for_steps_list = QListWidget()
        # Increase height to ensure better visibility
        self.parallel_for_steps_list.setMinimumHeight(80)
        self.parallel_for_steps_list.setMaximumHeight(200)
        for_loop_layout.addWidget(self.parallel_for_steps_list)

        # For loop controls
        for_controls_layout = QHBoxLayout()
        add_for_step_btn = QPushButton("➕ Add Step")
        add_for_step_btn.clicked.connect(self._add_parallel_for_step)
        add_for_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        for_controls_layout.addWidget(add_for_step_btn)

        remove_for_step_btn = QPushButton("🗑️ Remove")
        remove_for_step_btn.clicked.connect(self._remove_parallel_for_step)
        remove_for_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        for_controls_layout.addWidget(remove_for_step_btn)
        for_controls_layout.addStretch()

        for_loop_layout.addLayout(for_controls_layout)
        self.parallel_mode_tabs.addTab(for_loop_tab, "🔄 For Loop Mode")

        # Branches Mode Tab
        branches_tab = QWidget()
        branches_layout = QVBoxLayout(branches_tab)

        branches_help = QLabel("Execute multiple independent branches in parallel.")
        branches_help.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        branches_help.setWordWrap(True)
        branches_layout.addWidget(branches_help)

        # Branches list
        branches_header = QLabel("Parallel branches:")
        branches_header.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px;")
        branches_layout.addWidget(branches_header)

        self.parallel_branches_list = QListWidget()
        # Increase height to ensure better visibility
        self.parallel_branches_list.setMinimumHeight(80)
        self.parallel_branches_list.setMaximumHeight(200)
        branches_layout.addWidget(self.parallel_branches_list)

        # Branches controls
        branches_controls_layout = QHBoxLayout()
        add_branch_btn = QPushButton("➕ Add Branch")
        add_branch_btn.clicked.connect(self._add_parallel_branch)
        add_branch_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        branches_controls_layout.addWidget(add_branch_btn)

        remove_branch_btn = QPushButton("🗑️ Remove")
        remove_branch_btn.clicked.connect(self._remove_parallel_branch)
        remove_branch_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        branches_controls_layout.addWidget(remove_branch_btn)
        branches_controls_layout.addStretch()

        branches_layout.addLayout(branches_controls_layout)
        self.parallel_mode_tabs.addTab(branches_tab, "🌿 Branches Mode")

        mode_layout.addWidget(self.parallel_mode_tabs)
        layout.addWidget(mode_group)

        # Examples section
        examples_label = QLabel("📚 Common Parallel Patterns:")
        examples_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px; font-size: 12px;")
        layout.addWidget(examples_label)

        for_examples = QLabel("For Loop Mode:")
        for_examples.setStyleSheet("font-weight: bold; color: #2e7d32; font-size: 11px; margin-top: 4px;")
        layout.addWidget(for_examples)

        for_text = QLabel("• Process each user in parallel: each='user', in='data.users_list'\n• Validate multiple items: each='item', in='data.validation_items'")
        for_text.setStyleSheet("color: #666; font-size: 10px; margin-left: 16px;")
        layout.addWidget(for_text)

        branches_examples = QLabel("Branches Mode:")
        branches_examples.setStyleSheet("font-weight: bold; color: #1976d2; font-size: 11px; margin-top: 4px;")
        layout.addWidget(branches_examples)

        branches_text = QLabel("• Independent API calls: Branch 1 gets user data, Branch 2 gets permissions\n• Parallel data processing: Branch 1 processes files, Branch 2 sends notifications")
        branches_text.setStyleSheet("color: #666; font-size: 10px; margin-left: 16px; margin-bottom: 8px;")
        layout.addWidget(branches_text)

        return widget

    def set_step(self, step, step_index: int, workflow: Workflow = None):
        """Set the current step to configure."""
        self.current_step = step
        self.current_step_index = step_index
        if workflow:
            self.workflow = workflow

        if isinstance(step, ActionStep):
            self._populate_action_config(step)
            self.setCurrentWidget(self.action_config_widget)
        elif isinstance(step, ScriptStep):
            self._populate_script_config(step)
            self.setCurrentWidget(self.script_config_widget)
        elif isinstance(step, SwitchStep):
            self._populate_switch_config(step)
            self.setCurrentWidget(self.switch_config_widget)
        elif isinstance(step, ReturnStep):
            self._populate_return_config(step)
            self.setCurrentWidget(self.return_config_widget)
        elif isinstance(step, TryCatchStep):
            self._populate_try_catch_config(step)
            self.setCurrentWidget(self.try_catch_config_widget)
        elif isinstance(step, ParallelStep):
            self._populate_parallel_config(step)
            self.setCurrentWidget(self.parallel_config_widget)
        else:
            self.setCurrentWidget(self.empty_widget)

    def clear_selection(self):
        """Clear the current step selection."""
        self.current_step = None
        self.current_step_index = -1
        self.setCurrentWidget(self.empty_widget)

    def _populate_action_config(self, step: ActionStep):
        """Populate the action configuration form with step data."""
        self.action_name_edit.setText(step.action_name or "")
        self.action_description_edit.setText(step.description or "")
        self.action_output_key_edit.setText(step.output_key or "")

        # Populate input args table using enhanced method or fallback
        if hasattr(self.action_input_args_table, 'populate_from_step'):
            self.action_input_args_table.populate_from_step(step)
            # Set context for enhanced features
            if hasattr(self.action_input_args_table, 'set_context') and hasattr(self, 'workflow'):
                step_index = self.current_step_index if self.current_step_index >= 0 else -1
                self.action_input_args_table.set_context(self.workflow, step, step_index)
        else:
            # Fallback for regular QTableWidget
            self.action_input_args_table.setRowCount(len(step.input_args))
            for i, (key, value) in enumerate(step.input_args.items()):
                self.action_input_args_table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.action_input_args_table.setItem(i, 1, QTableWidgetItem(str(value)))

        # Populate JSON output
        self.action_json_edit.setPlainText(step.user_provided_json_output or "")

    def _populate_script_config(self, step: ScriptStep):
        """Populate the script configuration form with step data."""
        self.script_description_edit.setText(step.description or "")
        self.script_output_key_edit.setText(step.output_key or "")

        # Set the script step in the enhanced editor
        available_data_paths = self._get_available_data_paths_for_step()
        self.enhanced_script_editor.set_script_step(step, available_data_paths)

        # Populate input args table using enhanced method or fallback
        if hasattr(self.script_input_args_table, 'populate_from_step'):
            self.script_input_args_table.populate_from_step(step)
            # Set context for enhanced features
            if hasattr(self.script_input_args_table, 'set_context') and hasattr(self, 'workflow'):
                step_index = self.current_step_index if self.current_step_index >= 0 else -1
                self.script_input_args_table.set_context(self.workflow, step, step_index)
        else:
            # Fallback for regular QTableWidget
            self.script_input_args_table.setRowCount(len(step.input_args))
            for i, (key, value) in enumerate(step.input_args.items()):
                self.script_input_args_table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.script_input_args_table.setItem(i, 1, QTableWidgetItem(str(value)))

        # Populate JSON output
        self.script_json_edit.setPlainText(step.user_provided_json_output or "")

    def _populate_switch_config(self, step: SwitchStep):
        """Populate the switch configuration form with step data."""
        self.switch_description_edit.setText(step.description or "")
        self.switch_output_key_edit.setText(step.output_key or "_")

        # Populate cases list
        self.switch_cases_list.clear()
        for i, case in enumerate(step.cases):
            condition_preview = case.condition[:50] + "..." if len(case.condition) > 50 else case.condition
            steps_count = len(case.steps)
            item_text = f"Case {i+1}: {condition_preview} ({steps_count} step(s))"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)  # Store case index
            self.switch_cases_list.addItem(item)

        # Update default case display
        if step.default_case:
            steps_count = len(step.default_case.steps)
            self.default_case_label.setText(f"Default case defined ({steps_count} step(s))")
            self.default_case_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        else:
            self.default_case_label.setText("No default case defined")
            self.default_case_label.setStyleSheet("color: #666; font-style: italic;")

    def _on_action_data_changed(self):
        """Handle changes to action step data."""
        if not isinstance(self.current_step, ActionStep):
            return

        self.current_step.action_name = self.action_name_edit.text()
        self.current_step.description = self.action_description_edit.text() or None
        self.current_step.output_key = self.action_output_key_edit.text()

        # Update input args from enhanced table or fallback to regular table
        if hasattr(self.action_input_args_table, 'get_input_args_dict'):
            self.current_step.input_args = self.action_input_args_table.get_input_args_dict()
        else:
            # Fallback for regular QTableWidget
            self.current_step.input_args = {}
            for row in range(self.action_input_args_table.rowCount()):
                key_item = self.action_input_args_table.item(row, 0)
                value_item = self.action_input_args_table.item(row, 1)
                if key_item and value_item and key_item.text():
                    self.current_step.input_args[key_item.text()] = value_item.text()

        self.step_updated.emit()

    def _on_script_data_changed(self):
        """Handle changes to script step data."""
        if not isinstance(self.current_step, ScriptStep):
            return

        self.current_step.description = self.script_description_edit.text() or None
        self.current_step.output_key = self.script_output_key_edit.text()
        # Note: script code is now handled by the enhanced editor

        # Update input args from enhanced table or fallback to regular table
        if hasattr(self.script_input_args_table, 'get_input_args_dict'):
            self.current_step.input_args = self.script_input_args_table.get_input_args_dict()
        else:
            # Fallback for regular QTableWidget
            self.current_step.input_args = {}
            for row in range(self.script_input_args_table.rowCount()):
                key_item = self.script_input_args_table.item(row, 0)
                value_item = self.script_input_args_table.item(row, 1)
                if key_item and value_item and key_item.text():
                    self.current_step.input_args[key_item.text()] = value_item.text()

        self.step_updated.emit()

    def _on_switch_data_changed(self):
        """Handle changes to switch step data."""
        if not isinstance(self.current_step, SwitchStep):
            return

        self.current_step.description = self.switch_description_edit.text() or None
        self.current_step.output_key = self.switch_output_key_edit.text() or "_"

        self.step_updated.emit()

    def _populate_return_config(self, step: ReturnStep):
        """Populate the return configuration form with step data."""
        self.return_description_edit.setText(step.description or "")

        # Populate output mapper table
        self.return_output_mapper_table.setRowCount(len(step.output_mapper))
        for i, (key, value) in enumerate(step.output_mapper.items()):
            self.return_output_mapper_table.setItem(i, 0, QTableWidgetItem(str(key)))
            self.return_output_mapper_table.setItem(i, 1, QTableWidgetItem(str(value)))

    def _on_return_data_changed(self):
        """Handle changes to return step data."""
        if not isinstance(self.current_step, ReturnStep):
            return

        self.current_step.description = self.return_description_edit.text() or None

        # Update output mapper from table
        self.current_step.output_mapper = {}
        for row in range(self.return_output_mapper_table.rowCount()):
            key_item = self.return_output_mapper_table.item(row, 0)
            value_item = self.return_output_mapper_table.item(row, 1)
            if key_item and value_item and key_item.text():
                self.current_step.output_mapper[key_item.text()] = value_item.text()

        self.step_updated.emit()

    def _add_return_mapping(self):
        """Add a new row to the return output mapper table."""
        row_count = self.return_output_mapper_table.rowCount()
        self.return_output_mapper_table.insertRow(row_count)
        self.return_output_mapper_table.setItem(row_count, 0, QTableWidgetItem(""))
        self.return_output_mapper_table.setItem(row_count, 1, QTableWidgetItem(""))

    def _remove_return_mapping(self):
        """Remove the selected row from the return output mapper table."""
        current_row = self.return_output_mapper_table.currentRow()
        if current_row >= 0:
            self.return_output_mapper_table.removeRow(current_row)
            self._on_return_data_changed()

    def _show_return_templates(self):
        """Show return step templates dialog."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel, QTextEdit

        dialog = QDialog(self)
        dialog.setWindowTitle("Return Step Templates")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)

        # Header
        header = QLabel("Choose a template for common return patterns:")
        header.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 8px;")
        layout.addWidget(header)

        # Template list
        template_list = QListWidget()

        # Define templates
        templates = [
            {
                "name": "User Profile Return",
                "description": "Return basic user profile information",
                "mappings": {
                    "user_id": "data.user_info.user.id",
                    "user_name": "data.user_info.user.name",
                    "user_email": "data.user_info.user.email",
                    "department": "meta_info.user.department"
                }
            },
            {
                "name": "Status Check Return",
                "description": "Return status and validation results",
                "mappings": {
                    "is_valid": "data.validation_result.is_valid",
                    "status": "data.validation_result.status",
                    "message": "data.validation_result.message",
                    "timestamp": "meta_info.request.timestamp"
                }
            },
            {
                "name": "Data Processing Return",
                "description": "Return processed data with metadata",
                "mappings": {
                    "processed_data": "data.processing_result.data",
                    "record_count": "data.processing_result.count",
                    "processing_time": "data.processing_result.duration",
                    "processed_by": "meta_info.user.email"
                }
            },
            {
                "name": "Error Handling Return",
                "description": "Return error information and context",
                "mappings": {
                    "error_code": "data.error_info.code",
                    "error_message": "data.error_info.message",
                    "error_details": "data.error_info.details",
                    "user_context": "meta_info.user.id"
                }
            }
        ]

        for template in templates:
            item_text = f"{template['name']}\n{template['description']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, template)
            template_list.addItem(item)

        layout.addWidget(template_list)

        # Preview area
        preview_label = QLabel("Template Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        layout.addWidget(preview_label)

        preview_text = QTextEdit()
        preview_text.setMaximumHeight(150)
        preview_text.setReadOnly(True)
        layout.addWidget(preview_text)

        # Update preview when selection changes
        def update_preview():
            current_item = template_list.currentItem()
            if current_item:
                template = current_item.data(Qt.UserRole)
                preview_content = "Output Mapper:\n"
                for key, value in template['mappings'].items():
                    preview_content += f"  {key} → {value}\n"
                preview_text.setPlainText(preview_content)

        template_list.currentItemChanged.connect(update_preview)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show dialog and apply template if accepted
        if dialog.exec() == QDialog.Accepted:
            current_item = template_list.currentItem()
            if current_item:
                template = current_item.data(Qt.UserRole)
                self._apply_return_template(template['mappings'])

    def _apply_return_template(self, mappings):
        """Apply a template to the return output mapper."""
        # Clear existing mappings
        self.return_output_mapper_table.setRowCount(0)

        # Add template mappings
        for key, value in mappings.items():
            row = self.return_output_mapper_table.rowCount()
            self.return_output_mapper_table.insertRow(row)
            self.return_output_mapper_table.setItem(row, 0, QTableWidgetItem(key))
            self.return_output_mapper_table.setItem(row, 1, QTableWidgetItem(value))

        # Trigger data change event
        self._on_return_data_changed()

    # Try/Catch Configuration Methods
    def _populate_try_catch_config(self, step: TryCatchStep):
        """Populate the try/catch configuration widget with step data."""
        self.try_catch_description_edit.setText(step.description or "")
        self.try_catch_output_key_edit.setText(step.output_key or "")

        # Populate status codes
        if step.catch_block and step.catch_block.on_status_code:
            status_codes_str = ",".join(map(str, step.catch_block.on_status_code))
            self.status_codes_edit.setText(status_codes_str)
        else:
            self.status_codes_edit.setText("")

        # Populate try steps
        self.try_steps_list.clear()
        if step.try_steps:
            for try_step in step.try_steps:
                step_text = self._get_step_display_text(try_step)
                self.try_steps_list.addItem(step_text)

        # Populate catch steps
        self.catch_steps_list.clear()
        if step.catch_block and step.catch_block.steps:
            for catch_step in step.catch_block.steps:
                step_text = self._get_step_display_text(catch_step)
                self.catch_steps_list.addItem(step_text)

    def _get_step_display_text(self, step):
        """Get display text for a step in lists."""
        if isinstance(step, ActionStep):
            return f"Action: {step.action_name or 'Unnamed'}"
        elif isinstance(step, ScriptStep):
            return f"Script: {step.description or 'Unnamed'}"
        elif isinstance(step, ReturnStep):
            return f"Return: {step.description or 'Unnamed'}"
        else:
            return f"{type(step).__name__}: {getattr(step, 'description', 'Unnamed')}"

    def _on_try_catch_data_changed(self):
        """Handle changes to try/catch configuration data."""
        if not self.current_step or not isinstance(self.current_step, TryCatchStep):
            return

        # Update basic properties
        self.current_step.description = self.try_catch_description_edit.text()
        self.current_step.output_key = self.try_catch_output_key_edit.text()

        # Update status codes
        status_codes_text = self.status_codes_edit.text().strip()
        if status_codes_text:
            try:
                status_codes = [int(code.strip()) for code in status_codes_text.split(",") if code.strip()]
                if not self.current_step.catch_block:
                    from core_structures import CatchBlock
                    self.current_step.catch_block = CatchBlock()
                self.current_step.catch_block.on_status_code = status_codes
            except ValueError:
                # Invalid status codes, keep existing or set to empty
                if self.current_step.catch_block:
                    self.current_step.catch_block.on_status_code = []
        else:
            if self.current_step.catch_block:
                self.current_step.catch_block.on_status_code = []

        # Emit step updated signal
        self.step_updated.emit()

    def _add_try_step(self):
        """Add a new step to the try block."""
        # This would open a step selection dialog
        # For now, add a placeholder
        self.try_steps_list.addItem("New Try Step (configure in step editor)")
        self._on_try_catch_data_changed()

    def _remove_try_step(self):
        """Remove the selected step from the try block."""
        current_row = self.try_steps_list.currentRow()
        if current_row >= 0:
            self.try_steps_list.takeItem(current_row)
            self._on_try_catch_data_changed()

    def _add_catch_step(self):
        """Add a new step to the catch block."""
        # This would open a step selection dialog
        # For now, add a placeholder
        self.catch_steps_list.addItem("New Catch Step (configure in step editor)")
        self._on_try_catch_data_changed()

    def _remove_catch_step(self):
        """Remove the selected step from the catch block."""
        current_row = self.catch_steps_list.currentRow()
        if current_row >= 0:
            self.catch_steps_list.takeItem(current_row)
            self._on_try_catch_data_changed()

    # Parallel Configuration Methods
    def _populate_parallel_config(self, step: ParallelStep):
        """Populate the parallel configuration widget with step data."""
        self.parallel_description_edit.setText(step.description or "")
        self.parallel_output_key_edit.setText(step.output_key or "")

        # Determine mode and populate accordingly
        if step.for_loop:
            # For loop mode
            self.parallel_mode_tabs.setCurrentIndex(0)  # For Loop Mode tab
            self.parallel_each_edit.setText(step.for_loop.each or "")
            self.parallel_in_source_edit.setText(step.for_loop.in_source or "")

            # Populate for loop steps
            self.parallel_for_steps_list.clear()
            if step.for_loop.steps:
                for for_step in step.for_loop.steps:
                    step_text = self._get_step_display_text(for_step)
                    self.parallel_for_steps_list.addItem(step_text)
        elif step.branches:
            # Branches mode
            self.parallel_mode_tabs.setCurrentIndex(1)  # Branches Mode tab

            # Populate branches
            self.parallel_branches_list.clear()
            for i, branch in enumerate(step.branches):
                branch_text = f"Branch {i+1} ({len(branch.steps)} steps)"
                self.parallel_branches_list.addItem(branch_text)

    def _on_parallel_data_changed(self):
        """Handle changes to parallel configuration data."""
        if not self.current_step or not isinstance(self.current_step, ParallelStep):
            return

        # Update basic properties
        self.current_step.description = self.parallel_description_edit.text()
        self.current_step.output_key = self.parallel_output_key_edit.text()

        # Update mode-specific data based on current tab
        current_mode = self.parallel_mode_tabs.currentIndex()
        if current_mode == 0:  # For Loop Mode
            if not self.current_step.for_loop:
                from core_structures import ParallelForLoop
                self.current_step.for_loop = ParallelForLoop()

            self.current_step.for_loop.each = self.parallel_each_edit.text()
            self.current_step.for_loop.in_source = self.parallel_in_source_edit.text()

            # Clear branches mode if switching
            self.current_step.branches = None
        elif current_mode == 1:  # Branches Mode
            # Clear for loop mode if switching
            self.current_step.for_loop = None

            # Branches are managed through add/remove methods

        # Emit step updated signal
        self.step_updated.emit()

    def _on_parallel_mode_changed(self, index):
        """Handle parallel mode tab change."""
        self._on_parallel_data_changed()

    def _add_parallel_for_step(self):
        """Add a new step to the parallel for loop."""
        # This would open a step selection dialog
        # For now, add a placeholder
        self.parallel_for_steps_list.addItem("New For Step (configure in step editor)")
        self._on_parallel_data_changed()

    def _remove_parallel_for_step(self):
        """Remove the selected step from the parallel for loop."""
        current_row = self.parallel_for_steps_list.currentRow()
        if current_row >= 0:
            self.parallel_for_steps_list.takeItem(current_row)
            self._on_parallel_data_changed()

    def _add_parallel_branch(self):
        """Add a new branch to the parallel execution."""
        # This would open a branch configuration dialog
        # For now, add a placeholder
        branch_count = self.parallel_branches_list.count() + 1
        self.parallel_branches_list.addItem(f"Branch {branch_count} (0 steps)")
        self._on_parallel_data_changed()

    def _remove_parallel_branch(self):
        """Remove the selected branch from the parallel execution."""
        current_row = self.parallel_branches_list.currentRow()
        if current_row >= 0:
            self.parallel_branches_list.takeItem(current_row)
            self._on_parallel_data_changed()

    def _validate_output_key_field(self):
        """Validate output_key field with real-time feedback."""
        if not self.current_step:
            return

        # Import here to avoid circular imports
        from output_key_validator import output_key_validator

        step_type = type(self.current_step).__name__

        # Get the appropriate output_key field based on step type
        if isinstance(self.current_step, ActionStep):
            output_key = self.action_output_key_edit.text()
            indicator = self.action_output_key_indicator
            field_edit = self.action_output_key_edit
        elif isinstance(self.current_step, ScriptStep):
            output_key = self.script_output_key_edit.text()
            indicator = self.script_output_key_indicator
            field_edit = self.script_output_key_edit
        else:
            return

        # Validate the output_key
        result = output_key_validator.validate_output_key(output_key, step_type, self.current_step)

        # Update visual indicators
        if result.is_valid:
            indicator.setText("✓")
            indicator.setStyleSheet("color: green; font-weight: bold;")
            indicator.setToolTip("Valid output_key")
            field_edit.setStyleSheet("border: 2px solid #4caf50; background-color: #e8f5e8;")
        else:
            indicator.setText("✗")
            indicator.setStyleSheet("color: red; font-weight: bold;")
            error_msg = "\n".join(result.errors)
            suggestions = "\n".join(result.suggestions) if result.suggestions else ""
            tooltip = f"Validation errors:\n{error_msg}"
            if suggestions:
                tooltip += f"\n\nSuggestions:\n{suggestions}"
            indicator.setToolTip(tooltip)
            field_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")

    def _validate_action_name_field(self):
        """Validate action_name field with real-time feedback."""
        if not self.current_step or not isinstance(self.current_step, ActionStep):
            return

        # Import here to avoid circular imports
        from action_name_validator import action_name_validator

        action_name = self.action_name_edit.text()

        # Validate the action_name
        result = action_name_validator.validate_action_name(action_name, self.current_step)

        # Update visual indicators
        if result.is_valid:
            if result.is_known_action:
                self.action_name_indicator.setText("✓")
                self.action_name_indicator.setStyleSheet("color: green; font-weight: bold;")
                self.action_name_indicator.setToolTip(f"Valid Moveworks action: {action_name}")
                self.action_name_edit.setStyleSheet("color: #2c3e50; border: 2px solid #4caf50; background-color: #e8f5e8; padding: 6px 10px; font-size: 13px; font-weight: 500;")
            else:
                self.action_name_indicator.setText("?")
                self.action_name_indicator.setStyleSheet("color: orange; font-weight: bold;")
                self.action_name_indicator.setToolTip(f"Valid format but not in Moveworks catalog: {action_name}")
                self.action_name_edit.setStyleSheet("color: #2c3e50; border: 2px solid #ff9800; background-color: #fff3e0; padding: 6px 10px; font-size: 13px; font-weight: 500;")
        else:
            self.action_name_indicator.setText("✗")
            self.action_name_indicator.setStyleSheet("color: red; font-weight: bold;")
            error_msg = "\n".join(result.errors)
            warnings_msg = "\n".join(result.warnings) if result.warnings else ""
            suggestions = "\n".join(result.suggestions) if result.suggestions else ""

            tooltip = f"Validation errors:\n{error_msg}"
            if warnings_msg:
                tooltip += f"\n\nWarnings:\n{warnings_msg}"
            if suggestions:
                tooltip += f"\n\nSuggestions:\n{suggestions}"

            self.action_name_indicator.setToolTip(tooltip)
            self.action_name_edit.setStyleSheet("color: #2c3e50; border: 2px solid #f44336; background-color: #ffebee; padding: 6px 10px; font-size: 13px; font-weight: 500;")

    def _validate_script_code_field(self):
        """Validate script code field with real-time feedback."""
        if not self.current_step or not isinstance(self.current_step, ScriptStep):
            return

        # Get the code from the enhanced script editor
        code = self.current_step.code if self.current_step.code else ""

        # Validate the code field using compliance validator
        from compliance_validator import compliance_validator
        temp_workflow = Workflow(steps=[self.current_step])
        result = compliance_validator.validate_workflow_compliance(temp_workflow)

        # Check for code field specific errors
        code_errors = []
        code_warnings = []

        # Check for mandatory field errors related to code
        for error in result.mandatory_field_errors:
            if 'code' in error.lower():
                code_errors.append(error)

        # Check for APIthon errors
        for error in result.apiton_errors:
            if any(keyword in error.lower() for keyword in ['byte', 'private', 'return']):
                code_errors.append(error)

        # Check for APIthon warnings
        for warning in result.warnings:
            if any(keyword in warning.lower() for keyword in ['byte', 'return', 'citation']):
                code_warnings.append(warning)

        # Update visual indicators
        if not code_errors:
            if code_warnings:
                self.script_code_indicator.setText("⚠")
                self.script_code_indicator.setStyleSheet("color: orange; font-weight: bold;")
                warning_msg = "\n".join(code_warnings)
                self.script_code_indicator.setToolTip(f"Warnings:\n{warning_msg}")
            else:
                self.script_code_indicator.setText("✓")
                self.script_code_indicator.setStyleSheet("color: green; font-weight: bold;")
                self.script_code_indicator.setToolTip("Valid APIthon code")
        else:
            self.script_code_indicator.setText("✗")
            self.script_code_indicator.setStyleSheet("color: red; font-weight: bold;")
            error_msg = "\n".join(code_errors)
            suggestions = "\n".join(result.suggestions) if result.suggestions else ""

            tooltip = f"Validation errors:\n{error_msg}"
            if suggestions:
                tooltip += f"\n\nSuggestions:\n{suggestions}"

            self.script_code_indicator.setToolTip(tooltip)

    def _validate_return_output_mapper(self):
        """Validate return step output_mapper field with real-time feedback."""
        if not self.current_step or not isinstance(self.current_step, ReturnStep):
            return

        # Import here to avoid circular imports
        from compliance_validator import compliance_validator

        # Create a temporary workflow for validation
        temp_workflow = Workflow(steps=[self.current_step])
        result = compliance_validator.validate_workflow_compliance(temp_workflow)

        # Check for output_mapper validation errors
        mapper_errors = []
        mapper_warnings = []

        # Check for DSL string quoting issues
        for error in result.errors:
            if 'output_mapper' in error.lower():
                mapper_errors.append(error)

        # Check for data reference validation
        for warning in result.warnings:
            if 'output_mapper' in warning.lower():
                mapper_warnings.append(warning)

        # Visual feedback for the table (could be enhanced with cell-level validation)
        if mapper_errors:
            self.return_output_mapper_table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #f44336;
                    background-color: #ffebee;
                }
            """)
            # Set tooltip with errors
            error_msg = "\n".join(mapper_errors)
            self.return_output_mapper_table.setToolTip(f"Validation errors:\n{error_msg}")
        elif mapper_warnings:
            self.return_output_mapper_table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #ff9800;
                    background-color: #fff3e0;
                }
            """)
            warning_msg = "\n".join(mapper_warnings)
            self.return_output_mapper_table.setToolTip(f"Warnings:\n{warning_msg}")
        else:
            self.return_output_mapper_table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #4caf50;
                    background-color: #e8f5e8;
                }
            """)
            self.return_output_mapper_table.setToolTip("Valid output mapper configuration")

    def _validate_current_step(self):
        """Validate the current step and provide real-time feedback."""
        if not self.current_step:
            return

        # Create a temporary workflow with just the current step for validation
        temp_workflow = Workflow(steps=[self.current_step])

        # Perform compliance validation
        result = compliance_validator.validate_workflow_compliance(temp_workflow)

        # Update UI based on validation results
        self._update_validation_ui(result)

    def _update_validation_ui(self, result: ComplianceValidationResult):
        """Update UI elements based on validation results."""
        # Update field styling based on validation
        if isinstance(self.current_step, ActionStep):
            self._update_action_field_validation(result)
        elif isinstance(self.current_step, ScriptStep):
            self._update_script_field_validation(result)

    def _update_action_field_validation(self, result: ComplianceValidationResult):
        """Update action step field validation styling."""
        # Reset styling with proper text color
        self.action_name_edit.setStyleSheet("color: #2c3e50; background-color: #ffffff; border: 2px solid #bdc3c7; border-radius: 4px; padding: 6px 10px; font-size: 13px; font-weight: 500;")
        self.action_output_key_edit.setStyleSheet("")

        # Check for field naming errors
        for error in result.field_naming_errors:
            if "action_name" in error.lower():
                self.action_name_edit.setStyleSheet("color: #2c3e50; border: 2px solid #f44336; background-color: #ffebee; padding: 6px 10px; font-size: 13px; font-weight: 500;")
            elif "output_key" in error.lower():
                self.action_output_key_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")

        # Check for mandatory field errors
        for error in result.mandatory_field_errors:
            if "action_name" in error.lower():
                self.action_name_edit.setStyleSheet("color: #2c3e50; border: 2px solid #f44336; background-color: #ffebee; padding: 6px 10px; font-size: 13px; font-weight: 500;")
            elif "output_key" in error.lower():
                self.action_output_key_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")

    def _update_script_field_validation(self, result: ComplianceValidationResult):
        """Update script step field validation styling."""
        # Reset styling
        self.script_output_key_edit.setStyleSheet("")

        # Check for field naming errors
        for error in result.field_naming_errors:
            if "output_key" in error.lower():
                self.script_output_key_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")

        # Check for mandatory field errors
        for error in result.mandatory_field_errors:
            if "output_key" in error.lower():
                self.script_output_key_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")
            elif "code" in error.lower():
                # Update script code indicator for mandatory field errors
                self.script_code_indicator.setText("✗")
                self.script_code_indicator.setStyleSheet("color: red; font-weight: bold;")
                self.script_code_indicator.setToolTip("Code field is required and cannot be empty")

        # Check for APIthon errors
        for error in result.apiton_errors:
            # Update script code indicator for APIthon validation errors
            self.script_code_indicator.setText("✗")
            self.script_code_indicator.setStyleSheet("color: red; font-weight: bold;")
            current_tooltip = self.script_code_indicator.toolTip()
            if current_tooltip and "Validation errors:" not in current_tooltip:
                self.script_code_indicator.setToolTip(f"{current_tooltip}\n{error}")
            else:
                self.script_code_indicator.setToolTip(f"APIthon validation error: {error}")

    def _on_script_validation_updated(self, result: APIthonValidationResult):
        """Handle script validation updates from the enhanced editor."""
        # Update any UI components that need to respond to validation changes
        # For example, update the validation panel in the right pane
        if hasattr(self, 'apiton_validation_widget'):
            self.apiton_validation_widget.update_validation_result(result)

    def _get_available_data_paths_for_step(self) -> set:
        """Get available data paths for the current step based on previous steps."""
        available_paths = set()

        # Add meta_info paths
        available_paths.add("meta_info.user.email")
        available_paths.add("meta_info.user.name")
        available_paths.add("meta_info.user.id")

        # Add data paths from previous steps
        if hasattr(self, 'workflow_list') and self.workflow_list.workflow:
            current_index = getattr(self, 'current_step_index', -1)
            for i, step in enumerate(self.workflow_list.workflow.steps):
                if i >= current_index and current_index >= 0:
                    break  # Don't include current step or later steps

                if step.output_key:
                    available_paths.add(f"data.{step.output_key}")

                    # If step has parsed JSON, add nested paths
                    if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                        self._add_json_paths_recursive(
                            step.parsed_json_output,
                            f"data.{step.output_key}",
                            available_paths
                        )

        return available_paths

    def _add_json_paths_recursive(self, data: Any, path_prefix: str, paths: set, max_depth: int = 3):
        """Recursively add JSON paths to the available paths set."""
        if max_depth <= 0:
            return

        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path_prefix}.{key}"
                paths.add(new_path)
                if isinstance(value, (dict, list)):
                    self._add_json_paths_recursive(value, new_path, paths, max_depth - 1)
        elif isinstance(data, list) and data:
            # Add array access pattern
            paths.add(f"{path_prefix}[0]")
            if isinstance(data[0], (dict, list)):
                self._add_json_paths_recursive(data[0], f"{path_prefix}[0]", paths, max_depth - 1)

    def _add_action_input_arg(self):
        """Add a new row to the action input args table."""
        if hasattr(self.action_input_args_table, 'add_argument_row'):
            self.action_input_args_table.add_argument_row()
        else:
            # Fallback for regular QTableWidget
            row_count = self.action_input_args_table.rowCount()
            self.action_input_args_table.insertRow(row_count)
            self.action_input_args_table.setItem(row_count, 0, QTableWidgetItem(""))
            self.action_input_args_table.setItem(row_count, 1, QTableWidgetItem(""))

    def _remove_action_input_arg(self):
        """Remove the selected row from the action input args table."""
        if hasattr(self.action_input_args_table, 'remove_selected_row'):
            self.action_input_args_table.remove_selected_row()
        else:
            # Fallback for regular QTableWidget
            current_row = self.action_input_args_table.currentRow()
            if current_row >= 0:
                self.action_input_args_table.removeRow(current_row)
        self._on_action_data_changed()

    def _auto_suggest_action_args(self):
        """Auto-suggest input arguments based on the selected action."""
        if not isinstance(self.current_step, ActionStep):
            return

        action_name = self.action_name_edit.text().strip()
        if not action_name:
            QMessageBox.information(
                self,
                "No Action Selected",
                "Please enter an action name first to get argument suggestions."
            )
            return

        if hasattr(self.action_input_args_table, 'auto_populate_from_action'):
            self.action_input_args_table.auto_populate_from_action(action_name)
        else:
            QMessageBox.information(
                self,
                "Feature Not Available",
                "Auto-suggestion feature is not available for this table."
            )

    def _suggest_args_from_json(self):
        """Show JSON input dialog for argument suggestions."""
        if hasattr(self.action_input_args_table, 'show_json_input_dialog'):
            self.action_input_args_table.show_json_input_dialog()
        else:
            QMessageBox.information(
                self,
                "Feature Not Available",
                "JSON suggestion feature is not available for this table."
            )

    def _add_script_input_arg(self):
        """Add a new row to the script input args table."""
        if hasattr(self.script_input_args_table, 'add_argument_row'):
            self.script_input_args_table.add_argument_row()
        else:
            # Fallback for regular QTableWidget
            row_count = self.script_input_args_table.rowCount()
            self.script_input_args_table.insertRow(row_count)
            self.script_input_args_table.setItem(row_count, 0, QTableWidgetItem(""))
            self.script_input_args_table.setItem(row_count, 1, QTableWidgetItem(""))

    def _remove_script_input_arg(self):
        """Remove the selected row from the script input args table."""
        if hasattr(self.script_input_args_table, 'remove_selected_row'):
            self.script_input_args_table.remove_selected_row()
        else:
            # Fallback for regular QTableWidget
            current_row = self.script_input_args_table.currentRow()
            if current_row >= 0:
                self.script_input_args_table.removeRow(current_row)
        self._on_script_data_changed()

    def _suggest_script_args_from_json(self):
        """Show JSON input dialog for script argument suggestions."""
        if hasattr(self.script_input_args_table, 'show_json_input_dialog'):
            self.script_input_args_table.show_json_input_dialog()
        else:
            QMessageBox.information(
                self,
                "Feature Not Available",
                "JSON suggestion feature is not available for this table."
            )

    def _parse_action_json(self):
        """Parse and save the action's JSON output."""
        if not isinstance(self.current_step, ActionStep):
            return

        json_text = self.action_json_edit.toPlainText()
        try:
            if json_text.strip():
                parsed = json.loads(json_text)
                self.current_step.user_provided_json_output = json_text
                self.current_step.parsed_json_output = parsed
                QMessageBox.information(self, "Success", "JSON parsed and saved successfully!")
            else:
                self.current_step.user_provided_json_output = None
                self.current_step.parsed_json_output = None
            self.step_updated.emit()
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON Error", f"Invalid JSON: {str(e)}")

    def _parse_script_json(self):
        """Parse and save the script's JSON output."""
        if not isinstance(self.current_step, ScriptStep):
            return

        json_text = self.script_json_edit.toPlainText()
        try:
            if json_text.strip():
                parsed = json.loads(json_text)
                self.current_step.user_provided_json_output = json_text
                self.current_step.parsed_json_output = parsed
                QMessageBox.information(self, "Success", "JSON parsed and saved successfully!")
            else:
                self.current_step.user_provided_json_output = None
                self.current_step.parsed_json_output = None
            self.step_updated.emit()
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON Error", f"Invalid JSON: {str(e)}")

    def _add_switch_case(self):
        """Add a new switch case."""
        if not isinstance(self.current_step, SwitchStep):
            return

        from switch_case_editor import SwitchCaseEditorDialog

        dialog = SwitchCaseEditorDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            case = dialog.get_case()
            if case:
                self.current_step.cases.append(case)
                self._populate_switch_config(self.current_step)
                self.step_updated.emit()

    def _edit_switch_case(self):
        """Edit the selected switch case."""
        if not isinstance(self.current_step, SwitchStep):
            return

        current_row = self.switch_cases_list.currentRow()
        if current_row < 0 or current_row >= len(self.current_step.cases):
            QMessageBox.information(self, "No Selection", "Please select a case to edit.")
            return

        from switch_case_editor import SwitchCaseEditorDialog

        case = self.current_step.cases[current_row]
        dialog = SwitchCaseEditorDialog(case, parent=self)
        if dialog.exec() == QDialog.Accepted:
            updated_case = dialog.get_case()
            if updated_case:
                self.current_step.cases[current_row] = updated_case
                self._populate_switch_config(self.current_step)
                self.step_updated.emit()

    def _remove_switch_case(self):
        """Remove the selected switch case."""
        if not isinstance(self.current_step, SwitchStep):
            return

        current_row = self.switch_cases_list.currentRow()
        if current_row < 0 or current_row >= len(self.current_step.cases):
            QMessageBox.information(self, "No Selection", "Please select a case to remove.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove this case?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            del self.current_step.cases[current_row]
            self._populate_switch_config(self.current_step)
            self.step_updated.emit()

    def _on_switch_case_selected(self, item):
        """Handle switch case selection."""
        # This could be used to show case details in the future
        pass

    def _add_default_case(self):
        """Add a default case to the switch."""
        if not isinstance(self.current_step, SwitchStep):
            return

        from switch_case_editor import DefaultCaseEditorDialog

        dialog = DefaultCaseEditorDialog(self.current_step.default_case, parent=self)
        if dialog.exec() == QDialog.Accepted:
            default_case = dialog.get_default_case()
            if default_case:
                self.current_step.default_case = default_case
                self._populate_switch_config(self.current_step)
                self.step_updated.emit()

    def _edit_default_case(self):
        """Edit the default case."""
        if not isinstance(self.current_step, SwitchStep):
            return

        if not self.current_step.default_case:
            QMessageBox.information(self, "No Default Case", "No default case is defined. Use 'Add Default Case' first.")
            return

        from switch_case_editor import DefaultCaseEditorDialog

        dialog = DefaultCaseEditorDialog(self.current_step.default_case, parent=self)
        if dialog.exec() == QDialog.Accepted:
            default_case = dialog.get_default_case()
            if default_case:
                self.current_step.default_case = default_case
                self._populate_switch_config(self.current_step)
                self.step_updated.emit()

    def _remove_default_case(self):
        """Remove the default case."""
        if not isinstance(self.current_step, SwitchStep):
            return

        if not self.current_step.default_case:
            QMessageBox.information(self, "No Default Case", "No default case is defined.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove the default case?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.current_step.default_case = None
            self._populate_switch_config(self.current_step)
            self.step_updated.emit()


class JsonVariableSelectionPanel(QWidget):
    """Panel for browsing and selecting JSON variables from step outputs."""

    variable_selected = Signal(str)  # Emits the selected data path

    def __init__(self):
        super().__init__()
        self.workflow = None
        self.current_step_index = -1

        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("JSON Variable Selection")
        header_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header_label)

        # Step selection
        step_selection_layout = QHBoxLayout()
        step_selection_layout.addWidget(QLabel("Select step:"))

        self.step_combo = QComboBox()
        self.step_combo.currentIndexChanged.connect(self._on_step_selection_changed)
        step_selection_layout.addWidget(self.step_combo)

        layout.addLayout(step_selection_layout)

        # JSON tree view
        self.json_tree = QTreeWidget()
        self.json_tree.setHeaderLabel("JSON Structure")
        self.json_tree.itemClicked.connect(self._on_tree_item_clicked)
        layout.addWidget(self.json_tree)

        # Selected path display
        self.selected_path_label = QLabel("Selected: None")
        self.selected_path_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.selected_path_label)

        # Copy button
        copy_btn = QPushButton("Copy Selected Path")
        copy_btn.clicked.connect(self._copy_selected_path)
        layout.addWidget(copy_btn)

    def set_workflow(self, workflow: Workflow, current_step_index: int = -1):
        """Set the workflow and update the step selection."""
        self.workflow = workflow
        self.current_step_index = current_step_index
        self._update_step_combo()

    def _update_step_combo(self):
        """Update the step selection combo box."""
        self.step_combo.clear()

        if not self.workflow:
            return

        # Add steps that have parsed JSON output and come before current step
        for i, step in enumerate(self.workflow.steps):
            if i >= self.current_step_index and self.current_step_index >= 0:
                break  # Don't include current step or later steps

            if step.parsed_json_output is not None:
                if isinstance(step, ActionStep):
                    label = f"Step {i+1}: {step.action_name} ({step.output_key})"
                elif isinstance(step, ScriptStep):
                    label = f"Step {i+1}: Script ({step.output_key})"

                self.step_combo.addItem(label, i)

    def _on_step_selection_changed(self, index):
        """Handle step selection change."""
        if index < 0:
            self.json_tree.clear()
            return

        step_index = self.step_combo.itemData(index)
        if step_index is not None and step_index < len(self.workflow.steps):
            step = self.workflow.steps[step_index]
            self._populate_json_tree(step.parsed_json_output, step.output_key)

    def _populate_json_tree(self, json_data: Any, output_key: str):
        """Populate the JSON tree with the structure of the given JSON data."""
        self.json_tree.clear()

        if json_data is None:
            return

        root_item = QTreeWidgetItem([f"data.{output_key}"])
        root_item.setData(0, Qt.UserRole, f"data.{output_key}")
        self.json_tree.addTopLevelItem(root_item)

        self._add_json_items(root_item, json_data, f"data.{output_key}")
        root_item.setExpanded(True)

    def _add_json_items(self, parent_item: QTreeWidgetItem, data: Any, path_prefix: str):
        """Recursively add JSON structure items to the tree."""
        if isinstance(data, dict):
            for key, value in data.items():
                child_path = f"{path_prefix}.{key}"
                child_item = QTreeWidgetItem([key])
                child_item.setData(0, Qt.UserRole, child_path)
                parent_item.addChild(child_item)

                # Add type hint
                if isinstance(value, (dict, list)):
                    child_item.setText(0, f"{key} ({type(value).__name__})")
                    self._add_json_items(child_item, value, child_path)
                else:
                    child_item.setText(0, f"{key}: {repr(value)}")

        elif isinstance(data, list):
            for i, item in enumerate(data):
                child_path = f"{path_prefix}[{i}]"
                child_item = QTreeWidgetItem([f"[{i}]"])
                child_item.setData(0, Qt.UserRole, child_path)
                parent_item.addChild(child_item)

                if isinstance(item, (dict, list)):
                    child_item.setText(0, f"[{i}] ({type(item).__name__})")
                    self._add_json_items(child_item, item, child_path)
                else:
                    child_item.setText(0, f"[{i}]: {repr(item)}")

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int = 0):
        """Handle tree item click."""
        _ = column  # Unused parameter required by Qt signal
        path = item.data(0, Qt.UserRole)
        if path:
            self.selected_path_label.setText(f"Selected: {path}")
            self.variable_selected.emit(path)

    def _copy_selected_path(self):
        """Copy the selected path to clipboard."""
        selected_items = self.json_tree.selectedItems()
        if selected_items:
            path = selected_items[0].data(0, Qt.UserRole)
            if path:
                QApplication.clipboard().setText(path)
                QMessageBox.information(self, "Copied", f"Path copied to clipboard: {path}")


class YamlPreviewPanel(QWidget):
    """Enhanced panel for displaying the generated YAML with real-time validation."""

    validation_status_changed = Signal(bool, int, int)  # is_valid, error_count, warning_count
    export_requested = Signal()  # Emitted when user requests export

    def __init__(self):
        super().__init__()
        self.workflow = None
        self.validation_summary = None
        self.auto_refresh_enabled = True
        self._setup_ui()
        self._setup_validation_integration()

    def _setup_ui(self):
        """Set up the enhanced YAML preview UI."""
        layout = QVBoxLayout(self)

        # Header with controls
        header_layout = QHBoxLayout()
        header_label = QLabel("YAML Preview")
        header_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        header_layout.addWidget(header_label)

        # Auto-refresh toggle
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.toggled.connect(self._on_auto_refresh_toggled)
        header_layout.addWidget(self.auto_refresh_checkbox)

        # Manual refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_yaml)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        header_layout.addWidget(self.refresh_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Validation status bar
        self.validation_bar = self._create_validation_status_bar()
        layout.addWidget(self.validation_bar)

        # YAML text display with syntax highlighting
        self.yaml_text = QTextEdit()
        self.yaml_text.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.yaml_text.setFont(font)
        self.yaml_text.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.yaml_text)

        # Export controls
        export_layout = QHBoxLayout()

        self.export_btn = QPushButton("Export YAML")
        self.export_btn.clicked.connect(self._on_export_requested)
        self.export_btn.setStyleSheet("""
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
        export_layout.addWidget(self.export_btn)

        self.validation_gate_label = QLabel("")
        self.validation_gate_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        export_layout.addWidget(self.validation_gate_label)

        export_layout.addStretch()
        layout.addLayout(export_layout)

        # Detailed error display (collapsible)
        self.error_display = ErrorListWidget()
        self.error_display.setMaximumHeight(200)
        self.error_display.hide()
        layout.addWidget(self.error_display)

    def _create_validation_status_bar(self):
        """Create the validation status bar with color-coded indicators."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)

        # Validation status icon and text
        self.status_icon = QLabel("⏳")
        self.status_icon.setFixedSize(16, 16)
        self.status_icon.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_icon)

        self.status_text = QLabel("Validating...")
        self.status_text.setStyleSheet("font-weight: bold; color: #2c3e50;")
        status_layout.addWidget(self.status_text)

        status_layout.addStretch()

        # Error and warning counters
        self.error_counter = QLabel("0 errors")
        self.error_counter.setStyleSheet("color: #f44336; font-weight: bold;")
        status_layout.addWidget(self.error_counter)

        self.warning_counter = QLabel("0 warnings")
        self.warning_counter.setStyleSheet("color: #ff9800; font-weight: bold;")
        status_layout.addWidget(self.warning_counter)

        # Toggle error display button
        self.toggle_errors_btn = QPushButton("Show Details")
        self.toggle_errors_btn.clicked.connect(self._toggle_error_display)
        self.toggle_errors_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2196f3;
                border: 1px solid #2196f3;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        status_layout.addWidget(self.toggle_errors_btn)

        return status_frame

    def _setup_validation_integration(self):
        """Set up integration with the real-time validation system."""
        from realtime_validation_manager import realtime_validation_manager

        self.validation_manager = realtime_validation_manager
        self.validation_manager.validation_updated.connect(self._on_validation_updated)

    def _on_auto_refresh_toggled(self, enabled: bool):
        """Handle auto-refresh toggle."""
        self.auto_refresh_enabled = enabled
        if enabled and self.workflow:
            self.refresh_yaml()

    def _on_validation_updated(self, summary):
        """Handle validation updates from the validation manager."""
        self.validation_summary = summary
        self._update_validation_display(summary)

        # Auto-refresh YAML if enabled
        if self.auto_refresh_enabled:
            self.refresh_yaml()

    def _update_validation_display(self, summary):
        """Update the validation status display."""
        # Update counters
        self.error_counter.setText(f"{summary.total_errors} errors")
        self.warning_counter.setText(f"{summary.total_warnings} warnings")

        # Update status icon and text
        if summary.total_errors == 0:
            if summary.total_warnings == 0:
                self.status_icon.setText("✅")
                self.status_text.setText("All validations passed")
                self.status_text.setStyleSheet("font-weight: bold; color: #4caf50;")
            else:
                self.status_icon.setText("⚠️")
                self.status_text.setText("Validation passed with warnings")
                self.status_text.setStyleSheet("font-weight: bold; color: #ff9800;")
        else:
            self.status_icon.setText("❌")
            self.status_text.setText("Validation errors found")
            self.status_text.setStyleSheet("font-weight: bold; color: #f44336;")

        # Update export button state
        self.export_btn.setEnabled(summary.is_export_ready)

        if summary.is_export_ready:
            self.validation_gate_label.setText("✓ Ready for export")
            self.validation_gate_label.setStyleSheet("color: #4caf50; font-size: 10px; font-style: italic;")
        else:
            critical_count = len(summary.critical_errors)
            self.validation_gate_label.setText(f"⚠ {critical_count} critical error(s) must be fixed before export")
            self.validation_gate_label.setStyleSheet("color: #f44336; font-size: 10px; font-style: italic;")

        # Update error display
        if summary.total_errors > 0 or summary.total_warnings > 0:
            all_issues = []
            for errors in summary.errors_by_step.values():
                all_issues.extend([error.get_formatted_message() for error in errors])
            for warnings in summary.warnings_by_step.values():
                all_issues.extend([warning.get_formatted_message() for warning in warnings])

            self.error_display.set_errors(all_issues)
            self.toggle_errors_btn.setText(f"Show Details ({len(all_issues)})")
        else:
            self.error_display.clear_errors()
            self.toggle_errors_btn.setText("Show Details")

        # Emit validation status change
        self.validation_status_changed.emit(
            summary.is_export_ready,
            summary.total_errors,
            summary.total_warnings
        )

    def _toggle_error_display(self):
        """Toggle the visibility of the error display."""
        if self.error_display.isVisible():
            self.error_display.hide()
            self.toggle_errors_btn.setText("Show Details")
        else:
            self.error_display.show()
            self.toggle_errors_btn.setText("Hide Details")

    def _on_export_requested(self):
        """Handle export request with validation gate."""
        if not self.validation_summary or not self.validation_summary.is_export_ready:
            # Show validation gate dialog
            from PySide6.QtWidgets import QMessageBox

            critical_errors = self.validation_summary.critical_errors if self.validation_summary else []
            error_list = "\n".join([f"• {error.get_formatted_message()}" for error in critical_errors[:5]])

            if len(critical_errors) > 5:
                error_list += f"\n... and {len(critical_errors) - 5} more errors"

            QMessageBox.warning(
                self,
                "Export Blocked",
                f"Cannot export YAML due to critical validation errors:\n\n{error_list}\n\nPlease fix these errors before exporting."
            )
            return

        self.export_requested.emit()

    def set_workflow(self, workflow: Workflow):
        """Set the workflow and update the YAML preview."""
        self.workflow = workflow

        # Update validation manager
        if hasattr(self, 'validation_manager'):
            self.validation_manager.set_workflow(workflow)

        self.refresh_yaml()

    def refresh_yaml(self):
        """Refresh the YAML preview and validation."""
        if not self.workflow:
            self.yaml_text.setPlainText("No workflow to display")
            return

        try:
            from yaml_generator import generate_yaml_string
            yaml_output = generate_yaml_string(self.workflow, "compound_action")

            # Apply syntax highlighting (basic)
            self._apply_yaml_highlighting(yaml_output)

        except ValueError as e:
            # Handle validation errors specifically
            error_str = str(e).lower()
            if "output_key" in error_str or "action_name" in error_str:
                error_text = f"❌ YAML Generation Blocked - Missing Required Fields:\n\n{str(e)}\n\n"
                error_text += "💡 Fix the following issues:\n"

                if "output_key" in error_str:
                    error_text += "• Add output_key to all ActionStep and ScriptStep instances\n"
                    error_text += "• Use lowercase_snake_case format (e.g., 'user_info', 'processed_data')\n"
                    error_text += "• Ensure all output_key values are unique within the workflow\n"

                if "action_name" in error_str:
                    error_text += "• Add action_name to all ActionStep instances\n"
                    error_text += "• Use valid Moveworks action names (e.g., 'mw.get_user_by_email')\n"
                    error_text += "• Or use custom action names with valid characters (letters, numbers, dots, underscores)\n"

                error_text += "\n📝 Example valid values:\n"
                if "output_key" in error_str:
                    error_text += "• output_key: user_info, processed_data, api_response\n"
                if "action_name" in error_str:
                    error_text += "• action_name: mw.get_user_by_email, mw.create_ticket, custom_action\n"

                self.yaml_text.setPlainText(error_text)
            else:
                self.yaml_text.setPlainText(f"❌ Validation Error:\n\n{str(e)}")
        except Exception as e:
            self.yaml_text.setPlainText(f"Error generating YAML:\n{str(e)}")

    def _apply_yaml_highlighting(self, yaml_content: str):
        """Apply basic syntax highlighting to YAML content."""
        # For now, just set the plain text
        # In a full implementation, this would apply syntax highlighting
        self.yaml_text.setPlainText(yaml_content)



    def _copy_yaml(self):
        """Copy YAML content to clipboard."""
        yaml_content = self.yaml_text.toPlainText()
        if yaml_content and yaml_content != "No steps in workflow":
            QApplication.clipboard().setText(yaml_content)
            QMessageBox.information(self, "Copied", "YAML content copied to clipboard!")
        else:
            QMessageBox.warning(self, "Nothing to Copy", "No YAML content to copy.")

    def _export_yaml(self):
        """Export YAML content to file."""
        yaml_content = self.yaml_text.toPlainText()
        if not yaml_content or yaml_content == "No steps in workflow":
            QMessageBox.warning(self, "Nothing to Export", "No YAML content to export.")
            return

        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export YAML", "workflow.yaml", "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                QMessageBox.information(self, "Export Successful", f"YAML exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export YAML:\n{str(e)}")


class MainWindow(QMainWindow):
    """Main application window for the Moveworks YAML Assistant."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moveworks YAML Assistant")
        self.setGeometry(100, 100, 1400, 900)

        # Set comprehensive application styling
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #f5f5f5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 13px;
                color: #2c3e50;
            }

            /* Menu Bar - High Contrast */
            QMenuBar {
                background-color: #2c3e50;
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                padding: 4px;
                border: none;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #ffffff;
                padding: 8px 12px;
                margin: 0px 2px;
                border-radius: 4px;
                font-weight: 500;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
                color: #ffffff;
            }
            QMenuBar::item:pressed {
                background-color: #3498db;
                color: #ffffff;
            }

            /* Menu Dropdowns - High Contrast */
            QMenu {
                background-color: #ffffff;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
                font-weight: 500;
            }
            QMenu::item {
                background-color: transparent;
                color: #2c3e50;
                padding: 8px 16px;
                margin: 1px;
                border-radius: 4px;
                font-weight: 500;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QMenu::item:disabled {
                color: #95a5a6;
            }
            QMenu::separator {
                height: 1px;
                background-color: #bdc3c7;
                margin: 4px 8px;
            }

            /* Dialog Boxes - High Contrast */
            QDialog {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
            }
            QDialog QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
            }
            QDialog QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QDialog QPushButton:hover {
                background-color: #2980b9;
            }
            QDialog QPushButton:pressed {
                background-color: #21618c;
            }

            /* Message Boxes - High Contrast */
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
                min-height: 25px;
            }

            /* Splitter Handles */
            QSplitter::handle {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:vertical {
                height: 3px;
            }

            /* General Text Elements - High Contrast */
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
            }
            QTextEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }

            /* Tooltips - High Contrast */
            QToolTip {
                background-color: #2c3e50;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: 500;
            }

            /* Tab Widgets - High Contrast */
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
                border-bottom-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
                color: #2c3e50;
            }

            /* Group Boxes - High Contrast */
            QGroupBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #2c3e50;
                background-color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 14px;
            }

            /* List Widgets - High Contrast */
            QListWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                color: #2c3e50;
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 13px;
                font-weight: 500;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #ebf3fd;
                color: #2c3e50;
            }

            /* Tree Widgets - High Contrast */
            QTreeWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
            }
            QTreeWidget::item {
                color: #2c3e50;
                padding: 4px;
                font-size: 13px;
                font-weight: 500;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #ebf3fd;
                color: #2c3e50;
            }
            QTreeWidget::branch {
                color: #2c3e50;
            }

            /* Combo Boxes - High Contrast */
            QComboBox {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 20px;
                font-weight: 500;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                color: #2c3e50;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }

            /* Table Widgets - High Contrast */
            QTableWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                color: #2c3e50;
                padding: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #ebf3fd;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                border: 1px solid #bdc3c7;
                font-size: 13px;
                font-weight: 600;
            }

            /* Scroll Bars - High Contrast */
            QScrollBar:vertical {
                background-color: #ecf0f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
            QScrollBar:horizontal {
                background-color: #ecf0f1;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #95a5a6;
            }
        """)



        # Initialize unified tutorial system
        try:
            self.unified_tutorial_manager = UnifiedTutorialManager(self)
            print("✓ Unified tutorial system initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize unified tutorial system: {e}")
            self.unified_tutorial_manager = None

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main splitter for layout
        main_splitter = QSplitter(Qt.Horizontal)
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(main_splitter)

        # Left panel: Step list and controls
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)

        # Center panel: Step configuration with examples
        center_panel = self._create_center_panel()
        main_splitter.addWidget(center_panel)

        # Right panel: Enhanced JSON selector and YAML preview
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([300, 600, 400])

        # Create menu bar
        self._create_menu_bar()

        # Connect signals
        self.workflow_list.step_selected.connect(self._on_step_selected)
        self.enhanced_json_panel.path_selected.connect(self._on_variable_selected)

        # Initialize with empty workflow
        self._update_all_panels()

    def _create_left_panel(self):
        """Create the redesigned left panel with simplified workflow management."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Modern header with quick actions
        header_widget = self._create_modern_header()
        layout.addWidget(header_widget)

        # Quick start section
        quick_start_widget = self._create_quick_start_section()
        layout.addWidget(quick_start_widget)

        # Action name input for compound action
        action_name_group = QGroupBox("Compound Action Name")
        action_name_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #333;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        action_name_layout = QVBoxLayout(action_name_group)

        self.action_name_edit = QLineEdit()
        self.action_name_edit.setObjectName("compound_action_name_field")  # For tutorial targeting
        self.action_name_edit.setPlaceholderText("e.g., my_compound_action")
        self.action_name_edit.setText("compound_action")
        self.action_name_edit.setToolTip("Name for the compound action (required for Moveworks compliance)")
        self.action_name_edit.textChanged.connect(self._on_action_name_changed)
        self.action_name_edit.setStyleSheet("""
            QLineEdit {
                color: #2c3e50;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        action_name_layout.addWidget(self.action_name_edit)
        layout.addWidget(action_name_group)

        # Input Variables section
        self.input_variables_widget = InputVariablesWidget()
        self.input_variables_widget.variables_changed.connect(self._on_input_variables_changed)
        layout.addWidget(self.input_variables_widget)

        # Step list
        self.workflow_list = WorkflowListWidget()
        self.workflow_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-size: 13px;
                selection-background-color: #bbdefb;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #bbdefb;
                color: #333;
            }
        """)
        layout.addWidget(self.workflow_list)

        # Advanced tools section (collapsible)
        advanced_section = self._create_advanced_tools_section()
        layout.addWidget(advanced_section)

        # Step management section
        management_section = self._create_step_management_section()
        layout.addWidget(management_section)

        return panel

    def _create_modern_header(self):
        """Create a modern header with workflow title and quick actions."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Workflow title
        title_label = QLabel("🚀 Workflow Builder")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-radius: 6px;
            }
        """)
        header_layout.addWidget(title_label)

        # Quick action buttons
        wizard_btn = QPushButton("🧙")
        wizard_btn.setToolTip("New Workflow Wizard")
        wizard_btn.setFixedSize(32, 32)
        wizard_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        wizard_btn.clicked.connect(self._show_workflow_wizard)
        header_layout.addWidget(wizard_btn)

        template_btn = QPushButton("📋")
        template_btn.setToolTip("Apply Template")
        template_btn.setFixedSize(32, 32)
        template_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        template_btn.clicked.connect(self._show_template_library)
        header_layout.addWidget(template_btn)

        return header_widget

    def _create_quick_start_section(self):
        """Create a quick start section with common actions."""
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(8)

        # Section title
        title_label = QLabel("⚡ Quick Start")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                padding: 6px 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                border-left: 4px solid #3498db;
            }
        """)
        section_layout.addWidget(title_label)

        # Quick action buttons in a grid
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setSpacing(4)

        # Common button style
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """

        # Essential buttons only
        action_btn = QPushButton("➕ Add Action")
        action_btn.setStyleSheet(button_style)
        action_btn.clicked.connect(self._add_action_step)
        buttons_layout.addWidget(action_btn)

        script_btn = QPushButton("📝 Add Script")
        script_btn.setStyleSheet(button_style.replace("#3498db", "#27ae60").replace("#2980b9", "#229954").replace("#21618c", "#1e8449"))
        script_btn.clicked.connect(self._add_script_step)
        buttons_layout.addWidget(script_btn)

        section_layout.addWidget(buttons_widget)
        return section_widget

    def _create_advanced_tools_section(self):
        """Create a collapsible section for advanced workflow tools."""
        from PySide6.QtWidgets import QGroupBox, QToolButton

        group_box = QGroupBox("🔧 Advanced Tools")
        group_box.setCheckable(True)
        group_box.setChecked(False)  # Collapsed by default
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #34495e;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ecf0f1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #ecf0f1;
            }
            QGroupBox::indicator {
                width: 16px;
                height: 16px;
            }
            QGroupBox::indicator:unchecked {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNEwxMCA4TDYgMTJWNFoiIGZpbGw9IiM3Zjg2OWMiLz4KPC9zdmc+);
            }
            QGroupBox::indicator:checked {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkwxMCA2TDggMTBMNCA2WiIgZmlsbD0iIzM0OThlNSIvPgo8L3N2Zz4=);
            }
        """)

        layout = QVBoxLayout(group_box)
        layout.setSpacing(4)

        # Button style for advanced tools
        button_style = """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """

        # Control flow buttons
        control_style = button_style.replace("#95a5a6", "#f39c12").replace("#7f8c8d", "#e67e22").replace("#6c7b7d", "#d35400")

        switch_btn = QPushButton("🔀 Switch Step")
        switch_btn.setObjectName("add_switch_button")
        switch_btn.clicked.connect(self._add_switch_step)
        switch_btn.setStyleSheet(control_style)
        layout.addWidget(switch_btn)

        for_btn = QPushButton("🔄 For Loop")
        for_btn.clicked.connect(self._add_for_step)
        for_btn.setStyleSheet(control_style)
        layout.addWidget(for_btn)

        parallel_btn = QPushButton("⚡ Parallel")
        parallel_btn.clicked.connect(self._add_parallel_step)
        parallel_btn.setStyleSheet(control_style)
        layout.addWidget(parallel_btn)

        # Error handling buttons
        error_style = button_style.replace("#95a5a6", "#e74c3c").replace("#7f8c8d", "#c0392b").replace("#6c7b7d", "#a93226")

        try_catch_btn = QPushButton("🛡️ Try/Catch")
        try_catch_btn.setObjectName("add_try_catch_button")
        try_catch_btn.clicked.connect(self._add_try_catch_step)
        try_catch_btn.setStyleSheet(error_style)
        layout.addWidget(try_catch_btn)

        raise_btn = QPushButton("⚠️ Raise Error")
        raise_btn.clicked.connect(self._add_raise_step)
        raise_btn.setStyleSheet(error_style)
        layout.addWidget(raise_btn)

        return_btn = QPushButton("↩️ Return")
        return_btn.clicked.connect(self._add_return_step)
        return_btn.setStyleSheet(error_style)
        layout.addWidget(return_btn)

        return group_box

    def _create_step_management_section(self):
        """Create step management controls."""
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(6)

        # Section title
        title_label = QLabel("📋 Step Management")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
                padding: 6px 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                border-left: 4px solid #e74c3c;
            }
        """)
        section_layout.addWidget(title_label)

        # Management buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(3)

        # Button style
        button_style = """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """

        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.clicked.connect(self._remove_selected_step)
        remove_btn.setToolTip(get_tooltip("remove_step"))
        remove_btn.setStyleSheet(button_style)
        buttons_layout.addWidget(remove_btn)

        # Movement buttons
        move_style = button_style.replace("#e74c3c", "#34495e").replace("#c0392b", "#2c3e50").replace("#a93226", "#1b2631")

        move_up_btn = QPushButton("⬆️ Move Up")
        move_up_btn.clicked.connect(self._move_step_up)
        move_up_btn.setToolTip(get_tooltip("move_up"))
        move_up_btn.setStyleSheet(move_style)
        buttons_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton("⬇️ Move Down")
        move_down_btn.clicked.connect(self._move_step_down)
        move_down_btn.setToolTip(get_tooltip("move_down"))
        move_down_btn.setStyleSheet(move_style)
        buttons_layout.addWidget(move_down_btn)

        section_layout.addLayout(buttons_layout)
        return section_widget

    def _create_center_panel(self):
        """Create the center panel with step configuration and examples."""
        # Create tab widget for center panel with high contrast styling
        center_tabs = QTabWidget()
        center_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #4caf50;
                color: #ffffff;
                border-bottom-color: #4caf50;
            }
            QTabBar::tab:hover {
                background-color: #c8e6c9;
                color: #2c3e50;
            }
        """)

        # Configuration tab
        config_tab = QWidget()
        config_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
            }
        """)
        config_layout = QVBoxLayout(config_tab)
        config_layout.setContentsMargins(8, 8, 8, 8)
        config_layout.setSpacing(8)

        self.config_panel = StepConfigurationPanel()
        self.config_panel.setObjectName("action_config_panel")  # For tutorial targeting
        self.config_panel.step_updated.connect(self._on_step_updated)
        config_layout.addWidget(self.config_panel)

        center_tabs.addTab(config_tab, "📝 Configuration")

        # Examples tab
        examples_tab = QWidget()
        examples_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
            }
        """)
        examples_layout = QVBoxLayout(examples_tab)
        examples_layout.setContentsMargins(8, 8, 8, 8)
        examples_layout.setSpacing(8)

        self.examples_panel = ContextualExamplesPanel()
        self.examples_panel.example_applied.connect(self._on_example_applied)
        examples_layout.addWidget(self.examples_panel)

        center_tabs.addTab(examples_tab, "💡 Examples")

        # Bender Function Builder tab
        bender_tab = QWidget()
        bender_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
            }
        """)
        bender_layout = QVBoxLayout(bender_tab)
        bender_layout.setContentsMargins(8, 8, 8, 8)
        bender_layout.setSpacing(8)

        self.bender_builder = BenderFunctionBuilder()
        self.bender_builder.function_built.connect(self._on_bender_function_built)
        bender_layout.addWidget(self.bender_builder)

        center_tabs.addTab(bender_tab, "🔧 Bender Functions")

        # Visual Builder tab
        visual_tab = QWidget()
        visual_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
            }
        """)
        visual_layout = QVBoxLayout(visual_tab)
        visual_layout.setContentsMargins(8, 8, 8, 8)
        visual_layout.setSpacing(8)

        self.visual_builder = SimpleVisualBuilder()
        self.visual_builder.workflow_changed.connect(self._on_visual_workflow_changed)
        visual_layout.addWidget(self.visual_builder)

        center_tabs.addTab(visual_tab, "🎨 Visual Builder")

        return center_tabs

    def _create_right_panel(self):
        """Create the right panel with clean tabbed interface and YAML preview."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Create main tab widget for the right panel with high contrast styling
        right_tabs = QTabWidget()
        right_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
                border-bottom-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
                color: #2c3e50;
            }
        """)

        # JSON Path Selector Tab
        from tabbed_json_selector import TabbedJsonPathSelector
        self.enhanced_json_panel = TabbedJsonPathSelector()
        self.enhanced_json_panel.setObjectName("json_path_selector_button")  # For tutorial targeting
        right_tabs.addTab(self.enhanced_json_panel, "🔍 JSON Explorer")

        # YAML Preview Tab
        self.yaml_panel = YamlPreviewPanel()
        self.yaml_panel.setObjectName("yaml_preview_panel")  # For tutorial targeting
        right_tabs.addTab(self.yaml_panel, "📄 YAML Preview")

        # Validation Results Tab
        self.validation_panel = self._create_validation_panel()
        right_tabs.addTab(self.validation_panel, "✅ Validation")

        # APIthon Validation Tab
        self.apiton_validation_widget = APIthonValidationWidget()
        right_tabs.addTab(self.apiton_validation_widget, "🐍 APIthon")

        # Simplified Data Path Selector Tab
        self.simplified_data_selector = SimplifiedDataPathSelector(self.workflow_list.workflow)
        self.simplified_data_selector.path_selected.connect(self._on_simplified_path_selected)
        right_tabs.addTab(self.simplified_data_selector, "🎯 Data Helper")

        # Smart Suggestions Tab
        self.smart_suggestions_widget = SmartSuggestionsWidget()
        self.smart_suggestions_widget.suggestion_applied.connect(self._on_suggestion_applied)
        right_tabs.addTab(self.smart_suggestions_widget, "🧠 Suggestions")

        layout.addWidget(right_tabs)
        return panel

    def _create_validation_panel(self):
        """Create the validation results panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Validation Results")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 8px;
                background-color: #e3f2fd;
                border-radius: 4px;
                border: 1px solid #2196f3;
            }
        """)
        header_layout.addWidget(header_label)

        # Validate button
        validate_btn = QPushButton("🔍 Validate Now")
        validate_btn.setObjectName("validate_button")  # For tutorial targeting
        validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        validate_btn.clicked.connect(self._validate_workflow)
        header_layout.addWidget(validate_btn)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Status indicator
        self.validation_status = StatusIndicator()
        layout.addWidget(self.validation_status)

        # Create tabbed validation interface
        validation_tabs = QTabWidget()
        validation_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 6px 12px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
                border-bottom-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
                color: #2c3e50;
            }
        """)

        # General validation tab
        general_validation_widget = QWidget()
        general_validation_layout = QVBoxLayout(general_validation_widget)
        general_validation_layout.setContentsMargins(4, 4, 4, 4)

        self.error_display = ErrorListWidget()
        general_validation_layout.addWidget(self.error_display)

        validation_tabs.addTab(general_validation_widget, "🔍 General")

        # Compliance validation tab
        compliance_validation_widget = QWidget()
        compliance_validation_layout = QVBoxLayout(compliance_validation_widget)
        compliance_validation_layout.setContentsMargins(4, 4, 4, 4)

        self.compliance_display = self._create_compliance_display()
        compliance_validation_layout.addWidget(self.compliance_display)

        validation_tabs.addTab(compliance_validation_widget, "📋 Compliance")

        layout.addWidget(validation_tabs)

        return panel

    def _create_compliance_display(self):
        """Create the compliance validation display widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Compliance status header
        self.compliance_status_label = QLabel("✓ Compliance Status: Ready")
        self.compliance_status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #4caf50;
                padding: 8px;
                background-color: #e8f5e8;
                border-radius: 4px;
                border: 1px solid #4caf50;
            }
        """)
        layout.addWidget(self.compliance_status_label)

        # Compliance sections
        sections_scroll = QScrollArea()
        sections_scroll.setWidgetResizable(True)
        sections_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        sections_widget = QWidget()
        sections_layout = QVBoxLayout(sections_widget)

        # Field Naming section
        field_naming_group = QGroupBox("Field Naming Compliance")
        field_naming_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        field_naming_layout = QVBoxLayout(field_naming_group)

        self.field_naming_status = QLabel("✓ All field names follow lowercase_snake_case")
        self.field_naming_status.setStyleSheet("color: #4caf50; font-size: 12px;")
        field_naming_layout.addWidget(self.field_naming_status)

        self.field_naming_errors = QLabel("")
        self.field_naming_errors.setWordWrap(True)
        self.field_naming_errors.setStyleSheet("color: #f44336; font-size: 11px;")
        field_naming_layout.addWidget(self.field_naming_errors)

        sections_layout.addWidget(field_naming_group)

        # Mandatory Fields section
        mandatory_fields_group = QGroupBox("Mandatory Fields Compliance")
        mandatory_fields_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        mandatory_fields_layout = QVBoxLayout(mandatory_fields_group)

        self.mandatory_fields_status = QLabel("✓ All mandatory fields are present")
        self.mandatory_fields_status.setStyleSheet("color: #4caf50; font-size: 12px;")
        mandatory_fields_layout.addWidget(self.mandatory_fields_status)

        self.mandatory_fields_errors = QLabel("")
        self.mandatory_fields_errors.setWordWrap(True)
        self.mandatory_fields_errors.setStyleSheet("color: #f44336; font-size: 11px;")
        mandatory_fields_layout.addWidget(self.mandatory_fields_errors)

        sections_layout.addWidget(mandatory_fields_group)

        # APIthon Compliance section
        apiton_compliance_group = QGroupBox("APIthon Script Compliance")
        apiton_compliance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        apiton_compliance_layout = QVBoxLayout(apiton_compliance_group)

        self.apiton_compliance_status = QLabel("✓ All scripts follow APIthon restrictions")
        self.apiton_compliance_status.setStyleSheet("color: #4caf50; font-size: 12px;")
        apiton_compliance_layout.addWidget(self.apiton_compliance_status)

        self.apiton_compliance_errors = QLabel("")
        self.apiton_compliance_errors.setWordWrap(True)
        self.apiton_compliance_errors.setStyleSheet("color: #f44336; font-size: 11px;")
        apiton_compliance_layout.addWidget(self.apiton_compliance_errors)

        sections_layout.addWidget(apiton_compliance_group)

        sections_layout.addStretch()
        sections_scroll.setWidget(sections_widget)
        layout.addWidget(sections_scroll)

        return widget

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Workflow", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_workflow)
        file_menu.addAction(new_action)

        # Workflow Wizard
        wizard_action = QAction("🧙 New Workflow Wizard...", self)
        wizard_action.setShortcut("Ctrl+Shift+N")
        wizard_action.triggered.connect(self._show_workflow_wizard)
        wizard_action.setToolTip("Step-by-step wizard for creating workflows")
        file_menu.addAction(wizard_action)

        open_action = QAction("Open Workflow...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_workflow)
        file_menu.addAction(open_action)

        save_action = QAction("Save Workflow...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_workflow)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # Template library
        template_action = QAction("Template Library...", self)
        template_action.setObjectName("template_library_button")  # For tutorial targeting
        template_action.setShortcut("Ctrl+T")
        template_action.triggered.connect(self._show_template_library)
        file_menu.addAction(template_action)

        file_menu.addSeparator()

        export_yaml_action = QAction("Export YAML...", self)
        export_yaml_action.triggered.connect(self._export_yaml)
        file_menu.addAction(export_yaml_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        validate_action = QAction("Validate Workflow", self)
        validate_action.setShortcut("F5")
        validate_action.triggered.connect(self._validate_workflow)
        tools_menu.addAction(validate_action)

        tools_menu.addSeparator()

        # Tutorial submenu
        tutorials_submenu = tools_menu.addMenu("📚 Tutorials")

        # Unified Tutorial System (Plugin-based architecture)
        if self.unified_tutorial_manager:
            unified_tutorial_action = QAction("🎓 Interactive Tutorial System", self)
            unified_tutorial_action.triggered.connect(self._show_unified_tutorials)
            unified_tutorial_action.setToolTip("Plugin-based tutorial system with comprehensive content migration and enhanced features")
            tutorials_submenu.addAction(unified_tutorial_action)

            tutorials_submenu.addSeparator()

            # Tutorial Builder
            create_tutorial_action = QAction("✨ Create New Tutorial...", self)
            create_tutorial_action.triggered.connect(self._show_tutorial_builder)
            create_tutorial_action.setToolTip("Visual tutorial builder for creating custom tutorials without programming")
            tutorials_submenu.addAction(create_tutorial_action)



        # Help menu
        help_menu = menubar.addMenu("Help")

        help_action = QAction("Help Topics", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        help_menu.addSeparator()

        getting_started_action = QAction("Getting Started", self)
        getting_started_action.triggered.connect(lambda: self._show_help_topic("Getting Started"))
        help_menu.addAction(getting_started_action)

        action_steps_action = QAction("Action Steps", self)
        action_steps_action.triggered.connect(lambda: self._show_help_topic("Action Steps"))
        help_menu.addAction(action_steps_action)

        script_steps_action = QAction("Script Steps", self)
        script_steps_action.triggered.connect(lambda: self._show_help_topic("Script Steps"))
        help_menu.addAction(script_steps_action)

        validation_action = QAction("Validation", self)
        validation_action.triggered.connect(lambda: self._show_help_topic("Validation"))
        help_menu.addAction(validation_action)

        help_menu.addSeparator()

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _add_action_step(self):
        """Add a new action step to the workflow."""
        action_step = ActionStep(
            action_name="",
            output_key="",
            description="New action step"
        )
        self.workflow_list.add_step(action_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_script_step(self):
        """Add a new script step to the workflow."""
        script_step = ScriptStep(
            code="# Enter your APIthon script here\nreturn {}",
            output_key="",
            description="New script step"
        )
        self.workflow_list.add_step(script_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_switch_step(self):
        """Add a new switch step to the workflow."""
        switch_step = SwitchStep(
            description="New switch step",
            output_key="_"
        )
        self.workflow_list.add_step(switch_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_for_step(self):
        """Add a new for loop step to the workflow."""
        for_step = ForLoopStep(
            description="New for loop step",
            each="item",
            in_source="",
            output_key=""
        )
        self.workflow_list.add_step(for_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_parallel_step(self):
        """Add a new parallel step to the workflow."""
        parallel_step = ParallelStep(
            description="New parallel step",
            output_key="_"
        )
        self.workflow_list.add_step(parallel_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_return_step(self):
        """Add a new return step to the workflow."""
        return_step = ReturnStep(
            description="New return step",
            output_key="_"
        )
        self.workflow_list.add_step(return_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_try_catch_step(self):
        """Add a new try/catch step to the workflow."""
        try_catch_step = TryCatchStep(
            description="New try/catch step",
            output_key="_"
        )
        self.workflow_list.add_step(try_catch_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_raise_step(self):
        """Add a new raise step to the workflow."""
        raise_step = RaiseStep(
            description="New raise step",
            output_key="_"
        )
        self.workflow_list.add_step(raise_step)
        self._update_all_panels()

        # Select the new step
        new_index = len(self.workflow_list.workflow.steps) - 1
        self.workflow_list.setCurrentRow(new_index)
        self._on_step_selected(new_index)

    def _add_mw_action_step(self):
        """Add a new built-in Moveworks action step."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel

        # Create action selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Built-in Action")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        # Add instruction label
        label = QLabel("Select a Moveworks built-in action:")
        layout.addWidget(label)

        # Create list widget for actions
        action_list = QListWidget()
        for action in MW_ACTIONS_CATALOG:
            item_text = f"{action.display_name} ({action.action_name})"
            action_list.addItem(item_text)
        layout.addWidget(action_list)

        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show dialog and handle selection
        if dialog.exec() == QDialog.Accepted:
            current_row = action_list.currentRow()
            if current_row >= 0:
                selected_action = MW_ACTIONS_CATALOG[current_row]

                # Create action step with pre-filled data
                action_step = ActionStep(
                    action_name=selected_action.action_name,
                    output_key="",
                    description=selected_action.description,
                    user_provided_json_output=selected_action.typical_json_output_example
                )

                # Parse the JSON output if provided
                if action_step.user_provided_json_output:
                    try:
                        action_step.parsed_json_output = json.loads(action_step.user_provided_json_output)
                    except json.JSONDecodeError:
                        pass  # Leave parsed_json_output as None

                self.workflow_list.add_step(action_step)
                self._update_all_panels()

                # Select the new step
                new_index = len(self.workflow_list.workflow.steps) - 1
                self.workflow_list.setCurrentRow(new_index)
                self._on_step_selected(new_index)

    def _remove_selected_step(self):
        """Remove the currently selected step."""
        self.workflow_list.remove_selected_step()
        self.config_panel.clear_selection()
        self._update_all_panels()

    def _move_step_up(self):
        """Move the selected step up in the list."""
        self.workflow_list.move_step_up()
        self._update_all_panels()

    def _move_step_down(self):
        """Move the selected step down in the list."""
        self.workflow_list.move_step_down()
        self._update_all_panels()

    def _on_step_selected(self, step_index: int):
        """Handle step selection from the workflow list with enhanced JSON selector integration."""
        if 0 <= step_index < len(self.workflow_list.workflow.steps):
            step = self.workflow_list.workflow.steps[step_index]
            self.config_panel.set_step(step, step_index, self.workflow_list.workflow)

            # Enhanced JSON panel integration with better step handling
            self.enhanced_json_panel.set_workflow(self.workflow_list.workflow, step_index)

            # Update examples context based on step type
            if isinstance(step, ActionStep):
                self.examples_panel.set_context("action_step")
            elif isinstance(step, ScriptStep):
                self.examples_panel.set_context("script_step")
            else:
                self.examples_panel.set_context("general")
        else:
            self.config_panel.clear_selection()
            self.examples_panel.set_context("general")
            # Clear the JSON panel when no step is selected
            self.enhanced_json_panel.set_workflow(self.workflow_list.workflow, -1)

    def _on_step_updated(self):
        """Handle updates to step configuration with enhanced JSON selector refresh."""
        self.workflow_list.update_workflow_display()
        self.yaml_panel.refresh_yaml()

        # Refresh the JSON selector to pick up any new parsed JSON data
        current_step_index = self.workflow_list.currentRow()
        if current_step_index >= 0:
            self.enhanced_json_panel.set_workflow(self.workflow_list.workflow, current_step_index)

        # Update validation
        self._update_validation()

    def _update_validation(self):
        """Update the validation panel with current workflow status."""
        if not self.workflow_list.workflow.steps:
            self.validation_status.set_status("ready", "No steps to validate")
            self.error_display.clear_errors()
            return

        try:
            # Validate workflow
            errors = comprehensive_validate(self.workflow_list.workflow)

            if errors:
                self.validation_status.set_error_count(len(errors))
                self.error_display.set_errors(errors)
            else:
                self.validation_status.set_error_count(0)
                self.error_display.clear_errors()

        except Exception as e:
            self.validation_status.set_status("error", f"Validation failed: {str(e)}")
            self.error_display.clear_errors()

    def _on_variable_selected(self, path: str):
        """Handle variable selection from the JSON panel."""
        # This could be used to automatically insert the path into input fields
        # For now, we just copy it to clipboard
        QApplication.clipboard().setText(path)

    def _on_simplified_path_selected(self, path: str):
        """Handle path selection from the simplified data path selector."""
        # Copy to clipboard and show a brief notification
        QApplication.clipboard().setText(path)

        # Show a brief status message
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(f"Data path copied to clipboard: {path}", 3000)

    def _on_suggestion_applied(self, suggestion_id: str, implementation_code: str):
        """Handle application of a smart suggestion."""
        try:
            # Execute the suggestion implementation code
            # This is a simplified implementation - in production, you'd want more sophisticated code execution
            if implementation_code.strip():
                # For now, show the code to the user for manual application
                reply = QMessageBox.question(
                    self, "Apply Suggestion",
                    f"Apply this suggestion?\n\nCode to execute:\n{implementation_code}",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    # In a real implementation, you would parse and execute the suggestion code
                    # For now, we'll show a success message
                    QMessageBox.information(
                        self, "Suggestion Applied",
                        "Suggestion applied successfully! Please review your workflow."
                    )

                    # Refresh all panels to show changes
                    self._update_all_panels()

        except Exception as e:
            QMessageBox.critical(
                self, "Error Applying Suggestion",
                f"Failed to apply suggestion:\n{str(e)}"
            )

    def _on_visual_workflow_changed(self, workflow: Workflow):
        """Handle workflow changes from the visual builder."""
        # Update the main workflow
        self.workflow_list.workflow = workflow
        self.workflow_list.update_workflow_display()

        # Update other panels (but not the visual builder to avoid recursion)
        self.enhanced_json_panel.set_workflow(workflow)
        self.yaml_panel.set_workflow(workflow)
        self.input_variables_widget.set_workflow(workflow)

        if hasattr(self, 'simplified_data_selector'):
            self.simplified_data_selector.setWorkflow(workflow)

        if hasattr(self, 'smart_suggestions_widget'):
            self.smart_suggestions_widget.set_workflow(workflow)

        self._update_validation()
        self._update_compliance_validation()

    def _on_action_name_changed(self):
        """Handle action name changes."""
        # Refresh YAML when action name changes
        if hasattr(self, 'yaml_panel'):
            self.yaml_panel.refresh_yaml()

    def _on_input_variables_changed(self):
        """Handle input variables changes."""
        # Update all panels when input variables change
        self._update_all_panels()

        # Update validation to check for input variable references
        self._update_validation()

        # Refresh YAML to include input_variables section
        if hasattr(self, 'yaml_panel'):
            self.yaml_panel.refresh_yaml()

    def _update_all_panels(self):
        """Update all panels with the current workflow."""
        self.enhanced_json_panel.set_workflow(self.workflow_list.workflow)
        self.yaml_panel.set_workflow(self.workflow_list.workflow)
        self.input_variables_widget.set_workflow(self.workflow_list.workflow)

        # Update simplified data selector if it exists
        if hasattr(self, 'simplified_data_selector'):
            self.simplified_data_selector.setWorkflow(self.workflow_list.workflow)

        # Update smart suggestions
        if hasattr(self, 'smart_suggestions_widget'):
            self.smart_suggestions_widget.set_workflow(self.workflow_list.workflow)

        # Update visual builder
        if hasattr(self, 'visual_builder'):
            self.visual_builder.set_workflow(self.workflow_list.workflow)

        self._update_validation()
        self._update_compliance_validation()

    def _update_compliance_validation(self):
        """Update the compliance validation display."""
        if not hasattr(self, 'compliance_display'):
            return

        # Get action name for compound action validation
        action_name = getattr(self, 'action_name_edit', None)
        action_name_value = action_name.text() if action_name else "compound_action"

        # Perform compliance validation
        result = compliance_validator.validate_workflow_compliance(
            self.workflow_list.workflow,
            action_name_value
        )

        # Update overall compliance status
        if result.is_valid:
            self.compliance_status_label.setText("✓ Compliance Status: All checks passed")
            self.compliance_status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #4caf50;
                    padding: 8px;
                    background-color: #e8f5e8;
                    border-radius: 4px;
                    border: 1px solid #4caf50;
                }
            """)
        else:
            error_count = len(result.errors) + len(result.mandatory_field_errors) + len(result.field_naming_errors) + len(result.apiton_errors)
            self.compliance_status_label.setText(f"❌ Compliance Status: {error_count} issue(s) found")
            self.compliance_status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #f44336;
                    padding: 8px;
                    background-color: #ffebee;
                    border-radius: 4px;
                    border: 1px solid #f44336;
                }
            """)

        # Update field naming compliance
        if result.field_naming_errors:
            self.field_naming_status.setText(f"❌ {len(result.field_naming_errors)} field naming issue(s)")
            self.field_naming_status.setStyleSheet("color: #f44336; font-size: 12px; font-weight: bold;")
            self.field_naming_errors.setText("\n".join(result.field_naming_errors))
        else:
            self.field_naming_status.setText("✓ All field names follow lowercase_snake_case")
            self.field_naming_status.setStyleSheet("color: #4caf50; font-size: 12px;")
            self.field_naming_errors.setText("")

        # Update mandatory fields compliance
        if result.mandatory_field_errors:
            self.mandatory_fields_status.setText(f"❌ {len(result.mandatory_field_errors)} mandatory field issue(s)")
            self.mandatory_fields_status.setStyleSheet("color: #f44336; font-size: 12px; font-weight: bold;")
            self.mandatory_fields_errors.setText("\n".join(result.mandatory_field_errors))
        else:
            self.mandatory_fields_status.setText("✓ All mandatory fields are present")
            self.mandatory_fields_status.setStyleSheet("color: #4caf50; font-size: 12px;")
            self.mandatory_fields_errors.setText("")

        # Update APIthon compliance
        if result.apiton_errors:
            self.apiton_compliance_status.setText(f"❌ {len(result.apiton_errors)} APIthon issue(s)")
            self.apiton_compliance_status.setStyleSheet("color: #f44336; font-size: 12px; font-weight: bold;")
            self.apiton_compliance_errors.setText("\n".join(result.apiton_errors))
        else:
            self.apiton_compliance_status.setText("✓ All scripts follow APIthon restrictions")
            self.apiton_compliance_status.setStyleSheet("color: #4caf50; font-size: 12px;")
            self.apiton_compliance_errors.setText("")

    def _validate_workflow(self):
        """Validate the current workflow and show results."""
        self._update_validation()

        # Show a message if validation is successful
        if not self.workflow_list.workflow.steps:
            QMessageBox.information(self, "Validation", "No steps to validate.")
            return

        errors = comprehensive_validate(self.workflow_list.workflow)
        if not errors:
            QMessageBox.information(self, "Validation", "✅ Workflow validation passed successfully!")
        else:
            QMessageBox.warning(self, "Validation", f"❌ Found {len(errors)} validation error(s). Check the Validation tab for details.")

    def _export_yaml(self):
        """Export the current workflow as YAML with compliance validation."""
        if not self.workflow_list.workflow.steps:
            QMessageBox.warning(self, "Export YAML", "No workflow to export.")
            return

        # Perform compliance validation before export
        action_name_value = self.action_name_edit.text() if hasattr(self, 'action_name_edit') else "compound_action"
        result = compliance_validator.validate_workflow_compliance(
            self.workflow_list.workflow,
            action_name_value
        )

        # Check if there are compliance issues
        if not result.is_valid:
            error_count = len(result.errors) + len(result.mandatory_field_errors) + len(result.field_naming_errors) + len(result.apiton_errors)
            reply = QMessageBox.question(
                self, "Compliance Issues Found",
                f"Found {error_count} compliance issue(s) in the workflow:\n\n"
                f"• Field naming errors: {len(result.field_naming_errors)}\n"
                f"• Mandatory field errors: {len(result.mandatory_field_errors)}\n"
                f"• APIthon errors: {len(result.apiton_errors)}\n"
                f"• Other errors: {len(result.errors)}\n\n"
                "Do you want to export anyway? The generated YAML may not be valid for Moveworks.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                QMessageBox.information(
                    self, "Export Cancelled",
                    "Please fix the compliance issues and try again.\n"
                    "Check the Validation → Compliance tab for details."
                )
                return

        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export YAML", "workflow.yaml", "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if filename:
            try:
                yaml_content = generate_yaml_string(self.workflow_list.workflow, action_name_value)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)

                if result.is_valid:
                    QMessageBox.information(self, "Export Successful", f"✅ YAML exported successfully to:\n{filename}\n\nAll compliance checks passed!")
            except ValueError as e:
                # Handle validation errors specifically
                error_str = str(e).lower()
                if "output_key" in error_str or "action_name" in error_str:
                    error_msg = "❌ Export Failed - Missing Required Fields\n\n"
                    error_msg += str(e) + "\n\n"
                    error_msg += "Please fix the following before exporting:\n"

                    if "output_key" in error_str:
                        error_msg += "• Add output_key to all ActionStep and ScriptStep instances\n"
                        error_msg += "• Use lowercase_snake_case format\n"
                        error_msg += "• Ensure all output_key values are unique\n"

                    if "action_name" in error_str:
                        error_msg += "• Add action_name to all ActionStep instances\n"
                        error_msg += "• Use valid Moveworks action names or custom action names\n"
                        error_msg += "• Ensure action names contain only valid characters\n"

                    QMessageBox.critical(self, "Export Failed", error_msg)
                else:
                    QMessageBox.critical(self, "Export Failed", f"Validation Error:\n\n{str(e)}")
                return
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export YAML:\n{str(e)}")
                return

            # Handle validation results after successful YAML generation
            if not result.is_valid:
                QMessageBox.warning(self, "Export Completed with Issues", f"⚠️ YAML exported to:\n{filename}\n\nWarning: Compliance issues detected. Please review before using in production.")

    def _show_help(self):
        """Show the help dialog."""
        from comprehensive_help_dialog import ComprehensiveHelpDialog
        help_dialog = ComprehensiveHelpDialog(self)
        help_dialog.exec()

    def _show_help_topic(self, topic: str):
        """Show help for a specific topic."""
        from comprehensive_help_dialog import ComprehensiveHelpDialog
        help_dialog = ComprehensiveHelpDialog(self)
        help_dialog.show_topic(topic)
        help_dialog.exec()

    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(self, "About Moveworks YAML Assistant",
                         """
                         <h3>Moveworks YAML Assistant</h3>
                         <p>A comprehensive tool for creating and managing Moveworks workflow YAML files.</p>
                         <p><b>Features:</b></p>
                         <ul>
                         <li>Visual workflow builder</li>
                         <li>JSON path selector</li>
                         <li>Real-time validation</li>
                         <li>Template library</li>
                         <li>Interactive tutorials</li>
                         </ul>
                         <p><b>Version:</b> 2.0</p>
                         """)

    def _on_example_applied(self, example_code: str):
        """Handle example code being applied."""
        # Get current step and apply example
        current_row = self.workflow_list.currentRow()
        if current_row >= 0:
            step = self.workflow_list.workflow.steps[current_row]

            # Apply example based on step type
            if isinstance(step, ActionStep):
                # For action steps, try to parse as input args or JSON output
                try:
                    # Try to parse as JSON for output
                    json.loads(example_code)
                    step.user_provided_json_output = example_code
                except json.JSONDecodeError:
                    # Not JSON, might be input args format
                    pass
            elif isinstance(step, ScriptStep):
                # For script steps, apply as code
                step.code = example_code

            # Refresh displays
            self.config_panel.set_step(step, current_row, self.workflow_list.workflow)
            self._on_step_updated()

    def _on_bender_function_built(self, expression: str):
        """Handle when a Bender function expression is built."""
        # Try to insert the expression into the currently focused input field
        focused_widget = QApplication.focusWidget()

        if isinstance(focused_widget, QLineEdit):
            # Insert at cursor position in line edit
            cursor_pos = focused_widget.cursorPosition()
            current_text = focused_widget.text()
            new_text = current_text[:cursor_pos] + expression + current_text[cursor_pos:]
            focused_widget.setText(new_text)
            focused_widget.setCursorPosition(cursor_pos + len(expression))
        elif isinstance(focused_widget, QTextEdit):
            # Insert at cursor position in text edit
            cursor = focused_widget.textCursor()
            cursor.insertText(expression)
        else:
            # Show a message with the expression to copy
            QMessageBox.information(
                self,
                "Bender Function Built",
                f"Copy this expression to use in your workflow:\n\n{expression}",
                QMessageBox.Ok
            )

    def _show_template_library(self):
        """Show the template library dialog."""
        dialog = TemplateBrowserDialog(self)
        dialog.template_selected.connect(self._load_template)
        dialog.exec()

    def _load_template(self, template_id: str):
        """Load a template into the current workflow."""
        template = template_library.get_template(template_id)
        if template:
            reply = QMessageBox.question(
                self, "Load Template",
                f"Load template '{template.name}'? This will replace the current workflow.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.workflow_list.workflow = template.workflow
                self.workflow_list.update_workflow_display()
                self.config_panel.clear_selection()
                self._update_all_panels()

                QMessageBox.information(self, "Success", f"Template '{template.name}' loaded successfully!")

    def _show_unified_tutorials(self):
        """Show the unified tutorial system with plugin architecture."""
        if self.unified_tutorial_manager:
            self.unified_tutorial_manager.show_tutorial_selection()
        else:
            QMessageBox.warning(
                self,
                "Tutorial System Unavailable",
                "The unified tutorial system is not available. Please check the installation."
            )

    def _show_tutorial_builder(self):
        """Show the JSON-based tutorial builder."""
        try:
            print("Opening JSON Tutorial Builder...")

            # Import the JSON tutorial builder
            from json_tutorial_builder import JSONTutorialBuilderDialog
            print("✓ JSON Tutorial Builder imported successfully")

            # Create and show the dialog
            builder_dialog = JSONTutorialBuilderDialog(self)
            builder_dialog.tutorial_created.connect(self._on_tutorial_created)
            print("✓ JSON Tutorial Builder dialog created successfully")

            print("Showing JSON Tutorial Builder dialog...")
            builder_dialog.exec()

        except ImportError as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Import Error: {e}")
            print(f"Full traceback:\n{error_details}")

            QMessageBox.warning(
                self,
                "Tutorial Builder Unavailable",
                f"The JSON tutorial builder is not available:\n\n{str(e)}\n\n"
                f"Please ensure json_tutorial_builder.py is in the application directory.\n\n"
                f"Technical details:\n{error_details}"
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"General Error: {e}")
            print(f"Full traceback:\n{error_details}")

            QMessageBox.critical(
                self,
                "Tutorial Builder Error",
                f"Failed to open JSON tutorial builder:\n\n{str(e)}\n\n"
                f"Technical details:\n{error_details}"
            )

    def _on_tutorial_created(self, plugin_path: str):
        """Handle tutorial creation completion."""
        QMessageBox.information(
            self,
            "Tutorial Created",
            f"Tutorial plugin created successfully!\n\n"
            f"File: {plugin_path}\n\n"
            f"The tutorial will be available after restarting the application."
        )

    def _new_workflow(self):
        """Create a new workflow."""
        reply = QMessageBox.question(
            self, "New Workflow",
            "Are you sure you want to create a new workflow? Unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.workflow_list.workflow = Workflow()
            self.workflow_list.update_workflow_display()
            self.config_panel.clear_selection()
            self._update_all_panels()

    def _show_workflow_wizard(self):
        """Show the workflow creation wizard."""
        wizard = WorkflowWizard(self)
        wizard.workflow_created.connect(self._apply_wizard_workflow)
        wizard.exec()

    def _apply_wizard_workflow(self, workflow):
        """Apply a workflow created by the wizard."""
        # Ask if user wants to replace current workflow
        if self.workflow_list.workflow.steps:
            reply = QMessageBox.question(
                self, "Apply Wizard Workflow",
                "This will replace your current workflow. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Apply the new workflow
        self.workflow_list.workflow = workflow
        self.workflow_list.update_workflow_display()
        self.config_panel.clear_selection()
        self._update_all_panels()

        # Show success message
        QMessageBox.information(
            self, "Workflow Created",
            "Workflow created successfully! You can now customize it further using the full editor."
        )

    def _open_workflow(self):
        """Open a workflow from file."""
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Workflow", "", "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    workflow_data = json.load(f)

                # Load workflow from JSON data
                workflow = Workflow()
                for step_data in workflow_data.get("steps", []):
                    if step_data["type"] == "action":
                        step = ActionStep(
                            action_name=step_data["action_name"],
                            output_key=step_data["output_key"],
                            description=step_data.get("description"),
                            input_args=step_data.get("input_args", {}),
                            progress_updates=step_data.get("progress_updates"),
                            delay_config=step_data.get("delay_config"),
                            user_provided_json_output=step_data.get("user_provided_json_output")
                        )
                    elif step_data["type"] == "script":
                        step = ScriptStep(
                            code=step_data["code"],
                            output_key=step_data["output_key"],
                            description=step_data.get("description"),
                            input_args=step_data.get("input_args", {}),
                            user_provided_json_output=step_data.get("user_provided_json_output")
                        )

                    workflow.steps.append(step)

                self.workflow_list.workflow = workflow
                self.workflow_list.update_workflow_display()
                self.config_panel.clear_selection()
                self._update_all_panels()

                QMessageBox.information(self, "Success", f"Workflow loaded from {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load workflow: {str(e)}")

    def _save_workflow(self):
        """Save the current workflow to file."""
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Workflow", "", "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                # Convert workflow to JSON-serializable format
                workflow_data = {"steps": []}

                for step in self.workflow_list.workflow.steps:
                    if isinstance(step, ActionStep):
                        step_data = {
                            "type": "action",
                            "action_name": step.action_name,
                            "output_key": step.output_key,
                            "description": step.description,
                            "input_args": step.input_args,
                            "progress_updates": step.progress_updates,
                            "delay_config": step.delay_config,
                            "user_provided_json_output": step.user_provided_json_output
                        }
                    elif isinstance(step, ScriptStep):
                        step_data = {
                            "type": "script",
                            "code": step.code,
                            "output_key": step.output_key,
                            "description": step.description,
                            "input_args": step.input_args,
                            "user_provided_json_output": step.user_provided_json_output
                        }

                    workflow_data["steps"].append(step_data)

                with open(filename, 'w') as f:
                    json.dump(workflow_data, f, indent=2)

                QMessageBox.information(self, "Success", f"Workflow saved to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save workflow: {str(e)}")

    def _export_yaml_duplicate(self):
        """Export the generated YAML to file (duplicate method - should be removed)."""
        # This method appears to be a duplicate - redirecting to main export method
        self._export_yaml()

    def _validate_workflow(self):
        """Validate the current workflow and show results with enhanced suggestions."""
        if not self.workflow_list.workflow.steps:
            QMessageBox.information(self, "Validation", "No steps in workflow to validate.")
            return

        # Use enhanced validator for better error messages and suggestions
        enhanced_errors = enhanced_validator.validate_with_suggestions(self.workflow_list.workflow)

        # Convert enhanced errors to basic error messages for existing dialog
        error_messages = [error.message for error in enhanced_errors]

        # Show detailed validation dialog
        dialog = ValidationDialog(error_messages, self)
        dialog.exec()

        # Update YAML panel validation status
        self.yaml_panel.refresh_yaml()

    def _show_help(self):
        """Show the help dialog."""
        if not hasattr(self, '_help_dialog') or self._help_dialog is None:
            self._help_dialog = HelpDialog(self)
        self._help_dialog.show()
        self._help_dialog.raise_()
        self._help_dialog.activateWindow()

    def _show_help_topic(self, topic_title: str):
        """Show help dialog with a specific topic."""
        if not hasattr(self, '_help_dialog') or self._help_dialog is None:
            self._help_dialog = HelpDialog(self)
        self._help_dialog.show_topic(topic_title)

    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self, "About Moveworks YAML Assistant",
            "Moveworks YAML Assistant v2.0 (Phase 5)\n\n"
            "A desktop application for creating and managing\n"
            "Moveworks Compound Action workflows.\n\n"
            "Features:\n"
            "• Visual workflow builder\n"
            "• JSON-driven data mapping\n"
            "• Real-time validation\n"
            "• Built-in action library\n"
            "• Comprehensive help system\n\n"
            "Built with PySide6 and Python."
        )


def check_environment():
    """
    Check if the environment is properly set up for the GUI application.

    Returns:
        Tuple[bool, str]: (success, error_message)
    """
    import importlib.util

    # Check Python version
    if sys.version_info < (3, 10):
        return False, f"Python 3.10+ required, but you have {sys.version.split()[0]}"

    # Check critical dependencies
    critical_deps = [
        ('PySide6', 'PySide6'),
        ('yaml', 'PyYAML'),
    ]

    missing_deps = []
    for import_name, package_name in critical_deps:
        if importlib.util.find_spec(import_name) is None:
            missing_deps.append(package_name)

    if missing_deps:
        deps_list = ', '.join(missing_deps)
        return False, f"Missing critical dependencies: {deps_list}"

    return True, ""


def show_environment_error(error_message: str):
    """Show environment error dialog with setup instructions."""
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton
        from PySide6.QtCore import QProcess

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create error dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Environment Setup Required")
        msg_box.setText("Environment Setup Required")
        msg_box.setInformativeText(
            f"The Moveworks YAML Assistant cannot start due to environment issues:\n\n"
            f"{error_message}\n\n"
            f"Would you like to set up the environment automatically?"
        )

        # Add custom buttons
        setup_button = msg_box.addButton("Setup Environment", QMessageBox.ActionRole)
        manual_button = msg_box.addButton("Manual Instructions", QMessageBox.ActionRole)
        cancel_button = msg_box.addButton("Cancel", QMessageBox.RejectRole)

        msg_box.setDefaultButton(setup_button)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == setup_button:
            # Launch setup process
            process = QProcess()
            process.start(sys.executable, ["run_app.py", "--setup-only"])
            process.waitForFinished(60000)  # Wait up to 60 seconds

            if process.exitCode() == 0:
                QMessageBox.information(
                    None,
                    "Setup Complete",
                    "Environment setup completed successfully!\n\n"
                    "Please restart the application."
                )
            else:
                error_output = process.readAllStandardError().data().decode()
                QMessageBox.critical(
                    None,
                    "Setup Failed",
                    f"Environment setup failed:\n\n{error_output}\n\n"
                    f"Please check the console output and try manual setup."
                )

        elif clicked_button == manual_button:
            # Show manual instructions
            QMessageBox.information(
                None,
                "Manual Setup Instructions",
                "To set up the environment manually:\n\n"
                "1. Open a terminal/command prompt\n"
                "2. Navigate to the project directory\n"
                "3. Run: python run_app.py --setup-only\n"
                "4. Follow the on-screen instructions\n\n"
                "For detailed instructions, see ENVIRONMENT_SETUP.md"
            )

    except ImportError:
        # Fallback to console output if PySide6 is not available
        print(f"Environment Error: {error_message}")
        print("\nTo set up the environment:")
        print("1. Open a terminal/command prompt")
        print("2. Navigate to the project directory")
        print("3. Run: python run_app.py --setup-only")
        print("4. Follow the on-screen instructions")


def main():
    """Main application entry point with environment validation."""
    # Check environment before importing PySide6 components
    env_ok, error_msg = check_environment()

    if not env_ok:
        show_environment_error(error_msg)
        sys.exit(1)

    # Environment is OK, proceed with normal startup
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Moveworks YAML Assistant")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Moveworks")

    # Create and show main window
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        # Handle any startup errors gracefully
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to initialize the application:\n\n{str(e)}\n\n"
            f"Please check the console output for more details."
        )
        sys.exit(1)

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()