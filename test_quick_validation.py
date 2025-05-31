#!/usr/bin/env python3
"""
Quick test for enhanced validation features.
"""

from core_structures import *
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate

def test_switch_validation():
    """Test switch validation improvements."""
    print("Testing Switch Validation...")
    
    # Create action with JSON output
    action = ActionStep(
        action_name='mw.get_user',
        output_key='user_info',
        user_provided_json_output='{"user": {"status": "active", "role": "admin"}}'
    )
    
    # Create switch with condition
    switch = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.user_info.user.status == 'active'",
                steps=[
                    ActionStep(
                        action_name='mw.notify',
                        output_key='notify_result'
                    )
                ]
            )
        ]
    )
    
    workflow = Workflow(steps=[action, switch])
    
    # Test without context
    errors = comprehensive_validate(workflow)
    print(f"Errors without context: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
    
    # Test with context
    context = DataContext(initial_inputs={'input_email': 'test@example.com'})
    errors = comprehensive_validate(workflow, context)
    print(f"Errors with context: {len(errors)}")
    for e in errors:
        print(f"  - {e}")

def test_data_type_validation():
    """Test data type validation."""
    print("\nTesting Data Type Validation...")
    
    # Create action with invalid input_args type
    action = ActionStep(
        action_name='mw.test',
        output_key='test_output',
        input_args="invalid_type"  # Should be dict
    )
    
    workflow = Workflow(steps=[action])
    errors = comprehensive_validate(workflow)
    
    print(f"Data type validation errors: {len(errors)}")
    for e in errors:
        print(f"  - {e}")

def test_try_catch_validation():
    """Test try/catch validation."""
    print("\nTesting Try/Catch Validation...")
    
    # Create try/catch with valid status codes
    try_catch = TryCatchStep(
        try_steps=[
            ActionStep(
                action_name='mw.risky_action',
                output_key='risky_result'
            )
        ],
        catch_block=CatchBlock(
            on_status_code=[400, 404],
            steps=[
                ActionStep(
                    action_name='mw.handle_error',
                    output_key='error_result'
                )
            ]
        )
    )
    
    workflow = Workflow(steps=[try_catch])
    errors = comprehensive_validate(workflow)
    
    print(f"Try/catch validation errors: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML:")
    print(yaml_output)

def test_output_key_validation():
    """Test output key validation."""
    print("\nTesting Output Key Validation...")
    
    # Test invalid output keys
    invalid_keys = ['123invalid', 'data', 'invalid@key', 'a', 'a' * 51]
    
    for key in invalid_keys:
        action = ActionStep(
            action_name='mw.test',
            output_key=key
        )
        workflow = Workflow(steps=[action])
        errors = comprehensive_validate(workflow)
        
        output_key_errors = [e for e in errors if 'Output key' in e]
        print(f"Key '{key}': {len(output_key_errors)} errors")
        for e in output_key_errors:
            print(f"  - {e}")

if __name__ == "__main__":
    print("🔍 QUICK VALIDATION TESTING")
    print("=" * 50)
    
    test_switch_validation()
    test_data_type_validation()
    test_try_catch_validation()
    test_output_key_validation()
    
    print("\n✅ Quick validation testing complete!")
