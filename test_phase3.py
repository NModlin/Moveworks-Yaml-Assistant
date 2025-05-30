#!/usr/bin/env python3
"""
Test script for Phase 3 control flow constructs.

This script tests the new control flow step types (switch, for, parallel, return)
and their YAML generation and validation.
"""

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep, 
    ParallelStep, ReturnStep, SwitchCase, DefaultCase, ParallelBranch
)
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate


def test_switch_step():
    """Test switch step creation and YAML generation."""
    print("Testing Switch Step...")
    
    # Create a simple action step first
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"status": "active", "role": "admin"}}'
    )
    
    # Create switch cases
    case1 = SwitchCase(
        condition="data.user_info.user.status == 'active'",
        steps=[
            ActionStep(
                action_name="mw.send_notification",
                output_key="notification_result",
                input_args={"message": "User is active"}
            )
        ]
    )
    
    case2 = SwitchCase(
        condition="data.user_info.user.role == 'admin'",
        steps=[
            ActionStep(
                action_name="mw.grant_admin_access",
                output_key="admin_result",
                input_args={"user_id": "data.user_info.user.id"}
            )
        ]
    )
    
    default_case = DefaultCase(
        steps=[
            ActionStep(
                action_name="mw.log_event",
                output_key="log_result",
                input_args={"event": "Unknown user status"}
            )
        ]
    )
    
    # Create switch step
    switch_step = SwitchStep(
        description="Handle user based on status and role",
        cases=[case1, case2],
        default_case=default_case,
        output_key="_"
    )
    
    # Create workflow
    workflow = Workflow(steps=[action_step, switch_step])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Switch step validation passed!")
    
    print("-" * 50)


def test_for_loop_step():
    """Test for loop step creation and YAML generation."""
    print("Testing For Loop Step...")
    
    # Create action that returns an array
    action_step = ActionStep(
        action_name="mw.get_all_users",
        output_key="users_list",
        input_args={},
        user_provided_json_output='{"users": [{"id": "1", "name": "John"}, {"id": "2", "name": "Jane"}]}'
    )
    
    # Create for loop step
    for_step = ForLoopStep(
        description="Process each user",
        each="currentUser",
        index="i",
        in_source="data.users_list.users",
        output_key="processed_users",
        steps=[
            ActionStep(
                action_name="mw.update_user",
                output_key="update_result",
                input_args={
                    "user_id": "currentUser.id",
                    "name": "currentUser.name"
                }
            )
        ]
    )
    
    # Create workflow
    workflow = Workflow(steps=[action_step, for_step])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ For loop step validation passed!")
    
    print("-" * 50)


def test_parallel_step():
    """Test parallel step creation and YAML generation."""
    print("Testing Parallel Step...")
    
    # Create parallel branches
    branch1 = ParallelBranch(
        name="email_branch",
        steps=[
            ActionStep(
                action_name="mw.send_email",
                output_key="email_result",
                input_args={"recipient": "data.input_email"}
            )
        ]
    )
    
    branch2 = ParallelBranch(
        name="slack_branch",
        steps=[
            ActionStep(
                action_name="mw.send_slack_message",
                output_key="slack_result",
                input_args={"channel": "#general"}
            )
        ]
    )
    
    # Create parallel step
    parallel_step = ParallelStep(
        description="Send notifications in parallel",
        branches=[branch1, branch2],
        output_key="_"
    )
    
    # Create workflow
    workflow = Workflow(steps=[parallel_step])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Parallel step validation passed!")
    
    print("-" * 50)


def test_return_step():
    """Test return step creation and YAML generation."""
    print("Testing Return Step...")
    
    # Create some action steps first
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"id": "123", "name": "John Doe"}}'
    )
    
    action2 = ActionStep(
        action_name="mw.get_user_permissions",
        output_key="permissions",
        input_args={"user_id": "data.user_info.user.id"},
        user_provided_json_output='{"permissions": ["read", "write"]}'
    )
    
    # Create return step
    return_step = ReturnStep(
        description="Return user summary",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_permissions": "data.permissions.permissions"
        },
        output_key="_"
    )
    
    # Create workflow
    workflow = Workflow(steps=[action1, action2, return_step])
    
    # Generate YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML:")
    print(yaml_output)
    
    # Validate
    errors = comprehensive_validate(workflow)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Return step validation passed!")
    
    print("-" * 50)


def main():
    """Run all Phase 3 tests."""
    print("Phase 3 Control Flow Constructs Test")
    print("=" * 50)
    
    test_switch_step()
    test_for_loop_step()
    test_parallel_step()
    test_return_step()
    
    print("Phase 3 testing complete!")


if __name__ == "__main__":
    main()
