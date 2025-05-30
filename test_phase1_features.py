#!/usr/bin/env python3
"""
Test script for Enhanced JSON Path Selector Phase 1 Features.

This script demonstrates and tests:
1. Smart Auto-Completion
2. Real-Time Path Validation  
3. Drag & Drop Path Insertion
4. Path Bookmarking System

Phase 1 focuses on high-impact, low-complexity features that provide immediate
productivity improvements for workflow creation.
"""

import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import our enhanced components
from enhanced_json_selector import EnhancedJsonPathSelector, DropTargetLineEdit, SmartPathCompleter, PathValidator
from core_structures import Workflow, ActionStep, ScriptStep

class Phase1TestWindow(QMainWindow):
    """Test window for Phase 1 Enhanced JSON Path Selector features."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced JSON Path Selector - Phase 1 Features Test")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🚀 Phase 1 Features: Smart Auto-Completion, Validation, Drag & Drop, Bookmarks")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Test buttons
        button_layout = QHBoxLayout()
        
        test_btn1 = QPushButton("1️⃣ Test Auto-Completion")
        test_btn1.clicked.connect(self.test_auto_completion)
        button_layout.addWidget(test_btn1)
        
        test_btn2 = QPushButton("2️⃣ Test Path Validation")
        test_btn2.clicked.connect(self.test_path_validation)
        button_layout.addWidget(test_btn2)
        
        test_btn3 = QPushButton("3️⃣ Test Drag & Drop")
        test_btn3.clicked.connect(self.test_drag_drop)
        button_layout.addWidget(test_btn3)
        
        test_btn4 = QPushButton("4️⃣ Test Bookmarks")
        test_btn4.clicked.connect(self.test_bookmarks)
        button_layout.addWidget(test_btn4)
        
        test_all_btn = QPushButton("🎯 Test All Features")
        test_all_btn.clicked.connect(self.test_all_features)
        test_all_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        button_layout.addWidget(test_all_btn)
        
        layout.addLayout(button_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side: JSON Selector
        self.json_selector = EnhancedJsonPathSelector()
        self.json_selector.path_selected.connect(self.on_path_selected)
        content_layout.addWidget(self.json_selector, 2)
        
        # Right side: Test area
        test_area = QWidget()
        test_layout = QVBoxLayout(test_area)
        
        test_layout.addWidget(QLabel("🧪 Test Area"))
        
        # Test input fields with Phase 1 features
        test_layout.addWidget(QLabel("Drop Target Input (supports drag & drop):"))
        self.test_input1 = DropTargetLineEdit()
        self.test_input1.setPlaceholderText("Drag paths here or type with auto-completion...")
        test_layout.addWidget(self.test_input1)
        
        test_layout.addWidget(QLabel("Another Drop Target Input:"))
        self.test_input2 = DropTargetLineEdit()
        self.test_input2.setPlaceholderText("Another field for testing...")
        test_layout.addWidget(self.test_input2)
        
        # Results area
        test_layout.addWidget(QLabel("📋 Test Results:"))
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        test_layout.addWidget(self.results_text)
        
        content_layout.addWidget(test_area, 1)
        layout.addWidget(QWidget())  # Spacer
        layout.addLayout(content_layout)
        
        # Initialize with test data
        self.setup_test_data()
        
        print("\n" + "="*80)
        print("PHASE 1 FEATURES TEST - Enhanced JSON Path Selector")
        print("="*80)
        print("Testing: Smart Auto-Completion, Path Validation, Drag & Drop, Bookmarks")
        print("Click the test buttons to try different Phase 1 features!")
        print("="*80)
    
    def setup_test_data(self):
        """Setup test workflow with complex JSON data."""
        # Create a comprehensive test workflow
        workflow = Workflow()
        
        # Step 1: User lookup with nested data
        step1 = ActionStep(
            action_name="lookup_user_details",
            output_key="user_info",
            description="Look up comprehensive user information"
        )
        step1.parsed_json_output = {
            "user": {
                "id": "emp_12345",
                "personal": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@company.com",
                    "phone": "+1-555-0123"
                },
                "work": {
                    "department": "Engineering",
                    "title": "Senior Software Engineer",
                    "manager": {
                        "id": "mgr_67890",
                        "name": "Jane Smith",
                        "email": "jane.smith@company.com"
                    },
                    "team": "Platform Team",
                    "location": "San Francisco"
                },
                "permissions": ["read", "write", "admin", "deploy"],
                "active": True,
                "last_login": "2024-01-15T10:30:00Z"
            },
            "metadata": {
                "query_time": "2024-01-15T14:22:33Z",
                "source": "LDAP",
                "confidence": 0.98
            }
        }
        workflow.steps.append(step1)
        
        # Step 2: Get user tickets with array data
        step2 = ActionStep(
            action_name="get_user_tickets",
            output_key="tickets",
            description="Retrieve all tickets for the user"
        )
        step2.parsed_json_output = {
            "tickets": [
                {
                    "id": "TKT-001",
                    "title": "Password Reset Request",
                    "status": "open",
                    "priority": "high",
                    "created_date": "2024-01-15",
                    "assignee": {
                        "id": "agent_123",
                        "name": "Support Agent",
                        "team": "IT Support"
                    },
                    "tags": ["password", "urgent", "security"]
                },
                {
                    "id": "TKT-002", 
                    "title": "Software Installation Request",
                    "status": "in_progress",
                    "priority": "medium",
                    "created_date": "2024-01-14",
                    "assignee": {
                        "id": "agent_456",
                        "name": "Tech Support",
                        "team": "Desktop Support"
                    },
                    "tags": ["software", "installation"]
                }
            ],
            "summary": {
                "total_count": 2,
                "open_count": 1,
                "high_priority_count": 1
            }
        }
        workflow.steps.append(step2)
        
        # Step 3: Calculate metrics
        step3 = ScriptStep(
            output_key="metrics",
            code="calculate_user_metrics(user_info, tickets)",
            description="Calculate user engagement metrics"
        )
        step3.parsed_json_output = {
            "engagement": {
                "ticket_frequency": 0.5,
                "avg_resolution_time": 24.5,
                "satisfaction_score": 4.2
            },
            "risk_factors": {
                "high_priority_tickets": 1,
                "overdue_tickets": 0,
                "escalated_tickets": 0
            }
        }
        workflow.steps.append(step3)
        
        # Set the workflow in the selector
        self.json_selector.set_workflow(workflow, 3)  # Current step index after all steps
        
        # Setup test inputs with Phase 1 features
        self.test_input1.set_path_completer(self.json_selector.smart_completer)
        self.test_input1.set_path_validator(self.json_selector.path_validator)
        self.test_input2.set_path_completer(self.json_selector.smart_completer)
        self.test_input2.set_path_validator(self.json_selector.path_validator)
        
        self.log_result("✅ Test data loaded with 3 steps containing complex JSON structures")
    
    def test_auto_completion(self):
        """Test smart auto-completion functionality."""
        self.log_result("\n🔍 Testing Smart Auto-Completion:")
        self.log_result("1. Click in the test input fields above")
        self.log_result("2. Start typing: 'data.user' or 'data.tick'")
        self.log_result("3. Auto-completion should appear with available paths")
        self.log_result("4. Try fuzzy matching: 'usr.nm' should suggest 'user.name' paths")
        
        # Update completions
        self.json_selector.smart_completer.update_completions()
        self.log_result("✅ Auto-completion updated with current JSON paths")
    
    def test_path_validation(self):
        """Test real-time path validation."""
        self.log_result("\n✅ Testing Real-Time Path Validation:")
        self.log_result("1. Type valid paths like: data.user_info.user.personal.first_name")
        self.log_result("2. Type invalid paths like: data.user_info.user.invalid_field")
        self.log_result("3. Watch for green (valid) or red (invalid) borders")
        self.log_result("4. Hover over invalid fields to see suggestions")
        
        # Test some paths programmatically
        test_paths = [
            "data.user_info.user.personal.first_name",  # Valid
            "data.user_info.user.invalid_field",        # Invalid
            "data.tickets.tickets[0].title",             # Valid array access
            "data.tickets.tickets[99].title"             # Invalid array index
        ]
        
        for path in test_paths:
            result = self.json_selector.path_validator.validate_path(path, {})
            status = "✅ Valid" if result.valid else "❌ Invalid"
            self.log_result(f"  {path}: {status}")
    
    def test_drag_drop(self):
        """Test drag & drop functionality."""
        self.log_result("\n🖱️ Testing Drag & Drop:")
        self.log_result("1. Click and drag any path from the JSON tree on the left")
        self.log_result("2. Drop it into one of the test input fields above")
        self.log_result("3. The path should be inserted automatically")
        self.log_result("4. Try dragging multiple different paths")
        self.log_result("✅ Drag & drop is ready - try it now!")
    
    def test_bookmarks(self):
        """Test bookmark functionality."""
        self.log_result("\n📌 Testing Bookmarks:")
        self.log_result("1. Select a path from the JSON tree")
        self.log_result("2. Click the '📌 Bookmark' button")
        self.log_result("3. Enter a name for the bookmark")
        self.log_result("4. Use the bookmarks dropdown to select saved paths")
        self.log_result("5. Click '⚙️ Manage' to open bookmark management")
        
        # Add some sample bookmarks
        sample_bookmarks = [
            ("User Email", "data.user_info.user.personal.email"),
            ("User Department", "data.user_info.user.work.department"),
            ("First Ticket Title", "data.tickets.tickets[0].title")
        ]
        
        for name, path in sample_bookmarks:
            self.json_selector.bookmark_manager.add_bookmark(name, path, "Sample")
        
        self.json_selector._update_bookmarks_combo()
        self.log_result("✅ Added sample bookmarks - check the bookmarks dropdown!")
    
    def test_all_features(self):
        """Test all Phase 1 features together."""
        self.log_result("\n🎯 Testing All Phase 1 Features:")
        self.test_auto_completion()
        self.test_path_validation()
        self.test_drag_drop()
        self.test_bookmarks()
        self.log_result("\n🎉 All Phase 1 features are ready for testing!")
        self.log_result("Try the interactive features above to see them in action.")
    
    def on_path_selected(self, path: str):
        """Handle path selection from the JSON selector."""
        self.log_result(f"\n🎯 Path Selected: {path}")
        self.log_result(f"   Usage tracked and bookmark button enabled")
    
    def log_result(self, message: str):
        """Log a test result to the results area."""
        self.results_text.append(message)
        print(message)  # Also print to console

def main():
    """Run the Phase 1 test application."""
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = Phase1TestWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
