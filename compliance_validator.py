"""
Compliance Validator for Moveworks YAML Assistant.

This module provides comprehensive compliance validation including mandatory field
enforcement, field naming standardization, and enhanced APIthon validation.
"""

from typing import List, Dict, Any, Set
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, RaiseStep, TryCatchStep
)
from enhanced_apiton_validator import enhanced_apiton_validator


class ComplianceValidationResult:
    """Result of compliance validation with detailed feedback."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.mandatory_field_errors = []
        self.field_naming_errors = []
        self.apiton_errors = []


class ComplianceValidator:
    """Enhanced compliance validator for Moveworks YAML Assistant."""
    
    def __init__(self):
        self.mandatory_fields = {
            'ActionStep': ['action_name', 'output_key'],
            'ScriptStep': ['code', 'output_key'],
            'SwitchStep': ['cases'],
            'ForLoopStep': ['each', 'in_source', 'output_key'],
            'ParallelStep': [],  # Varies by mode - output_key required when containing for loops
            'ReturnStep': [],  # output_mapper is optional
            'RaiseStep': ['output_key'],  # output_key is always required for error tracking
            'TryCatchStep': ['try_steps']
        }

        # Enhanced output_key requirements based on context
        self.output_key_requirements = {
            'ActionStep': 'always_required',
            'ScriptStep': 'always_required',
            'ForLoopStep': 'required_in_parallel',  # Required when used within parallel expressions
            'ParallelStep': 'required_with_for_loops',  # Required when containing for loops
            'RaiseStep': 'always_required',  # Always required for error information
            'SwitchStep': 'optional',
            'ReturnStep': 'optional',
            'TryCatchStep': 'optional'
        }

        # Enhanced action_name requirements and validation rules
        self.action_name_requirements = {
            'ActionStep': 'always_required',  # ActionStep always requires action_name
            'ScriptStep': 'not_applicable',   # ScriptStep doesn't use action_name
            'ForLoopStep': 'not_applicable',
            'ParallelStep': 'not_applicable',
            'RaiseStep': 'not_applicable',
            'SwitchStep': 'not_applicable',
            'ReturnStep': 'not_applicable',
            'TryCatchStep': 'not_applicable'
        }
        
        self.reserved_output_keys = {
            'data', 'input', 'output', 'error', 'requestor', 'mw', 'meta_info', 'user'
        }
    
    def validate_workflow_compliance(self, workflow: Workflow, action_name: str = None) -> ComplianceValidationResult:
        """
        Perform comprehensive compliance validation on a workflow.
        
        Args:
            workflow: The Workflow instance to validate
            action_name: Optional action name for compound action validation
            
        Returns:
            ComplianceValidationResult with detailed validation feedback
        """
        result = ComplianceValidationResult()
        
        # Validate compound action structure
        self._validate_compound_action_structure(workflow, action_name, result)
        
        # Validate each step
        for i, step in enumerate(workflow.steps):
            step_num = i + 1
            self._validate_step_compliance(step, step_num, result)

        # Validate output_key uniqueness across the entire workflow
        self.validate_output_key_uniqueness(workflow, result)

        # Set overall validity
        result.is_valid = (
            len(result.errors) == 0 and
            len(result.mandatory_field_errors) == 0 and
            len(result.field_naming_errors) == 0 and
            len(result.apiton_errors) == 0
        )
        
        return result
    
    def _validate_compound_action_structure(self, workflow: Workflow, action_name: str, result: ComplianceValidationResult):
        """Validate compound action structure compliance."""
        # Validate action_name is provided and not empty
        if not action_name or not action_name.strip():
            result.mandatory_field_errors.append("Compound action must have a non-empty action_name")
        
        # Validate steps array exists and is not empty
        if not workflow.steps:
            result.mandatory_field_errors.append("Compound action must contain at least one step in the steps array")
    
    def _validate_step_compliance(self, step: Any, step_num: int, result: ComplianceValidationResult):
        """Validate individual step compliance."""
        step_type = type(step).__name__
        
        # Validate mandatory fields
        self._validate_mandatory_fields(step, step_type, step_num, result)
        
        # Validate field naming
        self._validate_field_naming(step, step_type, step_num, result)
        
        # Validate APIthon scripts
        if isinstance(step, ScriptStep):
            self._validate_apiton_compliance(step, step_num, result)
    
    def _validate_mandatory_fields(self, step: Any, step_type: str, step_num: int, result: ComplianceValidationResult):
        """Validate that all mandatory fields are present and non-empty."""
        mandatory_fields = self.mandatory_fields.get(step_type, [])

        # Enhanced output_key validation based on context
        self._validate_output_key_requirements(step, step_type, step_num, result)

        # Enhanced action_name validation based on context
        self._validate_action_name_requirements(step, step_type, step_num, result)
        
        for field_name in mandatory_fields:
            if not hasattr(step, field_name):
                result.mandatory_field_errors.append(
                    f"Step {step_num} ({step_type}): Missing mandatory field '{field_name}'"
                )
            else:
                field_value = getattr(step, field_name)
                if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
                    result.mandatory_field_errors.append(
                        f"Step {step_num} ({step_type}): Mandatory field '{field_name}' cannot be empty"
                    )
                elif isinstance(field_value, list) and len(field_value) == 0:
                    result.mandatory_field_errors.append(
                        f"Step {step_num} ({step_type}): Mandatory field '{field_name}' cannot be an empty list"
                    )
        
        # Special validation for specific step types
        if isinstance(step, ParallelStep):
            if not step.branches and not step.for_loop:
                result.mandatory_field_errors.append(
                    f"Step {step_num} (ParallelStep): Must have either 'branches' or 'for_loop' configuration"
                )
        
        if isinstance(step, SwitchStep):
            if step.cases:
                for i, case in enumerate(step.cases):
                    if not case.condition or not case.condition.strip():
                        result.mandatory_field_errors.append(
                            f"Step {step_num} (SwitchStep): Case {i+1} must have a non-empty condition"
                        )
                    if not case.steps:
                        result.mandatory_field_errors.append(
                            f"Step {step_num} (SwitchStep): Case {i+1} must have at least one step"
                        )
    
    def _validate_field_naming(self, step: Any, step_type: str, step_num: int, result: ComplianceValidationResult):
        """Validate field naming follows lowercase_snake_case convention."""
        # Check output_key naming
        if hasattr(step, 'output_key') and step.output_key:
            output_key = step.output_key
            
            # Check for reserved names
            if output_key.lower() in self.reserved_output_keys:
                result.field_naming_errors.append(
                    f"Step {step_num} ({step_type}): output_key '{output_key}' is a reserved name"
                )
            
            # Check naming convention
            if not self._is_valid_snake_case(output_key):
                result.field_naming_errors.append(
                    f"Step {step_num} ({step_type}): output_key '{output_key}' should use lowercase_snake_case format"
                )
        
        # Check input_args keys
        if hasattr(step, 'input_args') and step.input_args:
            if isinstance(step.input_args, dict):
                for key in step.input_args.keys():
                    if not self._is_valid_snake_case(key):
                        result.field_naming_errors.append(
                            f"Step {step_num} ({step_type}): input_args key '{key}' should use lowercase_snake_case format"
                        )
    
    def _validate_apiton_compliance(self, step: ScriptStep, step_num: int, result: ComplianceValidationResult):
        """Validate APIthon script compliance using enhanced validator with comprehensive field validation."""
        # Validate code field presence and naming consistency
        self._validate_script_code_field(step, step_num, result)

        if step.code and step.code.strip():
            # Use enhanced APIthon validator
            apiton_result = enhanced_apiton_validator.comprehensive_validate(step)

            if not apiton_result.is_valid:
                for error in apiton_result.errors:
                    if hasattr(error, 'message'):
                        # New ValidationError objects with detailed information
                        error_msg = f"Step {step_num}: {error.message}"
                        if error.error_type == "import_statement":
                            error_msg += f" (Line {error.line_number})" if error.line_number else ""
                            if error.remediation:
                                error_msg += f" - {error.remediation}"
                        result.apiton_errors.append(error_msg)
                    else:
                        # Backward compatibility for string errors
                        result.apiton_errors.append(f"Step {step_num}: {error}")

            # Add warnings and suggestions with enhanced import-specific messaging
            for warning in apiton_result.warnings:
                if hasattr(warning, 'message'):
                    result.warnings.append(f"Step {step_num}: {warning.message}")
                else:
                    result.warnings.append(f"Step {step_num}: {warning}")

            for suggestion in apiton_result.suggestions:
                result.suggestions.append(f"Step {step_num}: {suggestion}")

            # Add import-specific educational context if violations found
            if apiton_result.import_violations:
                result.suggestions.append(
                    f"Step {step_num}: APIthon runs in a sandboxed environment. "
                    f"Use built-in Python functions (len, str, int, dict, list) or data.* references instead of imports."
                )
                result.suggestions.append(
                    f"Step {step_num}: For HTTP requests, use action steps like 'mw.http_request' instead of importing requests."
                )

            # Validate 4096-byte limit with specific error messaging
            self._validate_apiton_byte_limits(step, step_num, result)

            # Validate private method detection
            self._validate_apiton_private_methods(step, step_num, result)

            # Validate return statement logic
            self._validate_apiton_return_logic(step, step_num, result, apiton_result)
        else:
            # Code field is empty - this is a mandatory field error
            result.mandatory_field_errors.append(
                f"Step {step_num} (ScriptStep): 'code' field cannot be empty"
            )
    
    def _is_valid_snake_case(self, name: str) -> bool:
        """Check if a name follows valid snake_case convention."""
        if not name:
            return False
        
        # Must start with letter or underscore
        if not (name[0].isalpha() or name[0] == '_'):
            return False
        
        # Must contain only letters, numbers, and underscores
        if not all(c.isalnum() or c == '_' for c in name):
            return False
        
        # Should not start with underscore (private convention)
        if name.startswith('_'):
            return False
        
        # Should be lowercase
        if name != name.lower():
            return False
        
        return True

    def _validate_output_key_requirements(self, step: Any, step_type: str, step_num: int, result: ComplianceValidationResult):
        """Validate output_key requirements based on step type and context."""
        requirement = self.output_key_requirements.get(step_type, 'optional')

        if requirement == 'always_required':
            # ActionStep, ScriptStep, RaiseStep always require output_key
            if not hasattr(step, 'output_key') or not step.output_key or not step.output_key.strip():
                result.mandatory_field_errors.append(
                    f"Step {step_num} ({step_type}): output_key is required for {step_type}"
                )

        elif requirement == 'required_in_parallel':
            # ForLoopStep requires output_key when used within parallel expressions
            # This would need workflow context to determine - for now treat as always required
            if not hasattr(step, 'output_key') or not step.output_key or not step.output_key.strip():
                result.mandatory_field_errors.append(
                    f"Step {step_num} ({step_type}): output_key is required for {step_type}"
                )

        elif requirement == 'required_with_for_loops':
            # ParallelStep requires output_key when containing for loops
            if hasattr(step, 'for_loop') and step.for_loop:
                if not hasattr(step, 'output_key') or not step.output_key or not step.output_key.strip():
                    result.mandatory_field_errors.append(
                        f"Step {step_num} ({step_type}): output_key is required when ParallelStep contains for loops"
                    )

    def validate_output_key_uniqueness(self, workflow: Any, result: ComplianceValidationResult):
        """Validate that all output_key values are unique within the workflow."""
        output_keys = {}  # Maps output_key -> list of (step_num, step_type)

        for step_num, step in enumerate(workflow.steps, 1):
            if hasattr(step, 'output_key') and step.output_key and step.output_key.strip() and step.output_key != '_':
                output_key = step.output_key.strip()
                step_type = type(step).__name__

                if output_key not in output_keys:
                    output_keys[output_key] = []
                output_keys[output_key].append((step_num, step_type))

        # Check for duplicates
        for output_key, step_list in output_keys.items():
            if len(step_list) > 1:
                step_descriptions = [f"Step {num} ({stype})" for num, stype in step_list]
                result.mandatory_field_errors.append(
                    f"Duplicate output_key '{output_key}' found in: {', '.join(step_descriptions)}"
                )

    def _validate_action_name_requirements(self, step: Any, step_type: str, step_num: int, result: ComplianceValidationResult):
        """Validate action_name requirements based on step type and context."""
        requirement = self.action_name_requirements.get(step_type, 'not_applicable')

        if requirement == 'always_required':
            # ActionStep always requires action_name
            if not hasattr(step, 'action_name') or not step.action_name or not step.action_name.strip():
                result.mandatory_field_errors.append(
                    f"Step {step_num} ({step_type}): action_name is required for {step_type}"
                )
            else:
                # Validate action_name format and content
                self._validate_action_name_format(step.action_name, step_type, step_num, result)

    def _validate_action_name_format(self, action_name: str, step_type: str, step_num: int, result: ComplianceValidationResult):
        """Validate action_name format and naming conventions."""
        action_name = action_name.strip()

        # Check for invalid characters (whitespace, special chars except dots and underscores)
        import re
        if re.search(r'[^\w\.]', action_name):
            result.field_naming_errors.append(
                f"Step {step_num} ({step_type}): action_name '{action_name}' contains invalid characters. Use only letters, numbers, dots, and underscores."
            )

        # Check minimum length
        if len(action_name) < 2:
            result.field_naming_errors.append(
                f"Step {step_num} ({step_type}): action_name '{action_name}' is too short. Minimum 2 characters required."
            )

        # Check for proper mw. prefix format for built-in actions
        if action_name.startswith('mw.'):
            if len(action_name) <= 3:  # Just "mw."
                result.field_naming_errors.append(
                    f"Step {step_num} ({step_type}): action_name '{action_name}' is incomplete. Specify the action after 'mw.'"
                )

        # Validate against MW_ACTIONS_CATALOG if available
        self._validate_action_name_catalog(action_name, step_type, step_num, result)

    def _validate_action_name_catalog(self, action_name: str, step_type: str, step_num: int, result: ComplianceValidationResult):
        """Validate action_name against Moveworks Actions Catalog."""
        try:
            from mw_actions_catalog import MW_ACTIONS_CATALOG

            # Get list of known action names
            known_actions = [action.action_name for action in MW_ACTIONS_CATALOG]

            # Check if it's a known action
            if action_name not in known_actions:
                # Check for similar actions (typo detection)
                similar_actions = [action for action in known_actions if action_name.lower() in action.lower()]

                if similar_actions:
                    suggestions = similar_actions[:3]  # Top 3 suggestions
                    result.warnings.append(
                        f"Step {step_num} ({step_type}): action_name '{action_name}' not found in catalog. Did you mean: {', '.join(suggestions)}?"
                    )
                else:
                    result.warnings.append(
                        f"Step {step_num} ({step_type}): action_name '{action_name}' not found in Moveworks catalog. Verify the action name is correct."
                    )
        except ImportError:
            # MW_ACTIONS_CATALOG not available, skip catalog validation
            pass

    def _validate_script_code_field(self, step: ScriptStep, step_num: int, result: ComplianceValidationResult):
        """Validate that ScriptStep uses consistent 'code' field naming."""
        # Check if the step has the required 'code' attribute
        if not hasattr(step, 'code'):
            result.mandatory_field_errors.append(
                f"Step {step_num} (ScriptStep): Missing required 'code' field"
            )

        # Check for potential field naming inconsistencies (if other attributes exist)
        inconsistent_fields = []
        for attr_name in ['script', 'apiton_code', 'script_code', 'python_code']:
            if hasattr(step, attr_name):
                inconsistent_fields.append(attr_name)

        if inconsistent_fields:
            result.field_naming_errors.append(
                f"Step {step_num} (ScriptStep): Use 'code' field instead of: {', '.join(inconsistent_fields)}"
            )

    def _validate_apiton_byte_limits(self, step: ScriptStep, step_num: int, result: ComplianceValidationResult):
        """Validate APIthon script byte limits with specific error messaging."""
        if step.code:
            code_bytes = len(step.code.encode('utf-8'))

            if code_bytes > 4096:
                result.apiton_errors.append(
                    f"Step {step_num}: APIthon script exceeds 4096-byte limit ({code_bytes} bytes). "
                    f"Consider breaking into smaller scripts or optimizing code length."
                )
            elif code_bytes > 3276:  # 80% of limit
                result.warnings.append(
                    f"Step {step_num}: APIthon script approaching byte limit ({code_bytes}/4096 bytes). "
                    f"Consider optimizing for better performance."
                )

    def _validate_apiton_private_methods(self, step: ScriptStep, step_num: int, result: ComplianceValidationResult):
        """Validate that APIthon scripts don't use private methods or identifiers."""
        if step.code:
            import re

            # Find identifiers starting with underscore (private convention)
            private_pattern = r'\b_[a-zA-Z_][a-zA-Z0-9_]*\b'
            private_matches = re.findall(private_pattern, step.code)

            if private_matches:
                unique_private = list(set(private_matches))
                result.apiton_errors.append(
                    f"Step {step_num}: Private identifiers not allowed in APIthon: {', '.join(unique_private)}. "
                    f"Use public identifiers without leading underscores."
                )

    def _validate_apiton_return_logic(self, step: ScriptStep, step_num: int, result: ComplianceValidationResult, apiton_result):
        """Validate return statement logic with educational guidance."""
        if hasattr(apiton_result, 'return_analysis') and apiton_result.return_analysis:
            return_analysis = apiton_result.return_analysis

            # Check for missing return statements when last line is assignment
            if (not return_analysis.get('has_explicit_return') and
                return_analysis.get('last_statement_type') == 'Assign'):
                result.suggestions.append(
                    f"Step {step_num}: Consider adding 'return' statement. "
                    f"The last line assigns to a variable but doesn't return it. "
                    f"The output_key will receive None instead of your variable's value."
                )

            # Validate reserved output_key handling
            if step.output_key in ['result', 'results']:
                if step.output_key == 'result':
                    result.suggestions.append(
                        f"Step {step_num}: output_key 'result' suggests citation format. "
                        f"Consider returning a dictionary with citation fields like 'title', 'url', 'snippet'."
                    )
                elif step.output_key == 'results':
                    result.suggestions.append(
                        f"Step {step_num}: output_key 'results' suggests citation list format. "
                        f"Consider returning a list of citation dictionaries."
                    )


# Global instance for easy access
compliance_validator = ComplianceValidator()
