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
        
        # Beginner Tutorial: Your First Workflow
        first_workflow_tutorial = Tutorial(
            id="first_workflow",
            title="Your First Workflow",
            description="Learn to create a simple user lookup workflow step by step",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="10 minutes",
            learning_objectives=[
                "Create action and script steps",
                "Configure input arguments",
                "Provide JSON output examples",
                "Validate and export workflows"
            ],
            steps=[
                TutorialStep(
                    title="Welcome to Your First Workflow",
                    description="Introduction to workflow creation",
                    instruction="Welcome! This tutorial will guide you through creating your first Moveworks workflow. We'll build a simple user lookup workflow that demonstrates the core concepts.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add Your First Action Step",
                    description="Create an action step",
                    instruction="Click the 'Add Action Step' button in the left panel to create your first workflow step.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Configure the Action",
                    description="Set up action properties",
                    instruction="Now configure your action step:<br>1. Set Action Name to 'mw.get_user_by_email'<br>2. Set Output Key to 'user_info'<br>3. Add a description",
                    target_element="action_config_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add Input Arguments",
                    description="Configure action inputs",
                    instruction="Add an input argument:<br>1. Click 'Add Argument'<br>2. Set Key to 'email'<br>3. Set Value to 'data.input_email'",
                    target_element="input_args_section",
                    action_type="info"
                ),
                TutorialStep(
                    title="Provide JSON Output",
                    description="Add example output",
                    instruction="Scroll down to the JSON Output section and paste the example JSON that shows what this action will return. This enables data mapping in later steps.",
                    target_element="json_output_section",
                    action_type="info"
                ),
                TutorialStep(
                    title="Add a Script Step",
                    description="Create a processing step",
                    instruction="Now add a script step to process the user data. Click 'Add Script Step' in the left panel.",
                    target_element="add_script_button",
                    action_type="click"
                ),
                TutorialStep(
                    title="Write Script Code",
                    description="Add processing logic",
                    instruction="Write APIthon code to process the user data and create a welcome message. Remember to include a 'return' statement.",
                    target_element="script_code_editor",
                    action_type="info"
                ),
                TutorialStep(
                    title="Validate Your Workflow",
                    description="Check for errors",
                    instruction="Look at the validation panel on the right. It should show green if everything is configured correctly. Fix any red errors that appear.",
                    target_element="validation_panel",
                    action_type="info"
                ),
                TutorialStep(
                    title="Preview the YAML",
                    description="See the generated output",
                    instruction="Click the 'YAML Preview' tab to see the generated YAML. This is what will be deployed to Moveworks.",
                    target_element="yaml_preview_tab",
                    action_type="click"
                ),
                TutorialStep(
                    title="Congratulations!",
                    description="Tutorial complete",
                    instruction="You've successfully created your first Moveworks workflow! You can now export it as YAML or save the project for later editing.",
                    action_type="info"
                )
            ]
        )
        
        # Intermediate Tutorial: Expression Types
        expression_types_tutorial = Tutorial(
            id="expression_types",
            title="Master All Expression Types",
            description="Learn to use all 8 Moveworks expression types effectively",
            category=TutorialCategory.EXPRESSION_TYPES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="25 minutes",
            prerequisites=["first_workflow"],
            learning_objectives=[
                "Understand all 8 expression types",
                "Use control flow expressions",
                "Handle errors with try_catch",
                "Create parallel workflows"
            ],
            steps=[
                TutorialStep(
                    title="Expression Types Overview",
                    description="Introduction to expression types",
                    instruction="Moveworks supports 8 expression types: action, script, switch, for, parallel, return, raise, and try_catch. Each serves a specific purpose in workflow automation.",
                    action_type="info"
                ),
                TutorialStep(
                    title="Switch Expression",
                    description="Conditional branching",
                    instruction="Let's add a switch expression to handle different user types. This allows conditional logic in your workflow.",
                    target_element="add_switch_button",
                    action_type="click"
                ),
                # Additional steps would be added here...
            ]
        )
        
        # Advanced Tutorial: Enhanced Features
        enhanced_features_tutorial = Tutorial(
            id="enhanced_features",
            title="Enhanced Features Deep Dive",
            description="Master the advanced features like JSON Path Selector and Template Library",
            category=TutorialCategory.ENHANCED_FEATURES,
            difficulty=TutorialDifficulty.ADVANCED,
            estimated_time="30 minutes",
            prerequisites=["first_workflow", "expression_types"],
            learning_objectives=[
                "Use the JSON Path Selector effectively",
                "Leverage the Template Library",
                "Apply contextual examples",
                "Optimize with enhanced validation"
            ],
            steps=[
                TutorialStep(
                    title="JSON Path Selector",
                    description="Visual data selection",
                    instruction="The JSON Path Selector lets you visually browse and select data from previous steps. Let's explore this powerful feature.",
                    target_element="json_path_selector",
                    action_type="info"
                ),
                # Additional steps would be added here...
            ]
        )
        
        # Store tutorials
        self.tutorials = {
            "first_workflow": first_workflow_tutorial,
            "expression_types": expression_types_tutorial,
            "enhanced_features": enhanced_features_tutorial
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
