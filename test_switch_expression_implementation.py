#!/usr/bin/env python3
"""
Test script for Switch Expression Implementation in the Moveworks YAML Assistant.

This script demonstrates the comprehensive switch expression functionality
including DSL condition generation, case management, and YAML generation.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase
)
from yaml_generator import generate_yaml_string
from dsl_validator import dsl_validator


def test_basic_switch_creation():
    """Test basic switch step creation and structure."""
    print("🔀 Basic Switch Creation")
    print("-" * 50)
    
    # Create a basic switch step
    switch_step = SwitchStep(
        description="User role-based access control",
        output_key="_"
    )
    
    print(f"✅ Switch step created: {switch_step.description}")
    print(f"   Output key: {switch_step.output_key}")
    print(f"   Cases: {len(switch_step.cases)}")
    print(f"   Default case: {'Yes' if switch_step.default_case else 'No'}")
    print()


def test_dsl_condition_validation():
    """Test DSL condition validation for switch cases."""
    print("🔍 DSL Condition Validation")
    print("-" * 50)
    
    test_conditions = [
        "data.user.role == 'admin'",
        "data.user.access_level == 'member'",
        "data.temperature > 25 and data.humidity < 60",
        "data.status != 'inactive'",
        "meta_info.user.email.endswith('@company.com')",
        "invalid condition syntax =="  # Invalid condition
    ]
    
    for condition in test_conditions:
        result = dsl_validator.validate_dsl_expression(condition)
        status = "✅ Valid" if result.is_valid else "❌ Invalid"
        print(f"   {status}: {condition}")
        if not result.is_valid:
            print(f"      Errors: {', '.join(result.errors[:2])}")
    
    print()


def test_switch_case_creation():
    """Test switch case creation with various conditions and steps."""
    print("📋 Switch Case Creation")
    print("-" * 50)
    
    # Create cases for different user roles
    admin_case = SwitchCase(
        condition="data.user.role == 'admin'",
        steps=[
            ActionStep(
                action_name="mw.grant_admin_access",
                output_key="admin_access_result",
                input_args={"user_id": "data.user.id"}
            ),
            ScriptStep(
                code="return {'access_level': 'full', 'permissions': ['read', 'write', 'delete']}",
                output_key="admin_permissions"
            )
        ]
    )
    
    member_case = SwitchCase(
        condition="data.user.role == 'member'",
        steps=[
            ActionStep(
                action_name="mw.grant_member_access",
                output_key="member_access_result",
                input_args={"user_id": "data.user.id"}
            )
        ]
    )
    
    guest_case = SwitchCase(
        condition="data.user.role == 'guest'",
        steps=[
            ActionStep(
                action_name="mw.grant_guest_access",
                output_key="guest_access_result",
                input_args={"user_id": "data.user.id", "limited": True}
            )
        ]
    )
    
    print(f"✅ Admin case: {admin_case.condition} ({len(admin_case.steps)} steps)")
    print(f"✅ Member case: {member_case.condition} ({len(member_case.steps)} steps)")
    print(f"✅ Guest case: {guest_case.condition} ({len(guest_case.steps)} steps)")
    print()
    
    return [admin_case, member_case, guest_case]


def test_default_case_creation():
    """Test default case creation."""
    print("🔄 Default Case Creation")
    print("-" * 50)
    
    default_case = DefaultCase(
        steps=[
            ActionStep(
                action_name="mw.log_unknown_role",
                output_key="log_result",
                input_args={"role": "data.user.role", "message": "Unknown user role"}
            ),
            ActionStep(
                action_name="mw.send_notification",
                output_key="notification_result",
                input_args={"message": "Access denied: Unknown role"}
            )
        ]
    )
    
    print(f"✅ Default case created with {len(default_case.steps)} steps")
    print("   Steps:")
    for i, step in enumerate(default_case.steps):
        if isinstance(step, ActionStep):
            print(f"      {i+1}. Action: {step.action_name}")
        elif isinstance(step, ScriptStep):
            print(f"      {i+1}. Script: {step.output_key}")
    print()
    
    return default_case


def test_complete_switch_workflow():
    """Test a complete switch workflow with multiple cases and default."""
    print("🏗️ Complete Switch Workflow")
    print("-" * 50)
    
    # Create cases
    cases = test_switch_case_creation()
    default_case = test_default_case_creation()
    
    # Create complete switch step
    switch_step = SwitchStep(
        description="User role-based access control system",
        cases=cases,
        default_case=default_case,
        output_key="_"
    )
    
    # Create workflow
    workflow = Workflow(steps=[switch_step])
    
    print(f"✅ Complete switch workflow created:")
    print(f"   Description: {switch_step.description}")
    print(f"   Cases: {len(switch_step.cases)}")
    print(f"   Default case: {'Yes' if switch_step.default_case else 'No'}")
    print()
    
    return workflow


def test_yaml_generation():
    """Test YAML generation for switch expressions."""
    print("📄 YAML Generation")
    print("-" * 50)
    
    # Create a comprehensive switch workflow
    workflow = test_complete_switch_workflow()
    
    try:
        yaml_output = generate_yaml_string(workflow, "user_access_control")
        print("✅ YAML generated successfully:")
        print()
        
        # Show the YAML output
        lines = yaml_output.split('\n')
        for i, line in enumerate(lines[:30]):  # Show first 30 lines
            print(f"   {line}")
        
        if len(lines) > 30:
            print(f"   ... ({len(lines) - 30} more lines)")
            
        return yaml_output
        
    except Exception as e:
        print(f"❌ Error generating YAML: {e}")
        return None


def test_nested_switch_expressions():
    """Test nested switch expressions."""
    print("\n🔗 Nested Switch Expressions")
    print("-" * 50)
    
    # Create inner switch for admin users
    inner_switch = SwitchStep(
        description="Admin privilege level check",
        cases=[
            SwitchCase(
                condition="data.user.admin_level == 'super'",
                steps=[
                    ActionStep(
                        action_name="mw.grant_super_admin_access",
                        output_key="super_admin_result"
                    )
                ]
            ),
            SwitchCase(
                condition="data.user.admin_level == 'regular'",
                steps=[
                    ActionStep(
                        action_name="mw.grant_regular_admin_access",
                        output_key="regular_admin_result"
                    )
                ]
            )
        ],
        default_case=DefaultCase(
            steps=[
                ActionStep(
                    action_name="mw.grant_basic_admin_access",
                    output_key="basic_admin_result"
                )
            ]
        )
    )
    
    # Create outer switch
    outer_switch = SwitchStep(
        description="Main user role check",
        cases=[
            SwitchCase(
                condition="data.user.role == 'admin'",
                steps=[inner_switch]  # Nested switch
            ),
            SwitchCase(
                condition="data.user.role == 'user'",
                steps=[
                    ActionStep(
                        action_name="mw.grant_user_access",
                        output_key="user_access_result"
                    )
                ]
            )
        ],
        default_case=DefaultCase(
            steps=[
                ActionStep(
                    action_name="mw.deny_access",
                    output_key="deny_result"
                )
            ]
        )
    )
    
    workflow = Workflow(steps=[outer_switch])
    
    try:
        yaml_output = generate_yaml_string(workflow, "nested_access_control")
        print("✅ Nested switch YAML generated successfully")
        print(f"   Outer switch cases: {len(outer_switch.cases)}")
        print(f"   Inner switch cases: {len(inner_switch.cases)}")
        
        # Show a portion of the YAML
        lines = yaml_output.split('\n')
        print("\n   First 20 lines of generated YAML:")
        for i, line in enumerate(lines[:20]):
            print(f"   {line}")
            
    except Exception as e:
        print(f"❌ Error generating nested switch YAML: {e}")


def test_complex_conditions():
    """Test complex DSL conditions in switch cases."""
    print("\n🧮 Complex DSL Conditions")
    print("-" * 50)
    
    complex_conditions = [
        "data.user.age >= 18 and data.user.verified == true",
        "data.temperature > 30 or data.humidity > 80",
        "data.user.department == 'IT' and data.user.clearance_level >= 3",
        "data.request.priority == 'high' and data.request.category != 'spam'",
        "meta_info.user.email.contains('@company.com') and data.user.active == true"
    ]
    
    cases = []
    for i, condition in enumerate(complex_conditions):
        # Validate condition
        result = dsl_validator.validate_dsl_expression(condition)
        status = "✅" if result.is_valid else "❌"
        print(f"   {status} Condition {i+1}: {condition}")
        
        if result.is_valid:
            case = SwitchCase(
                condition=condition,
                steps=[
                    ActionStep(
                        action_name=f"handle_condition_{i+1}",
                        output_key=f"condition_{i+1}_result"
                    )
                ]
            )
            cases.append(case)
    
    if cases:
        switch_step = SwitchStep(
            description="Complex condition handling",
            cases=cases
        )
        
        workflow = Workflow(steps=[switch_step])
        
        try:
            yaml_output = generate_yaml_string(workflow, "complex_conditions")
            print(f"\n✅ Complex conditions switch created with {len(cases)} valid cases")
            
        except Exception as e:
            print(f"❌ Error with complex conditions: {e}")


def main():
    """Run all switch expression tests."""
    print("=" * 60)
    print("🚀 Switch Expression Implementation Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_basic_switch_creation()
        test_dsl_condition_validation()
        test_switch_case_creation()
        test_default_case_creation()
        test_complete_switch_workflow()
        test_yaml_generation()
        test_nested_switch_expressions()
        test_complex_conditions()
        
        print("\n" + "=" * 60)
        print("✅ All switch expression tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
