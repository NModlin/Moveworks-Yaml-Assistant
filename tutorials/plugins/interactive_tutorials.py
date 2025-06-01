"""
Interactive Tutorial Plugin.

This plugin migrates all tutorials from integrated_tutorial_system.py
with enhanced copy-paste functionality and real-time interaction features.
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


class InteractiveTutorialPlugin(TutorialPlugin):
    """Plugin for interactive tutorials from integrated_tutorial_system.py."""
    
    def get_plugin_id(self) -> str:
        return "interactive_tutorials"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Interactive Tutorial System",
            "version": "1.0.0",
            "description": "Enhanced tutorials with copy-paste functionality and real-time guidance",
            "author": "Moveworks YAML Assistant",
            "source": "integrated_tutorial_system.py",
            "module_name": "interactive_tutorials",
            "tutorial_count": 3,
            "categories": ["Getting Started", "Data Handling"],
            "features": ["copy_paste", "real_time_interaction", "json_examples"]
        }
    
    def get_tutorials(self) -> List[UnifiedTutorial]:
        """Return all interactive tutorials converted to unified format."""
        tutorials = []
        
        # Interactive Basic Workflow (exact content preservation)
        interactive_basic = UnifiedTutorial(
            id="interactive_basic_workflow",
            title="Interactive Basic Workflow",
            description="Hands-on tutorial with copy-paste examples and real-time guidance",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="10 minutes",
            learning_objectives=[
                "Experience real-time tutorial interaction",
                "Practice copy-paste workflow creation",
                "Learn JSON data exploration",
                "Understand YAML generation process",
                "Master interactive guidance features"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to Interactive Learning",
                    description="This tutorial provides hands-on experience with copy-paste examples.",
                    instruction="You'll create a real workflow while learning. The tutorial panel is draggable - move it if it covers important areas. All examples can be copied with one click.",
                    action_type="info",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Set Action Name with Copy-Paste",
                    description="Let's start by setting the compound action name using our copy-paste feature.",
                    instruction="Use the copy button below to automatically fill the Action Name field, or manually copy and paste the example.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="interactive_demo_workflow",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Add Action Step Interactively",
                    description="Create your first action step with real-time guidance.",
                    instruction="Click the 'Add Action Step' button to create a new step. Watch how the tutorial panel automatically repositions to avoid covering the configuration area.",
                    target_element="add_action_btn",
                    action_type="click",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Configure Action with Examples",
                    description="Set up your action step using provided examples.",
                    instruction="Copy the action name below and paste it into the Action Name field. Notice how the copy button provides visual feedback when clicked.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.interactive_demo_action",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Add JSON with Real-Time Preview",
                    description="Add sample JSON to enable data exploration features.",
                    instruction="Copy the JSON example below into the JSON Output field. This enables the JSON Path Selector and provides real-time data exploration.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data='{\n  "demo_data": {\n    "user": {\n      "name": "Interactive User",\n      "email": "user@demo.com",\n      "preferences": {\n        "tutorial_mode": "interactive",\n        "copy_paste_enabled": true\n      }\n    },\n    "workflow": {\n      "status": "active",\n      "steps_completed": 3,\n      "features_used": ["copy_paste", "json_explorer", "real_time_guidance"]\n    }\n  }\n}',
                    sample_json=get_tutorial_json_data("interactive_basic"),
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Parse JSON for Interactive Exploration",
                    description="Enable interactive JSON data exploration.",
                    instruction="Click 'Parse & Save JSON Output' to process the JSON and activate the interactive JSON Path Selector. This allows you to explore data paths visually.",
                    target_element="parse_json_btn",
                    action_type="click",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Explore JSON Paths Interactively",
                    description="Use the interactive JSON Path Selector.",
                    instruction="Click on the 'JSON Explorer' tab to see the interactive data path selector. Try clicking on different data paths to see how they're formatted for use in workflows.",
                    target_element="json_path_selector_button",
                    action_type="click",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Real-Time YAML Preview",
                    description="See your workflow YAML update in real-time.",
                    instruction="Switch to the 'YAML Preview' tab to see your generated workflow. Notice how it updates automatically as you make changes - this is real-time YAML generation.",
                    target_element="yaml_preview_panel",
                    action_type="click",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Interactive Validation",
                    description="Validate your workflow with real-time feedback.",
                    instruction="Click 'Validate Now' to see interactive validation in action. The system provides immediate feedback on compliance and suggests improvements.",
                    target_element="validate_button",
                    action_type="click",
                    auto_advance=False
                ),
                UnifiedTutorialStep(
                    title="Interactive Tutorial Complete!",
                    description="You've experienced the full interactive tutorial system!",
                    instruction="This tutorial demonstrated copy-paste functionality, real-time guidance, interactive JSON exploration, and live YAML preview. These features make workflow creation faster and more intuitive.",
                    action_type="info",
                    auto_advance=False
                )
            ],
            version="1.0.0",
            author="Interactive System Migration",
            plugin_source="interactive_tutorials"
        )
        tutorials.append(interactive_basic)
        
        # Advanced JSON Processing (exact content preservation)
        json_processing = UnifiedTutorial(
            id="interactive_json_processing",
            title="Advanced JSON Data Processing",
            description="Master JSON data manipulation with interactive examples and copy-paste workflows",
            category=TutorialCategory.DATA_HANDLING,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="15 minutes",
            prerequisites=["interactive_basic_workflow"],
            learning_objectives=[
                "Process complex JSON data structures",
                "Use interactive JSON Path Selector effectively",
                "Implement data transformation patterns",
                "Handle nested data with copy-paste examples",
                "Master real-time data exploration"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Introduction to JSON Processing",
                    description="Learn to handle complex JSON data in workflows.",
                    instruction="This tutorial covers advanced JSON processing techniques using interactive tools and copy-paste examples for complex data structures.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Load Complex JSON Data",
                    description="Start with a complex, nested JSON structure.",
                    instruction="Copy the complex JSON example below. This represents real-world data with nested objects, arrays, and multiple data types.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data='{\n  "enterprise_data": {\n    "employees": [\n      {\n        "id": "emp_001",\n        "personal": {\n          "name": "Alice Johnson",\n          "email": "alice@company.com",\n          "department": "Engineering"\n        },\n        "projects": [\n          {"name": "Project Alpha", "status": "active", "priority": "high"},\n          {"name": "Project Beta", "status": "completed", "priority": "medium"}\n        ],\n        "skills": ["Python", "JavaScript", "SQL"],\n        "performance": {\n          "rating": 4.8,\n          "reviews": [\n            {"quarter": "Q1", "score": 4.7},\n            {"quarter": "Q2", "score": 4.9}\n          ]\n        }\n      }\n    ],\n    "metadata": {\n      "last_updated": "2024-01-15",\n      "data_source": "HR_System",\n      "record_count": 1\n    }\n  }\n}',
                    sample_json=get_tutorial_json_data("interactive_json_processing")
                ),
                UnifiedTutorialStep(
                    title="Interactive Path Exploration",
                    description="Use the JSON Path Selector to explore nested data.",
                    instruction="Parse the JSON and use the interactive path selector to explore different data paths. Try clicking on nested objects and arrays to see how paths are constructed.",
                    target_element="parse_json_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Extract Nested Data",
                    description="Learn to reference deeply nested data values.",
                    instruction="Use the path selector to find the employee's email address. Copy the generated path and see how it references nested data: data.output_key.enterprise_data.employees[0].personal.email",
                    target_element="json_path_selector_button",
                    action_type="click",
                    copy_paste_data="data.output_key.enterprise_data.employees[0].personal.email"
                ),
                UnifiedTutorialStep(
                    title="Process Array Data",
                    description="Handle arrays and collections in JSON data.",
                    instruction="Explore how to reference array elements and iterate over collections. The path selector shows different ways to access array data.",
                    target_element="json_path_selector_button",
                    action_type="info",
                    copy_paste_data="data.output_key.enterprise_data.employees[0].projects"
                ),
                UnifiedTutorialStep(
                    title="Create Data Transformation",
                    description="Build a workflow that transforms the JSON data.",
                    instruction="Add another action step that uses the extracted data to create a summary report. This demonstrates real-world data processing patterns.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure Data Processing Action",
                    description="Set up the data transformation step.",
                    instruction="Configure the action to process the employee data and create a formatted output using the paths you explored.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.process_employee_data"
                ),
                UnifiedTutorialStep(
                    title="Validate Complex Data Flow",
                    description="Ensure your data processing workflow is correct.",
                    instruction="Use the validation system to check that your data references are correct and the workflow handles the complex JSON structure properly.",
                    target_element="validate_button",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="JSON Processing Mastery Complete!",
                    description="You've mastered advanced JSON data processing!",
                    instruction="You can now handle complex, nested JSON data structures, use interactive path selection, and build sophisticated data transformation workflows.",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Interactive System Migration",
            plugin_source="interactive_tutorials"
        )
        tutorials.append(json_processing)
        
        # Real-Time Workflow Building (exact content preservation)
        realtime_workflow = UnifiedTutorial(
            id="interactive_realtime_building",
            title="Real-Time Workflow Building",
            description="Experience live workflow creation with instant feedback and copy-paste acceleration",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="12 minutes",
            learning_objectives=[
                "Build workflows with real-time feedback",
                "Use copy-paste to accelerate development",
                "Experience live YAML generation",
                "Master interactive validation",
                "Understand instant preview features"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Real-Time Workflow Creation",
                    description="Build workflows with instant visual feedback.",
                    instruction="This tutorial demonstrates real-time workflow building where every change is immediately reflected in the YAML preview and validation system.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Start with Quick Setup",
                    description="Use copy-paste for rapid workflow initialization.",
                    instruction="Copy the workflow name below to quickly set up your compound action. Notice how the YAML preview updates instantly.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="realtime_demo_workflow"
                ),
                UnifiedTutorialStep(
                    title="Add Steps with Live Preview",
                    description="Watch the YAML update as you add each step.",
                    instruction="Add an action step and observe how the YAML structure updates in real-time. The preview panel shows exactly what will be generated.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configure with Instant Validation",
                    description="See validation feedback as you type.",
                    instruction="Configure your action step and watch the validation indicators update in real-time. Green indicators show compliance, red shows issues.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.realtime_action"
                ),
                UnifiedTutorialStep(
                    title="Experience Live YAML Generation",
                    description="See your workflow YAML generated instantly.",
                    instruction="Switch to the YAML preview tab and make changes to see how the YAML updates immediately. This is live code generation in action.",
                    target_element="yaml_preview_panel",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Real-Time Building Complete!",
                    description="You've experienced the power of real-time workflow building!",
                    instruction="Real-time feedback, instant validation, and live YAML generation make workflow creation faster and more reliable than ever before.",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Interactive System Migration",
            plugin_source="interactive_tutorials"
        )
        tutorials.append(realtime_workflow)
        
        return tutorials
    
    def initialize(self) -> bool:
        """Initialize the interactive tutorial plugin."""
        # Add deprecation warning for legacy system
        warnings.warn(
            "Integrated tutorial system is deprecated. Please use the unified tutorial system instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return True
