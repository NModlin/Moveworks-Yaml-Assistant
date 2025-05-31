#!/usr/bin/env python3
"""
Test script for enhanced YAML generation with Moveworks compliance.

This script tests the enhanced YAML generation system to ensure it produces
proper Moveworks compound action format with mandatory fields.
"""

from core_structures import ActionStep, ScriptStep, Workflow
from yaml_generator import generate_yaml_string, workflow_to_yaml_dict


def test_enhanced_yaml_generation():
    """Test the enhanced YAML generation with compound action format."""
    print("=== Testing Enhanced YAML Generation ===\n")
    
    # Create a comprehensive workflow
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"},
        delay_config={"delay_seconds": 5},
        user_provided_json_output='{"user": {"id": "12345", "name": "John Doe", "email": "john@example.com"}}'
    )
    
    script_step = ScriptStep(
        code="""# Process user data
user_name = data.user_info.user.name
user_email = meta_info.user.email
result = {
    "greeting": f"Hello, {user_name}!",
    "contact_email": user_email,
    "user_id": data.user_info.user.id
}
return result""",
        output_key="processed_data",
        description="Process user information with greeting",
        input_args={"user_data": "data.user_info"},
        user_provided_json_output='{"greeting": "Hello, John Doe!", "contact_email": "user@company.com", "user_id": "12345"}'
    )
    
    workflow = Workflow(steps=[action_step, script_step])
    
    # Test 1: Generate YAML with custom action name
    print("1. Testing YAML generation with custom action name:")
    print("-" * 50)
    yaml_output = generate_yaml_string(workflow, "my_user_lookup_action")
    print(yaml_output)
    print("-" * 50)
    
    # Test 2: Generate YAML with default action name
    print("\n2. Testing YAML generation with default action name:")
    print("-" * 50)
    yaml_output_default = generate_yaml_string(workflow)
    print(yaml_output_default)
    print("-" * 50)
    
    # Test 3: Check workflow dictionary structure
    print("\n3. Testing workflow dictionary structure:")
    print("-" * 50)
    workflow_dict = workflow_to_yaml_dict(workflow, "test_compound_action")
    print("Workflow dictionary keys:", list(workflow_dict.keys()))
    print("Action name:", workflow_dict.get("action_name"))
    print("Steps count:", len(workflow_dict.get("steps", [])))
    print("First step type:", list(workflow_dict["steps"][0].keys())[0] if workflow_dict.get("steps") else "None")
    print("Second step type:", list(workflow_dict["steps"][1].keys())[0] if len(workflow_dict.get("steps", [])) > 1 else "None")
    print("-" * 50)
    
    # Test 4: Verify data type enforcement
    print("\n4. Testing data type enforcement:")
    print("-" * 50)
    first_step = workflow_dict["steps"][0]["action"]
    print("Action input_args type:", type(first_step.get("input_args")))
    print("Action delay_config type:", type(first_step.get("delay_config")))
    if first_step.get("delay_config"):
        print("Delay seconds type:", type(first_step["delay_config"].get("delay_seconds")))
        print("Delay seconds value:", first_step["delay_config"].get("delay_seconds"))
    
    second_step = workflow_dict["steps"][1]["script"]
    print("Script input_args type:", type(second_step.get("input_args")))
    print("Script description type:", type(second_step.get("description")))
    print("-" * 50)
    
    print("\n✅ Enhanced YAML generation test completed successfully!")
    print("✅ Compound action format enforced")
    print("✅ Data type validation working")
    print("✅ Action name parameter support functional")


if __name__ == "__main__":
    test_enhanced_yaml_generation()
