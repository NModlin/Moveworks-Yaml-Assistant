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
    QPushButton, QMessageBox,
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
from tutorial_system import TutorialManager, TutorialDialog
from integrated_tutorial_system import InteractiveTutorialManager
from tutorial_integration import TutorialIntegrationManager
from template_library import TemplateBrowserDialog, template_library
from enhanced_json_selector import EnhancedJsonPathSelector
from contextual_examples import ContextualExamplesPanel
from enhanced_validator import enhanced_validator, ValidationError
from enhanced_script_editor import EnhancedScriptEditor
from enhanced_apiton_validator import enhanced_apiton_validator, APIthonValidationResult
from error_display import APIthonValidationWidget, EnhancedAPIthonValidationWidget
from compliance_validator import compliance_validator, ComplianceValidationResult
from dsl_input_widget import DSLInputWidget
from dsl_validator import dsl_validator


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


class StepConfigurationPanel(QStackedWidget):
    """Panel for configuring step properties."""

    step_updated = Signal()  # Emitted when step data is updated

    def __init__(self):
        super().__init__()
        self.current_step = None
        self.current_step_index = -1

        # Create different configuration widgets
        self.empty_widget = QLabel("Select a step to configure")
        self.empty_widget.setAlignment(Qt.AlignCenter)
        self.addWidget(self.empty_widget)

        self.action_config_widget = self._create_action_config_widget()
        self.addWidget(self.action_config_widget)

        self.script_config_widget = self._create_script_config_widget()
        self.addWidget(self.script_config_widget)

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
        self.action_name_edit.setToolTip(get_tooltip("action_name"))
        self.action_name_edit.setPlaceholderText("e.g., mw.get_user_by_email")

        # Create label with mandatory field indicator
        action_name_label = QLabel("Action Name: *")
        action_name_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(action_name_label, self.action_name_edit)

        self.action_description_edit = QLineEdit()
        self.action_description_edit.textChanged.connect(self._on_action_data_changed)
        self.action_description_edit.setToolTip(get_tooltip("description"))
        self.action_description_edit.setPlaceholderText("Optional description of this action")
        form_layout.addRow("Description:", self.action_description_edit)

        self.action_output_key_edit = QLineEdit()
        self.action_output_key_edit.textChanged.connect(self._on_action_data_changed)
        self.action_output_key_edit.textChanged.connect(self._validate_current_step)
        self.action_output_key_edit.setToolTip(get_tooltip("output_key"))
        self.action_output_key_edit.setPlaceholderText("e.g., user_info")

        # Create label with mandatory field indicator
        output_key_label = QLabel("Output Key: *")
        output_key_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(output_key_label, self.action_output_key_edit)

        layout.addWidget(form_group)

        # Input arguments table
        input_args_group = QGroupBox("Input Arguments")
        input_args_layout = QVBoxLayout(input_args_group)

        self.action_input_args_table = QTableWidget(0, 2)
        self.action_input_args_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.action_input_args_table.horizontalHeader().setStretchLastSection(True)
        self.action_input_args_table.itemChanged.connect(self._on_action_data_changed)
        self.action_input_args_table.setToolTip(get_tooltip("input_args"))
        input_args_layout.addWidget(self.action_input_args_table)

        # Buttons for input args
        input_args_buttons = QHBoxLayout()
        self.add_input_arg_btn = QPushButton("Add Argument")  # Store as attribute for tutorial
        self.add_input_arg_btn.setObjectName("add_input_arg_btn")  # For tutorial targeting
        self.add_input_arg_btn.clicked.connect(self._add_action_input_arg)

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

        # Apply consistent styling to remove button
        remove_arg_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)

        input_args_buttons.addWidget(self.add_input_arg_btn)
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
        self.script_output_key_edit.setToolTip(get_tooltip("output_key"))
        self.script_output_key_edit.setPlaceholderText("e.g., processed_data")

        # Create label with mandatory field indicator
        script_output_key_label = QLabel("Output Key: *")
        script_output_key_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        form_layout.addRow(script_output_key_label, self.script_output_key_edit)

        layout.addWidget(form_group)

        # Enhanced script editor section
        self.enhanced_script_editor = EnhancedScriptEditor()
        self.enhanced_script_editor.script_changed.connect(self._on_script_data_changed)
        self.enhanced_script_editor.validation_updated.connect(self._on_script_validation_updated)
        layout.addWidget(self.enhanced_script_editor)

        # Input arguments table
        input_args_group = QGroupBox("Input Arguments")
        input_args_layout = QVBoxLayout(input_args_group)

        self.script_input_args_table = QTableWidget(0, 2)
        self.script_input_args_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.script_input_args_table.horizontalHeader().setStretchLastSection(True)
        self.script_input_args_table.itemChanged.connect(self._on_script_data_changed)
        input_args_layout.addWidget(self.script_input_args_table)

        # Buttons for input args
        input_args_buttons = QHBoxLayout()
        add_arg_btn = QPushButton("Add Argument")
        add_arg_btn.clicked.connect(self._add_script_input_arg)
        remove_arg_btn = QPushButton("Remove Selected")
        remove_arg_btn.clicked.connect(self._remove_script_input_arg)
        input_args_buttons.addWidget(add_arg_btn)
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

    def set_step(self, step, step_index: int):
        """Set the current step to configure."""
        self.current_step = step
        self.current_step_index = step_index

        if isinstance(step, ActionStep):
            self._populate_action_config(step)
            self.setCurrentWidget(self.action_config_widget)
        elif isinstance(step, ScriptStep):
            self._populate_script_config(step)
            self.setCurrentWidget(self.script_config_widget)
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

        # Populate input args table
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

        # Populate input args table
        self.script_input_args_table.setRowCount(len(step.input_args))
        for i, (key, value) in enumerate(step.input_args.items()):
            self.script_input_args_table.setItem(i, 0, QTableWidgetItem(str(key)))
            self.script_input_args_table.setItem(i, 1, QTableWidgetItem(str(value)))

        # Populate JSON output
        self.script_json_edit.setPlainText(step.user_provided_json_output or "")

    def _on_action_data_changed(self):
        """Handle changes to action step data."""
        if not isinstance(self.current_step, ActionStep):
            return

        self.current_step.action_name = self.action_name_edit.text()
        self.current_step.description = self.action_description_edit.text() or None
        self.current_step.output_key = self.action_output_key_edit.text()

        # Update input args from table
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

        # Update input args from table
        self.current_step.input_args = {}
        for row in range(self.script_input_args_table.rowCount()):
            key_item = self.script_input_args_table.item(row, 0)
            value_item = self.script_input_args_table.item(row, 1)
            if key_item and value_item and key_item.text():
                self.current_step.input_args[key_item.text()] = value_item.text()

        self.step_updated.emit()

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
        # Reset styling
        self.action_name_edit.setStyleSheet("")
        self.action_output_key_edit.setStyleSheet("")

        # Check for field naming errors
        for error in result.field_naming_errors:
            if "action_name" in error.lower():
                self.action_name_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")
            elif "output_key" in error.lower():
                self.action_output_key_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")

        # Check for mandatory field errors
        for error in result.mandatory_field_errors:
            if "action_name" in error.lower():
                self.action_name_edit.setStyleSheet("border: 2px solid #f44336; background-color: #ffebee;")
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
        row_count = self.action_input_args_table.rowCount()
        self.action_input_args_table.insertRow(row_count)
        self.action_input_args_table.setItem(row_count, 0, QTableWidgetItem(""))
        self.action_input_args_table.setItem(row_count, 1, QTableWidgetItem(""))

    def _remove_action_input_arg(self):
        """Remove the selected row from the action input args table."""
        current_row = self.action_input_args_table.currentRow()
        if current_row >= 0:
            self.action_input_args_table.removeRow(current_row)
            self._on_action_data_changed()

    def _add_script_input_arg(self):
        """Add a new row to the script input args table."""
        row_count = self.script_input_args_table.rowCount()
        self.script_input_args_table.insertRow(row_count)
        self.script_input_args_table.setItem(row_count, 0, QTableWidgetItem(""))
        self.script_input_args_table.setItem(row_count, 1, QTableWidgetItem(""))

    def _remove_script_input_arg(self):
        """Remove the selected row from the script input args table."""
        current_row = self.script_input_args_table.currentRow()
        if current_row >= 0:
            self.script_input_args_table.removeRow(current_row)
            self._on_script_data_changed()

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

        # Initialize tutorial managers
        self.tutorial_manager = TutorialManager(self)
        self.interactive_tutorial_manager = InteractiveTutorialManager(self)
        self.comprehensive_tutorial_manager = TutorialIntegrationManager(self)

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
        """Create the left panel with step list and controls."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header_label = QLabel("🔧 Workflow Steps")
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
        layout.addWidget(header_label)

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

        # Control buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(4)

        # Button styling
        button_style = """
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """

        # Basic step types
        self.add_action_btn = QPushButton("➕ Add Action Step")
        self.add_action_btn.setObjectName("add_action_btn")
        self.add_action_btn.clicked.connect(self._add_action_step)
        self.add_action_btn.setToolTip(get_tooltip("add_action"))
        self.add_action_btn.setStyleSheet(button_style)
        button_layout.addWidget(self.add_action_btn)

        self.add_script_btn = QPushButton("📝 Add Script Step")
        self.add_script_btn.setObjectName("add_script_btn")
        self.add_script_btn.clicked.connect(self._add_script_step)
        self.add_script_btn.setToolTip(get_tooltip("add_script"))
        self.add_script_btn.setStyleSheet(button_style)
        button_layout.addWidget(self.add_script_btn)

        # Control flow step types
        control_flow_style = button_style.replace("#2196f3", "#4caf50").replace("#1976d2", "#388e3c").replace("#0d47a1", "#2e7d32")

        add_switch_btn = QPushButton("🔀 Add Switch Step")
        add_switch_btn.setObjectName("add_switch_button")  # For tutorial targeting
        add_switch_btn.clicked.connect(self._add_switch_step)
        add_switch_btn.setStyleSheet(control_flow_style)
        button_layout.addWidget(add_switch_btn)

        add_for_btn = QPushButton("🔄 Add For Loop Step")
        add_for_btn.clicked.connect(self._add_for_step)
        add_for_btn.setStyleSheet(control_flow_style)
        button_layout.addWidget(add_for_btn)

        add_parallel_btn = QPushButton("⚡ Add Parallel Step")
        add_parallel_btn.clicked.connect(self._add_parallel_step)
        add_parallel_btn.setStyleSheet(control_flow_style)
        button_layout.addWidget(add_parallel_btn)

        add_return_btn = QPushButton("↩️ Add Return Step")
        add_return_btn.clicked.connect(self._add_return_step)
        add_return_btn.setStyleSheet(control_flow_style)
        button_layout.addWidget(add_return_btn)

        # Error handling step types
        error_style = button_style.replace("#2196f3", "#ff9800").replace("#1976d2", "#f57c00").replace("#0d47a1", "#e65100")

        add_try_catch_btn = QPushButton("🛡️ Add Try/Catch Step")
        add_try_catch_btn.setObjectName("add_try_catch_button")  # For tutorial targeting
        add_try_catch_btn.clicked.connect(self._add_try_catch_step)
        add_try_catch_btn.setStyleSheet(error_style)
        button_layout.addWidget(add_try_catch_btn)

        add_raise_btn = QPushButton("⚠️ Add Raise Step")
        add_raise_btn.clicked.connect(self._add_raise_step)
        add_raise_btn.setStyleSheet(error_style)
        button_layout.addWidget(add_raise_btn)

        # Built-in actions
        builtin_style = button_style.replace("#2196f3", "#9c27b0").replace("#1976d2", "#7b1fa2").replace("#0d47a1", "#4a148c")

        add_mw_action_btn = QPushButton("🏗️ Add Built-in Action")
        add_mw_action_btn.clicked.connect(self._add_mw_action_step)
        add_mw_action_btn.setToolTip(get_tooltip("add_builtin"))
        add_mw_action_btn.setStyleSheet(builtin_style)
        button_layout.addWidget(add_mw_action_btn)

        # Spacer
        spacer_label = QLabel()
        spacer_label.setFixedHeight(8)
        button_layout.addWidget(spacer_label)

        # Management buttons
        management_style = button_style.replace("#2196f3", "#f44336").replace("#1976d2", "#d32f2f").replace("#0d47a1", "#b71c1c")

        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.clicked.connect(self._remove_selected_step)
        remove_btn.setToolTip(get_tooltip("remove_step"))
        remove_btn.setStyleSheet(management_style)
        button_layout.addWidget(remove_btn)

        # Movement buttons
        move_style = button_style.replace("#2196f3", "#607d8b").replace("#1976d2", "#455a64").replace("#0d47a1", "#263238")

        move_up_btn = QPushButton("⬆️ Move Up")
        move_up_btn.clicked.connect(self._move_step_up)
        move_up_btn.setToolTip(get_tooltip("move_up"))
        move_up_btn.setStyleSheet(move_style)
        button_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton("⬇️ Move Down")
        move_down_btn.clicked.connect(self._move_step_down)
        move_down_btn.setToolTip(get_tooltip("move_down"))
        move_down_btn.setStyleSheet(move_style)
        button_layout.addWidget(move_down_btn)

        layout.addLayout(button_layout)

        return panel

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

        # Comprehensive Tutorial Series
        comprehensive_tutorial_action = QAction("🚀 Comprehensive Tutorial Series", self)
        comprehensive_tutorial_action.triggered.connect(self._show_comprehensive_tutorials)
        comprehensive_tutorial_action.setToolTip("Complete 5-module tutorial series covering all Moveworks features")
        tutorials_submenu.addAction(comprehensive_tutorial_action)

        tutorials_submenu.addSeparator()

        interactive_tutorial_action = QAction("🎯 Interactive Basic Workflow", self)
        interactive_tutorial_action.triggered.connect(self._start_interactive_tutorial)
        tutorials_submenu.addAction(interactive_tutorial_action)

        tutorials_submenu.addSeparator()

        all_tutorials_action = QAction("📖 All Tutorials...", self)
        all_tutorials_action.triggered.connect(self._show_tutorials)
        tutorials_submenu.addAction(all_tutorials_action)

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
            self.config_panel.set_step(step, step_index)

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

    def _on_action_name_changed(self):
        """Handle action name changes."""
        # Refresh YAML when action name changes
        if hasattr(self, 'yaml_panel'):
            self.yaml_panel.refresh_yaml()

    def _update_all_panels(self):
        """Update all panels with the current workflow."""
        self.enhanced_json_panel.set_workflow(self.workflow_list.workflow)
        self.yaml_panel.set_workflow(self.workflow_list.workflow)
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
                else:
                    QMessageBox.warning(self, "Export Completed with Issues", f"⚠️ YAML exported to:\n{filename}\n\nWarning: Compliance issues detected. Please review before using in production.")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export YAML:\n{str(e)}")

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
            self.config_panel.set_step(step, current_row)
            self._on_step_updated()

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

    def _start_interactive_tutorial(self):
        """Start the interactive basic workflow tutorial."""
        self.interactive_tutorial_manager.start_tutorial("interactive_basic")

    def _show_tutorials(self):
        """Show the tutorial selection dialog."""
        self.tutorial_manager.show_tutorial_dialog()

    def _show_comprehensive_tutorials(self):
        """Show the comprehensive tutorial series selection."""
        self.comprehensive_tutorial_manager.show_tutorial_selection()

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