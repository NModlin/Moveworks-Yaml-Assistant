#!/usr/bin/env python3
"""
Test script for Moveworks YAML Assistant compliance refinements.

This script tests the enhanced compliance features including field naming
standardization, mandatory field enforcement, enhanced APIthon validation,
and DSL string formatting.
"""

from core_structures import ActionStep, ScriptStep, SwitchStep, SwitchCase, Workflow
from yaml_generator import generate_yaml_string, _is_dsl_expression, _ensure_dsl_string_quoting
from compliance_validator import compliance_validator
from enhanced_apiton_validator import enhanced_apiton_validator


def test_dsl_string_detection():
    """Test DSL expression detection and formatting."""
    print("=== Testing DSL String Detection ===")

    test_cases = [
        ("data.user_info.email", True),
        ("meta_info.user.name", True),
        ("data.status == 'active'", True),
        ("$CONCAT(['Hello', 'World'], ' ')", True),
        ("regular_string", False),
        ("123", False),
        ("", False),
    ]

    for test_string, expected in test_cases:
        result = _is_dsl_expression(test_string)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{test_string}' -> {result} (expected {expected})")

    print()


def test_dsl_string_formatting():
    """Test DSL string formatting in nested structures."""
    print("=== Testing DSL String Formatting ===")

    test_data = {
        "email": "data.user_info.email",
        "condition": "data.status == 'active'",
        "nested": {
            "user_id": "data.user.id",
            "regular": "normal_string"
        },
        "list": ["data.item[0]", "regular_item"]
    }

    formatted = _ensure_dsl_string_quoting(test_data)
    print("Original:", test_data)
    print("Formatted:", formatted)
    print()


def test_enhanced_apiton_validation():
    """Test enhanced APIthon validation with stricter restrictions."""
    print("=== Testing Enhanced APIthon Validation ===")

    # Test enhanced import detection
    invalid_scripts = [
        "from os import path",
        "from datetime import datetime as dt",
        "import json as j",
        "from collections import *",
        "__import__('os')",
        "class MyClass:\n    pass",
        "class MyClass():\n    pass",
        "class MyClass(object):\n    pass"
    ]

    for script in invalid_scripts:
        script_step = ScriptStep(
            code=script,
            output_key="test_output"
        )

        result = enhanced_apiton_validator.comprehensive_validate(script_step)
        status = "✓" if not result.is_valid else "✗"
        script_display = script.replace('\n', '\\n')
        print(f"{status} Script: {script_display}")
        if result.errors:
            print(f"    Errors: {result.errors}")

    print()


def test_mandatory_field_enforcement():
    """Test mandatory field enforcement for different step types."""
    print("=== Testing Mandatory Field Enforcement ===")

    # Test ActionStep with missing fields
    incomplete_action = ActionStep(
        action_name="",  # Empty mandatory field
        output_key="test_output"
    )

    # Test ScriptStep with missing fields
    incomplete_script = ScriptStep(
        code="",  # Empty mandatory field
        output_key="test_output"
    )

    # Test SwitchStep with empty cases
    incomplete_switch = SwitchStep(
        cases=[],  # Empty mandatory field
        output_key="test_output"
    )

    workflow = Workflow(steps=[incomplete_action, incomplete_script, incomplete_switch])

    result = compliance_validator.validate_workflow_compliance(workflow, "")  # Empty action name

    print(f"Validation result: {'✗ FAILED' if not result.is_valid else '✓ PASSED'}")
    print("Mandatory field errors:")
    for error in result.mandatory_field_errors:
        print(f"  - {error}")

    print()


def test_field_naming_validation():
    """Test field naming standardization validation."""
    print("=== Testing Field Naming Validation ===")

    # Test with invalid naming conventions
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="userInfo",  # camelCase - should be user_info
        input_args={
            "userEmail": "data.input_email",  # camelCase key
            "UserID": "data.user_id"  # PascalCase key
        }
    )

    workflow = Workflow(steps=[action_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")

    print(f"Validation result: {'✗ FAILED' if not result.is_valid else '✓ PASSED'}")
    print("Field naming errors:")
    for error in result.field_naming_errors:
        print(f"  - {error}")

    print()


def test_yaml_generation_with_dsl_formatting():
    """Test YAML generation with proper DSL string formatting."""
    print("=== Testing YAML Generation with DSL Formatting ===")

    # Create workflow with DSL expressions
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={
            "email": "data.input_email",
            "user_id": "meta_info.user.id"
        }
    )

    script_step = ScriptStep(
        code="""# Process user data
user_name = data.user_info.user.name
result = {
    "greeting": f"Hello, {user_name}!",
    "user_email": meta_info.user.email
}
return result""",
        output_key="processed_data",
        input_args={
            "user_data": "data.user_info"
        }
    )

    switch_step = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.user_info.status == 'active'",
                steps=[action_step]
            )
        ],
        output_key="switch_result"
    )

    workflow = Workflow(steps=[action_step, script_step, switch_step])

    # Generate YAML
    yaml_output = generate_yaml_string(workflow, "enhanced_compound_action")

    print("Generated YAML with DSL formatting:")
    print(yaml_output)
    print()


def test_comprehensive_compliance():
    """Test comprehensive compliance validation."""
    print("=== Testing Comprehensive Compliance ===")

    # Create a compliant workflow
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )

    script_step = ScriptStep(
        code="""# Valid APIthon script
user_name = data.user_info.user.name
result = {"greeting": f"Hello, {user_name}!"}
return result""",
        output_key="greeting_result"
    )

    workflow = Workflow(steps=[action_step, script_step])

    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "compliant_action")

    print(f"Compliance validation: {'✓ PASSED' if result.is_valid else '✗ FAILED'}")

    if not result.is_valid:
        print("Errors found:")
        for error in result.errors + result.mandatory_field_errors + result.field_naming_errors + result.apiton_errors:
            print(f"  - {error}")
    else:
        print("All compliance checks passed!")

    print()


if __name__ == "__main__":
    print("Moveworks YAML Assistant - Compliance Refinements Test")
    print("=" * 60)
    print()

    test_dsl_string_detection()
    test_dsl_string_formatting()
    test_enhanced_apiton_validation()
    test_mandatory_field_enforcement()
    test_field_naming_validation()
    test_yaml_generation_with_dsl_formatting()
    test_comprehensive_compliance()

    print("=" * 60)
    print("Compliance refinements testing completed!")
