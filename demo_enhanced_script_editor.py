#!/usr/bin/env python3
"""
Demonstration of the Enhanced Script Editor for APIthon scripts.

This script shows how the enhanced script editor provides real-time validation,
resource monitoring, and educational feedback for APIthon script development.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from core_structures import ScriptStep
from enhanced_script_editor import EnhancedScriptEditor
from enhanced_apiton_validator import APIthonValidationResult


class DemoWindow(QMainWindow):
    """Demo window for the enhanced script editor."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced APIthon Script Editor Demo")
        self.setGeometry(100, 100, 1000, 700)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the demo UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Demo buttons
        demo_buttons = [
            ("Valid Script", self._load_valid_script),
            ("Assignment Issue", self._load_assignment_issue),
            ("Citation Format", self._load_citation_format),
            ("Resource Limits", self._load_resource_limits),
            ("Multiple Issues", self._load_multiple_issues),
            ("Clear", self._clear_script)
        ]
        
        for button_text, callback in demo_buttons:
            btn = QPushButton(button_text)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            header_layout.addWidget(btn)
            
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Enhanced script editor
        self.script_editor = EnhancedScriptEditor()
        self.script_editor.validation_updated.connect(self._on_validation_updated)
        layout.addWidget(self.script_editor)
        
        # Initialize with a sample script
        self._load_valid_script()
        
    def _load_valid_script(self):
        """Load a valid APIthon script example."""
        script = ScriptStep(
            code="""# Process user information
user_name = data.user_info.name
user_email = meta_info.user.email

# Create response
response = {
    "greeting": f"Hello, {user_name}!",
    "contact": user_email,
    "timestamp": "2024-01-01",
    "status": "processed"
}

return response""",
            output_key="user_response",
            description="Process user information and create response"
        )
        
        available_paths = {
            "data.user_info.name",
            "data.user_info.id", 
            "meta_info.user.email",
            "meta_info.user.name"
        }
        
        self.script_editor.set_script_step(script, available_paths)
        
    def _load_assignment_issue(self):
        """Load a script with assignment issue (common mistake)."""
        script = ScriptStep(
            code="""# Common mistake: assignment as last line
user_name = data.user_info.name
result = {"greeting": f"Hello, {user_name}!"}""",
            output_key="greeting_result",
            description="Script with assignment issue"
        )
        
        available_paths = {"data.user_info.name"}
        self.script_editor.set_script_step(script, available_paths)
        
    def _load_citation_format(self):
        """Load a script demonstrating citation format validation."""
        script = ScriptStep(
            code="""# Citation format example
search_result = {
    "id": "doc_123",
    "friendly_id": "user_guide_123", 
    "title": "User Guide - Getting Started",
    "url": "https://docs.example.com/user-guide",
    "snippet": "This guide helps you get started with the platform..."
}

return search_result""",
            output_key="result",  # Reserved name for citations
            description="Citation format example"
        )
        
        self.script_editor.set_script_step(script, set())
        
    def _load_resource_limits(self):
        """Load a script that approaches resource limits."""
        # Create a script with a long string to demonstrate size warnings
        long_comment = "# " + "This is a very long comment. " * 50
        script = ScriptStep(
            code=f"""{long_comment}

# This script demonstrates resource usage monitoring
large_string = "{'x' * 1000}"
numbers = [1, 2, 3, 4294967295]  # Max uint32 value

result = {{
    "data": large_string,
    "numbers": numbers,
    "size_info": "This script is getting large"
}}

return result""",
            output_key="large_data",
            description="Script demonstrating resource limits"
        )
        
        self.script_editor.set_script_step(script, set())
        
    def _load_multiple_issues(self):
        """Load a script with multiple validation issues."""
        script = ScriptStep(
            code="""import json  # ❌ Not allowed

# ❌ Private identifier
_secret_data = "confidential"

# ❌ Undefined data reference
user_name = data.nonexistent_field

# ❌ Assignment as last line (no return)
result = {"error": "multiple issues"}""",
            output_key="results",  # Reserved name but wrong format
            description="Script with multiple issues"
        )
        
        self.script_editor.set_script_step(script, {"data.user_info.name"})
        
    def _clear_script(self):
        """Clear the script editor."""
        script = ScriptStep(
            code="",
            output_key="",
            description=""
        )
        
        self.script_editor.set_script_step(script, set())
        
    def _on_validation_updated(self, result: APIthonValidationResult):
        """Handle validation updates from the script editor."""
        # Print validation results to console for demo purposes
        print("\n" + "="*50)
        print("VALIDATION UPDATE")
        print("="*50)
        print(f"Valid: {result.is_valid}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        print(f"Suggestions: {len(result.suggestions)}")
        
        if result.resource_usage:
            print(f"Code size: {result.resource_usage.get('code_bytes', 0)} bytes")
            
        if result.return_analysis:
            print(f"Last statement: {result.return_analysis.get('last_statement_type', 'Unknown')}")
            print(f"Has return: {result.return_analysis.get('has_explicit_return', False)}")
            
        if result.citation_compliance.get('is_reserved'):
            print(f"Citation compliance: {result.citation_compliance.get('compliance_status', 'unknown')}")
            
        if result.errors:
            print("\nErrors:")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
                
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings[:3]:  # Show first 3 warnings
                print(f"  - {warning}")
                
        if result.suggestions:
            print("\nSuggestions:")
            for suggestion in result.suggestions[:3]:  # Show first 3 suggestions
                print(f"  - {suggestion}")


def main():
    """Run the enhanced script editor demo."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the demo window
    window = DemoWindow()
    window.show()
    
    print("Enhanced APIthon Script Editor Demo")
    print("="*50)
    print("Features demonstrated:")
    print("- Real-time validation with visual feedback")
    print("- Resource constraint monitoring (code size, string length, numeric ranges)")
    print("- Return value logic analysis (assignment vs expression detection)")
    print("- Citation format validation for reserved output_key names")
    print("- Educational tooltips and suggestions")
    print("- Comprehensive error reporting with fix suggestions")
    print("\nClick the demo buttons to see different validation scenarios!")
    print("Validation results will be printed to this console.")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
