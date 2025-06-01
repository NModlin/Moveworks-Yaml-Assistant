"""
Unified Tutorial System for Moveworks YAML Assistant.

This module combines the best features from all existing tutorial systems:
- Non-blocking interactive overlay (from integrated_tutorial_system.py)
- Comprehensive tutorial structure (from comprehensive_tutorial_system.py)  
- Clean selection dialog (from tutorial_system.py)
- Copy-paste functionality and real-time interaction
- Progressive 5-module curriculum with learning objectives
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QProgressBar, QFrame, QListWidget, QListWidgetItem, QDialog, QScrollArea,
    QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QClipboard

from tutorial_data import get_tutorial_json_data, get_tutorial_script_example


class TutorialCategory(Enum):
    """Tutorial categories for organization."""
    GETTING_STARTED = "Getting Started"
    EXPRESSION_TYPES = "Expression Types"
    DATA_HANDLING = "Data Handling"
    ADVANCED_FEATURES = "Advanced Features"
    BEST_PRACTICES = "Best Practices"


class TutorialDifficulty(Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


@dataclass
class UnifiedTutorialStep:
    """Enhanced tutorial step combining all best features."""
    title: str
    description: str
    instruction: str
    target_element: Optional[str] = None  # Widget name or CSS selector
    action_type: str = "info"  # info, click, type, copy_paste, highlight, wait, validate
    action_data: Dict[str, Any] = field(default_factory=dict)
    copy_paste_data: Optional[str] = None  # Data for copy-paste functionality
    expected_result: Optional[str] = None  # Expected outcome description
    validation_function: Optional[Callable] = None
    auto_advance: bool = False
    delay_ms: int = 1000
    highlight_color: str = "#3498db"
    sample_json: Optional[Dict[str, Any]] = None  # JSON examples for the step
    screenshot_path: Optional[str] = None
    video_url: Optional[str] = None


@dataclass
class UnifiedTutorial:
    """Complete tutorial with comprehensive metadata."""
    id: str
    title: str
    description: str
    category: TutorialCategory
    difficulty: TutorialDifficulty
    estimated_time: str
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    steps: List[UnifiedTutorialStep] = field(default_factory=list)
    completion_reward: str = ""
    tags: List[str] = field(default_factory=list)


class UnifiedTutorialOverlay(QWidget):
    """
    Non-blocking interactive tutorial overlay combining best features:
    - Visual highlighting with smooth animations
    - Copy-paste functionality with examples
    - Real-time UI interaction (non-blocking)
    - Progress tracking and navigation
    - Rich content display with JSON examples
    """

    step_completed = Signal()
    tutorial_cancelled = Signal()
    next_step_requested = Signal()
    previous_step_requested = Signal()
    copy_to_clipboard = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make overlay non-blocking for UI interaction
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        # Current step data
        self.current_step = None
        self.target_widget = None
        self.target_rect = QRect()
        self.step_number = 1
        self.total_steps = 1

        # Create separate floating panel for instructions (independent window)
        self.floating_panel = QWidget(None)  # No parent - truly independent
        self.floating_panel.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.floating_panel.setAttribute(Qt.WA_DeleteOnClose, False)
        
        self._setup_floating_panel()
        self._setup_animations()

    def _setup_floating_panel(self):
        """Setup the floating instruction panel."""
        self.floating_panel.setMinimumSize(400, 300)
        self.floating_panel.setMaximumSize(500, 600)
        self.floating_panel.resize(450, 400)
        
        # Main layout
        layout = QVBoxLayout(self.floating_panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header with progress
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 8, 8, 8)

        # Step indicator and progress bar
        self.step_indicator = QLabel("Step 1 of 1")
        self.step_indicator.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        self.step_indicator.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.3);
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: white;
                border-radius: 3px;
            }
        """)
        
        header_layout.addWidget(self.step_indicator)
        header_layout.addWidget(self.progress_bar)
        layout.addWidget(header_frame)

        # Content area with scroll
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(8)

        # Step title
        self.step_title = QLabel()
        self.step_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }
        """)
        self.step_title.setWordWrap(True)
        content_layout.addWidget(self.step_title)

        # Step description
        self.step_description = QTextEdit()
        self.step_description.setReadOnly(True)
        self.step_description.setMaximumHeight(80)
        self.step_description.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 8px;
                color: #2c3e50;
            }
        """)
        content_layout.addWidget(self.step_description)

        # Instruction text
        self.instruction_text = QTextEdit()
        self.instruction_text.setReadOnly(True)
        self.instruction_text.setMaximumHeight(100)
        self.instruction_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e9ecef;
                background-color: white;
                border-radius: 4px;
                padding: 8px;
                color: #495057;
            }
        """)
        content_layout.addWidget(self.instruction_text)

        # Copy-paste frame (hidden by default)
        self.copy_paste_frame = QFrame()
        self.copy_paste_frame.setVisible(False)
        self.copy_paste_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #28a745;
                border-radius: 6px;
                background-color: #f8fff9;
                padding: 8px;
            }
        """)
        copy_paste_layout = QVBoxLayout(self.copy_paste_frame)
        copy_paste_layout.setContentsMargins(8, 8, 8, 8)

        copy_label = QLabel("📋 Copy this example:")
        copy_label.setStyleSheet("color: #28a745; font-weight: bold; margin-bottom: 4px;")
        copy_paste_layout.addWidget(copy_label)

        self.copy_paste_text = QTextEdit()
        self.copy_paste_text.setReadOnly(True)
        self.copy_paste_text.setMaximumHeight(80)
        self.copy_paste_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #28a745;
                background-color: white;
                border-radius: 4px;
                padding: 6px;
                font-family: 'Courier New', monospace;
                color: #2c3e50;
            }
        """)
        copy_paste_layout.addWidget(self.copy_paste_text)

        self.copy_button = QPushButton("📋 Copy to Clipboard")
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        copy_paste_layout.addWidget(self.copy_button)

        content_layout.addWidget(self.copy_paste_frame)

        # Add stretch to push buttons to bottom
        content_layout.addStretch()

        content_scroll.setWidget(content_widget)
        layout.addWidget(content_scroll)

        # Navigation buttons
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(8, 8, 8, 8)

        # Previous button
        self.previous_btn = QPushButton("← Previous")
        self.previous_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """)
        self.previous_btn.clicked.connect(self.previous_step_requested.emit)
        button_layout.addWidget(self.previous_btn)

        # Skip tutorial button
        self.skip_btn = QPushButton("Skip Tutorial")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.skip_btn.clicked.connect(self.tutorial_cancelled.emit)
        button_layout.addWidget(self.skip_btn)

        button_layout.addStretch()

        # Next button
        self.next_btn = QPushButton("Next →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.next_btn.clicked.connect(self.next_step_requested.emit)
        button_layout.addWidget(self.next_btn)

        layout.addWidget(button_frame)

        # Make panel draggable
        self.floating_panel.mousePressEvent = self._start_drag
        self.floating_panel.mouseMoveEvent = self._drag_panel
        self.floating_panel.mouseReleaseEvent = self._end_drag
        self.drag_position = None

    def _setup_animations(self):
        """Setup animations for smooth transitions."""
        self.highlight_animation = QPropertyAnimation(self, b"geometry")
        self.highlight_animation.setDuration(500)
        self.highlight_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Pulse animation timer
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_highlight)
        self.pulse_timer.setInterval(1000)

    def show_step(self, step: UnifiedTutorialStep, target_widget: QWidget = None,
                  step_number: int = 1, total_steps: int = 1):
        """Show a tutorial step with highlighting and instructions."""
        self.current_step = step
        self.target_widget = target_widget
        self.step_number = step_number
        self.total_steps = total_steps

        # Update floating panel content
        self.step_indicator.setText(f"Step {step_number} of {total_steps}")
        self.progress_bar.setValue(int((step_number / total_steps) * 100))
        self.step_title.setText(step.title)
        self.step_description.setHtml(f"<p>{step.description}</p>")
        self.instruction_text.setHtml(f"<p>{step.instruction}</p>")

        # Update button states
        self.previous_btn.setEnabled(step_number > 1)
        if step_number == total_steps:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next →")

        # Show copy-paste data if available
        if step.copy_paste_data:
            self.copy_paste_frame.setVisible(True)
            self.copy_paste_text.setPlainText(step.copy_paste_data)
        else:
            self.copy_paste_frame.setVisible(False)

        # Position floating panel to avoid target widget
        self._position_floating_panel(target_widget)

        # Show overlay and panel
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.floating_panel.show()
        self.floating_panel.raise_()
        self.floating_panel.activateWindow()

        # Setup highlighting if target widget exists
        if target_widget:
            self._setup_highlighting(target_widget)
            self.pulse_timer.start()

    def _position_floating_panel(self, target_widget: QWidget = None):
        """Position floating panel to avoid covering target widget."""
        if not self.parent():
            return

        parent_rect = self.parent().rect()
        panel_size = self.floating_panel.size()

        # Default position (top-right)
        x = parent_rect.width() - panel_size.width() - 20
        y = 20

        # Adjust position if target widget would be covered
        if target_widget:
            target_global = target_widget.mapToGlobal(QPoint(0, 0))
            parent_global = self.parent().mapToGlobal(QPoint(0, 0))
            target_local = target_global - parent_global
            target_rect = QRect(target_local, target_widget.size())

            # Check if default position overlaps with target
            panel_rect = QRect(x, y, panel_size.width(), panel_size.height())
            if panel_rect.intersects(target_rect):
                # Try left side
                x = 20
                panel_rect = QRect(x, y, panel_size.width(), panel_size.height())
                if panel_rect.intersects(target_rect):
                    # Try bottom
                    x = parent_rect.width() - panel_size.width() - 20
                    y = parent_rect.height() - panel_size.height() - 20

        self.floating_panel.move(x, y)

    def _setup_highlighting(self, target_widget: QWidget):
        """Setup highlighting for target widget."""
        if not target_widget or not self.parent():
            return

        # Get target widget position relative to parent
        target_global = target_widget.mapToGlobal(QPoint(0, 0))
        parent_global = self.parent().mapToGlobal(QPoint(0, 0))
        target_local = target_global - parent_global

        self.target_rect = QRect(target_local, target_widget.size())
        self.update()  # Trigger repaint

    def _pulse_highlight(self):
        """Create pulsing highlight effect."""
        self.update()

    def paintEvent(self, event):
        """Paint the overlay with highlighting."""
        if not self.target_rect.isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Semi-transparent overlay
        overlay_color = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), overlay_color)

        # Clear the target area (make it visible)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self.target_rect, QColor(0, 0, 0, 0))

        # Draw highlight border
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        highlight_color = QColor(self.current_step.highlight_color if self.current_step else "#3498db")
        highlight_color.setAlpha(200)

        pen = QPen(highlight_color, 3)
        painter.setPen(pen)
        painter.setBrush(QBrush())
        painter.drawRect(self.target_rect)

    def _copy_to_clipboard(self):
        """Copy the example text to clipboard."""
        if self.current_step and self.current_step.copy_paste_data:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_step.copy_paste_data)

            # Provide visual feedback
            original_text = self.copy_button.text()
            self.copy_button.setText("✅ Copied!")
            QTimer.singleShot(1500, lambda: self.copy_button.setText(original_text))

    def _start_drag(self, event):
        """Start dragging the floating panel."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.floating_panel.frameGeometry().topLeft()

    def _drag_panel(self, event):
        """Drag the floating panel."""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.floating_panel.move(event.globalPosition().toPoint() - self.drag_position)

    def _end_drag(self, event):
        """End dragging the floating panel."""
        self.drag_position = None

    def hide(self):
        """Hide the overlay and floating panel."""
        super().hide()
        if self.floating_panel:
            self.floating_panel.hide()
        if self.pulse_timer:
            self.pulse_timer.stop()

    def closeEvent(self, event):
        """Handle close event."""
        if self.floating_panel:
            self.floating_panel.close()
        if self.pulse_timer:
            self.pulse_timer.stop()
        super().closeEvent(event)


class UnifiedTutorialSelectionDialog(QDialog):
    """Enhanced tutorial selection dialog combining best features."""

    tutorial_selected = Signal(str)  # Emits tutorial ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Moveworks YAML Assistant - Interactive Tutorials")
        self.setModal(True)
        self.setMinimumSize(900, 650)
        self.resize(1000, 750)

        self.tutorials = {}
        self._setup_ui()
        self._load_tutorials()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the tutorial selection UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_label = QLabel("🎓 Interactive Tutorial System")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        header_label.setAlignment(Qt.AlignCenter)

        # Subtitle
        subtitle_label = QLabel("Master Moveworks compound actions through progressive, hands-on tutorials")
        subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 16px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)

        layout.addWidget(header_label)
        layout.addWidget(subtitle_label)

        # Main content area
        content_layout = QHBoxLayout()

        # Left side - Tutorial list
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)

        list_label = QLabel("📚 Available Tutorials")
        list_label.setFont(QFont("Arial", 14, QFont.Bold))
        list_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        left_layout.addWidget(list_label)

        self.tutorial_list = QListWidget()
        self.tutorial_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f4;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        left_layout.addWidget(self.tutorial_list)

        # Right side - Tutorial details
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)

        details_label = QLabel("📋 Tutorial Details")
        details_label.setFont(QFont("Arial", 14, QFont.Bold))
        details_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        right_layout.addWidget(details_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
                padding: 12px;
                font-size: 13px;
                color: #495057;
            }
        """)
        right_layout.addWidget(self.details_text)

        # Set panel proportions
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 1)
        layout.addLayout(content_layout)

        # Bottom controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 16, 0, 0)

        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        help_btn.clicked.connect(self._show_help)
        controls_layout.addWidget(help_btn)

        controls_layout.addStretch()

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        # Start tutorial button
        self.start_button = QPushButton("🚀 Start Tutorial")
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """)

        controls_layout.addWidget(self.close_button)
        controls_layout.addWidget(self.start_button)
        layout.addLayout(controls_layout)

    def _connect_signals(self):
        """Connect UI signals."""
        self.tutorial_list.itemSelectionChanged.connect(self._on_tutorial_selected)
        self.start_button.clicked.connect(self._start_selected_tutorial)
        self.close_button.clicked.connect(self.close)

    def _load_tutorials(self):
        """Load available tutorials with comprehensive content."""
        # Module 1: Basic Compound Action
        module_1 = UnifiedTutorial(
            id="unified_module_1_basic",
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
                UnifiedTutorialStep(
                    title="Welcome to Compound Actions",
                    description="Welcome! This tutorial teaches you to create Moveworks compound actions.",
                    instruction="We'll build an employee onboarding notification system that demonstrates data lookup and notification patterns. Click 'Next' to begin.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Set Compound Action Name",
                    description="Every Moveworks workflow needs a unique compound action name.",
                    instruction="Click in the 'Compound Action Name' field and enter the name below. This identifies your workflow in the Moveworks system.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="employee_onboarding_notification"
                ),
                UnifiedTutorialStep(
                    title="Add Your First Action Step",
                    description="Action steps perform API calls or system operations.",
                    instruction="Click the '⚡ Add Action Step' button to create your first step. This will open the action configuration panel.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Action Name",
                    description="Each action step needs a unique name for data referencing.",
                    instruction="In the Action Name field, enter the name below. This will be used to reference the action's output data.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.get_user_by_email"
                ),
                UnifiedTutorialStep(
                    title="Set Output Key",
                    description="The output key defines how to reference this step's results.",
                    instruction="Enter the output key below. This creates a data reference 'data.user_info' for use in later steps.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="user_info"
                ),
                UnifiedTutorialStep(
                    title="Add Input Arguments",
                    description="Input arguments provide data to the action.",
                    instruction="Click 'Add Argument' and create an input parameter. Use 'email' as the key and 'data.input_email' as the value.",
                    target_element="add_input_arg_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Provide Sample JSON Output",
                    description="JSON output helps with data path selection in later steps.",
                    instruction="Paste the sample JSON below into the JSON Output field. This represents what the user lookup action will return.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data=get_tutorial_json_data("user_lookup"),
                    sample_json=get_tutorial_json_data("user_lookup")
                ),
                UnifiedTutorialStep(
                    title="Parse JSON for Data Selection",
                    description="Parsing JSON enables the JSON Path Selector for easy data referencing.",
                    instruction="Click 'Parse & Save JSON Output' to process the JSON and enable data path selection tools.",
                    target_element="parse_json_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Add Notification Step",
                    description="Now we'll add a second step to send a notification.",
                    instruction="Click '⚡ Add Action Step' again to create a notification step that will use data from the first step.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Notification Action",
                    description="Configure the notification step with proper data references.",
                    instruction="Set the action name to 'mw.send_notification' and output key to 'notification_result'. This creates our notification step.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.send_notification"
                ),
                UnifiedTutorialStep(
                    title="Explore JSON Path Selector",
                    description="The JSON Path Selector helps you reference data from previous steps.",
                    instruction="Click on the 'JSON Explorer' tab to see available data paths from your user lookup step.",
                    target_element="json_path_selector_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Review Generated YAML",
                    description="Check the YAML Preview to see your complete compound action.",
                    instruction="Click the 'YAML Preview' tab to see the generated Moveworks-compliant YAML with proper structure and data references.",
                    target_element="yaml_preview_panel",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Validate Your Workflow",
                    description="Always validate your workflow before deployment.",
                    instruction="Click the 'Validate Now' button to check for compliance issues and ensure your workflow meets Moveworks standards.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 1 Complete!",
                    description="Congratulations! You've created your first Moveworks compound action.",
                    instruction="You've learned the fundamentals: compound action naming, action steps, data flow, and validation. Ready for Module 2?",
                    action_type="info"
                )
            ]
        )

        # Module 2: Interactive Basic Workflow (from integrated system)
        module_2 = UnifiedTutorial(
            id="unified_interactive_basic",
            title="Interactive Basic Workflow",
            description="Hands-on tutorial with copy-paste examples and real-time guidance",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="10 minutes",
            learning_objectives=[
                "Experience real-time tutorial interaction",
                "Practice copy-paste workflow creation",
                "Learn JSON data exploration",
                "Understand YAML generation process"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to Interactive Learning",
                    description="This tutorial provides hands-on experience with copy-paste examples.",
                    instruction="You'll create a real workflow while learning. The tutorial panel is draggable - move it if it covers important areas.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Set Action Name with Copy-Paste",
                    description="Let's start by setting the compound action name using our copy-paste feature.",
                    instruction="Use the copy button below to automatically fill the Action Name field, or manually copy and paste.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="interactive_demo_workflow"
                ),
                UnifiedTutorialStep(
                    title="Add Action Step",
                    description="Create your first action step.",
                    instruction="Click the 'Add Action Step' button to create a new step. This opens the configuration panel.",
                    target_element="add_action_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure with JSON Example",
                    description="Add sample JSON to enable data exploration.",
                    instruction="Copy the JSON example below into the JSON Output field. This enables the JSON Path Selector.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data=get_tutorial_json_data("basic_example"),
                    sample_json=get_tutorial_json_data("basic_example")
                ),
                UnifiedTutorialStep(
                    title="Interactive Tutorial Complete",
                    description="You've experienced the interactive tutorial system!",
                    instruction="This tutorial demonstrated copy-paste functionality, real-time guidance, and JSON exploration. Try other tutorials to learn more!",
                    action_type="info"
                )
            ]
        )

        # Store tutorials
        self.tutorials = {
            "unified_module_1_basic": module_1,
            "unified_interactive_basic": module_2
        }

        # Populate tutorial list
        for tutorial_id, tutorial in self.tutorials.items():
            item = QListWidgetItem()

            # Create tutorial item text with icons
            difficulty_icon = {
                TutorialDifficulty.BEGINNER: "🟢",
                TutorialDifficulty.INTERMEDIATE: "🟡",
                TutorialDifficulty.ADVANCED: "🔴"
            }.get(tutorial.difficulty, "⚪")

            category_icon = {
                TutorialCategory.GETTING_STARTED: "🚀",
                TutorialCategory.EXPRESSION_TYPES: "🔧",
                TutorialCategory.DATA_HANDLING: "📊",
                TutorialCategory.ADVANCED_FEATURES: "⚡",
                TutorialCategory.BEST_PRACTICES: "✨"
            }.get(tutorial.category, "📚")

            item_text = f"{difficulty_icon} {category_icon} {tutorial.title}\n"
            item_text += f"   {tutorial.description}\n"
            item_text += f"   ⏱️ {tutorial.estimated_time} | 📚 {tutorial.difficulty.value}"

            item.setText(item_text)
            item.setData(Qt.UserRole, tutorial_id)

            self.tutorial_list.addItem(item)

    def _on_tutorial_selected(self):
        """Handle tutorial selection."""
        current_item = self.tutorial_list.currentItem()
        if current_item:
            tutorial_id = current_item.data(Qt.UserRole)
            tutorial = self.tutorials.get(tutorial_id)

            if tutorial:
                self._show_tutorial_details(tutorial)
                self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
            self.details_text.clear()

    def _show_tutorial_details(self, tutorial: UnifiedTutorial):
        """Show detailed information about the selected tutorial."""
        details_html = f"""
        <h2 style="color: #2c3e50; margin-bottom: 12px;">{tutorial.title}</h2>

        <div style="background-color: #e8f4fd; padding: 12px; border-radius: 6px; margin-bottom: 16px;">
            <p style="margin: 0;"><strong>📝 Description:</strong> {tutorial.description}</p>
            <p style="margin: 8px 0 0 0;"><strong>⏱️ Time:</strong> {tutorial.estimated_time} | <strong>📊 Difficulty:</strong> {tutorial.difficulty.value}</p>
            <p style="margin: 8px 0 0 0;"><strong>🏷️ Category:</strong> {tutorial.category.value}</p>
        </div>

        <h3 style="color: #2c3e50; margin-bottom: 8px;">🎯 Learning Objectives</h3>
        <ul style="margin-bottom: 16px;">
        """

        for objective in tutorial.learning_objectives:
            details_html += f"<li style='margin-bottom: 4px;'>{objective}</li>"

        details_html += "</ul>"

        if tutorial.prerequisites:
            details_html += "<h3 style='color: #2c3e50; margin-bottom: 8px;'>📋 Prerequisites</h3>"
            details_html += "<p style='margin-bottom: 16px;'>"
            details_html += ", ".join(tutorial.prerequisites)
            details_html += "</p>"

        details_html += f"""
        <div style="background-color: #f8f9fa; padding: 12px; border-radius: 6px;">
            <p style="margin: 0;"><strong>📚 Tutorial Structure:</strong> {len(tutorial.steps)} interactive steps</p>
            <p style="margin: 8px 0 0 0;"><strong>🎮 Features:</strong> Copy-paste examples, visual highlighting, real-time guidance</p>
        </div>
        """

        self.details_text.setHtml(details_html)

    def _start_selected_tutorial(self):
        """Start the selected tutorial."""
        current_item = self.tutorial_list.currentItem()
        if current_item:
            tutorial_id = current_item.data(Qt.UserRole)
            self.tutorial_selected.emit(tutorial_id)
            self.close()

    def _show_help(self):
        """Show help information about the tutorial system."""
        help_text = """
        <h2>🎓 Tutorial System Help</h2>

        <h3>🚀 Getting Started</h3>
        <p>Select a tutorial from the list to see its details, then click "Start Tutorial" to begin interactive learning.</p>

        <h3>🎮 Tutorial Features</h3>
        <ul>
            <li><strong>📋 Copy-Paste Examples:</strong> Click copy buttons to automatically fill form fields</li>
            <li><strong>🎯 Visual Highlighting:</strong> Important UI elements are highlighted during tutorials</li>
            <li><strong>📱 Draggable Panel:</strong> Move the tutorial panel if it covers important areas</li>
            <li><strong>⏭️ Step Navigation:</strong> Use Previous/Next buttons or skip tutorials anytime</li>
        </ul>

        <h3>📚 Tutorial Categories</h3>
        <ul>
            <li><strong>🚀 Getting Started:</strong> Basic concepts and first workflows</li>
            <li><strong>🔧 Expression Types:</strong> Different step types and configurations</li>
            <li><strong>📊 Data Handling:</strong> JSON processing and data flow</li>
            <li><strong>⚡ Advanced Features:</strong> Complex workflows and integrations</li>
            <li><strong>✨ Best Practices:</strong> Optimization and compliance tips</li>
        </ul>

        <h3>🎯 Difficulty Levels</h3>
        <ul>
            <li><strong>🟢 Beginner:</strong> No prior experience needed</li>
            <li><strong>🟡 Intermediate:</strong> Basic Moveworks knowledge helpful</li>
            <li><strong>🔴 Advanced:</strong> Requires understanding of previous modules</li>
        </ul>

        <p><strong>💡 Tip:</strong> Complete tutorials in order for the best learning experience!</p>
        """

        from PySide6.QtWidgets import QMessageBox
        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("Tutorial System Help")
        help_dialog.setTextFormat(Qt.RichText)
        help_dialog.setText(help_text)
        help_dialog.setStandardButtons(QMessageBox.Ok)
        help_dialog.exec()


class UnifiedTutorialManager:
    """
    Unified tutorial manager combining the best features from all systems:
    - Non-blocking interactive overlay
    - Comprehensive tutorial content
    - Clean selection dialog
    - Copy-paste functionality
    - Progress tracking and navigation
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_tutorial: Optional[UnifiedTutorial] = None
        self.current_step_index: int = 0
        self.tutorial_overlay: Optional[UnifiedTutorialOverlay] = None
        self.selection_dialog: Optional[UnifiedTutorialSelectionDialog] = None

    def show_tutorial_selection(self):
        """Show the unified tutorial selection dialog."""
        if not self.selection_dialog:
            self.selection_dialog = UnifiedTutorialSelectionDialog(self.main_window)
            self.selection_dialog.tutorial_selected.connect(self.start_tutorial)

        self.selection_dialog.show()
        self.selection_dialog.raise_()
        self.selection_dialog.activateWindow()

    def start_tutorial(self, tutorial_id: str) -> bool:
        """Start a unified tutorial."""
        # Get tutorial from selection dialog
        if not self.selection_dialog or tutorial_id not in self.selection_dialog.tutorials:
            return False

        self.current_tutorial = self.selection_dialog.tutorials[tutorial_id]
        self.current_step_index = 0

        # Create tutorial overlay
        self.tutorial_overlay = UnifiedTutorialOverlay(self.main_window)
        self.tutorial_overlay.next_step_requested.connect(self._next_step)
        self.tutorial_overlay.previous_step_requested.connect(self._previous_step)
        self.tutorial_overlay.tutorial_cancelled.connect(self._cancel_tutorial)

        # Start first step
        self._show_current_step()
        return True

    def _show_current_step(self):
        """Show the current tutorial step."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial.steps):
            self._complete_tutorial()
            return

        step = self.current_tutorial.steps[self.current_step_index]

        # Special handling for specific steps (from integrated system)
        if step.title == "Explore JSON Path Selector":
            self._activate_json_explorer_tab()
        elif step.title == "Review Generated YAML":
            self._activate_yaml_preview_tab()

        target_widget = self._find_target_widget(step.target_element)

        self.tutorial_overlay.show_step(
            step,
            target_widget,
            self.current_step_index + 1,
            len(self.current_tutorial.steps)
        )

    def _find_target_widget(self, target_element: Optional[str]) -> Optional[QWidget]:
        """Find the target widget for highlighting."""
        if not target_element:
            return None

        # Try to find widget by object name
        widget = self.main_window.findChild(QWidget, target_element)
        if widget:
            return widget

        # Try common widget mappings
        widget_mappings = {
            "add_action_button": "add_action_btn",
            "compound_action_name_field": "action_name_edit",
            "action_config_panel": "config_panel",
            "json_output_edit": "action_json_edit",
            "parse_json_btn": "parse_json_btn",
            "add_input_arg_btn": "add_input_arg_btn",
            "json_path_selector_button": "enhanced_json_panel",
            "yaml_preview_panel": "yaml_panel",
            "validate_button": "validate_btn"
        }

        mapped_name = widget_mappings.get(target_element)
        if mapped_name:
            widget = self.main_window.findChild(QWidget, mapped_name)
            if widget:
                return widget

        return None

    def _activate_json_explorer_tab(self):
        """Activate the JSON Explorer tab."""
        try:
            # Find the right tabs widget and activate JSON Explorer
            right_tabs = self.main_window.findChild(QWidget, "right_tabs")
            if hasattr(right_tabs, 'setCurrentIndex'):
                # Assuming JSON Explorer is at index 0
                right_tabs.setCurrentIndex(0)
        except Exception:
            pass

    def _activate_yaml_preview_tab(self):
        """Activate the YAML Preview tab."""
        try:
            # Find the right tabs widget and activate YAML Preview
            right_tabs = self.main_window.findChild(QWidget, "right_tabs")
            if hasattr(right_tabs, 'setCurrentIndex'):
                # Assuming YAML Preview is at index 1
                right_tabs.setCurrentIndex(1)
        except Exception:
            pass

    def _next_step(self):
        """Move to the next tutorial step."""
        if self.current_tutorial and self.current_step_index < len(self.current_tutorial.steps) - 1:
            self.current_step_index += 1
            self._show_current_step()
        else:
            self._complete_tutorial()

    def _previous_step(self):
        """Move to the previous tutorial step."""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._show_current_step()

    def _cancel_tutorial(self):
        """Cancel the current tutorial."""
        if self.tutorial_overlay:
            self.tutorial_overlay.hide()
            self.tutorial_overlay = None
        self.current_tutorial = None
        self.current_step_index = 0

    def _complete_tutorial(self):
        """Complete the current tutorial."""
        if self.tutorial_overlay:
            self.tutorial_overlay.hide()
            self.tutorial_overlay = None

        # Show completion message
        from PySide6.QtWidgets import QMessageBox
        if self.current_tutorial:
            QMessageBox.information(
                self.main_window,
                "🎉 Tutorial Complete!",
                f"Congratulations! You've completed '{self.current_tutorial.title}'.\n\n"
                f"You've learned: {', '.join(self.current_tutorial.learning_objectives[:2])}...\n\n"
                f"Ready to try another tutorial?"
            )

        self.current_tutorial = None
        self.current_step_index = 0

    def is_tutorial_active(self) -> bool:
        """Check if a tutorial is currently active."""
        return self.current_tutorial is not None

    def get_current_tutorial_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active tutorial."""
        if not self.current_tutorial:
            return None

        return {
            "id": self.current_tutorial.id,
            "title": self.current_tutorial.title,
            "current_step": self.current_step_index + 1,
            "total_steps": len(self.current_tutorial.steps),
            "progress": (self.current_step_index + 1) / len(self.current_tutorial.steps) * 100
        }
