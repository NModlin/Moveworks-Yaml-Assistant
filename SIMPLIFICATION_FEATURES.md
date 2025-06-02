# Moveworks YAML Assistant - Simplification Features

This document describes the new simplification features implemented to make the Moveworks YAML Assistant more accessible to beginners while preserving all advanced functionality.

## 🎯 Overview

The simplification project introduces several new components designed to reduce the learning curve for new users:

1. **Expression Factory System** - Simplified creation of workflow expressions
2. **Enhanced Template System** - More accessible template-based workflow creation
3. **Workflow Creation Wizard** - Step-by-step guided workflow creation
4. **Simplified Data Path Selector** - Intuitive data path selection interface
5. **Streamlined Three-Panel Interface** - Reorganized layout for better usability

## 🏗️ New Components

### 1. Expression Factory (`expression_factory.py`)

The `ExpressionFactory` class provides simple methods to create workflow expressions with sensible defaults:

```python
from expression_factory import ExpressionFactory, CommonPatterns

# Create an action step
action = ExpressionFactory.create_action(
    action_name="mw.get_user_by_email",
    output_key="user_info",
    input_args={"email": "data.user_email"}
)

# Create a script step
script = ExpressionFactory.create_script(
    code="return {'processed': True}",
    output_key="processing_result"
)

# Use common patterns
user_lookup_steps = CommonPatterns.user_lookup_pattern()
```

**Features:**
- Factory methods for all 8 expression types
- Sensible defaults to reduce configuration overhead
- Common workflow patterns for typical use cases
- Full compatibility with existing core structures

### 2. Simplified Template System (`template_library.py`)

Enhanced the existing template system with beginner-friendly templates:

```python
from template_library import SimplifiedTemplateSystem

template_system = SimplifiedTemplateSystem()

# Get template categories
categories = template_system.get_template_categories()
# Returns: ["User Management", "Communication", "Approvals", ...]

# Get templates by category
user_templates = template_system.get_templates_by_category("User Management")

# Get specific template
template = template_system.get_template_by_key("user_lookup")
```

**New Templates Added:**
- **Simple User Lookup** - Basic user lookup with validation
- **Quick Action** - Single action workflow template
- **Basic Script** - Simple APIthon script template
- **Approval Workflow** - Basic approval request workflow
- **Data Transformation** - Data processing template

### 3. Workflow Creation Wizard (`workflow_wizard.py`)

A step-by-step wizard that guides users through workflow creation:

```python
from workflow_wizard import WorkflowWizard

wizard = WorkflowWizard(parent_window)
wizard.workflow_created.connect(handle_new_workflow)
wizard.exec()
```

**Wizard Pages:**
1. **Introduction** - Welcome and overview
2. **Workflow Type** - Template selection or custom workflow
3. **Basic Information** - Action name and description
4. **Input Variables** - Define workflow inputs
5. **Steps Configuration** - Configure workflow steps
6. **Summary** - Review and create

**Features:**
- Template-based quick start options
- Progressive disclosure of complexity
- Validation at each step
- Integration with ExpressionFactory for step creation

### 4. Simplified Data Path Selector (`simplified_data_path_selector.py`)

An intuitive interface for selecting data paths:

```python
from simplified_data_path_selector import SimplifiedDataPathSelector

selector = SimplifiedDataPathSelector(workflow)
selector.path_selected.connect(handle_path_selection)
```

**Features:**
- **Common Data Sources** - Buttons for typical data sources
  - Input Variables (`data.*`)
  - Current User (`meta_info.user.*`)
  - Previous Steps (`data.step_output.*`)
  - Custom Path (manual entry)
- **Recent Paths** - Quick access to recently used paths
- **Quick Reference** - Common pattern examples
- **Dialog-based Selection** - Specialized dialogs for each data source type

### 5. Enhanced Main Interface

The main GUI has been updated with simplification features:

**New Menu Items:**
- **File → 🧙 New Workflow Wizard...** (`Ctrl+Shift+N`) - Launch the workflow wizard
- Enhanced template library access

**New UI Components:**
- **📋 Apply Template** button in the left panel for quick template access
- **🎯 Data Helper** tab in the right panel with the simplified data path selector
- Improved visual hierarchy and button organization

## 🎨 Design Principles

### Progressive Disclosure
- Advanced features are available but not overwhelming for beginners
- Templates provide quick starts for common use cases
- Wizard guides users through complex workflows step-by-step

### Sensible Defaults
- ExpressionFactory provides reasonable default values
- Templates include working examples with realistic data
- Wizard pre-populates fields where possible

### Visual Feedback
- Clear visual distinction between different types of components
- Color-coded buttons for different step types
- Status indicators and validation feedback

### Contextual Help
- Tooltips explain the purpose of each component
- Quick reference guides for common patterns
- Examples integrated into the interface

## 🔧 Integration with Existing Features

All new components are designed to work seamlessly with existing functionality:

- **Backward Compatibility** - All existing workflows continue to work
- **Validation Integration** - New components use existing validation systems
- **Template System** - Enhanced existing template library
- **YAML Generation** - Works with existing YAML generation engine
- **Compliance** - Maintains strict Moveworks compliance

## 📚 Usage Examples

### Creating a Simple User Lookup Workflow

1. **Using the Wizard:**
   - File → New Workflow Wizard
   - Select "User Lookup" template
   - Follow guided steps

2. **Using Templates:**
   - Click "📋 Apply Template" button
   - Select "Simple User Lookup"
   - Customize as needed

3. **Using Expression Factory:**
   ```python
   steps = CommonPatterns.user_lookup_pattern()
   workflow = Workflow(steps=steps)
   ```

### Selecting Data Paths

1. **Using Data Helper:**
   - Go to "🎯 Data Helper" tab
   - Click "📧 Input Variables" for workflow inputs
   - Click "👤 Current User" for user information
   - Click "📋 Previous Steps" for step outputs

2. **Recent Paths:**
   - Previously used paths appear in the recent list
   - Double-click to select and copy to clipboard

## 🧪 Testing

Run the test suite to verify all components work correctly:

```bash
python test_simplification.py
```

The test suite covers:
- ExpressionFactory functionality
- SimplifiedTemplateSystem operations
- Basic component instantiation
- YAML generation with new components

## 🚀 Future Enhancements

Potential areas for further simplification:

1. **Smart Suggestions** - AI-powered workflow suggestions based on user input
2. **Visual Workflow Builder** - Drag-and-drop workflow construction
3. **Interactive Tutorials** - Built-in guided tutorials for common scenarios
4. **Template Marketplace** - Community-contributed templates
5. **Workflow Analytics** - Usage patterns and optimization suggestions

## 📖 Documentation Updates

The following documentation has been updated to reflect the new features:

- **User Guide** - Added sections on wizard and templates
- **Developer Guide** - ExpressionFactory and component APIs
- **Tutorial Content** - Updated with simplified approaches
- **README** - Overview of new features

## 🎉 Success Metrics

The simplification features are considered successful if:

1. **Usability** - New users can create basic workflows within 5 minutes
2. **Adoption** - Template and wizard usage increases over time
3. **Support** - Reduction in basic functionality support questions
4. **Retention** - Users continue to use the application after initial success

## 🤝 Contributing

When adding new simplification features:

1. Follow the progressive disclosure principle
2. Provide sensible defaults
3. Include comprehensive examples
4. Maintain backward compatibility
5. Add appropriate tests
6. Update documentation

The goal is to make the Moveworks YAML Assistant accessible to everyone while preserving the power and flexibility that advanced users need.
