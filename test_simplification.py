#!/usr/bin/env python3
"""
Test script for the Moveworks YAML Assistant simplification features.

This script tests the new components:
- ExpressionFactory
- SimplifiedTemplateSystem
- WorkflowWizard
- SimplifiedDataPathSelector
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_expression_factory():
    """Test the ExpressionFactory functionality."""
    print("🧪 Testing ExpressionFactory...")
    
    try:
        from expression_factory import ExpressionFactory, CommonPatterns
        from core_structures import ActionStep, ScriptStep
        
        # Test creating an action
        action = ExpressionFactory.create_action(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.user_email"}
        )
        
        assert isinstance(action, ActionStep)
        assert action.action_name == "mw.get_user_by_email"
        assert action.output_key == "user_info"
        assert action.input_args["email"] == "data.user_email"
        
        # Test creating a script
        script = ExpressionFactory.create_script(
            code="return {'success': True}",
            output_key="script_result"
        )
        
        assert isinstance(script, ScriptStep)
        assert script.code == "return {'success': True}"
        assert script.output_key == "script_result"
        
        # Test common patterns
        user_lookup_steps = CommonPatterns.user_lookup_pattern()
        assert len(user_lookup_steps) == 2
        assert isinstance(user_lookup_steps[0], ActionStep)
        assert isinstance(user_lookup_steps[1], ScriptStep)
        
        print("✅ ExpressionFactory tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ExpressionFactory tests failed: {e}")
        return False

def test_simplified_template_system():
    """Test the SimplifiedTemplateSystem functionality."""
    print("🧪 Testing SimplifiedTemplateSystem...")
    
    try:
        from template_library import SimplifiedTemplateSystem
        
        template_system = SimplifiedTemplateSystem()
        
        # Test getting categories
        categories = template_system.get_template_categories()
        assert len(categories) > 0
        assert "User Management" in categories
        
        # Test getting templates by category
        user_mgmt_templates = template_system.get_templates_by_category("User Management")
        assert len(user_mgmt_templates) > 0
        
        # Test getting specific template
        user_lookup_template = template_system.get_template_by_key("user_lookup")
        assert user_lookup_template is not None
        assert user_lookup_template["name"] == "User Lookup"
        assert user_lookup_template["complexity"] == "Simple"
        
        print("✅ SimplifiedTemplateSystem tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ SimplifiedTemplateSystem tests failed: {e}")
        return False

def test_workflow_wizard():
    """Test the WorkflowWizard functionality (basic instantiation)."""
    print("🧪 Testing WorkflowWizard...")
    
    try:
        from workflow_wizard import WorkflowWizard
        from core_structures import Workflow
        
        # Test basic instantiation (can't test full UI without Qt app)
        wizard = WorkflowWizard()
        assert wizard is not None
        assert hasattr(wizard, 'workflow_data')
        assert hasattr(wizard, 'template_system')
        
        # Test workflow creation from data
        workflow = wizard.createWorkflowFromData()
        assert isinstance(workflow, Workflow)
        
        print("✅ WorkflowWizard tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowWizard tests failed: {e}")
        return False

def test_simplified_data_path_selector():
    """Test the SimplifiedDataPathSelector functionality (basic instantiation)."""
    print("🧪 Testing SimplifiedDataPathSelector...")
    
    try:
        from simplified_data_path_selector import SimplifiedDataPathSelector
        from core_structures import Workflow
        
        # Test basic instantiation (can't test full UI without Qt app)
        workflow = Workflow()
        selector = SimplifiedDataPathSelector(workflow)
        assert selector is not None
        assert selector.workflow == workflow
        assert hasattr(selector, 'recent_paths')
        
        # Test adding recent paths
        selector.addRecentPath("data.user_email")
        selector.addRecentPath("data.user_info.user.name")
        
        print("✅ SimplifiedDataPathSelector tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ SimplifiedDataPathSelector tests failed: {e}")
        return False

def test_yaml_generation():
    """Test YAML generation with the new factory components."""
    print("🧪 Testing YAML generation with new components...")
    
    try:
        from expression_factory import ExpressionFactory
        from core_structures import Workflow
        from yaml_generator import generate_yaml_string
        
        # Create a workflow using the factory
        steps = [
            ExpressionFactory.create_action(
                action_name="mw.get_user_by_email",
                output_key="user_info",
                input_args={"email": "data.user_email"}
            ),
            ExpressionFactory.create_script(
                code="return {'processed': True, 'user_id': data.user_info.user.id}",
                output_key="processing_result"
            )
        ]
        
        workflow = Workflow(steps=steps)
        
        # Generate YAML
        yaml_output = generate_yaml_string(workflow, "test_workflow")
        
        assert "action_name: test_workflow" in yaml_output
        assert "mw.get_user_by_email" in yaml_output
        assert "user_info" in yaml_output
        assert "processing_result" in yaml_output
        
        print("✅ YAML generation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ YAML generation tests failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Moveworks YAML Assistant Simplification Tests\n")
    
    tests = [
        test_expression_factory,
        test_simplified_template_system,
        test_workflow_wizard,
        test_simplified_data_path_selector,
        test_yaml_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simplification features are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
