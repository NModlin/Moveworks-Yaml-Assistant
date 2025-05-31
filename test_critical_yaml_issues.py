#!/usr/bin/env python3
"""
Critical YAML Generation Issues Test

This script specifically tests for the critical issues mentioned in the requirements:
1. Field name typos and accuracy
2. Type mismatches in data structures
3. Steps key implementation inconsistencies
4. Integration issues with compliance systems
"""

import sys
import yaml
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep,
    TryCatchStep, CatchBlock, ParallelForLoop
)
from yaml_generator import generate_yaml_string, workflow_to_yaml_dict, step_to_yaml_dict
from compliance_validator import compliance_validator


def test_critical_field_names():
    """Test for critical field name issues mentioned in requirements."""
    print("=" * 60)
    print("TESTING CRITICAL FIELD NAME ACCURACY")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Check for specific field name typos mentioned
    print("\n1. Checking for critical field name typos...")
    
    # Create comprehensive test cases for all step types
    test_steps = [
        ActionStep(
            action_name="test_action",
            output_key="result",
            input_args={"test": "value"},
            delay_config={"delay_seconds": 5},
            progress_updates={"on_pending": "Loading"}
        ),
        ScriptStep(
            code="return 'test'",
            output_key="script_result",
            input_args={"input": "data.value"}
        ),
        TryCatchStep(
            try_steps=[ActionStep(action_name="try_action", output_key="try_result")],
            catch_block=CatchBlock(
                on_status_code=[400, 404, 500],
                steps=[ActionStep(action_name="catch_action", output_key="catch_result")]
            )
        )
    ]
    
    # Check each step for correct field names
    critical_fields = {
        'ActionStep': ['action_name', 'output_key', 'input_args', 'delay_config', 'progress_updates'],
        'ScriptStep': ['code', 'output_key', 'input_args'],
        'TryCatchStep': ['try_catch']
    }
    
    for step in test_steps:
        step_type = type(step).__name__
        step_dict = step_to_yaml_dict(step)
        
        if step_type == 'ActionStep':
            action_fields = step_dict.get('action', {})
            for field in critical_fields['ActionStep']:
                if field in action_fields:
                    print(f"  ✓ ActionStep.{field} correctly named")
                elif field == 'input_args' and step.input_args:
                    issues_found.append(f"ActionStep missing {field} when it should be present")
                elif field == 'delay_config' and step.delay_config:
                    issues_found.append(f"ActionStep missing {field} when it should be present")
                elif field == 'progress_updates' and step.progress_updates:
                    issues_found.append(f"ActionStep missing {field} when it should be present")
        
        elif step_type == 'ScriptStep':
            script_fields = step_dict.get('script', {})
            for field in critical_fields['ScriptStep']:
                if field in script_fields:
                    print(f"  ✓ ScriptStep.{field} correctly named")
                else:
                    issues_found.append(f"ScriptStep missing mandatory field: {field}")
        
        elif step_type == 'TryCatchStep':
            if 'try_catch' in step_dict:
                print(f"  ✓ TryCatchStep.try_catch correctly named")
                try_catch_fields = step_dict['try_catch']
                
                # Check for 'try' and 'catch' sub-fields
                if 'try' not in try_catch_fields:
                    issues_found.append("TryCatchStep missing 'try' field")
                if 'catch' not in try_catch_fields:
                    issues_found.append("TryCatchStep missing 'catch' field")
                else:
                    catch_fields = try_catch_fields['catch']
                    if 'on_status_code' in catch_fields:
                        print(f"  ✓ TryCatchStep.catch.on_status_code correctly named")
                    if 'steps' in catch_fields:
                        print(f"  ✓ TryCatchStep.catch.steps correctly named")
            else:
                issues_found.append("TryCatchStep missing 'try_catch' key")
    
    return issues_found


def test_data_type_consistency():
    """Test for data type consistency issues."""
    print("\n" + "=" * 60)
    print("TESTING DATA TYPE CONSISTENCY")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Steps field must always be list
    print("\n1. Testing steps field type consistency...")
    
    workflows = [
        Workflow(steps=[ActionStep(action_name="single", output_key="result")]),  # Single step
        Workflow(steps=[  # Multiple steps
            ActionStep(action_name="first", output_key="result1"),
            ActionStep(action_name="second", output_key="result2")
        ])
    ]
    
    for i, workflow in enumerate(workflows):
        workflow_dict = workflow_to_yaml_dict(workflow)
        steps = workflow_dict.get('steps')
        
        if not isinstance(steps, list):
            issues_found.append(f"Workflow {i+1}: steps should be list, got {type(steps)}")
        else:
            print(f"  ✓ Workflow {i+1}: steps is correctly a list with {len(steps)} items")
    
    # Test 2: input_args and delay_config must be dicts
    print("\n2. Testing input_args and delay_config type enforcement...")
    
    action_with_complex_args = ActionStep(
        action_name="complex_action",
        output_key="result",
        input_args={"string_arg": "value", "number_arg": 42, "bool_arg": True},
        delay_config={"delay_seconds": 10, "max_retries": 3, "exponential_backoff": True}
    )
    
    action_dict = step_to_yaml_dict(action_with_complex_args)
    action_yaml = action_dict.get('action', {})
    
    input_args = action_yaml.get('input_args')
    if not isinstance(input_args, dict):
        issues_found.append(f"input_args should be dict, got {type(input_args)}")
    else:
        print(f"  ✓ input_args is correctly a dict with {len(input_args)} keys")
    
    delay_config = action_yaml.get('delay_config')
    if not isinstance(delay_config, dict):
        issues_found.append(f"delay_config should be dict, got {type(delay_config)}")
    else:
        print(f"  ✓ delay_config is correctly a dict with {len(delay_config)} keys")
        
        # Check delay_seconds is integer
        delay_seconds = delay_config.get('delay_seconds')
        if not isinstance(delay_seconds, int):
            issues_found.append(f"delay_seconds should be int, got {type(delay_seconds)}")
        else:
            print(f"  ✓ delay_seconds is correctly an int: {delay_seconds}")
    
    # Test 3: on_status_code conversion to integers
    print("\n3. Testing on_status_code integer conversion...")
    
    try_catch_with_codes = TryCatchStep(
        try_steps=[ActionStep(action_name="try_action", output_key="try_result")],
        catch_block=CatchBlock(
            on_status_code=["400", 404, "500"],  # Mix of strings and integers
            steps=[ActionStep(action_name="catch_action", output_key="catch_result")]
        )
    )
    
    try_catch_dict = step_to_yaml_dict(try_catch_with_codes)
    status_codes = try_catch_dict.get('try_catch', {}).get('catch', {}).get('on_status_code', [])
    
    for i, code in enumerate(status_codes):
        if not isinstance(code, int):
            issues_found.append(f"on_status_code[{i}] should be int, got {type(code)}: {code}")
        else:
            print(f"  ✓ on_status_code[{i}] is correctly an int: {code}")
    
    return issues_found


def test_nested_steps_consistency():
    """Test nested steps consistency in control flow structures."""
    print("\n" + "=" * 60)
    print("TESTING NESTED STEPS CONSISTENCY")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Switch case steps
    print("\n1. Testing switch case steps structure...")
    
    switch_step = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.status == 'active'",
                steps=[
                    ActionStep(action_name="action1", output_key="result1"),
                    ActionStep(action_name="action2", output_key="result2")
                ]
            ),
            SwitchCase(
                condition="data.status == 'inactive'",
                steps=[ActionStep(action_name="action3", output_key="result3")]
            )
        ],
        default_case=DefaultCase(steps=[
            ActionStep(action_name="default_action", output_key="default_result")
        ])
    )
    
    switch_dict = step_to_yaml_dict(switch_step)
    switch_yaml = switch_dict.get('switch', {})
    
    # Check cases
    cases = switch_yaml.get('cases', [])
    for i, case in enumerate(cases):
        case_steps = case.get('steps', [])
        if not isinstance(case_steps, list):
            issues_found.append(f"Switch case {i+1} steps should be list, got {type(case_steps)}")
        else:
            print(f"  ✓ Switch case {i+1} steps is list with {len(case_steps)} items")
    
    # Check default case
    default_case = switch_yaml.get('default', {})
    default_steps = default_case.get('steps', [])
    if not isinstance(default_steps, list):
        issues_found.append(f"Switch default steps should be list, got {type(default_steps)}")
    else:
        print(f"  ✓ Switch default steps is list with {len(default_steps)} items")
    
    # Test 2: For loop steps
    print("\n2. Testing for loop steps structure...")
    
    for_step = ForLoopStep(
        each="item",
        in_source="data.items",
        output_key="loop_results",
        steps=[
            ActionStep(action_name="process_item", output_key="processed_item"),
            ScriptStep(code="return item.value", output_key="item_value")
        ]
    )
    
    for_dict = step_to_yaml_dict(for_step)
    for_yaml = for_dict.get('for', {})
    for_steps = for_yaml.get('steps', [])
    
    if not isinstance(for_steps, list):
        issues_found.append(f"For loop steps should be list, got {type(for_steps)}")
    else:
        print(f"  ✓ For loop steps is list with {len(for_steps)} items")
    
    # Test 3: Parallel branches
    print("\n3. Testing parallel branches structure...")
    
    parallel_step = ParallelStep(
        branches=[
            ParallelBranch(
                name="branch1",
                steps=[ActionStep(action_name="branch1_action", output_key="branch1_result")]
            ),
            ParallelBranch(
                name="branch2",
                steps=[ActionStep(action_name="branch2_action", output_key="branch2_result")]
            )
        ]
    )
    
    parallel_dict = step_to_yaml_dict(parallel_step)
    parallel_yaml = parallel_dict.get('parallel', {})
    branches = parallel_yaml.get('branches', [])
    
    for i, branch in enumerate(branches):
        branch_steps = branch.get('steps', [])
        if not isinstance(branch_steps, list):
            issues_found.append(f"Parallel branch {i+1} steps should be list, got {type(branch_steps)}")
        else:
            print(f"  ✓ Parallel branch {i+1} steps is list with {len(branch_steps)} items")
    
    return issues_found


def test_compliance_integration_issues():
    """Test for integration issues with compliance systems."""
    print("\n" + "=" * 60)
    print("TESTING COMPLIANCE INTEGRATION ISSUES")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: YAML generation with compliance validation
    print("\n1. Testing YAML generation with compliance validation...")
    
    compliant_workflow = Workflow(steps=[
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={"email": "data.input_email"}
        )
    ])
    
    # Generate YAML
    yaml_output = generate_yaml_string(compliant_workflow, "test_compliant_action")
    
    # Validate compliance
    compliance_result = compliance_validator.validate_workflow_compliance(
        compliant_workflow, "test_compliant_action"
    )
    
    if not compliance_result.is_valid:
        issues_found.append("Compliant workflow failed compliance validation")
        for error in (compliance_result.errors + compliance_result.mandatory_field_errors + 
                     compliance_result.field_naming_errors + compliance_result.apiton_errors):
            issues_found.append(f"  Compliance error: {error}")
    else:
        print("  ✓ Compliant workflow passes validation")
    
    # Test 2: YAML parsability
    print("\n2. Testing generated YAML parsability...")
    
    try:
        parsed_yaml = yaml.safe_load(yaml_output)
        if parsed_yaml is None:
            issues_found.append("Generated YAML parses as None")
        else:
            print("  ✓ Generated YAML is parsable")
            
            # Check required structure
            if 'action_name' not in parsed_yaml:
                issues_found.append("Parsed YAML missing action_name")
            if 'steps' not in parsed_yaml:
                issues_found.append("Parsed YAML missing steps")
            else:
                print(f"  ✓ Parsed YAML has required structure")
                
    except yaml.YAMLError as e:
        issues_found.append(f"Generated YAML is not parsable: {e}")
    
    return issues_found


def main():
    """Run critical YAML generation issue testing."""
    print("MOVEWORKS YAML ASSISTANT - CRITICAL YAML GENERATION ISSUES TEST")
    print("=" * 80)
    
    all_issues = []
    
    # Run all critical tests
    all_issues.extend(test_critical_field_names())
    all_issues.extend(test_data_type_consistency())
    all_issues.extend(test_nested_steps_consistency())
    all_issues.extend(test_compliance_integration_issues())
    
    # Summary
    print("\n" + "=" * 80)
    print("CRITICAL ISSUES TEST SUMMARY")
    print("=" * 80)
    
    if all_issues:
        print(f"\n❌ FOUND {len(all_issues)} CRITICAL ISSUES:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("1. Review and fix field name accuracy in yaml_generator.py")
        print("2. Ensure proper data type enforcement in step_to_yaml_dict()")
        print("3. Verify steps key implementation consistency")
        print("4. Test integration with compliance validation")
        
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
        print("✅ YAML generation logic is working correctly")
        print("✅ All field names are accurate")
        print("✅ Data types are properly enforced")
        print("✅ Steps key implementation is consistent")
        print("✅ Compliance integration is working")
    
    print(f"\nTotal critical issues: {len(all_issues)}")
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
