#!/usr/bin/env python3
"""
Test script to verify the interactive tutorial functionality.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_interactive_tutorial():
    """Test the interactive tutorial system."""
    print("🧪 Testing Interactive Tutorial System")
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
        window.setWindowTitle("Interactive Tutorial Test - Non-Blocking Overlay")
        window.setGeometry(100, 100, 1200, 800)
        
        # Create central widget with test UI elements
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🎯 Interactive Tutorial Test")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Test action name field (simulates the real one)
        action_name_label = QLabel("Action Name:")
        layout.addWidget(action_name_label)
        
        action_name_edit = QLineEdit()
        action_name_edit.setObjectName("action_name_edit")  # This is how tutorial will find it
        action_name_edit.setPlaceholderText("e.g., mw.get_user_by_email")
        action_name_edit.setStyleSheet("""
            QLineEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                min-height: 25px;
            }
        """)
        layout.addWidget(action_name_edit)
        
        # Test output key field
        output_key_label = QLabel("Output Key:")
        layout.addWidget(output_key_label)
        
        output_key_edit = QLineEdit()
        output_key_edit.setObjectName("output_key_edit")
        output_key_edit.setPlaceholderText("e.g., user_info")
        output_key_edit.setStyleSheet("""
            QLineEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                min-height: 25px;
            }
        """)
        layout.addWidget(output_key_edit)
        
        # Test script code area
        script_label = QLabel("Script Code:")
        layout.addWidget(script_label)
        
        script_code_edit = QTextEdit()
        script_code_edit.setObjectName("script_code_edit")
        script_code_edit.setPlaceholderText("Enter your script code here...")
        script_code_edit.setMaximumHeight(150)
        script_code_edit.setStyleSheet("""
            QTextEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(script_code_edit)
        
        # Test button
        test_btn = QPushButton("🎯 Start Interactive Tutorial Test")
        test_btn.setObjectName("add_action_btn")  # Simulate the add action button
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(test_btn)
        
        # Instructions
        instructions = QLabel("""
📋 Interactive Tutorial Test Instructions:

1. Click the "Start Interactive Tutorial Test" button below
2. The tutorial overlay should appear with step-by-step instructions
3. You should be able to:
   • Click on the highlighted UI elements (action name field, output key field, etc.)
   • Use the copy-paste functionality to auto-fill fields
   • Navigate through tutorial steps with Previous/Next buttons
   • Interact with the underlying UI while the tutorial is active

✅ Expected Behavior:
• Tutorial overlay appears but doesn't block interaction
• You can click and type in the form fields
• Copy-paste buttons auto-fill the target fields
• Tutorial highlights the correct elements
• Navigation buttons work properly

❌ If you see issues:
• Overlay blocks interaction → Mouse events not passing through
• Can't click fields → Target highlighting not working
• Copy-paste doesn't work → Auto-fill functionality broken
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
        
        window.show()
        
        # Create tutorial manager
        tutorial_manager = InteractiveTutorialManager(window)
        
        # Create a test tutorial step
        def start_test_tutorial():
            # Create tutorial overlay
            overlay = InteractiveTutorialOverlay(window)
            
            # Test step 1: Action name
            step1 = InteractiveTutorialStep(
                title="Step 1: Configure Action Name",
                description="Let's fill in the action name field with a copy-paste example.",
                instruction="Click the copy button below to auto-fill the Action Name field, or manually click in the field and paste.",
                target_element="action_name_edit",
                action_type="copy_paste",
                copy_paste_data="mw.get_user_by_email"
            )
            
            # Find the target widget
            target_widget = window.findChild(QWidget, "action_name_edit")
            
            # Show the step
            overlay.show_step(step1, target_widget, 1, 3)
            
            # Connect navigation
            def next_step():
                # Step 2: Output key
                step2 = InteractiveTutorialStep(
                    title="Step 2: Configure Output Key",
                    description="Now let's set the output key for this action.",
                    instruction="Click the copy button to auto-fill the Output Key field.",
                    target_element="output_key_edit",
                    action_type="copy_paste",
                    copy_paste_data="user_info"
                )
                target_widget2 = window.findChild(QWidget, "output_key_edit")
                overlay.show_step(step2, target_widget2, 2, 3)
                
                def final_step():
                    # Step 3: Script code
                    step3 = InteractiveTutorialStep(
                        title="Step 3: Add Script Code",
                        description="Finally, let's add some processing script code.",
                        instruction="Click the copy button to auto-fill the script area with sample code.",
                        target_element="script_code_edit",
                        action_type="copy_paste",
                        copy_paste_data="user_name = data.user_info.user.name\nreturn {'greeting': f'Hello, {user_name}!'}"
                    )
                    target_widget3 = window.findChild(QWidget, "script_code_edit")
                    overlay.show_step(step3, target_widget3, 3, 3)
                
                overlay.next_step_requested.disconnect()
                overlay.next_step_requested.connect(final_step)
            
            overlay.next_step_requested.connect(next_step)
            
            return overlay
        
        # Connect the test button
        test_btn.clicked.connect(start_test_tutorial)
        
        print("✅ Interactive tutorial test window created successfully")
        print("📋 Manual Testing Required:")
        print("   1. Click the 'Start Interactive Tutorial Test' button")
        print("   2. Verify tutorial overlay appears")
        print("   3. Test interaction with form fields")
        print("   4. Test copy-paste auto-fill functionality")
        print("   5. Test tutorial navigation")
        print("\n⏳ Close the test window when done...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Interactive tutorial test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the interactive tutorial test."""
    print("🚀 Interactive Tutorial Test")
    print("=" * 70)
    
    success = test_interactive_tutorial()
    
    print("\n" + "=" * 70)
    if success == 0:  # QApplication.exec() returns 0 on normal exit
        print("✅ Interactive tutorial test completed!")
        print("   If the tutorial was interactive and functional, the fix is working!")
    else:
        print("❌ Interactive tutorial test failed")
    
    return success == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
