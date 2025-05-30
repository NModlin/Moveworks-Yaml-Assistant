#!/usr/bin/env python3
"""
Test script for the Enhanced JSON Path Selector.

This script demonstrates the improved functionality of the JSON Path Selector
including proper JSON tree population, visual feedback, search functionality,
and preview capabilities.
"""

import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import our enhanced components
from enhanced_json_selector import EnhancedJsonPathSelector
from core_structures import Workflow, ActionStep, ScriptStep

class TestWindow(QMainWindow):
    """Test window for the Enhanced JSON Path Selector."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced JSON Path Selector Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create test buttons
        button_layout = QHBoxLayout()
        
        test_btn1 = QPushButton("Test Simple JSON")
        test_btn1.clicked.connect(self.test_simple_json)
        button_layout.addWidget(test_btn1)
        
        test_btn2 = QPushButton("Test Complex JSON with Arrays")
        test_btn2.clicked.connect(self.test_complex_json)
        button_layout.addWidget(test_btn2)
        
        test_btn3 = QPushButton("Test Multiple Steps")
        test_btn3.clicked.connect(self.test_multiple_steps)
        button_layout.addWidget(test_btn3)
        
        debug_btn = QPushButton("Show Debug Panel")
        debug_btn.clicked.connect(self.show_debug_panel)
        button_layout.addWidget(debug_btn)
        
        layout.addLayout(button_layout)
        
        # Create the enhanced JSON selector
        self.json_selector = EnhancedJsonPathSelector()
        self.json_selector.path_selected.connect(self.on_path_selected)
        layout.addWidget(self.json_selector)
        
        # Initialize with empty workflow
        self.workflow = Workflow()
        self.json_selector.set_workflow(self.workflow)
        
        print("Test window initialized. Click buttons to test different scenarios.")
    
    def test_simple_json(self):
        """Test with simple JSON structure."""
        print("\n=== Testing Simple JSON ===")
        
        # Create a simple action step with JSON output
        action_step = ActionStep(
            action_name="get_user_info",
            output_key="user_data",
            description="Get user information"
        )
        
        # Add parsed JSON output
        action_step.parsed_json_output = {
            "user_id": "12345",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "department": "Engineering",
            "active": True
        }
        
        # Create workflow with this step
        self.workflow = Workflow(steps=[action_step])
        self.json_selector.set_workflow(self.workflow, 1)  # Current step index 1 (after this step)
        
        print("Simple JSON test loaded. The JSON selector should show the user data structure.")
    
    def test_complex_json(self):
        """Test with complex JSON structure including arrays."""
        print("\n=== Testing Complex JSON with Arrays ===")
        
        # Create an action step with complex JSON output
        action_step = ActionStep(
            action_name="get_user_tickets",
            output_key="ticket_data",
            description="Get user tickets and information"
        )
        
        # Add complex parsed JSON output with arrays
        action_step.parsed_json_output = {
            "user": {
                "id": "emp_12345",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "manager": {
                    "id": "mgr_67890",
                    "name": "Jane Smith",
                    "email": "jane.smith@company.com"
                },
                "permissions": ["read", "write", "admin"],
                "active": True
            },
            "tickets": [
                {
                    "id": "TKT-001",
                    "title": "Password Reset Request",
                    "status": "open",
                    "priority": "high",
                    "created_date": "2024-01-15",
                    "assignee": {
                        "id": "agent_123",
                        "name": "Support Agent"
                    }
                },
                {
                    "id": "TKT-002",
                    "title": "Software Installation",
                    "status": "in_progress",
                    "priority": "medium",
                    "created_date": "2024-01-14",
                    "assignee": {
                        "id": "agent_456",
                        "name": "Tech Support"
                    }
                }
            ],
            "metadata": {
                "total_tickets": 2,
                "open_tickets": 1,
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }
        
        # Create workflow with this step
        self.workflow = Workflow(steps=[action_step])
        self.json_selector.set_workflow(self.workflow, 1)  # Current step index 1 (after this step)
        
        print("Complex JSON test loaded. Try these paths:")
        print("- data.ticket_data.user.name")
        print("- data.ticket_data.tickets[0].title")
        print("- data.ticket_data.user.permissions[0]")
        print("- data.ticket_data.metadata.total_tickets")
    
    def test_multiple_steps(self):
        """Test with multiple steps having different JSON outputs."""
        print("\n=== Testing Multiple Steps ===")
        
        # Step 1: User lookup
        step1 = ActionStep(
            action_name="lookup_user",
            output_key="user_info",
            description="Look up user information"
        )
        step1.parsed_json_output = {
            "user_id": "12345",
            "name": "John Doe",
            "email": "john.doe@company.com"
        }
        
        # Step 2: Get user tickets
        step2 = ActionStep(
            action_name="get_tickets",
            output_key="tickets",
            description="Get user tickets"
        )
        step2.parsed_json_output = [
            {"id": "TKT-001", "title": "Password Reset", "status": "open"},
            {"id": "TKT-002", "title": "Software Install", "status": "closed"}
        ]
        
        # Step 3: Script step with calculation
        step3 = ScriptStep(
            output_key="summary",
            code="len(tickets)",
            description="Calculate ticket count"
        )
        step3.parsed_json_output = {
            "ticket_count": 2,
            "user_name": "John Doe",
            "summary": "User has 2 tickets"
        }
        
        # Create workflow with multiple steps
        self.workflow = Workflow(steps=[step1, step2, step3])
        self.json_selector.set_workflow(self.workflow, 3)  # Current step index 3 (after all steps)
        
        print("Multiple steps test loaded. Use the step dropdown to select different outputs.")
    
    def show_debug_panel(self):
        """Show the debug panel for troubleshooting."""
        print("\n=== Showing Debug Panel ===")
        self.json_selector.add_debug_info_panel()
        print("Debug panel added. Check the bottom of the JSON selector for debug information.")
    
    def on_path_selected(self, path: str):
        """Handle path selection from the JSON selector."""
        print(f"\n🎯 Path Selected: {path}")
        print(f"   This path has been copied to the clipboard and can be used in YAML generation.")
        print(f"   Example usage: input_args.some_field: {path}")

def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = TestWindow()
    window.show()
    
    print("\n" + "="*80)
    print("ENHANCED JSON PATH SELECTOR TEST")
    print("="*80)
    print("This test demonstrates the improved JSON Path Selector functionality:")
    print("1. Proper JSON tree population when steps are selected")
    print("2. Clear visual feedback for path selection")
    print("3. Search functionality within JSON structure")
    print("4. Preview panel showing actual values")
    print("5. Debug logging for troubleshooting")
    print("6. One-click path copying")
    print("\nClick the test buttons to try different scenarios!")
    print("="*80)
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
