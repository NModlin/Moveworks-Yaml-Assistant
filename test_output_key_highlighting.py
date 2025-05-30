#!/usr/bin/env python3
"""
Test script to specifically verify the output key field highlighting in Step 3 of the tutorial.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_output_key_highlighting():
    """Test the output key field highlighting in the tutorial."""
    print("🎯 Testing Output Key Field Highlighting")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
        from PySide6.QtWidgets import QLineEdit, QTextEdit, QPushButton, QLabel, QHBoxLayout
        from integrated_tutorial_system import InteractiveTutorialManager, InteractiveTutorialStep, InteractiveTutorialOverlay
        
        # Create minimal app for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create test window that simulates the main application structure
        window = QMainWindow()
        window.setWindowTitle("Output Key Highlighting Test")
        window.setGeometry(100, 100, 1200, 800)
        
        # Create central widget with test UI elements that match the real app structure
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Left panel (simulates workflow steps)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("📋 Workflow Steps"))
        
        # Add action button (for Step 1)
        add_action_btn = QPushButton("➕ Add Action")
        add_action_btn.setObjectName("add_action_btn")
        add_action_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(add_action_btn)
        
        left_layout.addStretch()
        left_panel.setFixedWidth(250)
        layout.addWidget(left_panel)
        
        # Center panel (simulates configuration area)
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.addWidget(QLabel("⚙️ Configuration"))
        
        # Create a config_panel attribute to match the real app structure
        config_panel = QWidget()
        config_layout = QVBoxLayout(config_panel)
        
        # Action Name field (for Step 2)
        config_layout.addWidget(QLabel("Action Name:"))
        action_name_edit = QLineEdit()
        action_name_edit.setObjectName("action_name_edit")
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
        config_layout.addWidget(action_name_edit)
        
        # Output Key field (for Step 3) - This is the main test target
        config_layout.addWidget(QLabel("Output Key:"))
        action_output_key_edit = QLineEdit()
        action_output_key_edit.setObjectName("action_output_key_edit")  # Real app uses this name
        action_output_key_edit.setPlaceholderText("e.g., user_info")
        action_output_key_edit.setStyleSheet("""
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
        config_layout.addWidget(action_output_key_edit)
        
        # Add the config_panel to the window so the tutorial can find it
        window.config_panel = config_panel
        
        center_layout.addWidget(config_panel)
        center_layout.addStretch()
        layout.addWidget(center_panel)
        
        # Right panel (simulates JSON explorer, etc.)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("🔍 JSON Explorer / YAML Preview"))
        right_layout.addStretch()
        right_panel.setFixedWidth(300)
        layout.addWidget(right_panel)
        
        # Test instructions
        instructions = QLabel("""
🎯 Output Key Highlighting Test Instructions:

1. Click "Start Step 3 Test" below
2. The tutorial should show Step 3: "Set the Output Key"
3. A green highlight border should appear around the "Output Key" input field
4. The floating tutorial panel should appear with copy-paste content

✅ Expected Results:
• Green highlight border around the Output Key field
• Floating tutorial panel with "user_info" copy-paste content
• Field should be clearly identified and interactive

❌ Check for Issues:
• No green highlight appearing
• Highlight appearing around wrong element
• Tutorial panel not positioning correctly
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 6px; 
                font-size: 11px; 
                color: #2c3e50;
                border: 1px solid #dee2e6;
            }
        """)
        instructions.setWordWrap(True)
        
        # Add instructions at the top
        main_layout = QVBoxLayout()
        main_layout.addWidget(instructions)
        main_layout.addWidget(central_widget)
        
        container = QWidget()
        container.setLayout(main_layout)
        window.setCentralWidget(container)
        
        # Test button
        test_btn = QPushButton("🎯 Start Step 3 Test (Output Key Highlighting)")
        test_btn.setStyleSheet("""
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
        
        def start_step3_test():
            # Create tutorial overlay
            overlay = InteractiveTutorialOverlay(window)
            
            # Create Step 3 specifically (the output key step)
            step3 = InteractiveTutorialStep(
                title="Step 3: Set the Output Key",
                description="The output key determines how we'll reference this step's data later.",
                instruction="In the <b>'Output Key'</b> field, copy and paste the text below. This will let us access the user data as 'data.user_info' in later steps:",
                target_element="output_key_edit",
                action_type="copy_paste",
                copy_paste_data="user_info"
            )
            
            # Create tutorial manager to test widget finding
            tutorial_manager = InteractiveTutorialManager(window)
            target_widget = tutorial_manager._find_target_widget("output_key_edit")
            
            print(f"🔍 Step 3 Test Results:")
            print(f"   Target element: output_key_edit")
            print(f"   Found widget: {target_widget}")
            if target_widget:
                print(f"   Widget class: {target_widget.__class__.__name__}")
                print(f"   Widget object name: {target_widget.objectName()}")
                print(f"   Widget visible: {target_widget.isVisible()}")
                print(f"   Widget geometry: {target_widget.geometry()}")
            
            # Show the step with highlighting
            overlay.show_step(step3, target_widget, 3, 16)  # Step 3 of 16
            
            print("✅ Step 3 test started")
            print("🔍 Check for green highlight around the Output Key field")
        
        test_btn.clicked.connect(start_step3_test)
        main_layout.addWidget(test_btn)
        
        window.show()
        
        print("✅ Output key highlighting test window created successfully")
        print("📋 Manual Testing Required:")
        print("   1. Click 'Start Step 3 Test'")
        print("   2. Verify green highlight appears around Output Key field")
        print("   3. Check floating tutorial panel appears with copy-paste content")
        print("   4. Test copy-paste auto-fill functionality")
        print("\n⏳ Close the test window when done...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Output key highlighting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the output key highlighting test."""
    print("🚀 Output Key Highlighting Test")
    print("=" * 70)
    
    success = test_output_key_highlighting()
    
    print("\n" + "=" * 70)
    if success == 0:  # QApplication.exec() returns 0 on normal exit
        print("✅ Output key highlighting test completed!")
        print("   If green highlight appeared around the Output Key field, the fix is working!")
    else:
        print("❌ Output key highlighting test failed")
    
    return success == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
