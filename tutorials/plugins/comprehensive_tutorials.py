"""
Comprehensive Tutorial Plugin.

This plugin migrates all tutorials from comprehensive_tutorial_system.py
with complete 5-module curriculum and advanced features.
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


class ComprehensiveTutorialPlugin(TutorialPlugin):
    """Plugin for comprehensive tutorials from comprehensive_tutorial_system.py."""
    
    def get_plugin_id(self) -> str:
        return "comprehensive_tutorials"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Comprehensive Tutorial Series",
            "version": "1.0.0",
            "description": "Complete 5-module curriculum covering all Moveworks features",
            "author": "Moveworks YAML Assistant",
            "source": "comprehensive_tutorial_system.py",
            "module_name": "comprehensive_tutorials",
            "tutorial_count": 5,
            "categories": ["Getting Started", "Expression Types", "Data Handling", "Advanced Features", "Best Practices"],
            "features": ["progressive_curriculum", "comprehensive_coverage", "advanced_features"]
        }
    
    def get_tutorials(self) -> List[UnifiedTutorial]:
        """Return all comprehensive tutorials converted to unified format."""
        tutorials = []
        
        # Module 1: Basic Compound Action (exact content preservation)
        module_1 = UnifiedTutorial(
            id="comprehensive_module_1_basic",
            title="Module 1: Basic Compound Action",
            description="Master the fundamentals of Moveworks compound actions with hands-on practice",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="20 minutes",
            learning_objectives=[
                "Understand compound action structure and YAML compliance",
                "Create your first action step with proper data flow",
                "Use the JSON Path Selector for basic data selection",
                "Generate compliant YAML with mandatory action_name and steps fields",
                "Validate workflow using the built-in compliance system",
                "Master basic data referencing patterns"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to Comprehensive Training",
                    description="Welcome to the comprehensive Moveworks compound action training series!",
                    instruction="This 5-module series will take you from beginner to expert in creating Moveworks workflows. We'll start with the fundamentals and build up to advanced enterprise automation patterns.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Understanding Compound Actions",
                    description="Learn what compound actions are and why they're powerful.",
                    instruction="Compound actions are reusable workflow templates that combine multiple steps into a single, executable unit. They enable complex automation while maintaining simplicity for end users.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Set Your First Compound Action Name",
                    description="Every compound action needs a unique, descriptive name.",
                    instruction="Enter 'employee_lookup_and_notification' as your compound action name. Use lowercase with underscores for Moveworks compliance.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="employee_lookup_and_notification"
                ),
                UnifiedTutorialStep(
                    title="Add Your First Action Step",
                    description="Action steps are the building blocks of compound actions.",
                    instruction="Click 'Add Action Step' to create your first step. This will open the action configuration panel where you'll define what this step does.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Action Name and Output Key",
                    description="Every action needs a name and output key for data referencing.",
                    instruction="Set the action name to 'mw.get_user_by_email' and output key to 'user_data'. The output key creates a data reference you can use in later steps.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.get_user_by_email"
                ),
                UnifiedTutorialStep(
                    title="Add Input Arguments",
                    description="Input arguments provide data to your action.",
                    instruction="Click 'Add Argument' to create an input parameter. Set the key to 'email' and value to 'data.input_email' to reference workflow input.",
                    target_element="add_input_arg_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Provide Sample JSON Output",
                    description="JSON output enables data path selection in later steps.",
                    instruction="Paste the sample JSON below. This represents what the user lookup action will return and enables the JSON Path Selector.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data='{\n  "user": {\n    "id": "user_12345",\n    "name": "John Doe",\n    "email": "john.doe@company.com",\n    "department": "Engineering",\n    "manager": {\n      "name": "Jane Smith",\n      "email": "jane.smith@company.com"\n    },\n    "location": {\n      "office": "San Francisco",\n      "building": "Main Campus",\n      "floor": 3\n    },\n    "employment": {\n      "start_date": "2023-01-15",\n      "position": "Senior Software Engineer",\n      "status": "active"\n    }\n  }\n}',
                    sample_json=get_tutorial_json_data("comprehensive_module_1")
                ),
                UnifiedTutorialStep(
                    title="Parse JSON for Data Selection",
                    description="Parsing JSON enables the JSON Path Selector.",
                    instruction="Click 'Parse & Save JSON Output' to process the JSON structure. This creates a visual data explorer for selecting paths in future steps.",
                    target_element="parse_json_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Add Notification Step",
                    description="Create a second step that uses data from the first step.",
                    instruction="Click 'Add Action Step' again to create a notification step. This will demonstrate how steps can reference each other's data.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Notification Action",
                    description="Set up the notification step with data references.",
                    instruction="Configure the notification action to use data from the user lookup step. Set action name to 'mw.send_notification' and output key to 'notification_result'.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.send_notification"
                ),
                UnifiedTutorialStep(
                    title="Use JSON Path Selector",
                    description="Select data paths from previous steps.",
                    instruction="Click on the 'JSON Explorer' tab to see available data paths from your user lookup step. Try clicking on different paths to see how they're formatted.",
                    target_element="json_path_selector_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Review Generated YAML",
                    description="Examine your complete compound action structure.",
                    instruction="Switch to the 'YAML Preview' tab to see your generated Moveworks-compliant YAML. Notice the structure with action_name at the top level and steps as an array.",
                    target_element="yaml_preview_panel",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Validate Your Compound Action",
                    description="Ensure your workflow meets Moveworks standards.",
                    instruction="Click 'Validate Now' to check for compliance issues. The validator ensures your compound action follows Moveworks best practices.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 1 Complete!",
                    description="Congratulations! You've mastered basic compound actions.",
                    instruction="You've learned compound action structure, action steps, data flow, JSON processing, and validation. You're ready for Module 2: Advanced Expression Types!",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Comprehensive System Migration",
            plugin_source="comprehensive_tutorials"
        )
        tutorials.append(module_1)
        
        # Module 2: Advanced Expression Types (exact content preservation)
        module_2 = UnifiedTutorial(
            id="comprehensive_module_2_expressions",
            title="Module 2: Advanced Expression Types",
            description="Master switch statements, for loops, and conditional logic in compound actions",
            category=TutorialCategory.EXPRESSION_TYPES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="25 minutes",
            prerequisites=["comprehensive_module_1_basic"],
            learning_objectives=[
                "Implement switch statements for conditional branching",
                "Create for loops for data processing and iteration",
                "Use conditional expressions for dynamic behavior",
                "Combine multiple expression types in complex workflows",
                "Handle error conditions with try-catch expressions",
                "Master parallel processing with parallel expressions"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Introduction to Advanced Expressions",
                    description="Learn powerful expression types for complex workflows.",
                    instruction="This module covers advanced expression types that enable sophisticated automation: switch statements, for loops, conditionals, try-catch, and parallel processing.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Create Multi-Department Workflow",
                    description="Build a workflow that handles different departments differently.",
                    instruction="Set the compound action name to 'department_specific_onboarding'. This workflow will use switch statements to handle different onboarding processes.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="department_specific_onboarding"
                ),
                UnifiedTutorialStep(
                    title="Add Switch Expression",
                    description="Use switch statements for conditional logic.",
                    instruction="Click 'Add Switch Step' to create conditional branching. Switch expressions evaluate conditions and execute different steps based on the results.",
                    target_element="add_switch_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Switch Conditions",
                    description="Set up conditions for different departments.",
                    instruction="Configure switch cases for Engineering, Sales, and HR departments. Each case will have different onboarding steps based on the employee's department.",
                    target_element="switch_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="data.user_data.user.department == 'Engineering'"
                ),
                UnifiedTutorialStep(
                    title="Add For Loop Processing",
                    description="Process multiple items with for loops.",
                    instruction="Click 'Add For Loop Step' to create iteration logic. For loops are essential for processing arrays of data like multiple employees or tasks.",
                    target_element="add_for_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Loop Parameters",
                    description="Set up data iteration and processing.",
                    instruction="Configure the for loop to iterate over a list of onboarding tasks. Each iteration will process one task from the array.",
                    target_element="for_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="data.onboarding_tasks"
                ),
                UnifiedTutorialStep(
                    title="Add Error Handling",
                    description="Implement try-catch for robust workflows.",
                    instruction="Click 'Add Try-Catch Step' to add error handling. This ensures your workflow can handle failures gracefully and provide meaningful feedback.",
                    target_element="add_try_catch_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Error Handling",
                    description="Set up try-catch logic for resilient workflows.",
                    instruction="Configure the try-catch to handle potential failures in the onboarding process and provide appropriate fallback actions.",
                    target_element="try_catch_config_panel",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Add Parallel Processing",
                    description="Execute multiple steps simultaneously.",
                    instruction="Click 'Add Parallel Step' to create concurrent execution. Parallel expressions allow multiple operations to run at the same time for efficiency.",
                    target_element="add_parallel_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Parallel Execution",
                    description="Set up concurrent operations.",
                    instruction="Configure parallel branches for simultaneous account creation, equipment ordering, and access provisioning. This reduces total onboarding time.",
                    target_element="parallel_config_panel",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Test Complex Logic",
                    description="Validate your advanced expression workflow.",
                    instruction="Use the validation system to test your complex workflow with multiple expression types. Ensure all conditions and loops are properly configured.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 2 Complete!",
                    description="Excellent! You've mastered advanced expression types.",
                    instruction="You can now create sophisticated workflows with conditional logic, loops, error handling, and parallel processing. Ready for Module 3: Data Processing?",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Comprehensive System Migration",
            plugin_source="comprehensive_tutorials"
        )
        tutorials.append(module_2)
        
        # Module 3: Data Processing and APIthon (exact content preservation)
        module_3 = UnifiedTutorial(
            id="comprehensive_module_3_data_processing",
            title="Module 3: Data Processing and APIthon Scripts",
            description="Master data transformation, APIthon scripting, and advanced data manipulation",
            category=TutorialCategory.DATA_HANDLING,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="30 minutes",
            prerequisites=["comprehensive_module_2_expressions"],
            learning_objectives=[
                "Create APIthon scripts for custom data processing",
                "Implement data transformation patterns",
                "Handle complex JSON data structures",
                "Use Bender functions for data manipulation",
                "Master data validation and error handling",
                "Optimize data processing performance"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Introduction to Data Processing",
                    description="Learn advanced data manipulation techniques.",
                    instruction="This module covers data processing, APIthon scripting, and advanced data transformation patterns essential for enterprise workflows.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Create Data Processing Workflow",
                    description="Build a workflow focused on data transformation.",
                    instruction="Set the compound action name to 'employee_data_processor'. This workflow will demonstrate advanced data processing capabilities.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="employee_data_processor"
                ),
                UnifiedTutorialStep(
                    title="Add APIthon Script Step",
                    description="Create custom data processing with APIthon.",
                    instruction="Click 'Add Script Step' to create an APIthon script. APIthon allows custom Python-like code for complex data transformations.",
                    target_element="add_script_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Write Data Processing Script",
                    description="Implement custom data transformation logic.",
                    instruction="Copy the APIthon script below that processes employee data and creates a formatted summary report.",
                    target_element="script_config_panel",
                    action_type="copy_paste",
                    copy_paste_data=get_tutorial_script_example("comprehensive_module_3")
                ),
                UnifiedTutorialStep(
                    title="Add Bender Function Processing",
                    description="Use Bender functions for data manipulation.",
                    instruction="Add a step that uses Bender functions like MAP, FILTER, and CONDITIONAL to process data arrays efficiently.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Bender Functions",
                    description="Set up advanced data manipulation functions.",
                    instruction="Configure Bender functions to filter, map, and transform employee data. These functions provide powerful data processing capabilities.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="bender.MAP"
                ),
                UnifiedTutorialStep(
                    title="Validate Data Processing",
                    description="Test your data transformation workflow.",
                    instruction="Use the validation system to ensure your data processing logic is correct and handles edge cases properly.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 3 Complete!",
                    description="Outstanding! You've mastered data processing and APIthon.",
                    instruction="You can now create sophisticated data transformation workflows with custom scripts and Bender functions. Ready for Module 4: Enterprise Integration?",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Comprehensive System Migration",
            plugin_source="comprehensive_tutorials"
        )
        tutorials.append(module_3)
        
        # Module 4: Enterprise Integration (exact content preservation)
        module_4 = UnifiedTutorial(
            id="comprehensive_module_4_enterprise",
            title="Module 4: Enterprise Integration",
            description="Master ServiceNow, Jira, and multi-system automation workflows",
            category=TutorialCategory.ADVANCED_FEATURES,
            difficulty=TutorialDifficulty.ADVANCED,
            estimated_time="35 minutes",
            prerequisites=["comprehensive_module_3_data_processing"],
            learning_objectives=[
                "Integrate with ServiceNow for ITSM automation",
                "Connect to Jira for project management workflows",
                "Implement multi-system data synchronization",
                "Handle enterprise authentication and security",
                "Create robust error handling for external systems",
                "Optimize performance for enterprise-scale operations"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Introduction to Enterprise Integration",
                    description="Learn to connect Moveworks with enterprise systems.",
                    instruction="This advanced module covers integration with ServiceNow, Jira, and other enterprise systems for comprehensive automation.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Create Enterprise Automation Workflow",
                    description="Build a multi-system integration workflow.",
                    instruction="Set the compound action name to 'enterprise_incident_automation'. This workflow will integrate ServiceNow and Jira for incident management.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="enterprise_incident_automation"
                ),
                UnifiedTutorialStep(
                    title="Add ServiceNow Integration",
                    description="Connect to ServiceNow for ITSM operations.",
                    instruction="Add an action step for ServiceNow integration. This will create incidents, update records, and query the ServiceNow database.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure ServiceNow Action",
                    description="Set up ServiceNow incident creation.",
                    instruction="Configure the ServiceNow action with proper authentication, table selection, and field mapping for incident creation.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="servicenow.create_incident"
                ),
                UnifiedTutorialStep(
                    title="Add Jira Integration",
                    description="Connect to Jira for project management.",
                    instruction="Add a Jira integration step to create corresponding tickets and link them to ServiceNow incidents for complete tracking.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Jira Action",
                    description="Set up Jira ticket creation and linking.",
                    instruction="Configure the Jira action to create tickets in the appropriate project with proper issue types and links to ServiceNow.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="jira.create_issue"
                ),
                UnifiedTutorialStep(
                    title="Add Data Synchronization",
                    description="Implement multi-system data sync.",
                    instruction="Add steps to synchronize data between ServiceNow and Jira, ensuring consistency across both systems.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Test Enterprise Integration",
                    description="Validate your multi-system workflow.",
                    instruction="Use comprehensive validation to test your enterprise integration workflow with proper error handling and data validation.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Module 4 Complete!",
                    description="Exceptional! You've mastered enterprise integration.",
                    instruction="You can now create sophisticated multi-system workflows that integrate ServiceNow, Jira, and other enterprise platforms. Ready for Module 5: Best Practices?",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Comprehensive System Migration",
            plugin_source="comprehensive_tutorials"
        )
        tutorials.append(module_4)
        
        # Module 5: Best Practices and Optimization (exact content preservation)
        module_5 = UnifiedTutorial(
            id="comprehensive_module_5_best_practices",
            title="Module 5: Best Practices and Optimization",
            description="Master workflow optimization, security, and production deployment strategies",
            category=TutorialCategory.BEST_PRACTICES,
            difficulty=TutorialDifficulty.ADVANCED,
            estimated_time="25 minutes",
            prerequisites=["comprehensive_module_4_enterprise"],
            learning_objectives=[
                "Implement security best practices for workflows",
                "Optimize workflow performance and efficiency",
                "Design for scalability and maintainability",
                "Handle production deployment considerations",
                "Implement comprehensive error handling and logging",
                "Master workflow testing and validation strategies"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Introduction to Best Practices",
                    description="Learn production-ready workflow development.",
                    instruction="This final module covers best practices for creating secure, scalable, and maintainable workflows ready for production deployment.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Security and Compliance",
                    description="Implement security best practices.",
                    instruction="Learn to secure your workflows with proper authentication, data encryption, and compliance with enterprise security policies.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Performance Optimization",
                    description="Optimize workflow efficiency and speed.",
                    instruction="Discover techniques for optimizing workflow performance, reducing execution time, and minimizing resource usage.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Error Handling and Resilience",
                    description="Build robust, fault-tolerant workflows.",
                    instruction="Implement comprehensive error handling, retry logic, and graceful degradation for production-ready workflows.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Testing and Validation",
                    description="Ensure workflow quality and reliability.",
                    instruction="Learn advanced testing strategies, validation techniques, and quality assurance practices for enterprise workflows.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Deployment and Monitoring",
                    description="Deploy and monitor production workflows.",
                    instruction="Master deployment strategies, monitoring setup, and ongoing maintenance practices for production workflows.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Comprehensive Training Complete!",
                    description="Congratulations! You've completed the comprehensive training series.",
                    instruction="You've mastered all aspects of Moveworks compound action development from basics to advanced enterprise integration and best practices. You're now ready to build production-grade automation workflows!",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Comprehensive System Migration",
            plugin_source="comprehensive_tutorials"
        )
        tutorials.append(module_5)
        
        return tutorials
    
    def initialize(self) -> bool:
        """Initialize the comprehensive tutorial plugin."""
        # Add deprecation warning for legacy system
        warnings.warn(
            "Comprehensive tutorial system is deprecated. Please use the unified tutorial system instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return True
