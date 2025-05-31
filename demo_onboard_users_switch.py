#!/usr/bin/env python3
"""
Demonstration of "Onboard Users" Switch Expression Implementation.

This script demonstrates a comprehensive user onboarding workflow using
switch expressions with DSL conditions, following the Moveworks pattern.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase
)
from yaml_generator import generate_yaml_string


def create_onboard_users_workflow():
    """Create a comprehensive user onboarding workflow with switch expressions."""
    print("🏢 Creating 'Onboard Users' Workflow")
    print("=" * 60)
    
    # Step 1: Get user information
    get_user_info_step = ActionStep(
        action_name="mw.get_user_info",
        output_key="user_info",
        input_args={"user_id": "data.input_user_id"},
        description="Retrieve user information from directory"
    )
    
    # Step 2: Switch based on user department
    department_switch = SwitchStep(
        description="Department-based onboarding process",
        cases=[
            # Engineering Department
            SwitchCase(
                condition="data.user_info.department == 'Engineering'",
                steps=[
                    ActionStep(
                        action_name="mw.create_engineering_accounts",
                        output_key="eng_accounts_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "email": "data.user_info.email",
                            "team": "data.user_info.team"
                        },
                        description="Create engineering-specific accounts (GitHub, Jira, etc.)"
                    ),
                    ActionStep(
                        action_name="mw.assign_development_tools",
                        output_key="dev_tools_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "role": "data.user_info.role",
                            "seniority": "data.user_info.seniority_level"
                        },
                        description="Assign development tools and licenses"
                    ),
                    ScriptStep(
                        code="""# Generate engineering welcome package
user_name = data.user_info.first_name
team = data.user_info.team
role = data.user_info.role

welcome_package = {
    'welcome_message': f'Welcome to the {team} team, {user_name}!',
    'onboarding_checklist': [
        'Complete security training',
        'Set up development environment',
        'Join team Slack channels',
        'Schedule 1:1 with manager'
    ],
    'tools_assigned': data.dev_tools_result.tools,
    'accounts_created': data.eng_accounts_result.accounts
}

return welcome_package""",
                        output_key="eng_welcome_package",
                        description="Generate engineering welcome package"
                    )
                ]
            ),
            
            # Sales Department
            SwitchCase(
                condition="data.user_info.department == 'Sales'",
                steps=[
                    ActionStep(
                        action_name="mw.create_sales_accounts",
                        output_key="sales_accounts_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "email": "data.user_info.email",
                            "territory": "data.user_info.sales_territory"
                        },
                        description="Create sales-specific accounts (Salesforce, HubSpot, etc.)"
                    ),
                    ActionStep(
                        action_name="mw.assign_sales_quota",
                        output_key="quota_assignment_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "role": "data.user_info.role",
                            "territory": "data.user_info.sales_territory",
                            "start_date": "data.user_info.start_date"
                        },
                        description="Assign sales quota and targets"
                    ),
                    ScriptStep(
                        code="""# Generate sales welcome package
user_name = data.user_info.first_name
territory = data.user_info.sales_territory
quota = data.quota_assignment_result.quarterly_quota

welcome_package = {
    'welcome_message': f'Welcome to the Sales team, {user_name}!',
    'territory_info': {
        'assigned_territory': territory,
        'quarterly_quota': quota,
        'key_accounts': data.quota_assignment_result.key_accounts
    },
    'onboarding_checklist': [
        'Complete sales methodology training',
        'Shadow senior sales rep',
        'Learn CRM system',
        'Meet territory customers'
    ],
    'accounts_created': data.sales_accounts_result.accounts
}

return welcome_package""",
                        output_key="sales_welcome_package",
                        description="Generate sales welcome package"
                    )
                ]
            ),
            
            # Marketing Department
            SwitchCase(
                condition="data.user_info.department == 'Marketing'",
                steps=[
                    ActionStep(
                        action_name="mw.create_marketing_accounts",
                        output_key="marketing_accounts_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "email": "data.user_info.email",
                            "specialization": "data.user_info.marketing_specialization"
                        },
                        description="Create marketing-specific accounts (Adobe, Analytics, etc.)"
                    ),
                    ActionStep(
                        action_name="mw.assign_marketing_campaigns",
                        output_key="campaign_assignment_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "specialization": "data.user_info.marketing_specialization",
                            "experience_level": "data.user_info.experience_level"
                        },
                        description="Assign marketing campaigns and projects"
                    )
                ]
            ),
            
            # HR Department
            SwitchCase(
                condition="data.user_info.department == 'HR'",
                steps=[
                    ActionStep(
                        action_name="mw.create_hr_accounts",
                        output_key="hr_accounts_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "email": "data.user_info.email",
                            "hr_role": "data.user_info.hr_specialization"
                        },
                        description="Create HR-specific accounts (Workday, BambooHR, etc.)"
                    ),
                    ActionStep(
                        action_name="mw.assign_hr_permissions",
                        output_key="hr_permissions_result",
                        input_args={
                            "user_id": "data.user_info.id",
                            "role": "data.user_info.role",
                            "clearance_level": "data.user_info.security_clearance"
                        },
                        description="Assign HR system permissions based on role"
                    )
                ]
            )
        ],
        
        # Default case for other departments
        default_case=DefaultCase(
            steps=[
                ActionStep(
                    action_name="mw.create_standard_accounts",
                    output_key="standard_accounts_result",
                    input_args={
                        "user_id": "data.user_info.id",
                        "email": "data.user_info.email",
                        "department": "data.user_info.department"
                    },
                    description="Create standard company accounts"
                ),
                ScriptStep(
                    code="""# Generate standard welcome package
user_name = data.user_info.first_name
department = data.user_info.department

welcome_package = {
    'welcome_message': f'Welcome to {department}, {user_name}!',
    'onboarding_checklist': [
        'Complete general orientation',
        'Set up workspace',
        'Meet team members',
        'Review department handbook'
    ],
    'accounts_created': data.standard_accounts_result.accounts,
    'next_steps': 'Contact your manager for department-specific onboarding'
}

return welcome_package""",
                    output_key="standard_welcome_package",
                    description="Generate standard welcome package"
                )
            ]
        ),
        output_key="_"
    )
    
    # Step 3: Send welcome notification
    send_notification_step = ActionStep(
        action_name="mw.send_welcome_notification",
        output_key="notification_result",
        input_args={
            "user_email": "data.user_info.email",
            "welcome_package": "data.eng_welcome_package or data.sales_welcome_package or data.standard_welcome_package",
            "manager_email": "data.user_info.manager_email"
        },
        description="Send personalized welcome notification to new user and manager"
    )
    
    # Create the complete workflow
    workflow = Workflow(
        steps=[
            get_user_info_step,
            department_switch,
            send_notification_step
        ]
    )
    
    print(f"✅ Workflow created with {len(workflow.steps)} main steps")
    print(f"   - User info retrieval")
    print(f"   - Department-based switch with {len(department_switch.cases)} cases")
    print(f"   - Welcome notification")
    print()
    
    return workflow


def demonstrate_switch_conditions():
    """Demonstrate the DSL conditions used in the switch cases."""
    print("🔍 Switch Condition Analysis")
    print("=" * 60)
    
    conditions = [
        "data.user_info.department == 'Engineering'",
        "data.user_info.department == 'Sales'",
        "data.user_info.department == 'Marketing'",
        "data.user_info.department == 'HR'"
    ]
    
    print("Switch conditions used in the onboarding workflow:")
    for i, condition in enumerate(conditions, 1):
        print(f"   {i}. {condition}")
    
    print("\nThese conditions demonstrate:")
    print("   ✅ Simple equality comparisons")
    print("   ✅ Data field access (data.user_info.department)")
    print("   ✅ String literal matching")
    print("   ✅ Department-based routing logic")
    print()


def demonstrate_step_structure():
    """Demonstrate the step structure within switch cases."""
    print("📋 Step Structure Analysis")
    print("=" * 60)
    
    print("Each switch case contains a list of steps:")
    print("   1. Action Steps - Call Moveworks actions")
    print("   2. Script Steps - Execute APIthon code")
    print("   3. Nested Steps - Can include other expressions")
    print()
    
    print("Engineering case example:")
    print("   - Action: Create engineering accounts")
    print("   - Action: Assign development tools")
    print("   - Script: Generate welcome package")
    print()
    
    print("Sales case example:")
    print("   - Action: Create sales accounts")
    print("   - Action: Assign sales quota")
    print("   - Script: Generate sales welcome package")
    print()
    
    print("Default case example:")
    print("   - Action: Create standard accounts")
    print("   - Script: Generate standard welcome package")
    print()


def generate_and_display_yaml():
    """Generate and display the YAML output."""
    print("📄 YAML Generation")
    print("=" * 60)
    
    workflow = create_onboard_users_workflow()
    
    try:
        yaml_output = generate_yaml_string(workflow, "onboard_users")
        
        print("✅ YAML generated successfully!")
        print("\nGenerated YAML structure:")
        
        lines = yaml_output.split('\n')
        
        # Show key sections
        print("\n--- Action Name and Steps Structure ---")
        for i, line in enumerate(lines[:10]):
            print(f"   {line}")
        
        print("\n--- Switch Expression Structure ---")
        switch_start = None
        for i, line in enumerate(lines):
            if 'switch:' in line:
                switch_start = i
                break
        
        if switch_start:
            for i in range(switch_start, min(switch_start + 15, len(lines))):
                print(f"   {lines[i]}")
        
        print(f"\n--- Full YAML Statistics ---")
        print(f"   Total lines: {len(lines)}")
        print(f"   Contains switch expression: {'switch:' in yaml_output}")
        print(f"   Contains cases: {'cases:' in yaml_output}")
        print(f"   Contains default: {'default:' in yaml_output}")
        
        return yaml_output
        
    except Exception as e:
        print(f"❌ Error generating YAML: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run the onboard users switch demonstration."""
    print("🚀 Onboard Users Switch Expression Demonstration")
    print("=" * 80)
    print()
    
    try:
        # Create and analyze the workflow
        workflow = create_onboard_users_workflow()
        
        # Demonstrate switch conditions
        demonstrate_switch_conditions()
        
        # Demonstrate step structure
        demonstrate_step_structure()
        
        # Generate YAML
        yaml_output = generate_and_display_yaml()
        
        if yaml_output:
            print("\n" + "=" * 80)
            print("✅ Onboard Users switch expression demonstration completed!")
            print("=" * 80)
            print("\nKey Features Demonstrated:")
            print("   🔀 Switch expressions with multiple cases")
            print("   🔍 DSL condition evaluation")
            print("   📋 Department-based workflow routing")
            print("   🛠️ Mixed action and script steps")
            print("   🔄 Default case handling")
            print("   📄 Complete YAML generation")
        else:
            print("\n❌ Demonstration completed with errors")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
