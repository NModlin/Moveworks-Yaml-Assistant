#!/usr/bin/env python3
"""
Test script for ReturnStep validation and DSL string quoting.

This script tests the validation functionality and DSL string quoting
for ReturnStep output_mapper fields.
"""

import sys
from core_structures import Workflow, ActionStep, ReturnStep
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator

def test_dsl_string_quoting():
    """Test DSL string quoting in output_mapper."""
    print("Testing DSL string quoting in output_mapper...")
    
    # Create a workflow with DSL expressions in output_mapper
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )
    
    return_step = ReturnStep(
        description="Return user data with DSL expressions",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "meta_info.user.email",
            "is_active": "data.user_info.status == 'active'",
            "department": "meta_info.user.department"
        }
    )
    
    workflow = Workflow(steps=[action_step, return_step])
    
    try:
        yaml_output = generate_yaml_string(workflow, "dsl_test_workflow")
        print("✅ YAML generation with DSL expressions successful!")
        
        # Check if DSL expressions are properly quoted
        dsl_expressions = [
            '"data.user_info.user.id"',
            '"data.user_info.user.name"',
            '"meta_info.user.email"',
            '"data.user_info.status == \'active\'"',
            '"meta_info.user.department"'
        ]
        
        all_quoted = True
        for expr in dsl_expressions:
            if expr not in yaml_output:
                print(f"❌ DSL expression not properly quoted: {expr}")
                all_quoted = False
        
        if all_quoted:
            print("✅ All DSL expressions properly quoted!")
            print("\nGenerated YAML with DSL quoting:")
            print(yaml_output)
            return True
        else:
            print("❌ Some DSL expressions not properly quoted!")
            return False
            
    except Exception as e:
        print(f"❌ YAML generation failed: {e}")
        return False

def test_return_step_validation():
    """Test ReturnStep validation."""
    print("\nTesting ReturnStep validation...")
    
    # Test 1: Valid return step
    valid_return_step = ReturnStep(
        description="Valid return step",
        output_mapper={
            "user_id": "data.user_info.id",
            "user_name": "data.user_info.name"
        }
    )
    
    workflow = Workflow(steps=[valid_return_step])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"Valid return step validation - Errors: {len(result.errors)}")
    if result.errors:
        for error in result.errors:
            print(f"  - {error}")
    
    # Test 2: Return step with empty output_mapper (should be valid)
    empty_return_step = ReturnStep(
        description="Empty return step",
        output_mapper={}
    )
    
    workflow2 = Workflow(steps=[empty_return_step])
    result2 = compliance_validator.validate_workflow_compliance(workflow2)
    
    print(f"Empty return step validation - Errors: {len(result2.errors)}")
    if result2.errors:
        for error in result2.errors:
            print(f"  - {error}")
    
    # Test 3: Return step with invalid field names (if any validation exists)
    invalid_return_step = ReturnStep(
        description="Return step with potential issues",
        output_mapper={
            "UserID": "data.user_info.id",  # CamelCase instead of snake_case
            "user-name": "data.user_info.name"  # Hyphen instead of underscore
        }
    )
    
    workflow3 = Workflow(steps=[invalid_return_step])
    result3 = compliance_validator.validate_workflow_compliance(workflow3)
    
    print(f"Invalid field names validation - Errors: {len(result3.errors)}")
    if result3.errors:
        for error in result3.errors:
            print(f"  - {error}")
    
    return len(result.errors) == 0 and len(result2.errors) == 0

def test_complex_return_workflow():
    """Test a complex workflow with multiple steps and return."""
    print("\nTesting complex workflow with return step...")
    
    # Create a multi-step workflow
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )
    
    action2 = ActionStep(
        action_name="mw.get_user_permissions",
        output_key="user_permissions",
        input_args={"user_id": "data.user_info.user.id"}
    )
    
    return_step = ReturnStep(
        description="Return comprehensive user data",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email",
            "permissions": "data.user_permissions.permissions",
            "is_admin": "data.user_permissions.is_admin == true",
            "department": "meta_info.user.department",
            "request_timestamp": "meta_info.request.timestamp"
        }
    )
    
    workflow = Workflow(steps=[action1, action2, return_step])
    
    try:
        yaml_output = generate_yaml_string(workflow, "complex_return_workflow")
        print("✅ Complex workflow YAML generation successful!")
        
        # Validate the workflow
        result = compliance_validator.validate_workflow_compliance(workflow)
        print(f"Complex workflow validation - Errors: {len(result.errors)}")
        
        if result.errors:
            for error in result.errors:
                print(f"  - {error}")
        
        print("\nGenerated complex workflow YAML:")
        print(yaml_output)
        
        return len(result.errors) == 0
        
    except Exception as e:
        print(f"❌ Complex workflow generation failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=" * 70)
    print("RETURN STEP VALIDATION AND DSL QUOTING TEST")
    print("=" * 70)
    
    # Test 1: DSL string quoting
    dsl_test_passed = test_dsl_string_quoting()
    
    # Test 2: Return step validation
    validation_test_passed = test_return_step_validation()
    
    # Test 3: Complex workflow
    complex_test_passed = test_complex_return_workflow()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS:")
    print(f"DSL String Quoting: {'✅ PASSED' if dsl_test_passed else '❌ FAILED'}")
    print(f"Return Step Validation: {'✅ PASSED' if validation_test_passed else '❌ FAILED'}")
    print(f"Complex Workflow: {'✅ PASSED' if complex_test_passed else '❌ FAILED'}")
    
    if dsl_test_passed and validation_test_passed and complex_test_passed:
        print("\n🎉 All validation tests passed! ReturnStep implementation is fully functional.")
        return 0
    else:
        print("\n⚠️ Some validation tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
