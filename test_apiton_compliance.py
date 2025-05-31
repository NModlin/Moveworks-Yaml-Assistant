#!/usr/bin/env python3
"""
Test script for comprehensive APIthon script field compliance implementation.

This script tests the enhanced compliance validation for ScriptStep instances
including field naming consistency, byte limits, private method detection,
and return statement validation.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_structures import ScriptStep, Workflow
from compliance_validator import compliance_validator
from yaml_generator import generate_yaml_string


def test_code_field_compliance():
    """Test code field naming compliance."""
    print("=" * 60)
    print("Testing Code Field Compliance")
    print("=" * 60)
    
    # Test 1: Valid ScriptStep with code field
    print("\n1. Testing valid ScriptStep with code field:")
    valid_step = ScriptStep(
        code="user_name = data.user_info.name\nreturn {'greeting': f'Hello, {user_name}!'}",
        output_key="greeting_result"
    )
    
    workflow = Workflow(steps=[valid_step])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.mandatory_field_errors:
        print(f"   Mandatory field errors: {result.mandatory_field_errors}")
    if result.field_naming_errors:
        print(f"   Field naming errors: {result.field_naming_errors}")
    if result.apiton_errors:
        print(f"   APIthon errors: {result.apiton_errors}")
    
    # Test 2: ScriptStep with empty code field
    print("\n2. Testing ScriptStep with empty code field:")
    empty_code_step = ScriptStep(
        code="",
        output_key="empty_result"
    )
    
    workflow = Workflow(steps=[empty_code_step])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.mandatory_field_errors:
        print(f"   Mandatory field errors: {result.mandatory_field_errors}")


def test_byte_limit_validation():
    """Test APIthon script byte limit validation."""
    print("\n" + "=" * 60)
    print("Testing Byte Limit Validation")
    print("=" * 60)
    
    # Test 1: Script within byte limit
    print("\n1. Testing script within byte limit:")
    small_script = ScriptStep(
        code="result = {'status': 'success'}\nreturn result",
        output_key="small_result"
    )
    
    workflow = Workflow(steps=[small_script])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.apiton_errors:
        print(f"   APIthon errors: {result.apiton_errors}")
    if result.warnings:
        print(f"   Warnings: {result.warnings}")
    
    # Test 2: Script exceeding byte limit
    print("\n2. Testing script exceeding byte limit:")
    large_script = "# " + "x" * 4100 + "\nreturn {'status': 'large'}"
    large_script_step = ScriptStep(
        code=large_script,
        output_key="large_result"
    )
    
    workflow = Workflow(steps=[large_script_step])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.apiton_errors:
        print(f"   APIthon errors: {result.apiton_errors}")


def test_private_method_detection():
    """Test private method detection in APIthon scripts."""
    print("\n" + "=" * 60)
    print("Testing Private Method Detection")
    print("=" * 60)
    
    # Test 1: Script with private identifiers
    print("\n1. Testing script with private identifiers:")
    private_script = ScriptStep(
        code="_private_var = data.user_info\n_helper_func = lambda x: x\nreturn _private_var",
        output_key="private_result"
    )
    
    workflow = Workflow(steps=[private_script])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.apiton_errors:
        print(f"   APIthon errors: {result.apiton_errors}")
    
    # Test 2: Script without private identifiers
    print("\n2. Testing script without private identifiers:")
    public_script = ScriptStep(
        code="public_var = data.user_info\nhelper_func = lambda x: x\nreturn public_var",
        output_key="public_result"
    )
    
    workflow = Workflow(steps=[public_script])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.apiton_errors:
        print(f"   APIthon errors: {result.apiton_errors}")


def test_return_logic_validation():
    """Test return statement logic validation."""
    print("\n" + "=" * 60)
    print("Testing Return Logic Validation")
    print("=" * 60)
    
    # Test 1: Script with proper return statement
    print("\n1. Testing script with proper return statement:")
    return_script = ScriptStep(
        code="user_name = data.user_info.name\nresult = {'greeting': f'Hello, {user_name}!'}\nreturn result",
        output_key="greeting_result"
    )
    
    workflow = Workflow(steps=[return_script])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.suggestions:
        print(f"   Suggestions: {result.suggestions}")
    
    # Test 2: Script with assignment as last line (no return)
    print("\n2. Testing script with assignment as last line:")
    assignment_script = ScriptStep(
        code="user_name = data.user_info.name\nresult = {'greeting': f'Hello, {user_name}!'}",
        output_key="assignment_result"
    )
    
    workflow = Workflow(steps=[assignment_script])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"   Valid: {result.is_valid}")
    if result.suggestions:
        print(f"   Suggestions: {result.suggestions}")


def test_yaml_generation():
    """Test YAML generation with literal block scalar formatting."""
    print("\n" + "=" * 60)
    print("Testing YAML Generation")
    print("=" * 60)
    
    # Test 1: Single-line script
    print("\n1. Testing single-line script YAML generation:")
    single_line_script = ScriptStep(
        code="return {'status': 'success'}",
        output_key="status_result"
    )
    
    workflow = Workflow(steps=[single_line_script])
    try:
        yaml_output = generate_yaml_string(workflow, "test_single_line")
        print("   YAML generated successfully:")
        print("   " + "\n   ".join(yaml_output.split("\n")[:10]))  # Show first 10 lines
    except Exception as e:
        print(f"   Error generating YAML: {e}")
    
    # Test 2: Multi-line script
    print("\n2. Testing multi-line script YAML generation:")
    multi_line_script = ScriptStep(
        code="""user_name = data.user_info.name
user_email = meta_info.user.email
result = {
    'greeting': f'Hello, {user_name}!',
    'email': user_email,
    'timestamp': 'now'
}
return result""",
        output_key="multi_result"
    )
    
    workflow = Workflow(steps=[multi_line_script])
    try:
        yaml_output = generate_yaml_string(workflow, "test_multi_line")
        print("   YAML generated successfully:")
        print("   " + "\n   ".join(yaml_output.split("\n")[:15]))  # Show first 15 lines
    except Exception as e:
        print(f"   Error generating YAML: {e}")


def main():
    """Run all compliance tests."""
    print("APIthon Script Field Compliance Test Suite")
    print("=" * 60)
    
    try:
        test_code_field_compliance()
        test_byte_limit_validation()
        test_private_method_detection()
        test_return_logic_validation()
        test_yaml_generation()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
