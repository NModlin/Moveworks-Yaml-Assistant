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
    QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QFont

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
        self.action_name_edit.setToolTip(get_tooltip("action_name"))
        self.action_name_edit.setPlaceholderText("e.g., mw.get_user_by_email")
        form_layout.addRow("Action Name:", self.action_name_edit)

        self.action_description_edit = QLineEdit()
        self.action_description_edit.textChanged.connect(self._on_action_data_changed)
        self.action_description_edit.setToolTip(get_tooltip("description"))
        self.action_description_edit.setPlaceholderText("Optional description of this action")
        form_layout.addRow("Description:", self.action_description_edit)

        self.action_output_key_edit = QLineEdit()
        self.action_output_key_edit.textChanged.connect(self._on_action_data_changed)
        self.action_output_key_edit.setToolTip(get_tooltip("output_key"))
        self.action_output_key_edit.setPlaceholderText("e.g., user_info")
        form_layout.addRow("Output Key:", self.action_output_key_edit)

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
        add_arg_btn = QPushButton("Add Argument")
        add_arg_btn.clicked.connect(self._add_action_input_arg)
        remove_arg_btn = QPushButton("Remove Selected")
        remove_arg_btn.clicked.connect(self._remove_action_input_arg)
        input_args_buttons.addWidget(add_arg_btn)
        input_args_buttons.addWidget(remove_arg_btn)
        input_args_buttons.addStretch()
        input_args_layout.addLayout(input_args_buttons)

        layout.addWidget(input_args_group)

        # JSON output section
        json_group = QGroupBox("JSON Output")
        json_layout = QVBoxLayout(json_group)

        self.action_json_edit = QTextEdit()
        self.action_json_edit.setPlaceholderText("Paste the JSON output this action will produce...")
        self.action_json_edit.setToolTip(get_tooltip("json_output"))
        json_layout.addWidget(self.action_json_edit)

        parse_json_btn = QPushButton("Parse & Save JSON Output")
        parse_json_btn.clicked.connect(self._parse_action_json)
        parse_json_btn.setToolTip(get_tooltip("parse_json"))
        json_layout.addWidget(parse_json_btn)

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
        self.script_output_key_edit.setToolTip(get_tooltip("output_key"))
        self.script_output_key_edit.setPlaceholderText("e.g., processed_data")
        form_layout.addRow("Output Key:", self.script_output_key_edit)

        layout.addWidget(form_group)

        # Script code section
        code_group = QGroupBox("APIthon Script Code")
        code_layout = QVBoxLayout(code_group)

        self.script_code_edit = QTextEdit()
        self.script_code_edit.setPlaceholderText("Enter your APIthon script code here...\n\n# Example:\nuser_name = data.user_info.user.name\nresult = {'greeting': f'Hello, {user_name}!'}\nreturn result")
        self.script_code_edit.setToolTip(get_tooltip("script_code"))
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.script_code_edit.setFont(font)
        self.script_code_edit.textChanged.connect(self._on_script_data_changed)
        code_layout.addWidget(self.script_code_edit)

        layout.addWidget(code_group)

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
        self.script_code_edit.setPlainText(step.code or "")

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
        self.current_step.code = self.script_code_edit.toPlainText()

        # Update input args from table
        self.current_step.input_args = {}
        for row in range(self.script_input_args_table.rowCount()):
            key_item = self.script_input_args_table.item(row, 0)
            value_item = self.script_input_args_table.item(row, 1)
            if key_item and value_item and key_item.text():
                self.current_step.input_args[key_item.text()] = value_item.text()

        self.step_updated.emit()

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
    """Panel for displaying the generated YAML."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("YAML Preview")
        header_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(header_label)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_yaml)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # YAML text display
        self.yaml_text = QTextEdit()
        self.yaml_text.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.yaml_text.setFont(font)
        layout.addWidget(self.yaml_text)

        # Validation status with enhanced display
        self.validation_status = StatusIndicator("Ready")
        self.validation_status.setToolTip(get_tooltip("validation_status"))
        layout.addWidget(self.validation_status)

        # Detailed error display (initially hidden)
        self.error_display = ErrorListWidget()
        self.error_display.setMaximumHeight(200)
        self.error_display.hide()
        layout.addWidget(self.error_display)

        self.workflow = None

    def set_workflow(self, workflow: Workflow):
        """Set the workflow and update the YAML preview."""
        self.workflow = workflow
        self.refresh_yaml()

    def refresh_yaml(self):
        """Refresh the YAML preview and validation."""
        if not self.workflow or not self.workflow.steps:
            self.yaml_text.setPlainText("No steps in workflow")
            self.validation_status.set_status("ready", "No steps to validate")
            self.error_display.clear_errors()
            self.error_display.hide()
            return

        try:
            # Generate YAML
            yaml_content = generate_yaml_string(self.workflow)
            self.yaml_text.setPlainText(yaml_content)

            # Validate workflow
            errors = comprehensive_validate(self.workflow)

            if errors:
                self.validation_status.set_error_count(len(errors))
                self.error_display.set_errors(errors)
                self.error_display.show()
            else:
                self.validation_status.set_error_count(0)
                self.error_display.clear_errors()
                self.error_display.hide()

        except Exception as e:
            self.yaml_text.setPlainText(f"Error generating YAML: {str(e)}")
            self.validation_status.set_status("error", "YAML Generation Error")
            self.error_display.set_errors([f"YAML Generation Error: {str(e)}"])
            self.error_display.show()


class MainWindow(QMainWindow):
    """Main application window for the Moveworks YAML Assistant."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moveworks YAML Assistant")
        self.setGeometry(100, 100, 1400, 900)

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

        # Center panel: Step configuration
        self.config_panel = StepConfigurationPanel()
        self.config_panel.step_updated.connect(self._on_step_updated)
        main_splitter.addWidget(self.config_panel)

        # Right panel: JSON variable selection and YAML preview
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([300, 500, 400])

        # Create menu bar
        self._create_menu_bar()

        # Connect signals
        self.workflow_list.step_selected.connect(self._on_step_selected)
        self.json_panel.variable_selected.connect(self._on_variable_selected)

        # Initialize with empty workflow
        self._update_all_panels()

    def _create_left_panel(self):
        """Create the left panel with step list and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Header
        header_label = QLabel("Workflow Steps")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header_label)

        # Step list
        self.workflow_list = WorkflowListWidget()
        layout.addWidget(self.workflow_list)

        # Control buttons
        button_layout = QVBoxLayout()

        # Basic step types
        add_action_btn = QPushButton("Add Action Step")
        add_action_btn.clicked.connect(self._add_action_step)
        add_action_btn.setToolTip(get_tooltip("add_action"))
        button_layout.addWidget(add_action_btn)

        add_script_btn = QPushButton("Add Script Step")
        add_script_btn.clicked.connect(self._add_script_step)
        add_script_btn.setToolTip(get_tooltip("add_script"))
        button_layout.addWidget(add_script_btn)

        # Control flow step types
        add_switch_btn = QPushButton("Add Switch Step")
        add_switch_btn.clicked.connect(self._add_switch_step)
        button_layout.addWidget(add_switch_btn)

        add_for_btn = QPushButton("Add For Loop Step")
        add_for_btn.clicked.connect(self._add_for_step)
        button_layout.addWidget(add_for_btn)

        add_parallel_btn = QPushButton("Add Parallel Step")
        add_parallel_btn.clicked.connect(self._add_parallel_step)
        button_layout.addWidget(add_parallel_btn)

        add_return_btn = QPushButton("Add Return Step")
        add_return_btn.clicked.connect(self._add_return_step)
        button_layout.addWidget(add_return_btn)

        # Error handling step types
        add_try_catch_btn = QPushButton("Add Try/Catch Step")
        add_try_catch_btn.clicked.connect(self._add_try_catch_step)
        button_layout.addWidget(add_try_catch_btn)

        add_raise_btn = QPushButton("Add Raise Step")
        add_raise_btn.clicked.connect(self._add_raise_step)
        button_layout.addWidget(add_raise_btn)

        # Built-in actions
        add_mw_action_btn = QPushButton("Add Built-in Action")
        add_mw_action_btn.clicked.connect(self._add_mw_action_step)
        add_mw_action_btn.setToolTip(get_tooltip("add_builtin"))
        button_layout.addWidget(add_mw_action_btn)

        button_layout.addWidget(QLabel())  # Spacer

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_selected_step)
        remove_btn.setToolTip(get_tooltip("remove_step"))
        button_layout.addWidget(remove_btn)

        move_up_btn = QPushButton("Move Up")
        move_up_btn.clicked.connect(self._move_step_up)
        move_up_btn.setToolTip(get_tooltip("move_up"))
        button_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton("Move Down")
        move_down_btn.clicked.connect(self._move_step_down)
        move_down_btn.setToolTip(get_tooltip("move_down"))
        button_layout.addWidget(move_down_btn)

        layout.addLayout(button_layout)

        return panel

    def _create_right_panel(self):
        """Create the right panel with JSON selection and YAML preview."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Create splitter for top/bottom sections
        right_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(right_splitter)

        # JSON variable selection panel
        self.json_panel = JsonVariableSelectionPanel()
        right_splitter.addWidget(self.json_panel)

        # YAML preview panel
        self.yaml_panel = YamlPreviewPanel()
        right_splitter.addWidget(self.yaml_panel)

        # Set splitter proportions
        right_splitter.setSizes([300, 400])

        return panel

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

        export_yaml_action = QAction("Export YAML...", self)
        export_yaml_action.triggered.connect(self._export_yaml)
        file_menu.addAction(export_yaml_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        validate_action = QAction("Validate Workflow", self)
        validate_action.setShortcut("F5")
        validate_action.triggered.connect(self._validate_workflow)
        edit_menu.addAction(validate_action)

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
        """Handle step selection from the workflow list."""
        if 0 <= step_index < len(self.workflow_list.workflow.steps):
            step = self.workflow_list.workflow.steps[step_index]
            self.config_panel.set_step(step, step_index)
            self.json_panel.set_workflow(self.workflow_list.workflow, step_index)
        else:
            self.config_panel.clear_selection()

    def _on_step_updated(self):
        """Handle updates to step configuration."""
        self.workflow_list.update_workflow_display()
        self.yaml_panel.refresh_yaml()

    def _on_variable_selected(self, path: str):
        """Handle variable selection from the JSON panel."""
        # This could be used to automatically insert the path into input fields
        # For now, we just copy it to clipboard
        QApplication.clipboard().setText(path)

    def _update_all_panels(self):
        """Update all panels with the current workflow."""
        self.json_panel.set_workflow(self.workflow_list.workflow)
        self.yaml_panel.set_workflow(self.workflow_list.workflow)

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

    def _export_yaml(self):
        """Export the generated YAML to file."""
        from PySide6.QtWidgets import QFileDialog

        if not self.workflow_list.workflow.steps:
            QMessageBox.warning(self, "Warning", "No steps in workflow to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export YAML", "", "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if filename:
            try:
                yaml_content = generate_yaml_string(self.workflow_list.workflow)
                with open(filename, 'w') as f:
                    f.write(yaml_content)

                QMessageBox.information(self, "Success", f"YAML exported to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export YAML: {str(e)}")

    def _validate_workflow(self):
        """Validate the current workflow and show results."""
        if not self.workflow_list.workflow.steps:
            QMessageBox.information(self, "Validation", "No steps in workflow to validate.")
            return

        errors = comprehensive_validate(self.workflow_list.workflow)

        # Show detailed validation dialog
        dialog = ValidationDialog(errors, self)
        dialog.exec()

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


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Moveworks YAML Assistant")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Moveworks")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()