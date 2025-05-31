#!/usr/bin/env python3
"""
Demo script showcasing ReturnStep functionality in the Moveworks YAML Assistant.

This script demonstrates the comprehensive ReturnStep implementation including:
1. Basic return step creation
2. DSL string quoting
3. Complex output mapping
4. YAML generation
5. Validation
"""

import sys
from core_structures import Workflow, ActionStep, ScriptStep, ReturnStep
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator

def demo_basic_return_step():
    """Demonstrate basic return step functionality."""
    print("🔹 DEMO 1: Basic Return Step")
    print("-" * 50)
    
    # Create a simple workflow with return
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"}
    )
    
    return_step = ReturnStep(
        description="Return basic user information",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email"
        }
    )
    
    workflow = Workflow(steps=[action_step, return_step])
    yaml_output = generate_yaml_string(workflow, "basic_return_demo")
    
    print("Generated YAML:")
    print(yaml_output)
    print()

def demo_dsl_expressions():
    """Demonstrate DSL expression handling in return steps."""
    print("🔹 DEMO 2: DSL Expressions and Conditional Logic")
    print("-" * 50)
    
    # Create workflow with DSL expressions
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )
    
    action2 = ActionStep(
        action_name="mw.get_user_permissions",
        output_key="permissions",
        input_args={"user_id": "data.user_info.user.id"}
    )
    
    return_step = ReturnStep(
        description="Return user data with conditional logic",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "is_active": "data.user_info.status == 'active'",
            "is_admin": "data.permissions.role == 'admin'",
            "department": "meta_info.user.department",
            "request_by": "meta_info.user.email",
            "has_permissions": "data.permissions.count > 0"
        }
    )
    
    workflow = Workflow(steps=[action1, action2, return_step])
    yaml_output = generate_yaml_string(workflow, "dsl_expressions_demo")
    
    print("Generated YAML with DSL expressions:")
    print(yaml_output)
    print()

def demo_complex_workflow():
    """Demonstrate complex workflow with script and return steps."""
    print("🔹 DEMO 3: Complex Workflow with Script and Return")
    print("-" * 50)
    
    # Create complex workflow
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )
    
    script_step = ScriptStep(
        code="""
# Process user data
user_data = data.user_info.user
processed_info = {
    "full_name": f"{user_data.first_name} {user_data.last_name}",
    "display_name": user_data.display_name or f"{user_data.first_name} {user_data.last_name}",
    "account_age_days": (datetime.now() - datetime.fromisoformat(user_data.created_at)).days,
    "is_verified": user_data.email_verified and user_data.phone_verified
}
return processed_info
        """.strip(),
        output_key="processed_user",
        description="Process and enhance user information"
    )
    
    return_step = ReturnStep(
        description="Return comprehensive user profile",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "email": "data.user_info.user.email",
            "full_name": "data.processed_user.full_name",
            "display_name": "data.processed_user.display_name",
            "account_age_days": "data.processed_user.account_age_days",
            "is_verified": "data.processed_user.is_verified",
            "department": "meta_info.user.department",
            "requested_by": "meta_info.user.email",
            "request_timestamp": "meta_info.request.timestamp"
        }
    )
    
    workflow = Workflow(steps=[action_step, script_step, return_step])
    yaml_output = generate_yaml_string(workflow, "complex_workflow_demo")
    
    print("Generated complex workflow YAML:")
    print(yaml_output)
    print()

def demo_validation():
    """Demonstrate validation functionality."""
    print("🔹 DEMO 4: Validation and Compliance")
    print("-" * 50)
    
    # Test valid return step
    valid_return = ReturnStep(
        description="Valid return step",
        output_mapper={
            "user_id": "data.user_info.id",
            "user_name": "data.user_info.name"
        }
    )
    
    workflow = Workflow(steps=[valid_return])
    result = compliance_validator.validate_workflow_compliance(workflow, "validation_demo")
    
    print(f"Validation result for valid return step:")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Field naming errors: {len(result.field_naming_errors)}")
    print(f"  Mandatory field errors: {len(result.mandatory_field_errors)}")
    
    if result.errors:
        print("  Error details:")
        for error in result.errors:
            print(f"    - {error}")
    
    if result.warnings:
        print("  Warning details:")
        for warning in result.warnings:
            print(f"    - {warning}")
    
    print()

def demo_empty_return():
    """Demonstrate empty return step (valid use case)."""
    print("🔹 DEMO 5: Empty Return Step")
    print("-" * 50)
    
    # Empty return step (valid for ending workflow without specific output)
    empty_return = ReturnStep(
        description="End workflow without specific output",
        output_mapper={}
    )
    
    workflow = Workflow(steps=[empty_return])
    yaml_output = generate_yaml_string(workflow, "empty_return_demo")
    
    print("Generated YAML for empty return step:")
    print(yaml_output)
    print()

def main():
    """Run all demos."""
    print("=" * 70)
    print("🎯 MOVEWORKS YAML ASSISTANT - RETURN STEP DEMO")
    print("=" * 70)
    print()
    
    # Run all demos
    demo_basic_return_step()
    demo_dsl_expressions()
    demo_complex_workflow()
    demo_validation()
    demo_empty_return()
    
    print("=" * 70)
    print("✅ All demos completed successfully!")
    print()
    print("Key features demonstrated:")
    print("  • Basic return step creation and YAML generation")
    print("  • Automatic DSL string quoting for data.* and meta_info.* references")
    print("  • Complex output mapping with conditional expressions")
    print("  • Integration with action and script steps")
    print("  • Validation and compliance checking")
    print("  • Empty return step handling")
    print()
    print("🚀 The ReturnStep implementation is fully functional!")
    print("=" * 70)

if __name__ == "__main__":
    main()
