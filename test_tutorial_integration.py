#!/usr/bin/env python3
"""
Test script to verify the integrated tutorial system is working correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all tutorial-related modules can be imported."""
    print("🧪 Testing Tutorial System Imports")
    print("=" * 50)

    try:
        # Test tutorial_data import
        import tutorial_data
        print("✅ tutorial_data imported successfully")

        # Test integrated_tutorial_system import
        from integrated_tutorial_system import InteractiveTutorialManager, InteractiveTutorialStep
        print("✅ integrated_tutorial_system imported successfully")

        # Test main_gui integration
        from main_gui import MainWindow
        print("✅ main_gui with tutorial integration imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_tutorial_data():
    """Test tutorial data functionality."""
    print("\n📚 Testing Tutorial Data")
    print("=" * 50)

    try:
        from tutorial_data import get_tutorial_json_data, get_tutorial_script_example

        # Test basic tutorial data
        basic_data = get_tutorial_json_data("interactive_basic")
        print(f"✅ Basic tutorial JSON data: {len(basic_data)} keys")
        print(f"   User name: {basic_data.get('user', {}).get('name', 'N/A')}")

        # Test script example
        script_example = get_tutorial_script_example("interactive_basic")
        print(f"✅ Script example: {len(script_example)} characters")
        first_line = script_example.split('\n')[0]
        print(f"   First line: {first_line}")

        return True

    except Exception as e:
        print(f"❌ Tutorial data error: {e}")
        return False

def test_tutorial_steps():
    """Test tutorial step creation."""
    print("\n🎯 Testing Tutorial Steps")
    print("=" * 50)

    try:
        from integrated_tutorial_system import InteractiveTutorialStep

        # Test basic step
        step = InteractiveTutorialStep(
            title="Test Step",
            description="This is a test step",
            instruction="Click the button to continue",
            target_element="add_action_btn",
            action_type="click"
        )

        print(f"✅ Created step: {step.title}")
        print(f"   Target: {step.target_element}")
        print(f"   Action: {step.action_type}")

        # Test copy-paste step
        copy_step = InteractiveTutorialStep(
            title="Copy-Paste Step",
            description="Test copy-paste functionality",
            instruction="Copy and paste the text below",
            action_type="copy_paste",
            copy_paste_data="mw.get_user_by_email"
        )

        print(f"✅ Created copy-paste step: {copy_step.title}")
        print(f"   Copy data: {copy_step.copy_paste_data}")

        return True

    except Exception as e:
        print(f"❌ Tutorial step error: {e}")
        return False

def test_tutorial_manager():
    """Test tutorial manager creation."""
    print("\n🎛️ Testing Tutorial Manager")
    print("=" * 50)

    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        from integrated_tutorial_system import InteractiveTutorialManager

        # Create minimal app for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create test window
        window = QMainWindow()

        # Create tutorial manager
        manager = InteractiveTutorialManager(window)

        # Test tutorial availability
        tutorials = manager.get_available_tutorials()
        print(f"✅ Tutorial manager created successfully")
        print(f"   Available tutorials: {len(tutorials)}")

        for tutorial in tutorials:
            print(f"   • {tutorial['title']} ({tutorial['difficulty']})")
            print(f"     {tutorial['description']}")
            print(f"     Estimated time: {tutorial['estimated_time']}")

        return True

    except Exception as e:
        print(f"❌ Tutorial manager error: {e}")
        return False

def main():
    """Run all tutorial integration tests."""
    print("🚀 Tutorial Integration Test")
    print("=" * 60)

    tests = [
        test_imports,
        test_tutorial_data,
        test_tutorial_steps,
        test_tutorial_manager
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 60)
    if passed == total:
        print("🎉 ALL TUTORIAL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Tutorial System Ready:")
        print("  • All imports working correctly")
        print("  • Tutorial data loading successfully")
        print("  • Tutorial steps creating properly")
        print("  • Tutorial manager functioning")
        print("\n🎯 Ready to Use:")
        print("  • Start the application: python run_app.py")
        print("  • Access tutorial: Tools → 📚 Tutorials → 🎯 Interactive Basic Workflow")
        print("  • Follow step-by-step guidance with copy-paste examples")
        print("  • Learn workflow creation hands-on!")

        return True
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
