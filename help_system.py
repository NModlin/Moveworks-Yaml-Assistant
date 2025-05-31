"""
Comprehensive Help System for the Enhanced Moveworks YAML Assistant.

This module provides contextual help, tutorials, tooltips, and user guidance
for all features of the application including all expression types, enhanced
features, and advanced functionality.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json


@dataclass
class HelpTopic:
    """Represents a comprehensive help topic with multimedia support."""
    title: str
    content: str
    category: str = "General"
    subcategory: str = ""
    difficulty: str = "Beginner"  # Beginner, Intermediate, Advanced
    related_topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)  # Code examples
    screenshots: List[str] = field(default_factory=list)  # Screenshot paths
    video_url: str = ""  # Tutorial video URL
    estimated_time: str = "2 minutes"  # Reading/completion time
    prerequisites: List[str] = field(default_factory=list)  # Required knowledge


@dataclass
class HelpSection:
    """Represents a major help section with multiple topics."""
    title: str
    description: str
    icon: str = "📖"
    topics: List[str] = field(default_factory=list)
    order: int = 0


class ComprehensiveHelpSystem:
    """
    Enhanced help system with complete documentation for all features.

    Provides:
    - Complete feature documentation
    - Interactive tutorials
    - Contextual help
    - Search functionality
    - Progressive learning paths
    - Multimedia support
    """

    def __init__(self):
        self.topics: Dict[str, HelpTopic] = {}
        self.sections: Dict[str, HelpSection] = {}
        self._initialize_comprehensive_help()

    def _initialize_comprehensive_help(self):
        """Initialize comprehensive help content for all features."""

        # Initialize help sections first
        self._initialize_help_sections()

        # Initialize all help topics
        self._initialize_getting_started()
        self._initialize_expression_types_help()
        self._initialize_enhanced_features_help()
        self._initialize_workflow_management_help()
        self._initialize_data_handling_help()
        self._initialize_dsl_help()  # New DSL-specific help
        self._initialize_validation_help()
        self._initialize_templates_help()
        self._initialize_advanced_features_help()
        self._initialize_troubleshooting_help()
        self._initialize_best_practices_help()

    def _initialize_help_sections(self):
        """Initialize major help sections."""
        sections = [
            HelpSection(
                title="Getting Started",
                description="Essential information for new users",
                icon="🚀",
                order=1
            ),
            HelpSection(
                title="Expression Types",
                description="Complete guide to all 8 Moveworks expression types",
                icon="🔧",
                order=2
            ),
            HelpSection(
                title="Enhanced Features",
                description="Advanced features and tools",
                icon="⭐",
                order=3
            ),
            HelpSection(
                title="Workflow Management",
                description="Creating, editing, and organizing workflows",
                icon="📋",
                order=4
            ),
            HelpSection(
                title="Data Handling",
                description="Working with JSON data and variable mapping",
                icon="🔄",
                order=5
            ),
            HelpSection(
                title="DSL & Data Mapping",
                description="Moveworks Data Mapping Syntax (DSL) expressions and functions",
                icon="🔗",
                order=6
            ),
            HelpSection(
                title="Validation & Testing",
                description="Ensuring workflow quality and correctness",
                icon="✅",
                order=7
            ),
            HelpSection(
                title="Templates & Examples",
                description="Pre-built templates and example workflows",
                icon="📚",
                order=8
            ),
            HelpSection(
                title="Advanced Features",
                description="Power user features and customization",
                icon="🎯",
                order=9
            ),
            HelpSection(
                title="Troubleshooting",
                description="Common issues and solutions",
                icon="🔧",
                order=10
            ),
            HelpSection(
                title="Best Practices",
                description="Tips and recommendations for optimal workflows",
                icon="💡",
                order=11
            )
        ]

        for section in sections:
            self.sections[section.title] = section

    def _initialize_getting_started(self):
        """Initialize getting started help topics."""

        # Application Overview
        self.add_topic(HelpTopic(
            title="Application Overview",
            content="""
# Enhanced Moveworks YAML Assistant

Welcome to the most comprehensive tool for creating Moveworks Compound Action workflows!

## What This Application Does

The Enhanced Moveworks YAML Assistant is a visual workflow builder that helps you create complex automation workflows for the Moveworks platform. It provides:

### 🎯 Complete Expression Support
- **All 8 Expression Types**: action, script, switch, for, parallel, return, raise, try_catch
- **Perfect YAML Compliance**: Generates YAML that matches Moveworks specifications exactly
- **Visual Workflow Builder**: Drag-and-drop interface for easy workflow creation

### 🚀 Enhanced Features
- **Intelligent Validation**: Real-time error checking with fix suggestions
- **Template Library**: Pre-built workflows for common use cases
- **JSON Path Selector**: Visual tool for mapping data between steps
- **Interactive Tutorials**: Step-by-step guidance for all features
- **Contextual Examples**: Smart examples that adapt to your current work

### 💡 Key Benefits
- **Faster Development**: Build workflows 10x faster than manual YAML editing
- **Fewer Errors**: Intelligent validation prevents common mistakes
- **Better Learning**: Interactive tutorials and examples teach best practices
- **Professional Results**: Generate production-ready YAML workflows

## Who Should Use This

- **Workflow Developers**: Create complex automation workflows
- **IT Administrators**: Build service management automations
- **Business Analysts**: Design process automation workflows
- **Beginners**: Learn Moveworks workflow development with guided tutorials
- **Experts**: Use advanced features for complex enterprise workflows

## Getting Started

1. **Start with Tutorials**: Click Help → Tutorials to begin learning
2. **Explore Templates**: Browse pre-built workflows in the Template Library
3. **Build Your First Workflow**: Follow the "Your First Workflow" tutorial
4. **Use Examples**: Check the Examples panel for context-aware help
5. **Validate Often**: Use the validation system to ensure quality

Ready to begin? Start with the "Your First Workflow" tutorial!
            """.strip(),
            category="Getting Started",
            difficulty="Beginner",
            keywords=["overview", "introduction", "welcome", "features", "benefits"],
            estimated_time="3 minutes",
            related_topics=["Your First Workflow", "Interface Overview", "Key Concepts"]
        ))

        # Interface Overview
        self.add_topic(HelpTopic(
            title="Interface Overview",
            content="""
# Application Interface Guide

The Enhanced Moveworks YAML Assistant uses a three-panel layout designed for efficient workflow creation.

## Main Interface Layout

### 🔧 Left Panel: Workflow Builder
**Purpose**: Create and manage your workflow steps

**Components**:
- **Compound Action Name**: Input field for naming your compound action (required for Moveworks compliance)
- **Add Step Buttons**: Create new action, script, or control flow steps
- **Step List**: Shows all steps in your workflow
- **Step Controls**: Move, copy, delete, and reorder steps
- **Workflow Actions**: Save, load, and export workflows

**Key Features**:
- Compound action naming for Moveworks compliance
- Drag-and-drop step reordering
- Visual step type indicators
- Quick step duplication
- Workflow validation status

### 📝 Center Panel: Configuration & Examples
**Purpose**: Configure selected steps and access help

**Tabs**:
1. **Configuration Tab**:
   - Step properties (name, output key, etc.)
   - Input arguments editor
   - JSON output specification
   - Advanced settings

2. **Examples Tab**:
   - Context-aware code examples
   - Best practice patterns
   - Copy-paste ready snippets
   - Explanation and use cases

### 🔍 Right Panel: Data & Preview
**Purpose**: Work with data and preview results

**Tabs**:
1. **JSON Path Selector**:
   - Visual JSON structure browser
   - Point-and-click data selection
   - Path validation and preview
   - Array handling tools

2. **YAML Preview**:
   - Live YAML generation
   - Syntax highlighting
   - Validation indicators
   - Export options

3. **Validation Results**:
   - Real-time error checking
   - Fix suggestions
   - Warning explanations
   - Quality metrics

## Menu System

### File Menu
- **New Workflow**: Start fresh
- **Open Workflow**: Load existing workflow
- **Save/Save As**: Preserve your work
- **Export YAML**: Generate final output
- **Recent Files**: Quick access to recent work

### Edit Menu
- **Undo/Redo**: Workflow changes
- **Copy/Paste Steps**: Duplicate configurations
- **Find/Replace**: Search workflow content
- **Preferences**: Customize application

### View Menu
- **Panel Visibility**: Show/hide panels
- **Zoom Controls**: Adjust interface size
- **Themes**: Light/dark mode
- **Layout Options**: Customize arrangement

### Tools Menu
- **Validate Workflow**: Comprehensive checking
- **Template Browser**: Access pre-built workflows
- **JSON Path Tester**: Test data paths
- **Bulk Operations**: Multi-step actions

### Help Menu
- **Tutorials**: Interactive learning
- **Documentation**: Complete reference
- **Examples**: Sample workflows
- **Support**: Get assistance

## Keyboard Shortcuts

### Essential Shortcuts
- **Ctrl+N**: New workflow
- **Ctrl+O**: Open workflow
- **Ctrl+S**: Save workflow
- **Ctrl+E**: Export YAML
- **F5**: Validate workflow
- **F1**: Show help

### Step Management
- **Ctrl+A**: Add action step
- **Ctrl+Shift+A**: Add script step
- **Delete**: Remove selected step
- **Ctrl+Up/Down**: Move step
- **Ctrl+D**: Duplicate step

### Navigation
- **Tab**: Next panel
- **Shift+Tab**: Previous panel
- **Ctrl+1/2/3**: Switch to panel
- **Escape**: Clear selection

## Status Indicators

### Workflow Status
- 🟢 **Green**: Workflow is valid and ready
- 🟡 **Yellow**: Warnings present but functional
- 🔴 **Red**: Errors must be fixed
- ⚪ **Gray**: No validation performed yet

### Step Status
- ✅ **Checkmark**: Step is properly configured
- ⚠️ **Warning**: Minor issues or suggestions
- ❌ **Error**: Critical issues requiring attention
- 📝 **Pencil**: Step needs configuration

## Tips for Efficient Use

1. **Use Keyboard Shortcuts**: Speed up common operations
2. **Keep Validation Panel Open**: Catch errors early
3. **Leverage Templates**: Start with proven patterns
4. **Use Examples Panel**: Learn from context-aware suggestions
5. **Save Frequently**: Preserve your work regularly
6. **Validate Often**: Check quality throughout development

The interface is designed to support both beginners and experts. Start with the tutorials to learn the basics, then explore advanced features as you become more comfortable.
            """.strip(),
            category="Getting Started",
            difficulty="Beginner",
            keywords=["interface", "layout", "panels", "navigation", "shortcuts"],
            estimated_time="5 minutes",
            related_topics=["Application Overview", "Your First Workflow", "Keyboard Shortcuts"],
            prerequisites=["Application Overview"]
        ))

        # Compound Action Name
        self.add_topic(HelpTopic(
            title="Compound Action Name",
            content="""
# Compound Action Name

The Compound Action Name is a **mandatory field** that identifies your entire workflow in the Moveworks platform.

## What is a Compound Action Name?

A compound action name is the unique identifier for your complete workflow. It's different from individual step names:

- **Compound Action Name**: Identifies the entire workflow (e.g., "user_onboarding_workflow")
- **Step Action Names**: Identify individual actions within steps (e.g., "mw.get_user_by_email")

## Why is it Required?

Moveworks requires all workflows to follow a specific YAML structure:

```yaml
action_name: your_compound_action_name  # ← This is the compound action name
steps:                                  # ← Your workflow steps go here
  - action:
      action_name: mw.get_user_by_email # ← This is a step action name
      output_key: user_info
```

## Naming Conventions

### ✅ Good Names
- `user_onboarding_workflow`
- `ticket_escalation_process`
- `employee_offboarding`
- `service_request_handler`

### ❌ Avoid These
- Names with spaces: `user onboarding workflow`
- Special characters: `user-onboarding@workflow`
- Too generic: `workflow1`, `test`
- Too long: `very_long_compound_action_name_that_is_hard_to_read`

## Best Practices

1. **Use descriptive names**: Clearly indicate what the workflow does
2. **Use underscores**: Separate words with underscores, not spaces or hyphens
3. **Keep it concise**: Aim for 2-4 words maximum
4. **Be specific**: Avoid generic terms like "workflow" or "process" unless necessary
5. **Use lowercase**: Follow standard naming conventions

## How to Set the Name

1. **Location**: Find the "Compound Action Name" field in the left panel
2. **Default Value**: The field starts with "compound_action"
3. **Change It**: Replace with your desired name
4. **Real-time Update**: The YAML preview updates automatically

## Impact on YAML Output

The compound action name becomes the top-level `action_name` field in your generated YAML:

```yaml
action_name: my_workflow_name  # ← Your compound action name here
steps:
  - action:
      action_name: mw.get_user_by_email
      output_key: user_info
  - script:
      code: |
        # Your script code here
      output_key: processed_data
```

## Validation

The system validates that:
- ✅ The name is not empty
- ✅ The name follows naming conventions
- ✅ The name is included in all YAML exports

**Remember**: This name identifies your entire workflow in the Moveworks platform, so choose it carefully!
            """.strip(),
            category="Getting Started",
            subcategory="Essential Concepts",
            difficulty="Beginner",
            keywords=["compound", "action", "name", "workflow", "identifier", "yaml", "moveworks"],
            estimated_time="3 minutes",
            related_topics=["YAML Structure", "Moveworks Compliance", "Workflow Creation"],
            examples=[
                "user_onboarding_workflow",
                "ticket_escalation_process",
                "employee_offboarding",
                "service_request_handler"
            ]
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

        # YAML Structure
        self.add_topic(HelpTopic(
            title="YAML Structure & Moveworks Compliance",
            content="""
# YAML Structure & Moveworks Compliance

The Enhanced Moveworks YAML Assistant generates YAML that strictly follows Moveworks compound action requirements.

## Mandatory Compound Action Structure

All generated YAML follows this **required** structure:

```yaml
action_name: your_compound_action_name  # ← Mandatory top-level field
steps:                                  # ← Mandatory steps array
  - action:                            # ← Individual workflow steps
      action_name: mw.get_user_by_email
      output_key: user_info
      input_args:
        email: data.input_email
  - script:
      code: |
        # Your APIthon script here
        result = {"processed": True}
        return result
      output_key: processed_data
```

## Key Requirements

### 1. Top-Level Fields (Mandatory)
- **`action_name`**: String identifying the compound action
- **`steps`**: Array containing all workflow steps

### 2. Data Type Enforcement
- **`input_args`**: Must be a dictionary/object
- **`delay_config.delay_seconds`**: Must be an integer
- **`progress_updates`**: Must be a dictionary/object
- **`on_status_code`**: Must be integer or array of integers

### 3. Step Wrapping
- **All steps** are wrapped in the `steps` array for consistency
- **Single step workflows** still use the array format
- **Multiple step workflows** maintain the same structure

## Differences from Basic YAML

### ❌ Old Format (Non-Compliant)
```yaml
# This format is NOT Moveworks compliant
action:
  action_name: mw.get_user_by_email
  output_key: user_info
```

### ✅ New Format (Moveworks Compliant)
```yaml
# This format IS Moveworks compliant
action_name: my_workflow_name
steps:
  - action:
      action_name: mw.get_user_by_email
      output_key: user_info
```

## Enhanced Features

### 1. Automatic Type Validation
The system automatically ensures:
- Dictionary fields are properly formatted
- Integer fields contain valid numbers
- String fields are properly quoted
- Arrays are correctly structured

### 2. Literal Block Scalars for Scripts
APIthon scripts use proper YAML literal block format:

```yaml
script:
  code: |
    # Multi-line script with proper formatting
    user_name = data.user_info.name
    result = {
        "greeting": f"Hello, {user_name}!",
        "processed": True
    }
    return result
  output_key: processed_data
```

### 3. Consistent Field Ordering
Fields are ordered for optimal readability:
1. `action_name` or `code` (primary identifier)
2. `output_key` (result destination)
3. `input_args` (input parameters)
4. `description` (documentation)
5. Additional configuration fields

## Validation Benefits

The enhanced YAML generation provides:

- **✅ Guaranteed Compliance**: All output follows Moveworks requirements
- **✅ Type Safety**: Automatic data type enforcement
- **✅ Structure Validation**: Proper nesting and field organization
- **✅ Format Consistency**: Standardized output across all workflows

## Export Process

When you export YAML:

1. **Compound Action Name**: Taken from the left panel input field
2. **Steps Array**: Generated from your workflow steps
3. **Type Enforcement**: All fields validated and properly typed
4. **Format Compliance**: Structure verified against Moveworks requirements

## Best Practices

1. **Always Set Action Name**: Use the compound action name field
2. **Validate Before Export**: Check for compliance issues
3. **Review Generated YAML**: Verify the structure meets your needs
4. **Test with Moveworks**: Validate the YAML works in your environment

The enhanced YAML generation ensures your workflows are always Moveworks-compliant and ready for production use.
            """.strip(),
            category="Getting Started",
            subcategory="Essential Concepts",
            difficulty="Intermediate",
            keywords=["yaml", "structure", "compliance", "moveworks", "format", "mandatory"],
            estimated_time="5 minutes",
            related_topics=["Compound Action Name", "YAML Export", "Validation"],
            examples=[
                "action_name: user_lookup_workflow",
                "steps: [...]",
                "input_args: {email: data.input_email}",
                "delay_config: {delay_seconds: 5}"
            ]
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
- Compound action structure compliance

Validation levels:
- Real-time: Basic checks as you type
- On-demand: Full validation when requested
- Pre-export: Complete validation before YAML generation

Status indicators:
- ✅ Green: No issues found
- ⚠️ Yellow: Warnings (workflow works but could be improved)
- ❌ Red: Errors (must be fixed before export)

The validation panel provides detailed error descriptions and suggested fixes.
            """.strip(),
            category="Quality",
            keywords=["validation", "errors", "warnings", "quality", "check"],
            related_topics=["Error Messages", "Best Practices", "YAML Export"]
        ))

        # Add topics to section
        self.sections["Getting Started"].topics.extend([
            "Application Overview",
            "Interface Overview",
            "Your First Workflow",
            "Key Concepts"
        ])

    def _initialize_expression_types_help(self):
        """Initialize help topics for all expression types."""

        # Action Expression
        self.add_topic(HelpTopic(
            title="Action Expression",
            content="""
# Action Expression - Execute HTTP Requests and Moveworks Actions

The **action** expression is the foundation of Moveworks workflows, enabling you to call external APIs, Moveworks built-in actions, and third-party services.

## Basic Structure

```yaml
action:
  action_name: "mw.get_user_by_email"
  output_key: "user_info"
  input_args:
    email: "data.input_email"
  description: "Look up user information by email address"
```

## Required Fields

### action_name
The name of the action to execute. This can be:
- **Moveworks built-ins**: `mw.get_user_by_email`, `mw.create_ticket`, etc.
- **Custom actions**: Your organization's custom API endpoints
- **Third-party APIs**: External service integrations

### output_key
Unique identifier for storing the action's output. Used to reference results in later steps via `data.output_key`.

## Optional Fields

### input_args
Key-value pairs passed as arguments to the action:
```yaml
input_args:
  email: "data.input_email"
  include_manager: true
  fields: ["name", "department", "location"]
```

### description
Human-readable description of what the action does:
```yaml
description: "Retrieve user profile information including manager details"
```

### delay_config
Configure delays and retries:
```yaml
delay_config:
  initial_delay_ms: 1000
  max_retries: 3
  backoff_multiplier: 2.0
```

### progress_updates
Messages shown during execution:
```yaml
progress_updates:
  - "Looking up user information..."
  - "Retrieving manager details..."
```

## Common Patterns

### User Lookup
```yaml
action:
  action_name: "mw.get_user_by_email"
  output_key: "user_data"
  input_args:
    email: "data.user_email"
    include_manager: true
```

### Ticket Creation
```yaml
action:
  action_name: "mw.create_ticket"
  output_key: "new_ticket"
  input_args:
    title: "data.ticket_title"
    description: "data.ticket_description"
    priority: "high"
    assignee: "data.user_data.user.manager.email"
```

### API Integration
```yaml
action:
  action_name: "custom.external_api_call"
  output_key: "api_response"
  input_args:
    endpoint: "/users/profile"
    method: "GET"
    headers:
      Authorization: "Bearer data.auth_token"
    params:
      user_id: "data.user_data.user.id"
```

## Best Practices

1. **Use Descriptive Output Keys**: Choose names that clearly indicate the data type
2. **Provide Meaningful Descriptions**: Help future maintainers understand the purpose
3. **Handle Errors Gracefully**: Use try_catch expressions for critical actions
4. **Validate Input Data**: Ensure required data exists before making calls
5. **Use Progress Updates**: Keep users informed during long-running operations

## Error Handling

Actions can fail for various reasons. Use try_catch expressions to handle failures:

```yaml
try_catch:
  try_block:
    action:
      action_name: "mw.get_user_by_email"
      output_key: "user_info"
      input_args:
        email: "data.input_email"
  catch_block:
    return:
      error: "User not found"
      message: "Unable to locate user with provided email"
```

## Data Output

Actions return JSON data that becomes available to subsequent steps. Always provide JSON output examples to enable proper data mapping:

```json
{
  "user": {
    "id": "emp_12345",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "manager": {
      "id": "mgr_67890",
      "name": "Jane Smith",
      "email": "jane.smith@company.com"
    }
  }
}
```

The action expression is essential for integrating with external systems and forms the backbone of most Moveworks workflows.
            """.strip(),
            category="Expression Types",
            difficulty="Beginner",
            keywords=["action", "api", "call", "http", "request", "moveworks"],
            estimated_time="8 minutes",
            related_topics=["Script Expression", "Input Arguments", "Error Handling"],
            examples=[
                "action:\n  action_name: \"mw.get_user_by_email\"\n  output_key: \"user_info\"\n  input_args:\n    email: \"data.input_email\"",
                "action:\n  action_name: \"mw.create_ticket\"\n  output_key: \"ticket_result\"\n  input_args:\n    title: \"Password Reset Request\"\n    priority: \"high\""
            ]
        ))

        # Script Expression
        self.add_topic(HelpTopic(
            title="Script Expression",
            content="""
# Script Expression - Execute Custom APIthon Code

The **script** expression allows you to execute custom APIthon (Python-like) code to process data, perform calculations, and implement business logic.

## Basic Structure

```yaml
script:
  code: |
    # Process user data
    user = data.user_info.user

    # Create welcome message
    message = f"Welcome, {user.name}! You're in {user.department}."

    # Return processed data
    return {
        "welcome_message": message,
        "user_id": user.id,
        "department": user.department
    }
  output_key: "processed_data"
  description: "Process user information and create welcome message"
```

## Required Fields

### code
The APIthon script to execute. Must include a `return` statement to produce output.

### output_key
Unique identifier for storing the script's output.

## Optional Fields

### description
Human-readable description of what the script does.

### input_args
Additional variables available to the script (beyond the standard data context).

## APIthon Language Features

APIthon is a Python-like language with these capabilities:

### Data Types
- **Strings**: `"Hello, world!"`
- **Numbers**: `42`, `3.14`
- **Booleans**: `True`, `False`
- **Lists**: `[1, 2, 3]`
- **Dictionaries**: `{"key": "value"}`

### Control Flow
```python
# Conditional statements
if user.department == "Engineering":
    priority = "high"
elif user.department == "Sales":
    priority = "medium"
else:
    priority = "low"

# Loops
for ticket in data.tickets:
    if ticket.status == "open":
        open_count += 1
```

### String Operations
```python
# String formatting
message = f"Hello, {user.name}!"

# String methods
email_domain = user.email.split("@")[1]
name_upper = user.name.upper()
```

### List Operations
```python
# List comprehensions
open_tickets = [t for t in data.tickets if t.status == "open"]

# List methods
ticket_ids = [ticket.id for ticket in data.tickets]
total_tickets = len(data.tickets)
```

## Data Access Patterns

### Accessing Previous Step Data
```python
# Get data from previous steps
user = data.user_lookup.user
tickets = data.ticket_search.tickets

# Access nested data
manager_email = data.user_lookup.user.manager.email
```

### Working with Arrays
```python
# Process arrays
ticket_count = len(data.tickets)
first_ticket = data.tickets[0] if data.tickets else None

# Filter arrays
high_priority = [t for t in data.tickets if t.priority == "high"]
```

### Meta Information
```python
# Access user context
current_user = meta_info.user.first_name
user_department = meta_info.user.department
```

## Common Patterns

### Data Transformation
```python
# Transform user data
user = data.user_info.user
return {
    "display_name": f"{user.name} ({user.department})",
    "contact_info": {
        "email": user.email,
        "manager": user.manager.name
    },
    "permissions": user.permissions
}
```

### Calculations
```python
# Calculate statistics
tickets = data.ticket_data.tickets
total = len(tickets)
open_count = len([t for t in tickets if t.status == "open"])
closed_count = total - open_count

return {
    "total_tickets": total,
    "open_tickets": open_count,
    "closed_tickets": closed_count,
    "completion_rate": (closed_count / total * 100) if total > 0 else 0
}
```

### Conditional Logic
```python
# Business logic
user = data.user_info.user

if user.department == "Engineering":
    approval_required = user.permissions.get("admin", False) == False
elif user.department == "Finance":
    approval_required = True
else:
    approval_required = False

return {
    "approval_required": approval_required,
    "approver": user.manager.email if approval_required else None
}
```

## Best Practices

1. **Always Include Return Statement**: Scripts must return data to be useful
2. **Use Descriptive Variable Names**: Make code readable and maintainable
3. **Handle Edge Cases**: Check for empty arrays, missing data, etc.
4. **Keep Scripts Focused**: Each script should have a single, clear purpose
5. **Comment Complex Logic**: Explain business rules and calculations
6. **Validate Input Data**: Check that required data exists before processing

## Error Handling

Handle potential errors in your scripts:

```python
# Safe data access
user = data.user_info.get("user")
if not user:
    return {"error": "User data not found"}

# Safe array access
tickets = data.tickets or []
first_ticket = tickets[0] if tickets else None

# Safe calculations
total = len(tickets)
rate = (completed / total * 100) if total > 0 else 0
```

## Testing Scripts

Test your scripts with realistic data:

1. **Provide Complete JSON Examples**: Include all fields your script accesses
2. **Test Edge Cases**: Empty arrays, missing fields, null values
3. **Validate Output**: Ensure return data matches expected format
4. **Use Validation Panel**: Check for syntax errors and warnings

Script expressions are powerful tools for implementing custom business logic and data processing in your Moveworks workflows.
            """.strip(),
            category="Expression Types",
            difficulty="Intermediate",
            keywords=["script", "code", "apiton", "python", "logic", "processing"],
            estimated_time="12 minutes",
            related_topics=["Action Expression", "Data Context", "APIthon Syntax"],
            examples=[
                "script:\n  code: |\n    user = data.user_info.user\n    return {\n        \"message\": f\"Hello, {user.name}!\"\n    }\n  output_key: \"greeting\"",
                "script:\n  code: |\n    tickets = data.tickets or []\n    open_count = len([t for t in tickets if t.status == \"open\"])\n    return {\"open_tickets\": open_count}\n  output_key: \"stats\""
            ]
        ))

        # Add topics to section
        self.sections["Expression Types"].topics.extend([
            "Action Expression",
            "Script Expression",
            "Switch Expression",
            "For Expression",
            "Parallel Expression",
            "Return Expression",
            "Raise Expression",
            "Try Catch Expression"
        ])

    def _initialize_enhanced_features_help(self):
        """Initialize help topics for enhanced features."""

        # Enhanced JSON Path Selector
        self.add_topic(HelpTopic(
            title="Enhanced JSON Path Selector",
            content="""
# Enhanced JSON Path Selector - Visual Data Selection Tool

The Enhanced JSON Path Selector is a powerful visual tool that makes it easy to select and map data between workflow steps, especially for beginners working with complex JSON structures.

## Key Features

### 🎯 Visual Data Selection
- **Tree View**: Browse JSON structure in an intuitive tree format
- **Point-and-Click**: Select data paths without typing complex expressions
- **Real-time Preview**: See actual values as you navigate
- **Path Validation**: Automatic checking of data path correctness

### 📋 Array Handling
- **Array Visualization**: Clear display of array contents and structure
- **Index Guidance**: Shows valid index ranges (0 to N-1)
- **Item Preview**: View individual array items and their structure
- **Safe Access**: Warnings for out-of-bounds array access

### 🔄 Data Flow Indicators
- **Visual Flow**: See how data moves from step to step
- **Usage Examples**: Context-aware examples for selected data
- **YAML Integration**: Direct integration with workflow generation
- **Dependency Tracking**: Understand data dependencies between steps

## How to Use

### 1. Access the Selector
1. Click the **JSON Path Selector** tab in the right panel
2. Select a workflow step that has JSON output
3. The selector will display the JSON structure

### 2. Browse JSON Structure
```
📊 Sample JSON Structure:
   ├── user_lookup_result/
   │   ├── user/
   │   │   ├── id: 'emp_12345'
   │   │   ├── name: 'John Doe'
   │   │   ├── email: 'john.doe@company.com'
   │   │   └── manager/
   │   │       ├── id: 'mgr_67890'
   │   │       └── name: 'Jane Smith'
   │   ├── tickets: [3 items] 🎫
   │   │   ├── [0]/ (TKT-001 - Password Reset)
   │   │   ├── [1]/ (TKT-002 - Software Installation)
   │   │   └── [2]/ (TKT-003 - Hardware Request)
   │   └── metadata/
   │       ├── total_tickets: 3
   │       └── last_updated: '2024-01-15T10:30:00Z'
```

### 3. Select Data Paths
- **Click on Fields**: Click any field to select its path
- **Array Elements**: Click on array indices to select specific items
- **Nested Objects**: Navigate through nested structures easily
- **Copy Paths**: Selected paths are automatically copied to clipboard

### 4. Use in Workflow
- **Paste Paths**: Use copied paths in input arguments
- **Validate Paths**: Selector validates paths in real-time
- **See Examples**: Get context-aware usage examples

## Supported Path Patterns

### Basic Field Access
```yaml
# Pattern: data.step_output.field_name
user_name: "data.user_lookup.user.name"
user_email: "data.user_lookup.user.email"
```

### Nested Object Access
```yaml
# Pattern: data.step_output.object.nested_field
manager_name: "data.user_lookup.user.manager.name"
manager_email: "data.user_lookup.user.manager.email"
```

### Array Element Access
```yaml
# Pattern: data.step_output.array[index].field
first_ticket: "data.user_lookup.tickets[0].title"
latest_status: "data.user_lookup.tickets[0].status"
```

### Array Operations
```yaml
# Get array length (use metadata when available)
ticket_count: "data.user_lookup.metadata.total_tickets"

# Access last item (use negative indexing carefully)
last_ticket: "data.user_lookup.tickets[-1].title"
```

## Beginner-Friendly Features

### 1. Clear Visual Indicators
- **📁 Folders**: Represent objects with nested data
- **📋 Arrays**: Show array length and item previews
- **🔢 Numbers**: Indicate numeric values
- **📝 Strings**: Show text content
- **✅ Booleans**: Display true/false values

### 2. Helpful Tooltips
- **Hover Information**: Detailed info about each field
- **Usage Suggestions**: How to use the selected data
- **Type Information**: Data types and expected formats
- **Example Values**: Sample data for context

### 3. Error Prevention
- **Path Validation**: Real-time checking of path correctness
- **Array Bounds**: Warnings for invalid array indices
- **Missing Data**: Alerts for non-existent fields
- **Type Mismatches**: Warnings for incorrect data types

## Advanced Features

### 1. Filtering and Search
- **Filter by Type**: Show only strings, numbers, arrays, etc.
- **Search Fields**: Find specific field names quickly
- **Pattern Matching**: Search for fields matching patterns
- **Bookmark Paths**: Save frequently used paths

### 2. Batch Operations
- **Multi-Select**: Select multiple paths at once
- **Bulk Copy**: Copy multiple paths to clipboard
- **Template Generation**: Generate input argument templates
- **Pattern Recognition**: Suggest common path patterns

### 3. Integration Features
- **Live Updates**: Reflects changes in JSON output
- **Validation Integration**: Works with workflow validation
- **Example Generation**: Creates usage examples automatically
- **Documentation Links**: Links to relevant help topics

## Best Practices

### 1. Start Simple
- Begin with basic field access before trying arrays
- Test paths individually before combining them
- Use the preview feature to verify data

### 2. Handle Arrays Safely
- Always check array length before accessing high indices
- Use index 0 for "first/most recent" items
- Consider using metadata counts instead of array.length

### 3. Validate Continuously
- Use the real-time validation features
- Test with realistic data samples
- Check for edge cases (empty arrays, missing fields)

### 4. Document Your Selections
- Use descriptive names for selected data
- Add comments explaining complex path selections
- Keep a record of important path patterns

## Common Use Cases

### User Information Extraction
```yaml
# Extract user details for personalization
user_name: "data.user_lookup.user.name"
user_email: "data.user_lookup.user.email"
department: "data.user_lookup.user.department"
manager_name: "data.user_lookup.user.manager.name"
```

### Ticket Processing
```yaml
# Process ticket arrays for summaries
latest_ticket: "data.tickets[0].title"
ticket_count: "data.metadata.total_tickets"
first_priority: "data.tickets[0].priority"
assignee_name: "data.tickets[0].assignee.name"
```

### Statistical Analysis
```yaml
# Extract metrics and counts
total_items: "data.results.metadata.total"
success_rate: "data.results.metadata.success_percentage"
error_count: "data.results.metadata.errors"
```

The Enhanced JSON Path Selector makes data selection intuitive and error-free, especially for users new to workflow development.
            """.strip(),
            category="Enhanced Features",
            difficulty="Beginner",
            keywords=["json", "path", "selector", "visual", "data", "mapping", "arrays"],
            estimated_time="10 minutes",
            related_topics=["Data Context", "Variable Mapping", "Array Handling"],
            examples=[
                "data.user_lookup.user.name",
                "data.tickets[0].title",
                "data.user_lookup.user.manager.email"
            ]
        ))

    def _initialize_workflow_management_help(self):
        """Initialize help topics for workflow management."""
        # This will be implemented in the next chunk
        pass

    def _initialize_data_handling_help(self):
        """Initialize help topics for data handling."""
        # This will be implemented in the next chunk
        pass

    def _initialize_dsl_help(self):
        """Initialize comprehensive DSL (Data Mapping Syntax) help topics."""

        # DSL Overview
        self.add_topic(HelpTopic(
            title="DSL Overview",
            content="""
# Moveworks Data Mapping Syntax (DSL) Overview

The Moveworks Data Mapping Syntax (DSL) is a powerful expression language used to reference data, perform transformations, and create dynamic values in your workflows.

## What is DSL?

DSL expressions allow you to:
- **Reference data** from previous steps: `data.user_info.name`
- **Access user context**: `meta_info.user.email`
- **Perform transformations**: `$CONCAT([data.first_name, ' ', data.last_name])`
- **Create conditions**: `data.user.age >= 18`
- **Build dynamic values**: `$IF(data.is_premium, 'Premium User', 'Standard User')`

## Where DSL is Used

DSL expressions are commonly used in:
- **Input Arguments**: Values passed to actions and scripts
- **Switch Conditions**: Logic for conditional branching
- **Output Mappers**: Transforming step outputs
- **For Loop Iterators**: Dynamic iteration over data
- **Return Values**: Dynamic return expressions

## DSL vs. Regular Values

### DSL Expressions (quoted in YAML):
```yaml
input_args:
  user_email: "data.user_info.email"           # DSL - references data
  full_name: "$CONCAT([data.first, data.last])" # DSL - function call
  condition: "data.age >= 18"                   # DSL - comparison
```

### Regular Values (not quoted):
```yaml
input_args:
  timeout: 30                    # Regular number
  enabled: true                  # Regular boolean
  message: "Hello World"         # Regular string
```

## Key DSL Patterns

### 1. Data References
- `data.field_name` - Access step output data
- `data.user_info.name` - Nested field access
- `data.items[0]` - Array element access

### 2. Meta Information
- `meta_info.user.email` - Current user's email
- `meta_info.user.name` - Current user's name
- `meta_info.user.id` - Current user's ID

### 3. DSL Functions
- `$CONCAT([...])` - String concatenation
- `$SPLIT(string, delimiter)` - String splitting
- `$IF(condition, true_val, false_val)` - Conditional logic
- `$TEXT(value)` - Convert to text

### 4. Operators
- `==`, `!=` - Equality comparison
- `>`, `<`, `>=`, `<=` - Numeric comparison
- `&&`, `||` - Logical operators

## Best Practices

1. **Use descriptive data paths**: `data.user_profile.contact_info.email`
2. **Test complex expressions**: Use the DSL Playground for validation
3. **Keep expressions readable**: Break complex logic into multiple steps
4. **Quote all DSL expressions**: Ensure proper YAML formatting
5. **Validate data paths**: Ensure referenced fields exist

## Getting Help

- **DSL Builder**: Use the interactive DSL builder for complex expressions
- **Templates**: Browse common DSL patterns in the template library
- **Validation**: Real-time DSL syntax checking
- **Examples**: Context-aware DSL examples based on your data

Ready to start using DSL? Check out the "Common DSL Patterns" and "DSL Builder" topics!
            """.strip(),
            category="DSL & Data Mapping",
            difficulty="Beginner",
            keywords=["dsl", "data", "mapping", "syntax", "expressions", "moveworks"],
            estimated_time="5 minutes",
            related_topics=["Common DSL Patterns", "DSL Builder", "Data References", "DSL Functions"],
            examples=[
                "data.user_info.email",
                "meta_info.user.name",
                "$CONCAT([data.first_name, ' ', data.last_name])",
                "data.age >= 18"
            ]
        ))

    def _initialize_validation_help(self):
        """Initialize help topics for validation."""
        # This will be implemented in the next chunk
        pass

    def _initialize_templates_help(self):
        """Initialize help topics for templates."""
        # This will be implemented in the next chunk
        pass

    def _initialize_advanced_features_help(self):
        """Initialize help topics for advanced features."""
        # This will be implemented in the next chunk
        pass

    def _initialize_troubleshooting_help(self):
        """Initialize help topics for troubleshooting."""
        # This will be implemented in the next chunk
        pass

    def _initialize_best_practices_help(self):
        """Initialize help topics for best practices."""
        # This will be implemented in the next chunk
        pass

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

    def get_sections(self) -> List[HelpSection]:
        """Get all help sections ordered by priority."""
        return sorted(self.sections.values(), key=lambda s: s.order)

    def get_section_topics(self, section_title: str) -> List[HelpTopic]:
        """Get all topics in a specific section."""
        section = self.sections.get(section_title)
        if not section:
            return []

        return [self.get_topic(topic_title) for topic_title in section.topics
                if self.get_topic(topic_title) is not None]


# Enhanced tooltip content for UI elements
TOOLTIPS = {
    "compound_action_name": "Unique identifier for your entire workflow (required for Moveworks compliance). Use descriptive names like 'user_onboarding_workflow' or 'ticket_escalation_process'. This becomes the top-level 'action_name' field in your YAML.",
    "action_name": "The name of the action to execute (e.g., 'mw.get_user_by_email')",
    "output_key": "Unique identifier for storing this step's output (used in data.output_key references)",
    "description": "Optional human-readable description of what this step does",
    "input_args": "Key-value pairs passed as arguments to the action or script. Use DSL expressions like 'data.field_name' or 'meta_info.user.email' for dynamic values.",
    "input_args_dsl": "Enter a Moveworks DSL expression or data path (e.g., 'data.user_info.email', '$CONCAT([data.first, data.last])', 'meta_info.user.name'). DSL expressions will be automatically quoted in the YAML output.",
    "switch_condition_dsl": "Enter the DSL expression for the switch condition (e.g., 'data.user.status == \"active\"', 'data.age >= 18'). This determines which case will be executed.",
    "output_mapper_dsl": "Enter a DSL expression to transform the output (e.g., 'data.result.value', '$CONCAT([data.prefix, data.value])'). This maps the step output to the desired format.",
    "for_loop_iterator_dsl": "Enter a DSL expression that evaluates to an array for iteration (e.g., 'data.items', 'data.user_list'). Each element will be available as 'data.item' in the loop body.",
    "json_output": "Example JSON that this step will produce when executed",
    "script_code": "APIthon (Python-like) code that processes data and returns a result",
    "parse_json": "Validate and save the JSON output for use in variable mapping",
    "add_action": "Add a new action step that calls a Moveworks action or external API",
    "add_script": "Add a new script step that executes APIthon code",
    "add_builtin": "Add a pre-configured Moveworks built-in action with example output",
    "json_browser": "Browse JSON structure from previous steps to select data paths",
    "yaml_preview": "Live preview of the generated YAML with Moveworks compliance validation",
    "validation_status": "Shows validation results including Moveworks compliance - hover for error details",
    "step_list": "List of workflow steps - click to select and configure",
    "move_up": "Move the selected step up in the execution order",
    "move_down": "Move the selected step down in the execution order",
    "remove_step": "Remove the selected step from the workflow",
    "save_workflow": "Save the current workflow to a JSON file",
    "load_workflow": "Load a workflow from a JSON file",
    "export_yaml": "Export the workflow as Moveworks-compliant YAML with compound action structure",
    "validate": "Run comprehensive validation including Moveworks compliance checks"
}


def get_tooltip(element_id: str) -> str:
    """Get tooltip text for a UI element."""
    return TOOLTIPS.get(element_id, "")


def get_contextual_help(context: str) -> str:
    """Get contextual help based on current application state."""
    help_texts = {
        "empty_workflow": "Start by setting a compound action name, then add your first step using the buttons on the left.",
        "no_step_selected": "Select a step from the list to configure its properties.",
        "action_step_selected": "Configure the action name, output key, and input arguments. Don't forget to provide JSON output!",
        "script_step_selected": "Write your APIthon code and specify the output key. Include a 'return' statement.",
        "validation_errors": "Fix the validation errors shown in red before exporting your workflow.",
        "no_json_output": "Provide JSON output examples to enable variable mapping between steps.",
        "ready_to_export": "Your workflow is valid and ready to export as Moveworks-compliant YAML!",
        "compound_action_name_empty": "Set a compound action name to identify your workflow. Use descriptive names like 'user_lookup_workflow'.",
        "compound_action_name_invalid": "Use valid naming conventions: lowercase letters, underscores, no spaces or special characters.",
        "moveworks_compliance": "Your YAML follows Moveworks compound action requirements with mandatory action_name and steps fields."
    }

    return help_texts.get(context, "")


# Global help system instance
help_system = ComprehensiveHelpSystem()
