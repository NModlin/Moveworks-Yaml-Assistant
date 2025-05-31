#!/usr/bin/env python3
"""
Demo script showcasing the try/catch and parallel expression support in the Moveworks YAML Assistant.

This script demonstrates the key features and capabilities of the enhanced try/catch and parallel expression systems.
"""

import sys
from core_structures import (
    Workflow, ActionStep, ScriptStep, TryCatchStep, ParallelStep,
    CatchBlock, ParallelForLoop, ParallelBranch, ReturnStep
)
from yaml_generator import generate_yaml_string


def demo_basic_try_catch():
    """Demonstrate basic try/catch functionality."""
    print("🔹 DEMO 1: Basic Try/Catch Expression")
    print("-" * 50)
    
    # Create try step
    try_action = ActionStep(
        action_name="mw.external_api_call",
        output_key="api_result",
        description="Call external API that might fail",
        input_args={"endpoint": "data.api_endpoint", "params": "data.api_params"}
    )
    
    # Create catch step
    catch_action = ActionStep(
        action_name="mw.log_error_and_fallback",
        output_key="fallback_result",
        description="Log error and provide fallback data",
        input_args={"error_info": "data.error_details", "fallback_data": "data.cached_data"}
    )
    
    # Create catch block
    catch_block = CatchBlock(
        description="Handle API failures",
        on_status_code=[400, 404, 500, 503],
        steps=[catch_action]
    )
    
    # Create try/catch step
    try_catch_step = TryCatchStep(
        description="API call with error handling",
        output_key="final_api_result",
        try_steps=[try_action],
        catch_block=catch_block
    )
    
    workflow = Workflow(steps=[try_catch_step])
    yaml_output = generate_yaml_string(workflow, "api_error_handling")
    
    print("Generated YAML:")
    print(yaml_output)
    print()


def demo_parallel_for_loop():
    """Demonstrate parallel for loop functionality."""
    print("🔹 DEMO 2: Parallel For Loop Expression")
    print("-" * 50)
    
    # Create step to process each user
    process_user_action = ActionStep(
        action_name="mw.validate_and_process_user",
        output_key="user_validation_result",
        description="Validate and process individual user",
        input_args={
            "user_data": "data.user",
            "validation_rules": "data.validation_config"
        }
    )
    
    # Create parallel for loop
    for_loop = ParallelForLoop(
        each="user",
        in_source="data.users_to_process",
        steps=[process_user_action]
    )
    
    # Create parallel step
    parallel_step = ParallelStep(
        description="Process all users in parallel",
        output_key="user_processing_results",
        for_loop=for_loop
    )
    
    workflow = Workflow(steps=[parallel_step])
    yaml_output = generate_yaml_string(workflow, "parallel_user_processing")
    
    print("Generated YAML:")
    print(yaml_output)
    print()


def demo_parallel_branches():
    """Demonstrate parallel branches functionality."""
    print("🔹 DEMO 3: Parallel Branches Expression")
    print("-" * 50)
    
    # Branch 1: User data processing
    user_data_action = ActionStep(
        action_name="mw.fetch_user_profile",
        output_key="user_profile",
        input_args={"user_id": "data.target_user_id"}
    )
    
    # Branch 2: Permission checking
    permissions_action = ActionStep(
        action_name="mw.check_user_permissions",
        output_key="user_permissions",
        input_args={"user_id": "data.target_user_id", "resource": "data.target_resource"}
    )
    
    # Branch 3: Audit logging
    audit_action = ActionStep(
        action_name="mw.log_access_attempt",
        output_key="audit_log",
        input_args={"user_id": "data.target_user_id", "timestamp": "meta_info.request.timestamp"}
    )
    
    # Create branches
    branch1 = ParallelBranch(steps=[user_data_action])
    branch2 = ParallelBranch(steps=[permissions_action])
    branch3 = ParallelBranch(steps=[audit_action])
    
    # Create parallel step with branches
    parallel_step = ParallelStep(
        description="Fetch user data, check permissions, and log access in parallel",
        output_key="parallel_access_check",
        branches=[branch1, branch2, branch3]
    )
    
    workflow = Workflow(steps=[parallel_step])
    yaml_output = generate_yaml_string(workflow, "parallel_access_verification")
    
    print("Generated YAML:")
    print(yaml_output)
    print()


def demo_complex_error_handling_workflow():
    """Demonstrate complex workflow with nested try/catch and parallel processing."""
    print("🔹 DEMO 4: Complex Error Handling Workflow")
    print("-" * 50)
    
    # Step 1: Initial data validation
    validation_action = ActionStep(
        action_name="mw.validate_input_data",
        output_key="validation_result",
        input_args={"input_data": "data.user_input"}
    )
    
    # Step 2: Parallel processing of validated data
    process_item_action = ActionStep(
        action_name="mw.process_data_item",
        output_key="processed_item",
        input_args={"item": "data.item", "config": "data.processing_config"}
    )
    
    parallel_processing = ParallelStep(
        description="Process validated items in parallel",
        output_key="processed_items",
        for_loop=ParallelForLoop(
            each="item",
            in_source="data.validation_result.valid_items",
            steps=[process_item_action]
        )
    )
    
    # Step 3: Try/catch for aggregation with fallback
    try_aggregation = ActionStep(
        action_name="mw.advanced_aggregation",
        output_key="aggregation_result",
        input_args={"processed_data": "data.processed_items"}
    )
    
    catch_simple_aggregation = ActionStep(
        action_name="mw.simple_aggregation",
        output_key="simple_aggregation_result",
        input_args={"processed_data": "data.processed_items"}
    )
    
    catch_error_log = ActionStep(
        action_name="mw.log_aggregation_error",
        output_key="error_log",
        input_args={"error_details": "data.error_info", "fallback_used": "true"}
    )
    
    aggregation_try_catch = TryCatchStep(
        description="Try advanced aggregation with simple fallback",
        output_key="final_aggregation",
        try_steps=[try_aggregation],
        catch_block=CatchBlock(
            on_status_code=[500, 503, 504],
            steps=[catch_simple_aggregation, catch_error_log]
        )
    )
    
    # Step 4: Return comprehensive results
    return_step = ReturnStep(
        description="Return processing results with metadata",
        output_mapper={
            "validation_status": "data.validation_result.status",
            "items_processed": "data.processed_items.length",
            "aggregation_method": "data.final_aggregation.method",
            "final_result": "data.final_aggregation.result",
            "processing_time": "meta_info.request.timestamp",
            "errors_encountered": "data.error_log.count"
        }
    )
    
    workflow = Workflow(steps=[
        validation_action,
        parallel_processing,
        aggregation_try_catch,
        return_step
    ])
    
    yaml_output = generate_yaml_string(workflow, "complex_data_processing")
    
    print("Generated YAML:")
    print(yaml_output)
    print()


def demo_real_world_scenarios():
    """Demonstrate real-world scenarios using try/catch and parallel expressions."""
    print("🔹 DEMO 5: Real-World Scenarios")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "User Onboarding with Error Handling",
            "description": "Onboard new users with fallback for system failures",
            "workflow": create_user_onboarding_workflow()
        },
        {
            "name": "Parallel Data Validation",
            "description": "Validate multiple data sources in parallel",
            "workflow": create_parallel_validation_workflow()
        },
        {
            "name": "Resilient API Integration",
            "description": "Integrate with multiple APIs with comprehensive error handling",
            "workflow": create_resilient_api_workflow()
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"Description: {scenario['description']}")
        
        yaml_output = generate_yaml_string(
            scenario['workflow'], 
            scenario['name'].lower().replace(' ', '_')
        )
        
        print("YAML Output:")
        print(yaml_output[:500] + "..." if len(yaml_output) > 500 else yaml_output)


def create_user_onboarding_workflow():
    """Create a user onboarding workflow with error handling."""
    # Try to create user account
    create_user_action = ActionStep(
        action_name="mw.create_user_account",
        output_key="user_account",
        input_args={"user_data": "data.new_user_info"}
    )
    
    # Fallback: queue for manual processing
    queue_manual_action = ActionStep(
        action_name="mw.queue_for_manual_processing",
        output_key="manual_queue_result",
        input_args={"user_data": "data.new_user_info", "reason": "account_creation_failed"}
    )
    
    return Workflow(steps=[
        TryCatchStep(
            description="Create user account with manual fallback",
            output_key="onboarding_result",
            try_steps=[create_user_action],
            catch_block=CatchBlock(
                on_status_code=[400, 409, 500],
                steps=[queue_manual_action]
            )
        )
    ])


def create_parallel_validation_workflow():
    """Create a parallel validation workflow."""
    # Validate different aspects in parallel
    email_validation = ActionStep(
        action_name="mw.validate_email",
        output_key="email_validation",
        input_args={"email": "data.user_email"}
    )
    
    phone_validation = ActionStep(
        action_name="mw.validate_phone",
        output_key="phone_validation",
        input_args={"phone": "data.user_phone"}
    )
    
    address_validation = ActionStep(
        action_name="mw.validate_address",
        output_key="address_validation",
        input_args={"address": "data.user_address"}
    )
    
    return Workflow(steps=[
        ParallelStep(
            description="Validate user data in parallel",
            output_key="validation_results",
            branches=[
                ParallelBranch(steps=[email_validation]),
                ParallelBranch(steps=[phone_validation]),
                ParallelBranch(steps=[address_validation])
            ]
        )
    ])


def create_resilient_api_workflow():
    """Create a resilient API integration workflow."""
    # Primary API call
    primary_api = ActionStep(
        action_name="mw.call_primary_api",
        output_key="primary_result",
        input_args={"query": "data.search_query"}
    )
    
    # Fallback API call
    fallback_api = ActionStep(
        action_name="mw.call_fallback_api",
        output_key="fallback_result",
        input_args={"query": "data.search_query"}
    )
    
    # Cache result
    cache_result = ActionStep(
        action_name="mw.cache_api_result",
        output_key="cache_status",
        input_args={"result": "data.api_response"}
    )
    
    return Workflow(steps=[
        TryCatchStep(
            description="Resilient API call with fallback",
            output_key="api_response",
            try_steps=[primary_api],
            catch_block=CatchBlock(
                on_status_code=[500, 502, 503, 504],
                steps=[fallback_api]
            )
        ),
        cache_result
    ])


def main():
    """Run all try/catch and parallel expression demos."""
    print("🚀 TRY/CATCH AND PARALLEL EXPRESSION DEMOS")
    print("=" * 60)
    
    demo_basic_try_catch()
    demo_parallel_for_loop()
    demo_parallel_branches()
    demo_complex_error_handling_workflow()
    demo_real_world_scenarios()
    
    print("=" * 60)
    print("✅ ALL DEMOS COMPLETED")
    print("\n🎯 Key Features Demonstrated:")
    print("• Basic try/catch error handling")
    print("• Parallel for loop processing")
    print("• Parallel branches execution")
    print("• Complex nested workflows")
    print("• Real-world scenario implementations")
    print("• Comprehensive YAML generation")
    print("• DSL string quoting and validation")
    print("=" * 60)


if __name__ == "__main__":
    main()
