"""
Tutorial Integration for Moveworks YAML Assistant.

This module integrates the comprehensive tutorial system with the main application,
providing seamless access to all 5 tutorial modules through the existing UI.
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit, QProgressBar
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from tutorials import UnifiedTutorialManager


class TutorialSelectionWidget(QWidget):
    """Widget for selecting and starting tutorials."""
    
    tutorial_selected = Signal(str)  # tutorial_id
    
    def __init__(self, tutorial_system: ComprehensiveTutorialSystem, parent=None):
        super().__init__(parent)
        self.tutorial_system = tutorial_system
        self.setMinimumSize(800, 550)
        self.resize(900, 650)
        self.setWindowTitle("Moveworks YAML Assistant - Tutorial Selection")
        
        self._setup_ui()
        self._populate_tutorials()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the tutorial selection UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Comprehensive Tutorial Series")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        
        # Description
        desc_label = QLabel("Master Moveworks compound actions through 5 progressive modules")
        desc_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Tutorial list
        self.tutorial_list = QListWidget()
        self.tutorial_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f8f8;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        
        # Tutorial details
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(120)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                padding: 8px;
            }
        """)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Tutorial")
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.close_button)
        controls_layout.addWidget(self.start_button)
        
        # Layout assembly
        layout.addWidget(header_label)
        layout.addWidget(desc_label)
        layout.addWidget(QLabel("Select a tutorial module:"))
        layout.addWidget(self.tutorial_list)
        layout.addWidget(QLabel("Tutorial Details:"))
        layout.addWidget(self.details_text)
        layout.addLayout(controls_layout)
    
    def _populate_tutorials(self):
        """Populate the tutorial list."""
        tutorials = self.tutorial_system.get_available_tutorials()
        
        # Sort tutorials by module order
        module_order = [
            "module_1_basic_compound_action",
            "module_2_it_automation", 
            "module_3_conditional_logic",
            "module_4_data_processing",
            "module_5_error_handling"
        ]
        
        sorted_tutorials = []
        for module_id in module_order:
            for tutorial in tutorials:
                if tutorial.id == module_id:
                    sorted_tutorials.append(tutorial)
                    break
        
        for tutorial in sorted_tutorials:
            item = QListWidgetItem()
            
            # Create tutorial item text
            difficulty_icon = {
                TutorialDifficulty.BEGINNER: "🟢",
                TutorialDifficulty.INTERMEDIATE: "🟡", 
                TutorialDifficulty.ADVANCED: "🔴"
            }.get(tutorial.difficulty, "⚪")
            
            item_text = f"{difficulty_icon} {tutorial.title}\n"
            item_text += f"   {tutorial.description}\n"
            item_text += f"   ⏱️ {tutorial.estimated_time} | 📚 {tutorial.difficulty.value}"
            
            item.setText(item_text)
            item.setData(Qt.UserRole, tutorial.id)
            
            self.tutorial_list.addItem(item)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.tutorial_list.itemSelectionChanged.connect(self._on_tutorial_selected)
        self.start_button.clicked.connect(self._start_selected_tutorial)
        self.close_button.clicked.connect(self.close)
    
    def _on_tutorial_selected(self):
        """Handle tutorial selection."""
        current_item = self.tutorial_list.currentItem()
        if current_item:
            tutorial_id = current_item.data(Qt.UserRole)
            tutorial = None
            
            for t in self.tutorial_system.get_available_tutorials():
                if t.id == tutorial_id:
                    tutorial = t
                    break
            
            if tutorial:
                self._show_tutorial_details(tutorial)
                self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
            self.details_text.clear()
    
    def _show_tutorial_details(self, tutorial: Tutorial):
        """Show detailed information about the selected tutorial."""
        details_html = f"""
        <h3>{tutorial.title}</h3>
        <p><strong>Description:</strong> {tutorial.description}</p>
        <p><strong>Difficulty:</strong> {tutorial.difficulty.value} | <strong>Time:</strong> {tutorial.estimated_time}</p>
        
        <p><strong>Learning Objectives:</strong></p>
        <ul>
        """
        
        for objective in tutorial.learning_objectives:
            details_html += f"<li>{objective}</li>"
        
        details_html += "</ul>"
        
        if tutorial.prerequisites:
            details_html += "<p><strong>Prerequisites:</strong> "
            details_html += ", ".join(tutorial.prerequisites)
            details_html += "</p>"
        
        details_html += f"<p><strong>Steps:</strong> {len(tutorial.steps)} interactive steps</p>"
        
        self.details_text.setHtml(details_html)
    
    def _start_selected_tutorial(self):
        """Start the selected tutorial."""
        current_item = self.tutorial_list.currentItem()
        if current_item:
            tutorial_id = current_item.data(Qt.UserRole)
            self.tutorial_selected.emit(tutorial_id)
            self.close()


class TutorialIntegrationManager:
    """
    Manages integration between the comprehensive tutorial system and main application.
    
    This class provides the interface for the main application to access and launch
    the comprehensive tutorial system.
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.tutorial_system = ComprehensiveTutorialSystem(main_window)
        self.selection_widget: Optional[TutorialSelectionWidget] = None
        
        # Integration with main window
        self._integrate_with_main_window()
    
    def _integrate_with_main_window(self):
        """Integrate tutorial system with main window."""
        # Add tutorial menu items or buttons to main window
        # This would be customized based on the actual main window structure
        pass
    
    def show_tutorial_selection(self):
        """Show the tutorial selection dialog."""
        if not self.selection_widget:
            self.selection_widget = TutorialSelectionWidget(self.tutorial_system, self.main_window)
            self.selection_widget.tutorial_selected.connect(self._start_tutorial)
        
        self.selection_widget.show()
        self.selection_widget.raise_()
        self.selection_widget.activateWindow()
    
    def _start_tutorial(self, tutorial_id: str):
        """Start a specific tutorial."""
        success = self.tutorial_system.start_tutorial(tutorial_id)
        if not success:
            print(f"Failed to start tutorial: {tutorial_id}")
    
    def get_tutorial_system(self) -> ComprehensiveTutorialSystem:
        """Get the tutorial system instance."""
        return self.tutorial_system
    
    def is_tutorial_active(self) -> bool:
        """Check if a tutorial is currently active."""
        return self.tutorial_system.current_tutorial is not None
    
    def get_current_tutorial_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active tutorial."""
        if not self.tutorial_system.current_tutorial:
            return None
        
        tutorial = self.tutorial_system.current_tutorial
        return {
            "id": tutorial.id,
            "title": tutorial.title,
            "current_step": self.tutorial_system.current_step_index + 1,
            "total_steps": len(tutorial.steps),
            "progress": (self.tutorial_system.current_step_index + 1) / len(tutorial.steps) * 100
        }
