# Enhanced Moveworks YAML Assistant - Complete User Guide

This comprehensive guide covers all enhanced features and capabilities of the Enhanced Moveworks YAML Assistant, including complete support for all 8 expression types and advanced workflow creation tools.

## 🎯 Complete Expression Type Support

The Enhanced Moveworks YAML Assistant now supports all 8 Moveworks expression types with perfect YAML compliance.

### 1. Action Expression
**Purpose**: Execute HTTP requests and native Moveworks actions

**YAML Structure**:
```yaml
action:
  action_name: "mw.action_name"
  output_key: "step_output"
  input_args:
    parameter: "data.input_value"
  delay_config:
    seconds: "10"
  progress_updates:
    on_pending: "Processing..."
    on_complete: "Complete!"
```

### 2. Script Expression
**Purpose**: Execute APIthon scripts for data processing

**YAML Structure**:
```yaml
script:
  output_key: "script_result"
  input_args:
    variable: "data.input_data"
  code: |
    # Your APIthon code here
    result = process_data(variable)
    return result
```

### 3. Switch Expression
**Purpose**: Conditional logic with multiple branches

**YAML Structure**:
```yaml
switch:
  cases:
  - condition: "data.user.role == 'admin'"
    steps:
    - action:
        action_name: "admin_action"
        output_key: "admin_result"
  default:
    steps:
    - action:
        action_name: "default_action"
        output_key: "default_result"
```

### 4. For Expression
**Purpose**: Iterate over collections with step execution

**YAML Structure**:
```yaml
for:
  each: "item"
  index: "item_index"
  in: "data.items_array"
  output_key: "loop_results"
  steps:
  - action:
      action_name: "process_item"
      output_key: "item_result"
```

### 5. Parallel Expression
**Purpose**: Execute steps concurrently for performance

**Branches Mode**:
```yaml
parallel:
  branches:
  - name: "logging_branch"
    steps:
    - action:
        action_name: "log_event"
        output_key: "log_result"
```

**Parallel For Mode**:
```yaml
parallel:
  for:
    each: "item"
    in: "data.items"
    output_key: "parallel_results"
    steps:
    - action:
        action_name: "process_item_parallel"
        output_key: "item_result"
```

### 6. Return Expression
**Purpose**: Return structured data with transformations

**YAML Structure**:
```yaml
return:
  output_mapper:
    MAP():
      converter:
        id: "item.id"
        name: "item.name.$TITLECASE()"
      items: "data.processed_items"
```

### 7. Raise Expression
**Purpose**: Throw errors and terminate workflow

**YAML Structure**:
```yaml
raise:
  output_key: "error_info"
  message: "An error occurred during processing"
```

### 8. Try-Catch Expression
**Purpose**: Handle errors with recovery logic

**YAML Structure**:
```yaml
try_catch:
  try:
    steps:
    - action:
        action_name: "risky_action"
        output_key: "action_result"
  catch:
    on_status_code: ["E400", "E500"]
    steps:
    - action:
        action_name: "error_handler"
        output_key: "error_handled"
```

## 📊 Enhanced Data Context Support

### Data References
- `data.input_variable_name` - Access input variables
- `data.step_output_key` - Access previous step outputs
- `data.step_output.nested.path` - Access nested data

### Meta Info References (NEW!)
- `meta_info.user.first_name` - User's first name
- `meta_info.user.last_name` - User's last name
- `meta_info.user.email_addr` - User's email address
- `meta_info.user.department` - User's department
- `meta_info.user.role` - User's role
- `meta_info.user.record_id` - User's record ID

## 🎓 Enhanced Tutorial System

The Interactive Tutorial System provides step-by-step guided tutorials to help users learn the application.

### Features
- **Guided Overlays**: Visual overlays that highlight specific UI elements
- **Step-by-Step Instructions**: Clear instructions for each tutorial step
- **Multiple Tutorials**: Different tutorials for various skill levels
- **Auto-Advance Options**: Some steps can automatically advance after completion

### Available Tutorials
1. **Basic Workflow Creation** (Beginner, 5 minutes)
   - Learn to create your first workflow
   - Add action and script steps
   - Configure step properties
   - Provide JSON output examples

2. **Control Flow and Conditions** (Intermediate, 8 minutes)
   - Use switch statements for conditional logic
   - Create loops for iterating over data
   - Add nested steps within control structures

### How to Use
1. Go to **Tools → Interactive Tutorials...**
2. Select a tutorial from the list
3. Click **Start Tutorial**
4. Follow the on-screen instructions
5. Use **Next**, **Skip**, or **Cancel Tutorial** buttons as needed

### Tutorial Components
- **TutorialManager**: Manages tutorial execution and state
- **TutorialDialog**: Dialog for selecting tutorials
- **TutorialOverlay**: Visual overlay with instructions and highlighting
- **TutorialStep**: Individual tutorial step with title, description, and actions

## 📚 2. Template Library

The Template Library provides pre-built workflow templates to help users get started quickly with common patterns.

### Features
- **Pre-built Templates**: Ready-to-use workflows for common scenarios
- **Template Browser**: Easy browsing with search and filtering
- **Import/Export**: Share templates between users
- **Template Preview**: See workflow structure before using
- **Categorization**: Templates organized by category and difficulty

### Built-in Templates

#### User Management
- **User Lookup** (Beginner)
  - Look up and process user information by email
  - Demonstrates basic action and script steps

#### IT Service Management
- **Ticket Creation** (Intermediate)
  - Create ServiceNow incident tickets
  - Shows user lookup, ticket creation, and response formatting

#### Best Practices
- **Error Handling Pattern** (Advanced)
  - Demonstrates proper error handling and validation
  - Shows conditional logic and safe data access

### How to Use
1. Go to **File → Template Library...**
2. Browse templates by category or search
3. Select a template to see details and preview
4. Click **Use Template** to load it into your workflow
5. Use **Export...** to save templates to files
6. Use **Import...** to load templates from files

### Template Structure
- **WorkflowTemplate**: Contains metadata and workflow
- **TemplateLibrary**: Manages template storage and retrieval
- **TemplateBrowserDialog**: UI for browsing and selecting templates

## 🔍 3. Visual JSON Path Selector

The Enhanced JSON Path Selector provides an improved way to navigate and select JSON data paths with tree visualization and search capabilities.

### Features
- **Tree Visualization**: Hierarchical view of JSON structure
- **Search Functionality**: Find paths, keys, or values quickly
- **Path Preview**: See the actual value at a selected path
- **Automatic Path Construction**: Builds correct data.* paths
- **Type Indicators**: Visual indicators for different data types

### How to Use
1. Select a step in your workflow
2. Go to the **Enhanced JSON Path Selector** panel (right side)
3. Choose a step from the dropdown to see its JSON structure
4. Browse the tree or use the search box
5. Click on any item to select its path
6. The path is automatically copied to clipboard
7. Use the preview panel to see the actual value

### Data Type Indicators
- **Blue**: Objects (dictionaries)
- **Dark Green**: Arrays (lists)
- **Dark Red**: Strings
- **Dark Magenta**: Numbers
- **Dark Cyan**: Booleans

### Search Tips
- Search for key names: "email", "user", "id"
- Search for values: "john.doe", "active", "true"
- Search for paths: "user.email", "data.result"

## 💡 4. Contextual Examples Panel

The Contextual Examples Panel provides relevant code examples and patterns based on your current context in the application.

### Features
- **Context-Aware**: Shows examples relevant to your current step type
- **Categorized Examples**: Organized by category and difficulty
- **Search and Filter**: Find specific examples quickly
- **Apply Examples**: One-click application of example code
- **Best Practices**: Learn recommended patterns and practices

### Example Categories

#### Action Steps
- Basic action step configuration
- Actions with multiple arguments
- Built-in Moveworks actions

#### Script Steps
- Basic data processing scripts
- Conditional logic and error handling
- Data validation patterns

#### Data Mapping
- Simple data reference patterns
- Complex nested object navigation
- Array element access

#### JSON Outputs
- User lookup response examples
- Ticket creation response examples
- API response structures

#### Best Practices
- Error handling patterns
- Data validation techniques
- Safe data access methods

### How to Use
1. Select a step in your workflow
2. Go to the **Examples** tab in the center panel
3. Browse context-relevant examples
4. Use search or category filter to find specific examples
5. Click on an example to see details and explanation
6. Click **Apply Example** to use the code in your current step

### Context Switching
The examples panel automatically updates based on:
- **Action Step Selected**: Shows action-related examples
- **Script Step Selected**: Shows script and data processing examples
- **No Selection**: Shows general examples and best practices

## 🔧 5. Enhanced Error Messages with Fix Suggestions

The Enhanced Validator provides detailed error messages with actionable fix suggestions and quick fixes for common issues.

### Features
- **Detailed Error Messages**: Clear descriptions of what's wrong
- **Fix Suggestions**: Step-by-step guidance on how to fix issues
- **Quick Fixes**: Automated fixes for common problems
- **Severity Levels**: Error, warning, and info classifications
- **Best Practice Checks**: Suggestions for improving workflow quality

### Error Types and Fixes

#### Missing Required Fields
- **Error**: "ActionStep missing required 'action_name'"
- **Suggestions**:
  - Add an action name (e.g., 'mw.get_user_by_email')
  - Use the built-in actions catalog
  - Check Moveworks documentation
- **Quick Fix**: Sets a default action name

#### Invalid Data References
- **Error**: "References unavailable data path 'data.unknown_step'"
- **Suggestions**:
  - Check that referenced step exists
  - Verify JSON structure of referenced step
  - Use JSON path selector for valid references

#### Script Syntax Errors
- **Error**: "Script syntax error - invalid syntax"
- **Suggestions**:
  - Fix Python syntax errors
  - Check indentation and colons
  - Test script logic before adding

#### Missing Return Statements
- **Error**: "Script should contain a 'return' statement"
- **Suggestions**:
  - Add return statement to output results
  - Return dictionary with processed data
- **Quick Fix**: Appends a basic return statement

### Best Practice Warnings

#### Missing Descriptions
- **Warning**: "Consider adding a description for better documentation"
- **Suggestions**: Add clear, concise descriptions

#### Missing JSON Output
- **Warning**: "Missing JSON output example - limits data mapping"
- **Suggestions**: Provide realistic example JSON output
- **Quick Fix**: Adds a basic JSON output template

#### Generic Output Keys
- **Info**: "Output key 'result' is generic - consider more descriptive name"
- **Suggestions**: Use descriptive names like 'user_info', 'ticket_details'

### How to Use
1. Go to **Tools → Validate Workflow** (F5)
2. Review the enhanced error messages
3. Read the fix suggestions for each error
4. Apply quick fixes where available
5. Use the suggestions to manually fix other issues
6. Re-validate to confirm fixes

### Validation Summary
The enhanced validator provides a summary showing:
- Total number of issues
- Count by severity (errors, warnings, info)
- Number of issues with quick fixes available
- Whether the workflow is ready for export

## 🚀 Getting Started with Enhanced Features

### For New Users
1. Start with **Interactive Tutorials** to learn the basics
2. Use **Template Library** to begin with proven patterns
3. Leverage **Contextual Examples** when configuring steps
4. Use **Enhanced JSON Path Selector** for data mapping
5. Run **Enhanced Validation** to catch and fix issues

### For Experienced Users
- Use templates as starting points for complex workflows
- Browse examples for advanced patterns and best practices
- Use enhanced validation to ensure workflow quality
- Share templates with team members

### Integration Tips
- All features work together seamlessly
- Examples panel updates based on current step selection
- JSON path selector shows data from previous steps
- Validation provides context-aware suggestions
- Templates include realistic JSON output examples

## 📁 File Structure

The enhanced features are implemented in these new files:
- `tutorial_system.py` - Interactive tutorial components
- `template_library.py` - Template management and browser
- `enhanced_json_selector.py` - Visual JSON path selection
- `contextual_examples.py` - Context-aware examples system
- `enhanced_validator.py` - Validator with fix suggestions

## 🧪 Testing

Run the test suite to verify all features work correctly:
```bash
python test_enhanced_features.py
```

This tests all components and their integration without requiring a GUI environment.

## 🎯 Next Steps

These enhanced features make the Moveworks YAML Assistant much more accessible to new users while providing powerful tools for experienced users. The combination of tutorials, templates, examples, and enhanced validation creates a comprehensive learning and development environment for Moveworks Compound Actions.
