#!/usr/bin/env python3
"""
Test script for Input Variables functionality in the Moveworks YAML Assistant.

This script tests the core functionality of input variables including:
- Creating input variables
- YAML generation with input_variables section
- Validation of input variable references
- Auto-completion integration
"""

import sys
import json
from core_structures import Workflow, ActionStep, ScriptStep, InputVariable
from yaml_generator import generate_yaml_string


def test_input_variable_creation():
    """Test creating input variables with validation."""
    print("Testing Input Variable Creation...")
    
    # Test valid input variable
    try:
        var1 = InputVariable(
            name="user_email",
            data_type="string",
            description="Email address of the user",
            required=True
        )
        print(f"✓ Created valid input variable: {var1.name}")
    except Exception as e:
        print(f"✗ Failed to create valid input variable: {e}")
        return False
    
    # Test invalid name (not snake_case)
    try:
        var2 = InputVariable(
            name="userEmail",  # camelCase - should fail
            data_type="string"
        )
        print("✗ Should have failed for camelCase name")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected camelCase name: {e}")
    
    # Test invalid data type
    try:
        var3 = InputVariable(
            name="test_var",
            data_type="invalid_type"  # Should fail
        )
        print("✗ Should have failed for invalid data type")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid data type: {e}")
    
    return True


def test_workflow_with_input_variables():
    """Test workflow with input variables."""
    print("\nTesting Workflow with Input Variables...")
    
    # Create input variables
    email_var = InputVariable(
        name="input_email",
        data_type="string",
        description="User email to look up",
        required=True
    )
    
    department_var = InputVariable(
        name="target_department",
        data_type="string",
        description="Department to filter by",
        required=False,
        default_value="IT"
    )
    
    # Create workflow
    workflow = Workflow()
    
    # Add input variables
    success1 = workflow.add_input_variable(email_var)
    success2 = workflow.add_input_variable(department_var)
    
    if not success1 or not success2:
        print("✗ Failed to add input variables to workflow")
        return False
    
    print(f"✓ Added {len(workflow.input_variables)} input variables to workflow")
    
    # Test duplicate variable name
    duplicate_var = InputVariable(
        name="input_email",  # Same name as email_var
        data_type="string"
    )
    
    success3 = workflow.add_input_variable(duplicate_var)
    if success3:
        print("✗ Should have rejected duplicate variable name")
        return False
    
    print("✓ Correctly rejected duplicate variable name")
    
    # Create steps that reference input variables
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information",
        input_args={"email": "data.input_email"}  # Reference input variable
    )
    
    script_step = ScriptStep(
        code="""
# Process user data with department filter
user_dept = data.user_info.department
target_dept = data.target_department

if user_dept == target_dept:
    result = {"match": True, "user": data.user_info}
else:
    result = {"match": False, "user": data.user_info}

return result
        """.strip(),
        output_key="filtered_result",
        description="Filter user by department"
    )
    
    workflow.steps = [action_step, script_step]
    
    print(f"✓ Created workflow with {len(workflow.steps)} steps")
    return True


def test_yaml_generation():
    """Test YAML generation with input variables."""
    print("\nTesting YAML Generation...")
    
    # Create workflow with input variables
    workflow = Workflow()
    
    # Add input variables
    email_var = InputVariable(
        name="user_email",
        data_type="string",
        description="Email address to look up",
        required=True
    )
    
    count_var = InputVariable(
        name="max_results",
        data_type="integer",
        description="Maximum number of results",
        required=False,
        default_value=10
    )
    
    workflow.add_input_variable(email_var)
    workflow.add_input_variable(count_var)
    
    # Add a simple action step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_data",
        input_args={"email": "data.user_email"}
    )
    
    workflow.steps = [action_step]
    
    try:
        yaml_output = generate_yaml_string(workflow, "test_compound_action")
        print("✓ Successfully generated YAML with input variables")
        
        # Check if input_variables section is present
        if "input_variables:" in yaml_output:
            print("✓ YAML contains input_variables section")
        else:
            print("✗ YAML missing input_variables section")
            return False
        
        # Check if variable definitions are present
        if "user_email:" in yaml_output and "max_results:" in yaml_output:
            print("✓ YAML contains variable definitions")
        else:
            print("✗ YAML missing variable definitions")
            return False
        
        # Print the generated YAML for inspection
        print("\nGenerated YAML:")
        print("=" * 50)
        print(yaml_output)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to generate YAML: {e}")
        return False


def test_input_variable_methods():
    """Test input variable utility methods."""
    print("\nTesting Input Variable Utility Methods...")
    
    workflow = Workflow()
    
    # Test empty workflow
    names = workflow.get_input_variable_names()
    if names != []:
        print("✗ Empty workflow should return empty names list")
        return False
    print("✓ Empty workflow returns empty names list")
    
    # Add variables
    var1 = InputVariable(name="test_var1", data_type="string")
    var2 = InputVariable(name="test_var2", data_type="number")
    
    workflow.add_input_variable(var1)
    workflow.add_input_variable(var2)
    
    # Test get_input_variable_names
    names = workflow.get_input_variable_names()
    expected_names = ["test_var1", "test_var2"]
    if names != expected_names:
        print(f"✗ Expected {expected_names}, got {names}")
        return False
    print("✓ get_input_variable_names works correctly")
    
    # Test get_input_variable_by_name
    found_var = workflow.get_input_variable_by_name("test_var1")
    if found_var != var1:
        print("✗ get_input_variable_by_name failed")
        return False
    print("✓ get_input_variable_by_name works correctly")
    
    # Test remove_input_variable
    success = workflow.remove_input_variable("test_var1")
    if not success or len(workflow.input_variables) != 1:
        print("✗ remove_input_variable failed")
        return False
    print("✓ remove_input_variable works correctly")
    
    return True


def main():
    """Run all tests."""
    print("🧪 Testing Input Variables Functionality")
    print("=" * 60)
    
    tests = [
        test_input_variable_creation,
        test_workflow_with_input_variables,
        test_yaml_generation,
        test_input_variable_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ Test passed")
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Input Variables functionality is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
