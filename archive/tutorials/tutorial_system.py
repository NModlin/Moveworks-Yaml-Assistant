"""
Interactive Tutorial System for the Moveworks YAML Assistant.

This module provides guided tutorials to help users learn the application.
"""

import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QTextEdit, QWidget, QFrame, QScrollArea, QComboBox,
    QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QPoint
from PySide6.QtGui import QFont, QPalette, QPainter, QColor, QPixmap


@dataclass
class TutorialStep:
    """Represents a single step in a tutorial."""
    title: str
    description: str
    target_element: Optional[str] = None  # CSS selector or widget name
    action: Optional[str] = None  # Action to perform (click, type, etc.)
    action_data: Optional[Dict[str, Any]] = None  # Data for the action
    validation: Optional[Callable] = None  # Function to validate step completion
    auto_advance: bool = False  # Whether to auto-advance after action
    delay: int = 1000  # Delay before auto-advance (ms)


class TutorialOverlay(QWidget):
    """Overlay widget that highlights tutorial targets and shows instructions."""

    step_completed = Signal()
    tutorial_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.current_step = None
        self.target_widget = None
        self.target_rect = QRect()

        # Create instruction panel with better sizing
        self.instruction_panel = QFrame(self)
        self.instruction_panel.setMinimumSize(400, 250)
        self.instruction_panel.setMaximumSize(600, 500)
        self.instruction_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.98);
                border: 3px solid #2196F3;
                border-radius: 12px;
                padding: 15px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                line-height: 1.4;
            }
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                min-height: 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        panel_layout = QVBoxLayout(self.instruction_panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(15)

        # Step title
        self.step_title = QLabel()
        self.step_title.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: #1976D2;
            margin-bottom: 8px;
        """)
        self.step_title.setWordWrap(True)
        panel_layout.addWidget(self.step_title)

        # Step description
        self.step_description = QLabel()
        self.step_description.setWordWrap(True)
        self.step_description.setStyleSheet("""
            color: #2c3e50;
            font-size: 13px;
            line-height: 1.5;
            margin: 8px 0px;
        """)
        panel_layout.addWidget(self.step_description)

        # Add some stretch to push buttons to bottom
        panel_layout.addStretch()

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 10, 0, 0)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.step_completed.emit)
        self.skip_button.setMinimumSize(80, 35)
        button_layout.addWidget(self.skip_button)

        button_layout.addStretch()  # Push buttons apart

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.step_completed.emit)
        self.next_button.setDefault(True)
        self.next_button.setMinimumSize(80, 35)
        button_layout.addWidget(self.next_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.tutorial_cancelled.emit)
        self.cancel_button.setMinimumSize(80, 35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                min-height: 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(self.cancel_button)

        panel_layout.addLayout(button_layout)

        # Auto-advance timer
        self.auto_advance_timer = QTimer()
        self.auto_advance_timer.setSingleShot(True)
        self.auto_advance_timer.timeout.connect(self.step_completed.emit)

    def show_step(self, step: TutorialStep, target_widget: QWidget = None):
        """Show a tutorial step with optional target highlighting."""
        self.current_step = step
        self.target_widget = target_widget

        # Update instruction panel
        self.step_title.setText(step.title)
        self.step_description.setText(step.description)

        # Position overlay to cover parent
        if self.parent():
            self.setGeometry(self.parent().rect())

        # Calculate target rectangle
        if target_widget:
            self.target_rect = target_widget.geometry()
            if target_widget.parent():
                # Convert to global coordinates
                global_pos = target_widget.parent().mapToGlobal(self.target_rect.topLeft())
                local_pos = self.mapFromGlobal(global_pos)
                self.target_rect.moveTo(local_pos)
        else:
            self.target_rect = QRect()

        # Position instruction panel
        self._position_instruction_panel()

        # Show overlay
        self.show()
        self.raise_()

        # Setup auto-advance if enabled
        if step.auto_advance:
            self.auto_advance_timer.start(step.delay)

    def _position_instruction_panel(self):
        """Position the instruction panel relative to the target."""
        panel_size = self.instruction_panel.sizeHint()

        if self.target_rect.isValid():
            # Position panel to the right of target, or below if no space
            x = self.target_rect.right() + 20
            y = self.target_rect.top()

            # Check if panel fits on the right
            if x + panel_size.width() > self.width():
                # Position below target
                x = self.target_rect.left()
                y = self.target_rect.bottom() + 20

                # Check if panel fits below
                if y + panel_size.height() > self.height():
                    # Position above target
                    y = self.target_rect.top() - panel_size.height() - 20
        else:
            # Center panel if no target
            x = (self.width() - panel_size.width()) // 2
            y = (self.height() - panel_size.height()) // 2

        self.instruction_panel.move(max(10, x), max(10, y))
        self.instruction_panel.resize(panel_size)

    def paintEvent(self, event):
        """Paint the overlay with target highlighting."""
        painter = QPainter(self)

        # Draw semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # Highlight target area
        if self.target_rect.isValid():
            # Clear the target area
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(self.target_rect, QColor(0, 0, 0, 0))

            # Draw highlight border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QColor(33, 150, 243, 200))  # Blue highlight
            painter.drawRect(self.target_rect.adjusted(-2, -2, 2, 2))


class TutorialDialog(QDialog):
    """Dialog for selecting and starting tutorials."""

    tutorial_selected = Signal(str)  # Emits tutorial ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interactive Tutorials")
        self.setModal(True)

        # Set larger minimum size and make it resizable
        self.setMinimumSize(900, 650)
        self.resize(1000, 750)

        # Apply enhanced styling for better readability
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #2c3e50;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 13px;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #ebf3fd;
                color: #2c3e50;
            }
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                color: #2c3e50;
                line-height: 1.4;
            }
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        self.tutorials = {}
        self._setup_ui()
        self._load_tutorials()

    def _setup_ui(self):
        """Setup the tutorial selection UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_label = QLabel("Choose a Tutorial")
        header_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            padding: 15px 0px;
        """)
        layout.addWidget(header_label)

        # Tutorial list with better sizing
        self.tutorial_list = QListWidget()
        self.tutorial_list.itemDoubleClicked.connect(self._start_selected_tutorial)
        self.tutorial_list.setMinimumHeight(280)
        layout.addWidget(self.tutorial_list)

        # Tutorial description with better sizing
        description_label = QLabel("Tutorial Details:")
        description_label.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            margin-top: 15px;
            font-size: 16px;
        """)
        layout.addWidget(description_label)

        self.description_text = QTextEdit()
        self.description_text.setMinimumHeight(180)
        self.description_text.setMaximumHeight(250)
        self.description_text.setReadOnly(True)
        self.description_text.setPlaceholderText("Select a tutorial to see its description...")
        layout.addWidget(self.description_text)

        # Buttons with better spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.addStretch()  # Push buttons to the right

        start_button = QPushButton("Start Tutorial")
        start_button.clicked.connect(self._start_selected_tutorial)
        start_button.setDefault(True)  # Make it the default button
        start_button.setMinimumSize(140, 40)
        button_layout.addWidget(start_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumSize(100, 40)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Connect selection change
        self.tutorial_list.currentItemChanged.connect(self._on_tutorial_selection_changed)

    def _load_tutorials(self):
        """Load available tutorials."""
        # Basic Workflow Tutorial
        basic_tutorial = {
            "id": "basic_workflow",
            "title": "Basic Workflow Creation",
            "description": "Learn how to create a Moveworks-compliant workflow with compound action naming and steps.",
            "difficulty": "Beginner",
            "estimated_time": "7 minutes",
            "steps": [
                TutorialStep(
                    title="Welcome to the Enhanced Tutorial",
                    description="This tutorial will guide you through creating your first Moveworks-compliant workflow. We'll start with setting a compound action name, then add steps. Click 'Next' to continue.",
                    auto_advance=False
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="First, set a name for your compound action. This identifies your entire workflow in Moveworks. Replace 'compound_action' with 'user_lookup_workflow' in the Compound Action Name field.",
                    target_element="compound_action_name_field",
                    action="focus"
                ),
                TutorialStep(
                    title="Understanding Compound Actions",
                    description="The compound action name becomes the top-level 'action_name' field in your YAML. This is required for Moveworks compliance. Notice how the YAML preview updates automatically.",
                    target_element="yaml_preview_panel",
                    auto_advance=False
                ),
                TutorialStep(
                    title="Add Your First Action Step",
                    description="Now click the 'Add Action Step' button to add your first action to the workflow.",
                    target_element="add_action_button",
                    action="click"
                ),
                TutorialStep(
                    title="Configure the Action",
                    description="Enter 'mw.get_user_by_email' as the action name and 'user_info' as the output key.",
                    target_element="action_name_field"
                ),
                TutorialStep(
                    title="Add Input Arguments",
                    description="Add an input argument with key 'email' and value 'data.input_email'.",
                    target_element="input_args_table"
                ),
                TutorialStep(
                    title="Provide JSON Output",
                    description="Add example JSON output to enable data mapping between steps.",
                    target_element="json_output_field"
                ),
                TutorialStep(
                    title="Review Your Moveworks-Compliant YAML",
                    description="Look at the YAML preview panel. Notice the compound action structure with 'action_name' at the top level and your steps wrapped in a 'steps' array. This format is required for Moveworks compliance.",
                    target_element="yaml_preview_panel",
                    auto_advance=False
                ),
                TutorialStep(
                    title="Tutorial Complete!",
                    description="Congratulations! You've created your first Moveworks-compliant workflow with proper compound action structure. The YAML is ready for use in Moveworks. Continue exploring to learn more features.",
                    auto_advance=False
                )
            ]
        }

        # Control Flow Tutorial
        control_flow_tutorial = {
            "id": "control_flow",
            "title": "Control Flow and Conditions",
            "description": "Learn how to use switch statements, loops, and conditional logic in workflows.",
            "difficulty": "Intermediate",
            "estimated_time": "8 minutes",
            "steps": [
                TutorialStep(
                    title="Control Flow Introduction",
                    description="This tutorial covers advanced workflow features like switch statements and loops.",
                    auto_advance=False
                ),
                TutorialStep(
                    title="Add a Switch Step",
                    description="Use switch steps to create conditional branching in your workflow.",
                    target_element="add_switch_button"
                ),
                TutorialStep(
                    title="Configure Switch Conditions",
                    description="Add conditions that evaluate data from previous steps.",
                    target_element="switch_config_panel"
                ),
                TutorialStep(
                    title="Add Nested Steps",
                    description="Add steps that execute when conditions are met.",
                    target_element="nested_steps_area"
                ),
                TutorialStep(
                    title="Control Flow Complete!",
                    description="You now know how to create complex conditional workflows!",
                    auto_advance=False
                )
            ]
        }

        # Comprehensive Tutorial Series (Module-based)
        module_1_tutorial = {
            "id": "module_1_basic_compound_action",
            "title": "Module 1: Your First Compound Action",
            "description": "Learn to create basic compound actions with lookup and notification",
            "difficulty": "Beginner",
            "estimated_time": "15 minutes",
            "steps": [
                TutorialStep(
                    title="Welcome to Compound Actions",
                    description="Welcome! This tutorial teaches you to create Moveworks compound actions. We'll build an employee onboarding notification system that demonstrates data lookup and notification patterns. Click 'Next' to begin.",
                    auto_advance=False
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="In the 'Compound Action Name' field at the top, enter 'employee_welcome_notification'. This becomes the top-level action_name in your YAML.",
                    target_element="compound_action_name_field"
                ),
                TutorialStep(
                    title="Add First Action Step",
                    description="Click 'Add Action Step' to create your first workflow step. This will look up user information by email.",
                    target_element="add_action_button"
                ),
                TutorialStep(
                    title="Configure User Lookup Action",
                    description="Set Action Name: 'mw.get_user_by_email', Output Key: 'user_info'. In Input Args, add key 'email' with value 'data.input_email'.",
                    target_element="action_config_panel"
                ),
                TutorialStep(
                    title="Add Sample JSON Output",
                    description="In the 'User Provided JSON Output' field, add sample user data. This enables the JSON Path Selector for subsequent steps.",
                    target_element="json_output_field"
                ),
                TutorialStep(
                    title="Open JSON Path Selector",
                    description="Click the 'JSON Explorer' tab to open the data explorer. Select 'Step 1: user_info' to see available data paths like data.user_info.user.manager.email.",
                    target_element="json_path_selector_button"
                ),
                TutorialStep(
                    title="Add Notification Action",
                    description="Add another Action Step with Action Name: 'mw.send_notification', Output Key: 'notification_result'. Use the JSON Path Selector to set recipient to manager's email.",
                    target_element="add_action_button"
                ),
                TutorialStep(
                    title="Validate Compliance",
                    description="Click 'Validate' to ensure your workflow meets all Moveworks requirements. Look for green validation status and proper DSL string quoting.",
                    target_element="validate_button"
                ),
                TutorialStep(
                    title="Review Generated YAML",
                    description="Check the YAML Preview panel. Notice the mandatory compound action structure with action_name at top level and steps array containing your workflow logic.",
                    target_element="yaml_preview_panel"
                ),
                TutorialStep(
                    title="Module 1 Complete!",
                    description="Congratulations! You've created your first Moveworks compound action with proper data flow and validation. Ready for Module 2: IT Automation?",
                    auto_advance=False
                )
            ]
        }

        module_2_tutorial = {
            "id": "module_2_it_automation",
            "title": "Module 2: IT Automation",
            "description": "ServiceNow/Jira ticket creation with HTTP requests and parameterization",
            "difficulty": "Intermediate",
            "estimated_time": "20 minutes",
            "steps": [
                TutorialStep(
                    title="Welcome to IT Automation",
                    description="Welcome to Module 2! We'll build an automated incident response system that creates tickets in both ServiceNow and Jira when critical alerts are triggered. This demonstrates enterprise IT automation with multiple system integration.",
                    auto_advance=False
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Set the compound action name to 'critical_alert_incident_response'. This workflow will handle critical system alerts automatically.",
                    target_element="compound_action_name_field"
                ),
                TutorialStep(
                    title="Add ServiceNow HTTP Request",
                    description="Click 'Add Action Step' to create an HTTP request for ServiceNow incident creation. We'll configure this as an API call.",
                    target_element="add_action_button"
                ),
                TutorialStep(
                    title="Configure ServiceNow Action",
                    description="Configure the ServiceNow action with parameterized values: Action Name: 'http_request', Output Key: 'servicenow_incident'. Use {{{SERVICENOW_TOKEN}}} for authentication and {{{ALERT_TITLE}}} for dynamic content.",
                    target_element="action_config_panel"
                ),
                TutorialStep(
                    title="Add Sample ServiceNow Response",
                    description="Add sample JSON output showing a ServiceNow incident response. This enables the JSON Path Selector for linking to subsequent steps.",
                    target_element="json_output_field"
                ),
                TutorialStep(
                    title="Use Template Library for Jira",
                    description="Click 'Templates' → 'IT Automation' → 'Jira Issue Creation' to add a pre-configured Jira integration step. Templates provide tested patterns for common scenarios.",
                    target_element="template_library_button"
                ),
                TutorialStep(
                    title="Link ServiceNow and Jira Data",
                    description="Use the JSON Path Selector to reference ServiceNow data in the Jira step. Set the Jira description to include 'data.servicenow_incident.result.number' for cross-system tracking.",
                    target_element="json_path_selector_button"
                ),
                TutorialStep(
                    title="Add Notification Step",
                    description="Add a final Slack notification step that includes both ServiceNow and Jira references. Use template formatting for consistent messaging across your organization.",
                    target_element="add_action_button"
                ),
                TutorialStep(
                    title="Validate Multi-System Workflow",
                    description="Run validation to check parameterization, data references, and API configurations. Look for proper {{{VARIABLE}}} usage and correct data.* references.",
                    target_element="validate_button"
                ),
                TutorialStep(
                    title="Module 2 Complete!",
                    description="Excellent! You've built an enterprise-grade IT automation workflow with multi-system integration, parameterization, and proper error handling. Ready for Module 3: Conditional Logic?",
                    auto_advance=False
                )
            ]
        }

        self.tutorials = {
            "basic_workflow": basic_tutorial,
            "control_flow": control_flow_tutorial,
            "module_1_basic_compound_action": module_1_tutorial,
            "module_2_it_automation": module_2_tutorial
        }

        # Populate tutorial list
        for tutorial_id, tutorial in self.tutorials.items():
            item = QListWidgetItem(f"{tutorial['title']} ({tutorial['difficulty']})")
            item.setData(Qt.UserRole, tutorial_id)
            self.tutorial_list.addItem(item)

    def _on_tutorial_selection_changed(self, current, previous):
        """Handle tutorial selection change."""
        if current:
            tutorial_id = current.data(Qt.UserRole)
            tutorial = self.tutorials.get(tutorial_id)
            if tutorial:
                description = f"""
                <b>{tutorial['title']}</b><br>
                <b>Difficulty:</b> {tutorial['difficulty']}<br>
                <b>Estimated Time:</b> {tutorial['estimated_time']}<br><br>
                {tutorial['description']}
                """
                self.description_text.setHtml(description)

    def _start_selected_tutorial(self):
        """Start the selected tutorial."""
        current_item = self.tutorial_list.currentItem()
        if current_item:
            tutorial_id = current_item.data(Qt.UserRole)
            self.tutorial_selected.emit(tutorial_id)
            self.accept()


class TutorialManager:
    """Manages tutorial execution and state."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_tutorial = None
        self.current_step_index = 0
        self.overlay = None
        self.tutorials = {}

        # Load tutorials from dialog
        dialog = TutorialDialog()
        self.tutorials = dialog.tutorials

    def start_tutorial(self, tutorial_id: str):
        """Start a specific tutorial."""
        if tutorial_id not in self.tutorials:
            return False

        self.current_tutorial = self.tutorials[tutorial_id]
        self.current_step_index = 0

        # Create overlay
        self.overlay = TutorialOverlay(self.main_window)
        self.overlay.step_completed.connect(self._next_step)
        self.overlay.tutorial_cancelled.connect(self._cancel_tutorial)

        # Start first step
        self._show_current_step()
        return True

    def _show_current_step(self):
        """Show the current tutorial step."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial["steps"]):
            self._complete_tutorial()
            return

        step = self.current_tutorial["steps"][self.current_step_index]
        target_widget = self._find_target_widget(step.target_element)

        self.overlay.show_step(step, target_widget)

    def _find_target_widget(self, target_element: Optional[str]) -> Optional[QWidget]:
        """Find the target widget for highlighting."""
        if not target_element:
            return None

        # Map target element names to actual widgets
        widget_map = {
            "compound_action_name_field": getattr(self.main_window, 'action_name_edit', None),
            "yaml_preview_panel": getattr(self.main_window, 'yaml_panel', None),
            "add_action_button": getattr(self.main_window, 'add_action_btn', None),
            "add_script_button": getattr(self.main_window, 'add_script_btn', None),
            "add_switch_button": getattr(self.main_window, 'add_switch_btn', None),
            "add_try_catch_button": getattr(self.main_window, 'add_try_catch_btn', None),
            "action_config_panel": getattr(self.main_window, 'config_panel', None),
            "json_path_selector_button": getattr(self.main_window, 'enhanced_json_panel', None),
            "validate_button": getattr(self.main_window, 'validate_btn', None),
            "template_library_button": None,  # Will be found by object name
            "action_name_field": getattr(self.main_window.config_panel, 'action_name_edit', None),
            "input_args_table": getattr(self.main_window.config_panel, 'input_args_table', None),
            "json_output_field": getattr(self.main_window.config_panel, 'json_output_edit', None),
        }

        # First try the widget map
        widget = widget_map.get(target_element)
        if widget:
            return widget

        # Fallback to finding by object name
        return self.main_window.findChild(QWidget, target_element)

    def _next_step(self):
        """Advance to the next tutorial step."""
        self.current_step_index += 1
        self._show_current_step()

    def _cancel_tutorial(self):
        """Cancel the current tutorial."""
        if self.overlay:
            self.overlay.hide()
            self.overlay = None
        self.current_tutorial = None
        self.current_step_index = 0

    def _complete_tutorial(self):
        """Complete the current tutorial."""
        if self.overlay:
            self.overlay.hide()
            self.overlay = None

        # Show completion message
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self.main_window,
            "Tutorial Complete",
            f"Congratulations! You've completed the '{self.current_tutorial['title']}' tutorial."
        )

        self.current_tutorial = None
        self.current_step_index = 0

    def show_tutorial_dialog(self):
        """Show the tutorial selection dialog."""
        dialog = TutorialDialog(self.main_window)
        dialog.tutorial_selected.connect(self.start_tutorial)
        dialog.exec()
