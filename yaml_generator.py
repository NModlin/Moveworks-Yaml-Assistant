"""
YAML generation module for Moveworks Compound Action workflows.

This module converts internal workflow representations into syntactically correct
YAML strings that comply with Moveworks Compound Action format with enhanced
compliance refinements for field naming standardization and DSL string formatting.

Based on Sections 2.1, 8.1, and 11.1 of the Source of Truth Document.
"""

import yaml
import re
from typing import Dict, Any, List
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, SwitchCase, DefaultCase, ParallelBranch,
    RaiseStep, TryCatchStep, CatchBlock, ParallelForLoop
)


def _is_dsl_expression(value: str) -> bool:
    """
    Check if a string value contains Moveworks DSL expressions that need quoting.

    Args:
        value: String value to check

    Returns:
        True if the value contains DSL expressions, False otherwise
    """
    if not isinstance(value, str):
        return False

    # DSL patterns that need string quoting in YAML
    dsl_patterns = [
        r'\bdata\.[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*',  # data.field_name
        r'\bmeta_info\.[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*',  # meta_info.user.email
        r'\bdata\.[a-zA-Z_][a-zA-Z0-9_]*\[[0-9]+\]',  # data.array[0]
        r'==|!=|>=|<=|>|<',  # Comparison operators in conditions
        r'\$CONCAT\(',  # Moveworks functions
        r'\$[A-Z_]+\(',  # Other Moveworks functions
    ]

    return any(re.search(pattern, value) for pattern in dsl_patterns)


def _ensure_dsl_string_quoting(obj: Any) -> Any:
    """
    Recursively ensure DSL expressions are properly quoted as strings.

    Args:
        obj: Object to process (dict, list, or primitive)

    Returns:
        Processed object with DSL expressions as quoted strings
    """
    if isinstance(obj, dict):
        return {key: _ensure_dsl_string_quoting(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_ensure_dsl_string_quoting(item) for item in obj]
    elif isinstance(obj, str) and _is_dsl_expression(obj):
        # Return as-is - YAML serializer will handle quoting
        return obj
    else:
        return obj


def _to_snake_case(name: str) -> str:
    """
    Convert a string to snake_case format for field naming standardization.

    Args:
        name: String to convert

    Returns:
        String in snake_case format
    """
    if not isinstance(name, str):
        return str(name)

    # Handle camelCase and PascalCase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)

    # Convert to lowercase and replace any remaining non-alphanumeric with underscore
    result = re.sub(r'[^a-zA-Z0-9_]', '_', s2).lower()

    # Remove multiple consecutive underscores
    result = re.sub(r'_+', '_', result)

    # Remove leading/trailing underscores
    return result.strip('_')


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

        # Add optional fields in the correct order with proper type enforcement and DSL formatting
        if step.input_args:
            if isinstance(step.input_args, dict):
                # Apply DSL string formatting to input_args values
                formatted_input_args = _ensure_dsl_string_quoting(step.input_args)
                action_dict['input_args'] = formatted_input_args
            else:
                # Convert to dict if not already and apply DSL formatting
                input_args_dict = dict(step.input_args) if step.input_args else {}
                action_dict['input_args'] = _ensure_dsl_string_quoting(input_args_dict)

        if step.description:
            action_dict['description'] = str(step.description)

        if step.delay_config:
            if isinstance(step.delay_config, dict):
                # Ensure delay_seconds is an integer
                delay_config = step.delay_config.copy()
                if 'delay_seconds' in delay_config:
                    try:
                        delay_config['delay_seconds'] = int(delay_config['delay_seconds'])
                    except (ValueError, TypeError):
                        delay_config['delay_seconds'] = 0
                action_dict['delay_config'] = delay_config
            else:
                action_dict['delay_config'] = step.delay_config

        if step.progress_updates:
            if isinstance(step.progress_updates, dict):
                action_dict['progress_updates'] = step.progress_updates
            else:
                # Convert to dict if not already
                action_dict['progress_updates'] = dict(step.progress_updates) if step.progress_updates else {}

        step_dict['action'] = action_dict

    elif isinstance(step, ScriptStep):
        # Create script dict following APIthon YAML format requirements
        # Use default values for empty required fields to prevent validation errors
        output_key = step.output_key if step.output_key and step.output_key.strip() else ''
        code = step.code if step.code and step.code.strip() else ''

        script_dict = {}

        # Add code field first with proper YAML literal block scalar format
        # The YAML library will handle the literal block scalar (|) formatting
        script_dict['code'] = code

        # Add output_key as required field
        script_dict['output_key'] = output_key

        # Add input_args if present (optional field) - enforce dict type with DSL formatting
        if step.input_args:
            if isinstance(step.input_args, dict):
                # Apply DSL string formatting to input_args values
                formatted_input_args = _ensure_dsl_string_quoting(step.input_args)
                script_dict['input_args'] = formatted_input_args
            else:
                # Convert to dict if not already and apply DSL formatting
                input_args_dict = dict(step.input_args) if step.input_args else {}
                script_dict['input_args'] = _ensure_dsl_string_quoting(input_args_dict)

        # Add description if present
        if step.description:
            script_dict['description'] = str(step.description)

        step_dict['script'] = script_dict

    elif isinstance(step, SwitchStep):
        step_dict['switch'] = {}

        # Add cases with DSL string formatting for conditions
        if step.cases:
            cases_list = []
            for case in step.cases:
                # Apply DSL string formatting to condition if it contains DSL expressions
                condition = case.condition
                if isinstance(condition, str) and _is_dsl_expression(condition):
                    condition = condition  # Keep as string for YAML quoting

                case_dict = {
                    'condition': condition,
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
        # Create return dict following yaml_syntex.md format with DSL string formatting
        if step.output_mapper:
            # Apply DSL string formatting to output_mapper values
            formatted_output_mapper = _ensure_dsl_string_quoting(step.output_mapper)
            step_dict['return'] = {'output_mapper': formatted_output_mapper}
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


def workflow_to_yaml_dict(workflow: Workflow, action_name: str = None) -> Dict[str, Any]:
    """
    Convert a Workflow instance into a Python dictionary suitable for YAML serialization.

    Following Moveworks Compound Action format requirements:
    - Mandatory top-level fields: action_name (string) and steps (list)
    - Single expression: wrapped in steps list for consistency
    - Multiple expressions: wrapped in steps list
    - Proper data type enforcement for all fields

    Args:
        workflow: The Workflow instance to convert
        action_name: Optional action name for the compound action

    Returns:
        Dictionary representing the workflow in YAML-compatible format
    """
    steps_list = []

    for step in workflow.steps:
        step_dict = step_to_yaml_dict(step)
        if step_dict:  # Only add non-empty step dictionaries
            steps_list.append(step_dict)

    # Create the compound action structure with mandatory fields
    compound_action = {
        "action_name": action_name or "compound_action",
        "steps": steps_list
    }

    return compound_action


def generate_yaml_string(workflow: Workflow, action_name: str = None) -> str:
    """
    Generate a YAML string from a Workflow instance with proper APIthon script formatting.

    Args:
        workflow: The Workflow instance to convert
        action_name: Optional action name for the compound action

    Returns:
        YAML string representation of the workflow with literal block scalars for script code
    """
    workflow_dict = workflow_to_yaml_dict(workflow, action_name)

    # Custom YAML representer for multiline strings and DSL expressions
    def represent_literal_str(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        elif _is_dsl_expression(data):
            # Force DSL expressions to be quoted
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    # Add custom representer for script code and DSL expressions
    yaml.add_representer(str, represent_literal_str)

    try:
        # Configure YAML output for proper formatting
        yaml_string = yaml.dump(
            workflow_dict,
            default_flow_style=False,
            indent=2,
            sort_keys=False,
            allow_unicode=True,
            width=1000  # Prevent line wrapping for long strings
        )
    finally:
        # Reset the representer to avoid affecting other YAML operations
        yaml.representer.Representer.yaml_representers[str] = yaml.representer.Representer.represent_str

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
