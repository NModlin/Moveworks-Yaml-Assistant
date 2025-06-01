#!/usr/bin/env python3
"""
Test script for the core functionality of the Moveworks YAML Assistant.

This script tests the core data structures, YAML generation, and validation
without requiring the GUI.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core_structures import ActionStep, ScriptStep, Workflow, DataContext
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate


def test_basic_workflow():
    """Test creating a basic workflow with action and script steps."""
    print("Testing basic workflow creation...")

    # Create an action step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"id": "12345", "name": "John Doe", "email": "john@example.com", "department": "Engineering"}}'
    )

    # Create a script step
    script_step = ScriptStep(
        code="""
# Process user data
user_name = data.user_info.user.name
user_dept = data.user_info.user.department

processed_result = {
    "greeting": f"Hello, {user_name}!",
    "user_id": data.user_info.user.id,
    "department_info": {
        "name": user_dept,
        "is_engineering": user_dept == "Engineering"
    }
}
return processed_result
        """.strip(),
        output_key="processed_data",
        description="Process user information",
        input_args={},
        user_provided_json_output='{"greeting": "Hello, John Doe!", "user_id": "12345", "department_info": {"name": "Engineering", "is_engineering": true}}'
    )

    # Create workflow
    workflow = Workflow(steps=[action_step, script_step])

    print(f"✓ Created workflow with {len(workflow.steps)} steps")
    return workflow


def test_yaml_generation(workflow):
    """Test YAML generation from workflow."""
    print("\nTesting YAML generation...")

    try:
        yaml_output = generate_yaml_string(workflow)
        print("✓ YAML generation successful")
        print("\nGenerated YAML:")
        print("-" * 50)
        print(yaml_output)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"✗ YAML generation failed: {e}")
        return False


def test_data_context():
    """Test data context functionality."""
    print("\nTesting data context...")

    # Create data context with initial inputs
    context = DataContext({"input_email": "test@example.com"})

    # Test initial input access
    try:
        email = context.get_data_value("input_email")
        assert email == "test@example.com"
        print("✓ Initial input access works")
    except Exception as e:
        print(f"✗ Initial input access failed: {e}")
        return False

    # Add step output
    user_data = {
        "user": {
            "id": "12345",
            "name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering"
        }
    }
    context.add_step_output("user_info", user_data)

    # Test step output access
    try:
        user_name = context.get_data_value("user_info.user.name")
        assert user_name == "John Doe"
        print("✓ Step output access works")
    except Exception as e:
        print(f"✗ Step output access failed: {e}")
        return False

    # Test path availability
    assert context.is_path_available("user_info.user.id")
    assert not context.is_path_available("user_info.user.nonexistent")
    print("✓ Path availability checking works")

    return True


def test_validation(workflow):
    """Test workflow validation."""
    print("\nTesting workflow validation...")

    # Test with initial data context
    initial_context = DataContext({"input_email": "test@example.com"})

    errors = comprehensive_validate(workflow, initial_context)

    if errors:
        print(f"✗ Validation found {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ Workflow validation passed")
        return True


def test_invalid_workflow():
    """Test validation with an invalid workflow."""
    print("\nTesting validation with invalid workflow...")

    # Create workflow with missing required fields
    invalid_action = ActionStep(
        action_name="",  # Missing action name
        output_key="",   # Missing output key
    )

    invalid_script = ScriptStep(
        code="",         # Missing code
        output_key="result",
    )

    invalid_workflow = Workflow(steps=[invalid_action, invalid_script])

    errors = comprehensive_validate(invalid_workflow)

    if errors:
        print(f"✓ Validation correctly found {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return True
    else:
        print("✗ Validation should have found errors but didn't")
        return False


def main():
    """Run all tests."""
    print("Moveworks YAML Assistant - Core Functionality Tests")
    print("=" * 60)

    # Test basic workflow creation
    workflow = test_basic_workflow()
    if not workflow:
        print("✗ Basic workflow test failed")
        return

    # Test YAML generation
    if not test_yaml_generation(workflow):
        print("✗ YAML generation test failed")
        return

    # Test data context
    if not test_data_context():
        print("✗ Data context test failed")
        return

    # Test validation
    if not test_validation(workflow):
        print("✗ Validation test failed")
        return

    # Test invalid workflow validation
    if not test_invalid_workflow():
        print("✗ Invalid workflow test failed")
        return

    print("\n" + "=" * 60)
    print("✓ All core functionality tests passed!")
    print("\nYou can now run the GUI application with:")
    print("  python main_gui.py")


if __name__ == "__main__":
    main()
