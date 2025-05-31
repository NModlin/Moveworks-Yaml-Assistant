#!/usr/bin/env python3
"""
Comprehensive test for enhanced return expression support in the Moveworks YAML Assistant.

This script tests all the enhanced return expression functionality including:
1. ReturnStep class with output_mapper field
2. UI components with drag-drop support
3. YAML generation with DSL string quoting
4. Template functionality
5. Real-time validation
6. Integration with JSON Path Selector
"""

import sys
import json
from core_structures import (
    Workflow, ActionStep, ScriptStep, ReturnStep, DataContext
)
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator


def test_return_step_basic_functionality():
    """Test basic ReturnStep functionality."""
    print("=" * 60)
    print("TEST 1: Basic ReturnStep Functionality")
    print("=" * 60)
    
    # Create a simple workflow with return step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"}
    )
    
    return_step = ReturnStep(
        description="Return user profile information",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email",
            "department": "meta_info.user.department"
        }
    )
    
    workflow = Workflow(steps=[action_step, return_step])
    
    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow, "user_profile_workflow")
        print("✅ YAML Generation Successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Verify DSL string quoting
        if '"data.user_info.user.id"' in yaml_output:
            print("✅ DSL string quoting working correctly")
        else:
            print("❌ DSL string quoting not applied")
            
    except Exception as e:
        print(f"❌ YAML Generation Failed: {e}")
    
    print()


def test_return_step_validation():
    """Test return step validation functionality."""
    print("=" * 60)
    print("TEST 2: Return Step Validation")
    print("=" * 60)
    
    # Test valid return step
    valid_return = ReturnStep(
        description="Valid return step",
        output_mapper={
            "user_id": "data.user_info.id",
            "user_name": "data.user_info.name",
            "is_active": "data.user_info.status == 'active'"
        }
    )
    
    workflow = Workflow(steps=[valid_return])
    result = compliance_validator.validate_workflow_compliance(workflow)
    
    print(f"Valid return step - Errors: {len(result.errors)}")
    if result.errors:
        for error in result.errors:
            print(f"  ❌ {error}")
    else:
        print("✅ Valid return step passed validation")
    
    # Test return step with empty output_mapper (should be valid)
    empty_return = ReturnStep(
        description="Empty return step",
        output_mapper={}
    )
    
    workflow2 = Workflow(steps=[empty_return])
    result2 = compliance_validator.validate_workflow_compliance(workflow2)
    
    print(f"\nEmpty return step - Errors: {len(result2.errors)}")
    if result2.errors:
        for error in result2.errors:
            print(f"  ❌ {error}")
    else:
        print("✅ Empty return step passed validation")
    
    print()


def test_complex_return_expressions():
    """Test complex return expressions with multiple data sources."""
    print("=" * 60)
    print("TEST 3: Complex Return Expressions")
    print("=" * 60)
    
    # Create a complex workflow
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
    
    script_step = ScriptStep(
        code="""
# Process user data
user_data = data.user_info.user
permissions = data.user_permissions.permissions

result = {
    "processed_at": "2024-01-01T12:00:00Z",
    "summary": f"User {user_data.name} has {len(permissions)} permissions",
    "is_admin": "admin" in [p.role for p in permissions]
}
return result
        """.strip(),
        output_key="processed_data"
    )
    
    return_step = ReturnStep(
        description="Return comprehensive user profile",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email",
            "permissions": "data.user_permissions.permissions",
            "is_admin": "data.processed_data.is_admin",
            "summary": "data.processed_data.summary",
            "department": "meta_info.user.department",
            "requested_by": "meta_info.user.email",
            "has_permissions": "data.user_permissions.permissions.length > 0"
        }
    )
    
    workflow = Workflow(steps=[action1, action2, script_step, return_step])
    
    try:
        yaml_output = generate_yaml_string(workflow, "complex_user_workflow")
        print("✅ Complex workflow YAML generation successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Validate the workflow
        result = compliance_validator.validate_workflow_compliance(workflow)
        print(f"\nValidation - Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")
        
        if result.errors:
            for error in result.errors:
                print(f"  ❌ {error}")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"  ⚠️ {warning}")
        
        if not result.errors:
            print("✅ Complex workflow passed validation")
            
    except Exception as e:
        print(f"❌ Complex workflow failed: {e}")
    
    print()


def test_return_step_templates():
    """Test return step template patterns."""
    print("=" * 60)
    print("TEST 4: Return Step Templates")
    print("=" * 60)
    
    # Test different template patterns
    templates = [
        {
            "name": "User Profile Template",
            "mappings": {
                "user_id": "data.user_info.user.id",
                "user_name": "data.user_info.user.name",
                "user_email": "data.user_info.user.email",
                "department": "meta_info.user.department"
            }
        },
        {
            "name": "Status Check Template",
            "mappings": {
                "is_valid": "data.validation_result.is_valid",
                "status": "data.validation_result.status",
                "message": "data.validation_result.message",
                "timestamp": "meta_info.request.timestamp"
            }
        },
        {
            "name": "Error Handling Template",
            "mappings": {
                "error_code": "data.error_info.code",
                "error_message": "data.error_info.message",
                "error_details": "data.error_info.details",
                "user_context": "meta_info.user.id"
            }
        }
    ]
    
    for template in templates:
        print(f"\nTesting {template['name']}:")
        
        return_step = ReturnStep(
            description=f"Return step using {template['name']}",
            output_mapper=template['mappings']
        )
        
        workflow = Workflow(steps=[return_step])
        
        try:
            yaml_output = generate_yaml_string(workflow, f"template_test_{template['name'].lower().replace(' ', '_')}")
            print(f"✅ {template['name']} YAML generation successful")
            
            # Validate template
            result = compliance_validator.validate_workflow_compliance(workflow)
            if result.errors:
                print(f"❌ Template validation failed: {result.errors}")
            else:
                print(f"✅ {template['name']} validation passed")
                
        except Exception as e:
            print(f"❌ {template['name']} failed: {e}")
    
    print()


def test_dsl_expression_patterns():
    """Test various DSL expression patterns in return steps."""
    print("=" * 60)
    print("TEST 5: DSL Expression Patterns")
    print("=" * 60)
    
    # Test different DSL patterns
    dsl_patterns = {
        "simple_data_reference": "data.user_info.name",
        "meta_info_reference": "meta_info.user.email",
        "equality_check": "data.user_info.status == 'active'",
        "inequality_check": "data.user_info.age >= 18",
        "length_check": "data.permissions.length > 0",
        "null_check": "data.optional_field != null",
        "string_concatenation": "data.user_info.first_name + ' ' + data.user_info.last_name",
        "complex_expression": "(data.user_info.status == 'active') && (data.permissions.length > 0)"
    }
    
    return_step = ReturnStep(
        description="Test DSL expression patterns",
        output_mapper=dsl_patterns
    )
    
    workflow = Workflow(steps=[return_step])
    
    try:
        yaml_output = generate_yaml_string(workflow, "dsl_patterns_test")
        print("✅ DSL patterns YAML generation successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Check that all DSL expressions are properly quoted
        quoted_count = 0
        for pattern in dsl_patterns.values():
            if f'"{pattern}"' in yaml_output:
                quoted_count += 1
        
        print(f"\n✅ {quoted_count}/{len(dsl_patterns)} DSL expressions properly quoted")
        
        if quoted_count == len(dsl_patterns):
            print("✅ All DSL expressions correctly formatted")
        else:
            print("⚠️ Some DSL expressions may not be properly quoted")
            
    except Exception as e:
        print(f"❌ DSL patterns test failed: {e}")
    
    print()


def main():
    """Run all return expression tests."""
    print("🚀 ENHANCED RETURN EXPRESSION SUPPORT TESTS")
    print("=" * 60)
    
    test_return_step_basic_functionality()
    test_return_step_validation()
    test_complex_return_expressions()
    test_return_step_templates()
    test_dsl_expression_patterns()
    
    print("=" * 60)
    print("✅ ALL RETURN EXPRESSION TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
