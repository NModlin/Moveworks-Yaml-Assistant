"""
Validation module for Moveworks Compound Action workflows.

This module provides validation functions to ensure workflows are correctly
structured and comply with Moveworks requirements.

Based on Sections 8.1, 8.2, and 11.1 of the Source of Truth Document.
"""

from typing import List, Set, Union, Dict
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


def _infer_workflow_inputs(workflow: Workflow) -> Dict[str, str]:
    """
    Infer workflow input variables from data references in the workflow.

    This function scans all data references in the workflow and identifies
    variables that appear to be workflow inputs (not step outputs).

    Args:
        workflow: The Workflow instance to scan

    Returns:
        Dictionary of inferred input variables with placeholder values
    """
    inferred_inputs = {}
    step_output_keys = set()

    # First pass: collect all step output keys
    for step in workflow.steps:
        if hasattr(step, 'output_key') and step.output_key and step.output_key != '_':
            step_output_keys.add(step.output_key)

    def extract_data_references(obj):
        """Recursively extract data references from nested structures."""
        if isinstance(obj, str) and obj.startswith('data.'):
            # Extract the top-level variable name
            data_path = obj[5:]  # Remove 'data.' prefix
            top_level_var = data_path.split('.')[0]

            # If it's not a step output, it's likely a workflow input
            if top_level_var not in step_output_keys:
                # Use a placeholder value for validation
                inferred_inputs[top_level_var] = f"<inferred_input_{top_level_var}>"
        elif isinstance(obj, dict):
            for value in obj.values():
                extract_data_references(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_data_references(item)

    # Second pass: extract data references from all steps
    for step in workflow.steps:
        if hasattr(step, 'input_args') and step.input_args:
            extract_data_references(step.input_args)

    return inferred_inputs


def validate_data_references(workflow: Workflow, initial_data_context: DataContext = None) -> List[str]:
    """
    Validate that all data references in input_args point to available data paths.

    This is an enhanced validation that checks if data.* references are valid.
    For workflow input variables (like data.input_email), we infer them from usage
    since they may not be explicitly defined in the initial context.

    Args:
        workflow: The Workflow instance to validate
        initial_data_context: Optional initial data context

    Returns:
        List of data reference error messages
    """
    errors = []

    # Create a running data context to track available data as we process steps
    # Start with any provided initial inputs
    initial_inputs = initial_data_context.initial_inputs if initial_data_context else {}

    # Infer workflow input variables from data references in the workflow
    inferred_inputs = _infer_workflow_inputs(workflow)

    # Combine explicit and inferred inputs
    combined_inputs = {**initial_inputs, **inferred_inputs}

    running_context = DataContext(initial_inputs=combined_inputs)

    def validate_data_reference(value: str, context_description: str, step_num: int) -> None:
        """Helper function to validate a single data reference."""
        if isinstance(value, str) and value.startswith('data.'):
            # Extract the data path (remove 'data.' prefix)
            data_path = value[5:]  # Remove 'data.'

            if not running_context.is_path_available(data_path):
                errors.append(
                    f"Step {step_num}: {context_description} references "
                    f"unavailable data path 'data.{data_path}'"
                )

    def validate_step_data_references(step, step_num: int) -> None:
        """Recursively validate data references in a step and its nested steps."""

        # Check input_args for data references
        if hasattr(step, 'input_args') and step.input_args:
            for arg_name, arg_value in step.input_args.items():
                validate_data_reference(arg_value, f"input_args['{arg_name}']", step_num)

        # Check specific step type fields
        if isinstance(step, SwitchStep):
            # Validate conditions in switch cases
            for i, case in enumerate(step.cases):
                validate_data_reference(case.condition, f"switch case {i+1} condition", step_num)
                # Recursively validate nested steps
                for nested_step in case.steps:
                    validate_step_data_references(nested_step, step_num)

            # Validate default case
            if step.default_case:
                for nested_step in step.default_case.steps:
                    validate_step_data_references(nested_step, step_num)

        elif isinstance(step, ForLoopStep):
            # Validate in_source for for loops
            validate_data_reference(step.in_source, "for loop 'in' source", step_num)
            # Recursively validate nested steps
            for nested_step in step.steps:
                validate_step_data_references(nested_step, step_num)

        elif isinstance(step, ParallelStep):
            # Recursively validate nested steps in parallel branches
            for i, branch in enumerate(step.branches):
                for nested_step in branch.steps:
                    validate_step_data_references(nested_step, step_num)

        elif isinstance(step, ReturnStep):
            # Validate output_mapper values
            for key, value in step.output_mapper.items():
                validate_data_reference(value, f"return output_mapper['{key}']", step_num)

        elif isinstance(step, TryCatchStep):
            # Validate try steps
            for nested_step in step.try_steps:
                validate_step_data_references(nested_step, step_num)

            # Validate catch steps
            if step.catch_block:
                for nested_step in step.catch_block.steps:
                    validate_step_data_references(nested_step, step_num)

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        # Validate this step's data references
        validate_step_data_references(step, step_num)

        # Add this step's output to the running context for future steps
        if hasattr(step, 'output_key') and step.output_key and step.output_key != '_':
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output is not None:
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


def validate_action_names(workflow: Workflow) -> List[str]:
    """
    Validate action names for proper format and known actions.

    Args:
        workflow: The Workflow instance to validate

    Returns:
        List of action name validation errors
    """
    errors = []

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        if isinstance(step, ActionStep) and step.action_name:
            # Check for proper mw. prefix for built-in actions
            if step.action_name.startswith('mw.'):
                # Could add validation against known mw actions catalog here
                if len(step.action_name) <= 3:  # Just "mw."
                    errors.append(f"Step {step_num}: Invalid action name '{step.action_name}' - missing action after 'mw.'")

            # Check for invalid characters
            if any(char in step.action_name for char in [' ', '\t', '\n', '\r']):
                errors.append(f"Step {step_num}: Action name '{step.action_name}' contains invalid whitespace characters")

            # Check for empty or very short names
            if len(step.action_name.strip()) < 2:
                errors.append(f"Step {step_num}: Action name '{step.action_name}' is too short")

    return errors


def validate_output_key_format(workflow: Workflow) -> List[str]:
    """
    Validate output key formats and naming conventions.

    Args:
        workflow: The Workflow instance to validate

    Returns:
        List of output key format validation errors
    """
    errors = []

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        if hasattr(step, 'output_key') and step.output_key and step.output_key != '_':
            # Check for valid identifier format
            if not step.output_key.replace('_', '').replace('-', '').isalnum():
                errors.append(f"Step {step_num}: Output key '{step.output_key}' contains invalid characters")

            # Check for reserved words
            reserved_words = ['data', 'input', 'output', 'error', 'requestor', 'mw']
            if step.output_key.lower() in reserved_words:
                errors.append(f"Step {step_num}: Output key '{step.output_key}' is a reserved word")

            # Check for starting with number
            if step.output_key[0].isdigit():
                errors.append(f"Step {step_num}: Output key '{step.output_key}' cannot start with a number")

    return errors


def validate_script_syntax(workflow: Workflow) -> List[str]:
    """
    Perform basic syntax validation on script code.

    APIthon scripts are executed as function bodies, so 'return' statements are valid.

    Args:
        workflow: The Workflow instance to validate

    Returns:
        List of script syntax validation errors
    """
    errors = []

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        if isinstance(step, ScriptStep) and step.code:
            # APIthon scripts are executed as function bodies, so we need to wrap them
            # in a function definition for syntax validation
            wrapped_code = f"def apiton_script():\n"
            # Indent each line of the user's code
            indented_code = '\n'.join(f"    {line}" for line in step.code.split('\n'))
            wrapped_code += indented_code

            syntax_error_found = False
            try:
                compile(wrapped_code, f'<step_{step_num}_script>', 'exec')
            except SyntaxError as e:
                syntax_error_found = True
                # Adjust line numbers in error messages since we wrapped the code
                error_msg = str(e)
                if hasattr(e, 'lineno') and e.lineno and e.lineno > 1:
                    # Subtract 1 from line number to account for the function wrapper
                    adjusted_lineno = e.lineno - 1
                    error_msg = error_msg.replace(f"line {e.lineno}", f"line {adjusted_lineno}")
                errors.append(f"Step {step_num}: Script syntax error - {error_msg}")
            except Exception as e:
                syntax_error_found = True
                errors.append(f"Step {step_num}: Script compilation error - {str(e)}")

            # Only check for return statement if there are no syntax errors
            if not syntax_error_found and 'return' not in step.code:
                errors.append(f"Step {step_num}: Script should contain a 'return' statement")

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

    # Action name validation
    all_errors.extend(validate_action_names(workflow))

    # Output key format validation
    all_errors.extend(validate_output_key_format(workflow))

    # Script syntax validation
    all_errors.extend(validate_script_syntax(workflow))

    # Data reference validation (only if no critical structural errors)
    critical_error_keywords = ['missing required', 'Unknown step type', 'must contain at least one']
    has_critical_errors = any(any(keyword in error for keyword in critical_error_keywords) for error in all_errors)

    if not has_critical_errors:
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
