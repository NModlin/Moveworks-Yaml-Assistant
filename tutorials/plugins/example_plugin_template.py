"""
Example Tutorial Plugin Template.

This is a complete, working example plugin that developers can use as a starting point
for creating their own tutorial plugins. Copy this file and modify it for your needs.

To use this template:
1. Copy this file to a new name (e.g., my_custom_plugin.py)
2. Update the plugin metadata (name, description, author, etc.)
3. Modify the tutorial content to match your requirements
4. Test the plugin by placing it in tutorials/plugins/ directory
5. Verify it appears in the tutorial system

Author: Moveworks YAML Assistant Team
Version: 1.0.0
"""

from typing import Dict, Any, List
from tutorials.unified_tutorial_system import (
    TutorialPlugin, UnifiedTutorial, UnifiedTutorialStep,
    TutorialCategory, TutorialDifficulty
)

# Import tutorial data for JSON examples (with fallback)
try:
    from tutorial_data import get_tutorial_json_data, get_tutorial_script_example
except ImportError:
    # Fallback if tutorial_data is not available
    def get_tutorial_json_data(tutorial_id: str, step_type: str = "user"):
        return {
            "example_data": {
                "user": {
                    "name": "Example User",
                    "email": "user@example.com",
                    "department": "Example Department"
                },
                "workflow": {
                    "status": "active",
                    "created": "2024-01-15"
                }
            }
        }
    
    def get_tutorial_script_example(tutorial_id: str):
        return "# Example script\nuser_name = data.example_output.example_data.user.name\nreturn {'greeting': f'Hello, {user_name}!'}"


class ExampleTutorialPlugin(TutorialPlugin):
    """
    Example tutorial plugin demonstrating the plugin architecture.
    
    This plugin provides sample tutorials that showcase different tutorial features
    and can be used as a template for creating new plugins.
    """
    
    def get_plugin_id(self) -> str:
        """Return unique plugin identifier."""
        return "example_plugin_template"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata including name, version, description."""
        return {
            "name": "Example Tutorial Plugin Template",
            "version": "1.0.0",
            "description": "Template plugin demonstrating tutorial creation patterns",
            "author": "Moveworks YAML Assistant Team",
            "module_name": "example_plugin_template",
            "tutorial_count": 2,
            "categories": ["Getting Started", "Best Practices"],
            "features": ["template_example", "copy_paste_demo", "step_by_step_guidance"],
            "documentation": "This is a template plugin for developers to use as a starting point"
        }
    
    def get_tutorials(self) -> List[UnifiedTutorial]:
        """Return list of tutorials provided by this plugin."""
        tutorials = []
        
        # Add the basic example tutorial
        basic_tutorial = self._create_basic_example_tutorial()
        tutorials.append(basic_tutorial)
        
        # Add the advanced example tutorial
        advanced_tutorial = self._create_advanced_example_tutorial()
        tutorials.append(advanced_tutorial)
        
        return tutorials
    
    def _create_basic_example_tutorial(self) -> UnifiedTutorial:
        """Create a basic example tutorial demonstrating core features."""
        return UnifiedTutorial(
            id="example_basic_tutorial",
            title="Basic Tutorial Example",
            description="A simple tutorial demonstrating basic tutorial features and patterns",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="8 minutes",
            learning_objectives=[
                "Understand basic tutorial structure",
                "Learn to use copy-paste functionality",
                "Experience step-by-step guidance",
                "Practice with simple workflow creation"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Welcome to the Example Tutorial",
                    description="This tutorial demonstrates basic tutorial features",
                    instruction="Welcome! This is an example tutorial that shows how tutorials work in the Moveworks YAML Assistant. You'll learn the basic patterns and features available in the tutorial system.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Copy-Paste Example",
                    description="Learn how copy-paste functionality works",
                    instruction="This step demonstrates copy-paste functionality. Click the copy button below to copy the example text, then paste it into the compound action name field.",
                    target_element="compound_action_name_field",
                    action_type="copy_paste",
                    copy_paste_data="example_basic_workflow"
                ),
                UnifiedTutorialStep(
                    title="Interactive Element Targeting",
                    description="See how tutorials can guide you to specific UI elements",
                    instruction="This step shows how tutorials can direct you to specific parts of the interface. Click the 'Add Action Step' button to create a new workflow step.",
                    target_element="add_action_btn",
                    action_type="click"
                ),
                UnifiedTutorialStep(
                    title="Configuration with Examples",
                    description="Configure workflow elements using provided examples",
                    instruction="Now configure your action step using the example below. Copy the action name and paste it into the action configuration panel.",
                    target_element="action_config_panel",
                    action_type="copy_paste",
                    copy_paste_data="mw.example_action"
                ),
                UnifiedTutorialStep(
                    title="JSON Data Example",
                    description="Add sample JSON data to your workflow",
                    instruction="Copy the JSON example below and add it to your action step. This demonstrates how to include sample data in tutorials.",
                    target_element="json_output_edit",
                    action_type="copy_paste",
                    copy_paste_data='{\n  "example_response": {\n    "status": "success",\n    "data": {\n      "message": "Example tutorial completed",\n      "user": "tutorial_user",\n      "timestamp": "2024-01-15T10:30:00Z"\n    }\n  }\n}',
                    sample_json=get_tutorial_json_data("example_basic")
                ),
                UnifiedTutorialStep(
                    title="Basic Tutorial Complete",
                    description="You've completed the basic example tutorial!",
                    instruction="Congratulations! You've learned the basic tutorial features including copy-paste functionality, element targeting, and JSON examples. These patterns can be used in any tutorial plugin.",
                    action_type="info"
                )
            ],
            version="1.0.0",
            author="Example Plugin Template",
            plugin_source="example_plugin_template"
        )
    
    def _create_advanced_example_tutorial(self) -> UnifiedTutorial:
        """Create an advanced example tutorial demonstrating complex features."""
        return UnifiedTutorial(
            id="example_advanced_tutorial",
            title="Advanced Tutorial Features",
            description="Demonstrates advanced tutorial features like validation, highlighting, and complex workflows",
            category=TutorialCategory.BEST_PRACTICES,
            difficulty=TutorialDifficulty.INTERMEDIATE,
            estimated_time="12 minutes",
            prerequisites=["example_basic_tutorial"],
            learning_objectives=[
                "Use advanced tutorial features",
                "Implement validation steps",
                "Handle complex workflow patterns",
                "Create comprehensive learning experiences"
            ],
            steps=[
                UnifiedTutorialStep(
                    title="Advanced Tutorial Introduction",
                    description="Learn about advanced tutorial capabilities",
                    instruction="This tutorial demonstrates advanced features like validation, element highlighting, and complex workflow patterns that make tutorials more interactive and educational.",
                    action_type="info"
                ),
                UnifiedTutorialStep(
                    title="Element Highlighting",
                    description="See how tutorials can highlight specific UI elements",
                    instruction="This step demonstrates element highlighting. The target element will be highlighted to draw your attention to important parts of the interface.",
                    target_element="compound_action_name_field",
                    action_type="highlight",
                    highlight_color="#4a86e8"
                ),
                UnifiedTutorialStep(
                    title="Validation Step Example",
                    description="Learn how tutorials can include validation",
                    instruction="This step shows how tutorials can include validation to ensure users complete tasks correctly. Click the validate button to check your workflow.",
                    target_element="validate_button",
                    action_type="validate"
                ),
                UnifiedTutorialStep(
                    title="Complex Copy-Paste Example",
                    description="Handle multi-line and complex copy-paste content",
                    instruction="This demonstrates copying complex, multi-line content like scripts or configuration files. The content below includes proper formatting and structure.",
                    target_element="script_code_edit",
                    action_type="copy_paste",
                    copy_paste_data=get_tutorial_script_example("example_advanced")
                ),
                UnifiedTutorialStep(
                    title="Auto-Advance Example",
                    description="Demonstrate automatic step advancement",
                    instruction="This step will automatically advance after a short delay, demonstrating how tutorials can control pacing and flow.",
                    action_type="wait",
                    auto_advance=True,
                    delay_ms=3000
                ),
                UnifiedTutorialStep(
                    title="Advanced Tutorial Complete",
                    description="You've mastered advanced tutorial features!",
                    instruction="Excellent work! You've learned advanced tutorial features including highlighting, validation, complex copy-paste, and auto-advancement. These techniques create rich, interactive learning experiences.",
                    action_type="info"
                )
            ],
            tags=["advanced", "validation", "highlighting", "auto-advance"],
            completion_reward="You've mastered advanced tutorial development patterns!",
            version="1.0.0",
            author="Example Plugin Template",
            plugin_source="example_plugin_template"
        )
    
    def initialize(self) -> bool:
        """Initialize plugin. Return True if successful."""
        # Add any initialization logic here
        # For example: validate dependencies, set up resources, etc.
        print("✓ Example tutorial plugin initialized successfully")
        return True
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        # Add cleanup logic here
        # For example: close files, release resources, etc.
        print("✓ Example tutorial plugin cleaned up successfully")


# Plugin registration (optional - the PluginManager handles discovery automatically)
# This is included for documentation purposes to show how plugins are structured
def get_plugin_class():
    """Return the plugin class for manual registration."""
    return ExampleTutorialPlugin


# Development testing (optional - for testing during development)
if __name__ == "__main__":
    # Test the plugin directly
    plugin = ExampleTutorialPlugin()
    
    print("Testing Example Tutorial Plugin")
    print("=" * 40)
    
    # Test metadata
    metadata = plugin.get_metadata()
    print(f"Plugin: {metadata['name']}")
    print(f"Version: {metadata['version']}")
    print(f"Author: {metadata['author']}")
    
    # Test tutorials
    tutorials = plugin.get_tutorials()
    print(f"Tutorials: {len(tutorials)}")
    
    for tutorial in tutorials:
        print(f"  - {tutorial.title} ({tutorial.difficulty.value}, {tutorial.estimated_time})")
        print(f"    Steps: {len(tutorial.steps)}")
        print(f"    Objectives: {len(tutorial.learning_objectives)}")
    
    print("✓ Plugin test completed successfully")
