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
    RaiseStep, TryCatchStep, CatchBlock, ParallelForLoop
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
        # Create action dict following yaml_syntex.md format
        # Use default values for empty required fields to prevent validation errors
        action_name = step.action_name if step.action_name and step.action_name.strip() else ''
        output_key = step.output_key if step.output_key and step.output_key.strip() else ''

        action_dict = {
            'action_name': action_name,
            'output_key': output_key
        }

        # Add optional fields in the correct order
        if step.input_args:
            action_dict['input_args'] = step.input_args

        if step.delay_config:
            # Ensure delay_config has proper structure
            delay_config = step.delay_config.copy() if isinstance(step.delay_config, dict) else step.delay_config
            action_dict['delay_config'] = delay_config

        if step.progress_updates:
            action_dict['progress_updates'] = step.progress_updates

        step_dict['action'] = action_dict

    elif isinstance(step, ScriptStep):
        # Create script dict following yaml_syntex.md format
        # Use default values for empty required fields to prevent validation errors
        output_key = step.output_key if step.output_key and step.output_key.strip() else ''
        code = step.code if step.code and step.code.strip() else ''

        script_dict = {
            'output_key': output_key
        }

        # Add input_args before code if present
        if step.input_args:
            script_dict['input_args'] = step.input_args

        # Add code field
        script_dict['code'] = code

        step_dict['script'] = script_dict

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
        # Create for loop dict following yaml_syntex.md format
        for_dict = {
            'each': step.each
        }

        # Add index if present
        if step.index:
            for_dict['index'] = step.index

        for_dict['in'] = step.in_source
        for_dict['output_key'] = step.output_key

        # Add steps
        if step.steps:
            for_dict['steps'] = [step_to_yaml_dict(nested_step) for nested_step in step.steps]

        step_dict['for'] = for_dict

    elif isinstance(step, ParallelStep):
        parallel_dict = {}

        # Handle parallel for loop mode
        if step.for_loop:
            for_config = {
                'each': step.for_loop.each,
                'in': step.for_loop.in_source
            }

            if step.for_loop.index_key:
                for_config['index_key'] = step.for_loop.index_key

            for_config['output_key'] = step.for_loop.output_key

            if step.for_loop.steps:
                for_config['steps'] = [step_to_yaml_dict(nested_step) for nested_step in step.for_loop.steps]

            parallel_dict['for'] = for_config

        # Handle parallel branches mode
        elif step.branches:
            branches_list = []
            for branch in step.branches:
                branch_dict = {
                    'steps': [step_to_yaml_dict(nested_step) for nested_step in branch.steps]
                }
                if branch.name:
                    branch_dict['name'] = branch.name
                branches_list.append(branch_dict)
            parallel_dict['branches'] = branches_list

        step_dict['parallel'] = parallel_dict

    elif isinstance(step, ReturnStep):
        # Create return dict following yaml_syntex.md format
        if step.output_mapper:
            step_dict['return'] = {'output_mapper': step.output_mapper}
        else:
            step_dict['return'] = {}

    elif isinstance(step, RaiseStep):
        # Create raise dict following yaml_syntex.md format
        raise_dict = {}

        if step.output_key and step.output_key != "_":
            raise_dict['output_key'] = step.output_key

        if step.message:
            raise_dict['message'] = step.message

        step_dict['raise'] = raise_dict

    elif isinstance(step, TryCatchStep):
        # Create try_catch dict following yaml_syntex.md format
        try_catch_dict = {
            'try': {
                'steps': [step_to_yaml_dict(nested_step) for nested_step in step.try_steps]
            }
        }

        # Add catch block if present
        if step.catch_block:
            catch_dict = {}

            # Add on_status_code if present (ensure proper format)
            if step.catch_block.on_status_code:
                if isinstance(step.catch_block.on_status_code, list):
                    # Convert string numbers to integers if needed
                    status_codes = []
                    for code in step.catch_block.on_status_code:
                        try:
                            status_codes.append(int(code))
                        except (ValueError, TypeError):
                            status_codes.append(code)  # Keep original if conversion fails
                    catch_dict['on_status_code'] = status_codes
                else:
                    # Single status code
                    try:
                        catch_dict['on_status_code'] = int(step.catch_block.on_status_code)
                    except (ValueError, TypeError):
                        catch_dict['on_status_code'] = step.catch_block.on_status_code

            catch_dict['steps'] = [step_to_yaml_dict(nested_step) for nested_step in step.catch_block.steps]

            try_catch_dict['catch'] = catch_dict

        step_dict['try_catch'] = try_catch_dict

    return step_dict


def workflow_to_yaml_dict(workflow: Workflow) -> Dict[str, Any]:
    """
    Convert a Workflow instance into a Python dictionary suitable for YAML serialization.

    Following yaml_syntex.md format:
    - Single expression: no 'steps' wrapper
    - Multiple expressions: wrapped in 'steps' list

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

    # Handle single expression vs multiple expressions
    if len(steps_list) == 1:
        # Single expression - return without 'steps' wrapper
        return steps_list[0]
    else:
        # Multiple expressions - wrap in 'steps' list
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
