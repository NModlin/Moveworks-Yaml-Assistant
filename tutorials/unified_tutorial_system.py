"""
Unified Tutorial System with Plugin-Based Architecture.

This module provides a comprehensive tutorial system that consolidates all functionality
from legacy systems while implementing a maintainable plugin-based architecture.
"""

import os
import sys
import importlib
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Type
from enum import Enum
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QProgressBar, QFrame, QListWidget, QListWidgetItem, QDialog, QScrollArea,
    QApplication, QSizePolicy, QMessageBox, QFileDialog, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSettings
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QClipboard


class TutorialCategory(Enum):
    """Tutorial categories for organization."""
    GETTING_STARTED = "Getting Started"
    EXPRESSION_TYPES = "Expression Types"
    DATA_HANDLING = "Data Handling"
    ADVANCED_FEATURES = "Advanced Features"
    BEST_PRACTICES = "Best Practices"
    CUSTOM = "Custom"


class TutorialDifficulty(Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


@dataclass
class UnifiedTutorialStep:
    """Enhanced tutorial step with comprehensive metadata and functionality."""
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
    highlight_color: str = "#4a86e8"  # Maintain exact visual consistency
    sample_json: Optional[Dict[str, Any]] = None  # JSON examples for the step
    screenshot_path: Optional[str] = None
    video_url: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)


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
    version: str = "1.0.0"
    author: str = ""
    created_date: str = ""
    last_modified: str = ""
    plugin_source: str = ""  # Which plugin provided this tutorial


class TutorialPlugin(ABC):
    """Base class for all tutorial plugins."""
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata including name, version, description."""
        pass
    
    @abstractmethod
    def get_tutorials(self) -> List[UnifiedTutorial]:
        """Return list of tutorials provided by this plugin."""
        pass
    
    @abstractmethod
    def get_plugin_id(self) -> str:
        """Return unique plugin identifier."""
        pass
    
    def initialize(self) -> bool:
        """Initialize plugin. Return True if successful."""
        return True
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    def validate_tutorial(self, tutorial: UnifiedTutorial) -> List[str]:
        """Validate tutorial structure. Return list of errors."""
        errors = []
        
        if not tutorial.id:
            errors.append("Tutorial ID is required")
        if not tutorial.title:
            errors.append("Tutorial title is required")
        if not tutorial.steps:
            errors.append("Tutorial must have at least one step")
        
        return errors


class PluginManager:
    """Manages tutorial plugin discovery, loading, and lifecycle."""
    
    def __init__(self, plugin_directory: str = "tutorials/plugins"):
        self.plugin_directory = Path(plugin_directory)
        self.plugins: Dict[str, TutorialPlugin] = {}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
        self.tutorials_cache: Dict[str, UnifiedTutorial] = {}
        
        # Ensure plugin directory exists
        self.plugin_directory.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = self.plugin_directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Tutorial plugins directory\n")
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugin directory."""
        discovered = []
        
        if not self.plugin_directory.exists():
            return discovered
        
        for file_path in self.plugin_directory.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            
            module_name = file_path.stem
            discovered.append(module_name)
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin by name."""
        try:
            # Add plugin directory to Python path if not already there
            plugin_dir_str = str(self.plugin_directory.parent)
            if plugin_dir_str not in sys.path:
                sys.path.insert(0, plugin_dir_str)
            
            # Import the plugin module
            module_path = f"tutorials.plugins.{plugin_name}"
            module = importlib.import_module(module_path)
            
            # Find plugin class (should end with 'Plugin')
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, TutorialPlugin) and 
                    attr != TutorialPlugin):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                print(f"Warning: No plugin class found in {plugin_name}")
                return False
            
            # Instantiate and initialize plugin
            plugin_instance = plugin_class()
            if not plugin_instance.initialize():
                print(f"Warning: Plugin {plugin_name} failed to initialize")
                return False
            
            # Store plugin and metadata
            plugin_id = plugin_instance.get_plugin_id()
            self.plugins[plugin_id] = plugin_instance
            self.plugin_metadata[plugin_id] = plugin_instance.get_metadata()
            
            # Cache tutorials from this plugin
            for tutorial in plugin_instance.get_tutorials():
                tutorial.plugin_source = plugin_id
                self.tutorials_cache[tutorial.id] = tutorial
            
            print(f"✓ Loaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> int:
        """Load all discovered plugins. Return number of successfully loaded plugins."""
        discovered = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in discovered:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        return loaded_count
    
    def get_plugin(self, plugin_id: str) -> Optional[TutorialPlugin]:
        """Get a loaded plugin by ID."""
        return self.plugins.get(plugin_id)
    
    def get_all_tutorials(self) -> List[UnifiedTutorial]:
        """Get all tutorials from all loaded plugins."""
        return list(self.tutorials_cache.values())
    
    def get_tutorials_by_category(self, category: TutorialCategory) -> List[UnifiedTutorial]:
        """Get tutorials filtered by category."""
        return [t for t in self.tutorials_cache.values() if t.category == category]
    
    def get_tutorial_by_id(self, tutorial_id: str) -> Optional[UnifiedTutorial]:
        """Get a specific tutorial by ID."""
        return self.tutorials_cache.get(tutorial_id)
    
    def import_plugin_from_file(self, file_path: str) -> bool:
        """Import a plugin from an external file."""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return False
            
            # Copy to plugin directory
            dest_path = self.plugin_directory / source_path.name
            dest_path.write_text(source_path.read_text())
            
            # Load the new plugin
            plugin_name = source_path.stem
            return self.load_plugin(plugin_name)
            
        except Exception as e:
            print(f"Failed to import plugin from {file_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin and remove its tutorials."""
        if plugin_id not in self.plugins:
            return False
        
        try:
            # Cleanup plugin
            self.plugins[plugin_id].cleanup()
            
            # Remove tutorials from cache
            tutorials_to_remove = [
                tid for tid, tutorial in self.tutorials_cache.items()
                if tutorial.plugin_source == plugin_id
            ]
            for tid in tutorials_to_remove:
                del self.tutorials_cache[tid]
            
            # Remove plugin
            del self.plugins[plugin_id]
            del self.plugin_metadata[plugin_id]
            
            return True
            
        except Exception as e:
            print(f"Failed to unload plugin {plugin_id}: {e}")
            return False
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin (unload and load again)."""
        if plugin_id in self.plugins:
            # Find the module name from metadata
            metadata = self.plugin_metadata.get(plugin_id, {})
            module_name = metadata.get("module_name", plugin_id)
            
            # Unload first
            self.unload_plugin(plugin_id)
            
            # Reload module
            module_path = f"tutorials.plugins.{module_name}"
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
            
            # Load again
            return self.load_plugin(module_name)
        
        return False


class UnifiedTutorialOverlay(QWidget):
    """
    Resizable, non-blocking tutorial overlay with visual highlighting.

    Features:
    - Maintains exact visual styling from current system (#4a86e8 colors, proper spacing)
    - Resizable panel with layout constraints (400x300px minimum)
    - Smart positioning to avoid covering target elements
    - Draggable with position memory
    - Pulsing animation and semi-transparent overlay
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

        # Settings for position memory
        self.settings = QSettings("MoveworksYAMLAssistant", "TutorialSystem")

        # Create separate floating panel for instructions (independent window)
        self.floating_panel = QWidget(None)  # No parent - truly independent
        # Use Window flag to enable resizing while keeping it on top
        self.floating_panel.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.floating_panel.setAttribute(Qt.WA_DeleteOnClose, False)
        self.floating_panel.setWindowTitle("Tutorial Guide")

        self._setup_floating_panel()
        self._setup_animations()
        self._restore_panel_position()

    def _setup_floating_panel(self):
        """Setup the resizable floating instruction panel with exact visual styling."""
        # Enhanced size requirements for resizable window
        self.floating_panel.setMinimumSize(400, 300)  # Minimum for readability
        self.floating_panel.setMaximumSize(1000, 1200)  # Larger maximum for flexibility
        self.floating_panel.resize(500, 450)  # Slightly larger default size

        # Main layout with exact spacing (16px margins, 12px element spacing)
        layout = QVBoxLayout(self.floating_panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with progress - exact color scheme (#4a86e8)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #4a86e8;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 8, 8, 8)

        # Step indicator with exact typography (16px for titles)
        self.step_indicator = QLabel("Step 1 of 1")
        self.step_indicator.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
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

        # Content area with scroll - exact background (#f8f8f8)
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(8)

        # Step title with exact typography
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

        # Step description - resizable with preferred height
        self.step_description = QTextEdit()
        self.step_description.setReadOnly(True)
        self.step_description.setMinimumHeight(60)
        self.step_description.setMaximumHeight(120)  # Allow some expansion
        self.step_description.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #f8f8f8;
                border-radius: 4px;
                padding: 8px;
                color: #2c3e50;
            }
        """)
        content_layout.addWidget(self.step_description)

        # Instruction text - resizable with preferred height
        self.instruction_text = QTextEdit()
        self.instruction_text.setReadOnly(True)
        self.instruction_text.setMinimumHeight(80)
        self.instruction_text.setMaximumHeight(200)  # Allow more expansion for longer instructions
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
        self.copy_paste_text.setMinimumHeight(60)
        self.copy_paste_text.setMaximumHeight(150)  # Allow expansion for longer code examples
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
        content_layout.addStretch()

        content_scroll.setWidget(content_widget)
        layout.addWidget(content_scroll)

        # Navigation buttons with exact styling
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
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

        # Next button with primary color
        self.next_btn = QPushButton("Next →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d71d9;
            }
        """)
        self.next_btn.clicked.connect(self.next_step_requested.emit)
        button_layout.addWidget(self.next_btn)

        layout.addWidget(button_frame)

        # Make panel draggable and resizable
        self.floating_panel.mousePressEvent = self._start_drag
        self.floating_panel.mouseMoveEvent = self._drag_panel
        self.floating_panel.mouseReleaseEvent = self._end_drag
        self.drag_position = None

    def _setup_animations(self):
        """Setup pulsing animation for highlighting."""
        self.highlight_animation = QPropertyAnimation(self, b"geometry")
        self.highlight_animation.setDuration(500)
        self.highlight_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Pulse animation timer for highlighting
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_highlight)
        self.pulse_timer.setInterval(1000)

    def _restore_panel_position(self):
        """Restore panel position from settings."""
        pos = self.settings.value("tutorial_panel_position", QPoint(100, 100))
        size = self.settings.value("tutorial_panel_size", self.floating_panel.size())

        self.floating_panel.move(pos)
        self.floating_panel.resize(size)

    def _save_panel_position(self):
        """Save panel position to settings."""
        self.settings.setValue("tutorial_panel_position", self.floating_panel.pos())
        self.settings.setValue("tutorial_panel_size", self.floating_panel.size())

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
        """Smart positioning to avoid covering target widget."""
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
        """Setup highlighting for target widget with exact color."""
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
        """Paint the overlay with non-blocking highlighting - green border only."""
        if not self.target_rect.isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # NO DARK OVERLAY - Only draw highlight border around target area
        # This ensures the UI remains fully interactive and visible

        # Draw multiple layers for a very prominent green highlight
        for i in range(4):
            glow_color = QColor("#28a745")  # Green color for highlighting
            glow_color.setAlpha(max(30, 80 - i * 15))  # Fade out for outer layers
            pen_glow = QPen(glow_color, 6 + i * 2)
            painter.setPen(pen_glow)
            painter.setBrush(QBrush(Qt.NoBrush))

            # Expand rect for each glow layer
            glow_rect = self.target_rect.adjusted(-i*3, -i*3, i*3, i*3)
            painter.drawRoundedRect(glow_rect, 8, 8)

        # Draw main highlight border
        highlight_color = QColor("#28a745")  # Bright green
        highlight_color.setAlpha(255)

        pen = QPen(highlight_color, 4)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRoundedRect(self.target_rect, 8, 8)

    def _copy_to_clipboard(self):
        """Copy the example text to clipboard with visual feedback."""
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
        """End dragging and save position."""
        self.drag_position = None
        self._save_panel_position()

    def hide(self):
        """Hide the overlay and floating panel."""
        super().hide()
        if self.floating_panel:
            self.floating_panel.hide()
        if self.pulse_timer:
            self.pulse_timer.stop()
        self._save_panel_position()

    def closeEvent(self, event):
        """Handle close event."""
        if self.floating_panel:
            self.floating_panel.close()
        if self.pulse_timer:
            self.pulse_timer.stop()
        self._save_panel_position()
        super().closeEvent(event)


class UnifiedTutorialSelectionDialog(QDialog):
    """Enhanced tutorial selection dialog with plugin management."""

    tutorial_selected = Signal(str)  # Emits tutorial ID
    import_plugin_requested = Signal()

    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setWindowTitle("Moveworks YAML Assistant - Tutorial System")
        self.setModal(True)
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self._setup_ui()
        self._load_tutorials()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the tutorial selection UI with exact visual styling."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with exact typography
        header_label = QLabel("🎓 Unified Tutorial System")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        header_label.setAlignment(Qt.AlignCenter)

        # Subtitle
        subtitle_label = QLabel("Plugin-based tutorial system with comprehensive content migration")
        subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 16px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)

        layout.addWidget(header_label)
        layout.addWidget(subtitle_label)

        # Main content with splitter for resizable panels
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Tutorial list with categories
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #f8f8f8;
                padding: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)

        # Tutorial list header
        list_header = QHBoxLayout()
        list_label = QLabel("📚 Available Tutorials")
        list_label.setFont(QFont("Arial", 14, QFont.Bold))
        list_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        list_header.addWidget(list_label)

        list_header.addStretch()

        # Import plugin button
        self.import_btn = QPushButton("📥 Import Plugin")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.import_btn.clicked.connect(self._import_plugin)
        list_header.addWidget(self.import_btn)

        left_layout.addLayout(list_header)

        # Category tabs
        self.category_tabs = QTabWidget()
        self.category_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a86e8;
                color: white;
            }
        """)

        # Create tabs for each category
        self.tutorial_lists = {}
        for category in TutorialCategory:
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(4, 4, 4, 4)

            tutorial_list = QListWidget()
            tutorial_list.setStyleSheet("""
                QListWidget {
                    border: none;
                    background-color: white;
                    selection-background-color: #4a86e8;
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
                    background-color: #4a86e8;
                    color: white;
                }
            """)
            tutorial_list.itemSelectionChanged.connect(self._on_tutorial_selected)

            tab_layout.addWidget(tutorial_list)
            self.tutorial_lists[category] = tutorial_list

            # Add tab with icon
            category_icons = {
                TutorialCategory.GETTING_STARTED: "🚀",
                TutorialCategory.EXPRESSION_TYPES: "🔧",
                TutorialCategory.DATA_HANDLING: "📊",
                TutorialCategory.ADVANCED_FEATURES: "⚡",
                TutorialCategory.BEST_PRACTICES: "✨",
                TutorialCategory.CUSTOM: "🔌"
            }
            icon = category_icons.get(category, "📚")
            self.category_tabs.addTab(tab_widget, f"{icon} {category.value}")

        left_layout.addWidget(self.category_tabs)

        # Right panel - Tutorial details
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

        # Plugin info section
        plugin_info_label = QLabel("🔌 Plugin Information")
        plugin_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        plugin_info_label.setStyleSheet("color: #2c3e50; margin-top: 8px; margin-bottom: 4px;")
        right_layout.addWidget(plugin_info_label)

        self.plugin_info_text = QTextEdit()
        self.plugin_info_text.setReadOnly(True)
        self.plugin_info_text.setMaximumHeight(100)
        self.plugin_info_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 8px;
                font-size: 11px;
                color: #6c757d;
            }
        """)
        right_layout.addWidget(self.plugin_info_text)

        # Set splitter proportions
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])
        layout.addWidget(main_splitter)

        # Bottom controls with exact styling
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

        # Plugin management button
        manage_btn = QPushButton("🔧 Manage Plugins")
        manage_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        manage_btn.clicked.connect(self._manage_plugins)
        controls_layout.addWidget(manage_btn)

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

        # Start tutorial button with primary color
        self.start_button = QPushButton("🚀 Start Tutorial")
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d71d9;
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
        self.start_button.clicked.connect(self._start_selected_tutorial)
        self.close_button.clicked.connect(self.close)

    def _load_tutorials(self):
        """Load tutorials from plugin manager and populate the UI."""
        # Clear existing tutorials
        for tutorial_list in self.tutorial_lists.values():
            tutorial_list.clear()

        # Load tutorials from plugin manager
        all_tutorials = self.plugin_manager.get_all_tutorials()

        # Group tutorials by category
        for tutorial in all_tutorials:
            category_list = self.tutorial_lists.get(tutorial.category)
            if category_list:
                item = QListWidgetItem()

                # Create tutorial item text with icons
                difficulty_icon = {
                    TutorialDifficulty.BEGINNER: "🟢",
                    TutorialDifficulty.INTERMEDIATE: "🟡",
                    TutorialDifficulty.ADVANCED: "🔴"
                }.get(tutorial.difficulty, "⚪")

                item_text = f"{difficulty_icon} {tutorial.title}\n"
                item_text += f"   {tutorial.description}\n"
                item_text += f"   ⏱️ {tutorial.estimated_time} | 📚 {tutorial.difficulty.value}"
                if tutorial.prerequisites:
                    item_text += f" | 📋 Prerequisites: {len(tutorial.prerequisites)}"

                item.setText(item_text)
                item.setData(Qt.UserRole, tutorial.id)

                category_list.addItem(item)

    def _on_tutorial_selected(self):
        """Handle tutorial selection from any category tab."""
        # Find which list has a selection
        selected_tutorial = None
        selected_tutorial_id = None

        for category_list in self.tutorial_lists.values():
            current_item = category_list.currentItem()
            if current_item:
                selected_tutorial_id = current_item.data(Qt.UserRole)
                selected_tutorial = self.plugin_manager.get_tutorial_by_id(selected_tutorial_id)
                break

        if selected_tutorial:
            self._show_tutorial_details(selected_tutorial)
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
            self.details_text.clear()
            self.plugin_info_text.clear()

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
            <p style="margin: 8px 0 0 0;"><strong>📅 Version:</strong> {tutorial.version} | <strong>👤 Author:</strong> {tutorial.author}</p>
        </div>
        """

        self.details_text.setHtml(details_html)

        # Show plugin information
        plugin_info = self.plugin_manager.plugin_metadata.get(tutorial.plugin_source, {})
        plugin_html = f"""
        <p><strong>Plugin:</strong> {plugin_info.get('name', 'Unknown')}</p>
        <p><strong>Version:</strong> {plugin_info.get('version', 'Unknown')} | <strong>Source:</strong> {plugin_info.get('source', 'Unknown')}</p>
        <p><strong>Description:</strong> {plugin_info.get('description', 'No description available')}</p>
        """
        self.plugin_info_text.setHtml(plugin_html)

    def _start_selected_tutorial(self):
        """Start the selected tutorial."""
        # Find selected tutorial
        selected_tutorial_id = None
        for category_list in self.tutorial_lists.values():
            current_item = category_list.currentItem()
            if current_item:
                selected_tutorial_id = current_item.data(Qt.UserRole)
                break

        if selected_tutorial_id:
            self.tutorial_selected.emit(selected_tutorial_id)
            self.close()

    def _import_plugin(self):
        """Import a plugin from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Tutorial Plugin",
            "",
            "Python Files (*.py);;All Files (*)"
        )

        if file_path:
            success = self.plugin_manager.import_plugin_from_file(file_path)
            if success:
                QMessageBox.information(
                    self,
                    "Plugin Imported",
                    f"Plugin imported successfully from {file_path}"
                )
                self._load_tutorials()  # Refresh tutorial list
            else:
                QMessageBox.warning(
                    self,
                    "Import Failed",
                    f"Failed to import plugin from {file_path}"
                )

    def _manage_plugins(self):
        """Show plugin management dialog."""
        # Create a simple plugin management dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Plugin Management")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(dialog)

        # Plugin list
        plugin_list = QListWidget()
        for plugin_id, metadata in self.plugin_manager.plugin_metadata.items():
            item_text = f"{metadata.get('name', plugin_id)} v{metadata.get('version', '1.0.0')}\n"
            item_text += f"   {metadata.get('description', 'No description')}\n"
            item_text += f"   📊 Tutorials: {metadata.get('tutorial_count', 0)}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, plugin_id)
            plugin_list.addItem(item)

        layout.addWidget(QLabel("Loaded Plugins:"))
        layout.addWidget(plugin_list)

        # Buttons
        button_layout = QHBoxLayout()

        reload_btn = QPushButton("🔄 Reload Plugin")
        reload_btn.clicked.connect(lambda: self._reload_selected_plugin(plugin_list))
        button_layout.addWidget(reload_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def _reload_selected_plugin(self, plugin_list: QListWidget):
        """Reload the selected plugin."""
        current_item = plugin_list.currentItem()
        if current_item:
            plugin_id = current_item.data(Qt.UserRole)
            success = self.plugin_manager.reload_plugin(plugin_id)
            if success:
                QMessageBox.information(self, "Plugin Reloaded", f"Plugin {plugin_id} reloaded successfully")
                self._load_tutorials()  # Refresh tutorial list
            else:
                QMessageBox.warning(self, "Reload Failed", f"Failed to reload plugin {plugin_id}")

    def _show_help(self):
        """Show help information about the unified tutorial system."""
        help_text = """
        <h2>🎓 Unified Tutorial System Help</h2>

        <h3>🚀 Getting Started</h3>
        <p>Select a tutorial from any category tab to see its details, then click "Start Tutorial" to begin interactive learning.</p>

        <h3>🎮 Tutorial Features</h3>
        <ul>
            <li><strong>📋 Copy-Paste Examples:</strong> Click copy buttons to automatically fill form fields</li>
            <li><strong>🎯 Visual Highlighting:</strong> Important UI elements are highlighted during tutorials</li>
            <li><strong>📱 Draggable Panel:</strong> Move the tutorial panel if it covers important areas</li>
            <li><strong>⏭️ Step Navigation:</strong> Use Previous/Next buttons or skip tutorials anytime</li>
            <li><strong>💾 Position Memory:</strong> Tutorial panel remembers your preferred position</li>
        </ul>

        <h3>📚 Tutorial Categories</h3>
        <ul>
            <li><strong>🚀 Getting Started:</strong> Basic concepts and first workflows</li>
            <li><strong>🔧 Expression Types:</strong> Different step types and configurations</li>
            <li><strong>📊 Data Handling:</strong> JSON processing and data flow</li>
            <li><strong>⚡ Advanced Features:</strong> Complex workflows and integrations</li>
            <li><strong>✨ Best Practices:</strong> Optimization and compliance tips</li>
            <li><strong>🔌 Custom:</strong> User-imported tutorial plugins</li>
        </ul>

        <h3>🔌 Plugin System</h3>
        <ul>
            <li><strong>📥 Import Plugins:</strong> Add new tutorial plugins from Python files</li>
            <li><strong>🔧 Manage Plugins:</strong> View and reload existing plugins</li>
            <li><strong>🔄 Auto-Discovery:</strong> Plugins are automatically discovered and loaded</li>
        </ul>

        <h3>🎯 Difficulty Levels</h3>
        <ul>
            <li><strong>🟢 Beginner:</strong> No prior experience needed</li>
            <li><strong>🟡 Intermediate:</strong> Basic Moveworks knowledge helpful</li>
            <li><strong>🔴 Advanced:</strong> Requires understanding of previous modules</li>
        </ul>

        <p><strong>💡 Tip:</strong> Complete tutorials in order for the best learning experience!</p>
        """

        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("Unified Tutorial System Help")
        help_dialog.setTextFormat(Qt.RichText)
        help_dialog.setText(help_text)
        help_dialog.setStandardButtons(QMessageBox.Ok)
        help_dialog.exec()

    def refresh_tutorials(self):
        """Refresh the tutorial list from plugin manager."""
        self._load_tutorials()


class UnifiedTutorialManager:
    """
    Main controller for the unified tutorial system with plugin-based architecture.

    Features:
    - Plugin-based tutorial loading and management
    - Non-blocking interactive overlay with exact visual styling
    - Comprehensive tutorial content migration
    - Clean selection dialog with category organization
    - Copy-paste functionality and position memory
    - Complete codebase cleanup and deprecation handling
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_tutorial: Optional[UnifiedTutorial] = None
        self.current_step_index: int = 0
        self.tutorial_overlay: Optional[UnifiedTutorialOverlay] = None
        self.selection_dialog: Optional[UnifiedTutorialSelectionDialog] = None

        # Initialize plugin manager and load plugins
        self.plugin_manager = PluginManager()
        self._load_plugins()

    def _load_plugins(self):
        """Load all available tutorial plugins."""
        try:
            loaded_count = self.plugin_manager.load_all_plugins()
            print(f"✓ Loaded {loaded_count} tutorial plugins")

            # Log loaded tutorials
            all_tutorials = self.plugin_manager.get_all_tutorials()
            print(f"✓ Available tutorials: {len(all_tutorials)}")

            for category in TutorialCategory:
                category_tutorials = self.plugin_manager.get_tutorials_by_category(category)
                if category_tutorials:
                    print(f"  - {category.value}: {len(category_tutorials)} tutorials")

        except Exception as e:
            print(f"✗ Error loading plugins: {e}")

    def show_tutorial_selection(self):
        """Show the unified tutorial selection dialog."""
        if not self.selection_dialog:
            self.selection_dialog = UnifiedTutorialSelectionDialog(self.plugin_manager, self.main_window)
            self.selection_dialog.tutorial_selected.connect(self.start_tutorial)

        # Refresh tutorials in case plugins were updated
        self.selection_dialog.refresh_tutorials()

        self.selection_dialog.show()
        self.selection_dialog.raise_()
        self.selection_dialog.activateWindow()

    def start_tutorial(self, tutorial_id: str) -> bool:
        """Start a unified tutorial by ID."""
        tutorial = self.plugin_manager.get_tutorial_by_id(tutorial_id)
        if not tutorial:
            print(f"✗ Tutorial not found: {tutorial_id}")
            return False

        self.current_tutorial = tutorial
        self.current_step_index = 0

        # Create tutorial overlay with exact visual styling
        self.tutorial_overlay = UnifiedTutorialOverlay(self.main_window)
        self.tutorial_overlay.next_step_requested.connect(self._next_step)
        self.tutorial_overlay.previous_step_requested.connect(self._previous_step)
        self.tutorial_overlay.tutorial_cancelled.connect(self._cancel_tutorial)

        # Start first step
        self._show_current_step()
        print(f"✓ Started tutorial: {tutorial.title}")
        return True

    def _show_current_step(self):
        """Show the current tutorial step with enhanced features."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial.steps):
            self._complete_tutorial()
            return

        step = self.current_tutorial.steps[self.current_step_index]

        # Special handling for specific steps (enhanced from integrated system)
        if step.title == "Explore JSON Path Selector" or "JSON Explorer" in step.instruction:
            self._activate_json_explorer_tab()
        elif step.title == "Review Generated YAML" or "YAML Preview" in step.instruction:
            self._activate_yaml_preview_tab()

        # Find target widget with enhanced mapping
        target_widget = self._find_target_widget(step.target_element)

        # Show step with exact visual styling
        self.tutorial_overlay.show_step(
            step,
            target_widget,
            self.current_step_index + 1,
            len(self.current_tutorial.steps)
        )

    def _find_target_widget(self, target_element: Optional[str]) -> Optional[QWidget]:
        """Find the target widget for highlighting with comprehensive mapping."""
        if not target_element:
            return None

        # Try to find widget by object name first
        widget = self.main_window.findChild(QWidget, target_element)
        if widget:
            return widget

        # Enhanced widget mappings for all legacy systems
        widget_mappings = {
            # Basic mappings
            "add_action_button": "add_action_btn",
            "add_action_btn": "add_action_btn",
            "compound_action_name_field": "action_name_edit",
            "action_config_panel": "config_panel",
            "json_output_edit": "action_json_edit",
            "parse_json_btn": "parse_json_btn",
            "add_input_arg_btn": "add_input_arg_btn",
            "json_path_selector_button": "enhanced_json_panel",
            "yaml_preview_panel": "yaml_panel",
            "validate_button": "validate_btn",

            # Advanced expression mappings
            "add_switch_button": "add_switch_btn",
            "add_for_button": "add_for_btn",
            "add_try_catch_button": "add_try_catch_btn",
            "add_parallel_button": "add_parallel_btn",
            "add_script_button": "add_script_btn",
            "switch_config_panel": "switch_config_panel",
            "for_config_panel": "for_config_panel",
            "try_catch_config_panel": "try_catch_config_panel",
            "parallel_config_panel": "parallel_config_panel",
            "script_config_panel": "script_config_panel",

            # Legacy system compatibility
            "tutorial_panel": "tutorial_overlay",
            "tutorial_dialog": "tutorial_selection_dialog"
        }

        mapped_name = widget_mappings.get(target_element)
        if mapped_name:
            widget = self.main_window.findChild(QWidget, mapped_name)
            if widget:
                return widget

        # Try partial name matching for dynamic widgets
        for child in self.main_window.findChildren(QWidget):
            if child.objectName() and target_element in child.objectName():
                return child

        return None

    def _activate_json_explorer_tab(self):
        """Activate the JSON Explorer tab."""
        try:
            # Find the right tabs widget and activate JSON Explorer
            right_tabs = self.main_window.findChild(QWidget, "right_tabs")
            if hasattr(right_tabs, 'setCurrentIndex'):
                # Assuming JSON Explorer is at index 0
                right_tabs.setCurrentIndex(0)
        except Exception as e:
            print(f"Could not activate JSON Explorer tab: {e}")

    def _activate_yaml_preview_tab(self):
        """Activate the YAML Preview tab."""
        try:
            # Find the right tabs widget and activate YAML Preview
            right_tabs = self.main_window.findChild(QWidget, "right_tabs")
            if hasattr(right_tabs, 'setCurrentIndex'):
                # Assuming YAML Preview is at index 1
                right_tabs.setCurrentIndex(1)
        except Exception as e:
            print(f"Could not activate YAML Preview tab: {e}")

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
        print("Tutorial cancelled by user")

    def _complete_tutorial(self):
        """Complete the current tutorial with enhanced feedback."""
        if self.tutorial_overlay:
            self.tutorial_overlay.hide()
            self.tutorial_overlay = None

        # Show enhanced completion message
        if self.current_tutorial:
            completion_message = f"🎉 Tutorial Complete!\n\n"
            completion_message += f"You've completed '{self.current_tutorial.title}'.\n\n"
            completion_message += f"Learning Objectives Achieved:\n"
            for i, objective in enumerate(self.current_tutorial.learning_objectives[:3], 1):
                completion_message += f"{i}. {objective}\n"
            if len(self.current_tutorial.learning_objectives) > 3:
                completion_message += f"...and {len(self.current_tutorial.learning_objectives) - 3} more!\n"
            completion_message += f"\nReady to try another tutorial?"

            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self.main_window,
                "Tutorial Complete!",
                completion_message
            )

        self.current_tutorial = None
        self.current_step_index = 0
        print("Tutorial completed successfully")

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
            "progress": (self.current_step_index + 1) / len(self.current_tutorial.steps) * 100,
            "category": self.current_tutorial.category.value,
            "difficulty": self.current_tutorial.difficulty.value,
            "plugin_source": self.current_tutorial.plugin_source
        }

    def get_available_tutorials(self) -> List[UnifiedTutorial]:
        """Get all available tutorials from all plugins."""
        return self.plugin_manager.get_all_tutorials()

    def get_tutorials_by_category(self, category: TutorialCategory) -> List[UnifiedTutorial]:
        """Get tutorials filtered by category."""
        return self.plugin_manager.get_tutorials_by_category(category)

    def reload_plugins(self):
        """Reload all plugins and refresh tutorial list."""
        try:
            # Reload all plugins
            for plugin_id in list(self.plugin_manager.plugins.keys()):
                self.plugin_manager.reload_plugin(plugin_id)

            # Refresh selection dialog if open
            if self.selection_dialog:
                self.selection_dialog.refresh_tutorials()

            print("✓ All plugins reloaded successfully")

        except Exception as e:
            print(f"✗ Error reloading plugins: {e}")

    def import_plugin(self, file_path: str) -> bool:
        """Import a new plugin from file."""
        success = self.plugin_manager.import_plugin_from_file(file_path)
        if success and self.selection_dialog:
            self.selection_dialog.refresh_tutorials()
        return success

    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all loaded plugins."""
        return self.plugin_manager.plugin_metadata.copy()

    def cleanup(self):
        """Cleanup tutorial system resources."""
        if self.tutorial_overlay:
            self.tutorial_overlay.hide()
            self.tutorial_overlay = None

        if self.selection_dialog:
            self.selection_dialog.close()
            self.selection_dialog = None

        # Cleanup all plugins
        for plugin in self.plugin_manager.plugins.values():
            plugin.cleanup()

        print("Tutorial system cleanup completed")


