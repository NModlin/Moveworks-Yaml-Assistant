#!/usr/bin/env python3
"""
Demonstration script for APIthon validation and YAML generation.

This script shows how the enhanced APIthon validation system works with
real examples of valid and invalid scripts, and demonstrates the proper
YAML generation with literal block scalars.
"""

from core_structures import ScriptStep, ActionStep, Workflow, DataContext
from apiton_validator import comprehensive_validate_apiton_script
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate


def demo_valid_apiton_script():
    """Demonstrate a valid APIthon script with proper YAML generation."""
    print("=" * 60)
    print("DEMO: Valid APIthon Script")
    print("=" * 60)
    
    # Create a realistic APIthon script
    script_code = """
# APIthon script to process user authentication data
user_email = data.user_info.email
user_status = data.user_info.status
current_time = "2024-01-01T12:00:00Z"

# Process authentication based on user status
if user_status == "active":
    auth_result = {
        "authenticated": True,
        "message": f"Welcome, {user_email}!",
        "access_level": "full",
        "session_timeout": 3600
    }
elif user_status == "pending":
    auth_result = {
        "authenticated": False,
        "message": f"Account pending approval for {user_email}",
        "access_level": "none",
        "session_timeout": 0
    }
else:
    auth_result = {
        "authenticated": False,
        "message": f"Account suspended for {user_email}",
        "access_level": "none",
        "session_timeout": 0
    }

# Add metadata
auth_result["timestamp"] = current_time
auth_result["user_agent"] = meta_info.user.email_addr
auth_result["request_id"] = f"req_{len(user_email)}"

return auth_result
    """.strip()
    
    # Create script step
    script_step = ScriptStep(
        code=script_code,
        output_key="auth_result",
        description="Process user authentication based on status",
        input_args={
            "user_data": "data.user_info",
            "session_config": "data.session_settings"
        }
    )
    
    print("Script Code:")
    print("-" * 40)
    print(script_code)
    print()
    
    # Validate the script
    print("Validation Results:")
    print("-" * 40)
    errors = comprehensive_validate_apiton_script(script_step)
    
    if errors:
        print("❌ Validation FAILED:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Validation PASSED - Script is valid APIthon code!")
    
    print()
    
    # Generate YAML
    print("Generated YAML:")
    print("-" * 40)
    workflow = Workflow(steps=[script_step])
    yaml_output = generate_yaml_string(workflow)
    print(yaml_output)


def demo_invalid_apiton_script():
    """Demonstrate an invalid APIthon script with validation errors."""
    print("=" * 60)
    print("DEMO: Invalid APIthon Script (Security Violations)")
    print("=" * 60)
    
    # Create a script with multiple APIthon violations
    invalid_code = """
import os  # ❌ Import not allowed
import json  # ❌ Import not allowed

class UserProcessor:  # ❌ Class definition not allowed
    def __init__(self):
        self._secret = "hidden"  # ❌ Private identifier not allowed
    
    def process_user(self):  # ❌ Function definition not allowed
        return "processed"

def dangerous_function():  # ❌ Function definition not allowed
    result = eval("os.system('rm -rf /')")  # ❌ eval() and os operations not allowed
    with open("/etc/passwd") as f:  # ❌ File operations not allowed
        data = f.read()
    return result

processor = UserProcessor()
result = processor.process_user()
return {"result": result}
    """.strip()
    
    # Create script step with invalid code
    script_step = ScriptStep(
        code=invalid_code,
        output_key="_invalid_result",  # ❌ Invalid output key (starts with underscore)
        description="This script violates multiple APIthon restrictions"
    )
    
    print("Invalid Script Code:")
    print("-" * 40)
    print(invalid_code)
    print()
    
    # Validate the script
    print("Validation Results:")
    print("-" * 40)
    errors = comprehensive_validate_apiton_script(script_step)
    
    if errors:
        print("❌ Validation FAILED (as expected):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print(f"\nTotal violations found: {len(errors)}")
    else:
        print("✅ Validation PASSED - This should not happen!")
    
    print()


def demo_workflow_validation():
    """Demonstrate workflow-level validation with multiple steps."""
    print("=" * 60)
    print("DEMO: Complete Workflow with APIthon Validation")
    print("=" * 60)
    
    # Create an action step
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"},
        user_provided_json_output='{"user": {"id": "12345", "name": "John Doe", "email": "john@example.com", "status": "active"}}'
    )
    
    # Create a valid script step
    valid_script = ScriptStep(
        code="""
# Process the user data from the previous action
user_data = data.user_info.user
processed_user = {
    "id": user_data["id"],
    "display_name": user_data["name"].upper(),
    "email_domain": user_data["email"].split("@")[1],
    "is_active": user_data["status"] == "active",
    "processed_at": "2024-01-01T12:00:00Z"
}
return processed_user
        """.strip(),
        output_key="processed_user",
        description="Process user data from action step"
    )
    
    # Create an invalid script step
    invalid_script = ScriptStep(
        code="import json\nreturn json.loads(data.user_info)",  # ❌ Import not allowed
        output_key="json_result",
        description="This script uses prohibited imports"
    )
    
    # Create workflow
    workflow = Workflow(steps=[action_step, valid_script, invalid_script])
    initial_context = DataContext({"input_email": "john@example.com"})
    
    print("Workflow Steps:")
    print("-" * 40)
    print("1. Action: Get user by email")
    print("2. Script: Process user data (valid APIthon)")
    print("3. Script: Parse JSON with imports (invalid APIthon)")
    print()
    
    # Validate entire workflow
    print("Comprehensive Workflow Validation:")
    print("-" * 40)
    all_errors = comprehensive_validate(workflow, initial_context)
    
    if all_errors:
        print(f"Found {len(all_errors)} validation errors:")
        for error in all_errors:
            print(f"  - {error}")
    else:
        print("✅ All validation passed!")
    
    print()
    
    # Generate YAML for the workflow
    print("Generated YAML (with APIthon formatting):")
    print("-" * 40)
    yaml_output = generate_yaml_string(workflow)
    print(yaml_output)


def main():
    """Run all APIthon validation demonstrations."""
    print("🚀 APIthon Validation System Demonstration")
    print("Moveworks YAML Assistant - Enhanced Script Validation")
    print()
    
    # Run demonstrations
    demo_valid_apiton_script()
    print("\n")
    demo_invalid_apiton_script()
    print("\n")
    demo_workflow_validation()
    
    print("\n" + "=" * 60)
    print("🎉 Demonstration Complete!")
    print("=" * 60)
    print()
    print("Key Features Demonstrated:")
    print("✅ Comprehensive APIthon code restriction validation")
    print("✅ Proper YAML generation with literal block scalars (|)")
    print("✅ Integration with existing workflow validation")
    print("✅ Clear error reporting for security violations")
    print("✅ Support for complex, realistic APIthon scripts")
    print()
    print("The APIthon validation system is now ready for production use!")


if __name__ == "__main__":
    main()
