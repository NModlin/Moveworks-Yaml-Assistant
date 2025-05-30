#!/usr/bin/env python3
"""
Test script to verify the tutorial overlay buttons are working correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tutorial_overlay():
    """Test the tutorial overlay button creation."""
    print("🧪 Testing Tutorial Overlay Button Creation")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        from integrated_tutorial_system import InteractiveTutorialOverlay, InteractiveTutorialStep
        
        # Create minimal app for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create test window
        window = QMainWindow()
        window.setGeometry(100, 100, 800, 600)
        window.show()
        
        # Create tutorial overlay
        overlay = InteractiveTutorialOverlay(window)
        
        # Create test step
        test_step = InteractiveTutorialStep(
            title="Test Step",
            description="This is a test step to verify button creation",
            instruction="This should show Previous, Skip Tutorial, and Next buttons at the bottom",
            action_type="info"
        )
        
        # Show the step
        overlay.show_step(test_step, None, 1, 5)
        
        print("✅ Tutorial overlay created successfully")
        print(f"   Previous button exists: {hasattr(overlay, 'previous_btn')}")
        print(f"   Skip button exists: {hasattr(overlay, 'skip_btn')}")
        print(f"   Next button exists: {hasattr(overlay, 'next_btn')}")
        
        if hasattr(overlay, 'previous_btn'):
            print(f"   Previous button visible: {overlay.previous_btn.isVisible()}")
            print(f"   Previous button size: {overlay.previous_btn.size()}")
            print(f"   Previous button text: '{overlay.previous_btn.text()}'")
        
        if hasattr(overlay, 'skip_btn'):
            print(f"   Skip button visible: {overlay.skip_btn.isVisible()}")
            print(f"   Skip button size: {overlay.skip_btn.size()}")
            print(f"   Skip button text: '{overlay.skip_btn.text()}'")
        
        if hasattr(overlay, 'next_btn'):
            print(f"   Next button visible: {overlay.next_btn.isVisible()}")
            print(f"   Next button size: {overlay.next_btn.size()}")
            print(f"   Next button text: '{overlay.next_btn.text()}'")
        
        print(f"   Instruction panel size: {overlay.instruction_panel.size()}")
        print(f"   Instruction panel visible: {overlay.instruction_panel.isVisible()}")
        
        # Test button functionality
        def test_next():
            print("🎯 Next button clicked!")
        
        def test_previous():
            print("🎯 Previous button clicked!")
        
        def test_skip():
            print("🎯 Skip button clicked!")
        
        overlay.next_step_requested.connect(test_next)
        overlay.previous_step_requested.connect(test_previous)
        overlay.tutorial_cancelled.connect(test_skip)
        
        print("\n📋 Instructions for Manual Testing:")
        print("1. Look for the tutorial overlay on the window")
        print("2. Check if you can see Previous, Skip Tutorial, and Next buttons")
        print("3. Try clicking each button to test functionality")
        print("4. Close the window when done testing")
        
        # Keep the app running for manual testing
        print("\n⏳ App running for manual testing... Close the window to exit.")
        return app.exec()
        
    except Exception as e:
        print(f"❌ Tutorial overlay test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tutorial overlay test."""
    print("🚀 Tutorial Overlay Button Test")
    print("=" * 60)
    
    success = test_tutorial_overlay()
    
    print("\n" + "=" * 60)
    if success == 0:  # QApplication.exec() returns 0 on normal exit
        print("✅ Tutorial overlay test completed successfully!")
        print("   If you saw the buttons in the overlay, the fix is working!")
    else:
        print("❌ Tutorial overlay test failed")
    
    return success == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
