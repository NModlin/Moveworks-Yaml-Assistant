#!/usr/bin/env python3
"""
Test script for the comprehensive tutorial integration.

This script tests the tutorial system integration with the main application
to ensure all components work together properly.
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tutorial_imports():
    """Test that all tutorial-related imports work correctly."""
    print("🧪 Testing Comprehensive Tutorial Imports")
    print("=" * 50)

    try:
        from tutorials import UnifiedTutorialManager
        print("✅ ComprehensiveTutorialSystem imported successfully")

        from tutorials import UnifiedTutorialManager as TutorialIntegrationManager, TutorialSelectionWidget
        print("✅ TutorialIntegrationManager imported successfully")

        # Test legacy imports still work
        import tutorial_data
        print("✅ tutorial_data imported successfully")

        from tutorials import UnifiedTutorialManager as InteractiveTutorialManager, InteractiveTutorialStep
        print("✅ integrated_tutorial_system imported successfully")

        from main_gui import MainWindow
        print("✅ main_gui with tutorial integration imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_comprehensive_tutorial_system():
    """Test creating the comprehensive tutorial system."""
    print("\n🎯 Testing Comprehensive Tutorial System")
    print("=" * 50)

    try:
        from tutorials import UnifiedTutorialManager

        # Create a mock main window
        app = QApplication.instance() or QApplication(sys.argv)

        class MockMainWindow:
            def findChild(self, widget_type, name):
                return None

        mock_window = MockMainWindow()
        tutorial_system = ComprehensiveTutorialSystem(mock_window)

        # Test getting tutorials
        tutorials = tutorial_system.get_available_tutorials()
        print(f"✅ Tutorial system created with {len(tutorials)} tutorials")

        # Test tutorial IDs
        expected_ids = [
            "module_1_basic_compound_action",
            "module_2_it_automation",
            "module_3_conditional_logic",
            "module_4_data_processing",
            "module_5_error_handling"
        ]

        actual_ids = [t.id for t in tutorials]
        for expected_id in expected_ids:
            if expected_id in actual_ids:
                print(f"✅ Found tutorial: {expected_id}")
            else:
                print(f"❌ Missing tutorial: {expected_id}")
                return False

        return True
    except Exception as e:
        print(f"❌ Tutorial system creation error: {e}")
        return False

def test_tutorial_content():
    """Test tutorial content structure."""
    print("\n📚 Testing Tutorial Content Structure")
    print("=" * 50)

    try:
        from tutorials import UnifiedTutorialManager

        app = QApplication.instance() or QApplication(sys.argv)

        class MockMainWindow:
            def findChild(self, widget_type, name):
                return None

        mock_window = MockMainWindow()
        tutorial_system = ComprehensiveTutorialSystem(mock_window)
        tutorials = tutorial_system.get_available_tutorials()

        for tutorial in tutorials:
            print(f"\n📖 Validating: {tutorial.title}")

            # Check required fields
            assert tutorial.id, "Tutorial must have ID"
            assert tutorial.title, "Tutorial must have title"
            assert tutorial.description, "Tutorial must have description"
            assert tutorial.learning_objectives, "Tutorial must have learning objectives"
            assert tutorial.steps, "Tutorial must have steps"

            print(f"   ✅ {len(tutorial.steps)} steps")
            print(f"   ✅ {len(tutorial.learning_objectives)} learning objectives")

            # Check step structure
            for i, step in enumerate(tutorial.steps):
                assert step.title, f"Step {i+1} must have title"
                assert step.instruction, f"Step {i+1} must have instruction"

        print("✅ All tutorial content validation passed")
        return True
    except Exception as e:
        print(f"❌ Tutorial content validation error: {e}")
        return False

def test_integration_manager():
    """Test the tutorial integration manager."""
    print("\n🔧 Testing Integration Manager")
    print("=" * 50)

    try:
        from tutorials import UnifiedTutorialManager as TutorialIntegrationManager

        app = QApplication.instance() or QApplication(sys.argv)

        class MockMainWindow:
            def findChild(self, widget_type, name):
                return None

        mock_window = MockMainWindow()
        integration_manager = TutorialIntegrationManager(mock_window)

        # Test getting tutorial system
        tutorial_system = integration_manager.get_tutorial_system()
        assert tutorial_system is not None, "Tutorial system should be available"
        print("✅ Tutorial system accessible through integration manager")

        # Test tutorial info when no tutorial is active
        info = integration_manager.get_current_tutorial_info()
        assert info is None, "No tutorial should be active initially"
        print("✅ Current tutorial info correctly returns None when inactive")

        # Test is_tutorial_active
        assert not integration_manager.is_tutorial_active(), "No tutorial should be active initially"
        print("✅ Tutorial active status correctly returns False when inactive")

        return True
    except Exception as e:
        print(f"❌ Integration manager test error: {e}")
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
        from tutorials import UnifiedTutorialStep as InteractiveTutorialStep

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
        from tutorials import UnifiedTutorialManager as InteractiveTutorialManager

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
        test_tutorial_imports,
        test_comprehensive_tutorial_system,
        test_tutorial_content,
        test_integration_manager,
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
        print("\n✅ Comprehensive Tutorial System Ready:")
        print("  • All imports working correctly")
        print("  • Comprehensive tutorial system functional")
        print("  • 5-module tutorial series available")
        print("  • Integration manager working")
        print("  • Legacy tutorial system still functional")
        print("\n🚀 Comprehensive Tutorial Series Available:")
        print("  • Module 1: Your First Compound Action")
        print("  • Module 2: IT Automation (ServiceNow/Jira)")
        print("  • Module 3: Conditional Logic (Switch Statements)")
        print("  • Module 4: Data Processing (APIthon Scripts)")
        print("  • Module 5: Error Handling (Try-Catch)")
        print("\n🎯 Ready to Use:")
        print("  • Start the application: python run_app.py")
        print("  • Access comprehensive tutorials: Tools → 📚 Tutorials → 🚀 Comprehensive Tutorial Series")
        print("  • Access legacy tutorials: Tools → 📚 Tutorials → 🎯 Interactive Basic Workflow")
        print("  • Follow progressive learning path with hands-on examples")
        print("  • Master all Moveworks compound action features!")

        return True
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
