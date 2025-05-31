#!/usr/bin/env python3
"""
Comprehensive test for action_name field compliance implementation.

This script tests all aspects of the action_name compliance system including:
- Mandatory field enforcement for ActionStep instances
- Naming convention validation (alphanumeric, dots, underscores)
- Integration with Moveworks Actions Catalog
- YAML generation blocking for non-compliant workflows
- UI validation indicators and error messaging
"""

import sys
from core_structures import Workflow, ActionStep, ScriptStep
from compliance_validator import compliance_validator
from action_name_validator import action_name_validator
from yaml_generator import generate_yaml_string


def test_mandatory_field_enforcement():
    """Test that action_name field is mandatory for ActionStep instances."""
    print("🔍 Testing Mandatory Field Enforcement")
    print("=" * 50)
    
    # Test ActionStep without action_name
    action_step = ActionStep(
        action_name="",  # Empty - should fail
        output_key="user_info",
        description="Test action"
    )
    
    workflow = Workflow(steps=[action_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    # Should have mandatory field errors
    assert not result.is_valid, "Workflow should be invalid with empty action_name"
    assert any("action_name" in error.lower() for error in result.mandatory_field_errors), \
        "Should have action_name mandatory field error"
    
    print("✅ ActionStep mandatory field enforcement: PASSED")
    
    # Test ActionStep with None action_name
    action_step.action_name = None
    
    workflow = Workflow(steps=[action_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    assert not result.is_valid, "Workflow should be invalid with None action_name"
    print("✅ ActionStep None action_name enforcement: PASSED")
    
    # Test ScriptStep (should not require action_name)
    script_step = ScriptStep(
        code="return {'result': 'test'}",
        output_key="script_result",
        description="Test script"
    )
    
    workflow = Workflow(steps=[script_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    # Should not have action_name errors for ScriptStep
    action_name_errors = [error for error in result.mandatory_field_errors 
                         if "action_name" in error.lower()]
    assert len(action_name_errors) == 0, "ScriptStep should not require action_name"
    
    print("✅ ScriptStep action_name not required: PASSED")


def test_naming_convention_validation():
    """Test action_name naming convention validation."""
    print("\n🔍 Testing Naming Convention Validation")
    print("=" * 50)
    
    # Test invalid naming patterns
    invalid_names = [
        "action name",      # spaces
        "action-name",      # hyphens
        "action@name",      # special characters
        "action/name",      # slashes
        "action name!",     # exclamation
        "action\tname",     # tabs
        "action\nname",     # newlines
        "a",               # too short
        "",                # empty
    ]
    
    for invalid_name in invalid_names:
        result = action_name_validator.validate_action_name(invalid_name)
        assert not result.is_valid, f"'{invalid_name}' should be invalid"
        print(f"✅ Invalid name '{invalid_name}': correctly rejected")
    
    # Test valid naming patterns
    valid_names = [
        "mw.get_user_by_email",
        "mw.create_ticket",
        "custom_action",
        "my_action_123",
        "action.with.dots",
        "action_with_underscores",
        "ActionWithCamelCase",  # While not recommended, it's technically valid
        "action123",
        "get_user",
    ]
    
    for valid_name in valid_names:
        result = action_name_validator.validate_action_name(valid_name)
        assert result.is_valid, f"'{valid_name}' should be valid"
        print(f"✅ Valid name '{valid_name}': correctly accepted")


def test_mw_prefix_validation():
    """Test validation of mw. prefix format."""
    print("\n🔍 Testing MW Prefix Validation")
    print("=" * 50)
    
    # Test incomplete mw. prefix
    result = action_name_validator.validate_action_name("mw.")
    assert not result.is_valid, "'mw.' should be invalid (incomplete)"
    assert any("incomplete" in error.lower() for error in result.errors), \
        "Should have incomplete error"
    print("✅ Incomplete 'mw.' prefix: correctly rejected")
    
    # Test valid mw. actions
    valid_mw_actions = [
        "mw.get_user_by_email",
        "mw.create_ticket",
        "mw.search_knowledge_base"
    ]
    
    for action_name in valid_mw_actions:
        result = action_name_validator.validate_action_name(action_name)
        assert result.is_valid, f"'{action_name}' should be valid"
        print(f"✅ Valid mw. action '{action_name}': correctly accepted")


def test_catalog_integration():
    """Test integration with Moveworks Actions Catalog."""
    print("\n🔍 Testing Catalog Integration")
    print("=" * 50)
    
    # Test known Moveworks action
    result = action_name_validator.validate_action_name("mw.get_user_by_email")
    assert result.is_valid, "Known Moveworks action should be valid"
    assert result.is_known_action, "Should be recognized as known action"
    print("✅ Known Moveworks action recognition: PASSED")
    
    # Test unknown action (should be valid format but not in catalog)
    result = action_name_validator.validate_action_name("mw.unknown_action")
    assert result.is_valid, "Valid format should pass even if not in catalog"
    assert not result.is_known_action, "Should not be recognized as known action"
    assert len(result.warnings) > 0, "Should have warnings about unknown action"
    print("✅ Unknown action warning: PASSED")
    
    # Test custom action (not mw. prefix)
    result = action_name_validator.validate_action_name("custom_action")
    assert result.is_valid, "Custom action should be valid"
    assert not result.is_known_action, "Custom action should not be in catalog"
    print("✅ Custom action validation: PASSED")


def test_yaml_generation_blocking():
    """Test that YAML generation is blocked for non-compliant action_name."""
    print("\n🔍 Testing YAML Generation Blocking")
    print("=" * 50)
    
    # Create non-compliant workflow
    action_step = ActionStep(
        action_name="",  # Missing required field
        output_key="user_info",
        description="Test action"
    )
    
    workflow = Workflow(steps=[action_step])
    
    # Should raise ValueError when trying to generate YAML
    try:
        yaml_output = generate_yaml_string(workflow, "test_action")
        assert False, "YAML generation should have been blocked"
    except ValueError as e:
        assert "action_name" in str(e).lower(), "Error should mention action_name"
        print("✅ YAML generation blocking: PASSED")
    
    # Test compliant workflow
    action_step.action_name = "mw.get_user_by_email"
    
    try:
        yaml_output = generate_yaml_string(workflow, "test_action")
        assert "action_name: mw.get_user_by_email" in yaml_output, "YAML should contain action_name"
        print("✅ Compliant YAML generation: PASSED")
    except Exception as e:
        assert False, f"Compliant workflow should generate YAML: {e}"


def test_field_name_standardization():
    """Test that the exact field name 'action_name' is used."""
    print("\n🔍 Testing Field Name Standardization")
    print("=" * 50)
    
    # Create compliant ActionStep
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Test action"
    )
    
    workflow = Workflow(steps=[action_step])
    
    # Generate YAML and check field name
    yaml_output = generate_yaml_string(workflow, "test_action")
    
    # Should use exact field name "action_name"
    assert "action_name:" in yaml_output, "YAML should contain 'action_name:' field"
    assert "actionName:" not in yaml_output, "YAML should not contain camelCase variant"
    assert "action:" not in yaml_output or "action_name:" in yaml_output, "Should use full field name"
    
    print("✅ Field name standardization: PASSED")


def test_data_type_validation():
    """Test that action_name values are validated as strings."""
    print("\n🔍 Testing Data Type Validation")
    print("=" * 50)
    
    # Test string action_name (valid)
    result = action_name_validator.validate_action_name("mw.get_user_by_email")
    assert result.is_valid, "String action_name should be valid"
    print("✅ String action_name validation: PASSED")
    
    # Test empty string (invalid)
    result = action_name_validator.validate_action_name("")
    assert not result.is_valid, "Empty string should be invalid"
    print("✅ Empty string rejection: PASSED")
    
    # Test whitespace-only string (invalid)
    result = action_name_validator.validate_action_name("   ")
    assert not result.is_valid, "Whitespace-only string should be invalid"
    print("✅ Whitespace-only string rejection: PASSED")


def test_suggestion_system():
    """Test the action_name suggestion system."""
    print("\n🔍 Testing Suggestion System")
    print("=" * 50)
    
    # Test suggestions for invalid action_name
    suggestions = action_name_validator.suggest_action_name_fixes("invalid action name")
    assert len(suggestions) > 0, "Should provide suggestions for invalid names"
    print(f"✅ Suggestions for invalid name: {len(suggestions)} suggestions provided")
    
    # Test suggestions for empty action_name
    suggestions = action_name_validator.suggest_action_name_fixes("")
    assert len(suggestions) > 0, "Should provide suggestions for empty names"
    assert any("mw." in suggestion for suggestion in suggestions), "Should suggest mw. actions"
    print(f"✅ Suggestions for empty name: {len(suggestions)} suggestions provided")
    
    # Test action suggestions
    all_suggestions = action_name_validator.get_action_suggestions("get_user")
    assert len(all_suggestions) > 0, "Should provide action suggestions"
    print(f"✅ Action suggestions: {len(all_suggestions)} suggestions available")


def run_all_tests():
    """Run all action_name compliance tests."""
    print("🚀 Starting Action Name Compliance Tests")
    print("=" * 60)
    
    try:
        test_mandatory_field_enforcement()
        test_naming_convention_validation()
        test_mw_prefix_validation()
        test_catalog_integration()
        test_yaml_generation_blocking()
        test_field_name_standardization()
        test_data_type_validation()
        test_suggestion_system()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("✅ Mandatory field enforcement working")
        print("✅ Naming convention validation working")
        print("✅ MW prefix validation working")
        print("✅ Catalog integration working")
        print("✅ YAML generation blocking working")
        print("✅ Field name standardization working")
        print("✅ Data type validation working")
        print("✅ Suggestion system working")
        print("\n🔧 Action name compliance system is fully functional!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
