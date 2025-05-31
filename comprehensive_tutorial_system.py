"""
Comprehensive Tutorial System for the Enhanced Moveworks YAML Assistant.

This module provides interactive tutorials that guide users through all features
of the application with step-by-step instructions, visual highlights, and
progress tracking.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QTextEdit, QListWidget, QListWidgetItem, QWidget, QFrame, QScrollArea,
    QGroupBox, QTabWidget, QCheckBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QFont, QPalette, QPainter, QColor, QPixmap, QIcon


class TutorialDifficulty(Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class TutorialCategory(Enum):
    """Tutorial categories."""
    GETTING_STARTED = "Getting Started"
    EXPRESSION_TYPES = "Expression Types"
    ENHANCED_FEATURES = "Enhanced Features"
    DATA_HANDLING = "Data Handling"
    BEST_PRACTICES = "Best Practices"
    ADVANCED_WORKFLOWS = "Advanced Workflows"


@dataclass
class TutorialStep:
    """Represents a single step in a tutorial."""
    title: str
    description: str
    instruction: str
    target_element: Optional[str] = None  # Widget name or CSS selector
    action_type: str = "info"  # info, click, type, wait, validate
    action_data: Dict[str, Any] = field(default_factory=dict)
    validation_function: Optional[Callable] = None
    auto_advance: bool = False
    delay_ms: int = 1000
    highlight_color: str = "#3498db"
    screenshot_path: Optional[str] = None
    video_url: Optional[str] = None


@dataclass
class Tutorial:
    """Represents a complete tutorial."""
    id: str
    title: str
    description: str
    category: TutorialCategory
    difficulty: TutorialDifficulty
    estimated_time: str
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    steps: List[TutorialStep] = field(default_factory=list)
    completion_reward: str = ""
    tags: List[str] = field(default_factory=list)


class TutorialHighlight(QWidget):
    """Visual highlight overlay for tutorial targets."""
    
    def __init__(self, target_widget: QWidget, color: str = "#3498db"):
        super().__init__(target_widget.parent())
        self.target_widget = target_widget
        self.highlight_color = QColor(color)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Animation for pulsing effect
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self._update_geometry()
        self.show()
        self._start_pulse_animation()
    
    def _update_geometry(self):
        """Update highlight geometry to match target."""
        if self.target_widget:
            target_rect = self.target_widget.geometry()
            # Add padding around target
            padding = 10
            highlight_rect = QRect(
                target_rect.x() - padding,
                target_rect.y() - padding,
                target_rect.width() + 2 * padding,
                target_rect.height() + 2 * padding
            )
            self.setGeometry(highlight_rect)
    
    def _start_pulse_animation(self):
        """Start pulsing animation."""
        original_rect = self.geometry()
        expanded_rect = QRect(
            original_rect.x() - 5,
            original_rect.y() - 5,
            original_rect.width() + 10,
            original_rect.height() + 10
        )
        
        self.animation.setStartValue(original_rect)
        self.animation.setEndValue(expanded_rect)
        self.animation.finished.connect(self._reverse_animation)
        self.animation.start()
    
    def _reverse_animation(self):
        """Reverse the animation for continuous pulsing."""
        start_value = self.animation.endValue()
        end_value = self.animation.startValue()
        self.animation.setStartValue(start_value)
        self.animation.setEndValue(end_value)
        self.animation.finished.disconnect()
        self.animation.finished.connect(self._start_pulse_animation)
        self.animation.start()
    
    def paintEvent(self, event):
        """Paint the highlight overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw highlight border
        pen_color = QColor(self.highlight_color)
        pen_color.setAlpha(200)
        painter.setPen(pen_color)
        
        # Draw fill
        fill_color = QColor(self.highlight_color)
        fill_color.setAlpha(50)
        painter.setBrush(fill_color)
        
        painter.drawRoundedRect(self.rect(), 8, 8)


class TutorialStepDialog(QDialog):
    """Dialog for displaying tutorial step instructions."""
    
    next_step = Signal()
    previous_step = Signal()
    skip_tutorial = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutorial")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Progress
        self.progress_label = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        # Content
        self.instruction_text = QTextEdit()
        self.instruction_text.setReadOnly(True)
        self.instruction_text.setMaximumHeight(150)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.skip_btn = QPushButton("Skip Tutorial")
        self.previous_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        
        self.skip_btn.setStyleSheet("color: #e74c3c;")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        controls_layout.addWidget(self.skip_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.previous_btn)
        controls_layout.addWidget(self.next_btn)
        
        # Layout assembly
        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.instruction_text)
        layout.addLayout(controls_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.next_btn.clicked.connect(self.next_step.emit)
        self.previous_btn.clicked.connect(self.previous_step.emit)
        self.skip_btn.clicked.connect(self.skip_tutorial.emit)
    
    def update_step(self, step: TutorialStep, step_number: int, total_steps: int):
        """Update dialog for current step."""
        self.title_label.setText(step.title)
        self.progress_label.setText(f"Step {step_number} of {total_steps}")
        self.progress_bar.setValue(int((step_number / total_steps) * 100))
        self.instruction_text.setHtml(f"<p>{step.instruction}</p>")
        
        # Update button states
        self.previous_btn.setEnabled(step_number > 1)
        
        if step_number == total_steps:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next")


class ComprehensiveTutorialSystem:
    """
    Enhanced tutorial system with comprehensive coverage of all features.
    
    Features:
    - Interactive step-by-step tutorials
    - Visual highlights and overlays
    - Progress tracking
    - Adaptive difficulty
    - Integration with help system
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.tutorials: Dict[str, Tutorial] = {}
        self.current_tutorial: Optional[Tutorial] = None
        self.current_step_index: int = 0
        self.step_dialog: Optional[TutorialStepDialog] = None
        self.highlight_overlay: Optional[TutorialHighlight] = None
        
        self._initialize_tutorials()
    
    def _initialize_tutorials(self):
        """Initialize all available tutorials."""
        
        # Module 1: Your First Compound Action - Simple Lookup and Notification
        module_1_tutorial = Tutorial(
            id="module_1_basic_compound_action",
            title="Module 1: Your First Compound Action",
            description="Learn to create basic compound actions with lookup and notification",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="15 minutes",
            learning_objectives=[
                "Understand basic compound action structure and YAML compliance",
                "Create your first action step with proper data flow",
                "Use the JSON Path Selector for basic data selection",
                "Generate compliant YAML with mandatory action_name and steps fields",
                "Validate workflow using the built-in compliance system"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Compound Actions",
                    description="Introduction to Moveworks compound actions",
                    instruction="Welcome! This tutorial teaches you to create Moveworks compound actions. We'll build an employee onboarding notification system that demonstrates data lookup and notification patterns. Click 'Next' to begin.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Every compound action needs a unique name",
                    instruction="In the 'Compound Action Name' field at the top, enter 'employee_welcome_notification'. This becomes the top-level action_name in your YAML.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "employee_welcome_notification"}
                ),
                TutorialStep(
                    title="Add First Action Step",
                    description="Create user lookup action",
                    instruction="Click 'Add Step' → 'Action Step' to create your first workflow step. This will look up user information by email.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure User Lookup Action",
                    description="Set up the user lookup",
                    instruction="Set Action Name: 'mw.get_user_by_email', Output Key: 'user_info'. In Input Args, add key 'email' with value 'data.input_email'.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "action_name": "mw.get_user_by_email",
                        "output_key": "user_info",
                        "input_args": {"email": "data.input_email"}
                    }
                ),
                TutorialStep(
                    title="Add Sample JSON Output",
                    description="Provide sample response data",
                    instruction="In the 'User Provided JSON Output' field, add sample user data. This enables the JSON Path Selector for subsequent steps.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    action_data={
                        "text": '{"user": {"id": "emp_12345", "name": "John Doe", "email": "john.doe@company.com", "department": "Engineering", "manager": {"id": "mgr_67890", "name": "Jane Smith", "email": "jane.smith@company.com"}, "active": true}}'
                    }
                ),
                TutorialStep(
                    title="Open JSON Path Selector",
                    description="Explore available data paths",
                    instruction="Click 'Tools' → 'JSON Path Selector' to open the data explorer. Select 'Step 1: user_info' to see available data paths like data.user_info.user.manager.email.",
                    target_element="json_path_selector_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Notification Action",
                    description="Create manager notification",
                    instruction="Add another Action Step with Action Name: 'mw.send_notification', Output Key: 'notification_result'. Use the JSON Path Selector to set recipient to manager's email.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure Notification Details",
                    description="Set up the notification",
                    instruction="In Input Args, add 'recipient': 'data.user_info.user.manager.email' and 'message': 'Welcome to the team! Please reach out to help onboard our new team member.'",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "action_name": "mw.send_notification",
                        "output_key": "notification_result",
                        "input_args": {
                            "recipient": "data.user_info.user.manager.email",
                            "message": "Welcome to the team! Please reach out to help onboard our new team member."
                        }
                    }
                ),
                TutorialStep(
                    title="Validate Compliance",
                    description="Check Moveworks compliance",
                    instruction="Click 'Validate' to ensure your workflow meets all Moveworks requirements. Look for green validation status and proper DSL string quoting.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Review Generated YAML",
                    description="Examine the complete workflow",
                    instruction="Check the YAML Preview panel. Notice the mandatory compound action structure with action_name at top level and steps array containing your workflow logic.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Module 1 Complete!",
                    description="First compound action created",
                    instruction="Congratulations! You've created your first Moveworks compound action with proper data flow and validation. Ready for Module 2: IT Automation?",
                    action_type="info"
                )
            ]
        )
        
        # Module 2: IT Automation - ServiceNow/Jira Ticket Creation
        module_2_tutorial = Tutorial(
            id="module_2_it_automation",
            title="Module 2: IT Automation",
            description="ServiceNow/Jira ticket creation with HTTP requests and parameterization",
            category=TutorialCategory.EXPRESSION_TYPES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="20 minutes",
            prerequisites=["module_1_basic_compound_action"],
            learning_objectives=[
                "Create HTTP request action steps for API integration",
                "Use parameterization with {{{VARIABLES}}} for dynamic values",
                "Leverage the template library for common IT automation patterns",
                "Configure delay settings and progress updates for user experience",
                "Handle complex input arguments with nested data structures"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to IT Automation",
                    description="Introduction to enterprise IT automation",
                    instruction="Welcome to Module 2! We'll build an automated incident response system that creates tickets in both ServiceNow and Jira when critical alerts are triggered. This demonstrates enterprise IT automation with multiple system integration.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Name your IT automation workflow",
                    instruction="Set the compound action name to 'critical_alert_incident_response'. This workflow will handle critical system alerts automatically.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "critical_alert_incident_response"}
                ),
                TutorialStep(
                    title="Add ServiceNow HTTP Request",
                    description="Create ServiceNow API action step",
                    instruction="Click 'Add Step' → 'Action Step' to create an HTTP request for ServiceNow incident creation. We'll configure this as an API call.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure ServiceNow Action",
                    description="Set up ServiceNow incident creation",
                    instruction="Configure the ServiceNow action with parameterized values: Action Name: 'http_request', Output Key: 'servicenow_incident'. Use {{{SERVICENOW_TOKEN}}} for authentication and {{{ALERT_TITLE}}} for dynamic content.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "action_name": "http_request",
                        "output_key": "servicenow_incident",
                        "parameterization": True
                    }
                ),
                TutorialStep(
                    title="Add Progress Updates",
                    description="Enhance user experience",
                    instruction="In the action configuration, add progress updates: On Pending: 'Creating ServiceNow incident...', On Complete: 'ServiceNow incident created successfully'. Also set delay_seconds to 5.",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add Sample ServiceNow Response",
                    description="Enable data path selection",
                    instruction="Add sample JSON output showing a ServiceNow incident response. This enables the JSON Path Selector for linking to subsequent steps.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    action_data={
                        "text": '{"result": {"sys_id": "abc123def456", "number": "INC0012345", "short_description": "Critical Database Connection Failure", "state": "1", "urgency": "1", "priority": "1"}}'
                    }
                ),
                TutorialStep(
                    title="Use Template Library for Jira",
                    description="Leverage pre-built patterns",
                    instruction="Click 'Templates' → 'IT Automation' → 'Jira Issue Creation' to add a pre-configured Jira integration step. Templates provide tested patterns for common scenarios.",
                    target_element="template_library_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Link ServiceNow and Jira Data",
                    description="Cross-system data integration",
                    instruction="Use the JSON Path Selector to reference ServiceNow data in the Jira step. Set the Jira description to include 'data.servicenow_incident.result.number' for cross-system tracking.",
                    target_element="json_path_selector_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Notification Step",
                    description="Complete the automation chain",
                    instruction="Add a final Slack notification step that includes both ServiceNow and Jira references. Use template formatting for consistent messaging across your organization.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Validate Multi-System Workflow",
                    description="Ensure enterprise compliance",
                    instruction="Run validation to check parameterization, data references, and API configurations. Look for proper {{{VARIABLE}}} usage and correct data.* references.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Module 2 Complete!",
                    description="IT automation mastered",
                    instruction="Excellent! You've built an enterprise-grade IT automation workflow with multi-system integration, parameterization, and proper error handling. Ready for Module 3: Conditional Logic?",
                    action_type="info"
                )
            ]
        )
        
        # Module 3: Conditional Logic - Approval Routing with Switch Statements
        module_3_tutorial = Tutorial(
            id="module_3_conditional_logic",
            title="Module 3: Conditional Logic",
            description="Approval routing with switch statements and complex business logic",
            category=TutorialCategory.EXPRESSION_TYPES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="18 minutes",
            prerequisites=["module_2_it_automation"],
            learning_objectives=[
                "Create switch expressions for conditional workflow branching",
                "Use conditional data mapping with complex business logic",
                "Implement SwitchStep class with multiple cases and default handling",
                "Handle nested conditional flows and data validation",
                "Integrate switch logic with the compliance validation system"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Conditional Logic",
                    description="Introduction to switch expressions",
                    instruction="Welcome to Module 3! We'll build an expense approval routing system that automatically routes expenses based on amount and employee level. This demonstrates complex conditional logic with multiple decision points.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Name your conditional workflow",
                    instruction="Set the compound action name to 'expense_approval_routing'. This workflow will route expense approvals based on business rules.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "expense_approval_routing"}
                ),
                TutorialStep(
                    title="Add Switch Expression",
                    description="Create conditional branching",
                    instruction="Click 'Add Switch Step' to create a conditional expression. This will route expenses based on amount and employee level.",
                    target_element="add_switch_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure Switch Condition",
                    description="Set up the switch logic",
                    instruction="Set the switch expression to evaluate 'data.expense_amount'. This will determine which approval path to take based on the expense amount.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "switch_expression": "data.expense_amount",
                        "cases": ["< 100", "< 1000", ">= 1000"]
                    }
                ),
                TutorialStep(
                    title="Add Case for Small Expenses",
                    description="Handle expenses under $100",
                    instruction="Add a case for expenses under $100 that auto-approves. Set condition: 'data.expense_amount < 100' and action: 'mw.auto_approve'.",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add Case for Medium Expenses",
                    description="Handle expenses $100-$1000",
                    instruction="Add a case for medium expenses requiring manager approval. Set condition: 'data.expense_amount < 1000' and route to manager.",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add Default Case",
                    description="Handle large expenses",
                    instruction="Add a default case for expenses over $1000 requiring executive approval. This ensures all expense amounts are handled.",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Test Switch Logic",
                    description="Validate conditional flow",
                    instruction="Use the validation system to test your switch logic with different expense amounts. Ensure all cases are properly handled.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Review Conditional YAML",
                    description="Examine switch structure",
                    instruction="Check the YAML Preview to see how switch expressions are structured. Notice the cases array and default handling.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Module 3 Complete!",
                    description="Conditional logic mastered",
                    instruction="Excellent! You've mastered conditional logic with switch expressions. Ready for Module 4: Data Processing?",
                    action_type="info"
                )
            ]
        )

        # Module 4: Data Processing - List Handling with Script Steps
        module_4_tutorial = Tutorial(
            id="module_4_data_processing",
            title="Module 4: Data Processing",
            description="List handling and data transformations with APIthon scripts",
            category=TutorialCategory.DATA_HANDLING,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="22 minutes",
            prerequisites=["module_3_conditional_logic"],
            learning_objectives=[
                "Create APIthon scripts for data processing and transformations",
                "Handle list operations and data aggregation efficiently",
                "Implement proper return value logic with educational guidance",
                "Use literal block scalar YAML formatting for complex scripts",
                "Validate script compliance with 4096-byte limits and restrictions"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Data Processing",
                    description="Introduction to APIthon scripts",
                    instruction="Welcome to Module 4! We'll build an employee performance report generator that processes lists of employee data and creates summary reports. This demonstrates advanced data processing with APIthon scripts.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Name your data processing workflow",
                    instruction="Set the compound action name to 'employee_performance_report'. This workflow will process employee data and generate reports.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "employee_performance_report"}
                ),
                TutorialStep(
                    title="Add Script Step",
                    description="Create data processing script",
                    instruction="Click 'Add Script Step' to create an APIthon script for data processing. Scripts allow complex data transformations.",
                    target_element="add_script_btn",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure Script Details",
                    description="Set up the script step",
                    instruction="Set Script Name: 'process_employee_data', Output Key: 'processed_results'. This script will handle list processing and aggregation.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "script_name": "process_employee_data",
                        "output_key": "processed_results"
                    }
                ),
                TutorialStep(
                    title="Write Data Processing Script",
                    description="Implement list processing logic",
                    instruction="Add the APIthon script for processing employee performance data. Use list comprehensions and aggregation functions.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    action_data={
                        "text": """# Process employee performance data
employees = data.employee_list
high_performers = [emp for emp in employees if emp.get('score', 0) >= 85]
avg_score = sum(emp.get('score', 0) for emp in employees) / len(employees)

# Generate summary report
report = {
    'total_employees': len(employees),
    'high_performers': len(high_performers),
    'average_score': round(avg_score, 2),
    'top_performer': max(employees, key=lambda x: x.get('score', 0))
}

return report"""
                    }
                ),
                TutorialStep(
                    title="Validate Script Compliance",
                    description="Check APIthon restrictions",
                    instruction="Run validation to ensure your script meets APIthon requirements: no imports, under 4096 bytes, proper return logic.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Sample Input Data",
                    description="Provide test data",
                    instruction="Add sample employee data to test your script. This enables the JSON Path Selector for subsequent steps.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    action_data={
                        "text": '{"employee_list": [{"id": "emp1", "name": "Alice", "score": 92}, {"id": "emp2", "name": "Bob", "score": 78}, {"id": "emp3", "name": "Carol", "score": 88}]}'
                    }
                ),
                TutorialStep(
                    title="Add Report Generation Action",
                    description="Create final report",
                    instruction="Add an Action Step to generate the final report using the processed data. Reference script output with data.processed_results.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Review Data Flow",
                    description="Examine the complete workflow",
                    instruction="Check the YAML Preview to see how script steps integrate with action steps. Notice the literal block scalar formatting for the script.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Module 4 Complete!",
                    description="Data processing mastered",
                    instruction="Outstanding! You've mastered data processing with APIthon scripts and list operations. Ready for Module 5: Error Handling?",
                    action_type="info"
                )
            ]
        )

        # Module 5: Error Handling - Robust API Calls with Try-Catch
        module_5_tutorial = Tutorial(
            id="module_5_error_handling",
            title="Module 5: Error Handling",
            description="Robust workflows with try-catch expressions and error recovery",
            category=TutorialCategory.BEST_PRACTICES,
            difficulty=TutorialDifficulty.ADVANCED,
            estimated_time="25 minutes",
            prerequisites=["module_4_data_processing"],
            learning_objectives=[
                "Implement try-catch expressions for robust error handling",
                "Design error recovery strategies and fallback mechanisms",
                "Use TryCatchStep class with comprehensive error reporting",
                "Handle API failures gracefully with retry logic",
                "Create enterprise-grade workflows with proper error management"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Error Handling",
                    description="Introduction to robust workflows",
                    instruction="Welcome to Module 5! We'll build a multi-system data synchronization workflow with comprehensive error handling. This demonstrates enterprise-grade error recovery and resilience patterns.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Name your resilient workflow",
                    instruction="Set the compound action name to 'resilient_data_sync'. This workflow will handle errors gracefully across multiple systems.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "resilient_data_sync"}
                ),
                TutorialStep(
                    title="Add Try-Catch Expression",
                    description="Create error handling block",
                    instruction="Click 'Add Try/Catch Step' to create an error handling expression. This will wrap risky operations with error recovery.",
                    target_element="add_try_catch_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure Try Block",
                    description="Set up the main operation",
                    instruction="In the try block, add an API call that might fail. Set Action Name: 'http_request', URL: 'https://api.system1.com/sync'.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "action_name": "http_request",
                        "url": "https://api.system1.com/sync",
                        "output_key": "sync_result"
                    }
                ),
                TutorialStep(
                    title="Configure Catch Block",
                    description="Set up error recovery",
                    instruction="In the catch block, add a fallback action. Set Action Name: 'mw.log_error' and add notification to administrators.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "action_name": "mw.log_error",
                        "fallback_action": "mw.send_admin_notification"
                    }
                ),
                TutorialStep(
                    title="Add Retry Logic",
                    description="Implement retry mechanism",
                    instruction="Configure retry settings: max_retries: 3, retry_delay: 5. This provides resilience against temporary failures.",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add Finally Block",
                    description="Ensure cleanup operations",
                    instruction="Add a finally block to ensure cleanup operations always run, regardless of success or failure.",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Test Error Scenarios",
                    description="Validate error handling",
                    instruction="Use the validation system to test various error scenarios. Ensure your workflow handles all failure modes gracefully.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Monitoring and Alerts",
                    description="Complete the resilient workflow",
                    instruction="Add monitoring actions to track success/failure rates and alert administrators when error thresholds are exceeded.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Review Error Handling YAML",
                    description="Examine the complete structure",
                    instruction="Check the YAML Preview to see how try-catch expressions are structured. Notice the comprehensive error handling patterns.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Module 5 Complete!",
                    description="Error handling mastered",
                    instruction="Congratulations! You've completed all 5 modules and mastered Moveworks compound actions. You can now build enterprise-grade workflows with confidence!",
                    action_type="info"
                )
            ]
        )
        
        # Module 4: Data Processing - List Handling with Script Steps
        module_4_tutorial = Tutorial(
            id="module_4_data_processing",
            title="Module 4: Data Processing",
            description="List handling with script steps and APIthon validation",
            category=TutorialCategory.DATA_HANDLING,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="22 minutes",
            prerequisites=["module_3_conditional_logic"],
            learning_objectives=[
                "Create script expressions for complex data manipulation",
                "Handle list processing and array transformations",
                "Implement APIthon validation with 4096-byte limits",
                "Use return value validation and educational guidance",
                "Process complex data structures with proper error handling"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Data Processing",
                    description="Introduction to APIthon scripts",
                    instruction="Welcome to Module 4! We'll build an employee performance report generation system that processes lists of employee data, calculates statistics, and generates formatted reports. This demonstrates complex data processing with APIthon scripts.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Name your data processing workflow",
                    instruction="Set the compound action name to 'employee_performance_analysis'. This workflow will process employee performance data and generate analytics.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "employee_performance_analysis"}
                ),
                TutorialStep(
                    title="Add Data Retrieval Step",
                    description="Get employee performance data",
                    instruction="Add an action step with Action Name: 'mw.get_employee_performance_data', Output Key: 'employee_data'. This will retrieve the list of employees to process.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Sample Employee List",
                    description="Provide complex array data",
                    instruction="Add sample JSON with multiple employees and performance metrics. This demonstrates list processing capabilities.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    action_data={
                        "text": '{"employees": [{"id": "emp_001", "name": "Alice Johnson", "department": "Engineering", "performance_score": 92, "goals_completed": 8, "goals_total": 10}, {"id": "emp_002", "name": "Bob Smith", "department": "Engineering", "performance_score": 78, "goals_completed": 6, "goals_total": 10}, {"id": "emp_003", "name": "Carol Davis", "department": "Engineering", "performance_score": 95, "goals_completed": 10, "goals_total": 10}], "metadata": {"total_count": 3, "department": "Engineering", "report_period": "Q4 2024"}}'
                    }
                ),
                TutorialStep(
                    title="Add Performance Analysis Script",
                    description="Create data processing script",
                    instruction="Click 'Add Step' → 'Script Step' to add APIthon code. Set Output Key: 'performance_analysis'. We'll write code to calculate statistics and identify top performers.",
                    target_element="add_script_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Write APIthon Processing Code",
                    description="Implement list processing logic",
                    instruction="Write APIthon code using list comprehensions, aggregation functions, and data transformations. Remember the 4096-byte limit and include a return statement.",
                    target_element="action_config_panel",
                    action_type="info",
                    action_data={
                        "code_template": "employees = data.employee_data.employees\n# Calculate statistics\ntotal_score = sum([emp.performance_score for emp in employees])\navg_score = total_score / len(employees)\n# Find top performers\ntop_performers = [emp for emp in employees if emp.performance_score > avg_score]\nreturn {'average_score': avg_score, 'top_performers': top_performers}"
                    }
                ),
                TutorialStep(
                    title="Validate APIthon Compliance",
                    description="Check script requirements",
                    instruction="Use the validation panel to check your script. It verifies: 4096-byte limit, no imports/classes/private methods, proper return statement, and data structure compliance.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Report Formatting Script",
                    description="Create formatted output",
                    instruction="Add another script step to format the analysis results into a readable report. Set Output Key: 'formatted_report'.",
                    target_element="add_script_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Test List Processing",
                    description="Verify data transformations",
                    instruction="Review the YAML preview to see how script expressions are formatted with literal block scalars (|). Test your list comprehensions and aggregation logic.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Module 4 Complete!",
                    description="Data processing mastered",
                    instruction="Excellent! You've mastered APIthon scripts for complex data processing, list manipulation, and report generation. Ready for Module 5: Error Handling with try-catch?",
                    action_type="info"
                )
            ]
        )

        # Module 5: Error Handling - Robust API Calls with Try-Catch
        module_5_tutorial = Tutorial(
            id="module_5_error_handling",
            title="Module 5: Error Handling",
            description="Robust API calls with try-catch and comprehensive error recovery",
            category=TutorialCategory.BEST_PRACTICES,
            difficulty=TutorialDifficulty.ADVANCED,
            estimated_time="25 minutes",
            prerequisites=["module_4_data_processing"],
            learning_objectives=[
                "Create try_catch expressions for comprehensive error handling",
                "Handle API failures, network timeouts, and data validation errors",
                "Implement TryCatchStep class with proper error recovery patterns",
                "Use status code handling and fallback mechanisms",
                "Build resilient workflows that gracefully handle failures"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Error Handling",
                    description="Introduction to resilient workflows",
                    instruction="Welcome to Module 5! We'll build a multi-system data synchronization workflow that gracefully handles failures, implements retry logic, and provides comprehensive error reporting. This demonstrates enterprise-grade error handling.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Set Compound Action Name",
                    description="Name your resilient workflow",
                    instruction="Set the compound action name to 'resilient_employee_data_sync'. This workflow will synchronize data across multiple systems with comprehensive error handling.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    action_data={"text": "resilient_employee_data_sync"}
                ),
                TutorialStep(
                    title="Add Primary Sync with Try-Catch",
                    description="Create error-resilient operation",
                    instruction="Click 'Add Step' → 'Try-Catch Step' to add error handling. Set description: 'Attempt primary HR system synchronization', Output Key: 'primary_sync_result'.",
                    target_element="add_try_catch_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure Try Block",
                    description="Set up main operation",
                    instruction="In the try block, add an action step for HR system sync: Action Name: 'mw.sync_hr_system', Output Key: 'hr_sync_attempt'. Include timeout and retry parameters.",
                    target_element="try_block_config",
                    action_type="info",
                    action_data={
                        "action_name": "mw.sync_hr_system",
                        "output_key": "hr_sync_attempt",
                        "timeout_seconds": 30
                    }
                ),
                TutorialStep(
                    title="Configure Catch Block",
                    description="Set up error recovery",
                    instruction="In the catch block, add error logging and fallback data retrieval. This ensures the workflow continues even when the primary system fails.",
                    target_element="catch_block_config",
                    action_type="info",
                    action_data={
                        "error_logging": True,
                        "fallback_action": "mw.get_cached_employee_data"
                    }
                ),
                TutorialStep(
                    title="Configure Status Codes",
                    description="Define error triggers",
                    instruction="Set status codes that trigger the catch block: ['400', '401', '403', '404', '500', '502', '503', '504']. This covers authentication, authorization, and server errors.",
                    target_element="status_code_config",
                    action_type="info",
                    action_data={
                        "status_codes": ["400", "401", "403", "404", "500", "502", "503", "504"]
                    }
                ),
                TutorialStep(
                    title="Add Retry Logic",
                    description="Implement intelligent retries",
                    instruction="Add a second try-catch step for payroll system sync with retry logic. Include exponential backoff delays and maximum retry limits.",
                    target_element="add_try_catch_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Add Validation Script",
                    description="Generate comprehensive reports",
                    instruction="Add a script step to validate all sync operations and generate a detailed status report. Include success/failure counts and recommendations.",
                    target_element="add_script_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Test Error Scenarios",
                    description="Validate error handling",
                    instruction="Use the validation panel to test your error handling logic. Verify status code configurations, fallback mechanisms, and retry patterns.",
                    target_element="validate_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Review Error Handling YAML",
                    description="Understand try-catch structure",
                    instruction="Examine the YAML preview to see how try-catch expressions are structured with try_steps, catch_block, and on_status_code configurations.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Module 5 Complete!",
                    description="Error handling mastered",
                    instruction="Outstanding! You've mastered enterprise-grade error handling with comprehensive recovery strategies. You've completed all 5 modules of the Moveworks YAML Assistant tutorial series!",
                    action_type="info"
                )
            ]
        )

        # Store tutorials
        self.tutorials = {
            "module_1_basic_compound_action": module_1_tutorial,
            "module_2_it_automation": module_2_tutorial,
            "module_3_conditional_logic": module_3_tutorial,
            "module_4_data_processing": module_4_tutorial,
            "module_5_error_handling": module_5_tutorial
        }
    
    def get_available_tutorials(self) -> List[Tutorial]:
        """Get all available tutorials."""
        return list(self.tutorials.values())
    
    def get_tutorials_by_category(self, category: TutorialCategory) -> List[Tutorial]:
        """Get tutorials in a specific category."""
        return [t for t in self.tutorials.values() if t.category == category]
    
    def get_tutorials_by_difficulty(self, difficulty: TutorialDifficulty) -> List[Tutorial]:
        """Get tutorials of a specific difficulty."""
        return [t for t in self.tutorials.values() if t.difficulty == difficulty]
    
    def start_tutorial(self, tutorial_id: str) -> bool:
        """Start a specific tutorial."""
        if tutorial_id not in self.tutorials:
            return False
        
        self.current_tutorial = self.tutorials[tutorial_id]
        self.current_step_index = 0
        
        # Create step dialog
        self.step_dialog = TutorialStepDialog(self.main_window)
        self.step_dialog.next_step.connect(self._next_step)
        self.step_dialog.previous_step.connect(self._previous_step)
        self.step_dialog.skip_tutorial.connect(self._skip_tutorial)
        
        # Start first step
        self._show_current_step()
        return True
    
    def _show_current_step(self):
        """Display the current tutorial step."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial.steps):
            return
        
        step = self.current_tutorial.steps[self.current_step_index]
        
        # Update step dialog
        self.step_dialog.update_step(
            step,
            self.current_step_index + 1,
            len(self.current_tutorial.steps)
        )
        self.step_dialog.show()
        
        # Add highlight if target specified
        if step.target_element:
            self._highlight_target(step.target_element, step.highlight_color)
    
    def _highlight_target(self, target_element: str, color: str):
        """Highlight the target UI element."""
        # Remove existing highlight
        if self.highlight_overlay:
            self.highlight_overlay.close()
            self.highlight_overlay = None
        
        # Find target widget
        target_widget = self.main_window.findChild(QWidget, target_element)
        if target_widget:
            self.highlight_overlay = TutorialHighlight(target_widget, color)
    
    def _next_step(self):
        """Move to the next tutorial step."""
        if not self.current_tutorial:
            return
        
        self.current_step_index += 1
        
        if self.current_step_index >= len(self.current_tutorial.steps):
            self._complete_tutorial()
        else:
            self._show_current_step()
    
    def _previous_step(self):
        """Move to the previous tutorial step."""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._show_current_step()
    
    def _skip_tutorial(self):
        """Skip the current tutorial."""
        self._cleanup_tutorial()
    
    def _complete_tutorial(self):
        """Complete the current tutorial."""
        if self.current_tutorial:
            # Show completion message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self.main_window,
                "Tutorial Complete!",
                f"Congratulations! You've completed the '{self.current_tutorial.title}' tutorial.\n\n"
                f"You've learned: {', '.join(self.current_tutorial.learning_objectives)}"
            )
        
        self._cleanup_tutorial()
    
    def _cleanup_tutorial(self):
        """Clean up tutorial resources."""
        if self.step_dialog:
            self.step_dialog.close()
            self.step_dialog = None
        
        if self.highlight_overlay:
            self.highlight_overlay.close()
            self.highlight_overlay = None
        
        self.current_tutorial = None
        self.current_step_index = 0


# Global tutorial system instance
tutorial_system: Optional[ComprehensiveTutorialSystem] = None


def initialize_tutorial_system(main_window):
    """Initialize the global tutorial system."""
    global tutorial_system
    tutorial_system = ComprehensiveTutorialSystem(main_window)
    return tutorial_system
