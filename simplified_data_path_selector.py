"""
Simplified Data Path Selector for the Moveworks YAML Assistant.

This module provides a more intuitive UI for selecting data paths,
focusing on common patterns and making it easier for beginners to understand
data flow in workflows.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QDialog, QDialogButtonBox,
    QComboBox, QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from core_structures import Workflow


class SimplifiedDataPathSelector(QWidget):
    """A more straightforward data path selector focused on common patterns."""
    
    path_selected = Signal(str)  # Signal emitted when a path is selected
    
    def __init__(self, workflow=None, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.recent_paths = []  # Store recently used paths
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # Apply modern styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }
            QGroupBox {
                font-weight: 600;
                color: #2c3e50;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3d71d9;
            }
            QPushButton:pressed {
                background-color: #2c5aa0;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #e1e8ed;
                border-radius: 6px;
                font-size: 13px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 4px;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #4a86e8;
                color: white;
            }
        """)
        
        # Header
        header_label = QLabel("🔍 Data Path Selector")
        header_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px;
            background-color: #e3f2fd;
            border-radius: 6px;
            border: 1px solid #4a86e8;
        """)
        layout.addWidget(header_label)
        
        # Common data sources section
        sources_group = QGroupBox("Common Data Sources")
        sources_layout = QVBoxLayout(sources_group)
        sources_layout.setSpacing(8)
        
        # Create buttons for common data sources
        self.createDataSourceButton(sources_layout, "📧 Input Variables", "data.", 
                                   "Variables passed to your workflow when it starts")
        self.createDataSourceButton(sources_layout, "👤 Current User", "meta_info.user.", 
                                   "Information about the user running the workflow")
        self.createDataSourceButton(sources_layout, "📋 Previous Steps", "data.", 
                                   "Output from previous workflow steps")
        self.createDataSourceButton(sources_layout, "✏️ Custom Path", "", 
                                   "Enter a custom data path manually")
        
        layout.addWidget(sources_group)
        
        # Recent paths section
        recent_group = QGroupBox("Recent Paths")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(120)
        self.recent_list.itemDoubleClicked.connect(self.selectRecentPath)
        recent_layout.addWidget(self.recent_list)
        
        # Add some example recent paths
        self.addRecentPath("data.user_email")
        self.addRecentPath("data.user_info.user.name")
        self.addRecentPath("meta_info.user.email")
        
        layout.addWidget(recent_group)
        
        # Quick reference section
        reference_group = QGroupBox("Quick Reference")
        reference_layout = QVBoxLayout(reference_group)
        
        reference_text = QLabel("""
        <b>Common Patterns:</b><br>
        • <code>data.variable_name</code> - Input variables<br>
        • <code>data.step_output.field</code> - Output from previous steps<br>
        • <code>meta_info.user.email</code> - Current user's email<br>
        • <code>meta_info.user.name</code> - Current user's name
        """)
        reference_text.setWordWrap(True)
        reference_text.setStyleSheet("""
            padding: 12px;
            background-color: #f8f9fa;
            border-radius: 6px;
            font-size: 12px;
            line-height: 1.4;
        """)
        reference_layout.addWidget(reference_text)
        
        layout.addWidget(reference_group)
        
        layout.addStretch()
        
    def createDataSourceButton(self, layout, label, prefix, tooltip):
        """Create a data source button with icon and description."""
        button = QPushButton(label)
        button.setToolTip(tooltip)
        button.setMinimumHeight(50)
        button.clicked.connect(lambda: self.handleSourceSelected(prefix, label))
        layout.addWidget(button)
        
    def handleSourceSelected(self, prefix, source_type):
        """Handle data source selection."""
        if prefix == "data." and "Input Variables" in source_type:
            self.showInputVariablesDialog()
        elif prefix == "meta_info.user.":
            self.showUserFieldsDialog()
        elif prefix == "data." and "Previous Steps" in source_type:
            self.showPreviousStepsDialog()
        else:
            self.showCustomPathDialog()
    
    def showInputVariablesDialog(self):
        """Show dialog for selecting input variables."""
        dialog = InputVariablesDialog(self.workflow, self)
        if dialog.exec() == QDialog.Accepted:
            selected_path = dialog.getSelectedPath()
            if selected_path:
                self.selectPath(selected_path)
    
    def showUserFieldsDialog(self):
        """Show dialog for selecting user fields."""
        dialog = UserFieldsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_path = dialog.getSelectedPath()
            if selected_path:
                self.selectPath(selected_path)
    
    def showPreviousStepsDialog(self):
        """Show dialog for selecting previous step outputs."""
        dialog = PreviousStepsDialog(self.workflow, self)
        if dialog.exec() == QDialog.Accepted:
            selected_path = dialog.getSelectedPath()
            if selected_path:
                self.selectPath(selected_path)
    
    def showCustomPathDialog(self):
        """Show dialog for entering custom paths."""
        dialog = CustomPathDialog(self)
        if dialog.exec() == QDialog.Accepted:
            custom_path = dialog.getCustomPath()
            if custom_path:
                self.selectPath(custom_path)
    
    def selectPath(self, path):
        """Select a data path and emit the signal."""
        self.addRecentPath(path)
        self.path_selected.emit(path)
    
    def selectRecentPath(self, item):
        """Select a path from the recent paths list."""
        path = item.text()
        self.path_selected.emit(path)
    
    def addRecentPath(self, path):
        """Add a path to the recent paths list."""
        # Remove if already exists
        for i in range(self.recent_list.count()):
            if self.recent_list.item(i).text() == path:
                self.recent_list.takeItem(i)
                break
        
        # Add to top
        item = QListWidgetItem(path)
        item.setToolTip(f"Click to use: {path}")
        self.recent_list.insertItem(0, item)
        
        # Keep only last 10 items
        while self.recent_list.count() > 10:
            self.recent_list.takeItem(self.recent_list.count() - 1)
    
    def setWorkflow(self, workflow):
        """Update the workflow reference."""
        self.workflow = workflow


class InputVariablesDialog(QDialog):
    """Dialog for selecting input variables."""
    
    def __init__(self, workflow, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.selected_path = None
        self.setWindowTitle("Select Input Variable")
        self.setModal(True)
        self.resize(400, 300)
        self.setupUI()
    
    def setupUI(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select an input variable that your workflow receives:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Variables list
        self.variables_list = QListWidget()
        
        if self.workflow and self.workflow.input_variables:
            for var in self.workflow.input_variables:
                item = QListWidgetItem(f"data.{var.name}")
                item.setToolTip(f"Type: {var.data_type}\nDescription: {var.description}")
                item.setData(Qt.UserRole, f"data.{var.name}")
                self.variables_list.addItem(item)
        else:
            # Add some common examples
            examples = [
                ("data.user_email", "User's email address"),
                ("data.user_id", "User's unique identifier"),
                ("data.message", "Message content"),
                ("data.request_details", "Request details")
            ]
            for path, desc in examples:
                item = QListWidgetItem(path)
                item.setToolTip(desc)
                item.setData(Qt.UserRole, path)
                self.variables_list.addItem(item)
        
        self.variables_list.itemDoubleClicked.connect(self.selectVariable)
        layout.addWidget(self.variables_list)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def selectVariable(self, item):
        """Select a variable and close dialog."""
        self.selected_path = item.data(Qt.UserRole)
        self.accept()
    
    def accept(self):
        """Accept the dialog with selected item."""
        current_item = self.variables_list.currentItem()
        if current_item:
            self.selected_path = current_item.data(Qt.UserRole)
        super().accept()
    
    def getSelectedPath(self):
        """Get the selected path."""
        return self.selected_path


class UserFieldsDialog(QDialog):
    """Dialog for selecting user fields."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self.setWindowTitle("Select User Field")
        self.setModal(True)
        self.resize(400, 300)
        self.setupUI()
    
    def setupUI(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select a field from the current user's information:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # User fields list
        self.fields_list = QListWidget()
        
        user_fields = [
            ("meta_info.user.email", "User's email address"),
            ("meta_info.user.name", "User's full name"),
            ("meta_info.user.id", "User's unique identifier"),
            ("meta_info.user.department", "User's department"),
            ("meta_info.user.manager", "User's manager"),
            ("meta_info.user.title", "User's job title")
        ]
        
        for path, desc in user_fields:
            item = QListWidgetItem(path)
            item.setToolTip(desc)
            item.setData(Qt.UserRole, path)
            self.fields_list.addItem(item)
        
        self.fields_list.itemDoubleClicked.connect(self.selectField)
        layout.addWidget(self.fields_list)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def selectField(self, item):
        """Select a field and close dialog."""
        self.selected_path = item.data(Qt.UserRole)
        self.accept()
    
    def accept(self):
        """Accept the dialog with selected item."""
        current_item = self.fields_list.currentItem()
        if current_item:
            self.selected_path = current_item.data(Qt.UserRole)
        super().accept()
    
    def getSelectedPath(self):
        """Get the selected path."""
        return self.selected_path


class PreviousStepsDialog(QDialog):
    """Dialog for selecting previous step outputs."""
    
    def __init__(self, workflow, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.selected_path = None
        self.setWindowTitle("Select Previous Step Output")
        self.setModal(True)
        self.resize(500, 400)
        self.setupUI()
    
    def setupUI(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select output from a previous workflow step:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Steps tree
        self.steps_tree = QTreeWidget()
        self.steps_tree.setHeaderLabels(["Step", "Output Key", "Path"])
        
        if self.workflow and self.workflow.steps:
            for i, step in enumerate(self.workflow.steps):
                step_item = QTreeWidgetItem([f"Step {i+1}", "", ""])
                
                # Add output key if available
                output_key = getattr(step, 'output_key', None)
                if output_key:
                    output_item = QTreeWidgetItem([f"  {output_key}", output_key, f"data.{output_key}"])
                    output_item.setData(0, Qt.UserRole, f"data.{output_key}")
                    step_item.addChild(output_item)
                
                self.steps_tree.addTopLevelItem(step_item)
        else:
            # Add examples
            examples = [
                ("Step 1: User Lookup", "user_info", "data.user_info"),
                ("Step 2: Send Email", "email_result", "data.email_result")
            ]
            for step_name, output_key, path in examples:
                step_item = QTreeWidgetItem([step_name, "", ""])
                output_item = QTreeWidgetItem([f"  {output_key}", output_key, path])
                output_item.setData(0, Qt.UserRole, path)
                step_item.addChild(output_item)
                self.steps_tree.addTopLevelItem(step_item)
        
        self.steps_tree.expandAll()
        self.steps_tree.itemDoubleClicked.connect(self.selectStep)
        layout.addWidget(self.steps_tree)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def selectStep(self, item, column):
        """Select a step output and close dialog."""
        path = item.data(0, Qt.UserRole)
        if path:
            self.selected_path = path
            self.accept()
    
    def accept(self):
        """Accept the dialog with selected item."""
        current_item = self.steps_tree.currentItem()
        if current_item:
            path = current_item.data(0, Qt.UserRole)
            if path:
                self.selected_path = path
        super().accept()
    
    def getSelectedPath(self):
        """Get the selected path."""
        return self.selected_path


class CustomPathDialog(QDialog):
    """Dialog for entering custom data paths."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.custom_path = None
        self.setWindowTitle("Enter Custom Path")
        self.setModal(True)
        self.resize(400, 200)
        self.setupUI()
    
    def setupUI(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Enter a custom data path:")
        layout.addWidget(instructions)
        
        # Path input
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("e.g., data.custom_field.nested_value")
        layout.addWidget(self.path_edit)
        
        # Examples
        examples = QLabel("""
        <b>Examples:</b><br>
        • data.field_name<br>
        • data.step_output.nested_field<br>
        • meta_info.user.custom_attribute
        """)
        examples.setStyleSheet("font-size: 11px; color: #666; margin: 8px 0;")
        layout.addWidget(examples)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept(self):
        """Accept the dialog with entered path."""
        self.custom_path = self.path_edit.text().strip()
        if self.custom_path:
            super().accept()
    
    def getCustomPath(self):
        """Get the custom path."""
        return self.custom_path
