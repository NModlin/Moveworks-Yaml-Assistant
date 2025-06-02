"""
Unit tests for the Moveworks YAML Assistant simplification features.

This module tests the new components introduced in the simplification project:
- ExpressionFactory
- SimplifiedTemplateSystem
- CommonPatterns
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from expression_factory import ExpressionFactory, CommonPatterns
from template_library import SimplifiedTemplateSystem
from core_structures import (
    ActionStep, ScriptStep, SwitchStep, ForLoopStep, ParallelStep,
    ReturnStep, RaiseStep, TryCatchStep, Workflow, InputVariable
)


class TestExpressionFactory(unittest.TestCase):
    """Test cases for the ExpressionFactory class."""
    
    def test_create_action(self):
        """Test creating action steps with the factory."""
        action = ExpressionFactory.create_action(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.user_email"},
            description="Get user by email"
        )
        
        self.assertIsInstance(action, ActionStep)
        self.assertEqual(action.action_name, "mw.get_user_by_email")
        self.assertEqual(action.output_key, "user_info")
        self.assertEqual(action.input_args["email"], "data.user_email")
        self.assertEqual(action.description, "Get user by email")
    
    def test_create_action_defaults(self):
        """Test creating action steps with default values."""
        action = ExpressionFactory.create_action()
        
        self.assertIsInstance(action, ActionStep)
        self.assertEqual(action.action_name, "")
        self.assertEqual(action.output_key, "action_result")
        self.assertEqual(action.input_args, {})
        self.assertEqual(action.description, "")
    
    def test_create_script(self):
        """Test creating script steps with the factory."""
        script = ExpressionFactory.create_script(
            code="return {'success': True}",
            output_key="script_result",
            description="Process data"
        )
        
        self.assertIsInstance(script, ScriptStep)
        self.assertEqual(script.code, "return {'success': True}")
        self.assertEqual(script.output_key, "script_result")
        self.assertEqual(script.description, "Process data")
    
    def test_create_script_defaults(self):
        """Test creating script steps with default values."""
        script = ExpressionFactory.create_script()
        
        self.assertIsInstance(script, ScriptStep)
        self.assertEqual(script.code, "# Your APIthon code here\nreturn {}")
        self.assertEqual(script.output_key, "script_result")
        self.assertEqual(script.description, "")
    
    def test_create_switch(self):
        """Test creating switch steps with the factory."""
        switch = ExpressionFactory.create_switch(
            description="Handle user types"
        )
        
        self.assertIsInstance(switch, SwitchStep)
        self.assertEqual(switch.description, "Handle user types")
        self.assertEqual(switch.cases, [])
        self.assertIsNone(switch.default_case)
    
    def test_create_for_loop(self):
        """Test creating for loop steps with the factory."""
        for_loop = ExpressionFactory.create_for_loop(
            each="user",
            in_source="data.users",
            output_key="processed_users"
        )
        
        self.assertIsInstance(for_loop, ForLoopStep)
        self.assertEqual(for_loop.each, "user")
        self.assertEqual(for_loop.in_source, "data.users")
        self.assertEqual(for_loop.output_key, "processed_users")
        self.assertEqual(for_loop.steps, [])
    
    def test_create_parallel(self):
        """Test creating parallel steps with the factory."""
        parallel = ExpressionFactory.create_parallel(
            description="Run actions in parallel"
        )
        
        self.assertIsInstance(parallel, ParallelStep)
        self.assertEqual(parallel.description, "Run actions in parallel")
        self.assertEqual(parallel.branches, [])
    
    def test_create_return(self):
        """Test creating return steps with the factory."""
        return_step = ExpressionFactory.create_return(
            output_mapper={"result": "data.final_result"},
            description="Return workflow result"
        )
        
        self.assertIsInstance(return_step, ReturnStep)
        self.assertEqual(return_step.output_mapper["result"], "data.final_result")
        self.assertEqual(return_step.description, "Return workflow result")
    
    def test_create_raise(self):
        """Test creating raise steps with the factory."""
        raise_step = ExpressionFactory.create_raise(
            message="User not found",
            output_key="error_result",
            description="Handle user not found error"
        )
        
        self.assertIsInstance(raise_step, RaiseStep)
        self.assertEqual(raise_step.message, "User not found")
        self.assertEqual(raise_step.output_key, "error_result")
        self.assertEqual(raise_step.description, "Handle user not found error")
    
    def test_create_try_catch(self):
        """Test creating try-catch steps with the factory."""
        try_catch = ExpressionFactory.create_try_catch(
            description="Handle potential failures"
        )
        
        self.assertIsInstance(try_catch, TryCatchStep)
        self.assertEqual(try_catch.description, "Handle potential failures")
        self.assertEqual(try_catch.try_steps, [])
        self.assertIsNone(try_catch.catch_block)


class TestCommonPatterns(unittest.TestCase):
    """Test cases for the CommonPatterns class."""
    
    def test_user_lookup_pattern(self):
        """Test the user lookup pattern."""
        steps = CommonPatterns.user_lookup_pattern()
        
        self.assertEqual(len(steps), 2)
        self.assertIsInstance(steps[0], ActionStep)
        self.assertIsInstance(steps[1], ScriptStep)
        
        # Check action step
        action = steps[0]
        self.assertEqual(action.action_name, "mw.get_user_by_email")
        self.assertEqual(action.output_key, "user_info")
        self.assertEqual(action.input_args["email"], "data.user_email")
        
        # Check script step
        script = steps[1]
        self.assertEqual(script.output_key, "user_validation")
        self.assertIn("data.user_info", script.code)
    
    def test_user_lookup_pattern_custom_email(self):
        """Test the user lookup pattern with custom email field."""
        steps = CommonPatterns.user_lookup_pattern("data.custom_email")
        
        action = steps[0]
        self.assertEqual(action.input_args["email"], "data.custom_email")
    
    def test_error_handling_pattern(self):
        """Test the error handling pattern."""
        try_catch = CommonPatterns.error_handling_pattern(
            "mw.risky_action",
            {"param": "data.input"}
        )
        
        self.assertIsInstance(try_catch, TryCatchStep)
        self.assertEqual(len(try_catch.try_steps), 1)
        self.assertIsNotNone(try_catch.catch_block)
        
        # Check try step
        action = try_catch.try_steps[0]
        self.assertIsInstance(action, ActionStep)
        self.assertEqual(action.action_name, "mw.risky_action")
        self.assertEqual(action.input_args["param"], "data.input")
        
        # Check catch block
        catch_steps = try_catch.catch_block.steps
        self.assertEqual(len(catch_steps), 1)
        self.assertIsInstance(catch_steps[0], ScriptStep)
    
    def test_conditional_processing_pattern(self):
        """Test the conditional processing pattern."""
        switch = CommonPatterns.conditional_processing_pattern(
            "data.user_type == 'admin'",
            "admin_action",
            "regular_action"
        )
        
        self.assertIsInstance(switch, SwitchStep)
        self.assertEqual(len(switch.cases), 1)
        self.assertIsNotNone(switch.default_case)
        
        # Check case
        case = switch.cases[0]
        self.assertEqual(case.condition, "data.user_type == 'admin'")
        self.assertEqual(len(case.steps), 1)
        self.assertIsInstance(case.steps[0], ActionStep)
        self.assertEqual(case.steps[0].action_name, "admin_action")
        
        # Check default case
        default_steps = switch.default_case.steps
        self.assertEqual(len(default_steps), 1)
        self.assertIsInstance(default_steps[0], ActionStep)
        self.assertEqual(default_steps[0].action_name, "regular_action")


class TestSimplifiedTemplateSystem(unittest.TestCase):
    """Test cases for the SimplifiedTemplateSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template_system = SimplifiedTemplateSystem()
    
    def test_initialization(self):
        """Test that the template system initializes correctly."""
        self.assertIsInstance(self.template_system.templates, dict)
        self.assertGreater(len(self.template_system.templates), 0)
    
    def test_get_template_categories(self):
        """Test getting template categories."""
        categories = self.template_system.get_template_categories()
        
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        self.assertIn("User Management", categories)
        self.assertIn("Communication", categories)
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        user_mgmt_templates = self.template_system.get_templates_by_category("User Management")
        
        self.assertIsInstance(user_mgmt_templates, dict)
        self.assertGreater(len(user_mgmt_templates), 0)
        
        # Check that all returned templates are in the correct category
        for template in user_mgmt_templates.values():
            self.assertEqual(template["category"], "User Management")
    
    def test_get_template_by_key(self):
        """Test getting a specific template by key."""
        template = self.template_system.get_template_by_key("user_lookup")
        
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], "User Lookup")
        self.assertEqual(template["category"], "User Management")
        self.assertEqual(template["complexity"], "Simple")
        self.assertIn("yaml", template)
        self.assertIn("description", template)
    
    def test_get_nonexistent_template(self):
        """Test getting a template that doesn't exist."""
        template = self.template_system.get_template_by_key("nonexistent_template")
        self.assertIsNone(template)
    
    def test_template_structure(self):
        """Test that all templates have the required structure."""
        required_fields = ["name", "description", "category", "complexity", "yaml"]
        
        for key, template in self.template_system.templates.items():
            for field in required_fields:
                self.assertIn(field, template, f"Template '{key}' missing field '{field}'")
            
            # Check that complexity is one of the expected values
            self.assertIn(template["complexity"], ["Simple", "Moderate", "Advanced"])
    
    def test_yaml_content(self):
        """Test that template YAML content is valid."""
        for key, template in self.template_system.templates.items():
            yaml_content = template["yaml"]
            
            # Basic checks for YAML structure
            self.assertIn("action_name:", yaml_content)
            self.assertIn("steps:", yaml_content)
            
            # Check for proper indentation (should use spaces, not tabs)
            self.assertNotIn("\t", yaml_content, f"Template '{key}' contains tabs instead of spaces")


class TestWorkflowIntegration(unittest.TestCase):
    """Test integration between new components and existing workflow structures."""
    
    def test_factory_with_workflow(self):
        """Test using ExpressionFactory with Workflow objects."""
        steps = [
            ExpressionFactory.create_action(
                action_name="mw.get_user_by_email",
                output_key="user_info",
                input_args={"email": "data.user_email"}
            ),
            ExpressionFactory.create_script(
                code="return {'processed': True}",
                output_key="processing_result"
            )
        ]
        
        workflow = Workflow(steps=steps)
        
        self.assertEqual(len(workflow.steps), 2)
        self.assertIsInstance(workflow.steps[0], ActionStep)
        self.assertIsInstance(workflow.steps[1], ScriptStep)
    
    def test_common_patterns_with_workflow(self):
        """Test using CommonPatterns with Workflow objects."""
        user_lookup_steps = CommonPatterns.user_lookup_pattern()
        workflow = Workflow(steps=user_lookup_steps)
        
        self.assertEqual(len(workflow.steps), 2)
        self.assertIsInstance(workflow.steps[0], ActionStep)
        self.assertIsInstance(workflow.steps[1], ScriptStep)
    
    def test_workflow_with_input_variables(self):
        """Test creating workflows with input variables using the factory."""
        input_variables = [
            InputVariable(
                name="user_email",
                data_type="string",
                description="User's email address",
                required=True
            ),
            InputVariable(
                name="message",
                data_type="string",
                description="Message to send",
                required=False,
                default_value="Welcome!"
            )
        ]
        
        steps = [
            ExpressionFactory.create_action(
                action_name="mw.send_notification",
                output_key="notification_result",
                input_args={
                    "recipient": "data.user_email",
                    "message": "data.message"
                }
            )
        ]
        
        workflow = Workflow(steps=steps, input_variables=input_variables)
        
        self.assertEqual(len(workflow.input_variables), 2)
        self.assertEqual(workflow.input_variables[0].name, "user_email")
        self.assertEqual(workflow.input_variables[1].name, "message")
        self.assertTrue(workflow.input_variables[0].required)
        self.assertFalse(workflow.input_variables[1].required)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestExpressionFactory))
    test_suite.addTest(unittest.makeSuite(TestCommonPatterns))
    test_suite.addTest(unittest.makeSuite(TestSimplifiedTemplateSystem))
    test_suite.addTest(unittest.makeSuite(TestWorkflowIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
