"""
Validation module for Moveworks Compound Action workflows.

This module provides validation functions to ensure workflows are correctly
structured and comply with Moveworks requirements.

Based on Sections 8.1, 8.2, and 11.1 of the Source of Truth Document.
"""

from typing import List, Set, Union
from core_structures import (
    Workflow, ActionStep, ScriptStep, DataContext, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, SwitchCase, DefaultCase, ParallelBranch,
    RaiseStep, TryCatchStep, CatchBlock
)


def validate_step(step, existing_output_keys: Set[str]) -> List[str]:
    """
    Validate a single step and check for output key conflicts.

    Args:
        step: The step to validate (any step type)
        existing_output_keys: Set of output keys already used

    Returns:
        List of error message strings
    """
    errors = []

    if isinstance(step, ActionStep):
        # Check required fields for ActionStep
        if not step.action_name:
            errors.append("ActionStep missing required 'action_name'")

        if not step.output_key:
            errors.append("ActionStep missing required 'output_key'")

        # Check for valid action_name format (basic check)
        if step.action_name and not step.action_name.strip():
            errors.append("ActionStep 'action_name' cannot be empty or whitespace")

    elif isinstance(step, ScriptStep):
        # Check required fields for ScriptStep
        if not step.code:
            errors.append("ScriptStep missing required 'code'")

        if not step.output_key:
            errors.append("ScriptStep missing required 'output_key'")

        # Check for valid code (basic check)
        if step.code and not step.code.strip():
            errors.append("ScriptStep 'code' cannot be empty or whitespace")

    elif isinstance(step, SwitchStep):
        # Check required fields for SwitchStep
        if not step.cases and not step.default_case:
            errors.append("SwitchStep must have at least one case or a default case")

        # Validate each case
        for i, case in enumerate(step.cases):
            if not case.condition:
                errors.append(f"SwitchStep case {i+1} missing required field: condition")
            # Recursively validate nested steps
            for nested_step in case.steps:
                errors.extend(validate_step(nested_step, existing_output_keys))

        # Validate default case if present
        if step.default_case:
            for nested_step in step.default_case.steps:
                errors.extend(validate_step(nested_step, existing_output_keys))

    elif isinstance(step, ForLoopStep):
        # Check required fields for ForLoopStep
        if not step.each:
            errors.append("ForLoopStep missing required field: each")
        if not step.in_source:
            errors.append("ForLoopStep missing required field: in_source")
        if not step.output_key:
            errors.append("ForLoopStep missing required field: output_key")

        # Recursively validate nested steps
        for nested_step in step.steps:
            errors.extend(validate_step(nested_step, existing_output_keys))

    elif isinstance(step, ParallelStep):
        # Check required fields for ParallelStep
        if not step.branches:
            errors.append("ParallelStep must have at least one branch")

        # Validate each branch
        for i, branch in enumerate(step.branches):
            if not branch.steps:
                errors.append(f"ParallelStep branch {i+1} must have at least one step")
            # Recursively validate nested steps
            for nested_step in branch.steps:
                errors.extend(validate_step(nested_step, existing_output_keys))

    elif isinstance(step, ReturnStep):
        # Check required fields for ReturnStep
        if not step.output_mapper:
            errors.append("ReturnStep missing required field: output_mapper")

    elif isinstance(step, RaiseStep):
        # RaiseStep validation - message is optional
        # No required fields beyond output_key which is checked below
        pass

    elif isinstance(step, TryCatchStep):
        # Check required fields for TryCatchStep
        if not step.try_steps:
            errors.append("TryCatchStep must have at least one step in try block")

        # Validate try steps
        for nested_step in step.try_steps:
            errors.extend(validate_step(nested_step, existing_output_keys))

        # Validate catch block if present
        if step.catch_block:
            if not step.catch_block.steps:
                errors.append("TryCatchStep catch block must have at least one step")

            # Validate catch steps
            for nested_step in step.catch_block.steps:
                errors.extend(validate_step(nested_step, existing_output_keys))

    else:
        errors.append(f"Unknown step type: {type(step)}")

    # Check output_key uniqueness (if not '_' and exists)
    if hasattr(step, 'output_key') and step.output_key and step.output_key != '_':
        if not step.output_key.strip():
            errors.append("output_key cannot be empty or whitespace")
        elif step.output_key in existing_output_keys:
            errors.append(f"Duplicate output_key '{step.output_key}' found")
        else:
            # Add to existing keys if valid
            existing_output_keys.add(step.output_key)

    return errors


def validate_workflow(workflow: Workflow, initial_data_context: DataContext = None) -> List[str]:
    """
    Validate an entire workflow for structural correctness.

    Args:
        workflow: The Workflow instance to validate
        initial_data_context: Optional initial data context

    Returns:
        List of all error messages found
    """
    all_errors = []

    if not workflow.steps:
        all_errors.append("Workflow must contain at least one step")
        return all_errors

    # Track seen output keys
    seen_output_keys = set()

    # Initialize with keys from initial data context if provided
    if initial_data_context:
        seen_output_keys.update(initial_data_context.get_available_paths())

    # Validate each step
    for i, step in enumerate(workflow.steps):
        step_errors = validate_step(step, seen_output_keys)

        # Add step index to error messages for clarity
        for error in step_errors:
            all_errors.append(f"Step {i + 1}: {error}")

    return all_errors


def validate_data_references(workflow: Workflow, initial_data_context: DataContext = None) -> List[str]:
    """
    Validate that all data references in input_args point to available data paths.

    This is an enhanced validation that checks if data.* references are valid.

    Args:
        workflow: The Workflow instance to validate
        initial_data_context: Optional initial data context

    Returns:
        List of data reference error messages
    """
    errors = []

    # Create a running data context to track available data as we process steps
    running_context = DataContext(
        initial_inputs=initial_data_context.initial_inputs if initial_data_context else {}
    )

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        # Check input_args for data references
        if hasattr(step, 'input_args') and step.input_args:
            for arg_name, arg_value in step.input_args.items():
                if isinstance(arg_value, str) and arg_value.startswith('data.'):
                    # Extract the data path (remove 'data.' prefix)
                    data_path = arg_value[5:]  # Remove 'data.'

                    if not running_context.is_path_available(data_path):
                        errors.append(
                            f"Step {step_num}: input_args['{arg_name}'] references "
                            f"unavailable data path 'data.{data_path}'"
                        )

        # Add this step's output to the running context for future steps
        if step.output_key and step.output_key != '_' and step.parsed_json_output is not None:
            running_context.add_step_output(step.output_key, step.parsed_json_output)

    return errors


def validate_json_outputs(workflow: Workflow) -> List[str]:
    """
    Validate that all user-provided JSON outputs are valid JSON.

    Args:
        workflow: The Workflow instance to validate

    Returns:
        List of JSON validation error messages
    """
    errors = []

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        if hasattr(step, 'user_provided_json_output') and step.user_provided_json_output:
            if step.parsed_json_output is None:
                errors.append(f"Step {step_num}: Invalid JSON in user_provided_json_output")

    return errors


def comprehensive_validate(workflow: Workflow, initial_data_context: DataContext = None) -> List[str]:
    """
    Perform comprehensive validation of a workflow.

    Args:
        workflow: The Workflow instance to validate
        initial_data_context: Optional initial data context

    Returns:
        List of all validation errors found
    """
    all_errors = []

    # Basic structural validation
    all_errors.extend(validate_workflow(workflow, initial_data_context))

    # JSON output validation
    all_errors.extend(validate_json_outputs(workflow))

    # Data reference validation (only if no structural errors)
    if not all_errors:
        all_errors.extend(validate_data_references(workflow, initial_data_context))

    return all_errors


# Example usage and testing
if __name__ == "__main__":
    from core_structures import ActionStep, ScriptStep, Workflow, DataContext

    # Test with a valid workflow
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"id": "12345", "name": "John Doe"}}'
    )

    script_step = ScriptStep(
        code="return {'processed': True}",
        output_key="result",
        input_args={"user_data": "data.user_info.user"},
        user_provided_json_output='{"processed": true}'
    )

    workflow = Workflow(steps=[action_step, script_step])
    initial_context = DataContext({"input_email": "test@example.com"})

    errors = comprehensive_validate(workflow, initial_context)

    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Workflow validation passed!")
