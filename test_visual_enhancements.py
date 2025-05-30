#!/usr/bin/env python3
"""
Test script for the enhanced visual design and user flow improvements
in the Moveworks YAML Assistant's JSON Path Selector component.

This script demonstrates:
1. Visual Design Standards (8px margins, #f8f8f8 backgrounds, consistent styling)
2. User Flow Enhancements (auto-population, real-time search, visual feedback)
3. Enhanced JSON Explorer and Preview functionality
"""

import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

# Set up logging to see the enhanced feedback
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import our enhanced components
from enhanced_json_selector import EnhancedJsonPathSelector, VisualDesignConstants
from core_structures import Workflow, ActionStep, ScriptStep


class VisualEnhancementsDemo(QMainWindow):
    """Demo window showcasing the enhanced visual design and user flow improvements."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moveworks YAML Assistant - Enhanced JSON Path Selector Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply consistent visual design
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
            }}
        """)
        
        self._setup_ui()
        self._create_demo_workflow()
        
    def _setup_ui(self):
        """Setup the demo UI with enhanced visual standards."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN)
        layout.setSpacing(VisualDesignConstants.SECTION_SPACING)
        
        # Demo header
        header = QLabel("🎨 Enhanced JSON Path Selector - Visual Design & User Flow Demo")
        header.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {VisualDesignConstants.ACCENT_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                background-color: white;
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 8px;
                margin-bottom: {VisualDesignConstants.SECTION_SPACING}px;
            }}
        """)
        layout.addWidget(header)
        
        # Demo controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(VisualDesignConstants.BUTTON_SPACING)
        
        # Load sample data button
        load_btn = QPushButton("📊 Load Sample Data")
        load_btn.clicked.connect(self._load_sample_data)
        load_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        controls_layout.addWidget(load_btn)
        
        # Test search button
        search_btn = QPushButton("🔍 Test Search Features")
        search_btn.clicked.connect(self._test_search_features)
        search_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        controls_layout.addWidget(search_btn)
        
        # Test visual feedback button
        feedback_btn = QPushButton("✨ Test Visual Feedback")
        feedback_btn.clicked.connect(self._test_visual_feedback)
        feedback_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #388e3c;
            }}
        """)
        controls_layout.addWidget(feedback_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Enhanced JSON Path Selector
        self.json_selector = EnhancedJsonPathSelector()
        layout.addWidget(self.json_selector)
        
        # Status display
        self.status_label = QLabel("Ready - Click 'Load Sample Data' to begin demo")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {VisualDesignConstants.ACCENT_COLOR};
                font-style: italic;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
                border-radius: 4px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """)
        layout.addWidget(self.status_label)
        
    def _create_demo_workflow(self):
        """Create a demo workflow with sample JSON data."""
        self.workflow = Workflow()
        
        # Step 1: User lookup action
        user_step = ActionStep(
            name="lookup_user",
            action_name="user_lookup",
            description="Look up user information",
            output_key="user_data"
        )
        user_step.parsed_json_output = {
            "user": {
                "id": "12345",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "manager": {
                    "name": "Jane Smith",
                    "email": "jane.smith@company.com"
                },
                "location": "San Francisco"
            },
            "permissions": ["read", "write", "admin"],
            "last_login": "2024-01-15T10:30:00Z"
        }
        self.workflow.add_step(user_step)
        
        # Step 2: Ticket processing script
        ticket_step = ScriptStep(
            name="process_tickets",
            description="Process user tickets",
            output_key="ticket_data"
        )
        ticket_step.parsed_json_output = {
            "tickets": [
                {
                    "id": "TKT-001",
                    "title": "Password Reset Request",
                    "status": "open",
                    "priority": "high",
                    "assignee": {
                        "name": "Support Team",
                        "email": "support@company.com"
                    },
                    "created_date": "2024-01-15T09:00:00Z"
                },
                {
                    "id": "TKT-002", 
                    "title": "Access Request",
                    "status": "closed",
                    "priority": "medium",
                    "assignee": {
                        "name": "IT Admin",
                        "email": "itadmin@company.com"
                    },
                    "created_date": "2024-01-14T14:30:00Z"
                }
            ],
            "total_count": 2,
            "status_summary": {
                "open": 1,
                "closed": 1,
                "in_progress": 0
            }
        }
        self.workflow.add_step(ticket_step)
        
    def _load_sample_data(self):
        """Load sample data into the JSON selector."""
        self.json_selector.set_workflow(self.workflow, current_step_index=2)
        self.status_label.setText("✅ Sample data loaded - Try selecting different steps and exploring the JSON structure")
        
    def _test_search_features(self):
        """Demonstrate the enhanced search functionality."""
        # Simulate search queries
        search_queries = ["user", "email", "ticket", "status"]
        
        for i, query in enumerate(search_queries):
            # Use QTimer to simulate user typing with delays
            from PySide6.QtCore import QTimer
            QTimer.singleShot(i * 1500, lambda q=query: self._simulate_search(q))
            
        self.status_label.setText("🔍 Testing search features - Watch the real-time filtering and visual feedback")
        
    def _simulate_search(self, query: str):
        """Simulate a search query."""
        if hasattr(self.json_selector, 'search_edit'):
            self.json_selector.search_edit.setText(query)
            
    def _test_visual_feedback(self):
        """Demonstrate the enhanced visual feedback features."""
        self.status_label.setText("✨ Testing visual feedback - Notice the status indicators, hover effects, and interactive elements")
        
        # Test auto-populate status updates
        self.json_selector._update_auto_populate_status("🎨 Demonstrating visual feedback features", "info")
        
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.json_selector._update_auto_populate_status("✅ Visual enhancements active", "success"))


def main():
    """Run the visual enhancements demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Moveworks YAML Assistant - Visual Demo")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Moveworks")
    
    # Create and show demo window
    demo = VisualEnhancementsDemo()
    demo.show()
    
    print("🎨 Visual Design & User Flow Enhancements Demo")
    print("=" * 50)
    print("Features demonstrated:")
    print("• 8px uniform margins and consistent spacing")
    print("• #f8f8f8 light backgrounds with subtle borders")
    print("• Monospace fonts for code and JSON paths")
    print("• Hover effects and interactive feedback")
    print("• Auto-population workflow for JSON Explorer")
    print("• Real-time search filtering with visual indicators")
    print("• Enhanced YAML preview with validation status")
    print("• Single-click path selection with copy functionality")
    print("• Persistent status indicators and user feedback")
    print("=" * 50)
    print("Click 'Load Sample Data' to begin exploring the enhancements!")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
