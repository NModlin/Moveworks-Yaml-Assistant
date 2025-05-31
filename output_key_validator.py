"""
Output Key Validator for Moveworks YAML Assistant.

This module provides comprehensive validation for output_key fields including:
- Mandatory field enforcement based on step type
- Lowercase snake_case naming validation
- Uniqueness validation across workflows
- Data reference generation for downstream steps
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep,
    ParallelStep, ReturnStep, RaiseStep, TryCatchStep
)


@dataclass
class OutputKeyValidationResult:
    """Result of output_key validation with detailed feedback."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    data_reference: Optional[str] = None  # Generated data.{output_key} reference


class OutputKeyValidator:
    """Comprehensive validator for output_key fields in Moveworks workflows."""
    
    def __init__(self):
        # Reserved output_key names that cannot be used
        self.reserved_names = {
            'data', 'input', 'output', 'error', 'requestor', 'mw', 'meta_info', 'user',
            'workflow', 'action', 'script', 'step', 'result', 'response'
        }
        
        # Step types that always require output_key
        self.always_required_types = {
            'ActionStep', 'ScriptStep', 'RaiseStep'
        }
        
        # Step types that conditionally require output_key
        self.conditionally_required_types = {
            'ForLoopStep': 'when used in parallel execution',
            'ParallelStep': 'when containing for loops'
        }
        
        # Snake case pattern for validation - allows single letters and proper snake_case
        self.snake_case_pattern = re.compile(r'^[a-z]([a-z0-9_]*[a-z0-9])?$')
    
    def validate_output_key(self, output_key: str, step_type: str, step_context: Any = None) -> OutputKeyValidationResult:
        """
        Validate a single output_key field.
        
        Args:
            output_key: The output_key value to validate
            step_type: Type of step (e.g., 'ActionStep', 'ScriptStep')
            step_context: Optional step instance for context-specific validation
            
        Returns:
            OutputKeyValidationResult with validation details
        """
        result = OutputKeyValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[]
        )
        
        # Check if field is required for this step type
        if self._is_output_key_required(step_type, step_context):
            if not output_key or not output_key.strip():
                result.errors.append(f"{step_type} requires a non-empty output_key")
                result.is_valid = False
                result.suggestions.append(f"Add a unique output_key like '{self._suggest_output_key(step_type)}'")
                return result
        
        # If empty but not required, that's valid
        if not output_key or not output_key.strip():
            return result
        
        output_key = output_key.strip()
        
        # Validate naming convention (lowercase_snake_case)
        if not self._is_valid_snake_case(output_key):
            result.errors.append(f"output_key '{output_key}' must use lowercase_snake_case format")
            result.is_valid = False
            result.suggestions.append(f"Use '{self._to_snake_case(output_key)}' instead")
        
        # Check for reserved names
        if output_key.lower() in self.reserved_names:
            result.errors.append(f"output_key '{output_key}' is a reserved name")
            result.is_valid = False
            result.suggestions.append(f"Use a different name like '{output_key}_result' or '{output_key}_data'")
        
        # Generate data reference if valid
        if result.is_valid:
            result.data_reference = f"data.{output_key}"
        
        return result
    
    def validate_workflow_output_keys(self, workflow: Workflow) -> List[OutputKeyValidationResult]:
        """
        Validate all output_key fields in a workflow for uniqueness and compliance.
        
        Args:
            workflow: The workflow to validate
            
        Returns:
            List of validation results for each step
        """
        results = []
        output_key_usage = {}  # Track usage for uniqueness validation
        
        for step_index, step in enumerate(workflow.steps):
            step_type = type(step).__name__
            output_key = getattr(step, 'output_key', '')
            
            # Validate individual output_key
            result = self.validate_output_key(output_key, step_type, step)
            
            # Track usage for uniqueness validation
            if output_key and output_key.strip() and output_key != '_':
                clean_key = output_key.strip()
                if clean_key not in output_key_usage:
                    output_key_usage[clean_key] = []
                output_key_usage[clean_key].append((step_index + 1, step_type))
            
            results.append(result)
        
        # Check for duplicate output_keys
        for output_key, usage_list in output_key_usage.items():
            if len(usage_list) > 1:
                for step_num, step_type in usage_list:
                    step_result = results[step_num - 1]
                    step_result.errors.append(f"output_key '{output_key}' is used in multiple steps")
                    step_result.is_valid = False
                    step_result.suggestions.append(f"Use a unique name like '{output_key}_{step_num}'")
        
        return results
    
    def _is_output_key_required(self, step_type: str, step_context: Any = None) -> bool:
        """Check if output_key is required for the given step type and context."""
        if step_type in self.always_required_types:
            return True
        
        if step_type == 'ForLoopStep':
            # Required when used in parallel execution (simplified check for now)
            return True
        
        if step_type == 'ParallelStep' and step_context:
            # Required when containing for loops
            return hasattr(step_context, 'for_loop') and step_context.for_loop is not None
        
        return False
    
    def _is_valid_snake_case(self, name: str) -> bool:
        """Check if a name follows valid snake_case convention."""
        if not name:
            return False
        
        # Must match snake_case pattern
        return bool(self.snake_case_pattern.match(name))
    
    def _to_snake_case(self, name: str) -> str:
        """Convert a name to valid snake_case format."""
        if not name:
            return ""
        
        # Convert camelCase/PascalCase to snake_case
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove invalid characters
        name = re.sub(r'[^a-z0-9_]', '_', name)
        
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'key_' + name
        
        return name or 'output_key'
    
    def _suggest_output_key(self, step_type: str) -> str:
        """Suggest an appropriate output_key name based on step type."""
        suggestions = {
            'ActionStep': 'action_result',
            'ScriptStep': 'script_result',
            'ForLoopStep': 'loop_results',
            'ParallelStep': 'parallel_results',
            'RaiseStep': 'error_info',
            'SwitchStep': 'switch_result',
            'ReturnStep': 'return_value',
            'TryCatchStep': 'try_result'
        }
        return suggestions.get(step_type, 'step_result')
    
    def generate_data_reference_suggestions(self, workflow: Workflow) -> Dict[str, List[str]]:
        """
        Generate data reference suggestions for each step based on previous steps' output_keys.
        
        Args:
            workflow: The workflow to analyze
            
        Returns:
            Dictionary mapping step index to list of available data references
        """
        suggestions = {}
        available_keys = ['input_email', 'input_data']  # Common initial inputs
        
        for step_index, step in enumerate(workflow.steps):
            # Add current available keys to suggestions
            suggestions[step_index] = [f"data.{key}" for key in available_keys]
            
            # Add this step's output_key to available keys for next steps
            if hasattr(step, 'output_key') and step.output_key and step.output_key.strip() and step.output_key != '_':
                available_keys.append(step.output_key.strip())
        
        return suggestions


# Global validator instance
output_key_validator = OutputKeyValidator()
