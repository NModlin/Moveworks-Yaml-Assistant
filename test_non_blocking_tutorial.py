#!/usr/bin/env python3
"""
Test script to verify the non-blocking interactive tutorial functionality.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_non_blocking_tutorial():
    """Test the non-blocking interactive tutorial system."""
    print("🧪 Testing Non-Blocking Interactive Tutorial System")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
        from PySide6.QtWidgets import QLineEdit, QTextEdit, QPushButton, QLabel
        from integrated_tutorial_system import InteractiveTutorialManager, InteractiveTutorialStep, InteractiveTutorialOverlay
        
        # Create minimal app for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create test window that simulates the main application
        window = QMainWindow()
        window.setWindowTitle("Non-Blocking Tutorial Test - Should Allow Interaction")
        window.setGeometry(100, 100, 800, 600)
        
        # Create central widget with test UI elements
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🎯 Non-Blocking Tutorial Test")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Test button that should be clickable during tutorial
        test_btn = QPushButton("🎯 Click Me During Tutorial!")
        test_btn.setObjectName("add_action_btn")  # This is what tutorial will target
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 15px 20px;
                font-size: 16px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        click_count = [0]  # Use list to allow modification in nested function
        
        def on_button_click():
            click_count[0] += 1
            test_btn.setText(f"✅ Clicked {click_count[0]} times!")
            print(f"🎉 Button clicked {click_count[0]} times - Tutorial is NOT blocking!")
        
        test_btn.clicked.connect(on_button_click)
        layout.addWidget(test_btn)
        
        # Test input field
        input_label = QLabel("Test Input Field (should be typeable during tutorial):")
        layout.addWidget(input_label)
        
        test_input = QLineEdit()
        test_input.setObjectName("action_name_edit")
        test_input.setPlaceholderText("Type here during tutorial to test interaction...")
        test_input.setStyleSheet("""
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
        layout.addWidget(test_input)
        
        # Status display
        status_label = QLabel("Status: Ready for testing")
        status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        layout.addWidget(status_label)
        
        # Instructions
        instructions = QLabel("""
📋 Non-Blocking Tutorial Test Instructions:

1. Click "Start Tutorial" below
2. A floating tutorial panel should appear (separate from main window)
3. The tutorial should highlight the blue button above
4. CRITICAL TEST: You should be able to:
   • Click the blue "Click Me During Tutorial!" button
   • Type in the input field above
   • Interact with all UI elements normally
   • Use the tutorial's copy-paste functionality

✅ Expected Behavior:
• Floating tutorial panel appears separately
• Main window remains fully interactive
• You can click buttons and type while tutorial is active
• Tutorial highlights target elements with green border
• No blocking overlay covering the main window

❌ If tutorial still blocks interaction:
• The floating panel approach needs further refinement
• Mouse events are still being captured somewhere
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
        start_tutorial_btn = QPushButton("🚀 Start Non-Blocking Tutorial Test")
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
        
        def start_test_tutorial():
            status_label.setText("Status: Tutorial started - Test interaction now!")
            status_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
            
            # Create tutorial overlay
            overlay = InteractiveTutorialOverlay(window)
            
            # Test step targeting the button
            step = InteractiveTutorialStep(
                title="Non-Blocking Tutorial Test",
                description="This tutorial should NOT block interaction with the main window.",
                instruction="Try clicking the blue button above and typing in the input field. If you can interact normally, the non-blocking tutorial is working!",
                target_element="add_action_btn",
                action_type="click"
            )
            
            # Find the target widget
            target_widget = window.findChild(QWidget, "add_action_btn")
            
            # Show the step
            overlay.show_step(step, target_widget, 1, 1)
            
            print("✅ Tutorial started - testing non-blocking interaction...")
            print("🎯 Try clicking the blue button and typing in the input field")
        
        start_tutorial_btn.clicked.connect(start_test_tutorial)
        layout.addWidget(start_tutorial_btn)
        
        window.show()
        
        print("✅ Non-blocking tutorial test window created successfully")
        print("📋 Manual Testing Required:")
        print("   1. Click 'Start Non-Blocking Tutorial Test'")
        print("   2. Verify floating tutorial panel appears")
        print("   3. Test clicking the blue button")
        print("   4. Test typing in the input field")
        print("   5. Confirm no interaction is blocked")
        print("\n⏳ Close the test window when done...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Non-blocking tutorial test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the non-blocking tutorial test."""
    print("🚀 Non-Blocking Interactive Tutorial Test")
    print("=" * 70)
    
    success = test_non_blocking_tutorial()
    
    print("\n" + "=" * 70)
    if success == 0:  # QApplication.exec() returns 0 on normal exit
        print("✅ Non-blocking tutorial test completed!")
        print("   If you could interact with UI elements during tutorial, it's working!")
    else:
        print("❌ Non-blocking tutorial test failed")
    
    return success == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
