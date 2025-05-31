#!/usr/bin/env python3
"""
Comprehensive test suite for APIthon validation and YAML generation.

This script tests the enhanced APIthon validation system to ensure strict compliance
with APIthon restrictions and proper YAML formatting for script blocks.
"""

import sys
from core_structures import ScriptStep, Workflow, DataContext
from apiton_validator import (
    validate_apiton_code_restrictions, validate_apiton_syntax,
    validate_script_step_structure, comprehensive_validate_apiton_script,
    validate_workflow_apiton_scripts, generate_apiton_examples
)
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate


def test_valid_apiton_scripts():
    """Test valid APIthon scripts that should pass validation."""
    print("=== Testing Valid APIthon Scripts ===")

    valid_scripts = [
        {
            'name': 'Simple calculation with return',
            'code': '''
result = data.input_value * 2
return {"doubled": result}
            '''.strip(),
            'output_key': 'calculation_result'
        },
        {
            'name': 'Data processing with meta_info',
            'code': '''
user_name = data.user_info.name
user_email = meta_info.user.email_addr
processed = {
    "greeting": f"Hello, {user_name}!",
    "contact": user_email
}
return processed
            '''.strip(),
            'output_key': 'processed_data'
        },
        {
            'name': 'Conditional logic',
            'code': '''
if data.status == "active":
    result = {"message": "User is active", "code": 200}
else:
    result = {"message": "User is inactive", "code": 404}
return result
            '''.strip(),
            'output_key': 'status_result'
        },
        {
            'name': 'List processing',
            'code': '''
items = data.item_list
processed_items = []
for item in items:
    processed_items.append({
        "id": item.get("id"),
        "name": item.get("name", "Unknown")
    })
return {"items": processed_items, "count": len(processed_items)}
            '''.strip(),
            'output_key': 'list_result'
        }
    ]

    all_passed = True
    for script_info in valid_scripts:
        print(f"\nTesting: {script_info['name']}")

        script_step = ScriptStep(
            code=script_info['code'],
            output_key=script_info['output_key'],
            input_args={"user_data": "data.user_info"}
        )

        errors = comprehensive_validate_apiton_script(script_step)

        if errors:
            print(f"  ❌ FAILED - Unexpected errors:")
            for error in errors:
                print(f"    - {error}")
            all_passed = False
        else:
            print(f"  ✅ PASSED")

    return all_passed


def test_invalid_apiton_scripts():
    """Test invalid APIthon scripts that should fail validation."""
    print("\n=== Testing Invalid APIthon Scripts ===")

    invalid_scripts = [
        {
            'name': 'Import statement',
            'code': 'import json\nreturn {}',
            'expected_error': 'Import statements are not allowed'
        },
        {
            'name': 'Class definition',
            'code': 'class MyClass:\n    pass\nreturn {}',
            'expected_error': 'Class definitions are not allowed'
        },
        {
            'name': 'Function definition',
            'code': 'def my_function():\n    return "hello"\nreturn {}',
            'expected_error': 'Function definitions are not allowed'
        },
        {
            'name': 'Private identifier',
            'code': '_private_var = "secret"\nreturn {"value": _private_var}',
            'expected_error': 'Private identifiers'
        },
        {
            'name': 'Eval function',
            'code': 'result = eval("1 + 1")\nreturn {"result": result}',
            'expected_error': 'eval() function is not allowed'
        },
        {
            'name': 'File operations',
            'code': 'with open("file.txt") as f:\n    content = f.read()\nreturn {"content": content}',
            'expected_error': 'File operations are not allowed'
        },
        {
            'name': 'Empty code',
            'code': '',
            'expected_error': 'Script step must have non-empty code'
        },
        {
            'name': 'Invalid output key',
            'code': 'return {}',
            'output_key': '123invalid',
            'expected_error': 'must be a valid identifier'
        }
    ]

    all_passed = True
    for script_info in invalid_scripts:
        print(f"\nTesting: {script_info['name']}")

        script_step = ScriptStep(
            code=script_info['code'],
            output_key=script_info.get('output_key', 'test_result')
        )

        errors = comprehensive_validate_apiton_script(script_step)

        if not errors:
            print(f"  ❌ FAILED - Expected errors but none found")
            all_passed = False
        else:
            # Check if expected error is found
            expected_found = any(script_info['expected_error'] in error for error in errors)
            if expected_found:
                print(f"  ✅ PASSED - Found expected error: {script_info['expected_error']}")
            else:
                print(f"  ❌ FAILED - Expected error '{script_info['expected_error']}' not found")
                print(f"    Actual errors: {errors}")
                all_passed = False

    return all_passed


def test_yaml_generation():
    """Test YAML generation with proper literal block scalar formatting."""
    print("\n=== Testing YAML Generation ===")

    # Create a script step with multiline code
    script_step = ScriptStep(
        code='''# APIthon script to process user data
user_name = data.user_info.name
processed_result = {
    "greeting": f"Hello, {user_name}!",
    "user_id": data.user_info.id
}
return processed_result''',
        output_key="processed_data",
        input_args={"user_data": "data.user_info"}
    )

    workflow = Workflow(steps=[script_step])

    # Generate YAML
    yaml_output = generate_yaml_string(workflow)

    print("Generated YAML:")
    print(yaml_output)

    # Check for proper formatting
    checks = [
        ('code: |' in yaml_output, "Uses literal block scalar (|) for code"),
        ('output_key: processed_data' in yaml_output, "Contains output_key"),
        ('input_args:' in yaml_output, "Contains input_args"),
        ('user_data: data.user_info' in yaml_output, "Contains input_args mapping")
    ]

    all_passed = True
    for check_passed, description in checks:
        if check_passed:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}")
            all_passed = False

    return all_passed


def test_integration_with_main_validator():
    """Test integration with the main validation system."""
    print("\n=== Testing Integration with Main Validator ===")

    # Create a workflow with both valid and invalid scripts
    valid_script = ScriptStep(
        code='result = data.input_value * 2\nreturn {"doubled": result}',
        output_key="valid_result"
    )

    invalid_script = ScriptStep(
        code='import json\nreturn {}',  # Should be flagged
        output_key="invalid_result"
    )

    workflow = Workflow(steps=[valid_script, invalid_script])
    initial_context = DataContext({"input_value": 42})

    # Run comprehensive validation
    errors = comprehensive_validate(workflow, initial_context)

    print(f"Found {len(errors)} validation errors:")
    for error in errors:
        print(f"  - {error}")

    # Should find APIthon restriction errors
    apiton_errors = [error for error in errors if 'Import statements are not allowed' in error]

    if apiton_errors:
        print("  ✅ APIthon validation integrated successfully")
        return True
    else:
        print("  ❌ APIthon validation not properly integrated")
        return False


def main():
    """Run all APIthon validation tests."""
    print("APIthon Validation Test Suite")
    print("=" * 50)

    test_results = []

    # Run all tests
    test_results.append(("Valid Scripts", test_valid_apiton_scripts()))
    test_results.append(("Invalid Scripts", test_invalid_apiton_scripts()))
    test_results.append(("YAML Generation", test_yaml_generation()))
    test_results.append(("Integration", test_integration_with_main_validator()))

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! APIthon validation is working correctly.")
        return 0
    else:
        print("❌ SOME TESTS FAILED. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
