"""
Contextual Examples Panel for the Moveworks YAML Assistant.

This module provides context-aware examples to help users learn patterns and best practices.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QComboBox, QGroupBox,
    QSplitter, QTabWidget, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


@dataclass
class Example:
    """Represents a code or configuration example."""
    title: str
    description: str
    category: str
    context: str  # When to show this example
    code: str
    explanation: str
    tags: List[str]
    difficulty: str = "Beginner"


class ExamplesDatabase:
    """Database of contextual examples."""
    
    def __init__(self):
        self.examples: Dict[str, Example] = {}
        self._load_examples()
    
    def _load_examples(self):
        """Load built-in examples."""
        
        # Action Step Examples
        self.examples["basic_action"] = Example(
            title="Basic Action Step",
            description="Simple action step with input arguments",
            category="Action Steps",
            context="action_step",
            code="""action_name: "mw.get_user_by_email"
output_key: "user_info"
input_args:
  email: "data.input_email"
""",
            explanation="This example shows a basic action step that calls the Moveworks user lookup action. The email parameter comes from the workflow input.",
            tags=["action", "basic", "user-lookup"],
            difficulty="Beginner"
        )
        
        self.examples["action_with_multiple_args"] = Example(
            title="Action with Multiple Arguments",
            description="Action step with multiple input arguments",
            category="Action Steps",
            context="action_step",
            code="""action_name: "servicenow.create_incident"
output_key: "ticket_result"
input_args:
  short_description: "data.issue_summary"
  description: "data.issue_details"
  caller_id: "data.user_info.user.id"
  urgency: "3"
  impact: "3"
  category: "Software"
""",
            explanation="This example demonstrates an action with multiple input arguments, mixing data references and static values.",
            tags=["action", "servicenow", "multiple-args"],
            difficulty="Intermediate"
        )
        
        # Script Step Examples
        self.examples["basic_script"] = Example(
            title="Basic Script Step",
            description="Simple data processing script",
            category="Script Steps",
            context="script_step",
            code="""# Process user information
user = data.user_info.user
result = {
    "display_name": user.name,
    "email": user.email,
    "department": user.department
}
return result
""",
            explanation="This script extracts and reformats user information from a previous step's output.",
            tags=["script", "basic", "data-processing"],
            difficulty="Beginner"
        )
        
        self.examples["conditional_script"] = Example(
            title="Conditional Logic Script",
            description="Script with conditional logic and error handling",
            category="Script Steps",
            context="script_step",
            code="""# Validate and process ticket creation
if hasattr(data.ticket_result, 'error') and data.ticket_result.error:
    return {
        "success": False,
        "error_message": data.ticket_result.error,
        "suggested_action": "Please try again or contact support"
    }

ticket = data.ticket_result.ticket
return {
    "success": True,
    "ticket_number": ticket.number,
    "ticket_url": f"https://company.service-now.com/nav_to.do?uri=incident.do?sys_id={ticket.sys_id}",
    "message": f"Ticket {ticket.number} created successfully"
}
""",
            explanation="This script demonstrates error handling and conditional logic to process API responses safely.",
            tags=["script", "conditional", "error-handling"],
            difficulty="Advanced"
        )
        
        # Data Mapping Examples
        self.examples["simple_data_mapping"] = Example(
            title="Simple Data Mapping",
            description="Basic data reference patterns",
            category="Data Mapping",
            context="data_mapping",
            code="""# Reference previous step output
"data.user_info.user.email"

# Reference workflow input
"data.input_email"

# Reference nested object property
"data.api_response.result.items[0].name"
""",
            explanation="These examples show common patterns for referencing data from previous steps and workflow inputs.",
            tags=["data", "mapping", "references"],
            difficulty="Beginner"
        )
        
        self.examples["complex_data_mapping"] = Example(
            title="Complex Data Mapping",
            description="Advanced data reference patterns",
            category="Data Mapping",
            context="data_mapping",
            code="""# Array element access
"data.users_list.users[0].email"

# Nested object navigation
"data.ticket_info.ticket.assigned_to.user.name"

# Multiple level nesting
"data.api_response.result.data.items[0].properties.status"
""",
            explanation="These examples demonstrate accessing array elements and deeply nested object properties.",
            tags=["data", "mapping", "arrays", "nested"],
            difficulty="Intermediate"
        )
        
        # JSON Output Examples
        self.examples["user_json_output"] = Example(
            title="User Lookup JSON Output",
            description="Example JSON output for user lookup actions",
            category="JSON Outputs",
            context="json_output",
            code="""{
  "user": {
    "id": "12345",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "manager": {
      "id": "67890",
      "name": "Jane Smith",
      "email": "jane.smith@company.com"
    },
    "active": true
  }
}
""",
            explanation="This is a typical JSON structure returned by user lookup actions. Use this format when providing example outputs.",
            tags=["json", "user", "output"],
            difficulty="Beginner"
        )
        
        self.examples["ticket_json_output"] = Example(
            title="Ticket Creation JSON Output",
            description="Example JSON output for ticket creation actions",
            category="JSON Outputs",
            context="json_output",
            code="""{
  "ticket": {
    "number": "INC0012345",
    "sys_id": "abc123def456",
    "state": "New",
    "short_description": "User cannot access email",
    "assigned_to": {
      "user": {
        "id": "support123",
        "name": "Support Agent"
      }
    },
    "created_on": "2024-01-15T10:30:00Z",
    "priority": "3 - Moderate"
  }
}
""",
            explanation="This shows the typical structure of a ServiceNow incident ticket response. Include all relevant fields for data mapping.",
            tags=["json", "ticket", "servicenow"],
            difficulty="Intermediate"
        )
        
        # Best Practices Examples
        self.examples["error_handling_pattern"] = Example(
            title="Error Handling Best Practice",
            description="Recommended pattern for handling API errors",
            category="Best Practices",
            context="best_practices",
            code="""# Always check for errors in API responses
if hasattr(data.api_response, 'error') and data.api_response.error:
    return {
        "success": False,
        "error_type": "api_error",
        "error_message": data.api_response.error,
        "suggested_action": "Please try again later"
    }

# Process successful response
result = data.api_response.result
return {
    "success": True,
    "data": result,
    "message": "Operation completed successfully"
}
""",
            explanation="Always check for error conditions in API responses before processing data. This prevents runtime errors.",
            tags=["best-practices", "error-handling", "api"],
            difficulty="Intermediate"
        )
        
        self.examples["data_validation"] = Example(
            title="Data Validation Pattern",
            description="Validate data before processing",
            category="Best Practices",
            context="best_practices",
            code="""# Validate required data exists
if not hasattr(data.user_info, 'user') or not data.user_info.user:
    return {
        "success": False,
        "error": "User information not found"
    }

user = data.user_info.user

# Validate required fields
if not hasattr(user, 'email') or not user.email:
    return {
        "success": False,
        "error": "User email is required"
    }

# Process validated data
return {
    "success": True,
    "user_email": user.email,
    "user_name": getattr(user, 'name', 'Unknown')
}
""",
            explanation="Always validate that required data exists before using it. Use hasattr() and getattr() for safe access.",
            tags=["best-practices", "validation", "safety"],
            difficulty="Advanced"
        )
    
    def get_examples_by_context(self, context: str) -> List[Example]:
        """Get examples relevant to a specific context."""
        return [ex for ex in self.examples.values() if ex.context == context]
    
    def get_examples_by_category(self, category: str) -> List[Example]:
        """Get examples in a specific category."""
        return [ex for ex in self.examples.values() if ex.category == category]
    
    def search_examples(self, query: str) -> List[Example]:
        """Search examples by title, description, or tags."""
        query = query.lower()
        results = []
        
        for example in self.examples.values():
            if (query in example.title.lower() or
                query in example.description.lower() or
                any(query in tag.lower() for tag in example.tags)):
                results.append(example)
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """Get all example categories."""
        categories = set(ex.category for ex in self.examples.values())
        return sorted(list(categories))


class ContextualExamplesPanel(QWidget):
    """Panel showing contextual examples based on current application state."""
    
    example_applied = Signal(str)  # Emits example code to apply
    
    def __init__(self):
        super().__init__()
        self.database = ExamplesDatabase()
        self.current_context = ""
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the examples panel UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Contextual Examples")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header_label)
        
        # Context indicator
        self.context_label = QLabel("Context: General")
        self.context_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.context_label)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search examples...")
        self.search_edit.textChanged.connect(self._filter_examples)
        filter_layout.addWidget(self.search_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.currentTextChanged.connect(self._filter_examples)
        filter_layout.addWidget(self.category_combo)
        
        layout.addLayout(filter_layout)
        
        # Examples list
        self.examples_list = QListWidget()
        self.examples_list.currentItemChanged.connect(self._on_example_selected)
        layout.addWidget(self.examples_list)
        
        # Example details
        details_group = QGroupBox("Example Details")
        details_layout = QVBoxLayout(details_group)
        
        self.example_title = QLabel()
        self.example_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        details_layout.addWidget(self.example_title)
        
        self.example_description = QLabel()
        self.example_description.setWordWrap(True)
        self.example_description.setStyleSheet("color: #666; margin-bottom: 5px;")
        details_layout.addWidget(self.example_description)
        
        # Code display
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setMaximumHeight(150)
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.Monospace)
        self.code_text.setFont(font)
        details_layout.addWidget(self.code_text)
        
        # Explanation
        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setMaximumHeight(80)
        details_layout.addWidget(self.explanation_text)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Example")
        self.apply_btn.clicked.connect(self._apply_example)
        self.apply_btn.setEnabled(False)
        details_layout.addWidget(self.apply_btn)
        
        layout.addWidget(details_group)
        
        # Load initial data
        self._load_categories()
        self._load_examples()
    
    def _load_categories(self):
        """Load categories into combo box."""
        categories = self.database.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category)
    
    def _load_examples(self):
        """Load examples into the list."""
        self._filter_examples()
    
    def _filter_examples(self):
        """Filter examples based on search and category."""
        self.examples_list.clear()
        
        search_text = self.search_edit.text().strip()
        selected_category = self.category_combo.currentText()
        
        # Get examples to show
        if search_text:
            examples = self.database.search_examples(search_text)
        elif self.current_context:
            examples = self.database.get_examples_by_context(self.current_context)
        else:
            examples = list(self.database.examples.values())
        
        # Filter by category
        if selected_category != "All Categories":
            examples = [ex for ex in examples if ex.category == selected_category]
        
        # Add to list
        for example in examples:
            item = QListWidgetItem(f"{example.title} ({example.difficulty})")
            item.setData(Qt.UserRole, example)
            self.examples_list.addItem(item)
    
    def _on_example_selected(self, current, previous):
        """Handle example selection."""
        if current:
            example = current.data(Qt.UserRole)
            self._show_example_details(example)
            self.apply_btn.setEnabled(True)
        else:
            self.apply_btn.setEnabled(False)
    
    def _show_example_details(self, example: Example):
        """Show details for the selected example."""
        self.example_title.setText(example.title)
        self.example_description.setText(example.description)
        self.code_text.setPlainText(example.code)
        self.explanation_text.setPlainText(example.explanation)
    
    def _apply_example(self):
        """Apply the selected example."""
        current_item = self.examples_list.currentItem()
        if current_item:
            example = current_item.data(Qt.UserRole)
            self.example_applied.emit(example.code)
    
    def set_context(self, context: str):
        """Set the current context and update examples."""
        self.current_context = context
        self.context_label.setText(f"Context: {context.replace('_', ' ').title()}")
        self._filter_examples()


# Global examples database instance
examples_database = ExamplesDatabase()
