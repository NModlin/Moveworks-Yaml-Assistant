#!/usr/bin/env python3
"""
Simple test to verify Phase 3 implementation.
"""

from core_structures import (
    Workflow, ActionStep, SwitchStep, SwitchCase, DefaultCase
)
from yaml_generator import generate_yaml_string

# Create a simple workflow with a switch step
action_step = ActionStep(
    action_name="mw.get_user_by_email",
    output_key="user_info",
    input_args={"email": "data.input_email"}
)

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

default_case = DefaultCase(
    steps=[
        ActionStep(
            action_name="mw.log_event",
            output_key="log_result",
            input_args={"event": "Unknown user status"}
        )
    ]
)

switch_step = SwitchStep(
    description="Handle user based on status",
    cases=[case1],
    default_case=default_case,
    output_key="_"
)

workflow = Workflow(steps=[action_step, switch_step])

# Generate YAML
try:
    yaml_output = generate_yaml_string(workflow)
    print("YAML Generation Successful!")
    print("Generated YAML:")
    print(yaml_output)
except Exception as e:
    print(f"Error: {e}")
