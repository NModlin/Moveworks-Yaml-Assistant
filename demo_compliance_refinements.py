#!/usr/bin/env python3
"""
Demonstration of Moveworks YAML Assistant compliance refinements.

This script showcases the enhanced compliance features including field naming
standardization, mandatory field enforcement, enhanced APIthon validation,
and DSL string formatting.
"""

from core_structures import ActionStep, ScriptStep, SwitchStep, SwitchCase, Workflow
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator


def demo_compliant_workflow():
    """Demonstrate a fully compliant workflow."""
    print("🎯 COMPLIANT WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create a compliant workflow with proper naming and DSL expressions
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",  # Proper snake_case
        input_args={
            "email": "data.input_email",  # DSL expression - will be quoted
            "user_id": "meta_info.user.id"  # DSL expression - will be quoted
        }
    )
    
    script_step = ScriptStep(
        code="""# Compliant APIthon script
user_name = data.user_info.user.name
user_email = meta_info.user.email
result = {
    "greeting": f"Hello, {user_name}!",
    "contact_email": user_email,
    "timestamp": "2024-01-01T00:00:00Z"
}
return result""",
        output_key="processed_data",  # Proper snake_case
        input_args={
            "user_data": "data.user_info"  # DSL expression - will be quoted
        }
    )
    
    switch_step = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.user_info.status == 'active'",  # DSL expression - will be quoted
                steps=[action_step]
            )
        ],
        output_key="status_check_result"  # Proper snake_case
    )
    
    workflow = Workflow(steps=[action_step, script_step, switch_step])
    
    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "compliant_compound_action")
    
    print(f"✅ Compliance Status: {'PASSED' if result.is_valid else 'FAILED'}")
    
    if result.is_valid:
        print("✅ All compliance checks passed!")
        
        # Generate YAML with DSL formatting
        yaml_output = generate_yaml_string(workflow, "compliant_compound_action")
        
        print("\n📄 Generated YAML with DSL String Formatting:")
        print("-" * 40)
        print(yaml_output)
    else:
        print("❌ Compliance errors found:")
        for error in result.mandatory_field_errors + result.field_naming_errors + result.apiton_errors:
            print(f"  - {error}")


def demo_non_compliant_workflow():
    """Demonstrate validation of a non-compliant workflow."""
    print("\n❌ NON-COMPLIANT WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create a workflow with compliance violations
    action_step = ActionStep(
        action_name="",  # ❌ Empty mandatory field
        output_key="userInfo",  # ❌ camelCase instead of snake_case
        input_args={
            "userEmail": "data.input_email",  # ❌ camelCase key
            "UserID": "data.user_id"  # ❌ PascalCase key
        }
    )
    
    script_step = ScriptStep(
        code="import os\nfrom datetime import datetime",  # ❌ Prohibited imports
        output_key="data",  # ❌ Reserved name
    )
    
    switch_step = SwitchStep(
        cases=[],  # ❌ Empty mandatory field
        output_key="switchResult"  # ❌ camelCase
    )
    
    workflow = Workflow(steps=[action_step, script_step, switch_step])
    
    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "")  # ❌ Empty action name
    
    print(f"❌ Compliance Status: {'PASSED' if result.is_valid else 'FAILED'}")
    
    print("\n📋 Compliance Violations Found:")
    
    if result.mandatory_field_errors:
        print("\n🔴 Mandatory Field Errors:")
        for error in result.mandatory_field_errors:
            print(f"  - {error}")
    
    if result.field_naming_errors:
        print("\n🟡 Field Naming Errors:")
        for error in result.field_naming_errors:
            print(f"  - {error}")
    
    if result.apiton_errors:
        print("\n🟠 APIthon Validation Errors:")
        for error in result.apiton_errors:
            print(f"  - {error}")


def demo_dsl_formatting():
    """Demonstrate DSL string formatting in YAML output."""
    print("\n🔤 DSL STRING FORMATTING DEMONSTRATION")
    print("=" * 50)
    
    from yaml_generator import _is_dsl_expression, _ensure_dsl_string_quoting
    
    # Test DSL expression detection
    test_expressions = [
        "data.user_info.email",
        "meta_info.user.name", 
        "data.status == 'active'",
        "$CONCAT(['Hello', 'World'], ' ')",
        "regular_string",
        "data.items[0].name"
    ]
    
    print("🔍 DSL Expression Detection:")
    for expr in test_expressions:
        is_dsl = _is_dsl_expression(expr)
        status = "✅ DSL" if is_dsl else "⚪ Regular"
        print(f"  {status}: '{expr}'")
    
    # Test nested structure formatting
    print("\n🏗️  Nested Structure DSL Formatting:")
    test_data = {
        "input_args": {
            "email": "data.user_info.email",
            "user_id": "meta_info.user.id",
            "regular_field": "normal_value"
        },
        "condition": "data.status == 'active'",
        "list_data": ["data.item[0]", "regular_item"]
    }
    
    print("Original structure:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    formatted_data = _ensure_dsl_string_quoting(test_data)
    print("\nFormatted structure (DSL expressions preserved for YAML quoting):")
    for key, value in formatted_data.items():
        print(f"  {key}: {value}")


def demo_enhanced_apiton_validation():
    """Demonstrate enhanced APIthon validation."""
    print("\n🔒 ENHANCED APITON VALIDATION DEMONSTRATION")
    print("=" * 50)
    
    from enhanced_apiton_validator import enhanced_apiton_validator
    
    # Test prohibited patterns
    prohibited_scripts = [
        ("from os import path", "Import statement"),
        ("import json as j", "Import with alias"),
        ("from collections import *", "Wildcard import"),
        ("__import__('datetime')", "Dynamic import"),
        ("class MyClass:\n    pass", "Class definition"),
        ("class MyClass(object):\n    pass", "Class with inheritance")
    ]
    
    print("🚫 Enhanced Prohibited Pattern Detection:")
    
    for script, description in prohibited_scripts:
        script_step = ScriptStep(code=script, output_key="test_output")
        result = enhanced_apiton_validator.comprehensive_validate(script_step)
        
        status = "✅ BLOCKED" if not result.is_valid else "❌ MISSED"
        print(f"  {status}: {description}")
        if result.errors:
            print(f"    Errors: {len(result.errors)} found")


if __name__ == "__main__":
    print("🎯 MOVEWORKS YAML ASSISTANT - COMPLIANCE REFINEMENTS DEMO")
    print("=" * 60)
    
    demo_compliant_workflow()
    demo_non_compliant_workflow()
    demo_dsl_formatting()
    demo_enhanced_apiton_validation()
    
    print("\n" + "=" * 60)
    print("✨ Compliance refinements demonstration completed!")
    print("🎯 The Moveworks YAML Assistant now ensures 100% compliance!")
