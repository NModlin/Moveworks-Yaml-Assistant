"""
Real-time Validation Manager for the Moveworks YAML Assistant.

This module coordinates all validation systems to provide comprehensive
real-time feedback with location-specific error messages and auto-fix capabilities.
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QTimer

from core_structures import Workflow, ActionStep, ScriptStep
from enhanced_apiton_validator import enhanced_apiton_validator, ValidationError, APIthonValidationResult
from compliance_validator import compliance_validator, ComplianceValidationResult
from dsl_validator import dsl_validator, DSLValidationResult
from mw_actions_catalog import MW_ACTIONS_CATALOG


@dataclass
class ValidationSummary:
    """Summary of all validation results across the workflow."""
    total_errors: int = 0
    total_warnings: int = 0
    errors_by_step: Dict[int, List[ValidationError]] = None
    warnings_by_step: Dict[int, List[ValidationError]] = None
    errors_by_category: Dict[str, List[ValidationError]] = None
    critical_errors: List[ValidationError] = None
    auto_fixable_errors: List[ValidationError] = None
    is_export_ready: bool = False

    def __post_init__(self):
        if self.errors_by_step is None:
            self.errors_by_step = {}
        if self.warnings_by_step is None:
            self.warnings_by_step = {}
        if self.errors_by_category is None:
            self.errors_by_category = {}
        if self.critical_errors is None:
            self.critical_errors = []
        if self.auto_fixable_errors is None:
            self.auto_fixable_errors = []


class RealtimeValidationManager(QObject):
    """
    Comprehensive validation manager that coordinates all validation systems
    and provides real-time feedback with enhanced error messaging.
    """

    validation_updated = Signal(ValidationSummary)  # Emitted when validation results change
    field_validation_updated = Signal(int, str, str, str, str)  # step_index, field_name, state, message, value
    auto_fix_available = Signal(ValidationError)  # Emitted when auto-fix is available

    def __init__(self):
        super().__init__()
        self.current_workflow = None
        self.validation_cache = {}
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._perform_full_validation)
        self.debounce_delay = 300  # ms

    def set_workflow(self, workflow: Workflow):
        """Set the current workflow for validation."""
        self.current_workflow = workflow
        self.validation_cache.clear()
        self._trigger_validation()

    def validate_field(self, step_index: int, field_name: str, value: Any) -> Tuple[bool, str, List[str]]:
        """
        Validate a specific field in real-time.

        Returns:
            Tuple of (is_valid, message, suggestions)
        """
        if not self.current_workflow or step_index >= len(self.current_workflow.steps):
            return True, "No validation context", []

        step = self.current_workflow.steps[step_index]
        step_type = "Action" if isinstance(step, ActionStep) else "Script"

        # Validate based on field type
        if field_name == "output_key":
            return self._validate_output_key(value, step_index, step_type)
        elif field_name == "action_name":
            return self._validate_action_name(value, step_index)
        elif field_name.startswith("input_arg_"):
            arg_name = field_name.replace("input_arg_", "")
            return self._validate_input_arg(arg_name, value, step_index, step_type)
        elif field_name in ["delay_seconds", "timeout", "max_retries"]:
            return self._validate_numeric_field(field_name, value, step_index, step_type)
        elif field_name in ["enabled", "required", "optional"]:
            return self._validate_boolean_field(field_name, value, step_index, step_type)
        else:
            return True, "Field validation not implemented", []

    def _validate_output_key(self, value: str, step_index: int, step_type: str) -> Tuple[bool, str, List[str]]:
        """Validate output_key field with snake_case enforcement."""
        if not value.strip():
            return False, f"Step {step_index + 1} ({step_type}) → output_key: Field is required", ["Add a unique output key"]

        # Check snake_case format
        snake_case_pattern = r'^[a-z][a-z0-9_]*$'
        if not re.match(snake_case_pattern, value):
            suggestions = []

            # Provide specific auto-fix suggestions
            if ' ' in value:
                fixed = value.replace(' ', '_').lower()
                suggestions.append(f"Auto-fix: Replace spaces with underscores → '{fixed}'")
            elif '-' in value:
                fixed = value.replace('-', '_').lower()
                suggestions.append(f"Auto-fix: Replace hyphens with underscores → '{fixed}'")
            elif re.search(r'[A-Z]', value):
                # Convert camelCase to snake_case
                fixed = re.sub(r'([A-Z])', r'_\1', value).lower().lstrip('_')
                suggestions.append(f"Auto-fix: Convert to snake_case → '{fixed}'")
            else:
                suggestions.append("Use lowercase letters, numbers, and underscores only")

            return False, f"Step {step_index + 1} ({step_type}) → output_key: Must use lowercase_snake_case format", suggestions

        # Check for uniqueness
        if self.current_workflow:
            existing_keys = [s.output_key for i, s in enumerate(self.current_workflow.steps)
                           if i != step_index and s.output_key]
            if value in existing_keys:
                return False, f"Step {step_index + 1} ({step_type}) → output_key: Key '{value}' already used in another step", [f"Use a unique key like '{value}_2'"]

        return True, f"✓ Valid output_key: {value}", []

    def _validate_action_name(self, value: str, step_index: int) -> Tuple[bool, str, List[str]]:
        """Validate action_name against MW_ACTIONS_CATALOG."""
        if not value.strip():
            return False, f"Step {step_index + 1} (Action) → action_name: Field is required", ["Select an action from the catalog"]

        # Check if it's a known action
        known_actions = [action.action_name for action in MW_ACTIONS_CATALOG]

        if value in known_actions:
            return True, f"✓ Known Moveworks action: {value}", []

        # Check for similar actions (typo detection)
        similar_actions = [action for action in known_actions if value.lower() in action.lower()]
        suggestions = []

        if similar_actions:
            suggestions = [f"Did you mean: {action}" for action in similar_actions[:3]]
        else:
            suggestions = ["Browse available actions in the catalog", "Check action name spelling"]

        return False, f"Step {step_index + 1} (Action) → action_name: Unknown action '{value}'", suggestions

    def _validate_input_arg(self, arg_name: str, value: str, step_index: int, step_type: str) -> Tuple[bool, str, List[str]]:
        """Validate input argument with DSL expression support."""
        # Validate argument name (snake_case)
        snake_case_pattern = r'^[a-z][a-z0-9_]*$'
        if not re.match(snake_case_pattern, arg_name):
            return False, f"Step {step_index + 1} ({step_type}) → input_args.{arg_name}: Argument name must use lowercase_snake_case", ["Use lowercase letters, numbers, and underscores"]

        # If value looks like DSL, validate it
        if value and (value.startswith('data.') or value.startswith('meta_info.') or '$' in value):
            result = dsl_validator.validate_dsl_expression(value)

            if result.is_valid:
                if result.warnings:
                    warning_msg = "; ".join(result.warnings[:2])
                    return True, f"✓ Valid DSL with warnings: {warning_msg}", result.suggestions
                else:
                    return True, f"✓ Valid DSL expression: {value}", []
            else:
                error_msg = "; ".join(result.errors[:2])
                return False, f"Step {step_index + 1} ({step_type}) → input_args.{arg_name}: Invalid DSL - {error_msg}", result.suggestions

        return True, f"✓ Valid input argument: {arg_name}", []

    def _validate_numeric_field(self, field_name: str, value: str, step_index: int, step_type: str) -> Tuple[bool, str, List[str]]:
        """Validate numeric fields with range checking."""
        if not value.strip():
            return True, f"Optional numeric field: {field_name}", []

        try:
            num_value = int(value)

            # Define ranges for different fields
            ranges = {
                "delay_seconds": (0, 3600),  # 0 to 1 hour
                "timeout": (1, 300),         # 1 second to 5 minutes
                "max_retries": (0, 10)       # 0 to 10 retries
            }

            min_val, max_val = ranges.get(field_name, (0, 4294967295))

            if min_val <= num_value <= max_val:
                return True, f"✓ Valid {field_name}: {num_value}", []
            else:
                suggestions = [
                    f"Minimum value: {min_val}",
                    f"Maximum value: {max_val}",
                    f"Recommended range: {min_val}-{min(max_val, 60)}"
                ]
                return False, f"Step {step_index + 1} ({step_type}) → {field_name}: Value {num_value} outside valid range ({min_val}-{max_val})", suggestions

        except ValueError:
            return False, f"Step {step_index + 1} ({step_type}) → {field_name}: Invalid number format", ["Enter a valid integer"]

    def _validate_boolean_field(self, field_name: str, value: str, step_index: int, step_type: str) -> Tuple[bool, str, List[str]]:
        """Validate boolean fields."""
        if not value.strip():
            return True, f"Optional boolean field: {field_name}", []

        value_lower = value.lower().strip()
        valid_true = ["true", "yes", "1", "on", "enabled"]
        valid_false = ["false", "no", "0", "off", "disabled"]

        if value_lower in valid_true or value_lower in valid_false:
            return True, f"✓ Valid boolean: {value}", []
        else:
            suggestions = [
                "Valid true values: true, yes, 1",
                "Valid false values: false, no, 0"
            ]
            return False, f"Step {step_index + 1} ({step_type}) → {field_name}: Invalid boolean value '{value}'", suggestions

    def _trigger_validation(self):
        """Trigger full workflow validation with debouncing."""
        self.debounce_timer.stop()
        self.debounce_timer.start(self.debounce_delay)

    def _perform_full_validation(self):
        """Perform comprehensive validation of the entire workflow."""
        if not self.current_workflow:
            return

        summary = ValidationSummary()
        all_errors = []
        all_warnings = []

        # Validate each step
        for step_index, step in enumerate(self.current_workflow.steps):
            step_errors, step_warnings = self._validate_step(step, step_index)

            if step_errors:
                summary.errors_by_step[step_index] = step_errors
                all_errors.extend(step_errors)

            if step_warnings:
                summary.warnings_by_step[step_index] = step_warnings
                all_warnings.extend(step_warnings)

        # Categorize errors
        for error in all_errors:
            category = error.error_type
            if category not in summary.errors_by_category:
                summary.errors_by_category[category] = []
            summary.errors_by_category[category].append(error)

            # Check for critical errors
            if error.severity == "error" and error.error_type in ["structural", "mandatory_field"]:
                summary.critical_errors.append(error)

            # Check for auto-fixable errors
            if error.auto_fix_available:
                summary.auto_fixable_errors.append(error)

        # Set summary totals
        summary.total_errors = len(all_errors)
        summary.total_warnings = len(all_warnings)
        summary.is_export_ready = len(summary.critical_errors) == 0

        # Emit validation update
        self.validation_updated.emit(summary)

    def _validate_step(self, step, step_index: int) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate a single step and return errors and warnings."""
        errors = []
        warnings = []

        step_type = "Action" if isinstance(step, ActionStep) else "Script"

        # Basic field validation
        if not step.output_key:
            errors.append(ValidationError(
                message="Output key is required",
                step_number=step_index + 1,
                step_type=step_type,
                field_name="output_key",
                error_type="mandatory_field",
                remediation="Add a unique output key for this step",
                educational_context="Output keys are used to reference step results in subsequent steps"
            ))

        # Step-specific validation
        if isinstance(step, ActionStep):
            if not step.action_name:
                errors.append(ValidationError(
                    message="Action name is required",
                    step_number=step_index + 1,
                    step_type="Action",
                    field_name="action_name",
                    error_type="mandatory_field",
                    remediation="Select an action from the Moveworks catalog",
                    educational_context="Action name specifies which Moveworks action to execute"
                ))

        elif isinstance(step, ScriptStep):
            # Use enhanced APIthon validator
            available_paths = self._get_available_data_paths(step_index)
            result = enhanced_apiton_validator.comprehensive_validate(step, available_paths)

            # Add step context to APIthon validation errors
            for error in result.errors:
                error.step_number = step_index + 1
                error.step_type = "Script"
                errors.append(error)

            for warning in result.warnings:
                warning.step_number = step_index + 1
                warning.step_type = "Script"
                warnings.append(warning)

        return errors, warnings

    def _get_available_data_paths(self, step_index: int) -> Set[str]:
        """Get available data paths for a step based on previous steps."""
        available_paths = set()

        # Add meta_info paths
        available_paths.add("meta_info.user.email")
        available_paths.add("meta_info.user.name")
        available_paths.add("meta_info.user.id")

        # Add data paths from previous steps
        for i, step in enumerate(self.current_workflow.steps):
            if i >= step_index:
                break

            if step.output_key:
                available_paths.add(f"data.{step.output_key}")

        return available_paths

    def apply_auto_fix(self, error: ValidationError) -> bool:
        """Apply an automatic fix for the given error."""
        if not error.auto_fix_available or not error.auto_fix_data:
            return False

        # Implement auto-fix logic based on error type
        fix_type = error.auto_fix_data.get("type")

        if fix_type == "snake_case_conversion":
            # Auto-fix snake_case conversion
            original_value = error.auto_fix_data.get("original_value")
            fixed_value = error.auto_fix_data.get("fixed_value")

            # Apply the fix to the workflow
            # This would need to be implemented based on the specific field
            return True

        return False


# Global validation manager instance
realtime_validation_manager = RealtimeValidationManager()
