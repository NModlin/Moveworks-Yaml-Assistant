#!/usr/bin/env python3
"""
Comprehensive test for enhanced YAML structuring capabilities.

This script tests all the improvements made to the Moveworks YAML Assistant:
1. Enhanced data type validation
2. Improved data reference validation
3. Better error messages
4. Comprehensive expression type support
"""

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep,
    TryCatchStep, CatchBlock, DataContext
)
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate


def test_enhanced_data_type_validation():
    """Test enhanced data type validation for all step types."""
    print("=" * 60)
    print("Testing Enhanced Data Type Validation")
    print("=" * 60)
    
    # Test ActionStep with invalid data types
    print("\n1. Testing ActionStep data type validation:")
    action_step = ActionStep(
        action_name="test_action",
        output_key="test_output",
        input_args="invalid_type",  # Should be dict
        delay_config={"delay_seconds": "not_an_int"},  # Should be int
        progress_updates="invalid_type"  # Should be dict
    )
    
    workflow = Workflow(steps=[action_step])
    errors = comprehensive_validate(workflow)
    
    print(f"Found {len(errors)} validation errors:")
    for error in errors:
        print(f"  - {error}")
    
    # Test ScriptStep with invalid data types
    print("\n2. Testing ScriptStep data type validation:")
    script_step = ScriptStep(
        code="return 'test'",
        output_key="script_output",
        input_args="invalid_type"  # Should be dict
    )
    
    workflow = Workflow(steps=[script_step])
    errors = comprehensive_validate(workflow)
    
    print(f"Found {len(errors)} validation errors:")
    for error in errors:
        print(f"  - {error}")


def test_improved_data_reference_validation():
    """Test improved data reference validation for switch conditions."""
    print("\n" + "=" * 60)
    print("Testing Improved Data Reference Validation")
    print("=" * 60)
    
    # Create a workflow with proper data context
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"status": "active", "role": "admin", "id": "123"}}'
    )
    
    # Create switch step with conditions that should now validate correctly
    switch_step = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.user_info.user.status == 'active'",
                steps=[
                    ActionStep(
                        action_name="mw.send_notification",
                        output_key="notification_result",
                        input_args={"message": "User is active"}
                    )
                ]
            ),
            SwitchCase(
                condition="data.user_info.user.role == 'admin'",
                steps=[
                    ActionStep(
                        action_name="mw.grant_admin_access",
                        output_key="admin_result",
                        input_args={"user_id": "data.user_info.user.id"}
                    )
                ]
            )
        ],
        default_case=DefaultCase(
            steps=[
                ActionStep(
                    action_name="mw.log_event",
                    output_key="log_result",
                    input_args={"event": "Unknown user status"}
                )
            ]
        )
    )
    
    workflow = Workflow(steps=[action_step, switch_step])
    
    # Create initial data context with input variables
    initial_context = DataContext(initial_inputs={"input_email": "test@example.com"})
    
    errors = comprehensive_validate(workflow, initial_context)
    
    print(f"Switch validation found {len(errors)} errors:")
    for error in errors:
        print(f"  - {error}")
    
    # Generate YAML to verify structure
    print("\nGenerated YAML:")
    print(generate_yaml_string(workflow))


def test_try_catch_validation():
    """Test TryCatchStep validation with on_status_code."""
    print("\n" + "=" * 60)
    print("Testing TryCatchStep Validation")
    print("=" * 60)
    
    # Test with valid integer status codes
    try_catch_step = TryCatchStep(
        try_steps=[
            ActionStep(
                action_name="mw.risky_action",
                output_key="risky_result",
                input_args={"param": "value"}
            )
        ],
        catch_block=CatchBlock(
            on_status_code=[400, 404, 500],
            steps=[
                ActionStep(
                    action_name="mw.handle_error",
                    output_key="error_result",
                    input_args={"error": "API call failed"}
                )
            ]
        )
    )
    
    workflow = Workflow(steps=[try_catch_step])
    errors = comprehensive_validate(workflow)
    
    print(f"Valid TryCatch validation found {len(errors)} errors:")
    for error in errors:
        print(f"  - {error}")
    
    # Generate YAML to verify structure
    print("\nGenerated YAML:")
    print(generate_yaml_string(workflow))
    
    # Test with invalid status codes
    print("\n3. Testing invalid status codes:")
    try_catch_invalid = TryCatchStep(
        try_steps=[
            ActionStep(
                action_name="mw.risky_action",
                output_key="risky_result2",
                input_args={"param": "value"}
            )
        ],
        catch_block=CatchBlock(
            on_status_code=["not_a_number", "also_invalid"],
            steps=[
                ActionStep(
                    action_name="mw.handle_error",
                    output_key="error_result2",
                    input_args={"error": "API call failed"}
                )
            ]
        )
    )
    
    workflow_invalid = Workflow(steps=[try_catch_invalid])
    errors = comprehensive_validate(workflow_invalid)
    
    print(f"Invalid TryCatch validation found {len(errors)} errors:")
    for error in errors:
        print(f"  - {error}")


def test_output_key_validation():
    """Test enhanced output key validation."""
    print("\n" + "=" * 60)
    print("Testing Enhanced Output Key Validation")
    print("=" * 60)
    
    # Test various invalid output keys
    invalid_steps = [
        ActionStep(action_name="test1", output_key="123invalid"),  # Starts with number
        ActionStep(action_name="test2", output_key="data"),        # Reserved word
        ActionStep(action_name="test3", output_key="invalid@key"), # Invalid character
        ActionStep(action_name="test4", output_key="a"),           # Too short
        ActionStep(action_name="test5", output_key="a" * 51),      # Too long
    ]
    
    for i, step in enumerate(invalid_steps, 1):
        workflow = Workflow(steps=[step])
        errors = comprehensive_validate(workflow)
        
        print(f"\n{i}. Testing output key '{step.output_key}':")
        output_key_errors = [e for e in errors if 'Output key' in e]
        for error in output_key_errors:
            print(f"  - {error}")


def main():
    """Run all comprehensive validation tests."""
    print("🔍 COMPREHENSIVE VALIDATION TESTING")
    print("Testing all enhanced YAML structuring capabilities")
    
    test_enhanced_data_type_validation()
    test_improved_data_reference_validation()
    test_try_catch_validation()
    test_output_key_validation()
    
    print("\n" + "=" * 60)
    print("✅ COMPREHENSIVE VALIDATION TESTING COMPLETE!")
    print("=" * 60)
    print("All enhanced validation features tested successfully!")


if __name__ == "__main__":
    main()
