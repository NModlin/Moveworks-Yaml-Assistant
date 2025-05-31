#!/usr/bin/env python3
"""
Demonstration of comprehensive action_name field compliance for Moveworks YAML Assistant.

This script showcases all the enhanced action_name compliance features including:
- Mandatory field enforcement for ActionStep instances
- Naming convention validation (alphanumeric, dots, underscores)
- Integration with Moveworks Actions Catalog for validation and auto-completion
- YAML generation blocking for non-compliant workflows
- Field name standardization and data type validation
"""

from core_structures import Workflow, ActionStep, ScriptStep
from compliance_validator import compliance_validator
from action_name_validator import action_name_validator
from yaml_generator import generate_yaml_string


def demo_compliant_workflow():
    """Demonstrate a fully compliant workflow with proper action_name usage."""
    print("🎯 COMPLIANT WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create a compliant workflow with proper action_name fields
    action_step1 = ActionStep(
        action_name="mw.get_user_by_email",  # ✅ Valid Moveworks action
        output_key="user_info",
        input_args={
            "email": "data.input_email"
        },
        description="Get user information by email"
    )
    
    action_step2 = ActionStep(
        action_name="mw.create_ticket",  # ✅ Another valid Moveworks action
        output_key="ticket_info",
        input_args={
            "title": "User Request",
            "description": "data.user_info.request",
            "assignee": "data.user_info.manager.email"
        },
        description="Create support ticket"
    )
    
    custom_action = ActionStep(
        action_name="custom_notification_action",  # ✅ Valid custom action
        output_key="notification_result",
        input_args={
            "user_id": "data.user_info.id",
            "ticket_id": "data.ticket_info.id"
        },
        description="Send custom notification"
    )
    
    workflow = Workflow(steps=[action_step1, action_step2, custom_action])
    
    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "user_support_action")
    
    print(f"Workflow valid: {result.is_valid}")
    print(f"Mandatory field errors: {len(result.mandatory_field_errors)}")
    print(f"Field naming errors: {len(result.field_naming_errors)}")
    
    if result.is_valid:
        print("✅ All compliance checks passed!")
        
        # Generate YAML
        try:
            yaml_output = generate_yaml_string(workflow, "user_support_action")
            print("\n📄 Generated YAML:")
            print("-" * 30)
            print(yaml_output)
        except Exception as e:
            print(f"❌ YAML generation failed: {e}")
    else:
        print("❌ Compliance issues found:")
        for error in result.mandatory_field_errors + result.field_naming_errors:
            print(f"  • {error}")


def demo_non_compliant_workflow():
    """Demonstrate validation of a non-compliant workflow."""
    print("\n❌ NON-COMPLIANT WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create workflow with compliance violations
    action_step1 = ActionStep(
        action_name="",  # ❌ Missing required field
        output_key="user_info",
        description="Get user information"
    )
    
    action_step2 = ActionStep(
        action_name="invalid action name",  # ❌ Contains spaces
        output_key="ticket_info",
        description="Create ticket"
    )
    
    action_step3 = ActionStep(
        action_name="mw.",  # ❌ Incomplete mw. prefix
        output_key="notification_result",
        description="Send notification"
    )
    
    workflow = Workflow(steps=[action_step1, action_step2, action_step3])
    
    # Validate compliance
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"Workflow valid: {result.is_valid}")
    print(f"Mandatory field errors: {len(result.mandatory_field_errors)}")
    print(f"Field naming errors: {len(result.field_naming_errors)}")
    
    print("\n🔍 Compliance Issues Found:")
    for error in result.mandatory_field_errors:
        print(f"  • MANDATORY: {error}")
    
    for error in result.field_naming_errors:
        print(f"  • NAMING: {error}")
    
    # Try to generate YAML (should fail)
    try:
        yaml_output = generate_yaml_string(workflow, "test_action")
        print("❌ YAML generation should have been blocked!")
    except ValueError as e:
        print(f"\n✅ YAML generation correctly blocked: {str(e)[:100]}...")


def demo_individual_validation():
    """Demonstrate individual action_name validation with suggestions."""
    print("\n🔍 INDIVIDUAL ACTION_NAME VALIDATION")
    print("=" * 50)
    
    test_cases = [
        ("mw.get_user_by_email", "✅ Valid Moveworks action"),
        ("", "❌ Missing required field"),
        ("invalid action name", "❌ Contains spaces"),
        ("action@name", "❌ Invalid characters"),
        ("mw.", "❌ Incomplete mw. prefix"),
        ("custom_action", "✅ Valid custom action"),
        ("my.custom.action", "✅ Valid with dots"),
        ("action_123", "✅ Valid with numbers"),
        ("a", "❌ Too short"),
    ]
    
    for action_name, expected in test_cases:
        result = action_name_validator.validate_action_name(action_name)
        
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        catalog_status = " (Known)" if result.is_known_action else " (Custom)" if result.is_valid else ""
        
        print(f"{status}: '{action_name}'{catalog_status}")
        
        if not result.is_valid:
            for error in result.errors:
                print(f"    Error: {error}")
            for suggestion in result.suggestions:
                print(f"    Suggestion: {suggestion}")
        elif result.warnings:
            for warning in result.warnings:
                print(f"    Warning: {warning}")
        print()


def demo_catalog_integration():
    """Demonstrate integration with Moveworks Actions Catalog."""
    print("\n📚 CATALOG INTEGRATION DEMONSTRATION")
    print("=" * 50)
    
    # Test known Moveworks actions
    known_actions = [
        "mw.get_user_by_email",
        "mw.create_ticket",
        "mw.search_knowledge_base"
    ]
    
    print("Known Moveworks Actions:")
    for action_name in known_actions:
        result = action_name_validator.validate_action_name(action_name)
        status = "✅ RECOGNIZED" if result.is_known_action else "❓ UNKNOWN"
        print(f"  {status}: {action_name}")
        
        # Get action info if available
        action_info = action_name_validator.get_action_info(action_name)
        if action_info:
            print(f"    Category: {action_info['category']}")
            print(f"    Description: {action_info['description']}")
    
    print("\nAction Suggestions for 'get_user':")
    suggestions = action_name_validator.get_action_suggestions("get_user")
    for suggestion in suggestions[:5]:  # Show top 5
        print(f"  • {suggestion}")
    
    print("\nAvailable Categories:")
    categories = action_name_validator.get_all_categories()
    for category in categories:
        actions_in_category = action_name_validator.get_actions_by_category(category)
        print(f"  • {category}: {len(actions_in_category)} actions")


def demo_suggestion_system():
    """Demonstrate the action_name suggestion system."""
    print("\n💡 SUGGESTION SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    invalid_cases = [
        "invalid action name",  # Spaces
        "action-name",          # Hyphens
        "mw",                   # Incomplete
        "",                     # Empty
        "action@name",          # Special chars
    ]
    
    for invalid_name in invalid_cases:
        print(f"Invalid name: '{invalid_name}'")
        suggestions = action_name_validator.suggest_action_name_fixes(invalid_name)
        
        if suggestions:
            print("  Suggested fixes:")
            for suggestion in suggestions[:3]:  # Show top 3
                print(f"    • {suggestion}")
        else:
            print("  No specific suggestions available")
        print()


def demo_field_name_standardization():
    """Demonstrate field name standardization in YAML output."""
    print("\n📝 FIELD NAME STANDARDIZATION")
    print("=" * 50)
    
    # Create simple workflow
    action_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Test action"
    )
    
    workflow = Workflow(steps=[action_step])
    
    # Generate YAML and show field names
    yaml_output = generate_yaml_string(workflow, "test_action")
    
    print("Generated YAML uses standardized field names:")
    print("-" * 40)
    
    # Highlight the action_name field
    lines = yaml_output.split('\n')
    for line in lines:
        if 'action_name:' in line:
            print(f"✅ {line.strip()}")  # Highlight the correct field name
        elif line.strip():
            print(f"   {line}")
    
    print("\n✅ Uses exact field name 'action_name' (not 'actionName' or 'action')")


def main():
    """Run all demonstrations."""
    print("🚀 ACTION_NAME COMPLIANCE DEMONSTRATION")
    print("=" * 60)
    
    demo_compliant_workflow()
    demo_non_compliant_workflow()
    demo_individual_validation()
    demo_catalog_integration()
    demo_suggestion_system()
    demo_field_name_standardization()
    
    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("Key Features Demonstrated:")
    print("✅ Mandatory field enforcement for ActionStep instances")
    print("✅ Naming convention validation (alphanumeric, dots, underscores)")
    print("✅ Integration with Moveworks Actions Catalog")
    print("✅ YAML generation blocking for non-compliant workflows")
    print("✅ Field name standardization ('action_name')")
    print("✅ Data type validation and error reporting")
    print("✅ Comprehensive suggestion system")
    print("✅ Real-time validation with contextual feedback")


if __name__ == "__main__":
    main()
