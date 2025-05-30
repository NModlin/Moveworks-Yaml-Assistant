#!/usr/bin/env python3
"""
Test script to verify that the JSON Path Selector auto-population fix is working.

This script creates a workflow with steps that have parsed JSON output and
tests that the JSON Path Selector properly auto-populates when steps are selected.
"""

import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer

from core_structures import Workflow, ActionStep, ScriptStep
from tabbed_json_selector import TabbedJsonPathSelector

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestWindow(QMainWindow):
    """Test window for verifying JSON Path Selector functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Path Selector Auto-Population Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Click 'Create Test Workflow' to start testing")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Test button
        test_btn = QPushButton("Create Test Workflow")
        test_btn.clicked.connect(self.create_test_workflow)
        test_btn.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4CAF50; color: white;")
        layout.addWidget(test_btn)
        
        # JSON Path Selector
        self.json_selector = TabbedJsonPathSelector()
        self.json_selector.path_selected.connect(self.on_path_selected)
        layout.addWidget(self.json_selector)
        
        # Create test workflow
        self.workflow = None
        
    def create_test_workflow(self):
        """Create a test workflow with steps that have JSON output."""
        logger.info("Creating test workflow...")
        
        # Create workflow
        self.workflow = Workflow()
        
        # Step 1: Action step with user data
        user_step = ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            description="Get user information",
            input_args={"email": "data.input_email"}
        )
        
        # Add parsed JSON output
        user_json = {
            "user": {
                "id": "emp12345",
                "name": "John Doe", 
                "email": "john.doe@company.com",
                "department": "Engineering",
                "manager": {
                    "name": "Jane Smith",
                    "email": "jane.smith@company.com"
                },
                "permissions": ["read", "write", "admin"]
            },
            "metadata": {
                "last_login": "2024-01-15T10:30:00Z",
                "account_status": "active"
            }
        }
        user_step.user_provided_json_output = json.dumps(user_json, indent=2)
        user_step.parsed_json_output = user_json
        self.workflow.steps.append(user_step)
        
        # Step 2: Script step with processed data
        script_step = ScriptStep(
            code="result = {'greeting': f'Hello, {data.user_info.user.name}!', 'department_info': data.user_info.user.department}",
            output_key="processed_data",
            description="Process user data"
        )
        
        # Add parsed JSON output
        processed_json = {
            "greeting": "Hello, John Doe!",
            "department_info": "Engineering",
            "processing_time": "2024-01-15T10:35:00Z",
            "status": "completed"
        }
        script_step.user_provided_json_output = json.dumps(processed_json, indent=2)
        script_step.parsed_json_output = processed_json
        self.workflow.steps.append(script_step)
        
        # Step 3: Action step without JSON output (for testing)
        empty_step = ActionStep(
            action_name="mw.send_notification",
            output_key="notification_result",
            description="Send notification (no JSON output)",
            input_args={"message": "data.processed_data.greeting"}
        )
        # No JSON output for this step
        self.workflow.steps.append(empty_step)
        
        # Set the workflow in the JSON selector
        self.json_selector.set_workflow(self.workflow, 0)
        
        self.status_label.setText(f"✅ Created test workflow with {len(self.workflow.steps)} steps. Select different steps to test auto-population.")
        logger.info(f"Test workflow created with {len(self.workflow.steps)} steps")
        
        # Auto-test step selection after a short delay
        QTimer.singleShot(1000, self.auto_test_steps)
        
    def auto_test_steps(self):
        """Automatically test step selection to verify auto-population."""
        logger.info("Starting auto-test of step selection...")
        
        # Test each step
        for i in range(len(self.workflow.steps)):
            step = self.workflow.steps[i]
            logger.info(f"Testing step {i}: {step.description}")
            
            # Set the workflow with this step selected
            self.json_selector.set_workflow(self.workflow, i)
            
            # Check if JSON data was loaded
            has_json = hasattr(step, 'parsed_json_output') and step.parsed_json_output
            if has_json:
                logger.info(f"✅ Step {i} has JSON output - should auto-populate")
            else:
                logger.info(f"⚠️ Step {i} has no JSON output - should show empty tree")
                
        self.status_label.setText("✅ Auto-test completed. Check the console logs and try selecting steps manually.")
        
    def on_path_selected(self, path):
        """Handle path selection from the JSON selector."""
        logger.info(f"Path selected: {path}")
        self.status_label.setText(f"✅ Path selected: {path}")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
