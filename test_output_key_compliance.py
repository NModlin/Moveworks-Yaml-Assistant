#!/usr/bin/env python3
"""
Comprehensive test for output_key field compliance implementation.

This script tests all aspects of the output_key compliance system including:
- Mandatory field enforcement
- Lowercase snake_case validation
- Uniqueness validation
- YAML generation blocking
- UI validation indicators
"""

import sys
from core_structures import Workflow, ActionStep, ScriptStep, RaiseStep, ForLoopStep
from compliance_validator import compliance_validator
from output_key_validator import output_key_validator
from yaml_generator import generate_yaml_string


def test_mandatory_field_enforcement():
    """Test that mandatory output_key fields are enforced."""
    print("🔍 Testing Mandatory Field Enforcement")
    print("=" * 50)
    
    # Test ActionStep without output_key
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="",  # Empty - should fail
        description="Test action"
    )
    
    workflow = Workflow(steps=[action_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    # Should have mandatory field errors
    assert not result.is_valid, "Workflow should be invalid with empty output_key"
    assert any("output_key" in error.lower() for error in result.mandatory_field_errors), \
        "Should have output_key mandatory field error"
    
    print("✅ ActionStep mandatory field enforcement: PASSED")
    
    # Test ScriptStep without output_key
    script_step = ScriptStep(
        code="return {'result': 'test'}",
        output_key="",  # Empty - should fail
        description="Test script"
    )
    
    workflow = Workflow(steps=[script_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    assert not result.is_valid, "Workflow should be invalid with empty output_key"
    assert any("output_key" in error.lower() for error in result.mandatory_field_errors), \
        "Should have output_key mandatory field error"
    
    print("✅ ScriptStep mandatory field enforcement: PASSED")
    
    # Test RaiseStep without output_key
    raise_step = RaiseStep(
        message="Test error",
        output_key=""  # Empty - should fail
    )
    
    workflow = Workflow(steps=[raise_step])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    assert not result.is_valid, "Workflow should be invalid with empty output_key"
    assert any("output_key" in error.lower() for error in result.mandatory_field_errors), \
        "Should have output_key mandatory field error"
    
    print("✅ RaiseStep mandatory field enforcement: PASSED")


def test_snake_case_validation():
    """Test lowercase_snake_case naming validation."""
    print("\n🔍 Testing Snake Case Validation")
    print("=" * 50)
    
    # Test invalid naming patterns
    invalid_names = [
        "userInfo",      # camelCase
        "UserInfo",      # PascalCase
        "user-info",     # kebab-case
        "user info",     # spaces
        "user.info",     # dots
        "123user",       # starts with number
        "_private",      # starts with underscore
        "USER_INFO",     # all caps
    ]
    
    for invalid_name in invalid_names:
        result = output_key_validator.validate_output_key(invalid_name, "ActionStep")
        assert not result.is_valid, f"'{invalid_name}' should be invalid"
        assert any("snake_case" in error.lower() for error in result.errors), \
            f"'{invalid_name}' should have snake_case error"
        print(f"✅ Invalid name '{invalid_name}': correctly rejected")
    
    # Test valid naming patterns
    valid_names = [
        "user_info",
        "processed_data",
        "api_response",
        "validation_result",
        "result123",
        "user_info_v2",
        "step_result",
        "person_data"
    ]
    
    for valid_name in valid_names:
        result = output_key_validator.validate_output_key(valid_name, "ActionStep")
        assert result.is_valid, f"'{valid_name}' should be valid"
        print(f"✅ Valid name '{valid_name}': correctly accepted")


def test_uniqueness_validation():
    """Test output_key uniqueness validation."""
    print("\n🔍 Testing Uniqueness Validation")
    print("=" * 50)
    
    # Create workflow with duplicate output_keys
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="First action"
    )
    
    action2 = ActionStep(
        action_name="mw.get_user_by_id",
        output_key="user_info",  # Duplicate!
        description="Second action"
    )
    
    workflow = Workflow(steps=[action1, action2])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    assert not result.is_valid, "Workflow should be invalid with duplicate output_keys"
    assert any("duplicate" in error.lower() for error in result.mandatory_field_errors), \
        "Should have duplicate output_key error"
    
    print("✅ Duplicate output_key detection: PASSED")
    
    # Test unique output_keys
    action2.output_key = "user_details"  # Make unique
    
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    # Should pass uniqueness check (may fail other validations)
    duplicate_errors = [error for error in result.mandatory_field_errors 
                       if "duplicate" in error.lower()]
    assert len(duplicate_errors) == 0, "Should not have duplicate errors with unique keys"
    
    print("✅ Unique output_key validation: PASSED")


def test_yaml_generation_blocking():
    """Test that YAML generation is blocked for non-compliant workflows."""
    print("\n🔍 Testing YAML Generation Blocking")
    print("=" * 50)
    
    # Create non-compliant workflow
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="",  # Missing required field
        description="Test action"
    )
    
    workflow = Workflow(steps=[action_step])
    
    # Should raise ValueError when trying to generate YAML
    try:
        yaml_output = generate_yaml_string(workflow, "test_action")
        assert False, "YAML generation should have been blocked"
    except ValueError as e:
        assert "output_key" in str(e).lower(), "Error should mention output_key"
        print("✅ YAML generation blocking: PASSED")
    
    # Test compliant workflow
    action_step.output_key = "user_info"
    
    try:
        yaml_output = generate_yaml_string(workflow, "test_action")
        assert "output_key: user_info" in yaml_output, "YAML should contain output_key"
        print("✅ Compliant YAML generation: PASSED")
    except Exception as e:
        assert False, f"Compliant workflow should generate YAML: {e}"


def test_data_reference_generation():
    """Test data reference generation for downstream steps."""
    print("\n🔍 Testing Data Reference Generation")
    print("=" * 50)
    
    # Test valid output_key generates correct data reference
    result = output_key_validator.validate_output_key("user_info", "ActionStep")
    
    assert result.is_valid, "Valid output_key should pass validation"
    assert result.data_reference == "data.user_info", "Should generate correct data reference"
    
    print("✅ Data reference generation: PASSED")
    
    # Test workflow-level data reference suggestions
    action1 = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user"
    )
    
    script1 = ScriptStep(
        code="return {'processed': True}",
        output_key="processed_data",
        description="Process data"
    )
    
    workflow = Workflow(steps=[action1, script1])
    suggestions = output_key_validator.generate_data_reference_suggestions(workflow)
    
    # Second step should have access to first step's output
    step_1_suggestions = suggestions[1]
    assert "data.user_info" in step_1_suggestions, "Should suggest previous step's output_key"
    
    print("✅ Workflow data reference suggestions: PASSED")


def test_reserved_names():
    """Test reserved output_key name validation."""
    print("\n🔍 Testing Reserved Names Validation")
    print("=" * 50)
    
    reserved_names = ['data', 'input', 'output', 'error', 'user', 'meta_info']
    
    for reserved_name in reserved_names:
        result = output_key_validator.validate_output_key(reserved_name, "ActionStep")
        assert not result.is_valid, f"Reserved name '{reserved_name}' should be invalid"
        assert any("reserved" in error.lower() for error in result.errors), \
            f"'{reserved_name}' should have reserved name error"
        print(f"✅ Reserved name '{reserved_name}': correctly rejected")


def run_all_tests():
    """Run all output_key compliance tests."""
    print("🚀 Starting Output Key Compliance Tests")
    print("=" * 60)
    
    try:
        test_mandatory_field_enforcement()
        test_snake_case_validation()
        test_uniqueness_validation()
        test_yaml_generation_blocking()
        test_data_reference_generation()
        test_reserved_names()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("✅ Mandatory field enforcement working")
        print("✅ Snake case validation working")
        print("✅ Uniqueness validation working")
        print("✅ YAML generation blocking working")
        print("✅ Data reference generation working")
        print("✅ Reserved name validation working")
        print("\n🔧 Output key compliance system is fully functional!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
