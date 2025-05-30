#!/usr/bin/env python3
"""
Test script for the improved readability of the JSON Path Selector.

This script demonstrates the enhanced visual design with high-contrast
group box titles and improved readability against dark backgrounds.
"""

import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import our enhanced components
from enhanced_json_selector import EnhancedJsonPathSelector, VisualDesignConstants
from core_structures import Workflow, ActionStep, ScriptStep


class ReadabilityTestWindow(QMainWindow):
    """Test window showcasing the improved readability of the JSON Path Selector."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Path Selector - Improved Readability Test")
        self.setGeometry(100, 100, 1200, 900)
        
        # Apply dark background to test contrast
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #2b2b2b;
            }}
        """)
        
        self._setup_ui()
        self._create_test_workflow()
        
    def _setup_ui(self):
        """Setup the test UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with improved visibility
        header = QLabel("🎨 Improved Readability Test - High Contrast Group Titles")
        header.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                text-align: center;
            }}
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Instructions with high contrast
        instructions = QLabel(
            "✅ PROBLEM SOLVED: Group box titles are now highly visible with colored backgrounds!\n"
            "• Blue titles for main sections (Step Selection, JSON Explorer)\n"
            "• Green titles for search and preview sections\n"
            "• Orange titles for bookmarks and quick access\n"
            "• Purple titles for advanced features\n"
            "All text is now white on colored backgrounds for maximum readability."
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: white;
                padding: 15px;
                background-color: #1b5e20;
                border-radius: 6px;
                margin-bottom: 20px;
                border: 2px solid {VisualDesignConstants.SUCCESS_COLOR};
            }}
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Load test data button
        load_btn = QPushButton("📊 Load Test Data to See Improved Readability")
        load_btn.clicked.connect(self._load_test_data)
        load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: #388e3c;
            }}
        """)
        layout.addWidget(load_btn)
        
        # Enhanced JSON Path Selector with improved readability
        self.json_selector = EnhancedJsonPathSelector()
        layout.addWidget(self.json_selector)
        
        # Status display
        self.status_label = QLabel("Ready - Click the button above to load test data and see the improved readability")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 14px;
                font-style: italic;
                padding: 10px;
                background-color: #424242;
                border-radius: 4px;
                margin-top: 10px;
                border: 1px solid #666;
            }}
        """)
        layout.addWidget(self.status_label)
        
    def _create_test_workflow(self):
        """Create a test workflow with comprehensive JSON data."""
        self.workflow = Workflow()
        
        # Complex user data step
        user_step = ActionStep(
            name="get_user_profile",
            action_name="user_profile_lookup",
            description="Retrieve comprehensive user profile",
            output_key="user_profile"
        )
        user_step.parsed_json_output = {
            "personal_info": {
                "user_id": "USR-12345",
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@company.com",
                "phone": "+1-555-0123",
                "department": "Engineering",
                "title": "Senior Software Engineer",
                "location": {
                    "office": "San Francisco HQ",
                    "building": "Building A",
                    "floor": 3,
                    "desk": "3A-42"
                },
                "manager": {
                    "name": "Bob Smith",
                    "email": "bob.smith@company.com",
                    "user_id": "USR-67890"
                }
            },
            "access_info": {
                "permissions": ["read", "write", "admin", "deploy"],
                "groups": ["engineers", "senior_staff", "deployment_team"],
                "last_login": "2024-01-15T14:30:00Z",
                "login_count": 1247,
                "failed_attempts": 0
            },
            "preferences": {
                "theme": "dark",
                "language": "en-US",
                "timezone": "America/Los_Angeles",
                "notifications": {
                    "email": True,
                    "slack": True,
                    "mobile": False
                }
            }
        }
        self.workflow.add_step(user_step)
        
        # Complex project data step
        project_step = ScriptStep(
            name="get_project_data",
            description="Retrieve project information and metrics",
            output_key="project_data"
        )
        project_step.parsed_json_output = {
            "projects": [
                {
                    "project_id": "PROJ-001",
                    "name": "YAML Assistant Enhancement",
                    "status": "active",
                    "priority": "high",
                    "team": {
                        "lead": "Alice Johnson",
                        "members": ["Bob Smith", "Carol Davis", "David Wilson"],
                        "size": 4
                    },
                    "timeline": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-03-31",
                        "milestones": [
                            {
                                "name": "Phase 1 Complete",
                                "date": "2024-01-31",
                                "status": "completed"
                            },
                            {
                                "name": "Phase 2 Complete",
                                "date": "2024-02-28",
                                "status": "in_progress"
                            }
                        ]
                    },
                    "metrics": {
                        "completion_percentage": 65,
                        "tasks_total": 45,
                        "tasks_completed": 29,
                        "bugs_open": 3,
                        "bugs_resolved": 12
                    }
                }
            ],
            "summary": {
                "total_projects": 1,
                "active_projects": 1,
                "completed_projects": 0,
                "team_utilization": 0.85
            }
        }
        self.workflow.add_step(project_step)
        
    def _load_test_data(self):
        """Load test data into the JSON selector."""
        self.json_selector.set_workflow(self.workflow, current_step_index=2)
        self.status_label.setText("✅ Test data loaded! Notice how all group box titles are now clearly visible with colored backgrounds.")


def main():
    """Run the readability test."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("JSON Path Selector - Readability Test")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("Moveworks")
    
    # Create and show test window
    test_window = ReadabilityTestWindow()
    test_window.show()
    
    print("🎨 Improved Readability Test")
    print("=" * 40)
    print("PROBLEM SOLVED:")
    print("• Group box titles now have colored backgrounds")
    print("• White text on colored backgrounds for maximum contrast")
    print("• Different colors for different section types")
    print("• Easily readable against any background color")
    print("=" * 40)
    print("Click 'Load Test Data' to see the improvements!")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
