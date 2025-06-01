"""
Legacy Tutorial Plugin.

This plugin migrates all tutorials from the original tutorial_system.py
with 100% content preservation while adapting to the new plugin architecture.
"""

import warnings
from typing import Dict, Any, List
from tutorials.unified_tutorial_system import (
    TutorialPlugin, UnifiedTutorial, UnifiedTutorialStep,
    TutorialCategory, TutorialDifficulty
)

# Import tutorial data for JSON examples
try:
    from tutorial_data import get_tutorial_json_data, get_tutorial_script_example
except ImportError:
    # Fallback if tutorial_data is not available
    def get_tutorial_json_data(tutorial_id: str, step_type: str = "user"):
        return {"message": "Sample JSON data not available"}
    
    def get_tutorial_script_example(tutorial_id: str):
        return "# Sample script code\nreturn {}"


class LegacyTutorialPlugin(TutorialPlugin):
    """Plugin for legacy tutorials from tutorial_system.py."""
    
    def get_plugin_id(self) -> str:
        return "legacy_tutorials"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Legacy Tutorial System",
            "version": "1.0.0",
            "description": "Migrated tutorials from the original tutorial_system.py",
            "author": "Moveworks YAML Assistant",
            "source": "tutorial_system.py",
            "module_name": "legacy_tutorials",
            "tutorial_count": 4,
            "categories": ["Getting Started", "Expression Types"]
        }
    
    def get_tutorials(self) -> List[UnifiedTutorial]:
        """Return all legacy tutorials converted to unified format."""
        tutorials = []
        
        # Basic Workflow Tutorial (exact content preservation)
        basic_workflow = UnifiedTutorial(
            id="legacy_basic_workflow",
            title="Basic Workflow Creation",
            description="Learn how to create a Moveworks-compliant workflow with compound action naming and steps.",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="7 minutes",
            learning_objectives=[
                "Understand compound action structure",
                "Create basic workflow steps",
                "Generate Moveworks-compliant YAML",
                "Use the validation system"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to the Enhanced Tutorial",
                    description="This tutorial will guide you through creating your first Moveworks-compliant workflow.",
                    instruction="We'll start with setting a compound action name, then add steps. Click 'Next' to continue.",
                    action_type="info",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Set Your Compound Action Name",
                    description="Every workflow needs a unique compound action name.",
                    instruction="In the top field, enter a name for your compound action. Use lowercase with underscores, like 'my_workflow'.",
                    target_element="compound_action_name_field",
                    action_type="type",
                    copy_paste_data="my_basic_workflow",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Add Your First Action Step",
                    description="Action steps are the building blocks of workflows.",
                    instruction="Click the 'Add Action Step' button to create your first step. This will open the action configuration panel.",
                    target_element="add_action_btn",
                    action_type="click",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Configure the Action",
                    description="Set up your action step with the required information.",
                    instruction="Fill in the action name and output key. The action name identifies what this step does, and the output key is how you'll reference its results.",
                    target_element="action_config_panel",
                    action_type="info",
                    copy_paste_data="mw.get_user_info",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Add Sample JSON Output",
                    description="JSON output helps with data path selection in later steps.",
                    instruction="Paste sample JSON that represents what this action will return. This enables the JSON Path Selector.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data='{"user": {"name": "John Doe", "email": "john@company.com", "department": "Engineering"}}',
                    sample_json=get_tutorial_json_data("legacy_basic_workflow")
                ),
                UnifiedTutorialStep(
                    title="Review Your Moveworks-Compliant YAML",
                    description="Check the generated YAML structure.",
                    instruction="Look at the YAML preview panel. Notice the compound action structure with 'action_name' at the top level and your steps wrapped in a 'steps' array. This format is required for Moveworks compliance.",
                    target_element="yaml_preview_panel",
                    action_type="info",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Tutorial Complete!",
                    description="Congratulations! You've created your first Moveworks-compliant workflow.",
                    instruction="The YAML is ready for use in Moveworks. Continue exploring to learn more features like conditional logic, data processing, and error handling.",
                    action_type="info",
                    auto_advance=False
                )
            ],
            version="1.0.0",
            author="Legacy System Migration",
            plugin_source="legacy_tutorials"
        )
        tutorials.append(basic_workflow)
        
        # Control Flow Tutorial (exact content preservation)
        control_flow = UnifiedTutorial(
            id="legacy_control_flow",
            title="Control Flow and Conditional Logic",
            description="Learn to use switch statements, for loops, and conditional expressions in workflows.",
            category=TutorialCategory.EXPRESSION_TYPES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="12 minutes",
            prerequisites=["legacy_basic_workflow"],
            learning_objectives=[
                "Implement switch statements for conditional logic",
                "Create for loops for data processing",
                "Use conditional expressions effectively",
                "Build complex workflow logic"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Introduction to Control Flow",
                    description="Control flow expressions let you create dynamic, intelligent workflows.",
                    instruction="In this tutorial, you'll learn to use switch statements, for loops, and conditional logic to create sophisticated automation workflows.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Add a Switch Step",
                    description="Switch steps enable conditional branching in your workflow.",
                    instruction="Click the 'Add Switch Step' button to create a conditional branch. This allows your workflow to take different actions based on data values.",
                    target_element="add_switch_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Switch Conditions",
                    description="Set up the conditions that determine which branch to take.",
                    instruction="In the switch configuration, add conditions that evaluate data from previous steps. Each condition should return true or false.",
                    target_element="switch_config_panel",
                    action_type="info",
                    copy_paste_data="data.user_info.department == 'Engineering'"
                ),
                UnifiedTutorialStep(
                    title="Add For Loop Processing",
                    description="For loops let you process arrays and collections of data.",
                    instruction="Click 'Add For Loop Step' to create a loop that can process multiple items. This is useful for batch operations.",
                    target_element="add_for_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Loop Parameters",
                    description="Set up what data to loop over and how to process each item.",
                    instruction="Configure the for loop to iterate over an array from previous steps. Define what happens for each item in the collection.",
                    target_element="for_config_panel",
                    action_type="info",
                    copy_paste_data="data.user_list"
                ),
                UnifiedTutorialStep(
                    title="Test Your Control Flow",
                    description="Validate that your conditional logic works correctly.",
                    instruction="Use the validation panel to check your control flow logic. Make sure conditions are properly formatted and loops have valid data sources.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Control Flow Complete!",
                    description="You've mastered conditional logic and loops in Moveworks workflows.",
                    instruction="Your workflow now includes sophisticated control flow that can handle complex business logic and data processing scenarios.",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Legacy System Migration",
            plugin_source="legacy_tutorials"
        )
        tutorials.append(control_flow)
        
        # Module 1: Basic Compound Action (exact content preservation)
        module_1 = UnifiedTutorial(
            id="legacy_module_1_basic_compound_action",
            title="Module 1: Your First Compound Action",
            description="Learn to create basic compound actions with lookup and notification",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="15 minutes",
            learning_objectives=[
                "Understand compound action fundamentals",
                "Create employee onboarding workflows",
                "Implement data lookup patterns",
                "Build notification systems",
                "Master YAML compliance requirements"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to Compound Actions",
                    description="Welcome! This tutorial teaches you to create Moveworks compound actions.",
                    instruction="We'll build an employee onboarding notification system that demonstrates data lookup and notification patterns. Click 'Next' to begin.",
                    action_type="info",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Set Compound Action Name",
                    description="Every compound action needs a unique identifier.",
                    instruction="Enter 'employee_onboarding_notification' as your compound action name. This identifies your workflow in the Moveworks system.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="employee_onboarding_notification"
                ),
                UnifiedTutorialStep(
                    title="Add User Lookup Action",
                    description="First, we'll look up employee information.",
                    instruction="Click 'Add Action Step' to create a step that retrieves user data. This will be the foundation of our onboarding workflow.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure User Lookup",
                    description="Set up the user lookup action with proper naming.",
                    instruction="Set the action name to 'mw.get_user_by_email' and output key to 'user_info'. This creates a reusable data reference.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.get_user_by_email"
                ),
                UnifiedTutorialStep(
                    title="Add User Data JSON",
                    description="Provide sample JSON to enable data path selection.",
                    instruction="Paste the user data JSON below. This represents what the user lookup will return and enables the JSON Path Selector.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data=str(get_tutorial_json_data("legacy_module_1")),
                    sample_json=get_tutorial_json_data("legacy_module_1")
                ),
                UnifiedTutorialStep(
                    title="Add Notification Action",
                    description="Now we'll add a step to send the onboarding notification.",
                    instruction="Click 'Add Action Step' again to create the notification step that will welcome the new employee.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Notification",
                    description="Set up the notification action to use data from the user lookup.",
                    instruction="Set action name to 'mw.send_notification' and configure it to use data from the user_info step.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.send_notification"
                ),
                UnifiedTutorialStep(
                    title="Review Generated YAML",
                    description="Check your complete compound action structure.",
                    instruction="Look at the YAML preview to see your complete onboarding workflow. Notice how the steps reference each other's data.",
                    target_element="yaml_preview_panel",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Validate Your Workflow",
                    description="Ensure your compound action meets Moveworks standards.",
                    instruction="Click 'Validate Now' to check for compliance issues and verify your workflow is ready for deployment.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 1 Complete!",
                    description="Congratulations! You've created your first compound action.",
                    instruction="You've learned the fundamentals: compound action naming, action steps, data flow, and validation. Ready for Module 2: IT Automation?",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Legacy System Migration",
            plugin_source="legacy_tutorials"
        )
        tutorials.append(module_1)
        
        # Module 2: IT Automation (exact content preservation)
        module_2 = UnifiedTutorial(
            id="legacy_module_2_it_automation",
            title="Module 2: IT Automation",
            description="ServiceNow/Jira ticket creation with HTTP requests and parameterization",
            category=TutorialCategory.EXPRESSION_TYPES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="20 minutes",
            prerequisites=["legacy_module_1_basic_compound_action"],
            learning_objectives=[
                "Create HTTP request action steps",
                "Use parameterization with variables",
                "Integrate with ServiceNow and Jira",
                "Handle complex input arguments",
                "Implement enterprise automation patterns"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to IT Automation",
                    description="Learn to automate enterprise IT processes.",
                    instruction="We'll build an automated incident response system that creates tickets in both ServiceNow and Jira when critical alerts are triggered.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Set IT Automation Name",
                    description="Name your enterprise automation workflow.",
                    instruction="Set the compound action name to 'critical_alert_incident_response'. This workflow handles critical system alerts automatically.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="critical_alert_incident_response"
                ),
                UnifiedTutorialStep(
                    title="Add ServiceNow Integration",
                    description="Create a ServiceNow incident ticket.",
                    instruction="Add an action step for ServiceNow integration. This will create incident tickets automatically when alerts are triggered.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure ServiceNow Action",
                    description="Set up the ServiceNow ticket creation.",
                    instruction="Configure the action to create ServiceNow incidents with proper categorization and priority based on alert data.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="servicenow.create_incident"
                ),
                UnifiedTutorialStep(
                    title="Add Jira Integration",
                    description="Create corresponding Jira tickets for development tracking.",
                    instruction="Add another action step for Jira integration. This ensures both operations and development teams are notified.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Jira Action",
                    description="Set up Jira ticket creation with proper project assignment.",
                    instruction="Configure the Jira action to create tickets in the appropriate project with links to the ServiceNow incident.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="jira.create_issue"
                ),
                UnifiedTutorialStep(
                    title="Add Parameterization",
                    description="Use variables to make your workflow dynamic.",
                    instruction="Add input parameters that allow the workflow to handle different types of alerts and severity levels dynamically.",
                    target_element="add_input_arg_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Test Enterprise Integration",
                    description="Validate your multi-system automation.",
                    instruction="Use the validation system to ensure your workflow properly integrates with both ServiceNow and Jira systems.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 2 Complete!",
                    description="Excellent! You've built enterprise-grade IT automation.",
                    instruction="Your workflow now handles multi-system integration, parameterization, and proper error handling. Ready for Module 3: Conditional Logic?",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Legacy System Migration",
            plugin_source="legacy_tutorials"
        )
        tutorials.append(module_2)
        
        return tutorials
    
    def initialize(self) -> bool:
        """Initialize the legacy tutorial plugin."""
        # Add deprecation warning for legacy system
        warnings.warn(
            "Legacy tutorial system is deprecated. Please use the unified tutorial system instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return True
