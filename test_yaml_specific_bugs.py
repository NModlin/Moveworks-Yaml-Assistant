#!/usr/bin/env python3
"""
Specific YAML Generation Bug Testing

This script tests for specific potential bugs and edge cases that might exist
in the current YAML generation implementation.
"""

import sys
import yaml
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep,
    TryCatchStep, CatchBlock, ParallelForLoop
)
from yaml_generator import generate_yaml_string, workflow_to_yaml_dict, step_to_yaml_dict


def test_output_key_handling():
    """Test output_key handling across different step types."""
    print("=" * 60)
    print("TESTING OUTPUT_KEY HANDLING")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Switch step output_key handling
    print("\n1. Testing switch step output_key...")
    
    # Switch with default output_key
    switch_default = SwitchStep(
        cases=[SwitchCase(condition="data.test == 'true'", steps=[
            ActionStep(action_name="test", output_key="result")
        ])],
        output_key="_"  # Default value
    )
    
    switch_dict_default = step_to_yaml_dict(switch_default)
    
    # Check if default output_key is excluded
    if 'output_key' in switch_dict_default:
        issues_found.append("Switch step with default output_key '_' should not include output_key field")
    else:
        print("  ✓ Switch with default output_key '_' correctly excludes output_key field")
    
    # Switch with custom output_key
    switch_custom = SwitchStep(
        cases=[SwitchCase(condition="data.test == 'true'", steps=[
            ActionStep(action_name="test", output_key="result")
        ])],
        output_key="custom_result"
    )
    
    switch_dict_custom = step_to_yaml_dict(switch_custom)
    
    if 'output_key' not in switch_dict_custom:
        issues_found.append("Switch step with custom output_key should include output_key field")
    elif switch_dict_custom['output_key'] != "custom_result":
        issues_found.append(f"Switch output_key incorrect: expected 'custom_result', got '{switch_dict_custom['output_key']}'")
    else:
        print("  ✓ Switch with custom output_key correctly includes output_key field")
    
    return issues_found


def test_empty_workflow_handling():
    """Test handling of empty workflows."""
    print("\n" + "=" * 60)
    print("TESTING EMPTY WORKFLOW HANDLING")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Completely empty workflow
    print("\n1. Testing completely empty workflow...")
    
    empty_workflow = Workflow(steps=[])
    
    try:
        empty_dict = workflow_to_yaml_dict(empty_workflow)
        yaml_output = generate_yaml_string(empty_workflow)
        
        if 'steps' not in empty_dict:
            issues_found.append("Empty workflow missing 'steps' field")
        elif not isinstance(empty_dict['steps'], list):
            issues_found.append("Empty workflow 'steps' should be list")
        elif len(empty_dict['steps']) != 0:
            issues_found.append(f"Empty workflow should have 0 steps, got {len(empty_dict['steps'])}")
        else:
            print("  ✓ Empty workflow handled correctly")
            
    except Exception as e:
        issues_found.append(f"Empty workflow handling failed: {e}")
    
    return issues_found


def test_complex_nested_structures():
    """Test complex nested workflow structures."""
    print("\n" + "=" * 60)
    print("TESTING COMPLEX NESTED STRUCTURES")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Deeply nested switch with for loops
    print("\n1. Testing deeply nested structures...")
    
    complex_workflow = Workflow(steps=[
        SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.mode == 'batch'",
                    steps=[
                        ForLoopStep(
                            each="item",
                            in_source="data.items",
                            output_key="processed_items",
                            steps=[
                                ActionStep(
                                    action_name="process_item",
                                    output_key="item_result",
                                    input_args={"item_data": "data.item"}
                                ),
                                SwitchStep(
                                    cases=[
                                        SwitchCase(
                                            condition="data.item_result.status == 'success'",
                                            steps=[
                                                ActionStep(
                                                    action_name="log_success",
                                                    output_key="log_result"
                                                )
                                            ]
                                        )
                                    ],
                                    default_case=DefaultCase(steps=[
                                        ActionStep(
                                            action_name="log_error",
                                            output_key="error_log"
                                        )
                                    ])
                                )
                            ]
                        )
                    ]
                )
            ],
            default_case=DefaultCase(steps=[
                ActionStep(action_name="single_process", output_key="single_result")
            ])
        )
    ])
    
    try:
        complex_dict = workflow_to_yaml_dict(complex_workflow)
        yaml_output = generate_yaml_string(complex_workflow, "complex_nested_action")
        
        # Try to parse the generated YAML
        parsed_yaml = yaml.safe_load(yaml_output)
        
        if parsed_yaml is None:
            issues_found.append("Complex nested workflow YAML parsed as None")
        else:
            print("  ✓ Complex nested workflow YAML generated successfully")
            
            # Check structure depth
            steps = parsed_yaml.get('steps', [])
            if len(steps) > 0:
                first_step = steps[0]
                if 'switch' in first_step:
                    switch_cases = first_step['switch'].get('cases', [])
                    if len(switch_cases) > 0:
                        case_steps = switch_cases[0].get('steps', [])
                        if len(case_steps) > 0 and 'for' in case_steps[0]:
                            print("  ✓ Nested structure preserved correctly")
                        else:
                            issues_found.append("Nested for loop not found in switch case")
                    else:
                        issues_found.append("Switch cases not found in complex structure")
                else:
                    issues_found.append("Switch structure not found in complex workflow")
            else:
                issues_found.append("No steps found in complex workflow")
                
    except Exception as e:
        issues_found.append(f"Complex nested structure handling failed: {e}")
    
    return issues_found


def test_dsl_expression_edge_cases():
    """Test DSL expression handling edge cases."""
    print("\n" + "=" * 60)
    print("TESTING DSL EXPRESSION EDGE CASES")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Complex DSL expressions
    print("\n1. Testing complex DSL expressions...")
    
    complex_dsl_workflow = Workflow(steps=[
        ActionStep(
            action_name="complex_dsl_test",
            output_key="dsl_result",
            input_args={
                "nested_data": "data.user_info.profile.settings.theme",
                "array_access": "data.items[0].name",
                "complex_condition": "data.user.age >= 18 && data.user.status == 'active'",
                "function_call": "$CONCAT([data.first_name, ' ', data.last_name])",
                "meta_info_access": "meta_info.user.email_addr",
                "mixed_expression": "data.count > 0 ? data.items[0] : 'default'"
            }
        )
    ])
    
    try:
        yaml_output = generate_yaml_string(complex_dsl_workflow)
        parsed_yaml = yaml.safe_load(yaml_output)
        
        input_args = parsed_yaml['steps'][0]['action']['input_args']
        
        # Check if all DSL expressions are properly quoted
        dsl_fields = ['nested_data', 'array_access', 'complex_condition', 'function_call', 'meta_info_access']
        
        for field in dsl_fields:
            if field in input_args:
                value = input_args[field]
                if isinstance(value, str):
                    print(f"  ✓ {field} properly handled as string: {value[:50]}...")
                else:
                    issues_found.append(f"DSL field {field} should be string, got {type(value)}")
            else:
                issues_found.append(f"DSL field {field} missing from input_args")
                
    except Exception as e:
        issues_found.append(f"Complex DSL expression handling failed: {e}")
    
    return issues_found


def test_yaml_output_format():
    """Test YAML output format compliance."""
    print("\n" + "=" * 60)
    print("TESTING YAML OUTPUT FORMAT COMPLIANCE")
    print("=" * 60)
    
    issues_found = []
    
    # Test 1: Multiline script formatting
    print("\n1. Testing multiline script formatting...")
    
    multiline_script = ScriptStep(
        code="""
# This is a multiline APIthon script
user_data = data.user_info
processed_data = {
    "name": user_data.name,
    "email": user_data.email,
    "status": "processed"
}

# Return the processed data
return processed_data
        """.strip(),
        output_key="processed_result"
    )
    
    workflow_with_script = Workflow(steps=[multiline_script])
    yaml_output = generate_yaml_string(workflow_with_script)
    
    # Check for literal block scalar formatting
    if 'code: |' not in yaml_output and 'code: |-' not in yaml_output:
        issues_found.append("Multiline script should use literal block scalar (|) formatting")
    else:
        print("  ✓ Multiline script uses literal block scalar formatting")
    
    # Test 2: DSL expression quoting
    print("\n2. Testing DSL expression quoting in YAML...")
    
    dsl_workflow = Workflow(steps=[
        ActionStep(
            action_name="dsl_test",
            output_key="result",
            input_args={
                "data_ref": "data.user_info.email",
                "meta_ref": "meta_info.user.name"
            }
        )
    ])
    
    dsl_yaml = generate_yaml_string(dsl_workflow)
    
    # Check if DSL expressions are quoted
    if '"data.user_info.email"' not in dsl_yaml:
        issues_found.append("DSL expression 'data.user_info.email' not properly quoted")
    else:
        print("  ✓ DSL data reference properly quoted")
        
    if '"meta_info.user.name"' not in dsl_yaml:
        issues_found.append("DSL expression 'meta_info.user.name' not properly quoted")
    else:
        print("  ✓ DSL meta_info reference properly quoted")
    
    return issues_found


def main():
    """Run specific YAML generation bug testing."""
    print("MOVEWORKS YAML ASSISTANT - SPECIFIC BUG TESTING")
    print("=" * 80)
    
    all_issues = []
    
    # Run all specific bug tests
    all_issues.extend(test_output_key_handling())
    all_issues.extend(test_empty_workflow_handling())
    all_issues.extend(test_complex_nested_structures())
    all_issues.extend(test_dsl_expression_edge_cases())
    all_issues.extend(test_yaml_output_format())
    
    # Summary
    print("\n" + "=" * 80)
    print("SPECIFIC BUG TESTING SUMMARY")
    print("=" * 80)
    
    if all_issues:
        print(f"\n❌ FOUND {len(all_issues)} SPECIFIC BUGS:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
        
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Review output_key handling logic in step_to_yaml_dict()")
        print("2. Improve empty workflow validation")
        print("3. Test complex nested structure generation")
        print("4. Enhance DSL expression handling")
        print("5. Verify YAML output format compliance")
        
    else:
        print("\n✅ NO SPECIFIC BUGS FOUND")
        print("✅ Output key handling is correct")
        print("✅ Empty workflows handled properly")
        print("✅ Complex nested structures work correctly")
        print("✅ DSL expressions handled properly")
        print("✅ YAML output format is compliant")
    
    print(f"\nTotal specific bugs: {len(all_issues)}")
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
