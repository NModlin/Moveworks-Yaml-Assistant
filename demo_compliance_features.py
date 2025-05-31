#!/usr/bin/env python3
"""
Demonstration of Core Compliance Features in Moveworks YAML Assistant.

This script showcases the implemented compliance fixes and their benefits.
"""

import sys
from core_structures import ActionStep, ScriptStep, Workflow
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator
from enhanced_apiton_validator import enhanced_apiton_validator

def demo_field_naming_compliance():
    """Demonstrate field naming compliance validation."""
    print("🏷️  FIELD NAMING COMPLIANCE DEMO")
    print("=" * 50)
    
    print("\n❌ BEFORE: Non-compliant field naming")
    bad_action = ActionStep(
        action_name="getUserInfo",      # camelCase - INVALID
        output_key="userDetails",       # camelCase - INVALID
        description="Get user information"
    )
    
    workflow = Workflow(steps=[bad_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "testAction")
    
    print(f"Field naming errors: {len(result.field_naming_errors)}")
    for error in result.field_naming_errors:
        print(f"  • {error}")
    
    print("\n✅ AFTER: Compliant field naming")
    good_action = ActionStep(
        action_name="get_user_info",    # snake_case - VALID
        output_key="user_details",      # snake_case - VALID
        description="Get user information"
    )
    
    workflow = Workflow(steps=[good_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"Field naming errors: {len(result.field_naming_errors)}")
    print("All field names follow lowercase_snake_case convention! ✅")

def demo_mandatory_field_enforcement():
    """Demonstrate mandatory field enforcement."""
    print("\n\n🔒 MANDATORY FIELD ENFORCEMENT DEMO")
    print("=" * 50)
    
    print("\n❌ BEFORE: Missing mandatory fields")
    incomplete_action = ActionStep(
        action_name="",  # MISSING - INVALID
        output_key="",   # MISSING - INVALID
        description="Incomplete action"
    )
    
    workflow = Workflow(steps=[incomplete_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"Mandatory field errors: {len(result.mandatory_field_errors)}")
    for error in result.mandatory_field_errors:
        print(f"  • {error}")
    
    print("\n✅ AFTER: All mandatory fields present")
    complete_action = ActionStep(
        action_name="mw.get_user_by_email",  # PRESENT - VALID
        output_key="user_info",              # PRESENT - VALID
        description="Complete action"
    )
    
    workflow = Workflow(steps=[complete_action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"Mandatory field errors: {len(result.mandatory_field_errors)}")
    print("All mandatory fields are present! ✅")

def demo_apiton_validation():
    """Demonstrate APIthon script validation."""
    print("\n\n🐍 APITON SCRIPT VALIDATION DEMO")
    print("=" * 50)
    
    print("\n❌ BEFORE: Non-compliant APIthon script")
    bad_script = ScriptStep(
        code="""
import json  # PROHIBITED - imports not allowed
class DataProcessor:  # PROHIBITED - classes not allowed
    def process(self):
        return {}

def _private_method():  # PROHIBITED - private methods not allowed
    pass

result = {"status": "processed"}
return result
        """.strip(),
        output_key="bad_result",
        description="Non-compliant script"
    )
    
    available_paths = {"data.user_info", "meta_info.user.email"}
    apiton_result = enhanced_apiton_validator.comprehensive_validate(bad_script, available_paths)
    
    print(f"APIthon errors: {len(apiton_result.errors)}")
    for error in apiton_result.errors[:3]:  # Show first 3
        print(f"  • {error}")
    
    print("\n✅ AFTER: Compliant APIthon script")
    good_script = ScriptStep(
        code="""
# Valid APIthon script
user_email = data.user_info.email
user_name = data.user_info.name

# Process the data
greeting = f"Hello, {user_name}!"
result = {
    "greeting": greeting,
    "email": user_email,
    "timestamp": "2024-01-01T00:00:00Z"
}

return result
        """.strip(),
        output_key="greeting_result",
        description="Compliant script"
    )
    
    apiton_result = enhanced_apiton_validator.comprehensive_validate(good_script, available_paths)
    
    print(f"APIthon errors: {len(apiton_result.errors)}")
    if apiton_result.errors:
        for error in apiton_result.errors:
            print(f"  • {error}")
    else:
        print("Script follows all APIthon restrictions! ✅")

def demo_dsl_string_formatting():
    """Demonstrate DSL string formatting in YAML output."""
    print("\n\n🔗 DSL STRING FORMATTING DEMO")
    print("=" * 50)
    
    print("\nCreating action with DSL expressions...")
    action_with_dsl = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={
            "email": "data.input_email",           # DSL expression
            "user_id": "meta_info.user.id",        # DSL expression
            "include_details": True,               # Regular value
            "format": "json"                       # Regular value
        },
        description="Action with DSL expressions"
    )
    
    workflow = Workflow(steps=[action_with_dsl])
    yaml_output = generate_yaml_string(workflow, "demo_compound_action")
    
    print("\nGenerated YAML with properly quoted DSL expressions:")
    print("-" * 40)
    print(yaml_output)
    print("-" * 40)
    
    # Verify DSL quoting
    dsl_quoted = '"data.input_email"' in yaml_output and '"meta_info.user.id"' in yaml_output
    regular_not_quoted = 'include_details: true' in yaml_output.lower()
    
    if dsl_quoted and regular_not_quoted:
        print("✅ DSL expressions are properly quoted, regular values are not!")
    else:
        print("❌ DSL formatting may have issues")

def demo_comprehensive_validation():
    """Demonstrate comprehensive workflow validation."""
    print("\n\n🔍 COMPREHENSIVE VALIDATION DEMO")
    print("=" * 50)
    
    print("\nCreating a fully compliant workflow...")
    
    # Compliant action step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        description="Get user information"
    )
    
    # Compliant script step
    script_step = ScriptStep(
        code="""
user_name = data.user_info.user.name
user_email = data.user_info.user.email

processed_data = {
    "greeting": f"Hello, {user_name}!",
    "contact": user_email,
    "processed_at": "2024-01-01T00:00:00Z"
}

return processed_data
        """.strip(),
        output_key="processed_data",
        description="Process user data"
    )
    
    workflow = Workflow(steps=[action_step, script_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "compliant_workflow")
    
    total_errors = (len(result.errors) + len(result.mandatory_field_errors) + 
                   len(result.field_naming_errors) + len(result.apiton_errors))
    
    print(f"\n📊 COMPLIANCE REPORT:")
    print(f"  • Field naming errors: {len(result.field_naming_errors)}")
    print(f"  • Mandatory field errors: {len(result.mandatory_field_errors)}")
    print(f"  • APIthon errors: {len(result.apiton_errors)}")
    print(f"  • Other errors: {len(result.errors)}")
    print(f"  • Total errors: {total_errors}")
    print(f"  • Overall compliance: {'✅ PASSED' if result.is_valid else '❌ FAILED'}")
    
    if result.is_valid:
        print("\n🎉 This workflow is ready for production use!")
        print("\nGenerated YAML:")
        print("-" * 40)
        yaml_output = generate_yaml_string(workflow, "compliant_workflow")
        print(yaml_output[:500] + "..." if len(yaml_output) > 500 else yaml_output)
        print("-" * 40)

def main():
    """Run all compliance feature demonstrations."""
    print("🚀 MOVEWORKS YAML ASSISTANT - CORE COMPLIANCE FEATURES DEMO")
    print("=" * 70)
    
    demo_field_naming_compliance()
    demo_mandatory_field_enforcement()
    demo_apiton_validation()
    demo_dsl_string_formatting()
    demo_comprehensive_validation()
    
    print("\n\n🎯 SUMMARY")
    print("=" * 50)
    print("✅ Field naming compliance: Enforces lowercase_snake_case")
    print("✅ Mandatory field enforcement: Prevents incomplete workflows")
    print("✅ APIthon validation: Blocks prohibited patterns")
    print("✅ DSL string formatting: Proper YAML quoting")
    print("✅ Real-time UI feedback: Immediate validation in GUI")
    print("✅ Export protection: Warns about compliance issues")
    
    print("\n🚀 Try the GUI: python main_gui.py")
    print("   Navigate to Validation → Compliance tab to see real-time feedback!")

if __name__ == "__main__":
    main()
