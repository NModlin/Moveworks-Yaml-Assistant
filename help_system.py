"""
Help system for the Moveworks YAML Assistant.

This module provides contextual help, tooltips, and user guidance for the application.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class HelpTopic:
    """Represents a help topic with title, content, and related topics."""
    title: str
    content: str
    category: str = "General"
    related_topics: List[str] = None
    keywords: List[str] = None

    def __post_init__(self):
        if self.related_topics is None:
            self.related_topics = []
        if self.keywords is None:
            self.keywords = []


class HelpSystem:
    """Manages help content and provides search functionality."""

    def __init__(self):
        self.topics = {}
        self._initialize_help_content()

    def _initialize_help_content(self):
        """Initialize the help content database."""
        
        # Getting Started
        self.add_topic(HelpTopic(
            title="Getting Started",
            content="""
Welcome to the Moveworks YAML Assistant!

This application helps you create Moveworks Compound Action workflows through a visual interface.

Basic workflow:
1. Add action or script steps using the buttons on the left
2. Configure each step by selecting it and filling in the details
3. Provide JSON output examples for each step
4. Map variables between steps using the JSON browser
5. Validate and export your workflow

The application automatically generates valid YAML as you work.
            """.strip(),
            category="Getting Started",
            keywords=["start", "begin", "introduction", "workflow", "basic"]
        ))

        # Action Steps
        self.add_topic(HelpTopic(
            title="Action Steps",
            content="""
Action steps represent calls to Moveworks actions or external APIs.

Required fields:
- Action Name: The name of the action (e.g., "mw.get_user_by_email")
- Output Key: Where to store the action's result (e.g., "user_info")

Optional fields:
- Description: Human-readable description of what this action does
- Input Arguments: Key-value pairs passed to the action

Built-in Actions:
Use the "Add Built-in Action" button to select from pre-configured Moveworks actions with example outputs.

JSON Output:
Provide an example of what this action will return. This is used for variable mapping in subsequent steps.
            """.strip(),
            category="Steps",
            keywords=["action", "mw", "api", "call", "built-in"],
            related_topics=["Script Steps", "JSON Output", "Variable Mapping"]
        ))

        # Script Steps
        self.add_topic(HelpTopic(
            title="Script Steps",
            content="""
Script steps contain APIthon (Python-like) code that processes data.

Required fields:
- Code: The APIthon script to execute
- Output Key: Where to store the script's result

The script has access to:
- data.* variables from previous steps
- Input arguments passed to the script
- Standard Python operations and functions

Example script:
```python
user_name = data.user_info.user.name
result = {
    "greeting": f"Hello, {user_name}!",
    "processed": True
}
return result
```

Always include a 'return' statement to provide output for subsequent steps.
            """.strip(),
            category="Steps",
            keywords=["script", "code", "python", "apithon", "processing"],
            related_topics=["Action Steps", "Variable Mapping", "Data Context"]
        ))

        # JSON Output
        self.add_topic(HelpTopic(
            title="JSON Output",
            content="""
JSON Output defines what data a step will produce when executed.

Why it's important:
- Enables variable mapping between steps
- Provides structure for the JSON browser
- Helps with validation and error checking

How to use:
1. Paste or type the expected JSON output in the text area
2. Click "Parse & Save JSON Output" to validate and store it
3. The parsed structure becomes available in the JSON browser

Tips:
- Use realistic example data
- Include all fields that subsequent steps might need
- Ensure valid JSON syntax (use quotes around strings)
- For built-in actions, examples are pre-filled

The JSON browser will show the structure and allow you to select paths for variable mapping.
            """.strip(),
            category="Data",
            keywords=["json", "output", "structure", "data", "example"],
            related_topics=["Variable Mapping", "JSON Browser", "Action Steps"]
        ))

        # Variable Mapping
        self.add_topic(HelpTopic(
            title="Variable Mapping",
            content="""
Variable mapping connects data between workflow steps.

How it works:
1. Each step produces JSON output stored with its output key
2. Subsequent steps can reference this data in their input arguments
3. Use the JSON browser to explore available data and select paths

Data path format:
- data.step_output_key.field_name
- data.user_info.user.name
- data.api_result.items[0].id

Using the JSON browser:
1. Select a previous step from the dropdown
2. Browse the JSON structure in the tree view
3. Click on a field to select its path
4. Copy the path and paste it into input argument values

The system validates that all data references point to available data.
            """.strip(),
            category="Data",
            keywords=["mapping", "variables", "data", "reference", "path"],
            related_topics=["JSON Output", "JSON Browser", "Data Context"]
        ))

        # Validation
        self.add_topic(HelpTopic(
            title="Validation",
            content="""
The validation system ensures your workflow is correct and will execute properly.

Validation checks:
- Required fields are present
- Output keys are unique
- Data references point to available data
- JSON outputs are valid
- Script syntax is correct
- Action names follow proper format

Validation levels:
- Real-time: Basic checks as you type
- On-demand: Press F5 or use Edit > Validate
- Export-time: Full validation before YAML export

Error types:
- Structural: Missing required fields, invalid formats
- Data: Invalid data references, missing JSON outputs
- Syntax: Script compilation errors, malformed JSON

The validation status is shown in the YAML preview panel with color coding:
- Green: No errors found
- Red: Errors detected (hover for details)
            """.strip(),
            category="Validation",
            keywords=["validation", "errors", "check", "verify", "syntax"],
            related_topics=["YAML Preview", "Error Handling"]
        ))

    def add_topic(self, topic: HelpTopic):
        """Add a help topic to the system."""
        self.topics[topic.title] = topic

    def get_topic(self, title: str) -> Optional[HelpTopic]:
        """Get a help topic by title."""
        return self.topics.get(title)

    def search_topics(self, query: str) -> List[HelpTopic]:
        """Search for help topics by query."""
        query_lower = query.lower()
        results = []

        for topic in self.topics.values():
            # Search in title, content, and keywords
            if (query_lower in topic.title.lower() or
                query_lower in topic.content.lower() or
                any(query_lower in keyword.lower() for keyword in topic.keywords)):
                results.append(topic)

        return results

    def get_topics_by_category(self, category: str) -> List[HelpTopic]:
        """Get all topics in a specific category."""
        return [topic for topic in self.topics.values() if topic.category == category]

    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        categories = set(topic.category for topic in self.topics.values())
        return sorted(list(categories))

    def get_related_topics(self, topic_title: str) -> List[HelpTopic]:
        """Get topics related to the given topic."""
        topic = self.get_topic(topic_title)
        if not topic:
            return []

        related = []
        for related_title in topic.related_topics:
            related_topic = self.get_topic(related_title)
            if related_topic:
                related.append(related_topic)

        return related


# Tooltip content for UI elements
TOOLTIPS = {
    "action_name": "The name of the action to execute (e.g., 'mw.get_user_by_email')",
    "output_key": "Unique identifier for storing this step's output (used in data.output_key references)",
    "description": "Optional human-readable description of what this step does",
    "input_args": "Key-value pairs passed as arguments to the action or script",
    "json_output": "Example JSON that this step will produce when executed",
    "script_code": "APIthon (Python-like) code that processes data and returns a result",
    "parse_json": "Validate and save the JSON output for use in variable mapping",
    "add_action": "Add a new action step that calls a Moveworks action or external API",
    "add_script": "Add a new script step that executes APIthon code",
    "add_builtin": "Add a pre-configured Moveworks built-in action with example output",
    "json_browser": "Browse JSON structure from previous steps to select data paths",
    "yaml_preview": "Live preview of the generated YAML with validation status",
    "validation_status": "Shows validation results - hover for error details",
    "step_list": "List of workflow steps - click to select and configure",
    "move_up": "Move the selected step up in the execution order",
    "move_down": "Move the selected step down in the execution order",
    "remove_step": "Remove the selected step from the workflow",
    "save_workflow": "Save the current workflow to a JSON file",
    "load_workflow": "Load a workflow from a JSON file",
    "export_yaml": "Export the workflow as a YAML file for use in Moveworks",
    "validate": "Run comprehensive validation on the current workflow"
}


def get_tooltip(element_id: str) -> str:
    """Get tooltip text for a UI element."""
    return TOOLTIPS.get(element_id, "")


def get_contextual_help(context: str) -> str:
    """Get contextual help based on current application state."""
    help_texts = {
        "empty_workflow": "Start by adding your first step using the buttons on the left.",
        "no_step_selected": "Select a step from the list to configure its properties.",
        "action_step_selected": "Configure the action name, output key, and input arguments. Don't forget to provide JSON output!",
        "script_step_selected": "Write your APIthon code and specify the output key. Include a 'return' statement.",
        "validation_errors": "Fix the validation errors shown in red before exporting your workflow.",
        "no_json_output": "Provide JSON output examples to enable variable mapping between steps.",
        "ready_to_export": "Your workflow is valid and ready to export as YAML!"
    }
    
    return help_texts.get(context, "")


# Global help system instance
help_system = HelpSystem()
