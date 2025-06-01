#!/usr/bin/env python3
"""
Test script for the Enhanced Input Arguments system.

This script tests the key functionality of the enhanced input arguments table:
1. Auto-suggestion from action catalog
2. JSON-based argument suggestions
3. Data path suggestions from previous steps
4. Drag-and-drop functionality
5. Real-time validation
"""

import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

from enhanced_input_args_table import EnhancedInputArgsTable, InputArgsSuggestionEngine
from core_structures import Workflow, ActionStep, ScriptStep
from mw_actions_catalog import MW_ACTIONS_CATALOG


class TestWindow(QMainWindow):
    """Test window for the enhanced input arguments table."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Input Arguments Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create test workflow
        self.workflow = Workflow()
        
        # Add a test action step
        user_step = ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            description="Get user information"
        )
        user_step.parsed_json_output = {
            "user": {
                "id": "user123",
                "email": "john.doe@company.com",
                "name": "John Doe",
                "department": "Engineering",
                "manager": {
                    "id": "mgr456",
                    "email": "jane.smith@company.com",
                    "name": "Jane Smith"
                },
                "active": True
            }
        }
        self.workflow.steps.append(user_step)
        
        # Add a test script step
        script_step = ScriptStep(
            code="result = {'processed': True, 'timestamp': '2024-01-01'}",
            output_key="processing_result",
            description="Process user data"
        )
        script_step.parsed_json_output = {
            "processed": True,
            "timestamp": "2024-01-01T10:00:00Z",
            "data_count": 1
        }
        self.workflow.steps.append(script_step)
        
        # Create current step for testing
        self.current_step = ActionStep(
            action_name="mw.create_ticket",
            output_key="ticket_info",
            description="Create a support ticket"
        )
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the test UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Enhanced Input Arguments Table Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Test the enhanced input arguments features:\n"
            "• Double-click argument names for action-based suggestions\n"
            "• Double-click values for data path suggestions\n"
            "• Use the buttons below to test auto-population features\n"
            "• Try drag-and-drop (simulated with buttons)"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)
        
        # Enhanced input arguments table
        self.table = EnhancedInputArgsTable(step_type="action")
        self.table.set_context(self.workflow, self.current_step, 2)  # Current step is index 2
        layout.addWidget(self.table)
        
        # Test buttons
        button_layout = QVBoxLayout()
        
        # Auto-populate from action
        auto_populate_btn = QPushButton("Auto-Populate from mw.create_ticket")
        auto_populate_btn.clicked.connect(self._test_auto_populate)
        button_layout.addWidget(auto_populate_btn)
        
        # JSON suggestions
        json_suggest_btn = QPushButton("Test JSON Suggestions")
        json_suggest_btn.clicked.connect(self._test_json_suggestions)
        button_layout.addWidget(json_suggest_btn)
        
        # Add test data
        add_test_data_btn = QPushButton("Add Test Arguments")
        add_test_data_btn.clicked.connect(self._add_test_data)
        button_layout.addWidget(add_test_data_btn)
        
        # Validate
        validate_btn = QPushButton("Test Validation")
        validate_btn.clicked.connect(self._test_validation)
        button_layout.addWidget(validate_btn)
        
        # Show suggestions
        show_suggestions_btn = QPushButton("Show Data Path Suggestions")
        show_suggestions_btn.clicked.connect(self._show_data_suggestions)
        button_layout.addWidget(show_suggestions_btn)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready for testing")
        self.status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #e8f5e8;")
        layout.addWidget(self.status_label)
        
        # Connect validation signal
        self.table.validation_changed.connect(self._on_validation_changed)
        
    def _test_auto_populate(self):
        """Test auto-population from action catalog."""
        self.table.auto_populate_from_action("mw.create_ticket")
        self.status_label.setText("✅ Auto-populated arguments from mw.create_ticket")
        
    def _test_json_suggestions(self):
        """Test JSON-based suggestions."""
        # Simulate JSON input
        test_json = {
            "ticketTitle": "Test Ticket",
            "ticketDescription": "This is a test ticket",
            "assigneeEmail": "support@company.com",
            "priorityLevel": "high",
            "categoryName": "IT Support"
        }
        
        json_text = json.dumps(test_json, indent=2)
        self.table._process_json_for_suggestions(json_text)
        self.status_label.setText("✅ Processed JSON for argument suggestions")
        
    def _add_test_data(self):
        """Add some test arguments."""
        test_args = [
            ("title", "data.user_info.user.name + ' Support Request'"),
            ("description", "Issue reported by user"),
            ("assignee", "data.user_info.user.manager.email"),
            ("priority", "medium"),
            ("category", "IT Support")
        ]
        
        for key, value in test_args:
            self.table.add_argument_row(key, value)
            
        self.status_label.setText("✅ Added test arguments with data references")
        
    def _test_validation(self):
        """Test validation functionality."""
        # Add some invalid arguments for testing
        self.table.add_argument_row("InvalidKey", "data.user_info.user.name")  # Invalid snake_case
        self.table.add_argument_row("valid_key", "invalid_data_reference")  # Invalid data reference
        
        # Trigger validation
        self.table._validate_all_args()
        self.status_label.setText("✅ Validation test completed - check for error indicators")
        
    def _show_data_suggestions(self):
        """Show available data path suggestions."""
        suggestions = self.table.suggestion_engine.get_data_path_suggestions()
        
        suggestion_text = "Available data paths:\n"
        for i, suggestion in enumerate(suggestions[:10]):  # Show first 10
            suggestion_text += f"• {suggestion['value']} ({suggestion['source']})\n"
            
        self.status_label.setText(f"✅ Found {len(suggestions)} data path suggestions")
        print(suggestion_text)  # Print to console for detailed view
        
    def _on_validation_changed(self, is_valid: bool, issues: list):
        """Handle validation status changes."""
        if is_valid:
            self.status_label.setText("✅ All arguments are valid")
            self.status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #e8f5e8;")
        else:
            issue_count = len(issues)
            self.status_label.setText(f"❌ Found {issue_count} validation issue(s)")
            self.status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #ffebee;")
            
            # Print issues to console
            print("Validation issues:")
            for issue in issues:
                print(f"  • {issue}")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = TestWindow()
    window.show()
    
    print("Enhanced Input Arguments Test Application")
    print("=" * 50)
    print("Available Moveworks actions for testing:")
    for action in MW_ACTIONS_CATALOG[:5]:  # Show first 5 actions
        print(f"  • {action.action_name}: {action.description}")
    print(f"  ... and {len(MW_ACTIONS_CATALOG) - 5} more actions")
    print("\nTest the enhanced features using the buttons in the UI!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
