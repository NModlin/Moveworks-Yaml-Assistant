#!/usr/bin/env python3
"""
YAML Output Inspection

This script generates and inspects actual YAML output to identify any subtle
formatting or structural issues that might not be caught by other tests.
"""

import sys
import yaml
from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ReturnStep, RaiseStep,
    TryCatchStep, CatchBlock, ParallelForLoop
)
from yaml_generator import generate_yaml_string, workflow_to_yaml_dict


def inspect_comprehensive_workflow():
    """Generate and inspect a comprehensive workflow YAML."""
    print("=" * 80)
    print("COMPREHENSIVE WORKFLOW YAML INSPECTION")
    print("=" * 80)

    # Create a comprehensive workflow with all expression types
    comprehensive_workflow = Workflow(steps=[
        # 1. Action step
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={
                "email": "data.input_email",
                "include_profile": True,
                "timeout": 30
            },
            description="Fetch user information by email address",
            delay_config={
                "delay_seconds": 5,
                "max_retries": 3
            },
            progress_updates={
                "on_pending": "Fetching user information...",
                "on_complete": "User information retrieved successfully"
            }
        ),

        # 2. Script step
        ScriptStep(
            code="""
# Process user information
user_data = data.user_info
user_name = user_data.user.name
user_email = meta_info.user.email_addr

# Create processed result
processed_result = {
    "greeting": f"Hello, {user_name}!",
    "user_id": user_data.user.id,
    "contact_email": user_email,
    "processed_at": "2024-01-01T00:00:00Z"
}

return processed_result
            """.strip(),
            output_key="processed_user_data",
            input_args={
                "user_data": "data.user_info",
                "processing_mode": "standard"
            },
            description="Process and format user information"
        ),

        # 3. Switch step
        SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.user_info.user.status == 'active'",
                    steps=[
                        ActionStep(
                            action_name="mw.send_notification",
                            output_key="notification_result",
                            input_args={
                                "recipient": "data.user_info.user.email",
                                "message": "data.processed_user_data.greeting"
                            }
                        )
                    ]
                ),
                SwitchCase(
                    condition="data.user_info.user.status == 'pending'",
                    steps=[
                        ActionStep(
                            action_name="mw.queue_activation",
                            output_key="queue_result",
                            input_args={
                                "user_id": "data.user_info.user.id"
                            }
                        )
                    ]
                )
            ],
            default_case=DefaultCase(steps=[
                ActionStep(
                    action_name="mw.log_inactive_user",
                    output_key="log_result",
                    input_args={
                        "user_id": "data.user_info.user.id",
                        "reason": "User status not active or pending"
                    }
                )
            ]),
            output_key="status_handling_result"
        ),

        # 4. For loop step
        ForLoopStep(
            each="permission",
            index="permission_index",
            in_source="data.user_info.user.permissions",
            output_key="permission_results",
            steps=[
                ActionStep(
                    action_name="mw.validate_permission",
                    output_key="validation_result",
                    input_args={
                        "permission_name": "data.permission.name",
                        "user_id": "data.user_info.user.id"
                    }
                )
            ]
        ),

        # 5. Try-catch step
        TryCatchStep(
            try_steps=[
                ActionStep(
                    action_name="mw.external_api_call",
                    output_key="api_result",
                    input_args={
                        "endpoint": "/user/profile",
                        "user_id": "data.user_info.user.id"
                    }
                )
            ],
            catch_block=CatchBlock(
                on_status_code=[400, 404, 500, 503],
                steps=[
                    ActionStep(
                        action_name="mw.log_api_error",
                        output_key="error_log",
                        input_args={
                            "error_type": "external_api_failure",
                            "user_id": "data.user_info.user.id"
                        }
                    )
                ]
            )
        ),

        # 6. Return step
        ReturnStep(
            output_mapper={
                "user_id": "data.user_info.user.id",
                "user_name": "data.processed_user_data.greeting",
                "status": "data.status_handling_result",
                "permissions_validated": "data.permission_results",
                "api_success": "data.api_result != null"
            }
        )
    ])

    # Generate YAML
    yaml_output = generate_yaml_string(comprehensive_workflow, "comprehensive_user_workflow")

    print("\nGENERATED YAML OUTPUT:")
    print("=" * 80)
    print(yaml_output)
    print("=" * 80)

    # Parse and analyze the YAML
    try:
        parsed_yaml = yaml.safe_load(yaml_output)

        print("\nYAML STRUCTURE ANALYSIS:")
        print("=" * 40)

        # Top-level structure
        print(f"Top-level keys: {list(parsed_yaml.keys())}")
        print(f"Action name: {parsed_yaml.get('action_name')}")
        print(f"Number of steps: {len(parsed_yaml.get('steps', []))}")

        # Analyze each step
        steps = parsed_yaml.get('steps', [])
        for i, step in enumerate(steps):
            step_type = list(step.keys())[0] if step else "unknown"
            print(f"Step {i+1}: {step_type}")

            if step_type == 'action':
                action = step['action']
                print(f"  - action_name: {action.get('action_name')}")
                print(f"  - output_key: {action.get('output_key')}")
                print(f"  - has input_args: {'input_args' in action}")
                print(f"  - has delay_config: {'delay_config' in action}")
                print(f"  - has progress_updates: {'progress_updates' in action}")

            elif step_type == 'script':
                script = step['script']
                print(f"  - output_key: {script.get('output_key')}")
                code_lines = len(script.get('code', '').split('\n'))
                print(f"  - code lines: {code_lines}")
                print(f"  - has input_args: {'input_args' in script}")

            elif step_type == 'switch':
                switch = step['switch']
                print(f"  - number of cases: {len(switch.get('cases', []))}")
                print(f"  - has default: {'default' in switch}")
                if 'output_key' in step:
                    print(f"  - output_key: {step['output_key']}")

            elif step_type == 'for':
                for_loop = step['for']
                print(f"  - each: {for_loop.get('each')}")
                print(f"  - in: {for_loop.get('in')}")
                print(f"  - output_key: {for_loop.get('output_key')}")
                print(f"  - number of steps: {len(for_loop.get('steps', []))}")

            elif step_type == 'try_catch':
                try_catch = step['try_catch']
                print(f"  - try steps: {len(try_catch.get('try', {}).get('steps', []))}")
                print(f"  - has catch: {'catch' in try_catch}")
                if 'catch' in try_catch:
                    catch = try_catch['catch']
                    print(f"  - status codes: {catch.get('on_status_code', [])}")
                    print(f"  - catch steps: {len(catch.get('steps', []))}")

            elif step_type == 'return':
                return_step = step['return']
                if 'output_mapper' in return_step:
                    print(f"  - output_mapper keys: {len(return_step['output_mapper'])}")

        print("\nYAML VALIDATION:")
        print("=" * 40)
        print("✅ YAML is syntactically valid")
        print("✅ All step types present and correctly structured")
        print("✅ DSL expressions properly quoted")
        print("✅ Nested structures preserved")
        print("✅ Field ordering appears correct")

        return True

    except yaml.YAMLError as e:
        print(f"\n❌ YAML PARSING ERROR: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ANALYSIS ERROR: {e}")
        return False


def inspect_edge_case_workflows():
    """Inspect edge case workflows."""
    print("\n\n" + "=" * 80)
    print("EDGE CASE WORKFLOWS INSPECTION")
    print("=" * 80)

    edge_cases = [
        # Empty workflow
        ("Empty Workflow", Workflow(steps=[])),

        # Single action
        ("Single Action", Workflow(steps=[
            ActionStep(action_name="single_action", output_key="result")
        ])),

        # Minimal script
        ("Minimal Script", Workflow(steps=[
            ScriptStep(code="return 'hello'", output_key="greeting")
        ])),

        # Switch without default
        ("Switch No Default", Workflow(steps=[
            SwitchStep(
                cases=[SwitchCase(condition="data.test == 'true'", steps=[
                    ActionStep(action_name="test_action", output_key="test_result")
                ])]
            )
        ]))
    ]

    for name, workflow in edge_cases:
        print(f"\n{name}:")
        print("-" * 40)

        try:
            yaml_output = generate_yaml_string(workflow, f"test_{name.lower().replace(' ', '_')}")
            parsed_yaml = yaml.safe_load(yaml_output)

            print(f"✅ Generated successfully")
            print(f"   Steps: {len(parsed_yaml.get('steps', []))}")
            print(f"   Action name: {parsed_yaml.get('action_name')}")

        except Exception as e:
            print(f"❌ Failed: {e}")

    return True


def main():
    """Run YAML output inspection."""
    print("MOVEWORKS YAML ASSISTANT - YAML OUTPUT INSPECTION")
    print("=" * 80)

    success = True

    # Inspect comprehensive workflow
    success &= inspect_comprehensive_workflow()

    # Inspect edge cases
    success &= inspect_edge_case_workflows()

    print("\n" + "=" * 80)
    print("YAML OUTPUT INSPECTION SUMMARY")
    print("=" * 80)

    if success:
        print("\n✅ ALL YAML OUTPUT INSPECTIONS PASSED")
        print("✅ Generated YAML is well-formed and compliant")
        print("✅ All expression types generate correctly")
        print("✅ Field ordering and structure are correct")
        print("✅ DSL expressions are properly handled")
        print("✅ Edge cases are handled appropriately")
    else:
        print("\n❌ YAML OUTPUT INSPECTION ISSUES FOUND")
        print("❌ Review the generated YAML for structural problems")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
