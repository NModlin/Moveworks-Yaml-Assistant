"""
Smart Suggestions Widget for the Moveworks YAML Assistant.

This module provides intelligent workflow suggestions based on user context,
patterns, and best practices.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGroupBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from typing import List, Optional
from dataclasses import dataclass
from core_structures import Workflow
from smart_suggestions_system import SmartSuggestionsEngine, Suggestion


class SuggestionCard(QFrame):
    """A card widget displaying a single suggestion."""
    
    suggestion_applied = Signal(str)  # suggestion_id
    suggestion_dismissed = Signal(str)  # suggestion_id
    
    def __init__(self, suggestion: Suggestion, parent=None):
        super().__init__(parent)
        self.suggestion = suggestion
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the suggestion card UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 4px;
                padding: 8px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header with title and confidence
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.suggestion.title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Confidence indicator
        confidence_text = f"{int(self.suggestion.confidence * 100)}%"
        confidence_label = QLabel(confidence_text)
        confidence_color = self._get_confidence_color(self.suggestion.confidence)
        confidence_label.setStyleSheet(f"""
            QLabel {{
                background-color: {confidence_color};
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(confidence_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(self.suggestion.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(desc_label)
        
        # Benefits (if any)
        if self.suggestion.benefits:
            benefits_text = "Benefits: " + ", ".join(self.suggestion.benefits)
            benefits_label = QLabel(benefits_text)
            benefits_label.setWordWrap(True)
            benefits_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 11px;
                    font-style: italic;
                }
            """)
            layout.addWidget(benefits_label)
        
        # Time saved indicator
        if self.suggestion.estimated_time_saved > 0:
            time_label = QLabel(f"⏱️ Saves ~{self.suggestion.estimated_time_saved} minutes")
            time_label.setStyleSheet("""
                QLabel {
                    color: #f39c12;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            layout.addWidget(time_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        apply_btn.clicked.connect(lambda: self.suggestion_applied.emit(self.suggestion.id))
        buttons_layout.addWidget(apply_btn)
        
        dismiss_btn = QPushButton("❌ Dismiss")
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        dismiss_btn.clicked.connect(lambda: self.suggestion_dismissed.emit(self.suggestion.id))
        buttons_layout.addWidget(dismiss_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
    def _get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence level."""
        if confidence >= 0.8:
            return "#27ae60"  # Green
        elif confidence >= 0.6:
            return "#f39c12"  # Orange
        else:
            return "#e74c3c"  # Red


class SmartSuggestionsWidget(QWidget):
    """Widget for displaying smart workflow suggestions."""
    
    suggestion_applied = Signal(str, str)  # suggestion_id, implementation_code
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.suggestions_engine = SmartSuggestionsEngine()
        self.current_suggestions: List[Suggestion] = []
        self.current_workflow: Optional[Workflow] = None
        
        # Debounce timer for workflow updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_suggestions)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the smart suggestions UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_label = QLabel("🧠 Smart Suggestions")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border-radius: 6px;
            }
        """)
        layout.addWidget(header_label)
        
        # Status label
        self.status_label = QLabel("Analyzing workflow...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                font-style: italic;
                padding: 4px 8px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Suggestions scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.suggestions_container = QWidget()
        self.suggestions_layout = QVBoxLayout(self.suggestions_container)
        self.suggestions_layout.setContentsMargins(0, 0, 0, 0)
        self.suggestions_layout.setSpacing(4)
        
        self.scroll_area.setWidget(self.suggestions_container)
        layout.addWidget(self.scroll_area)
        
        # Initially show empty state
        self._show_empty_state()
        
    def set_workflow(self, workflow: Workflow):
        """Set the current workflow and trigger suggestions update."""
        self.current_workflow = workflow
        self.update_timer.start(500)  # 500ms debounce
        
    def _update_suggestions(self):
        """Update suggestions based on current workflow."""
        if not self.current_workflow:
            self._show_empty_state()
            return
            
        self.status_label.setText("Analyzing workflow...")
        
        # Generate suggestions
        try:
            suggestions = self.suggestions_engine.generate_suggestions(self.current_workflow)
            self.current_suggestions = suggestions
            self._display_suggestions(suggestions)
        except Exception as e:
            self.status_label.setText(f"Error generating suggestions: {str(e)}")
            
    def _display_suggestions(self, suggestions: List[Suggestion]):
        """Display the list of suggestions."""
        # Clear existing suggestions
        self._clear_suggestions()
        
        if not suggestions:
            self._show_no_suggestions()
            return
            
        self.status_label.setText(f"Found {len(suggestions)} suggestions")
        
        # Add suggestion cards
        for suggestion in suggestions:
            card = SuggestionCard(suggestion)
            card.suggestion_applied.connect(self._on_suggestion_applied)
            card.suggestion_dismissed.connect(self._on_suggestion_dismissed)
            self.suggestions_layout.addWidget(card)
            
        # Add stretch to push cards to top
        self.suggestions_layout.addStretch()
        
    def _clear_suggestions(self):
        """Clear all suggestion cards."""
        while self.suggestions_layout.count() > 0:
            child = self.suggestions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def _show_empty_state(self):
        """Show empty state when no workflow is available."""
        self._clear_suggestions()
        self.status_label.setText("Create a workflow to see suggestions")
        
        empty_label = QLabel("🤖\n\nStart building your workflow and I'll suggest\nimprovements and next steps!")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 14px;
                padding: 40px;
            }
        """)
        self.suggestions_layout.addWidget(empty_label)
        
    def _show_no_suggestions(self):
        """Show state when no suggestions are available."""
        self._clear_suggestions()
        self.status_label.setText("No suggestions available")
        
        no_suggestions_label = QLabel("✨\n\nYour workflow looks great!\nNo suggestions at this time.")
        no_suggestions_label.setAlignment(Qt.AlignCenter)
        no_suggestions_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 14px;
                padding: 40px;
            }
        """)
        self.suggestions_layout.addWidget(no_suggestions_label)
        
    def _on_suggestion_applied(self, suggestion_id: str):
        """Handle suggestion application."""
        suggestion = next((s for s in self.current_suggestions if s.id == suggestion_id), None)
        if suggestion:
            self.suggestion_applied.emit(suggestion_id, suggestion.implementation_code)
            
    def _on_suggestion_dismissed(self, suggestion_id: str):
        """Handle suggestion dismissal."""
        # Remove the suggestion from display
        for i in range(self.suggestions_layout.count()):
            item = self.suggestions_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, SuggestionCard) and widget.suggestion.id == suggestion_id:
                    widget.deleteLater()
                    break
                    
        # Update status
        remaining_count = len([s for s in self.current_suggestions if s.id != suggestion_id])
        if remaining_count == 0:
            self._show_no_suggestions()
        else:
            self.status_label.setText(f"Found {remaining_count} suggestions")
