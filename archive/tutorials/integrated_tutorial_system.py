"""
Integrated Tutorial System for the Moveworks YAML Assistant.

This module provides interactive tutorials that work directly with the actual
application UI, providing real-time guidance with copy-paste examples and
step-by-step instructions.
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QTextEdit, QProgressBar, QGraphicsDropShadowEffect,
    QScrollArea, QGroupBox, QApplication, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

from tutorial_data import get_tutorial_json_data, get_tutorial_script_example


@dataclass
class InteractiveTutorialStep:
    """Enhanced tutorial step with copy-paste examples and real UI interaction."""
    title: str
    description: str
    instruction: str
    target_element: Optional[str] = None
    action_type: str = "info"  # info, click, type, copy_paste, highlight
    copy_paste_data: Optional[str] = None
    expected_result: Optional[str] = None
    validation_function: Optional[callable] = None
    auto_advance: bool = False
    sample_json: Optional[Dict[str, Any]] = None


class InteractiveTutorialOverlay(QWidget):
    """
    Interactive tutorial overlay that provides real-time guidance with the actual UI.

    Features:
    - Step-by-step instructions with copy-paste examples
    - Real-time validation of user actions
    - Visual highlighting of target elements
    - Progress tracking and navigation
    - Non-blocking interaction with underlying UI elements
    """

    step_completed = Signal()
    tutorial_cancelled = Signal()
    next_step_requested = Signal()
    previous_step_requested = Signal()
    copy_to_clipboard = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Use a completely transparent overlay that doesn't capture mouse events
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # Make entire overlay transparent to mouse
        self.setStyleSheet("background: transparent;")

        self.current_step = None
        self.target_widget = None
        self.target_rect = QRect()
        self.step_number = 0
        self.total_steps = 0

        # Create separate floating instruction panel
        self.floating_panel = None

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self):
        """Setup the interactive tutorial UI with floating panel."""
        # The overlay itself is now completely transparent and non-blocking
        # All UI elements will be in a separate floating panel
        pass

    def _create_floating_instruction_panel(self):
        """Create a draggable floating instruction panel that doesn't block interaction."""
        if self.floating_panel:
            self.floating_panel.close()

        # Create a separate top-level widget for the instruction panel
        self.floating_panel = QWidget(None)  # No parent to make it truly independent
        self.floating_panel.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # Makes it a tool window that doesn't block interaction
        )
        self.floating_panel.setAttribute(Qt.WA_TranslucentBackground)

        # Variables for dragging functionality
        self.floating_panel.dragging = False
        self.floating_panel.drag_start_position = None

        # Main instruction panel with modern design
        self.instruction_panel = QFrame(self.floating_panel)
        self.instruction_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.98);
                border: none;
                border-radius: 12px;
                padding: 0px;
            }
        """)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.instruction_panel.setGraphicsEffect(shadow)

        # Panel layout
        panel_layout = QVBoxLayout(self.instruction_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)  # No margins - header will provide spacing
        panel_layout.setSpacing(0)  # No spacing - individual elements will provide spacing

        # Draggable header with step progress
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #007bff;
                border-radius: 8px 8px 0px 0px;
                padding: 8px;
            }
        """)
        self.header_frame.setCursor(Qt.OpenHandCursor)  # Indicate draggable area

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Drag handle icon
        drag_icon = QLabel("⋮⋮")
        drag_icon.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(drag_icon)

        self.step_indicator = QLabel("Step 1 of 10")
        self.step_indicator.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        header_layout.addWidget(self.step_indicator)

        header_layout.addStretch()

        # Move handle text
        move_label = QLabel("📌 Drag to move")
        move_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 10px;
                font-weight: 500;
            }
        """)
        header_layout.addWidget(move_label)

        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        self.close_btn.clicked.connect(self.tutorial_cancelled.emit)
        header_layout.addWidget(self.close_btn)

        panel_layout.addWidget(self.header_frame)

        # Content area with proper spacing
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #ecf0f1;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        content_layout.addWidget(self.progress_bar)

        # Step title
        self.step_title = QLabel()
        self.step_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: 600;
                margin: 10px 0px 5px 0px;
            }
        """)
        self.step_title.setWordWrap(True)
        content_layout.addWidget(self.step_title)

        # Step description
        self.step_description = QTextEdit()
        self.step_description.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                line-height: 1.5;
            }
        """)
        self.step_description.setReadOnly(True)
        self.step_description.setMaximumHeight(100)
        content_layout.addWidget(self.step_description)

        # Copy-paste section (hidden by default)
        self.copy_paste_frame = QFrame()
        self.copy_paste_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #28a745;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.copy_paste_frame.setVisible(False)

        copy_layout = QVBoxLayout(self.copy_paste_frame)
        copy_layout.setContentsMargins(10, 10, 10, 10)

        self.copy_paste_label = QLabel("📋 Copy this text:")
        self.copy_paste_label.setStyleSheet("font-weight: 600; color: #28a745;")
        copy_layout.addWidget(self.copy_paste_label)

        self.copy_paste_text = QTextEdit()
        self.copy_paste_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #2c3e50;
                border: 2px solid #28a745;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                font-weight: 500;
                padding: 8px;
                line-height: 1.4;
            }
        """)
        self.copy_paste_text.setMaximumHeight(80)
        self.copy_paste_text.setReadOnly(True)
        copy_layout.addWidget(self.copy_paste_text)

        # Copy button
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        copy_layout.addWidget(self.copy_btn)

        content_layout.addWidget(self.copy_paste_frame)

        # Instruction text - limit height to ensure buttons are visible
        self.instruction_text = QTextEdit()
        self.instruction_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
                padding: 10px;
                line-height: 1.4;
            }
        """)
        self.instruction_text.setReadOnly(True)
        self.instruction_text.setMaximumHeight(100)  # Reduced height to ensure buttons fit
        self.instruction_text.setMinimumHeight(80)
        content_layout.addWidget(self.instruction_text)

        # Action buttons with proper spacing
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(10)

        self.previous_btn = QPushButton("← Previous")
        self.previous_btn.setMinimumSize(100, 35)
        self.previous_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
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

        button_layout.addStretch()

        self.skip_btn = QPushButton("Skip Tutorial")
        self.skip_btn.setMinimumSize(100, 35)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 2px solid #6c757d;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6c757d;
                color: #ffffff;
                border-color: #6c757d;
            }
        """)
        self.skip_btn.clicked.connect(self.tutorial_cancelled.emit)
        button_layout.addWidget(self.skip_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setMinimumSize(100, 35)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.next_btn.clicked.connect(self.next_step_requested.emit)
        button_layout.addWidget(self.next_btn)

        content_layout.addLayout(button_layout)

        # Add content frame to main panel
        panel_layout.addWidget(content_frame)

        # Position the panel - make it appropriately sized
        self.instruction_panel.setMinimumSize(400, 450)
        self.instruction_panel.setMaximumSize(550, 600)
        self.instruction_panel.resize(480, 500)  # Default size

        # Debug: Ensure buttons are visible
        print(f"Tutorial buttons created: Previous={self.previous_btn.isVisible()}, Skip={self.skip_btn.isVisible()}, Next={self.next_btn.isVisible()}")
        self.previous_btn.show()
        self.skip_btn.show()
        self.next_btn.show()

        # Install event filter for dragging functionality
        self.header_frame.installEventFilter(self)
        self.floating_panel.installEventFilter(self)

    def _setup_animations(self):
        """Setup animations for smooth transitions."""
        self.highlight_animation = QPropertyAnimation(self, b"geometry")
        self.highlight_animation.setDuration(500)
        self.highlight_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Pulse animation timer
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_highlight)
        self.pulse_timer.setInterval(1000)

    def show_step(self, step: InteractiveTutorialStep, target_widget: QWidget = None,
                  step_number: int = 1, total_steps: int = 1):
        """Show an interactive tutorial step with copy-paste examples."""
        self.current_step = step
        self.target_widget = target_widget
        self.step_number = step_number
        self.total_steps = total_steps

        # Debug logging for target widget identification
        print(f"🎯 Tutorial Step {step_number}: {step.title}")
        print(f"   Target element: {step.target_element}")
        if target_widget:
            print(f"   ✅ Target widget found: {target_widget.__class__.__name__} - {target_widget.objectName()}")
            print(f"   📍 Widget visible: {target_widget.isVisible()}")
            print(f"   📐 Widget geometry: {target_widget.geometry()}")
        else:
            print(f"   ❌ No target widget provided for element: {step.target_element}")

        # Create the floating panel if it doesn't exist
        if not self.floating_panel:
            self._create_floating_instruction_panel()

        # Update UI elements
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

        # Position overlay and panel
        if self.parent():
            self.setGeometry(self.parent().rect())

        # Calculate target rectangle and position floating panel
        if target_widget:
            print(f"   🎨 Calculating target rectangle for highlighting...")
            self._calculate_target_rect(target_widget)
            print(f"   📍 Target rect: {self.target_rect}")
            self._position_floating_panel()
            self._start_highlight_animation()
        else:
            print(f"   ⚠️ No target widget - centering panel")
            self._center_floating_panel()

        # Show both the overlay (for highlighting) and the floating panel
        self.show()
        self.floating_panel.show()
        self.floating_panel.raise_()  # Bring to front

    def _copy_to_clipboard(self):
        """Copy the current copy-paste data to clipboard and optionally auto-fill target field."""
        if self.current_step and self.current_step.copy_paste_data:
            # Copy to clipboard
            QApplication.clipboard().setText(self.current_step.copy_paste_data)

            # Try to auto-fill the target field if it's a text input
            if self.target_widget and self.current_step.action_type == "copy_paste":
                self._auto_fill_target_field(self.target_widget, self.current_step.copy_paste_data)

            self.copy_btn.setText("✅ Copied & Filled!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy to Clipboard"))

    def _auto_fill_target_field(self, widget, text):
        """Automatically fill the target field with the provided text."""
        if not widget or not text:
            return

        try:
            print(f"🔧 Auto-filling widget: {widget.__class__.__name__} - {widget.objectName()} with: {text}")

            # Handle different types of input widgets
            if hasattr(widget, 'setText'):
                # QLineEdit, QTextEdit, etc.
                widget.setText(text)
                widget.setFocus()  # Give focus to the field
                print(f"   ✅ Used setText() method")
            elif hasattr(widget, 'setPlainText'):
                # QTextEdit with plain text
                widget.setPlainText(text)
                widget.setFocus()
                print(f"   ✅ Used setPlainText() method")
            elif hasattr(widget, 'insertPlainText'):
                # Insert text at cursor position
                widget.insertPlainText(text)
                widget.setFocus()
                print(f"   ✅ Used insertPlainText() method")

            # Trigger any change events to ensure the data is saved to the workflow
            if hasattr(widget, 'textChanged'):
                widget.textChanged.emit()
                print(f"   ✅ Triggered textChanged signal")

            # Additional signal triggers for different widget types
            if hasattr(widget, 'editingFinished'):
                widget.editingFinished.emit()
                print(f"   ✅ Triggered editingFinished signal")

            # Force a repaint to show the change
            widget.update()

            # Validate that the text was actually set
            current_text = ""
            if hasattr(widget, 'text'):
                current_text = widget.text()
            elif hasattr(widget, 'toPlainText'):
                current_text = widget.toPlainText()

            if current_text == text:
                print(f"✅ Auto-filled field successfully verified: {text}")
            else:
                print(f"⚠️ Auto-fill verification failed. Expected: '{text}', Got: '{current_text}'")

        except Exception as e:
            print(f"⚠️ Could not auto-fill field: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to just copying to clipboard
            pass

    def _calculate_target_rect(self, target_widget: QWidget):
        """Calculate the target rectangle for highlighting."""
        if target_widget and target_widget.parent():
            self.target_rect = target_widget.geometry()
            # Convert to global coordinates relative to overlay
            global_pos = target_widget.parent().mapToGlobal(self.target_rect.topLeft())
            local_pos = self.mapFromGlobal(global_pos)
            self.target_rect.moveTo(local_pos)
        else:
            self.target_rect = QRect()

    def _position_floating_panel(self):
        """Position the floating instruction panel optimally to avoid covering target elements."""
        if not self.floating_panel or not self.target_rect.isValid():
            self._center_floating_panel()
            return

        # Get screen geometry for positioning
        screen = QApplication.primaryScreen().geometry()
        if not self.target_widget:
            self._center_floating_panel()
            return

        # Get target widget global position and size
        target_global = self.target_widget.mapToGlobal(self.target_widget.rect().topLeft())
        target_size = self.target_widget.size()
        panel_size = self.floating_panel.size()

        print(f"   📍 Positioning panel - Target: {target_global}, Size: {target_size}")
        print(f"   📐 Panel size: {panel_size}")
        print(f"   🖥️ Screen: {screen}")

        # Define larger margins for better separation
        margin = 50  # Increased from 30 to 50 for better separation

        # Create an expanded "no-go zone" around the target to ensure we don't cover it
        no_go_zone = QRect(
            target_global.x() - margin,
            target_global.y() - margin,
            target_size.width() + 2 * margin,
            target_size.height() + 2 * margin
        )

        print(f"   🚫 No-go zone: {no_go_zone}")

        # Try different positions in order of preference:
        positions_to_try = [
            # 1. Far right of target (preferred)
            (target_global.x() + target_size.width() + margin * 2,
             max(margin, target_global.y() - 100)),  # Well above target

            # 2. Far left of target
            (target_global.x() - panel_size.width() - margin * 2,
             max(margin, target_global.y() - 100)),

            # 3. Well above target
            (max(margin, target_global.x() - (panel_size.width() - target_size.width()) // 2),
             target_global.y() - panel_size.height() - margin * 2),

            # 4. Well below target
            (max(margin, target_global.x() - (panel_size.width() - target_size.width()) // 2),
             target_global.y() + target_size.height() + margin * 2),

            # 5. Top-left corner
            (margin, margin),

            # 6. Top-right corner
            (screen.right() - panel_size.width() - margin, margin),

            # 7. Bottom-left corner
            (margin, screen.bottom() - panel_size.height() - margin),

            # 8. Bottom-right corner
            (screen.right() - panel_size.width() - margin,
             screen.bottom() - panel_size.height() - margin)
        ]

        panel_x, panel_y = None, None

        for i, (test_x, test_y) in enumerate(positions_to_try):
            # Ensure position is within screen bounds
            test_x = max(margin, min(test_x, screen.right() - panel_size.width() - margin))
            test_y = max(margin, min(test_y, screen.bottom() - panel_size.height() - margin))

            # Create panel rect at this position
            panel_rect = QRect(test_x, test_y, panel_size.width(), panel_size.height())

            # Check if panel would intersect with the no-go zone
            if not panel_rect.intersects(no_go_zone):
                panel_x, panel_y = test_x, test_y
                print(f"   ✅ Position {i+1} works: ({panel_x}, {panel_y}) - no intersection with target")
                break
            else:
                print(f"   ❌ Position {i+1} rejected: ({test_x}, {test_y}) - would cover target")

        # If no position worked, use the farthest corner from target
        if panel_x is None:
            # Calculate distance to each corner and pick the farthest
            target_center_x = target_global.x() + target_size.width() // 2
            target_center_y = target_global.y() + target_size.height() // 2

            corners = [
                (margin, margin),  # Top-left
                (screen.right() - panel_size.width() - margin, margin),  # Top-right
                (margin, screen.bottom() - panel_size.height() - margin),  # Bottom-left
                (screen.right() - panel_size.width() - margin,
                 screen.bottom() - panel_size.height() - margin)  # Bottom-right
            ]

            max_distance = 0
            best_corner = corners[0]

            for corner_x, corner_y in corners:
                distance = ((corner_x - target_center_x) ** 2 + (corner_y - target_center_y) ** 2) ** 0.5
                if distance > max_distance:
                    max_distance = distance
                    best_corner = (corner_x, corner_y)

            panel_x, panel_y = best_corner
            print(f"   ⚠️ Using farthest corner fallback: ({panel_x}, {panel_y})")

        print(f"   📌 Final position: ({panel_x}, {panel_y})")
        self.floating_panel.move(panel_x, panel_y)

    def _center_floating_panel(self):
        """Center the floating instruction panel on screen."""
        if not self.floating_panel:
            return

        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        center_x = (screen.width() - self.floating_panel.width()) // 2
        center_y = (screen.height() - self.floating_panel.height()) // 2
        self.floating_panel.move(center_x, center_y)

    def _start_highlight_animation(self):
        """Start the highlight animation for the target element."""
        if self.target_rect.isValid():
            self.pulse_timer.start()

    def _pulse_highlight(self):
        """Create a pulsing highlight effect."""
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """Paint the overlay with target highlighting - non-blocking version."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Only draw highlight border around target area, no blocking overlay
        if self.target_rect.isValid():
            # Draw multiple layers for a very prominent green highlight

            # Outer glow layers for maximum visibility
            for i in range(4):
                glow_color = QColor("#28a745")
                glow_color.setAlpha(max(30, 80 - i * 15))  # Fade out for outer layers
                pen_glow = QPen(glow_color, 6 + i * 2)
                painter.setPen(pen_glow)
                painter.setBrush(QBrush(Qt.NoBrush))

                # Expand rect for each glow layer
                glow_rect = self.target_rect.adjusted(-i*3, -i*3, i*3, i*3)
                painter.drawRoundedRect(glow_rect, 8, 8)

            # Main highlight border - very prominent
            highlight_color = QColor("#28a745")
            highlight_color.setAlpha(255)  # Fully opaque for main border

            pen = QPen(highlight_color, 5)  # Thicker border for better visibility
            pen.setStyle(Qt.SolidLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRoundedRect(self.target_rect, 8, 8)

            # Inner highlight for extra emphasis
            inner_color = QColor("#34ce57")  # Lighter green
            inner_color.setAlpha(180)
            inner_pen = QPen(inner_color, 2)
            painter.setPen(inner_pen)

            inner_rect = self.target_rect.adjusted(3, 3, -3, -3)
            painter.drawRoundedRect(inner_rect, 5, 5)

    def mousePressEvent(self, event):
        """Handle mouse press events - allow interaction with underlying UI."""
        # Check if click is on instruction panel
        if self.instruction_panel.geometry().contains(event.pos()):
            # Let the instruction panel handle the event
            super().mousePressEvent(event)
        else:
            # Pass the event to the underlying widget
            event.ignore()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events - allow interaction with underlying UI."""
        # Check if click is on instruction panel
        if self.instruction_panel.geometry().contains(event.pos()):
            # Let the instruction panel handle the event
            super().mouseReleaseEvent(event)
        else:
            # Pass the event to the underlying widget
            event.ignore()

    def mouseMoveEvent(self, event):
        """Handle mouse move events - allow interaction with underlying UI."""
        # Check if move is over instruction panel
        if self.instruction_panel.geometry().contains(event.pos()):
            # Let the instruction panel handle the event
            super().mouseMoveEvent(event)
        else:
            # Pass the event to the underlying widget
            event.ignore()

    def eventFilter(self, obj, event):
        """Handle events for dragging functionality."""
        try:
            from PySide6.QtCore import QEvent

            if obj == self.header_frame and self.floating_panel and hasattr(self.floating_panel, 'dragging'):
                if event.type() == QEvent.MouseButtonPress:
                    if event.button() == Qt.LeftButton:
                        self.floating_panel.dragging = True
                        self.floating_panel.drag_start_position = event.globalPos() - self.floating_panel.pos()
                        self.header_frame.setCursor(Qt.ClosedHandCursor)
                        print("   🖱️ Started dragging tutorial panel")
                        return True
                elif event.type() == QEvent.MouseMove:
                    if getattr(self.floating_panel, 'dragging', False) and event.buttons() == Qt.LeftButton:
                        new_pos = event.globalPos() - self.floating_panel.drag_start_position
                        self.floating_panel.move(new_pos)
                        return True
                elif event.type() == QEvent.MouseButtonRelease:
                    if event.button() == Qt.LeftButton:
                        self.floating_panel.dragging = False
                        self.header_frame.setCursor(Qt.OpenHandCursor)
                        print("   🖱️ Stopped dragging tutorial panel")
                        return True
        except Exception as e:
            print(f"   ❌ Event filter error: {e}")

        return super().eventFilter(obj, event)

    def hide_tutorial(self):
        """Hide the tutorial overlay and floating panel."""
        self.pulse_timer.stop()
        self.hide()
        if self.floating_panel:
            self.floating_panel.hide()
            self.floating_panel.close()
            self.floating_panel = None


class InteractiveTutorialManager:
    """
    Manages interactive tutorials that work directly with the main application.

    Features:
    - Real-time UI interaction
    - Copy-paste examples
    - Step validation
    - Progress tracking
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_tutorial = None
        self.current_step_index = 0
        self.tutorial_overlay = None
        self.tutorials = {}

        self._initialize_tutorials()

    def _initialize_tutorials(self):
        """Initialize interactive tutorials."""

        # Basic Interactive Workflow Tutorial
        basic_steps = [
            InteractiveTutorialStep(
                title="Welcome to Interactive Workflow Creation",
                description="Learn by doing! This tutorial guides you through creating a real workflow in the application.",
                instruction="🎯 <b>What you'll learn:</b><br>• Adding and configuring action steps<br>• Working with JSON data<br>• Using the JSON Path Selector<br>• Creating processing scripts<br>• Generating YAML workflows<br><br>📝 <b>You'll create:</b> A user lookup workflow that fetches user data and processes it with a script.",
                action_type="info"
            ),
            InteractiveTutorialStep(
                title="Step 1: Add Your First Action Step",
                description="Let's start by adding an action step to your workflow.",
                instruction="Look at the left panel and click the <b>'➕ Add Action'</b> button. This will create a new action step that can call APIs or services.",
                target_element="add_action_btn",
                action_type="click"
            ),
            InteractiveTutorialStep(
                title="Step 2: Configure the Action Name",
                description="Now we'll configure the action to fetch user information.",
                instruction="In the center panel, you should see the action configuration. In the <b>'Action Name'</b> field, copy and paste the text below:",
                target_element="action_name_edit",
                action_type="copy_paste",
                copy_paste_data="mw.get_user_by_email"
            ),
            InteractiveTutorialStep(
                title="Step 3: Set the Output Key",
                description="The output key determines how we'll reference this step's data later.",
                instruction="In the <b>'Output Key'</b> field, copy and paste the text below. This will let us access the user data as 'data.user_info' in later steps:",
                target_element="output_key_edit",
                action_type="copy_paste",
                copy_paste_data="user_info"
            ),
            InteractiveTutorialStep(
                title="Step 4: Add Input Arguments",
                description="Input arguments tell the action what data to use.",
                instruction="Scroll down to the <b>'Input Arguments'</b> section and click <b>'Add Argument'</b>. We'll add an email parameter for the user lookup.",
                target_element="add_input_arg_btn",
                action_type="click"
            ),
            InteractiveTutorialStep(
                title="Step 5: Configure the Email Argument",
                description="Set up the email parameter for the user lookup.",
                instruction="In the new argument row:<br>• <b>Key:</b> email<br>• <b>Value:</b> data.input_email<br><br>This tells the action to use the email from the workflow's input data.",
                action_type="type",
                copy_paste_data="email"
            ),
            InteractiveTutorialStep(
                title="Step 6: Add Sample JSON Output",
                description="Providing sample JSON helps with data selection in later steps.",
                instruction="Scroll down to the <b>'JSON Output'</b> section and paste the sample JSON below. This represents what the API would return:",
                target_element="json_output_edit",
                action_type="copy_paste",
                copy_paste_data='{\n  "user": {\n    "id": "emp_12345",\n    "name": "John Doe",\n    "email": "john.doe@company.com",\n    "department": "Engineering",\n    "manager": {\n      "name": "Jane Smith",\n      "email": "jane.smith@company.com"\n    },\n    "permissions": ["read", "write", "admin"]\n  }\n}'
            ),
            InteractiveTutorialStep(
                title="Step 7: Parse the JSON Data",
                description="Make the JSON data available for selection in other steps.",
                instruction="Click the <b>'Parse & Save JSON Output'</b> button. This processes the JSON and makes it available in the JSON Path Selector.",
                target_element="parse_json_btn",
                action_type="click"
            ),
            InteractiveTutorialStep(
                title="Step 8: View Your YAML",
                description="See the YAML that's been generated from your action step.",
                instruction="Look at the right panel and click the <b>'📄 YAML Preview'</b> tab. You'll see the YAML representation of your action step with the configuration you just entered.",
                target_element="yaml_preview_tab",
                action_type="highlight"
            ),
            InteractiveTutorialStep(
                title="Step 9: Add a Script Step",
                description="Now let's add a script step to process the user data.",
                instruction="Go back to the left panel and click <b>'➕ Add Script'</b>. Script steps let you process data using Python-like code.",
                target_element="add_script_btn",
                action_type="click"
            ),
            InteractiveTutorialStep(
                title="Step 10: Open the JSON Path Selector",
                description="Use the JSON Path Selector to choose data from the previous step.",
                instruction="In the right panel, click the <b>'🔍 JSON Explorer'</b> tab. This shows all available data from previous steps that you can use in your script.",
                target_element="json_explorer_tab",
                action_type="click"
            ),
            InteractiveTutorialStep(
                title="Step 11: Explore Available Data",
                description="See the data structure from your action step.",
                instruction="In the JSON Explorer, you should see the data from Step 1. Expand the tree to explore:<br>• <b>user_info</b> → <b>user</b> → <b>name</b><br><br>Click on different items to see their paths. Notice how paths like <b>'data.user_info.user.name'</b> appear.",
                target_element="json_tree",
                action_type="highlight"
            ),
            InteractiveTutorialStep(
                title="Step 12: Write Your Processing Script",
                description="Create a script that uses the selected data.",
                instruction="Go back to the center panel (Configuration tab) and in the <b>'Script Code'</b> area, paste the script below. This script extracts the user's name and creates a greeting:",
                target_element="script_code_edit",
                action_type="copy_paste",
                copy_paste_data="# Extract user information\nuser_name = data.user_info.user.name\nuser_email = data.user_info.user.email\nuser_dept = data.user_info.user.department\n\n# Create a greeting message\ngreeting = f\"Hello, {user_name}!\"\nsummary = f\"User {user_name} from {user_dept} department\"\n\n# Return processed data\nreturn {\n    \"greeting\": greeting,\n    \"user_name\": user_name,\n    \"user_email\": user_email,\n    \"summary\": summary\n}"
            ),
            InteractiveTutorialStep(
                title="Step 13: Set Script Output Key",
                description="Set the output key for your script step.",
                instruction="In the <b>'Output Key'</b> field for the script, paste the text below:",
                target_element="script_output_key_edit",
                action_type="copy_paste",
                copy_paste_data="greeting_result"
            ),
            InteractiveTutorialStep(
                title="Step 14: View Your Complete Workflow",
                description="See the complete YAML for your two-step workflow.",
                instruction="Click the <b>'📄 YAML Preview'</b> tab again. You now have a complete workflow with:<br>• An action step that fetches user data<br>• A script step that processes the data<br><br>This YAML can be used directly in Moveworks!",
                target_element="yaml_preview_tab",
                action_type="highlight"
            ),
            InteractiveTutorialStep(
                title="Congratulations! 🎉",
                description="You've successfully created your first interactive workflow!",
                instruction="<b>What you accomplished:</b><br>✅ Created an action step with proper configuration<br>✅ Added input arguments and sample JSON<br>✅ Used the JSON Path Selector to explore data<br>✅ Wrote a processing script using selected data paths<br>✅ Generated a complete, valid YAML workflow<br><br><b>Next steps:</b><br>• Try the Advanced Tutorial for multi-step workflows<br>• Explore the Template Library for more examples<br>• Create your own workflows using what you've learned!",
                action_type="info"
            )
        ]

        self.tutorials["interactive_basic"] = {
            "title": "Interactive Basic Workflow",
            "description": "Learn by doing - create a real workflow step by step",
            "difficulty": "Beginner",
            "estimated_time": "12 minutes",
            "steps": basic_steps
        }

    def start_tutorial(self, tutorial_id: str) -> bool:
        """Start an interactive tutorial."""
        if tutorial_id not in self.tutorials:
            return False

        self.current_tutorial = self.tutorials[tutorial_id]
        self.current_step_index = 0

        # Create tutorial overlay
        self.tutorial_overlay = InteractiveTutorialOverlay(self.main_window)
        self.tutorial_overlay.next_step_requested.connect(self._next_step)
        self.tutorial_overlay.previous_step_requested.connect(self._previous_step)
        self.tutorial_overlay.tutorial_cancelled.connect(self._cancel_tutorial)

        # Start first step
        self._show_current_step()
        return True

    def _show_current_step(self):
        """Show the current tutorial step."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial["steps"]):
            self._complete_tutorial()
            return

        step = self.current_tutorial["steps"][self.current_step_index]

        # Special handling for JSON Explorer steps
        if step.title == "Step 10: Open the JSON Path Selector":
            self._activate_json_explorer_tab()
        elif step.title == "Step 11: Explore Available Data":
            self._ensure_json_tree_populated()

        target_widget = self._find_target_widget(step.target_element)

        self.tutorial_overlay.show_step(
            step,
            target_widget,
            self.current_step_index + 1,
            len(self.current_tutorial["steps"])
        )

    def _find_target_widget(self, target_element: Optional[str]):
        """Find the target widget in the main application."""
        if not target_element:
            return None

        print(f"🔍 Looking for target element: {target_element}")

        # Try to find widget by object name first
        widget = self.main_window.findChild(QWidget, target_element)
        if widget:
            print(f"   ✅ Found by object name: {widget.__class__.__name__}")
            return widget

        # Enhanced widget mapping with better fallback strategies
        widget_map = {
            "add_action_btn": self._find_add_action_button(),
            "add_script_btn": self._find_add_script_button(),
            "action_name_edit": self._find_action_name_field(),
            "output_key_edit": self._find_output_key_field(),
            "add_input_arg_btn": self._find_in_config_panel("add_input_arg_btn"),
            "json_output_edit": self._find_json_output_field(),
            "parse_json_btn": self._find_parse_json_button(),
            "script_code_edit": self._find_script_code_field(),
            "script_output_key_edit": self._find_script_output_key_field(),
            "yaml_preview_tab": self._find_tab("📄 YAML Preview"),
            "json_explorer_tab": self._find_tab("🔍 JSON Explorer"),
            "json_tree": self._find_json_tree_widget()
        }

        found_widget = widget_map.get(target_element)

        if found_widget:
            print(f"   ✅ Found by widget map: {found_widget.__class__.__name__} - {found_widget.objectName()}")
        else:
            print(f"   ❌ Widget not found in map for: {target_element}")
            # Debug: List available widgets in config panel
            if hasattr(self.main_window, 'config_panel'):
                print(f"   📋 Available config panel widgets:")
                for attr_name in dir(self.main_window.config_panel):
                    if not attr_name.startswith('_'):
                        attr_value = getattr(self.main_window.config_panel, attr_name, None)
                        if hasattr(attr_value, 'objectName'):
                            print(f"      - {attr_name}: {attr_value.__class__.__name__} ({attr_value.objectName()})")

        # Ensure the widget is accessible for interaction
        if found_widget:
            if hasattr(found_widget, 'setEnabled'):
                found_widget.setEnabled(True)
            if hasattr(found_widget, 'show'):
                found_widget.show()
            # Bring the widget to front if it's in a tab
            self._ensure_widget_visible(found_widget)

        return found_widget

    def _find_in_config_panel(self, widget_name: str):
        """Find a widget in the configuration panel."""
        if hasattr(self.main_window, 'config_panel'):
            return getattr(self.main_window.config_panel, widget_name, None)
        return None

    def _find_add_action_button(self):
        """Find the Add Action button with multiple fallback strategies."""
        # Try direct attribute access first
        if hasattr(self.main_window, 'add_action_btn'):
            return self.main_window.add_action_btn

        # Try workflow list panel
        if hasattr(self.main_window, 'workflow_list'):
            if hasattr(self.main_window.workflow_list, 'add_action_btn'):
                return self.main_window.workflow_list.add_action_btn

        # Try findChild with various names
        for name in ['add_action_btn', 'addActionBtn', 'add_action_button']:
            widget = self.main_window.findChild(QWidget, name)
            if widget:
                return widget

        print(f"   ❌ Could not find Add Action button")
        return None

    def _find_add_script_button(self):
        """Find the Add Script button with multiple fallback strategies."""
        # Try direct attribute access first
        if hasattr(self.main_window, 'add_script_btn'):
            return self.main_window.add_script_btn

        # Try workflow list panel
        if hasattr(self.main_window, 'workflow_list'):
            if hasattr(self.main_window.workflow_list, 'add_script_btn'):
                return self.main_window.workflow_list.add_script_btn

        # Try findChild with various names
        for name in ['add_script_btn', 'addScriptBtn', 'add_script_button']:
            widget = self.main_window.findChild(QWidget, name)
            if widget:
                return widget

        print(f"   ❌ Could not find Add Script button")
        return None

    def _find_action_name_field(self):
        """Find the action name field with enhanced search."""
        # Try config panel first
        if hasattr(self.main_window, 'config_panel'):
            for attr_name in ['action_name_edit', 'actionNameEdit', 'action_name_field']:
                widget = getattr(self.main_window.config_panel, attr_name, None)
                if widget:
                    print(f"   ✅ Found action name field in config panel: {attr_name}")
                    return widget

        # Try findChild with various names
        for name in ['action_name_edit', 'actionNameEdit', 'action_name_field']:
            widget = self.main_window.findChild(QWidget, name)
            if widget:
                print(f"   ✅ Found action name field by findChild: {name}")
                return widget

        print(f"   ❌ Could not find action name field")
        return None

    def _find_json_output_field(self):
        """Find the JSON output field with enhanced search."""
        # Try config panel first
        if hasattr(self.main_window, 'config_panel'):
            for attr_name in ['json_output_edit', 'jsonOutputEdit', 'json_output_field']:
                widget = getattr(self.main_window.config_panel, attr_name, None)
                if widget:
                    print(f"   ✅ Found JSON output field in config panel: {attr_name}")
                    return widget

        # Try findChild with various names
        for name in ['json_output_edit', 'jsonOutputEdit', 'json_output_field']:
            widget = self.main_window.findChild(QWidget, name)
            if widget:
                print(f"   ✅ Found JSON output field by findChild: {name}")
                return widget

        print(f"   ❌ Could not find JSON output field")
        return None

    def _find_parse_json_button(self):
        """Find the Parse JSON button with enhanced search."""
        # Try config panel first
        if hasattr(self.main_window, 'config_panel'):
            for attr_name in ['parse_json_btn', 'parseJsonBtn', 'parse_json_button']:
                widget = getattr(self.main_window.config_panel, attr_name, None)
                if widget:
                    print(f"   ✅ Found parse JSON button in config panel: {attr_name}")
                    return widget

        # Try findChild with various names
        for name in ['parse_json_btn', 'parseJsonBtn', 'parse_json_button']:
            widget = self.main_window.findChild(QWidget, name)
            if widget:
                print(f"   ✅ Found parse JSON button by findChild: {name}")
                return widget

        print(f"   ❌ Could not find parse JSON button")
        return None

    def _find_script_code_field(self):
        """Find the script code field with enhanced search."""
        # Try config panel first
        if hasattr(self.main_window, 'config_panel'):
            for attr_name in ['script_code_edit', 'scriptCodeEdit', 'script_code_field']:
                widget = getattr(self.main_window.config_panel, attr_name, None)
                if widget:
                    print(f"   ✅ Found script code field in config panel: {attr_name}")
                    return widget

        # Try findChild with various names
        for name in ['script_code_edit', 'scriptCodeEdit', 'script_code_field']:
            widget = self.main_window.findChild(QWidget, name)
            if widget:
                print(f"   ✅ Found script code field by findChild: {name}")
                return widget

        print(f"   ❌ Could not find script code field")
        return None

    def _ensure_widget_visible(self, widget):
        """Ensure the widget is visible by activating its parent tabs if needed."""
        if not widget:
            return

        # Walk up the parent hierarchy to find and activate tabs
        parent = widget.parent()
        while parent:
            # Check if parent is a tab widget and activate the correct tab
            if hasattr(parent, 'indexOf') and hasattr(parent, 'setCurrentIndex'):
                try:
                    # Find which tab contains this widget
                    for i in range(parent.count()):
                        tab_widget = parent.widget(i)
                        if self._is_widget_descendant(widget, tab_widget):
                            parent.setCurrentIndex(i)
                            break
                except:
                    pass
            parent = parent.parent()

    def _is_widget_descendant(self, widget, potential_ancestor):
        """Check if widget is a descendant of potential_ancestor."""
        if not widget or not potential_ancestor:
            return False

        current = widget
        while current:
            if current == potential_ancestor:
                return True
            current = current.parent()
        return False

    def _find_tab(self, tab_name: str):
        """Find a tab by its name."""
        print(f"   🔍 Searching for tab: {tab_name}")

        # Look for tab widgets in the main window
        tab_widgets = self.main_window.findChildren(QTabWidget)
        print(f"   📋 Found {len(tab_widgets)} tab widgets")

        for tab_widget in tab_widgets:
            for i in range(tab_widget.count()):
                tab_text = tab_widget.tabText(i)
                print(f"      Tab {i}: '{tab_text}'")
                if tab_text == tab_name:
                    print(f"   ✅ Found matching tab: {tab_name}")
                    # Return the tab widget itself, not the tab content
                    # The tutorial will highlight the tab widget
                    return tab_widget

        print(f"   ❌ Tab not found: {tab_name}")
        return None

    def _find_output_key_field(self):
        """Find the output key field for the current step type."""
        print(f"   🔍 Searching for output key field...")

        # Check if we're in action configuration
        if hasattr(self.main_window, 'config_panel'):
            # Try action output key field first
            action_output_key = getattr(self.main_window.config_panel, 'action_output_key_edit', None)
            print(f"      Action output key field: {action_output_key}")
            if action_output_key:
                print(f"      Action output key visible: {action_output_key.isVisible()}")
                if action_output_key.isVisible():
                    print(f"   ✅ Found visible action output key field")
                    return action_output_key

            # Try script output key field
            script_output_key = getattr(self.main_window.config_panel, 'script_output_key_edit', None)
            print(f"      Script output key field: {script_output_key}")
            if script_output_key:
                print(f"      Script output key visible: {script_output_key.isVisible()}")
                if script_output_key.isVisible():
                    print(f"   ✅ Found visible script output key field")
                    return script_output_key

        # Fallback to findChild
        print(f"   🔍 Trying findChild fallback...")
        fallback_widget = self.main_window.findChild(QWidget, "action_output_key_edit") or \
                         self.main_window.findChild(QWidget, "script_output_key_edit") or \
                         self.main_window.findChild(QWidget, "output_key_edit")

        if fallback_widget:
            print(f"   ✅ Found by findChild: {fallback_widget.__class__.__name__} - {fallback_widget.objectName()}")
        else:
            print(f"   ❌ No output key field found")

        return fallback_widget

    def _find_script_output_key_field(self):
        """Find the script output key field specifically."""
        if hasattr(self.main_window, 'config_panel'):
            script_output_key = getattr(self.main_window.config_panel, 'script_output_key_edit', None)
            if script_output_key:
                return script_output_key

        # Fallback to findChild
        return self.main_window.findChild(QWidget, "script_output_key_edit")

    def _find_json_tree_widget(self):
        """Find the JSON tree widget in the enhanced JSON panel."""
        print(f"   🔍 Searching for JSON tree widget...")

        # Check if enhanced_json_panel exists and has json_tree
        if hasattr(self.main_window, 'enhanced_json_panel'):
            enhanced_panel = self.main_window.enhanced_json_panel
            print(f"      Enhanced JSON panel: {enhanced_panel.__class__.__name__}")

            # Check for json_tree attribute
            if hasattr(enhanced_panel, 'json_tree'):
                json_tree = enhanced_panel.json_tree
                print(f"   ✅ Found json_tree: {json_tree.__class__.__name__}")
                return json_tree
            else:
                print(f"      No json_tree attribute found")
                # List available attributes for debugging
                attrs = [attr for attr in dir(enhanced_panel) if not attr.startswith('_') and 'tree' in attr.lower()]
                print(f"      Available tree-related attributes: {attrs}")
        else:
            print(f"      No enhanced_json_panel found")

        # Fallback: search for any QTreeWidget in the main window
        from PySide6.QtWidgets import QTreeWidget
        tree_widgets = self.main_window.findChildren(QTreeWidget)
        print(f"   📋 Found {len(tree_widgets)} tree widgets")

        for tree_widget in tree_widgets:
            print(f"      Tree widget: {tree_widget.__class__.__name__} - {tree_widget.objectName()}")
            # Look for one that might be the JSON tree
            if hasattr(tree_widget, 'populate_from_json') or 'json' in tree_widget.objectName().lower():
                print(f"   ✅ Found JSON tree widget: {tree_widget.__class__.__name__}")
                return tree_widget

        print(f"   ❌ No JSON tree widget found")
        return None

    def _ensure_json_tree_populated(self):
        """Ensure the JSON tree is populated with data for Step 11."""
        print(f"🔄 Ensuring JSON tree is populated for Step 11...")

        # First, make sure we're on the JSON Explorer tab
        json_explorer_tab = self._find_tab("🔍 JSON Explorer")
        if json_explorer_tab:
            # Find the tab widget and activate the JSON Explorer tab
            tab_widgets = self.main_window.findChildren(QTabWidget)
            for tab_widget in tab_widgets:
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "🔍 JSON Explorer":
                        tab_widget.setCurrentIndex(i)
                        print(f"   ✅ Activated JSON Explorer tab")
                        break

        # Get the enhanced JSON panel and update it with the current workflow
        if hasattr(self.main_window, 'enhanced_json_panel'):
            enhanced_panel = self.main_window.enhanced_json_panel
            workflow = self.main_window.workflow_list.workflow

            # Update the JSON panel with the workflow
            if hasattr(enhanced_panel, 'set_workflow'):
                enhanced_panel.set_workflow(workflow, 0)  # Set to first step
                print(f"   ✅ Updated JSON panel with workflow")

            # If there's a step combo, try to select the first step with JSON data
            if hasattr(enhanced_panel, 'step_combo'):
                step_combo = enhanced_panel.step_combo
                if step_combo.count() > 0:
                    # Look for a step with JSON data
                    for i in range(step_combo.count()):
                        item_text = step_combo.itemText(i)
                        if "✅" in item_text:  # Step has JSON data
                            step_combo.setCurrentIndex(i)
                            print(f"   ✅ Selected step with JSON data: {item_text}")
                            break

            # Force update the JSON tree if possible
            if hasattr(enhanced_panel, '_update_json_tree'):
                enhanced_panel._update_json_tree()
                print(f"   ✅ Forced JSON tree update")

        print(f"✅ JSON tree population check complete")

    def _activate_json_explorer_tab(self):
        """Activate the JSON Explorer tab for Step 10."""
        print(f"🔄 Activating JSON Explorer tab for Step 10...")

        # Find and activate the JSON Explorer tab
        tab_widgets = self.main_window.findChildren(QTabWidget)
        for tab_widget in tab_widgets:
            for i in range(tab_widget.count()):
                if tab_widget.tabText(i) == "🔍 JSON Explorer":
                    tab_widget.setCurrentIndex(i)
                    print(f"   ✅ Activated JSON Explorer tab")

                    # Also update the JSON panel with current workflow
                    if hasattr(self.main_window, 'enhanced_json_panel'):
                        enhanced_panel = self.main_window.enhanced_json_panel
                        workflow = self.main_window.workflow_list.workflow
                        if hasattr(enhanced_panel, 'set_workflow'):
                            enhanced_panel.set_workflow(workflow, 1)  # Set to second step (script step)
                            print(f"   ✅ Updated JSON panel for script step")
                    return

        print(f"   ❌ Could not find JSON Explorer tab")

    def _next_step(self):
        """Move to the next tutorial step."""
        # Validate current step before proceeding
        if self._validate_current_step():
            self.current_step_index += 1
            self._show_current_step()
        else:
            # Show validation error message
            self._show_step_validation_error()

    def _previous_step(self):
        """Move to the previous tutorial step."""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._show_current_step()

    def _cancel_tutorial(self):
        """Cancel the current tutorial."""
        if self.tutorial_overlay:
            self.tutorial_overlay.hide_tutorial()
            self.tutorial_overlay = None
        self.current_tutorial = None
        self.current_step_index = 0

    def _validate_current_step(self):
        """Validate that the current tutorial step has been completed correctly."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial["steps"]):
            return True

        step = self.current_tutorial["steps"][self.current_step_index]

        # Skip validation for info and highlight steps
        if step.action_type in ["info", "highlight", "click"]:
            return True

        # Validate copy-paste steps
        if step.action_type == "copy_paste" and step.copy_paste_data:
            return self._validate_copy_paste_step(step)

        return True

    def _validate_copy_paste_step(self, step):
        """Validate that a copy-paste step was completed correctly."""
        target_widget = self._find_target_widget(step.target_element)
        if not target_widget:
            print(f"⚠️ Cannot validate step - target widget not found: {step.target_element}")
            return True  # Allow proceeding if widget not found

        # Get current text from widget
        current_text = ""
        if hasattr(target_widget, 'text'):
            current_text = target_widget.text()
        elif hasattr(target_widget, 'toPlainText'):
            current_text = target_widget.toPlainText()

        # Check if the expected text is present
        expected_text = step.copy_paste_data.strip()
        current_text = current_text.strip()

        if current_text == expected_text:
            print(f"✅ Step validation passed: '{current_text}' matches expected '{expected_text}'")
            return True
        else:
            print(f"❌ Step validation failed: '{current_text}' does not match expected '{expected_text}'")
            return False

    def _show_step_validation_error(self):
        """Show an error message when step validation fails."""
        if not self.current_tutorial or self.current_step_index >= len(self.current_tutorial["steps"]):
            return

        step = self.current_tutorial["steps"][self.current_step_index]

        QMessageBox.warning(
            self.main_window,
            "Step Not Complete",
            f"Please complete the current step before proceeding.\n\n"
            f"Step: {step.title}\n\n"
            f"Make sure to:\n"
            f"• Click the 'Copy to Clipboard' button\n"
            f"• Paste the text into the highlighted field\n"
            f"• Verify the field contains the correct text\n\n"
            f"Expected text: {step.copy_paste_data if step.copy_paste_data else 'N/A'}"
        )

    def _complete_tutorial(self):
        """Complete the current tutorial."""
        if self.tutorial_overlay:
            self.tutorial_overlay.hide_tutorial()
            self.tutorial_overlay = None

        QMessageBox.information(
            self.main_window,
            "Tutorial Complete! 🎉",
            "Congratulations! You've completed the interactive tutorial.\n\n"
            "You now know how to create workflows with the Moveworks YAML Assistant.\n\n"
            "Try creating your own workflows or explore the Template Library for more examples!"
        )

        self.current_tutorial = None
        self.current_step_index = 0

    def get_available_tutorials(self):
        """Get list of available tutorials."""
        return [
            {
                "id": tutorial_id,
                "title": tutorial["title"],
                "description": tutorial["description"],
                "difficulty": tutorial["difficulty"],
                "estimated_time": tutorial["estimated_time"]
            }
            for tutorial_id, tutorial in self.tutorials.items()
        ]
