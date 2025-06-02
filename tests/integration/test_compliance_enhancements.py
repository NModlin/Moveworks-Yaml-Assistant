#!/usr/bin/env python3
"""
Integration tests for enhanced compliance validation and YAML generation.

Tests the improvements made in Phase 1 and Phase 2 of the compliance implementation plan:
- Enhanced mandatory field enforcement with type checking
- Improved DSL value quoting for numeric/boolean literals
- Strict validation according to Moveworks specifications
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep, TryCatchStep, CatchBlock
)
from compliance_validator import compliance_validator, ComplianceValidationResult
from yaml_generator import generate_yaml_string, _is_dsl_expression, _is_numeric_or_boolean_literal


class TestComplianceEnhancements(unittest.TestCase):
    """Test enhanced compliance validation and YAML generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = compliance_validator

    def test_enhanced_mandatory_field_validation(self):
        """Test enhanced mandatory field validation with type checking."""
        # Test ActionStep with empty mandatory fields
        action_step = ActionStep(action_name="", output_key="")  # Empty required fields
        workflow = Workflow(steps=[action_step])

        result = self.validator.validate_workflow_compliance(workflow, "test_action")

        # Should have mandatory field errors
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.mandatory_field_errors) >= 2)

        # Check for specific error messages
        error_messages = ' '.join(result.mandatory_field_errors)
        self.assertIn('action_name', error_messages)
        self.assertIn('output_key', error_messages)
        self.assertIn('cannot be empty', error_messages)

    def test_type_validation_for_fields(self):
        """Test type validation for step fields."""
        # Create ActionStep with valid required fields but wrong optional field types
        action_step = ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info"
        )

        # Manually set wrong types after creation to bypass constructor validation
        action_step.input_args = "not_a_dict"  # Should be dict
        action_step.delay_config = ["not_a_dict"]  # Should be dict

        workflow = Workflow(steps=[action_step])

        result = self.validator.validate_workflow_compliance(workflow, "test_action")

        # Should have type validation errors
        self.assertFalse(result.is_valid)
        type_errors = [error for error in result.errors if 'should be' in error]
        self.assertTrue(len(type_errors) >= 2)

    def test_switch_step_validation(self):
        """Test SwitchStep validation for empty cases."""
        # Test SwitchStep with empty cases list
        switch_step = SwitchStep(cases=[])  # Empty cases list
        workflow = Workflow(steps=[switch_step])
        
        result = self.validator.validate_workflow_compliance(workflow, "test_action")
        
        # Should have mandatory field error for empty cases
        self.assertFalse(result.is_valid)
        error_messages = ' '.join(result.mandatory_field_errors)
        self.assertIn('cases', error_messages)
        self.assertIn('cannot be empty', error_messages)

    def test_for_loop_step_validation(self):
        """Test ForLoopStep validation for required fields."""
        # Test ForLoopStep with missing steps
        for_step = ForLoopStep(
            each="item",
            in_source="data.items",
            output_key="results",
            steps=[]  # Empty steps list
        )
        workflow = Workflow(steps=[for_step])
        
        result = self.validator.validate_workflow_compliance(workflow, "test_action")
        
        # Should have error for empty steps
        self.assertFalse(result.is_valid)
        error_messages = ' '.join(result.mandatory_field_errors)
        self.assertIn('steps', error_messages)
        self.assertIn('at least one step required', error_messages)

    def test_dsl_expression_detection(self):
        """Test DSL expression detection."""
        # Test data references
        self.assertTrue(_is_dsl_expression("data.user_info"))
        self.assertTrue(_is_dsl_expression("data.user_info.email"))
        self.assertTrue(_is_dsl_expression("data.items[0]"))
        
        # Test meta_info references
        self.assertTrue(_is_dsl_expression("meta_info.user.email"))
        self.assertTrue(_is_dsl_expression("requestor.department"))
        
        # Test DSL functions
        self.assertTrue(_is_dsl_expression("$CONCAT(data.first_name, ' ', data.last_name)"))
        self.assertTrue(_is_dsl_expression("$IF(data.active == 'true', 'Active', 'Inactive')"))
        
        # Test comparison operators
        self.assertTrue(_is_dsl_expression("data.count > 5"))
        self.assertTrue(_is_dsl_expression("data.status == 'active'"))
        
        # Test non-DSL expressions
        self.assertFalse(_is_dsl_expression("simple_string"))
        self.assertFalse(_is_dsl_expression("user@example.com"))

    def test_numeric_boolean_literal_detection(self):
        """Test numeric and boolean literal detection."""
        # Test boolean literals
        self.assertTrue(_is_numeric_or_boolean_literal("true"))
        self.assertTrue(_is_numeric_or_boolean_literal("false"))
        self.assertTrue(_is_numeric_or_boolean_literal("True"))
        self.assertTrue(_is_numeric_or_boolean_literal("FALSE"))
        
        # Test numeric literals
        self.assertTrue(_is_numeric_or_boolean_literal("123"))
        self.assertTrue(_is_numeric_or_boolean_literal("123.45"))
        self.assertTrue(_is_numeric_or_boolean_literal("-123"))
        self.assertTrue(_is_numeric_or_boolean_literal("0"))
        
        # Test non-literals
        self.assertFalse(_is_numeric_or_boolean_literal("data.count"))
        self.assertFalse(_is_numeric_or_boolean_literal("user_email"))
        self.assertFalse(_is_numeric_or_boolean_literal("abc123"))

    def test_yaml_generation_with_dsl_quoting(self):
        """Test YAML generation with proper DSL quoting."""
        # Create a workflow with DSL expressions and literals
        action_step = ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={
                "email": "data.input_email",  # DSL expression
                "timeout": "30",  # Numeric literal
                "active_only": "true",  # Boolean literal
                "department": "Engineering"  # Regular string
            }
        )
        
        script_step = ScriptStep(
            code="""
# Process user data
if data.user_info.active:
    result = {"status": "active", "count": 1}
else:
    result = {"status": "inactive", "count": 0}
return result
            """.strip(),
            output_key="processed_data"
        )
        
        workflow = Workflow(steps=[action_step, script_step])
        
        # Generate YAML
        yaml_output = generate_yaml_string(workflow, "test_compound_action")
        
        # Verify YAML structure
        self.assertIn("action_name: test_compound_action", yaml_output)
        self.assertIn("steps:", yaml_output)
        
        # Verify DSL expression quoting
        self.assertIn('"data.input_email"', yaml_output)  # DSL expression in double quotes
        
        # Verify literal quoting
        self.assertIn("'30'", yaml_output)  # Numeric literal in single quotes
        self.assertIn("'true'", yaml_output)  # Boolean literal in single quotes
        
        # Verify multiline script formatting
        self.assertIn("code: |", yaml_output)  # Literal block scalar for multiline code

    def test_parallel_step_validation(self):
        """Test ParallelStep validation for required configuration."""
        # Test ParallelStep with neither branches nor for_loop
        parallel_step = ParallelStep()  # No branches or for_loop
        workflow = Workflow(steps=[parallel_step])
        
        result = self.validator.validate_workflow_compliance(workflow, "test_action")
        
        # Should have error for missing configuration
        self.assertFalse(result.is_valid)
        error_messages = ' '.join(result.mandatory_field_errors)
        self.assertIn('branches', error_messages)
        self.assertIn('for_loop', error_messages)

    def test_try_catch_step_validation(self):
        """Test TryCatchStep validation for required try_steps."""
        # Test TryCatchStep with empty try_steps
        try_catch_step = TryCatchStep(try_steps=[])  # Empty try_steps
        workflow = Workflow(steps=[try_catch_step])
        
        result = self.validator.validate_workflow_compliance(workflow, "test_action")
        
        # Should have error for empty try_steps
        self.assertFalse(result.is_valid)
        error_messages = ' '.join(result.mandatory_field_errors)
        self.assertIn('try_steps', error_messages)
        self.assertIn('at least one step required', error_messages)

    def test_input_args_structure_validation(self):
        """Test input_args structure validation."""
        # Test ActionStep with complex input_args
        action_step = ActionStep(
            action_name="mw.create_ticket",
            output_key="ticket_info",
            input_args={
                "valid_key": "data.summary",
                "invalid-key!": "value",  # Invalid key with special characters
                "complex_expr": "data.count > 5 && data.active == 'true'"  # Complex DSL
            }
        )
        workflow = Workflow(steps=[action_step])
        
        result = self.validator.validate_workflow_compliance(workflow, "test_action")
        
        # Should have warnings for invalid key naming and suggestions for complex expressions
        self.assertTrue(len(result.warnings) > 0 or len(result.suggestions) > 0)

    def test_complete_workflow_validation(self):
        """Test validation of a complete, valid workflow."""
        # Create a valid workflow with all expression types
        action_step = ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.input_email"}
        )
        
        script_step = ScriptStep(
            code="result = {'processed': True}\nreturn result",
            output_key="processed_data"
        )
        
        return_step = ReturnStep(
            output_mapper={
                "user": "data.user_info",
                "processed": "data.processed_data"
            }
        )
        
        workflow = Workflow(steps=[action_step, script_step, return_step])
        
        result = self.validator.validate_workflow_compliance(workflow, "valid_compound_action")
        
        # Should be valid
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.mandatory_field_errors), 0)
        
        # Should generate valid YAML
        yaml_output = generate_yaml_string(workflow, "valid_compound_action")
        self.assertIn("action_name: valid_compound_action", yaml_output)
        self.assertIn("steps:", yaml_output)


if __name__ == '__main__':
    unittest.main()
