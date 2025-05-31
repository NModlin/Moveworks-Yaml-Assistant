#!/usr/bin/env python3
"""
Edge Case Testing for YAML Generation

This script tests specific edge cases and potential issues in YAML generation
that might not be caught by basic testing.
"""

import sys
import yaml
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep,
    TryCatchStep, CatchBlock, ParallelForLoop
)
from yaml_generator import generate_yaml_string, workflow_to_yaml_dict, step_to_yaml_dict


def test_empty_and_none_values():
    """Test handling of empty and None values."""
    print("=" * 60)
    print("TESTING EMPTY AND NONE VALUES")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Empty strings
    print("\n1. Testing empty string handling...")
    
    empty_action = ActionStep(
        action_name="",
        output_key="",
        input_args={},
        delay_config={},
        progress_updates={}
    )
    
    try:
        action_dict = step_to_yaml_dict(empty_action)
        yaml_output = generate_yaml_string(Workflow(steps=[empty_action]))
        print("  ✓ Empty strings handled without errors")
        
        # Check if empty fields are included
        action_yaml = action_dict.get('action', {})
        if action_yaml.get('action_name') == '':
            print("  ⚠ Empty action_name included in YAML (may cause validation issues)")
        if action_yaml.get('output_key') == '':
            print("  ⚠ Empty output_key included in YAML (may cause validation issues)")
            
    except Exception as e:
        issues_found.append(f"Empty string handling failed: {e}")
    
    # Test 2: None values
    print("\n2. Testing None value handling...")
    
    none_action = ActionStep(
        action_name="test_action",
        output_key="result",
        input_args=None,
        delay_config=None,
        progress_updates=None,
        description=None
    )
    
    try:
        action_dict = step_to_yaml_dict(none_action)
        yaml_output = generate_yaml_string(Workflow(steps=[none_action]))
        print("  ✓ None values handled without errors")
        
        # Check if None fields are excluded
        action_yaml = action_dict.get('action', {})
        if 'input_args' in action_yaml and action_yaml['input_args'] is None:
            issues_found.append("None input_args should be excluded from YAML")
        if 'delay_config' in action_yaml and action_yaml['delay_config'] is None:
            issues_found.append("None delay_config should be excluded from YAML")
            
    except Exception as e:
        issues_found.append(f"None value handling failed: {e}")
    
    return issues_found


def test_field_ordering():
    """Test field ordering in generated YAML."""
    print("\n" + "=" * 60)
    print("TESTING FIELD ORDERING")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Action step field order
    print("\n1. Testing ActionStep field ordering...")
    
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"},
        description="Get user information",
        delay_config={"delay_seconds": 5},
        progress_updates={"on_pending": "Loading..."}
    )
    
    action_dict = step_to_yaml_dict(action_step)
    action_yaml = action_dict.get('action', {})
    field_order = list(action_yaml.keys())
    
    # Expected order: action_name, output_key, input_args, description, delay_config, progress_updates
    expected_order = ['action_name', 'output_key']
    
    # Check if mandatory fields come first
    if field_order[:2] != expected_order:
        issues_found.append(f"ActionStep field order issue: expected {expected_order} first, got {field_order[:2]}")
    else:
        print(f"  ✓ Mandatory fields in correct order: {field_order[:2]}")
    
    print(f"  ✓ Full field order: {field_order}")
    
    # Test 2: Script step field order
    print("\n2. Testing ScriptStep field ordering...")
    
    script_step = ScriptStep(
        code="return 'test'",
        output_key="result",
        input_args={"input": "data.value"},
        description="Test script"
    )
    
    script_dict = step_to_yaml_dict(script_step)
    script_yaml = script_dict.get('script', {})
    script_field_order = list(script_yaml.keys())
    
    # Expected order: code, output_key, input_args, description
    script_expected = ['code', 'output_key']
    
    if script_field_order[:2] != script_expected:
        issues_found.append(f"ScriptStep field order issue: expected {script_expected} first, got {script_field_order[:2]}")
    else:
        print(f"  ✓ Script mandatory fields in correct order: {script_field_order[:2]}")
    
    print(f"  ✓ Full script field order: {script_field_order}")
    
    return issues_found


def test_yaml_syntax_validity():
    """Test that generated YAML is syntactically valid."""
    print("\n" + "=" * 60)
    print("TESTING YAML SYNTAX VALIDITY")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Complex workflow YAML validity
    print("\n1. Testing complex workflow YAML validity...")
    
    complex_workflow = Workflow(steps=[
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.input_email"},
            delay_config={"delay_seconds": 10}
        ),
        ScriptStep(
            code="""
# Multi-line script with special characters
user_name = data.user_info.user.name
special_chars = "quotes 'and' \"double quotes\""
result = {
    "greeting": f"Hello, {user_name}!",
    "special": special_chars
}
return result
            """.strip(),
            output_key="processed_data"
        ),
        SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.user_info.status == 'active'",
                    steps=[ActionStep(action_name="activate_user", output_key="activation_result")]
                )
            ],
            default_case=DefaultCase(steps=[
                ActionStep(action_name="deactivate_user", output_key="deactivation_result")
            ])
        )
    ])
    
    try:
        yaml_output = generate_yaml_string(complex_workflow, "complex_test_action")
        
        # Try to parse the generated YAML
        parsed_yaml = yaml.safe_load(yaml_output)
        
        if parsed_yaml is None:
            issues_found.append("Generated YAML parsed as None")
        else:
            print("  ✓ Complex workflow YAML is syntactically valid")
            print(f"  ✓ Parsed YAML has {len(parsed_yaml)} top-level keys")
            
            # Check structure
            if 'action_name' not in parsed_yaml:
                issues_found.append("Parsed YAML missing action_name")
            if 'steps' not in parsed_yaml:
                issues_found.append("Parsed YAML missing steps")
            elif not isinstance(parsed_yaml['steps'], list):
                issues_found.append("Parsed YAML steps is not a list")
            else:
                print(f"  ✓ Parsed YAML has {len(parsed_yaml['steps'])} steps")
        
    except yaml.YAMLError as e:
        issues_found.append(f"Generated YAML is not valid: {e}")
    except Exception as e:
        issues_found.append(f"YAML generation failed: {e}")
    
    return issues_found


def test_special_characters():
    """Test handling of special characters in YAML."""
    print("\n" + "=" * 60)
    print("TESTING SPECIAL CHARACTER HANDLING")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Special characters in strings
    print("\n1. Testing special characters in field values...")
    
    special_chars_workflow = Workflow(steps=[
        ActionStep(
            action_name="test_special_chars",
            output_key="special_result",
            input_args={
                "quotes": "String with 'single' and \"double\" quotes",
                "newlines": "String with\nnewlines\nand\ttabs",
                "unicode": "Unicode: 🚀 ñ ü ß",
                "backslashes": "Path\\with\\backslashes",
                "colon": "key:value pair"
            }
        )
    ])
    
    try:
        yaml_output = generate_yaml_string(special_chars_workflow)
        parsed_yaml = yaml.safe_load(yaml_output)
        
        print("  ✓ Special characters handled without errors")
        
        # Check if special characters are preserved
        input_args = parsed_yaml['steps'][0]['action']['input_args']
        
        if 'quotes' in input_args and "'" in input_args['quotes'] and '"' in input_args['quotes']:
            print("  ✓ Quotes preserved correctly")
        else:
            issues_found.append("Quotes not preserved correctly in YAML")
            
        if 'unicode' in input_args and '🚀' in input_args['unicode']:
            print("  ✓ Unicode characters preserved")
        else:
            issues_found.append("Unicode characters not preserved in YAML")
        
    except Exception as e:
        issues_found.append(f"Special character handling failed: {e}")
    
    return issues_found


def main():
    """Run edge case testing."""
    print("MOVEWORKS YAML ASSISTANT - EDGE CASE TESTING")
    print("=" * 80)
    
    all_issues = []
    
    # Run all edge case tests
    all_issues.extend(test_empty_and_none_values())
    all_issues.extend(test_field_ordering())
    all_issues.extend(test_yaml_syntax_validity())
    all_issues.extend(test_special_characters())
    
    # Summary
    print("\n" + "=" * 80)
    print("EDGE CASE TESTING SUMMARY")
    print("=" * 80)
    
    if all_issues:
        print(f"\n❌ FOUND {len(all_issues)} EDGE CASE ISSUES:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
    else:
        print("\n✅ NO EDGE CASE ISSUES FOUND")
        print("✅ YAML generation handles edge cases correctly")
    
    print(f"\nTotal edge case issues: {len(all_issues)}")
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
