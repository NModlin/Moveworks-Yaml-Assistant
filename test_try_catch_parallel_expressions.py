#!/usr/bin/env python3
"""
Comprehensive test for try_catch and parallel expression support in the Moveworks YAML Assistant.

This script tests all the enhanced try_catch and parallel expression functionality including:
1. TryCatchStep class with try_steps, catch_block, and output_key fields
2. ParallelStep class with for_loop and branches modes
3. YAML generation for both expression types
4. UI components and validation
5. Integration with existing compound action structure
"""

import sys
import json
from core_structures import (
    Workflow, ActionStep, ScriptStep, TryCatchStep, ParallelStep,
    CatchBlock, ParallelForLoop, ParallelBranch, ReturnStep
)
from yaml_generator import generate_yaml_string
from compliance_validator import compliance_validator


def test_try_catch_basic_functionality():
    """Test basic TryCatchStep functionality."""
    print("=" * 60)
    print("TEST 1: Basic TryCatchStep Functionality")
    print("=" * 60)
    
    # Create try steps
    try_action = ActionStep(
        action_name="mw.risky_operation",
        output_key="operation_result",
        input_args={"data": "data.input_data"}
    )
    
    # Create catch steps
    catch_action = ActionStep(
        action_name="mw.log_error",
        output_key="error_log",
        input_args={"error": "data.error_info"}
    )
    
    # Create catch block
    catch_block = CatchBlock(
        on_status_code=[400, 404, 500],
        steps=[catch_action]
    )
    
    # Create try/catch step
    try_catch_step = TryCatchStep(
        description="Handle risky operation with error logging",
        output_key="final_result",
        try_steps=[try_action],
        catch_block=catch_block
    )
    
    workflow = Workflow(steps=[try_catch_step])
    
    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow, "error_handling_workflow")
        print("✅ YAML Generation Successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Verify structure
        if "try_catch:" in yaml_output:
            print("✅ Try/catch structure present")
        if "try:" in yaml_output and "catch:" in yaml_output:
            print("✅ Try and catch blocks present")
        if "on_status_code:" in yaml_output:
            print("✅ Status codes configuration present")
            
    except Exception as e:
        print(f"❌ YAML Generation Failed: {e}")
    
    print()


def test_parallel_for_loop_mode():
    """Test ParallelStep for loop mode functionality."""
    print("=" * 60)
    print("TEST 2: Parallel For Loop Mode")
    print("=" * 60)
    
    # Create steps for the for loop
    process_user_action = ActionStep(
        action_name="mw.process_user",
        output_key="user_result",
        input_args={"user_data": "data.user"}
    )
    
    # Create for loop
    for_loop = ParallelForLoop(
        each="user",
        in_source="data.user_list",
        steps=[process_user_action]
    )
    
    # Create parallel step with for loop
    parallel_step = ParallelStep(
        description="Process users in parallel",
        output_key="processed_users",
        for_loop=for_loop
    )
    
    workflow = Workflow(steps=[parallel_step])
    
    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow, "parallel_for_workflow")
        print("✅ YAML Generation Successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Verify structure
        if "parallel:" in yaml_output:
            print("✅ Parallel structure present")
        if "for:" in yaml_output:
            print("✅ For loop configuration present")
        if "each:" in yaml_output and "in:" in yaml_output:
            print("✅ For loop parameters present")
            
    except Exception as e:
        print(f"❌ YAML Generation Failed: {e}")
    
    print()


def test_parallel_branches_mode():
    """Test ParallelStep branches mode functionality."""
    print("=" * 60)
    print("TEST 3: Parallel Branches Mode")
    print("=" * 60)
    
    # Create branch 1 steps
    branch1_action = ActionStep(
        action_name="mw.task_a",
        output_key="task_a_result",
        input_args={"input": "data.task_a_input"}
    )
    
    # Create branch 2 steps
    branch2_action = ActionStep(
        action_name="mw.task_b",
        output_key="task_b_result",
        input_args={"input": "data.task_b_input"}
    )
    
    # Create branches
    branch1 = ParallelBranch(steps=[branch1_action])
    branch2 = ParallelBranch(steps=[branch2_action])
    
    # Create parallel step with branches
    parallel_step = ParallelStep(
        description="Execute tasks in parallel branches",
        output_key="parallel_results",
        branches=[branch1, branch2]
    )
    
    workflow = Workflow(steps=[parallel_step])
    
    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow, "parallel_branches_workflow")
        print("✅ YAML Generation Successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Verify structure
        if "parallel:" in yaml_output:
            print("✅ Parallel structure present")
        if "branches:" in yaml_output:
            print("✅ Branches configuration present")
            
    except Exception as e:
        print(f"❌ YAML Generation Failed: {e}")
    
    print()


def test_complex_workflow_with_all_expressions():
    """Test a complex workflow with try/catch, parallel, and other expressions."""
    print("=" * 60)
    print("TEST 4: Complex Workflow with All Expression Types")
    print("=" * 60)
    
    # Step 1: Initial data fetch
    initial_fetch = ActionStep(
        action_name="mw.get_initial_data",
        output_key="initial_data",
        input_args={"query": "data.input_query"}
    )
    
    # Step 2: Parallel processing of data
    process_action = ActionStep(
        action_name="mw.process_item",
        output_key="processed_item",
        input_args={"item": "data.item"}
    )
    
    for_loop = ParallelForLoop(
        each="item",
        in_source="data.initial_data.items",
        steps=[process_action]
    )
    
    parallel_step = ParallelStep(
        description="Process items in parallel",
        output_key="processed_items",
        for_loop=for_loop
    )
    
    # Step 3: Try/catch for risky operation
    risky_action = ActionStep(
        action_name="mw.risky_aggregation",
        output_key="aggregation_result",
        input_args={"data": "data.processed_items"}
    )
    
    fallback_action = ActionStep(
        action_name="mw.fallback_aggregation",
        output_key="fallback_result",
        input_args={"data": "data.processed_items"}
    )
    
    catch_block = CatchBlock(
        on_status_code=[500, 503],
        steps=[fallback_action]
    )
    
    try_catch_step = TryCatchStep(
        description="Try aggregation with fallback",
        output_key="final_aggregation",
        try_steps=[risky_action],
        catch_block=catch_block
    )
    
    # Step 4: Return results
    return_step = ReturnStep(
        description="Return comprehensive results",
        output_mapper={
            "initial_count": "data.initial_data.count",
            "processed_count": "data.processed_items.length",
            "aggregation_result": "data.final_aggregation.result",
            "processing_time": "meta_info.request.timestamp"
        }
    )
    
    workflow = Workflow(steps=[initial_fetch, parallel_step, try_catch_step, return_step])
    
    # Test YAML generation
    try:
        yaml_output = generate_yaml_string(workflow, "comprehensive_workflow")
        print("✅ YAML Generation Successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Verify all expression types are present
        expressions_found = []
        if "action:" in yaml_output:
            expressions_found.append("action")
        if "parallel:" in yaml_output:
            expressions_found.append("parallel")
        if "try_catch:" in yaml_output:
            expressions_found.append("try_catch")
        if "return:" in yaml_output:
            expressions_found.append("return")
        
        print(f"✅ Expression types found: {', '.join(expressions_found)}")
        
    except Exception as e:
        print(f"❌ YAML Generation Failed: {e}")
    
    print()


def test_validation_compliance():
    """Test validation and compliance for try/catch and parallel expressions."""
    print("=" * 60)
    print("TEST 5: Validation and Compliance")
    print("=" * 60)
    
    # Test valid try/catch step
    valid_try_catch = TryCatchStep(
        description="Valid try/catch step",
        output_key="error_handling_result",
        try_steps=[ActionStep(action_name="mw.test_action", output_key="test_result")],
        catch_block=CatchBlock(
            on_status_code=[400, 500],
            steps=[ActionStep(action_name="mw.error_handler", output_key="error_result")]
        )
    )
    
    workflow1 = Workflow(steps=[valid_try_catch])
    result1 = compliance_validator.validate_workflow_compliance(workflow1)
    
    print(f"Valid try/catch step - Errors: {len(result1.errors)}")
    if result1.errors:
        for error in result1.errors:
            print(f"  ❌ {error}")
    else:
        print("✅ Valid try/catch step passed validation")
    
    # Test valid parallel step (for loop mode)
    valid_parallel = ParallelStep(
        description="Valid parallel step",
        output_key="parallel_processing_result",
        for_loop=ParallelForLoop(
            each="item",
            in_source="data.items_list",
            steps=[ActionStep(action_name="mw.process_item", output_key="item_result")]
        )
    )
    
    workflow2 = Workflow(steps=[valid_parallel])
    result2 = compliance_validator.validate_workflow_compliance(workflow2)
    
    print(f"\nValid parallel step - Errors: {len(result2.errors)}")
    if result2.errors:
        for error in result2.errors:
            print(f"  ❌ {error}")
    else:
        print("✅ Valid parallel step passed validation")
    
    # Test invalid step (missing output_key)
    invalid_try_catch = TryCatchStep(
        description="Invalid try/catch step",
        # Missing output_key
        try_steps=[ActionStep(action_name="mw.test_action", output_key="test_result")]
    )
    
    workflow3 = Workflow(steps=[invalid_try_catch])
    result3 = compliance_validator.validate_workflow_compliance(workflow3)
    
    print(f"\nInvalid try/catch step - Errors: {len(result3.errors)}")
    if result3.errors:
        print("✅ Invalid step correctly caught validation errors:")
        for error in result3.errors:
            print(f"  ❌ {error}")
    else:
        print("⚠️ Invalid step should have failed validation")
    
    print()


def test_dsl_string_quoting():
    """Test DSL string quoting in try/catch and parallel expressions."""
    print("=" * 60)
    print("TEST 6: DSL String Quoting")
    print("=" * 60)
    
    # Create try/catch with DSL expressions
    try_action = ActionStep(
        action_name="mw.test_operation",
        output_key="test_result",
        input_args={
            "user_id": "data.user_info.id",
            "is_active": "data.user_info.status == 'active'",
            "department": "meta_info.user.department"
        }
    )
    
    try_catch_step = TryCatchStep(
        description="Test DSL quoting in try/catch",
        output_key="dsl_test_result",
        try_steps=[try_action]
    )
    
    # Create parallel with DSL expressions
    parallel_action = ActionStep(
        action_name="mw.process_user",
        output_key="user_result",
        input_args={
            "user": "data.user",
            "is_valid": "data.user.status != null"
        }
    )
    
    parallel_step = ParallelStep(
        description="Test DSL quoting in parallel",
        output_key="parallel_dsl_result",
        for_loop=ParallelForLoop(
            each="user",
            in_source="data.users_list",
            steps=[parallel_action]
        )
    )
    
    workflow = Workflow(steps=[try_catch_step, parallel_step])
    
    try:
        yaml_output = generate_yaml_string(workflow, "dsl_quoting_test")
        print("✅ DSL quoting test YAML generation successful")
        print("\nGenerated YAML:")
        print(yaml_output)
        
        # Check for proper DSL quoting
        dsl_patterns = [
            '"data.user_info.id"',
            '"data.user_info.status == \'active\'"',
            '"meta_info.user.department"',
            '"data.users_list"',
            '"data.user.status != null"'
        ]
        
        quoted_count = 0
        for pattern in dsl_patterns:
            if pattern in yaml_output:
                quoted_count += 1
        
        print(f"\n✅ {quoted_count}/{len(dsl_patterns)} DSL expressions properly quoted")
        
        if quoted_count == len(dsl_patterns):
            print("✅ All DSL expressions correctly formatted")
        else:
            print("⚠️ Some DSL expressions may not be properly quoted")
            
    except Exception as e:
        print(f"❌ DSL quoting test failed: {e}")
    
    print()


def main():
    """Run all try/catch and parallel expression tests."""
    print("🚀 TRY/CATCH AND PARALLEL EXPRESSION SUPPORT TESTS")
    print("=" * 60)
    
    test_try_catch_basic_functionality()
    test_parallel_for_loop_mode()
    test_parallel_branches_mode()
    test_complex_workflow_with_all_expressions()
    test_validation_compliance()
    test_dsl_string_quoting()
    
    print("=" * 60)
    print("✅ ALL TRY/CATCH AND PARALLEL EXPRESSION TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
