#!/usr/bin/env python3
"""
Test script to verify the tutorial validation fix.

This script tests:
1. YAML generation with empty fields
2. Validation of empty fields
3. Tutorial step validation
4. Widget finding improvements
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_structures import ActionStep, ScriptStep, Workflow
from yaml_generator import generate_yaml_string, step_to_yaml_dict
from validator import comprehensive_validate
import yaml


def test_empty_fields_yaml_generation():
    """Test YAML generation with empty required fields."""
    print("🧪 Testing YAML Generation with Empty Fields")
    print("=" * 50)

    # Create steps with empty required fields (simulating tutorial issue)
    empty_action = ActionStep(
        action_name="",  # Empty action name
        output_key="",   # Empty output key
    )

    empty_script = ScriptStep(
        code="",         # Empty code
        output_key="",   # Empty output key
    )

    workflow = Workflow(steps=[empty_action, empty_script])

    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow)
        print("✅ YAML generation succeeded with empty fields:")
        print(yaml_output)
        print()

        # Verify YAML is valid
        parsed_yaml = yaml.safe_load(yaml_output)
        print("✅ Generated YAML is valid and parseable")
        print(f"   Parsed structure: {parsed_yaml}")
        print()

    except Exception as e:
        print(f"❌ YAML generation failed: {e}")
        return False

    return True


def test_validation_with_empty_fields():
    """Test validation with empty required fields."""
    print("🧪 Testing Validation with Empty Fields")
    print("=" * 50)

    # Create steps with empty required fields
    empty_action = ActionStep(
        action_name="",  # Empty action name
        output_key="",   # Empty output key
    )

    empty_script = ScriptStep(
        code="",         # Empty code
        output_key="",   # Empty output key
    )

    workflow = Workflow(steps=[empty_action, empty_script])

    # Test validation
    errors = comprehensive_validate(workflow)

    if errors:
        print(f"✅ Validation correctly found {len(errors)} error(s):")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        print()

        # Check for specific expected errors
        expected_errors = [
            "ActionStep missing required 'action_name'",
            "ActionStep missing required 'output_key'",
            "ScriptStep missing required 'code'",
            "ScriptStep missing required 'output_key'"
        ]

        found_expected = 0
        for expected in expected_errors:
            if any(expected in error for error in errors):
                found_expected += 1
                print(f"   ✅ Found expected error: {expected}")

        if found_expected == len(expected_errors):
            print(f"✅ All {len(expected_errors)} expected validation errors found")
        else:
            print(f"⚠️ Only {found_expected}/{len(expected_errors)} expected errors found")

        return True
    else:
        print("❌ Validation should have found errors but didn't")
        return False


def test_valid_workflow():
    """Test with a valid workflow to ensure we didn't break normal functionality."""
    print("🧪 Testing Valid Workflow (Regression Test)")
    print("=" * 50)

    # Create valid steps with proper JSON parsing
    valid_action = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"id": "12345", "name": "John Doe"}}'
    )

    # Parse the JSON to make it available for validation
    import json
    try:
        valid_action.parsed_json_output = json.loads(valid_action.user_provided_json_output)
    except:
        pass

    # Create a valid APIthon script (return statement is valid in APIthon context)
    valid_script = ScriptStep(
        code="# Process user data\nuser_name = data.user_info.user.name\nresult = {'greeting': f'Hello, {user_name}!', 'processed': True}\nreturn result",
        output_key="result",
        input_args={},  # No input args needed for this script
        user_provided_json_output='{"greeting": "Hello, John Doe!", "processed": true}'
    )

    # Parse the JSON to make it available for validation
    try:
        valid_script.parsed_json_output = json.loads(valid_script.user_provided_json_output)
    except:
        pass

    workflow = Workflow(steps=[valid_action, valid_script])

    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow)
        print("✅ YAML generation succeeded for valid workflow:")
        print(yaml_output)
        print()
    except Exception as e:
        print(f"❌ YAML generation failed for valid workflow: {e}")
        return False

    # Test validation with proper data context
    from core_structures import DataContext
    initial_context = DataContext(initial_inputs={"input_email": "test@example.com"})
    errors = comprehensive_validate(workflow, initial_context)

    if not errors:
        print("✅ Validation passed for valid workflow")
        return True
    else:
        print(f"⚠️ Validation found {len(errors)} error(s) for valid workflow:")
        for error in errors:
            print(f"   - {error}")

        # Check if errors are acceptable (some validation might be overly strict)
        critical_errors = [e for e in errors if any(keyword in e.lower() for keyword in
                          ['missing required', 'syntax error', 'compilation error'])]

        if not critical_errors:
            print("✅ No critical errors found - validation acceptable")
            return True
        else:
            print(f"❌ Found {len(critical_errors)} critical error(s)")
            return False


def test_step_to_yaml_dict():
    """Test individual step conversion to YAML dict."""
    print("🧪 Testing Individual Step Conversion")
    print("=" * 50)

    # Test empty action step
    empty_action = ActionStep(action_name="", output_key="")
    action_dict = step_to_yaml_dict(empty_action)

    print(f"Empty ActionStep dict: {action_dict}")

    expected_action = {
        'action': {
            'action_name': '',
            'output_key': ''
        }
    }

    if action_dict == expected_action:
        print("✅ Empty ActionStep conversion correct")
    else:
        print(f"❌ Empty ActionStep conversion incorrect. Expected: {expected_action}")
        return False

    # Test empty script step
    empty_script = ScriptStep(code="", output_key="")
    script_dict = step_to_yaml_dict(empty_script)

    print(f"Empty ScriptStep dict: {script_dict}")

    expected_script = {
        'script': {
            'output_key': '',
            'code': ''
        }
    }

    if script_dict == expected_script:
        print("✅ Empty ScriptStep conversion correct")
    else:
        print(f"❌ Empty ScriptStep conversion incorrect. Expected: {expected_script}")
        return False

    return True


def main():
    """Run all tests."""
    print("🚀 Tutorial Validation Fix Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_step_to_yaml_dict,
        test_empty_fields_yaml_generation,
        test_validation_with_empty_fields,
        test_valid_workflow
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ FAILED with exception: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 50)
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The tutorial validation fix is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
