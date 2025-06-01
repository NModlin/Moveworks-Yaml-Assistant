#!/usr/bin/env python3
"""
Test script to verify font readability in the interactive tutorial system.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tutorial_font_readability():
    """Test font readability in the tutorial system."""
    print("🧪 Testing Tutorial Font Readability")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
        from PySide6.QtWidgets import QLineEdit, QTextEdit, QPushButton, QLabel
        from tutorials import UnifiedTutorialManager as InteractiveTutorialManager, InteractiveTutorialStep, InteractiveTutorialOverlay
        
        # Create minimal app for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create test window that simulates the main application
        window = QMainWindow()
        window.setWindowTitle("Tutorial Font Readability Test")
        window.setGeometry(100, 100, 800, 600)
        
        # Create central widget with test UI elements
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🔍 Tutorial Font Readability Test")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Test target field
        target_label = QLabel("Target Field (for copy-paste testing):")
        layout.addWidget(target_label)
        
        target_field = QLineEdit()
        target_field.setObjectName("action_name_edit")
        target_field.setPlaceholderText("Tutorial will auto-fill this field...")
        target_field.setStyleSheet("""
            QLineEdit {
                color: #2c3e50;
                font-size: 14px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 10px;
                min-height: 20px;
            }
        """)
        layout.addWidget(target_field)
        
        # Instructions
        instructions = QLabel("""
📋 Tutorial Font Readability Test Instructions:

1. Click "Start Tutorial Font Test" below
2. A floating tutorial panel should appear with copy-paste content
3. Check the following text elements for readability:

✅ Expected High-Contrast Text:
• Step title: Dark text, clearly readable
• Step description: Dark text (#2c3e50) on transparent background
• Instruction text: Dark text (#2c3e50) on light background (#f8f9fa)
• Copy-paste text area: Dark text (#2c3e50) on white background (#ffffff)
• Copy-paste label: Green text (#28a745) for emphasis

❌ Check for Issues:
• Light or white text on light backgrounds
• Poor contrast that makes text hard to read
• Inconsistent font styling across tutorial elements

🎯 Specific Test for Step 3:
The copy-paste text area should show dark, clearly readable text
when it contains the sample code or configuration data.
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 6px; 
                font-size: 12px; 
                color: #2c3e50;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(instructions)
        
        # Start tutorial button
        start_tutorial_btn = QPushButton("🚀 Start Tutorial Font Test")
        start_tutorial_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        def start_font_test():
            # Create tutorial overlay
            overlay = InteractiveTutorialOverlay(window)
            
            # Test step with copy-paste content (like Step 3 mentioned in the issue)
            step = InteractiveTutorialStep(
                title="Font Readability Test - Copy-Paste Content",
                description="This step tests the font readability in the copy-paste section. The text below should be clearly readable with dark text on a white background.",
                instruction="Check the copy-paste text area below. The text should be dark (#2c3e50) on a white background (#ffffff) for optimal readability. Click the copy button to test auto-fill functionality.",
                target_element="action_name_edit",
                action_type="copy_paste",
                copy_paste_data="""# Sample script code for testing font readability
user_name = data.user_info.user.name
user_email = data.user_info.user.email
user_dept = data.user_info.user.department

# Create a greeting message
greeting = f"Hello, {user_name}!"
summary = f"User {user_name} from {user_dept} department"

# Return processed data
return {
    "greeting": greeting,
    "user_name": user_name,
    "user_email": user_email,
    "summary": summary
}"""
            )
            
            # Find the target widget
            target_widget = window.findChild(QWidget, "action_name_edit")
            
            # Show the step
            overlay.show_step(step, target_widget, 3, 16)  # Simulate Step 3 of 16
            
            print("✅ Tutorial font test started")
            print("🔍 Check the floating tutorial panel for font readability")
            print("📝 Specifically check the copy-paste text area")
        
        start_tutorial_btn.clicked.connect(start_font_test)
        layout.addWidget(start_tutorial_btn)
        
        # Status display
        status_label = QLabel("Status: Ready for font readability testing")
        status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        layout.addWidget(status_label)
        
        window.show()
        
        print("✅ Tutorial font readability test window created successfully")
        print("📋 Manual Testing Required:")
        print("   1. Click 'Start Tutorial Font Test'")
        print("   2. Check floating tutorial panel appears")
        print("   3. Verify all text elements are clearly readable")
        print("   4. Specifically check copy-paste text area")
        print("   5. Test copy-paste auto-fill functionality")
        print("\n⏳ Close the test window when done...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Tutorial font readability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tutorial font readability test."""
    print("🚀 Tutorial Font Readability Test")
    print("=" * 70)
    
    success = test_tutorial_font_readability()
    
    print("\n" + "=" * 70)
    if success == 0:  # QApplication.exec() returns 0 on normal exit
        print("✅ Tutorial font readability test completed!")
        print("   If all text was clearly readable, the font fixes are working!")
    else:
        print("❌ Tutorial font readability test failed")
    
    return success == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
