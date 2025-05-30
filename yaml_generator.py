"""
YAML generation module for Moveworks Compound Action workflows.

This module converts internal workflow representations into syntactically correct
YAML strings that comply with Moveworks Compound Action format.

Based on Sections 2.1, 8.1, and 11.1 of the Source of Truth Document.
"""

import yaml
from typing import Dict, Any, List
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, SwitchCase, DefaultCase, ParallelBranch,
    RaiseStep, TryCatchStep, CatchBlock
)


def step_to_yaml_dict(step) -> Dict[str, Any]:
    """
    Convert a single step to a YAML-compatible dictionary.

    Args:
        step: The step instance to convert

    Returns:
        Dictionary representing the step in YAML-compatible format
    """
    step_dict = {}

    if isinstance(step, ActionStep):
        # Required fields for action steps
        step_dict['action_name'] = step.action_name
        step_dict['output_key'] = step.output_key

        # Optional fields - only include if not empty
        if step.description:
            step_dict['description'] = step.description

        if step.input_args:
            step_dict['input_args'] = step.input_args

        if step.progress_updates:
            step_dict['progress_updates'] = step.progress_updates

        if step.delay_config:
            step_dict['delay_config'] = step.delay_config

    elif isinstance(step, ScriptStep):
        # Required fields for script steps
        step_dict['code'] = step.code
        step_dict['output_key'] = step.output_key

        # Optional fields - only include if not empty
        if step.description:
            step_dict['description'] = step.description

        if step.input_args:
            step_dict['input_args'] = step.input_args

    elif isinstance(step, SwitchStep):
        step_dict['switch'] = {}

        # Add cases
        if step.cases:
            cases_list = []
            for case in step.cases:
                case_dict = {
                    'condition': case.condition,
                    'steps': [step_to_yaml_dict(nested_step) for nested_step in case.steps]
                }
                cases_list.append(case_dict)
            step_dict['switch']['cases'] = cases_list

        # Add default case if present
        if step.default_case:
            step_dict['switch']['default'] = {
                'steps': [step_to_yaml_dict(nested_step) for nested_step in step.default_case.steps]
            }

        # Add output_key if not default
        if step.output_key != "_":
            step_dict['output_key'] = step.output_key

    elif isinstance(step, ForLoopStep):
        step_dict['for'] = {
            'each': step.each,
            'in': step.in_source,
            'output_key': step.output_key,
            'steps': [step_to_yaml_dict(nested_step) for nested_step in step.steps]
        }

        # Add optional index
        if step.index:
            step_dict['for']['index'] = step.index

    elif isinstance(step, ParallelStep):
        step_dict['parallel'] = {
            'branches': []
        }

        for branch in step.branches:
            branch_dict = {
                'steps': [step_to_yaml_dict(nested_step) for nested_step in branch.steps]
            }
            if branch.name:
                branch_dict['name'] = branch.name
            step_dict['parallel']['branches'].append(branch_dict)

        # Add output_key if not default
        if step.output_key != "_":
            step_dict['output_key'] = step.output_key

    elif isinstance(step, ReturnStep):
        step_dict['return'] = step.output_mapper

        # Add output_key if not default
        if step.output_key != "_":
            step_dict['output_key'] = step.output_key

    elif isinstance(step, RaiseStep):
        step_dict['raise'] = {}

        # Add message if provided
        if step.message:
            step_dict['raise']['message'] = step.message

        # Add output_key if not default
        if step.output_key != "_":
            step_dict['output_key'] = step.output_key

    elif isinstance(step, TryCatchStep):
        step_dict['try'] = {
            'steps': [step_to_yaml_dict(nested_step) for nested_step in step.try_steps]
        }

        # Add catch block if present
        if step.catch_block:
            step_dict['catch'] = {
                'steps': [step_to_yaml_dict(nested_step) for nested_step in step.catch_block.steps]
            }

            # Add catch block description if provided
            if step.catch_block.description:
                step_dict['catch']['description'] = step.catch_block.description

        # Add output_key if not default
        if step.output_key != "_":
            step_dict['output_key'] = step.output_key

    return step_dict


def workflow_to_yaml_dict(workflow: Workflow) -> Dict[str, Any]:
    """
    Convert a Workflow instance into a Python dictionary suitable for YAML serialization.

    Args:
        workflow: The Workflow instance to convert

    Returns:
        Dictionary representing the workflow in YAML-compatible format
    """
    steps_list = []

    for step in workflow.steps:
        step_dict = step_to_yaml_dict(step)
        if step_dict:  # Only add non-empty step dictionaries
            steps_list.append(step_dict)

    return {'steps': steps_list}


def generate_yaml_string(workflow: Workflow) -> str:
    """
    Generate a YAML string from a Workflow instance.

    Args:
        workflow: The Workflow instance to convert

    Returns:
        YAML string representation of the workflow
    """
    workflow_dict = workflow_to_yaml_dict(workflow)

    # Configure YAML output for proper formatting
    yaml_string = yaml.dump(
        workflow_dict,
        default_flow_style=False,
        indent=2,
        sort_keys=False,
        allow_unicode=True
    )

    return yaml_string


# Example usage and testing
if __name__ == "__main__":
    # Create a simple workflow for testing
    from core_structures import ActionStep, ScriptStep, Workflow

    # Create an action step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"id": "12345", "name": "John Doe", "email": "john@example.com"}}'
    )

    # Create a script step
    script_step = ScriptStep(
        code="""
# APIthon script to process user data
user_name = data.user_info.user.name
processed_result = {
    "greeting": f"Hello, {user_name}!",
    "user_id": data.user_info.user.id
}
return processed_result
        """.strip(),
        output_key="processed_data",
        description="Process user information",
        input_args={},
        user_provided_json_output='{"greeting": "Hello, John Doe!", "user_id": "12345"}'
    )

    # Create workflow
    workflow = Workflow(steps=[action_step, script_step])

    # Generate and print YAML
    yaml_output = generate_yaml_string(workflow)
    print("Generated YAML:")
    print(yaml_output)

    print("\nWorkflow dictionary:")
    print(workflow_to_yaml_dict(workflow))
