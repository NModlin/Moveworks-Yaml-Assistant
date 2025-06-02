"""
Workflow Creation Wizard for the Moveworks YAML Assistant.

This module provides a step-by-step wizard for guided workflow creation,
making it easier for beginners to create workflows without needing to understand
all the technical details upfront.
"""

from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QListWidget, QListWidgetItem, QPushButton,
    QGroupBox, QFormLayout, QCheckBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette

from core_structures import Workflow, InputVariable
from expression_factory import ExpressionFactory, CommonPatterns
from template_library import SimplifiedTemplateSystem


class WorkflowWizard(QWizard):
    """A step-by-step wizard for creating common workflows."""
    
    workflow_created = Signal(object)  # Emits the created workflow
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Workflow - Step by Step")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(800, 600)
        
        # Initialize data storage
        self.workflow_data = {}
        self.template_system = SimplifiedTemplateSystem()
        
        # Apply modern styling
        self.setStyleSheet("""
            QWizard {
                background-color: #f8f9fa;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }
            QWizardPage {
                background-color: #ffffff;
                border-radius: 8px;
                margin: 8px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #4a86e8;
                outline: none;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3d71d9;
            }
            QPushButton:pressed {
                background-color: #2c5aa0;
            }
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                background-color: #ffffff;
            }
        """)
        
        # Register fields for data collection
        self.registerField("workflow_type*", QComboBox(), "currentText")
        self.registerField("action_name*", QLineEdit())
        self.registerField("description", QTextEdit(), "plainText")
        
        # Add wizard pages
        self.addPage(self.createIntroPage())
        self.addPage(self.createWorkflowTypePage())
        self.addPage(self.createBasicInfoPage())
        self.addPage(self.createInputVariablesPage())
        self.addPage(self.createStepsPage())
        self.addPage(self.createSummaryPage())
    
    def createIntroPage(self):
        """Create the introduction page."""
        page = QWizardPage()
        page.setTitle("Welcome to the Workflow Wizard")
        page.setSubTitle("This wizard will guide you through creating a Moveworks workflow step by step.")
        
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Welcome message
        welcome_label = QLabel("""
        <h2>Create Your First Workflow</h2>
        <p>This wizard will help you create a Moveworks Compound Action workflow without needing to know all the technical details.</p>
        
        <p><b>What you'll do:</b></p>
        <ul>
        <li>Choose a workflow type or start from scratch</li>
        <li>Define basic information and input variables</li>
        <li>Configure workflow steps</li>
        <li>Review and create your workflow</li>
        </ul>
        
        <p>Don't worry - you can always modify the workflow later using the full editor!</p>
        """)
        welcome_label.setWordWrap(True)
        welcome_label.setStyleSheet("font-size: 14px; line-height: 1.5;")
        layout.addWidget(welcome_label)
        
        layout.addStretch()
        return page
    
    def createWorkflowTypePage(self):
        """Create the workflow type selection page."""
        page = QWizardPage()
        page.setTitle("Choose Workflow Type")
        page.setSubTitle("Select a template to get started quickly, or create a custom workflow")
        
        layout = QVBoxLayout(page)
        
        # Template selection
        template_group = QGroupBox("Quick Start Templates")
        template_layout = QVBoxLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("Custom Workflow (Start from scratch)")
        
        # Add templates from simplified template system
        for key, template in self.template_system.templates.items():
            display_text = f"{template['name']} - {template['description']}"
            self.template_combo.addItem(display_text)
            self.template_combo.setItemData(self.template_combo.count() - 1, key)
        
        self.registerField("workflow_type", self.template_combo, "currentText")
        template_layout.addWidget(self.template_combo)
        
        # Template description
        self.template_description = QTextEdit()
        self.template_description.setReadOnly(True)
        self.template_description.setMaximumHeight(120)
        self.template_description.setPlainText("Select a template to see its description and complexity level.")
        template_layout.addWidget(self.template_description)
        
        # Connect selection change
        self.template_combo.currentTextChanged.connect(self.updateTemplateDescription)
        
        layout.addWidget(template_group)
        layout.addStretch()
        
        return page
    
    def createBasicInfoPage(self):
        """Create the basic information page."""
        page = QWizardPage()
        page.setTitle("Basic Information")
        page.setSubTitle("Provide basic details about your workflow")
        
        layout = QVBoxLayout(page)
        
        # Form layout for basic info
        form_group = QGroupBox("Workflow Details")
        form_layout = QFormLayout(form_group)
        
        # Action name
        self.action_name_edit = QLineEdit()
        self.action_name_edit.setPlaceholderText("e.g., user_onboarding_workflow")
        self.registerField("action_name*", self.action_name_edit)
        form_layout.addRow("Action Name:", self.action_name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe what this workflow does...")
        self.description_edit.setMaximumHeight(100)
        self.registerField("description", self.description_edit, "plainText")
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(form_group)
        layout.addStretch()
        
        return page
    
    def createInputVariablesPage(self):
        """Create the input variables configuration page."""
        page = QWizardPage()
        page.setTitle("Input Variables")
        page.setSubTitle("Define what data your workflow needs to receive")
        
        layout = QVBoxLayout(page)
        
        # Instructions
        instructions = QLabel("""
        <b>Input Variables</b> are the data that your workflow receives when it starts.
        For example, if your workflow looks up a user, you might need an "email" input variable.
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin-bottom: 16px; padding: 12px; background-color: #e3f2fd; border-radius: 6px;")
        layout.addWidget(instructions)
        
        # Input variables table
        variables_group = QGroupBox("Input Variables")
        variables_layout = QVBoxLayout(variables_group)
        
        self.variables_table = QTableWidget(0, 4)
        self.variables_table.setHorizontalHeaderLabels(["Name", "Type", "Required", "Description"])
        self.variables_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        variables_layout.addWidget(self.variables_table)
        
        # Buttons for managing variables
        button_layout = QHBoxLayout()
        add_var_btn = QPushButton("Add Variable")
        add_var_btn.clicked.connect(self.addInputVariable)
        button_layout.addWidget(add_var_btn)
        
        remove_var_btn = QPushButton("Remove Selected")
        remove_var_btn.clicked.connect(self.removeInputVariable)
        button_layout.addWidget(remove_var_btn)
        
        button_layout.addStretch()
        variables_layout.addLayout(button_layout)
        
        layout.addWidget(variables_group)
        
        return page
    
    def createStepsPage(self):
        """Create the steps configuration page."""
        page = QWizardPage()
        page.setTitle("Workflow Steps")
        page.setSubTitle("Configure the actions your workflow will perform")
        
        layout = QVBoxLayout(page)
        
        # Instructions
        instructions = QLabel("""
        <b>Workflow Steps</b> are the individual actions your workflow performs.
        You can add actions (calling Moveworks functions) or scripts (custom code).
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin-bottom: 16px; padding: 12px; background-color: #e8f5e8; border-radius: 6px;")
        layout.addWidget(instructions)
        
        # Steps configuration will be implemented based on selected template
        self.steps_widget = QLabel("Steps configuration will be shown here based on your template selection.")
        self.steps_widget.setStyleSheet("padding: 20px; text-align: center; color: #666;")
        layout.addWidget(self.steps_widget)
        
        return page
    
    def createSummaryPage(self):
        """Create the summary and confirmation page."""
        page = QWizardPage()
        page.setTitle("Review and Create")
        page.setSubTitle("Review your workflow configuration and create it")
        
        layout = QVBoxLayout(page)
        
        # Summary display
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
        return page
    
    def updateTemplateDescription(self, template_text):
        """Update the template description when selection changes."""
        if template_text == "Custom Workflow (Start from scratch)":
            self.template_description.setPlainText(
                "Create a completely custom workflow from scratch. "
                "You'll define all steps manually. Complexity: Variable"
            )
        else:
            # Find the template key from the combo box
            current_index = self.template_combo.currentIndex()
            if current_index > 0:  # Skip the first "Custom" option
                template_key = self.template_combo.itemData(current_index)
                if template_key:
                    template = self.template_system.get_template_by_key(template_key)
                    if template:
                        description = f"{template['description']}\n\n"
                        description += f"Category: {template['category']}\n"
                        description += f"Complexity: {template['complexity']}"
                        self.template_description.setPlainText(description)
    
    def addInputVariable(self):
        """Add a new input variable row."""
        row = self.variables_table.rowCount()
        self.variables_table.insertRow(row)
        
        # Name
        name_item = QTableWidgetItem("variable_name")
        self.variables_table.setItem(row, 0, name_item)
        
        # Type
        type_combo = QComboBox()
        type_combo.addItems(["string", "number", "boolean", "object", "array"])
        self.variables_table.setCellWidget(row, 1, type_combo)
        
        # Required
        required_checkbox = QCheckBox()
        required_checkbox.setChecked(True)
        self.variables_table.setCellWidget(row, 2, required_checkbox)
        
        # Description
        desc_item = QTableWidgetItem("Description of the variable")
        self.variables_table.setItem(row, 3, desc_item)
    
    def removeInputVariable(self):
        """Remove the selected input variable."""
        current_row = self.variables_table.currentRow()
        if current_row >= 0:
            self.variables_table.removeRow(current_row)
    
    def validateCurrentPage(self):
        """Validate the current page before proceeding."""
        current_id = self.currentId()
        
        if current_id == 2:  # Basic info page
            action_name = self.action_name_edit.text().strip()
            if not action_name:
                QMessageBox.warning(self, "Validation Error", "Please enter an action name.")
                return False
            
            # Check for valid action name format
            if not action_name.replace('_', '').replace('-', '').isalnum():
                QMessageBox.warning(self, "Validation Error", 
                                  "Action name should only contain letters, numbers, underscores, and hyphens.")
                return False
        
        return super().validateCurrentPage()
    
    def accept(self):
        """Create the workflow when the wizard is completed."""
        try:
            workflow = self.createWorkflowFromData()
            self.workflow_created.emit(workflow)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create workflow: {str(e)}")
    
    def createWorkflowFromData(self):
        """Create a Workflow object from the collected data."""
        # Get basic info
        action_name = self.field("action_name")
        description = self.field("description")
        
        # Create input variables
        input_variables = []
        for row in range(self.variables_table.rowCount()):
            name_item = self.variables_table.item(row, 0)
            type_widget = self.variables_table.cellWidget(row, 1)
            required_widget = self.variables_table.cellWidget(row, 2)
            desc_item = self.variables_table.item(row, 3)
            
            if name_item and type_widget and required_widget and desc_item:
                input_var = InputVariable(
                    name=name_item.text(),
                    data_type=type_widget.currentText(),
                    description=desc_item.text(),
                    required=required_widget.isChecked()
                )
                input_variables.append(input_var)
        
        # Create workflow steps based on template or custom configuration
        steps = []
        template_text = self.field("workflow_type")
        
        if template_text != "Custom Workflow (Start from scratch)":
            # Use template-based steps
            current_index = self.template_combo.currentIndex()
            if current_index > 0:
                template_key = self.template_combo.itemData(current_index)
                if template_key == "user_lookup":
                    steps = CommonPatterns.user_lookup_pattern()
                elif template_key == "send_notification":
                    steps = [ExpressionFactory.create_action(
                        action_name="mw.send_notification",
                        output_key="notification_result",
                        input_args={
                            "message": "data.message",
                            "recipient": "data.recipient_email"
                        }
                    )]
                # Add more template implementations as needed
        
        # If no steps were created, add a default action step
        if not steps:
            steps = [ExpressionFactory.create_action(
                action_name="mw.placeholder_action",
                output_key="result",
                description="Placeholder action - please configure"
            )]
        
        # Create and return the workflow
        workflow = Workflow(steps=steps, input_variables=input_variables)
        return workflow
