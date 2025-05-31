#!/usr/bin/env python3
"""
Comprehensive YAML Generation Issues Test

This script identifies and tests specific issues in the Moveworks YAML Assistant's
YAML generation logic, focusing on:
1. Field name accuracy and compliance
2. Data structure type validation
3. Steps key implementation logic
4. Integration with compliance systems
5. Specific bug investigation
"""

import sys
import yaml
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep,
    TryCatchStep, CatchBlock, ParallelForLoop
)
from yaml_generator import (
    generate_yaml_string, workflow_to_yaml_dict, step_to_yaml_dict,
    _is_dsl_expression, _ensure_dsl_string_quoting
)
from compliance_validator import compliance_validator


def test_field_name_accuracy():
    """Test field name accuracy and compliance."""
    print("=" * 60)
    print("TESTING FIELD NAME ACCURACY AND COMPLIANCE")
    print("=" * 60)

    issues_found = []

    # Test 1: Action step field names
    print("\n1. Testing ActionStep field names...")
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        delay_config={"delay_seconds": 10},
        progress_updates={"on_pending": "Loading..."}
    )

    action_dict = step_to_yaml_dict(action_step)
    action_yaml = action_dict.get('action', {})

    # Check for correct field names
    expected_fields = ['action_name', 'output_key', 'input_args', 'delay_config', 'progress_updates']
    for field in expected_fields:
        if field not in action_yaml:
            issues_found.append(f"ActionStep missing field: {field}")
        else:
            print(f"  ✓ {field}: {action_yaml[field]}")

    # Check for typos in field names
    actual_fields = list(action_yaml.keys())
    for field in actual_fields:
        if field not in expected_fields and field != 'description':
            issues_found.append(f"ActionStep unexpected field: {field}")

    # Test 2: Script step field names
    print("\n2. Testing ScriptStep field names...")
    script_step = ScriptStep(
        code="result = data.input * 2\nreturn result",
        output_key="calculation_result",
        input_args={"input_value": "data.input"}
    )

    script_dict = step_to_yaml_dict(script_step)
    script_yaml = script_dict.get('script', {})

    expected_script_fields = ['code', 'output_key', 'input_args']
    for field in expected_script_fields:
        if field not in script_yaml:
            issues_found.append(f"ScriptStep missing field: {field}")
        else:
            print(f"  ✓ {field}: {type(script_yaml[field])}")

    # Test 3: Control flow field names
    print("\n3. Testing control flow field names...")

    # Switch step
    switch_step = SwitchStep(
        cases=[SwitchCase(condition="data.status == 'active'", steps=[action_step])],
        output_key="switch_result"
    )
    switch_dict = step_to_yaml_dict(switch_step)

    if 'switch' not in switch_dict:
        issues_found.append("SwitchStep missing 'switch' key")
    elif 'cases' not in switch_dict['switch']:
        issues_found.append("SwitchStep missing 'cases' field")
    else:
        print(f"  ✓ SwitchStep structure: {list(switch_dict.keys())}")

    # For loop step
    for_step = ForLoopStep(
        each="item",
        in_source="data.items",
        output_key="loop_results",
        steps=[action_step]
    )
    for_dict = step_to_yaml_dict(for_step)

    if 'for' not in for_dict:
        issues_found.append("ForLoopStep missing 'for' key")
    else:
        for_yaml = for_dict['for']
        expected_for_fields = ['each', 'in', 'output_key', 'steps']
        for field in expected_for_fields:
            if field not in for_yaml:
                issues_found.append(f"ForLoopStep missing field: {field}")
            else:
                print(f"  ✓ ForLoop {field}: {type(for_yaml[field])}")

    return issues_found


def test_data_structure_types():
    """Test data structure type validation."""
    print("\n" + "=" * 60)
    print("TESTING DATA STRUCTURE TYPE VALIDATION")
    print("=" * 60)

    issues_found = []

    # Test 1: Steps field should always be a list
    print("\n1. Testing steps field type consistency...")

    workflow = Workflow(steps=[
        ActionStep(action_name="test_action", output_key="result"),
        ScriptStep(code="return 'test'", output_key="script_result")
    ])

    workflow_dict = workflow_to_yaml_dict(workflow)

    if 'steps' not in workflow_dict:
        issues_found.append("Workflow missing 'steps' field")
    elif not isinstance(workflow_dict['steps'], list):
        issues_found.append(f"Workflow 'steps' should be list, got {type(workflow_dict['steps'])}")
    else:
        print(f"  ✓ Workflow steps type: {type(workflow_dict['steps'])}")
        print(f"  ✓ Steps count: {len(workflow_dict['steps'])}")

    # Test 2: input_args should be dict
    print("\n2. Testing input_args type enforcement...")

    action_with_args = ActionStep(
        action_name="test_action",
        output_key="result",
        input_args={"key1": "value1", "key2": "data.input_value"}
    )

    action_dict = step_to_yaml_dict(action_with_args)
    input_args = action_dict.get('action', {}).get('input_args')

    if not isinstance(input_args, dict):
        issues_found.append(f"input_args should be dict, got {type(input_args)}")
    else:
        print(f"  ✓ input_args type: {type(input_args)}")
        print(f"  ✓ input_args content: {input_args}")

    return issues_found


def test_steps_key_logic():
    """Test steps key implementation logic."""
    print("\n" + "=" * 60)
    print("TESTING STEPS KEY IMPLEMENTATION LOGIC")
    print("=" * 60)

    issues_found = []

    # Test 1: Single expression workflow
    print("\n1. Testing single expression workflow...")

    single_workflow = Workflow(steps=[
        ActionStep(action_name="single_action", output_key="result")
    ])

    single_dict = workflow_to_yaml_dict(single_workflow)

    if 'steps' not in single_dict:
        issues_found.append("Single expression workflow missing 'steps' key")
    elif not isinstance(single_dict['steps'], list):
        issues_found.append("Single expression 'steps' should be list")
    elif len(single_dict['steps']) != 1:
        issues_found.append(f"Single expression should have 1 step, got {len(single_dict['steps'])}")
    else:
        print(f"  ✓ Single expression properly wrapped in steps list")
        print(f"  ✓ Steps count: {len(single_dict['steps'])}")

    # Test 2: Multiple expression workflow
    print("\n2. Testing multiple expression workflow...")

    multi_workflow = Workflow(steps=[
        ActionStep(action_name="action1", output_key="result1"),
        ScriptStep(code="return 'test'", output_key="result2"),
        ActionStep(action_name="action2", output_key="result3")
    ])

    multi_dict = workflow_to_yaml_dict(multi_workflow)

    if len(multi_dict['steps']) != 3:
        issues_found.append(f"Multiple expression should have 3 steps, got {len(multi_dict['steps'])}")
    else:
        print(f"  ✓ Multiple expressions properly wrapped in steps list")
        print(f"  ✓ Steps count: {len(multi_dict['steps'])}")

    # Test 3: Nested steps in control flow
    print("\n3. Testing nested steps in control flow...")

    nested_workflow = Workflow(steps=[
        SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.status == 'active'",
                    steps=[
                        ActionStep(action_name="nested_action1", output_key="nested1"),
                        ActionStep(action_name="nested_action2", output_key="nested2")
                    ]
                )
            ],
            default_case=DefaultCase(steps=[
                ActionStep(action_name="default_action", output_key="default_result")
            ])
        )
    ])

    nested_dict = workflow_to_yaml_dict(nested_workflow)
    switch_cases = nested_dict['steps'][0]['switch']['cases']

    if not isinstance(switch_cases[0]['steps'], list):
        issues_found.append("Switch case steps should be list")
    elif len(switch_cases[0]['steps']) != 2:
        issues_found.append(f"Switch case should have 2 steps, got {len(switch_cases[0]['steps'])}")
    else:
        print(f"  ✓ Switch case steps properly formatted as list")
        print(f"  ✓ Case steps count: {len(switch_cases[0]['steps'])}")

    default_steps = nested_dict['steps'][0]['switch']['default']['steps']
    if not isinstance(default_steps, list):
        issues_found.append("Switch default steps should be list")
    else:
        print(f"  ✓ Switch default steps properly formatted as list")

    return issues_found


def test_dsl_integration():
    """Test integration with DSL string formatting."""
    print("\n" + "=" * 60)
    print("TESTING DSL STRING FORMATTING INTEGRATION")
    print("=" * 60)

    issues_found = []

    # Test 1: DSL expression detection
    print("\n1. Testing DSL expression detection...")

    test_cases = [
        ("data.user_info.email", True),
        ("meta_info.user.name", True),
        ("data.status == 'active'", True),
        ("$CONCAT(['Hello', 'World'])", True),
        ("regular_string", False),
        ("123", False),
        ("", False)
    ]

    for test_value, expected in test_cases:
        result = _is_dsl_expression(test_value)
        if result != expected:
            issues_found.append(f"DSL detection failed for '{test_value}': expected {expected}, got {result}")
        else:
            print(f"  ✓ '{test_value}' -> {result}")

    # Test 2: DSL string quoting in YAML
    print("\n2. Testing DSL string quoting in generated YAML...")

    workflow_with_dsl = Workflow(steps=[
        ActionStep(
            action_name="test_action",
            output_key="result",
            input_args={
                "email": "data.user_info.email",
                "condition": "data.status == 'active'",
                "regular_field": "normal_value"
            }
        )
    ])

    yaml_output = generate_yaml_string(workflow_with_dsl)

    # Check if DSL expressions are properly quoted
    if '"data.user_info.email"' not in yaml_output:
        issues_found.append("DSL expression 'data.user_info.email' not properly quoted in YAML")
    else:
        print("  ✓ data.user_info.email properly quoted")

    if '"data.status == \'active\'"' not in yaml_output and '"data.status == \'active\'"' not in yaml_output:
        issues_found.append("DSL expression with condition not properly quoted in YAML")
    else:
        print("  ✓ condition expression properly quoted")

    return issues_found


def test_compliance_integration():
    """Test integration with compliance validation."""
    print("\n" + "=" * 60)
    print("TESTING COMPLIANCE VALIDATION INTEGRATION")
    print("=" * 60)

    issues_found = []

    # Test 1: Valid workflow should pass compliance
    print("\n1. Testing valid workflow compliance...")

    valid_workflow = Workflow(steps=[
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.input_email"}
        ),
        ScriptStep(
            code="result = data.user_info.name\nreturn result",
            output_key="processed_name"
        )
    ])

    compliance_result = compliance_validator.validate_workflow_compliance(valid_workflow, "test_action")

    if not compliance_result.is_valid:
        issues_found.append("Valid workflow failed compliance validation")
        for error in compliance_result.errors + compliance_result.mandatory_field_errors + compliance_result.field_naming_errors:
            issues_found.append(f"  Compliance error: {error}")
    else:
        print("  ✓ Valid workflow passes compliance validation")

    # Test 2: Invalid workflow should fail compliance
    print("\n2. Testing invalid workflow compliance...")

    invalid_workflow = Workflow(steps=[
        ActionStep(
            action_name="",  # Empty action name
            output_key="userInfo",  # Wrong naming convention
            input_args={"userEmail": "data.input_email"}  # Wrong naming convention
        )
    ])

    invalid_compliance = compliance_validator.validate_workflow_compliance(invalid_workflow, "")

    if invalid_compliance.is_valid:
        issues_found.append("Invalid workflow incorrectly passed compliance validation")
    else:
        print("  ✓ Invalid workflow correctly fails compliance validation")
        print(f"  ✓ Found {len(invalid_compliance.mandatory_field_errors)} mandatory field errors")
        print(f"  ✓ Found {len(invalid_compliance.field_naming_errors)} field naming errors")

    return issues_found


def main():
    """Run comprehensive YAML generation issue testing."""
    print("MOVEWORKS YAML ASSISTANT - COMPREHENSIVE YAML GENERATION REVIEW")
    print("=" * 80)

    all_issues = []

    # Run all tests
    all_issues.extend(test_field_name_accuracy())
    all_issues.extend(test_data_structure_types())
    all_issues.extend(test_steps_key_logic())
    all_issues.extend(test_dsl_integration())
    all_issues.extend(test_compliance_integration())

    # Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE REVIEW SUMMARY")
    print("=" * 80)

    if all_issues:
        print(f"\n❌ FOUND {len(all_issues)} ISSUES:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
        print("✅ YAML generation logic appears to be working correctly")

    print(f"\nTotal issues identified: {len(all_issues)}")
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
