#!/usr/bin/env python3
"""
Test script for Phase 4 error handling constructs and built-in actions.

This script tests the new error handling step types (try/catch, raise)
and built-in actions catalog functionality.
"""

from core_structures import (
    Workflow, ActionStep, ScriptStep, RaiseStep, TryCatchStep, CatchBlock
)
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate
from mw_actions_catalog import MW_ACTIONS_CATALOG, get_action_by_name


def test_raise_step():
    """Test raise step creation and YAML generation."""
    print("Testing Raise Step...")
    
    # Create a simple raise step
    raise_step = RaiseStep(
        description="Raise an error",
        message="Something went wrong",
        output_key="error_info"
    )
    
    workflow = Workflow(steps=[raise_step])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML for Raise Step:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Raise step validation passed!")
    
    print("-" * 50)


def test_try_catch_step():
    """Test try/catch step creation and YAML generation."""
    print("Testing Try/Catch Step...")
    
    # Create action that might fail
    risky_action = ActionStep(
        action_name="mw.http_request",
        output_key="api_result",
        input_args={
            "url": "https://api.example.com/data",
            "method": "GET"
        },
        user_provided_json_output='{"status_code": 200, "body": {"data": "success"}}'
    )
    
    # Create catch block with error handling
    catch_block = CatchBlock(
        description="Handle API failure",
        steps=[
            ActionStep(
                action_name="mw.send_email",
                output_key="notification_result",
                input_args={
                    "to": "admin@company.com",
                    "subject": "API Error",
                    "body": "API request failed: error_data.api_result.error.message"
                }
            )
        ]
    )
    
    # Create try/catch step
    try_catch_step = TryCatchStep(
        description="Try API call with error handling",
        try_steps=[risky_action],
        catch_block=catch_block,
        output_key="operation_result"
    )
    
    workflow = Workflow(steps=[try_catch_step])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML for Try/Catch Step:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Try/catch step validation passed!")
    
    print("-" * 50)


def test_complex_error_handling():
    """Test complex error handling scenario."""
    print("Testing Complex Error Handling...")
    
    # Create a workflow with nested try/catch and raise
    workflow = Workflow(steps=[
        # Initial action
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.input_email"},
            user_provided_json_output='{"user": {"id": "123", "name": "John Doe", "active": true}}'
        ),
        
        # Try/catch block for user validation
        TryCatchStep(
            description="Validate user and perform action",
            try_steps=[
                # Check if user is active
                ScriptStep(
                    code="""
if not data.user_info.user.active:
    raise Exception("User is not active")
return {"validation": "passed"}
                    """.strip(),
                    output_key="validation_result",
                    user_provided_json_output='{"validation": "passed"}'
                ),
                
                # Perform action for active user
                ActionStep(
                    action_name="mw.create_ticket",
                    output_key="ticket_result",
                    input_args={
                        "title": "User Request",
                        "description": f"Request from {data.user_info.user.name}",
                        "assignee": "data.user_info.user.id"
                    }
                )
            ],
            catch_block=CatchBlock(
                description="Handle validation or action failure",
                steps=[
                    # Log the error
                    ActionStep(
                        action_name="mw.send_slack_message",
                        output_key="error_notification",
                        input_args={
                            "channel": "#errors",
                            "message": f"Failed to process user request: error_data.validation_result.error.message"
                        }
                    ),
                    
                    # Raise a custom error
                    RaiseStep(
                        description="Re-raise with custom message",
                        message="User processing failed",
                        output_key="final_error"
                    )
                ]
            ),
            output_key="processing_result"
        )
    ])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML for Complex Error Handling:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Complex error handling validation passed!")
    
    print("-" * 50)


def test_builtin_actions_catalog():
    """Test the built-in actions catalog functionality."""
    print("Testing Built-in Actions Catalog...")
    
    # Test catalog access
    print(f"Total actions in catalog: {len(MW_ACTIONS_CATALOG)}")
    
    # Test getting action by name
    user_action = get_action_by_name("mw.get_user_by_email")
    if user_action:
        print(f"Found action: {user_action.display_name}")
        print(f"Description: {user_action.description}")
        print(f"Input args: {[arg.name for arg in user_action.input_args]}")
        
        # Test creating action step with pre-filled data
        action_step = ActionStep(
            action_name=user_action.action_name,
            output_key="user_data",
            description=user_action.description,
            user_provided_json_output=user_action.typical_json_output_example
        )
        
        # Parse JSON output
        if action_step.user_provided_json_output:
            import json
            try:
                action_step.parsed_json_output = json.loads(action_step.user_provided_json_output)
                print("✓ JSON output parsed successfully")
            except json.JSONDecodeError as e:
                print(f"✗ JSON parsing failed: {e}")
        
        # Test in workflow
        workflow = Workflow(steps=[action_step])
        yaml_output = generate_yaml_string(workflow)
        print("Generated YAML for built-in action:")
        print(yaml_output)
        
    else:
        print("✗ Failed to find mw.get_user_by_email action")
    
    print("-" * 50)


def test_error_data_mapping():
    """Test error_data mapping in catch blocks."""
    print("Testing Error Data Mapping...")
    
    # Create workflow that demonstrates error_data usage
    workflow = Workflow(steps=[
        TryCatchStep(
            description="Test error data mapping",
            try_steps=[
                ActionStep(
                    action_name="mw.http_request",
                    output_key="api_call",
                    input_args={
                        "url": "https://api.example.com/fail",
                        "method": "GET"
                    }
                )
            ],
            catch_block=CatchBlock(
                description="Handle error with error_data mapping",
                steps=[
                    ActionStep(
                        action_name="mw.send_email",
                        output_key="error_email",
                        input_args={
                            "to": "admin@company.com",
                            "subject": "API Error Alert",
                            "body": "error_data.api_call.error.message"
                        }
                    ),
                    ScriptStep(
                        code="""
error_details = {
    "error_code": error_data.api_call.error.code,
    "error_message": error_data.api_call.error.message,
    "timestamp": "2025-01-27T10:30:00Z"
}
return error_details
                        """.strip(),
                        output_key="processed_error",
                        input_args={}
                    )
                ]
            ),
            output_key="error_handling_result"
        )
    ])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML with error_data mapping:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Error data mapping validation passed!")
    
    print("-" * 50)


def main():
    """Run all Phase 4 tests."""
    print("Phase 4 Error Handling & Built-in Actions Test")
    print("=" * 60)
    
    test_raise_step()
    test_try_catch_step()
    test_complex_error_handling()
    test_builtin_actions_catalog()
    test_error_data_mapping()
    
    print("Phase 4 testing complete!")


if __name__ == "__main__":
    main()
