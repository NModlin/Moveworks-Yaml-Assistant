#!/usr/bin/env python3
"""
Demonstration of comprehensive output_key field compliance for Moveworks YAML Assistant.

This script showcases all the enhanced output_key compliance features including:
- Mandatory field enforcement for ActionStep, ScriptStep, and RaiseStep
- Lowercase snake_case naming validation
- Uniqueness validation across workflows
- YAML generation blocking for non-compliant workflows
- Data reference generation for downstream steps
"""

from core_structures import Workflow, ActionStep, ScriptStep, RaiseStep, ForLoopStep
from compliance_validator import compliance_validator
from output_key_validator import output_key_validator
from yaml_generator import generate_yaml_string


def demo_compliant_workflow():
    """Demonstrate a fully compliant workflow with proper output_key usage."""
    print("🎯 COMPLIANT WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create a compliant workflow with proper output_key fields
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",  # ✅ Proper snake_case, unique
        input_args={
            "email": "data.input_email"
        },
        description="Get user information by email"
    )
    
    script_step = ScriptStep(
        code="""# Process user information
user_name = data.user_info.user.name
user_department = data.user_info.user.department

result = {
    "greeting": f"Hello, {user_name}!",
    "department_info": f"You work in {user_department}",
    "processed_at": "2024-01-01T00:00:00Z"
}
return result""",
        output_key="processed_greeting",  # ✅ Proper snake_case, unique
        description="Process user data and create greeting"
    )
    
    raise_step = RaiseStep(
        message="User not found in system",
        output_key="error_info"  # ✅ Required for RaiseStep
    )
    
    workflow = Workflow(steps=[action_step, script_step, raise_step])
    
    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "user_greeting_action")
    
    print(f"Workflow valid: {result.is_valid}")
    print(f"Mandatory field errors: {len(result.mandatory_field_errors)}")
    print(f"Field naming errors: {len(result.field_naming_errors)}")
    
    if result.is_valid:
        print("✅ All compliance checks passed!")
        
        # Generate YAML
        try:
            yaml_output = generate_yaml_string(workflow, "user_greeting_action")
            print("\n📄 Generated YAML:")
            print("-" * 30)
            print(yaml_output)
        except Exception as e:
            print(f"❌ YAML generation failed: {e}")
    else:
        print("❌ Compliance issues found:")
        for error in result.mandatory_field_errors + result.field_naming_errors:
            print(f"  • {error}")


def demo_non_compliant_workflow():
    """Demonstrate validation of a non-compliant workflow."""
    print("\n❌ NON-COMPLIANT WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create workflow with compliance violations
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="",  # ❌ Missing required field
        description="Get user information"
    )
    
    script_step = ScriptStep(
        code="return {'result': 'test'}",
        output_key="userInfo",  # ❌ camelCase instead of snake_case
        description="Process data"
    )
    
    raise_step = RaiseStep(
        message="Error occurred",
        output_key="data"  # ❌ Reserved name
    )
    
    workflow = Workflow(steps=[action_step, script_step, raise_step])
    
    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"Workflow valid: {result.is_valid}")
    print(f"Mandatory field errors: {len(result.mandatory_field_errors)}")
    print(f"Field naming errors: {len(result.field_naming_errors)}")
    
    print("\n🔍 Compliance Issues Found:")
    for error in result.mandatory_field_errors:
        print(f"  • MANDATORY: {error}")
    
    for error in result.field_naming_errors:
        print(f"  • NAMING: {error}")
    
    # Try to generate YAML (should fail)
    try:
        yaml_output = generate_yaml_string(workflow, "test_action")
        print("❌ YAML generation should have been blocked!")
    except ValueError as e:
        print(f"\n✅ YAML generation correctly blocked: {str(e)[:100]}...")


def demo_individual_validation():
    """Demonstrate individual output_key validation with suggestions."""
    print("\n🔍 INDIVIDUAL OUTPUT_KEY VALIDATION")
    print("=" * 50)
    
    test_cases = [
        ("user_info", "ActionStep", "✅ Valid"),
        ("", "ActionStep", "❌ Missing required field"),
        ("userInfo", "ActionStep", "❌ camelCase format"),
        ("user-info", "ActionStep", "❌ Invalid characters"),
        ("data", "ActionStep", "❌ Reserved name"),
        ("processed_data", "ScriptStep", "✅ Valid"),
        ("error_info", "RaiseStep", "✅ Valid"),
    ]
    
    for output_key, step_type, expected in test_cases:
        result = output_key_validator.validate_output_key(output_key, step_type)
        
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"{status}: '{output_key}' for {step_type}")
        
        if not result.is_valid:
            for error in result.errors:
                print(f"    Error: {error}")
            for suggestion in result.suggestions:
                print(f"    Suggestion: {suggestion}")
        else:
            if result.data_reference:
                print(f"    Data reference: {result.data_reference}")
        print()


def demo_uniqueness_validation():
    """Demonstrate output_key uniqueness validation."""
    print("\n🔄 UNIQUENESS VALIDATION DEMONSTRATION")
    print("=" * 50)
    
    # Create workflow with duplicate output_keys
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_data",
        description="First action"
    )
    
    action2 = ActionStep(
        action_name="mw.get_user_by_id", 
        output_key="user_data",  # Duplicate!
        description="Second action"
    )
    
    script1 = ScriptStep(
        code="return {'processed': True}",
        output_key="user_data",  # Another duplicate!
        description="Process data"
    )
    
    workflow = Workflow(steps=[action1, action2, script1])
    
    # Validate workflow-level uniqueness
    results = output_key_validator.validate_workflow_output_keys(workflow)
    
    print("Individual step validation results:")
    for i, result in enumerate(results):
        step = workflow.steps[i]
        step_type = type(step).__name__
        output_key = getattr(step, 'output_key', '')
        
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"  Step {i+1} ({step_type}): '{output_key}' - {status}")
        
        if not result.is_valid:
            for error in result.errors:
                print(f"    • {error}")


def demo_data_reference_suggestions():
    """Demonstrate data reference suggestions for workflow steps."""
    print("\n📊 DATA REFERENCE SUGGESTIONS")
    print("=" * 50)
    
    # Create multi-step workflow
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information"
    )
    
    script1 = ScriptStep(
        code="return {'processed': True}",
        output_key="processed_data",
        description="Process user data"
    )
    
    action2 = ActionStep(
        action_name="mw.create_ticket",
        output_key="ticket_info",
        description="Create support ticket"
    )
    
    workflow = Workflow(steps=[action1, script1, action2])
    
    # Generate data reference suggestions
    suggestions = output_key_validator.generate_data_reference_suggestions(workflow)
    
    print("Available data references for each step:")
    for step_index, step in enumerate(workflow.steps):
        step_type = type(step).__name__
        available_refs = suggestions.get(step_index, [])
        
        print(f"\nStep {step_index + 1} ({step_type}):")
        print(f"  Available data references:")
        for ref in available_refs:
            print(f"    • {ref}")


def main():
    """Run all demonstrations."""
    print("🚀 OUTPUT_KEY COMPLIANCE DEMONSTRATION")
    print("=" * 60)
    
    demo_compliant_workflow()
    demo_non_compliant_workflow()
    demo_individual_validation()
    demo_uniqueness_validation()
    demo_data_reference_suggestions()
    
    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("Key Features Demonstrated:")
    print("✅ Mandatory field enforcement for ActionStep, ScriptStep, RaiseStep")
    print("✅ Lowercase snake_case naming validation")
    print("✅ Reserved name checking")
    print("✅ Uniqueness validation across workflows")
    print("✅ YAML generation blocking for non-compliant workflows")
    print("✅ Data reference generation for downstream steps")
    print("✅ Comprehensive error messages and suggestions")


if __name__ == "__main__":
    main()
