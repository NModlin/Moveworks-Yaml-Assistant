"""
Enhanced Validator with Fix Suggestions for the Moveworks YAML Assistant.

This module extends the existing validator to provide actionable fix suggestions
for common validation errors.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, RaiseStep, TryCatchStep
)
from validator import comprehensive_validate


@dataclass
class ValidationError:
    """Enhanced validation error with fix suggestions."""
    message: str
    step_number: Optional[int] = None
    severity: str = "error"  # error, warning, info
    fix_suggestions: List[str] = None
    quick_fixes: List[Dict[str, Any]] = None  # Automated fixes

    def __post_init__(self):
        if self.fix_suggestions is None:
            self.fix_suggestions = []
        if self.quick_fixes is None:
            self.quick_fixes = []


class EnhancedValidator:
    """Enhanced validator with fix suggestions and quick fixes."""

    def __init__(self):
        self.common_fixes = self._load_common_fixes()

    def _load_common_fixes(self) -> Dict[str, Dict[str, Any]]:
        """Load common fix patterns."""
        return {
            "missing_action_name": {
                "suggestions": [
                    "Add an action name (e.g., 'mw.get_user_by_email')",
                    "Use the built-in actions catalog for valid action names",
                    "Check the Moveworks documentation for available actions"
                ],
                "quick_fix": {
                    "type": "set_field",
                    "field": "action_name",
                    "value": "mw.get_user_by_email"
                }
            },
            "missing_output_key": {
                "suggestions": [
                    "Add a unique output key (e.g., 'user_info', 'api_result')",
                    "Use descriptive names that indicate the step's purpose",
                    "Avoid reserved words like 'data', 'input', 'output'"
                ],
                "quick_fix": {
                    "type": "set_field",
                    "field": "output_key",
                    "value": "step_output"
                }
            },
            "missing_script_code": {
                "suggestions": [
                    "Add APIthon script code to process data",
                    "Include a 'return' statement to output results",
                    "Use 'data.previous_step_output' to access previous step data"
                ],
                "quick_fix": {
                    "type": "set_field",
                    "field": "code",
                    "value": "# Process data here\nresult = {'processed': True}\nreturn result"
                }
            },
            "duplicate_output_key": {
                "suggestions": [
                    "Change the output key to a unique value",
                    "Use descriptive names that reflect the step's purpose",
                    "Consider adding a suffix like '_v2' or '_processed'"
                ],
                "quick_fix": {
                    "type": "append_suffix",
                    "field": "output_key",
                    "suffix": "_v2"
                }
            },
            "invalid_data_reference": {
                "suggestions": [
                    "Check that the referenced step exists and comes before this step",
                    "Verify the JSON structure of the referenced step's output",
                    "Use the JSON path selector to build valid references"
                ]
            },
            "invalid_json_output": {
                "suggestions": [
                    "Fix JSON syntax errors (missing quotes, commas, brackets)",
                    "Use a JSON validator to check the format",
                    "Provide realistic example data that matches expected output"
                ],
                "quick_fix": {
                    "type": "set_field",
                    "field": "user_provided_json_output",
                    "value": '{"result": "example_value"}'
                }
            },
            "script_syntax_error": {
                "suggestions": [
                    "Fix Python syntax errors (indentation, missing colons, etc.)",
                    "Check for proper variable names and function calls",
                    "Test your script logic before adding to the workflow"
                ]
            },
            "missing_return_statement": {
                "suggestions": [
                    "Add a 'return' statement to output results from the script",
                    "Return a dictionary with the processed data",
                    "Example: return {'result': processed_data}"
                ],
                "quick_fix": {
                    "type": "append_code",
                    "field": "code",
                    "value": "\nreturn {'result': 'processed'}"
                }
            },
            "missing_switch_cases": {
                "suggestions": [
                    "Add at least one case to the switch statement",
                    "Include conditions that evaluate to boolean expressions",
                    "Consider adding a default case for unmatched conditions"
                ]
            },
            "invalid_switch_condition": {
                "suggestions": [
                    "Ensure switch conditions are valid boolean expressions",
                    "Use data references like 'data.step_output.field == value'",
                    "Check for proper syntax and data path validity"
                ]
            },
            "missing_for_loop_fields": {
                "suggestions": [
                    "Specify the 'each' variable name for iteration",
                    "Set the 'in' field to reference an array data path",
                    "Provide an 'output_key' to store loop results"
                ]
            },
            "invalid_parallel_configuration": {
                "suggestions": [
                    "Choose either 'branches' or 'for' mode for parallel execution",
                    "For branches: add multiple branch configurations",
                    "For parallel loops: configure the for loop parameters"
                ]
            },
            "missing_try_catch_blocks": {
                "suggestions": [
                    "Add steps to the 'try' block",
                    "Configure a 'catch' block for error handling",
                    "Specify 'on_status_code' for targeted error handling"
                ]
            },
            "invalid_data_reference_meta_info": {
                "suggestions": [
                    "Use 'meta_info.user.attribute' for user context data",
                    "Available user attributes: first_name, last_name, email_addr, department",
                    "Example: meta_info.user.first_name for the user's first name"
                ]
            },
            "undefined_input_variable": {
                "suggestions": [
                    "Define the input variable in the Input Variables section",
                    "Check the variable name for typos (must be lowercase_snake_case)",
                    "Ensure the variable is defined before referencing it in steps"
                ],
                "quick_fix": {
                    "type": "add_input_variable",
                    "variable_name": "",
                    "data_type": "string"
                }
            },
            "invalid_input_variable_reference": {
                "suggestions": [
                    "Use 'data.{variable_name}' format to reference input variables",
                    "Check that the variable name matches exactly (case-sensitive)",
                    "Verify the variable is defined in the Input Variables section"
                ]
            }
        }

    def validate_with_suggestions(self, workflow: Workflow) -> List[ValidationError]:
        """Validate workflow and provide fix suggestions."""
        # Get basic validation errors
        basic_errors = comprehensive_validate(workflow)

        # Convert to enhanced errors with suggestions
        enhanced_errors = []

        for error in basic_errors:
            enhanced_error = self._enhance_error(error, workflow)
            enhanced_errors.append(enhanced_error)

        # Add additional checks with suggestions
        enhanced_errors.extend(self._check_best_practices(workflow))
        enhanced_errors.extend(self._check_input_variable_references(workflow))

        return enhanced_errors

    def _enhance_error(self, error_message: str, workflow: Workflow) -> ValidationError:
        """Enhance a basic error message with fix suggestions."""
        # Extract step number if present
        step_number = None
        if error_message.startswith("Step "):
            try:
                step_number = int(error_message.split(":")[0].split(" ")[1])
            except (IndexError, ValueError):
                pass

        # Determine error type and get suggestions
        error_type = self._classify_error(error_message)
        fix_info = self.common_fixes.get(error_type, {})

        suggestions = fix_info.get("suggestions", [])
        quick_fix = fix_info.get("quick_fix")
        quick_fixes = [quick_fix] if quick_fix else []

        return ValidationError(
            message=error_message,
            step_number=step_number,
            severity="error",
            fix_suggestions=suggestions,
            quick_fixes=quick_fixes
        )

    def _classify_error(self, error_message: str) -> str:
        """Classify error message to determine fix type."""
        error_lower = error_message.lower()

        if "missing required 'action_name'" in error_lower:
            return "missing_action_name"
        elif "missing required 'output_key'" in error_lower:
            return "missing_output_key"
        elif "missing required 'code'" in error_lower:
            return "missing_script_code"
        elif "duplicate output_key" in error_lower:
            return "duplicate_output_key"
        elif "references unavailable data path" in error_lower:
            return "invalid_data_reference"
        elif "invalid json" in error_lower:
            return "invalid_json_output"
        elif "syntax error" in error_lower:
            return "script_syntax_error"
        elif "should contain a 'return' statement" in error_lower:
            return "missing_return_statement"
        else:
            return "unknown"

    def _check_best_practices(self, workflow: Workflow) -> List[ValidationError]:
        """Check for best practice violations and suggest improvements."""
        warnings = []

        for i, step in enumerate(workflow.steps):
            step_num = i + 1

            # Check for missing descriptions
            if not getattr(step, 'description', None):
                warnings.append(ValidationError(
                    message=f"Step {step_num}: Consider adding a description for better documentation",
                    step_number=step_num,
                    severity="info",
                    fix_suggestions=[
                        "Add a description to explain what this step does",
                        "Use clear, concise language that helps other users understand the purpose",
                        "Example: 'Look up user information by email address'"
                    ]
                ))

            # Check switch statement best practices
            if isinstance(step, SwitchStep):
                if not step.cases:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Switch statement has no cases - consider adding conditions",
                        step_number=step_num,
                        severity="warning",
                        fix_suggestions=[
                            "Add at least one case with a condition and steps",
                            "Consider adding a default case for unmatched conditions",
                            "Example: condition: 'data.user.status == \"active\"'"
                        ]
                    ))

                if not step.default_case and len(step.cases) < 2:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Consider adding a default case or more conditions to switch",
                        step_number=step_num,
                        severity="info",
                        fix_suggestions=[
                            "Add a default case to handle unmatched conditions",
                            "Add more cases to cover different scenarios",
                            "Default cases provide fallback behavior"
                        ]
                    ))

            # Check for loop best practices
            if isinstance(step, ForLoopStep):
                if not step.each or not step.in_source:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: For loop missing required fields (each, in)",
                        step_number=step_num,
                        severity="error",
                        fix_suggestions=[
                            "Set 'each' to the variable name for current item",
                            "Set 'in' to the data path of the array to iterate",
                            "Example: each='user', in='data.users'"
                        ]
                    ))

            # Check parallel step configuration
            if isinstance(step, ParallelStep):
                if not step.branches and not step.for_loop:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Parallel step has no branches or for loop configuration",
                        step_number=step_num,
                        severity="error",
                        fix_suggestions=[
                            "Add branches for concurrent execution of different steps",
                            "Or configure a for loop for parallel iteration",
                            "Choose one mode: branches OR for loop"
                        ]
                    ))

            # Check try-catch configuration
            if isinstance(step, TryCatchStep):
                if not step.try_steps:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Try-catch block has no steps in try block",
                        step_number=step_num,
                        severity="error",
                        fix_suggestions=[
                            "Add steps to the try block that might fail",
                            "Include actions or scripts that could throw errors",
                            "The try block should contain the risky operations"
                        ]
                    ))

                if not step.catch_block:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Try block without catch - consider adding error handling",
                        step_number=step_num,
                        severity="warning",
                        fix_suggestions=[
                            "Add a catch block to handle potential errors",
                            "Specify on_status_code for targeted error handling",
                            "Include recovery steps in the catch block"
                        ]
                    ))

            # Check for missing JSON output
            if isinstance(step, (ActionStep, ScriptStep)):
                if not getattr(step, 'user_provided_json_output', None):
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Missing JSON output example - this will limit data mapping capabilities",
                        step_number=step_num,
                        severity="warning",
                        fix_suggestions=[
                            "Provide example JSON output to enable data mapping",
                            "Use realistic data that matches what the action/script will return",
                            "This helps other users understand the available data structure"
                        ],
                        quick_fixes=[{
                            "type": "set_field",
                            "field": "user_provided_json_output",
                            "value": '{"result": "example_output"}'
                        }]
                    ))

            # Check for overly generic output keys
            if hasattr(step, 'output_key') and step.output_key:
                generic_keys = ['result', 'output', 'data', 'response']
                if step.output_key.lower() in generic_keys:
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Output key '{step.output_key}' is generic - consider using a more descriptive name",
                        step_number=step_num,
                        severity="info",
                        fix_suggestions=[
                            "Use descriptive output keys that indicate the data content",
                            "Examples: 'user_info', 'ticket_details', 'processed_data'",
                            "This makes data references clearer in subsequent steps"
                        ]
                    ))

            # Check for long script code without comments
            if isinstance(step, ScriptStep) and step.code:
                lines = step.code.split('\n')
                if len(lines) > 10 and not any(line.strip().startswith('#') for line in lines):
                    warnings.append(ValidationError(
                        message=f"Step {step_num}: Long script without comments - consider adding explanatory comments",
                        step_number=step_num,
                        severity="info",
                        fix_suggestions=[
                            "Add comments to explain complex logic",
                            "Use # to add single-line comments",
                            "Document any assumptions or business rules"
                        ]
                    ))

        return warnings

    def _check_input_variable_references(self, workflow: Workflow) -> List[ValidationError]:
        """Check for undefined input variable references."""
        errors = []

        # Get defined input variable names
        defined_variables = set()
        if hasattr(workflow, 'input_variables') and workflow.input_variables:
            defined_variables = {var.name for var in workflow.input_variables}

        # Check each step for input variable references
        for i, step in enumerate(workflow.steps):
            step_num = i + 1

            # Check input_args for data.{variable_name} references
            if hasattr(step, 'input_args') and step.input_args:
                for key, value in step.input_args.items():
                    if isinstance(value, str) and value.startswith('data.'):
                        # Extract variable name from data.{variable_name}
                        parts = value.split('.')
                        if len(parts) >= 2:
                            var_name = parts[1]
                            # Check if this looks like an input variable reference
                            # (no further dots, suggesting it's not a step output reference)
                            if len(parts) == 2 and var_name not in defined_variables:
                                # Check if it might be a step output reference
                                is_step_output = any(
                                    hasattr(s, 'output_key') and s.output_key == var_name
                                    for j, s in enumerate(workflow.steps) if j < i
                                )

                                if not is_step_output:
                                    errors.append(ValidationError(
                                        message=f"Step {step_num}: References undefined input variable '{var_name}' in {key}",
                                        step_number=step_num,
                                        severity="error",
                                        fix_suggestions=[
                                            f"Define input variable '{var_name}' in the Input Variables section",
                                            f"Check if '{var_name}' is a typo of an existing variable",
                                            f"Use the correct format: data.{var_name}"
                                        ]
                                    ))

            # Check script code for input variable references
            if isinstance(step, ScriptStep) and step.code:
                import re
                # Find data.{variable_name} patterns in script code
                data_refs = re.findall(r'data\.([a-zA-Z_][a-zA-Z0-9_]*)', step.code)
                for var_name in data_refs:
                    if var_name not in defined_variables:
                        # Check if it's a step output reference
                        is_step_output = any(
                            hasattr(s, 'output_key') and s.output_key == var_name
                            for j, s in enumerate(workflow.steps) if j < i
                        )

                        if not is_step_output:
                            errors.append(ValidationError(
                                message=f"Step {step_num}: Script references undefined input variable '{var_name}'",
                                step_number=step_num,
                                severity="error",
                                fix_suggestions=[
                                    f"Define input variable '{var_name}' in the Input Variables section",
                                    f"Check if '{var_name}' is a typo of an existing variable",
                                    "Verify the variable name follows lowercase_snake_case convention"
                                ]
                            ))

        return errors

    def apply_quick_fix(self, workflow: Workflow, error: ValidationError) -> bool:
        """Apply a quick fix to the workflow."""
        if not error.quick_fixes or not error.step_number:
            return False

        try:
            step_index = error.step_number - 1
            if step_index < 0 or step_index >= len(workflow.steps):
                return False

            step = workflow.steps[step_index]
            quick_fix = error.quick_fixes[0]  # Apply first available fix

            if quick_fix["type"] == "set_field":
                setattr(step, quick_fix["field"], quick_fix["value"])
                return True

            elif quick_fix["type"] == "append_suffix":
                current_value = getattr(step, quick_fix["field"], "")
                new_value = current_value + quick_fix["suffix"]
                setattr(step, quick_fix["field"], new_value)
                return True

            elif quick_fix["type"] == "append_code":
                current_code = getattr(step, quick_fix["field"], "")
                new_code = current_code + quick_fix["value"]
                setattr(step, quick_fix["field"], new_code)
                return True

        except Exception as e:
            print(f"Error applying quick fix: {e}")
            return False

        return False

    def get_validation_summary(self, errors: List[ValidationError]) -> Dict[str, Any]:
        """Get a summary of validation results."""
        error_count = len([e for e in errors if e.severity == "error"])
        warning_count = len([e for e in errors if e.severity == "warning"])
        info_count = len([e for e in errors if e.severity == "info"])

        fixable_count = len([e for e in errors if e.quick_fixes])

        return {
            "total_issues": len(errors),
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "fixable": fixable_count,
            "has_critical_errors": error_count > 0,
            "ready_for_export": error_count == 0
        }


# Global enhanced validator instance
enhanced_validator = EnhancedValidator()
