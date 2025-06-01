#!/usr/bin/env python3
"""
Verification script for Input Variables functionality.
This script tests the core functionality without requiring the GUI.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_input_variables():
    """Test input variables functionality."""
    print("🧪 Testing Input Variables Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Import core structures
        print("1. Testing imports...")
        from core_structures import InputVariable, Workflow, ActionStep
        from yaml_generator import generate_yaml_string
        print("   ✓ Successfully imported core structures")
        
        # Test 2: Create input variables
        print("\n2. Testing input variable creation...")
        
        # Valid input variable
        email_var = InputVariable(
            name="user_email",
            data_type="string",
            description="Email address of the user to look up",
            required=True
        )
        print(f"   ✓ Created email variable: {email_var.name}")
        
        # Input variable with default value
        count_var = InputVariable(
            name="max_results",
            data_type="integer",
            description="Maximum number of results to return",
            required=False,
            default_value=10
        )
        print(f"   ✓ Created count variable: {count_var.name}")
        
        # Test 3: Create workflow with input variables
        print("\n3. Testing workflow with input variables...")
        workflow = Workflow()
        
        # Add input variables
        success1 = workflow.add_input_variable(email_var)
        success2 = workflow.add_input_variable(count_var)
        
        if not success1 or not success2:
            print("   ✗ Failed to add input variables")
            return False
        
        print(f"   ✓ Added {len(workflow.input_variables)} input variables")
        
        # Test 4: Create steps that use input variables
        print("\n4. Testing steps with input variable references...")
        
        action_step = ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            description="Get user information by email",
            input_args={
                "email": "data.user_email",  # Reference to input variable
                "limit": "data.max_results"   # Reference to input variable
            }
        )
        
        workflow.steps = [action_step]
        print("   ✓ Created action step with input variable references")
        
        # Test 5: Generate YAML
        print("\n5. Testing YAML generation...")
        
        yaml_output = generate_yaml_string(workflow, "test_input_variables_action")
        print("   ✓ Successfully generated YAML")
        
        # Test 6: Verify YAML content
        print("\n6. Verifying YAML content...")
        
        required_sections = [
            "action_name: test_input_variables_action",
            "input_variables:",
            "user_email:",
            "max_results:",
            "type: string",
            "type: integer",
            "description:",
            "required: true",
            "default: 10",
            "steps:",
            "action: mw.get_user_by_email",
            "data.user_email",
            "data.max_results"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in yaml_output:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"   ✗ Missing sections in YAML: {missing_sections}")
            print("\nGenerated YAML:")
            print("-" * 40)
            print(yaml_output)
            print("-" * 40)
            return False
        
        print("   ✓ All required sections present in YAML")
        
        # Test 7: Test input variable utility methods
        print("\n7. Testing utility methods...")
        
        # Test get_input_variable_names
        names = workflow.get_input_variable_names()
        expected_names = ["user_email", "max_results"]
        if names != expected_names:
            print(f"   ✗ Expected {expected_names}, got {names}")
            return False
        print("   ✓ get_input_variable_names works correctly")
        
        # Test get_input_variable_by_name
        found_var = workflow.get_input_variable_by_name("user_email")
        if found_var != email_var:
            print("   ✗ get_input_variable_by_name failed")
            return False
        print("   ✓ get_input_variable_by_name works correctly")
        
        # Test duplicate variable prevention
        duplicate_var = InputVariable(name="user_email", data_type="string")
        success = workflow.add_input_variable(duplicate_var)
        if success:
            print("   ✗ Should have prevented duplicate variable")
            return False
        print("   ✓ Duplicate variable prevention works")
        
        # Test 8: Display final YAML
        print("\n8. Final YAML output:")
        print("=" * 50)
        print(yaml_output)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test input variable validation."""
    print("\n🔍 Testing Input Variable Validation")
    print("=" * 50)
    
    try:
        from core_structures import InputVariable
        
        # Test invalid name (camelCase)
        print("1. Testing invalid variable name...")
        try:
            invalid_var = InputVariable(name="userEmail", data_type="string")
            print("   ✗ Should have rejected camelCase name")
            return False
        except ValueError as e:
            print(f"   ✓ Correctly rejected camelCase: {str(e)[:50]}...")
        
        # Test invalid data type
        print("\n2. Testing invalid data type...")
        try:
            invalid_var = InputVariable(name="test_var", data_type="invalid_type")
            print("   ✗ Should have rejected invalid data type")
            return False
        except ValueError as e:
            print(f"   ✓ Correctly rejected invalid type: {str(e)[:50]}...")
        
        # Test valid names
        print("\n3. Testing valid variable names...")
        valid_names = ["user_email", "max_count", "is_active", "data_list", "user_id"]
        for name in valid_names:
            try:
                var = InputVariable(name=name, data_type="string")
                print(f"   ✓ Accepted valid name: {name}")
            except ValueError as e:
                print(f"   ✗ Rejected valid name {name}: {e}")
                return False
        
        # Test valid data types
        print("\n4. Testing valid data types...")
        valid_types = ["string", "number", "integer", "boolean", "array", "object", 
                      "List[string]", "List[number]", "User", "List[User]"]
        for data_type in valid_types:
            try:
                var = InputVariable(name="test_var", data_type=data_type)
                print(f"   ✓ Accepted valid type: {data_type}")
            except ValueError as e:
                print(f"   ✗ Rejected valid type {data_type}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error during validation testing: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Input Variables Verification Script")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_input_variables()
    test2_passed = test_validation()
    
    print("\n📊 Test Results")
    print("=" * 30)
    print(f"Core Functionality: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Validation Tests:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Input Variables functionality is working correctly.")
        print("\n📝 Summary of implemented features:")
        print("   • InputVariable dataclass with validation")
        print("   • Workflow integration with input_variables field")
        print("   • YAML generation with input_variables section")
        print("   • Data type validation and naming conventions")
        print("   • Utility methods for variable management")
        print("   • Auto-completion support for data.{variable_name}")
        return True
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
