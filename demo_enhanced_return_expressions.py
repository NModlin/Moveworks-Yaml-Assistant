#!/usr/bin/env python3
"""
Demo script showcasing the enhanced return expression support in the Moveworks YAML Assistant.

This script demonstrates the key features and capabilities of the enhanced return expression system.
"""

import sys
from core_structures import (
    Workflow, ActionStep, ScriptStep, ReturnStep
)
from yaml_generator import generate_yaml_string


def demo_basic_return_expression():
    """Demonstrate basic return expression functionality."""
    print("🔹 DEMO 1: Basic Return Expression")
    print("-" * 50)
    
    # Create a simple workflow with return
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Get user information by email",
        input_args={"email": "data.input_email"}
    )
    
    return_step = ReturnStep(
        description="Return basic user information",
        output_mapper={
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email",
            "department": "meta_info.user.department"
        }
    )
    
    workflow = Workflow(steps=[action_step, return_step])
    yaml_output = generate_yaml_string(workflow, "basic_return_demo")
    
    print("Generated YAML:")
    print(yaml_output)
    print()


def demo_advanced_dsl_expressions():
    """Demonstrate advanced DSL expressions in return steps."""
    print("🔹 DEMO 2: Advanced DSL Expressions")
    print("-" * 50)
    
    action_step = ActionStep(
        action_name="mw.get_user_profile",
        output_key="user_profile",
        input_args={"user_id": "data.input_user_id"}
    )
    
    return_step = ReturnStep(
        description="Return user profile with advanced DSL expressions",
        output_mapper={
            "user_id": "data.user_profile.user.id",
            "full_name": "data.user_profile.user.first_name + ' ' + data.user_profile.user.last_name",
            "is_active": "data.user_profile.user.status == 'active'",
            "is_adult": "data.user_profile.user.age >= 18",
            "has_permissions": "data.user_profile.permissions.length > 0",
            "is_admin": "(data.user_profile.role == 'admin') && (data.user_profile.permissions.length > 0)",
            "department": "meta_info.user.department",
            "requested_by": "meta_info.user.email",
            "request_time": "meta_info.request.timestamp"
        }
    )
    
    workflow = Workflow(steps=[action_step, return_step])
    yaml_output = generate_yaml_string(workflow, "advanced_dsl_demo")
    
    print("Generated YAML with DSL expressions:")
    print(yaml_output)
    print()


def demo_multi_step_workflow():
    """Demonstrate return expressions in a multi-step workflow."""
    print("🔹 DEMO 3: Multi-Step Workflow with Return")
    print("-" * 50)
    
    # Step 1: Get user information
    get_user_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        input_args={"email": "data.input_email"}
    )
    
    # Step 2: Get user permissions
    get_permissions_step = ActionStep(
        action_name="mw.get_user_permissions",
        output_key="user_permissions",
        input_args={"user_id": "data.user_info.user.id"}
    )
    
    # Step 3: Process data with script
    process_script = ScriptStep(
        code="""
# Process user data and permissions
user = data.user_info.user
permissions = data.user_permissions.permissions

# Calculate summary statistics
total_permissions = len(permissions)
admin_permissions = len([p for p in permissions if p.level == 'admin'])
active_permissions = len([p for p in permissions if p.status == 'active'])

result = {
    "total_permissions": total_permissions,
    "admin_permissions": admin_permissions,
    "active_permissions": active_permissions,
    "permission_ratio": active_permissions / total_permissions if total_permissions > 0 else 0,
    "is_power_user": admin_permissions > 0 and active_permissions >= 3
}
return result
        """.strip(),
        output_key="permission_analysis"
    )
    
    # Step 4: Return comprehensive results
    return_step = ReturnStep(
        description="Return comprehensive user analysis",
        output_mapper={
            # Basic user info
            "user_id": "data.user_info.user.id",
            "user_name": "data.user_info.user.name",
            "user_email": "data.user_info.user.email",
            
            # Permission analysis
            "total_permissions": "data.permission_analysis.total_permissions",
            "admin_permissions": "data.permission_analysis.admin_permissions",
            "active_permissions": "data.permission_analysis.active_permissions",
            "permission_ratio": "data.permission_analysis.permission_ratio",
            "is_power_user": "data.permission_analysis.is_power_user",
            
            # Status checks
            "is_active_user": "data.user_info.user.status == 'active'",
            "has_any_permissions": "data.user_permissions.permissions.length > 0",
            
            # Meta information
            "department": "meta_info.user.department",
            "analyzed_by": "meta_info.user.email",
            "analysis_timestamp": "meta_info.request.timestamp"
        }
    )
    
    workflow = Workflow(steps=[get_user_step, get_permissions_step, process_script, return_step])
    yaml_output = generate_yaml_string(workflow, "comprehensive_user_analysis")
    
    print("Generated comprehensive workflow YAML:")
    print(yaml_output)
    print()


def demo_template_patterns():
    """Demonstrate common template patterns for return expressions."""
    print("🔹 DEMO 4: Template Patterns")
    print("-" * 50)
    
    templates = [
        {
            "name": "User Profile Template",
            "description": "Standard user profile return pattern",
            "mappings": {
                "user_id": "data.user_info.user.id",
                "user_name": "data.user_info.user.name",
                "user_email": "data.user_info.user.email",
                "department": "meta_info.user.department"
            }
        },
        {
            "name": "Status Check Template",
            "description": "Validation and status return pattern",
            "mappings": {
                "is_valid": "data.validation_result.is_valid",
                "status": "data.validation_result.status",
                "message": "data.validation_result.message",
                "timestamp": "meta_info.request.timestamp"
            }
        },
        {
            "name": "Error Handling Template",
            "description": "Error information return pattern",
            "mappings": {
                "error_code": "data.error_info.code",
                "error_message": "data.error_info.message",
                "error_details": "data.error_info.details",
                "user_context": "meta_info.user.id"
            }
        }
    ]
    
    for template in templates:
        print(f"\n📋 {template['name']}")
        print(f"Description: {template['description']}")
        
        return_step = ReturnStep(
            description=template['description'],
            output_mapper=template['mappings']
        )
        
        workflow = Workflow(steps=[return_step])
        yaml_output = generate_yaml_string(workflow, f"template_{template['name'].lower().replace(' ', '_')}")
        
        print("YAML Output:")
        print(yaml_output)


def demo_validation_examples():
    """Demonstrate validation features."""
    print("🔹 DEMO 5: Validation Examples")
    print("-" * 50)
    
    print("✅ Valid return step with proper field naming:")
    valid_return = ReturnStep(
        description="Valid return step example",
        output_mapper={
            "user_id": "data.user_info.id",  # lowercase_snake_case ✓
            "user_name": "data.user_info.name",  # lowercase_snake_case ✓
            "is_active": "data.user_info.status == 'active'"  # DSL expression ✓
        }
    )
    
    workflow = Workflow(steps=[valid_return])
    yaml_output = generate_yaml_string(workflow, "valid_return_example")
    print(yaml_output)
    
    print("\n💡 Key validation features:")
    print("• Output keys use lowercase_snake_case format")
    print("• DSL expressions are automatically quoted")
    print("• Real-time validation provides immediate feedback")
    print("• Drag-drop support from JSON Path Selector")
    print("• Template system for common patterns")
    print()


def main():
    """Run all return expression demos."""
    print("🚀 ENHANCED RETURN EXPRESSION DEMOS")
    print("=" * 60)
    
    demo_basic_return_expression()
    demo_advanced_dsl_expressions()
    demo_multi_step_workflow()
    demo_template_patterns()
    demo_validation_examples()
    
    print("=" * 60)
    print("✅ ALL DEMOS COMPLETED")
    print("\n🎯 Key Features Demonstrated:")
    print("• Basic return expression functionality")
    print("• Advanced DSL expression support")
    print("• Multi-step workflow integration")
    print("• Template system for common patterns")
    print("• Validation and compliance features")
    print("• Automatic DSL string quoting")
    print("• Comprehensive YAML generation")
    print("=" * 60)


if __name__ == "__main__":
    main()
