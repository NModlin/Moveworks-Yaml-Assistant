#!/usr/bin/env python3
"""
Test script for ReturnStep UI implementation.

This script tests the new ReturnStep configuration widget and validation.
"""

import sys
from PySide6.QtWidgets import QApplication
from core_structures import Workflow, ActionStep, ReturnStep
from yaml_generator import generate_yaml_string
from main_gui import MainWindow

def test_return_step_creation():
    """Test creating a ReturnStep and generating YAML."""
    print("Testing ReturnStep creation and YAML generation...")
    
    # Create a workflow with an action step and return step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information",
        input_args={"email": "data.input_email"}
    )
    
    return_step = ReturnStep(
        description="Return user summary",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email"
        }
    )
    
    workflow = Workflow(steps=[action_step, return_step])
    
    # Generate YAML
    try:
        yaml_output = generate_yaml_string(workflow, "test_return_workflow")
        print("✅ YAML generation successful!")
        print("\nGenerated YAML:")
        print(yaml_output)
        return True
    except Exception as e:
        print(f"❌ YAML generation failed: {e}")
        return False

def test_return_step_ui():
    """Test the ReturnStep UI components."""
    print("\nTesting ReturnStep UI components...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Create the main window
        window = MainWindow()
        
        # Add a return step to test the UI
        return_step = ReturnStep(
            description="Test return step",
            output_mapper={
                "test_key": "data.test_value"
            }
        )
        
        window.workflow_list.add_step(return_step)
        window.workflow_list.setCurrentRow(0)
        
        # Check if the return config widget is created
        if hasattr(window.config_panel, 'return_config_widget'):
            print("✅ Return config widget created successfully!")

            # Check if the UI components exist
            if hasattr(window.config_panel, 'return_description_edit'):
                print("✅ Return description edit field exists!")

            if hasattr(window.config_panel, 'return_output_mapper_table'):
                print("✅ Return output mapper table exists!")

            if hasattr(window.config_panel, 'return_validation_timer'):
                print("✅ Return validation timer exists!")

            return True
        else:
            print("❌ Return config widget not found!")
            return False
            
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("RETURN STEP IMPLEMENTATION TEST")
    print("=" * 60)
    
    # Test 1: YAML generation
    yaml_test_passed = test_return_step_creation()
    
    # Test 2: UI components
    ui_test_passed = test_return_step_ui()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print(f"YAML Generation: {'✅ PASSED' if yaml_test_passed else '❌ FAILED'}")
    print(f"UI Components: {'✅ PASSED' if ui_test_passed else '❌ FAILED'}")
    
    if yaml_test_passed and ui_test_passed:
        print("\n🎉 All tests passed! ReturnStep implementation is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
