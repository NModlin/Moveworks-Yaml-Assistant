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
            'ParallelStep': [],  # Varies by mode
            'ReturnStep': [],  # output_mapper is optional
            'RaiseStep': [],  # All fields are optional
            'TryCatchStep': ['try_steps']
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
        """Validate APIthon script compliance using enhanced validator."""
        if step.code and step.code.strip():
            # Use enhanced APIthon validator
            apiton_result = enhanced_apiton_validator.comprehensive_validate(step)
            
            if not apiton_result.is_valid:
                for error in apiton_result.errors:
                    result.apiton_errors.append(f"Step {step_num}: {error}")
            
            # Add warnings and suggestions
            for warning in apiton_result.warnings:
                result.warnings.append(f"Step {step_num}: {warning}")
            
            for suggestion in apiton_result.suggestions:
                result.suggestions.append(f"Step {step_num}: {suggestion}")
    
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


# Global instance for easy access
compliance_validator = ComplianceValidator()
