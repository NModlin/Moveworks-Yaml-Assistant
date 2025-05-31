#!/usr/bin/env python3
"""
Test script for the integrated compliance validation system in the Moveworks YAML Assistant.

This script tests the core compliance fixes that have been implemented:
1. Field naming and structure compliance
2. Mandatory field enforcement with UI integration
3. APIthon script validation enhancement
4. DSL string formatting and data reference handling
"""

import sys
import json
from core_structures import ActionStep, ScriptStep, Workflow
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator
from enhanced_apiton_validator import enhanced_apiton_validator

def test_field_naming_compliance():
    """Test field naming compliance validation."""
    print("🔍 Testing Field Naming Compliance...")
    
    # Test with invalid field names (camelCase, PascalCase)
    invalid_action = ActionStep(
        action_name="mw.getUserByEmail",  # Should be snake_case
        output_key="userInfo",           # Should be snake_case
        description="Test action with invalid naming"
    )
    
    workflow = Workflow(steps=[invalid_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"  ❌ Invalid naming - Found {len(result.field_naming_errors)} field naming errors:")
    for error in result.field_naming_errors:
        print(f"    • {error}")
    
    # Test with valid field names (snake_case)
    valid_action = ActionStep(
        action_name="mw.get_user_by_email",  # Correct snake_case
        output_key="user_info",             # Correct snake_case
        description="Test action with valid naming"
    )
    
    workflow = Workflow(steps=[valid_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"  ✅ Valid naming - Found {len(result.field_naming_errors)} field naming errors")
    print()

def test_mandatory_field_enforcement():
    """Test mandatory field enforcement."""
    print("🔍 Testing Mandatory Field Enforcement...")
    
    # Test with missing mandatory fields
    incomplete_action = ActionStep(
        action_name="",  # Missing mandatory field
        output_key="",   # Missing mandatory field
        description="Incomplete action"
    )
    
    workflow = Workflow(steps=[incomplete_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"  ❌ Missing fields - Found {len(result.mandatory_field_errors)} mandatory field errors:")
    for error in result.mandatory_field_errors:
        print(f"    • {error}")
    
    # Test with all mandatory fields present
    complete_action = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Complete action"
    )
    
    workflow = Workflow(steps=[complete_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"  ✅ Complete fields - Found {len(result.mandatory_field_errors)} mandatory field errors")
    print()

def test_apiton_validation():
    """Test APIthon script validation enhancement."""
    print("🔍 Testing APIthon Script Validation...")
    
    # Test with prohibited patterns
    invalid_script = ScriptStep(
        code="""
import json  # Prohibited import
class MyClass:  # Prohibited class definition
    pass

def _private_method():  # Prohibited private method
    pass

result = {"test": "data"}
return result
        """.strip(),
        output_key="invalid_result",
        description="Script with prohibited patterns"
    )
    
    # Test APIthon validation directly
    available_paths = {"data.user_info", "meta_info.user.email"}
    apiton_result = enhanced_apiton_validator.comprehensive_validate(invalid_script, available_paths)
    
    print(f"  ❌ Invalid script - Found {len(apiton_result.errors)} APIthon errors:")
    for error in apiton_result.errors[:3]:  # Show first 3 errors
        print(f"    • {error}")
    
    # Test with valid APIthon script
    valid_script = ScriptStep(
        code="""
user_email = data.user_info.email
greeting = f"Hello, {user_email}!"
result = {"greeting": greeting, "timestamp": "2024-01-01"}
return result
        """.strip(),
        output_key="greeting_result",
        description="Valid APIthon script"
    )
    
    apiton_result = enhanced_apiton_validator.comprehensive_validate(valid_script, available_paths)
    
    print(f"  ✅ Valid script - Found {len(apiton_result.errors)} APIthon errors")
    print()

def test_dsl_string_formatting():
    """Test DSL string formatting in YAML generation."""
    print("🔍 Testing DSL String Formatting...")
    
    # Create action with DSL expressions in input_args
    action_with_dsl = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={
            "email": "data.input_email",           # DSL expression
            "include_details": "meta_info.user.id", # DSL expression
            "static_value": "test"                  # Regular string
        },
        description="Action with DSL expressions"
    )
    
    workflow = Workflow(steps=[action_with_dsl])
    yaml_output = generate_yaml_string(workflow, "test_compound_action")
    
    print("  Generated YAML with DSL expressions:")
    print("  " + "\n  ".join(yaml_output.split("\n")[:15]))  # Show first 15 lines
    
    # Verify DSL expressions are properly quoted
    if '"data.input_email"' in yaml_output and '"meta_info.user.id"' in yaml_output:
        print("  ✅ DSL expressions are properly quoted as strings")
    else:
        print("  ❌ DSL expressions may not be properly quoted")
    print()

def test_comprehensive_workflow_validation():
    """Test comprehensive workflow validation with all compliance checks."""
    print("🔍 Testing Comprehensive Workflow Validation...")
    
    # Create a workflow with multiple compliance issues
    problematic_workflow = Workflow(steps=[
        ActionStep(
            action_name="",  # Missing mandatory field
            output_key="userInfo",  # Invalid naming (camelCase)
            description="Problematic action"
        ),
        ScriptStep(
            code="import json\nreturn {}",  # Prohibited import
            output_key="",  # Missing mandatory field
            description="Problematic script"
        )
    ])
    
    result = compliance_validator.validate_workflow_compliance(problematic_workflow, "test_action")
    
    total_errors = (len(result.errors) + len(result.mandatory_field_errors) + 
                   len(result.field_naming_errors) + len(result.apiton_errors))
    
    print(f"  ❌ Problematic workflow - Found {total_errors} total compliance issues:")
    print(f"    • Field naming errors: {len(result.field_naming_errors)}")
    print(f"    • Mandatory field errors: {len(result.mandatory_field_errors)}")
    print(f"    • APIthon errors: {len(result.apiton_errors)}")
    print(f"    • Other errors: {len(result.errors)}")
    print(f"    • Overall valid: {result.is_valid}")
    print()

def main():
    """Run all compliance integration tests."""
    print("🚀 Starting Compliance Integration Tests")
    print("=" * 50)
    
    test_field_naming_compliance()
    test_mandatory_field_enforcement()
    test_apiton_validation()
    test_dsl_string_formatting()
    test_comprehensive_workflow_validation()
    
    print("✅ All compliance integration tests completed!")
    print("\nNext steps:")
    print("1. Run the main GUI: python main_gui.py")
    print("2. Create a workflow with compliance issues")
    print("3. Check the Validation → Compliance tab for real-time feedback")
    print("4. Try exporting YAML to see compliance warnings")

if __name__ == "__main__":
    main()
