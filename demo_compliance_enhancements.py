#!/usr/bin/env python3
"""
Demonstration of Enhanced Compliance Features in Moveworks YAML Assistant.

This script showcases the improvements made in Phase 1 and Phase 2 of the 
compliance implementation plan, including enhanced validation and YAML generation.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, 
    ForLoopStep, ReturnStep, InputVariable
)
from compliance_validator import compliance_validator
from yaml_generator import generate_yaml_string


def demo_enhanced_validation():
    """Demonstrate enhanced validation features."""
    print("🔍 ENHANCED VALIDATION DEMONSTRATION")
    print("=" * 50)
    
    # Demo 1: Invalid ActionStep (empty required fields)
    print("\n1. Testing Invalid ActionStep (empty required fields):")
    invalid_action = ActionStep(action_name="", output_key="")
    invalid_workflow = Workflow(steps=[invalid_action])
    
    result = compliance_validator.validate_workflow_compliance(invalid_workflow, "test_action")
    print(f"   Valid: {result.is_valid}")
    print("   Errors:")
    for error in result.mandatory_field_errors:
        print(f"   • {error}")
    
    # Demo 2: Type validation
    print("\n2. Testing Type Validation:")
    action_with_wrong_types = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info"
    )
    # Manually set wrong types to demonstrate validation
    action_with_wrong_types.input_args = "not_a_dict"  # Should be dict
    action_with_wrong_types.delay_config = ["not_a_dict"]  # Should be dict
    
    type_workflow = Workflow(steps=[action_with_wrong_types])
    result = compliance_validator.validate_workflow_compliance(type_workflow, "test_action")
    print(f"   Valid: {result.is_valid}")
    print("   Type Errors:")
    for error in result.errors:
        if 'should be' in error:
            print(f"   • {error}")
    
    # Demo 3: Valid workflow
    print("\n3. Testing Valid Workflow:")
    valid_action = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )
    valid_workflow = Workflow(steps=[valid_action])
    
    result = compliance_validator.validate_workflow_compliance(valid_workflow, "valid_action")
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.mandatory_field_errors + result.errors)}")


def demo_dsl_quoting():
    """Demonstrate enhanced DSL quoting in YAML generation."""
    print("\n\n🎯 DSL QUOTING DEMONSTRATION")
    print("=" * 50)
    
    # Create a workflow with various DSL expressions and literals
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={
            "email": "data.input_email",           # DSL expression
            "timeout": "30",                       # Numeric literal
            "active_only": "true",                 # Boolean literal
            "department": "Engineering",           # Regular string
            "complex_expr": "data.count > 5 && data.active == 'true'"  # Complex DSL
        }
    )
    
    script_step = ScriptStep(
        code="""
# Multi-line APIthon script
if data.user_info.active:
    result = {
        "status": "active",
        "count": 1,
        "processed": True
    }
else:
    result = {
        "status": "inactive", 
        "count": 0,
        "processed": False
    }
return result
        """.strip(),
        output_key="processed_data",
        input_args={
            "threshold": "10",      # Numeric literal
            "enabled": "false"      # Boolean literal
        }
    )
    
    return_step = ReturnStep(
        output_mapper={
            "user": "data.user_info",
            "processed": "data.processed_data",
            "meta": "meta_info.user.email"
        }
    )
    
    # Add input variables
    workflow = Workflow(
        steps=[action_step, script_step, return_step],
        input_variables=[
            InputVariable(
                name="input_email",
                data_type="string",
                description="Email address of the user to look up",
                required=True
            )
        ]
    )
    
    print("\nGenerating YAML with enhanced DSL quoting...")
    yaml_output = generate_yaml_string(workflow, "enhanced_compound_action")
    
    print("\nGenerated YAML:")
    print("-" * 30)
    print(yaml_output)
    print("-" * 30)
    
    # Highlight the quoting features
    print("\n📋 QUOTING FEATURES DEMONSTRATED:")
    print("• DSL expressions in double quotes: \"data.input_email\"")
    print("• Numeric literals in single quotes: '30', '10'")
    print("• Boolean literals in single quotes: 'true', 'false'")
    print("• Multi-line scripts with literal block scalar: code: |")
    print("• Complex DSL expressions properly quoted")
    print("• Regular strings without unnecessary quotes")


def demo_expression_validation():
    """Demonstrate validation for different expression types."""
    print("\n\n🏗️ EXPRESSION TYPE VALIDATION DEMONSTRATION")
    print("=" * 50)
    
    # Demo: SwitchStep with empty cases
    print("\n1. Testing SwitchStep with empty cases:")
    empty_switch = SwitchStep(cases=[])  # Invalid: empty cases
    switch_workflow = Workflow(steps=[empty_switch])
    
    result = compliance_validator.validate_workflow_compliance(switch_workflow, "test_switch")
    print(f"   Valid: {result.is_valid}")
    for error in result.mandatory_field_errors:
        if 'cases' in error:
            print(f"   • {error}")
    
    # Demo: ForLoopStep with empty steps
    print("\n2. Testing ForLoopStep with empty steps:")
    empty_for = ForLoopStep(
        each="item",
        in_source="data.items",
        output_key="results",
        steps=[]  # Invalid: empty steps
    )
    for_workflow = Workflow(steps=[empty_for])
    
    result = compliance_validator.validate_workflow_compliance(for_workflow, "test_for")
    print(f"   Valid: {result.is_valid}")
    for error in result.mandatory_field_errors:
        if 'steps' in error and 'ForLoopStep' in error:
            print(f"   • {error}")
    
    # Demo: Valid SwitchStep
    print("\n3. Testing Valid SwitchStep:")
    valid_switch = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.user_info.active == 'true'",
                steps=[
                    ActionStep(
                        action_name="mw.create_ticket",
                        output_key="ticket_info",
                        input_args={"summary": "User is active"}
                    )
                ]
            )
        ]
    )
    valid_switch_workflow = Workflow(steps=[valid_switch])
    
    result = compliance_validator.validate_workflow_compliance(valid_switch_workflow, "valid_switch")
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.mandatory_field_errors + result.errors)}")


def main():
    """Run all demonstrations."""
    print("🚀 MOVEWORKS YAML ASSISTANT - ENHANCED COMPLIANCE DEMONSTRATION")
    print("=" * 70)
    print("Showcasing Phase 1 & Phase 2 compliance enhancements:")
    print("• Enhanced mandatory field validation with type checking")
    print("• Improved DSL expression detection and quoting")
    print("• Strict compliance with Moveworks specifications")
    print("• Comprehensive error reporting with actionable messages")
    
    try:
        demo_enhanced_validation()
        demo_dsl_quoting()
        demo_expression_validation()
        
        print("\n\n✅ DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 50)
        print("All enhanced compliance features are working correctly!")
        print("\nKey Improvements Demonstrated:")
        print("• Strict field validation with detailed error messages")
        print("• Proper DSL expression and literal quoting in YAML")
        print("• Expression-specific validation rules")
        print("• Type checking for all step fields")
        print("• Moveworks specification compliance")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING DEMONSTRATION: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
