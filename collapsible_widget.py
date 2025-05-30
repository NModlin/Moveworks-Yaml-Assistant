#!/usr/bin/env python3
"""
Collapsible Widget for the JSON Path Selector.

This module provides a custom collapsible widget that can expand/collapse
sections to reduce clutter and improve organization.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)


class CollapsibleSection(QWidget):
    """
    A collapsible section widget that can expand/collapse its content.
    
    Features:
    - Animated expand/collapse
    - Custom styling
    - Toggle button with arrow indicator
    - Configurable colors and fonts
    """
    
    # Signal emitted when section is expanded/collapsed
    toggled = Signal(bool)
    
    def __init__(self, title="Section", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.is_expanded = True
        self.content_widget = None
        self.animation = None
        
        self._setup_ui()
        self._setup_animation()
        
    def _setup_ui(self):
        """Setup the collapsible section UI."""
        self.setObjectName("CollapsibleSection")
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header frame
        self.header_frame = QFrame()
        self.header_frame.setObjectName("CollapsibleHeader")
        self.header_frame.setFixedHeight(40)
        self.header_frame.setStyleSheet("""
            QFrame#CollapsibleHeader {
                background-color: #2196f3;
                border: 2px solid #1976d2;
                border-radius: 6px;
                margin: 2px;
            }
            QFrame#CollapsibleHeader:hover {
                background-color: #1976d2;
            }
        """)
        
        # Header layout
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)
        
        # Toggle button (arrow)
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setObjectName("ToggleButton")
        self.toggle_btn.setFixedSize(24, 24)
        self.toggle_btn.clicked.connect(self.toggle)
        self.toggle_btn.setStyleSheet("""
            QPushButton#ToggleButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#ToggleButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        header_layout.addWidget(self.toggle_btn)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setStyleSheet("""
            QLabel#SectionTitle {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Status indicator (optional)
        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 11px;
                background-color: transparent;
            }
        """)
        header_layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(self.header_frame)
        
        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setObjectName("CollapsibleContent")
        self.content_frame.setStyleSheet("""
            QFrame#CollapsibleContent {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-top: none;
                border-radius: 0px 0px 6px 6px;
                margin: 0px 2px 2px 2px;
            }
        """)
        
        # Content layout
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)
        
        self.main_layout.addWidget(self.content_frame)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.gray)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def _setup_animation(self):
        """Setup the expand/collapse animation."""
        self.animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        
    def set_content_widget(self, widget):
        """Set the content widget for this section."""
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)
            
        self.content_widget = widget
        if widget:
            self.content_layout.addWidget(widget)
            
    def set_title(self, title):
        """Set the section title."""
        self.title = title
        self.title_label.setText(title)
        
    def set_status(self, status):
        """Set the status text (appears on the right side of header)."""
        self.status_label.setText(status)
        
    def set_color(self, color):
        """Set the header color."""
        darker_color = color.replace("#", "#").replace("f", "e")  # Simple darkening
        self.header_frame.setStyleSheet(f"""
            QFrame#CollapsibleHeader {{
                background-color: {color};
                border: 2px solid {darker_color};
                border-radius: 6px;
                margin: 2px;
            }}
            QFrame#CollapsibleHeader:hover {{
                background-color: {darker_color};
            }}
        """)
        
    def toggle(self):
        """Toggle the expanded/collapsed state."""
        self.set_expanded(not self.is_expanded)
        
    def set_expanded(self, expanded):
        """Set the expanded state."""
        if self.is_expanded == expanded:
            return
            
        self.is_expanded = expanded
        
        # Update toggle button
        self.toggle_btn.setText("▼" if expanded else "▶")
        
        # Animate content
        if expanded:
            # Expand
            self.content_frame.setMaximumHeight(0)
            self.content_frame.show()
            
            # Calculate target height
            target_height = self.content_widget.sizeHint().height() + 24 if self.content_widget else 50
            
            self.animation.setStartValue(0)
            self.animation.setEndValue(target_height)
        else:
            # Collapse
            current_height = self.content_frame.height()
            self.animation.setStartValue(current_height)
            self.animation.setEndValue(0)
            
        self.animation.finished.connect(self._animation_finished)
        self.animation.start()
        
        # Emit signal
        self.toggled.emit(expanded)
        
    def _animation_finished(self):
        """Handle animation completion."""
        if not self.is_expanded:
            self.content_frame.hide()
        else:
            self.content_frame.setMaximumHeight(16777215)  # Remove height constraint
            
        self.animation.finished.disconnect()
        
    def is_expanded_state(self):
        """Return whether the section is currently expanded."""
        return self.is_expanded


class CollapsibleContainer(QWidget):
    """
    Container widget that manages multiple collapsible sections.
    
    Features:
    - Add/remove sections dynamically
    - Expand/collapse all functionality
    - Section management
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.sections = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the container UI."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
        # Add stretch at the end to push sections to top
        self.layout.addStretch()
        
    def add_section(self, title, content_widget=None, color="#2196f3", expanded=True):
        """Add a new collapsible section."""
        section = CollapsibleSection(title)
        
        if content_widget:
            section.set_content_widget(content_widget)
            
        section.set_color(color)
        section.set_expanded(expanded)
        
        # Insert before the stretch
        self.layout.insertWidget(len(self.sections), section)
        self.sections.append(section)
        
        return section
        
    def remove_section(self, section):
        """Remove a section."""
        if section in self.sections:
            self.sections.remove(section)
            self.layout.removeWidget(section)
            section.deleteLater()
            
    def expand_all(self):
        """Expand all sections."""
        for section in self.sections:
            section.set_expanded(True)
            
    def collapse_all(self):
        """Collapse all sections."""
        for section in self.sections:
            section.set_expanded(False)
            
    def get_section(self, title):
        """Get a section by title."""
        for section in self.sections:
            if section.title == title:
                return section
        return None
        
    def get_sections(self):
        """Get all sections."""
        return self.sections.copy()


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Collapsible Widget Test")
    window.setGeometry(100, 100, 600, 800)
    
    # Create container
    container = CollapsibleContainer()
    
    # Add test sections
    section1_content = QWidget()
    section1_layout = QVBoxLayout(section1_content)
    section1_layout.addWidget(QLabel("This is section 1 content"))
    section1_layout.addWidget(QLineEdit("Test input"))
    section1_layout.addWidget(QPushButton("Test button"))
    
    container.add_section("🔍 Search Section", section1_content, "#4caf50", True)
    
    section2_content = QWidget()
    section2_layout = QVBoxLayout(section2_content)
    section2_layout.addWidget(QLabel("This is section 2 content"))
    section2_layout.addWidget(QLabel("More content here"))
    
    container.add_section("📌 Bookmarks Section", section2_content, "#ff9800", False)
    
    window.setCentralWidget(container)
    window.show()
    
    sys.exit(app.exec())
