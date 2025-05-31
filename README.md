# Enhanced Moveworks YAML Assistant

A comprehensive desktop application for creating and managing Moveworks Compound Action workflows with complete support for all expression types, strict Moveworks compliance, and advanced features.

## 🚀 Overview

The Enhanced Moveworks YAML Assistant is the definitive solution for building complex Compound Action workflows. It provides complete support for all 8 Moveworks expression types, strict Moveworks compound action compliance, advanced data handling with `meta_info.user` support, intelligent validation with fix suggestions, and a comprehensive template library.

**Key Achievements:**
- ✅ **100% Expression Coverage**: All 8 expression types fully implemented
- ✅ **Strict Moveworks Compliance**: Mandatory compound action structure with action_name and steps
- ✅ **Perfect YAML Compliance**: Matches `yaml_syntex.md` format exactly
- ✅ **Enhanced Data Context**: Complete `data.*` and `meta_info.user` support
- ✅ **Comprehensive Templates**: Ready-to-use templates for all expression types
- ✅ **Intelligent Validation**: Actionable fix suggestions for all issues

## ✨ Complete Expression Type Support

### Core Expressions
- **🎯 action** - HTTP requests and native actions with full field support
  - `action_name`, `output_key`, `input_args`, `delay_config`, `progress_updates`
- **📝 script** - APIthon script execution with advanced data processing
  - `code`, `output_key`, `input_args` with proper formatting

### Control Flow Expressions
- **🔀 switch** - Conditional logic with multiple cases and default handling
  - `cases` with conditions, `default` case, nested step execution
- **🔄 for** - Iteration over collections with nested step execution
  - `each`, `index`, `in`, `output_key`, nested steps
- **⚡ parallel** - Concurrent execution (both branches and parallel loops)
  - `branches` mode and `for` loop mode with proper configuration

### Output & Error Handling
- **📤 return** - Structured data output with advanced mapping
  - `output_mapper` with complex data transformations
- **⚠️ raise** - Error handling and workflow termination
  - `message`, `output_key` for error information
- **🛡️ try_catch** - Robust error recovery with status code handling
  - `try` steps, `catch` blocks, `on_status_code` targeting

## 🔧 Advanced Features

### Strict Moveworks Compound Action Compliance
- **Mandatory Structure**: All YAML follows required compound action format
- **Action Name Field**: Top-level `action_name` field for workflow identification
- **Steps Array**: All workflow steps wrapped in mandatory `steps` array
- **Data Type Enforcement**: Automatic validation of field types (dict, int, string)
- **Real-time Validation**: Immediate feedback on Moveworks compliance

### Perfect YAML Generation
- **Compliance**: 100% compliant with `yaml_syntex.md` format and Moveworks requirements
- **Compound Action Structure**: Mandatory top-level action_name and steps fields
- **Proper Structure**: Correct field ordering, indentation, and nesting
- **Complex Support**: Full support for nested steps in control flow expressions
- **Type Safety**: Automatic data type enforcement for all fields

### Enhanced Data Context
- **Complete Data References**: Full support for all `data.*` patterns
- **Meta Info Support**: Access to `meta_info.user` attributes
  - `first_name`, `last_name`, `email_addr`, `department`, `role`, `record_id`
- **Nested JSON Paths**: Navigate complex data structures with validation
- **Path Enumeration**: Real-time discovery of available data paths

### Comprehensive Template Library
- **8 Expression Templates**: Ready-to-use templates for all expression types
- **Real-world Examples**: Based on actual `yaml_syntex.md` examples
- **Organized Categories**: User Management, IT Service Management, Control Flow, Error Handling
- **Import/Export**: Share and reuse templates across teams

### Enhanced Validation System
- **Intelligent Validation**: Validates all expression types and their requirements
- **Fix Suggestions**: Actionable suggestions for common issues
- **Quick Fixes**: Automated fixes for simple problems
- **Comprehensive Checks**: Validates data references, syntax, and best practices

### Interactive Tutorial System
- **Step-by-Step Guidance**: Tutorials for all expression types
- **Interactive Learning**: Hands-on tutorials with real examples
- **Progressive Difficulty**: From basic actions to complex control flow
- **Contextual Help**: Context-aware assistance throughout the application

## 📦 Installation

1. **Install Python 3.10+**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Quick Start

Use the startup script for easy launching:
```bash
# Launch the enhanced desktop GUI (default)
python run_app.py

# Or explicitly specify GUI
python run_app.py gui

# Launch CLI interface
python run_app.py cli

# Run comprehensive tests
python run_app.py test

# Run enhanced features tests
python test_enhanced_features.py

# Run comprehensive demo
python demo_comprehensive_features.py

# Show help
python run_app.py help
```

### Enhanced Desktop GUI Application

Run the main GUI application with all enhanced features:
```bash
python main_gui.py
```

**New Features Available:**
- 🏷️ Compound action name input for Moveworks compliance
- 🎯 All 8 expression types in the step creation menu
- 📚 Template browser with comprehensive templates
- 🔍 Enhanced JSON path selector with meta_info support
- ✅ Intelligent validation with Moveworks compliance checks
- 📖 Interactive tutorials including compound action guidance

### Testing & Demonstration

**Comprehensive Testing:**
```bash
# Test all enhanced features
python test_enhanced_features.py

# Run comprehensive demo
python demo_comprehensive_features.py

# Test core functionality
python test_core.py
```

**Legacy Testing:**
```bash
# Phase-specific tests
python test_phase3.py  # Control flow
python test_phase4.py  # Error handling
python test_phase5.py  # Advanced validation
```

## 📁 Enhanced Application Structure

```
enhanced_moveworks_yaml_assistant/
├── 🏗️ Core Engine
│   ├── core_structures.py          # Enhanced data models (all 8 expression types)
│   ├── yaml_generator.py           # Compliant YAML generation
│   └── validator.py               # Basic validation engine
│
├── 🎯 Enhanced Features
│   ├── enhanced_validator.py       # Intelligent validation with fix suggestions
│   ├── template_library.py         # Comprehensive template system
│   ├── tutorial_system.py          # Interactive tutorials
│   ├── enhanced_json_selector.py   # Advanced JSON path selection
│   └── contextual_examples.py      # Context-aware examples
│
├── 🖥️ User Interface
│   ├── main_gui.py                 # Enhanced PySide6 desktop application
│   ├── main_cli.py                 # Command-line interface
│   └── run_app.py                  # Enhanced startup script
│
├── 🧪 Testing & Demo
│   ├── test_enhanced_features.py   # Comprehensive test suite
│   ├── demo_comprehensive_features.py # Feature demonstration
│   ├── test_core.py                # Core functionality tests
│   ├── test_phase3.py              # Control flow tests
│   ├── test_phase4.py              # Error handling tests
│   └── test_phase5.py              # Advanced validation tests
│
├── 📚 Documentation
│   ├── yaml_syntex.md              # YAML syntax reference
│   ├── data_bank.md                # Data reference patterns
│   ├── ENHANCED_IMPLEMENTATION_SUMMARY.md # Implementation summary
│   ├── Project_Plan.md             # Original implementation plan
│   └── README.md                   # This enhanced documentation
│
└── 📦 Configuration
    ├── requirements.txt            # Python dependencies
    └── .gitignore                 # Git ignore patterns
```

## 🔧 Enhanced Key Components

### Core Data Structures (Enhanced)
- **All Expression Types**: Complete support for action, script, switch, for, parallel, return, raise, try_catch
- **Enhanced DataContext**: Support for `data.*` and `meta_info.user` references
- **Complex Nesting**: Full support for nested steps in control flow expressions
- **Validation Integration**: Built-in validation hooks for all expression types

### Enhanced GUI Components
- **Expression Type Selector**: Support for all 8 expression types
- **Template Browser**: Browse and apply comprehensive templates
- **Enhanced JSON Selector**: Visual selection with meta_info support
- **Intelligent Validation Panel**: Real-time validation with fix suggestions
- **Tutorial System**: Interactive step-by-step guidance
- **Contextual Examples**: Context-aware example suggestions

### Enhanced Data Flow
1. **Expression Selection**: Choose from all 8 expression types
2. **Template Application**: Apply ready-to-use templates
3. **Enhanced Configuration**: Configure complex expressions with nested steps
4. **Data Context Management**: Access both data.* and meta_info.user references
5. **Intelligent Validation**: Real-time validation with actionable fix suggestions
6. **Perfect YAML Generation**: Compliant output matching yaml_syntex.md format

## 🎯 Enhanced Workflow Creation Process

### 1. Compound Action Naming
- **Set Action Name**: Enter a descriptive name for your compound action (e.g., "user_onboarding_workflow")
- **Moveworks Compliance**: Name becomes the top-level `action_name` field in YAML
- **Naming Conventions**: Use lowercase letters, underscores, no spaces or special characters
- **Real-time Preview**: YAML updates automatically as you type

### 2. Expression Type Selection
- Choose from all 8 expression types: action, script, switch, for, parallel, return, raise, try_catch
- Use templates for quick start with pre-configured examples
- Access interactive tutorials for step-by-step guidance

### 3. Enhanced Configuration
- **Action Steps**: Configure with delay_config and progress_updates
- **Script Steps**: Write APIthon code with input_args support
- **Control Flow**: Configure complex nested steps (switch cases, for loops, parallel branches)
- **Error Handling**: Set up try_catch blocks with specific error code handling

### 3. Advanced Data Mapping
- **Data References**: Use visual JSON browser for `data.*` paths
- **Meta Info Access**: Select from `meta_info.user` attributes (first_name, email_addr, etc.)
- **Nested Paths**: Navigate complex JSON structures with validation
- **Real-time Validation**: Immediate feedback on data reference validity

### 4. Intelligent Validation & Export
- **Comprehensive Validation**: Check all expression types and requirements
- **Fix Suggestions**: Get actionable suggestions for common issues
- **Quick Fixes**: Apply automated fixes for simple problems
- **Perfect YAML**: Export compliant YAML matching yaml_syntex.md format

## 📋 Example Workflows

### Simple Action Workflow (Moveworks Compliant)
```yaml
action_name: fetch_user_details_workflow
steps:
- action:
    action_name: fetch_user_details
    output_key: user_details
    input_args:
      user_id: data.user_id
    delay_config:
      delay_seconds: 10
    progress_updates:
      on_pending: "Fetching user details, please wait..."
      on_complete: "User details fetched successfully."
```

### Complex Control Flow Workflow (Moveworks Compliant)
```yaml
action_name: user_access_management_workflow
steps:
- action:
    action_name: mw.get_user_by_email
    output_key: user_info
    input_args:
      email: meta_info.user.email_addr

- switch:
    cases:
    - condition: data.user_info.user.access_level == 'admin'
      steps:
      - action:
          action_name: send_admin_welcome
          output_key: admin_welcome_notification
          input_args:
            user_id: data.user_info.user.id
            message: "Welcome, Admin! You have full access."
    default:
      steps:
      - action:
          action_name: send_generic_welcome
          output_key: generic_welcome
          input_args:
            message: "Welcome to the system!"
```

## 🏆 Implementation Status

- ✅ **Enhanced Core Engine**: All 8 expression types with perfect YAML compliance
- ✅ **Strict Moveworks Compliance**: Mandatory compound action structure with action_name and steps
- ✅ **Advanced Data Context**: Complete data.* and meta_info.user support
- ✅ **Comprehensive Templates**: Templates for all expression types
- ✅ **Intelligent Validation**: Fix suggestions, automated corrections, and compliance checks
- ✅ **Interactive Tutorials**: Step-by-step guidance including compound action naming
- ✅ **Enhanced UI/UX**: Professional desktop application with Moveworks compliance features

## 🎓 Enhanced Learning & Support

### Interactive Tutorial System
- **Progressive Learning**: Tutorials for basic to advanced expression types
- **Hands-on Practice**: Interactive tutorials with real examples
- **Step-by-Step Guidance**: Detailed instructions for each expression type
- **Contextual Help**: Context-aware assistance throughout the application

### Comprehensive Template Library
- **Expression Coverage**: Templates for all 8 expression types
- **Real-world Examples**: Based on actual yaml_syntex.md examples
- **Organized Categories**: User Management, IT Service Management, Control Flow, Error Handling
- **Import/Export**: Share templates across teams and projects

### Enhanced Validation & Support
- **Intelligent Validation**: Validates all expression types and requirements
- **Actionable Fix Suggestions**: Specific suggestions for common issues
- **Quick Fix Automation**: Automated corrections for simple problems
- **Comprehensive Error Reporting**: Detailed validation results with severity indicators

## 🏗️ Architecture & Design

### Enhanced Architecture
This implementation extends the original **PySide6 Desktop Application** architecture with:

- **Complete Expression Support**: All 8 Moveworks expression types
- **Enhanced Data Context**: Support for both data.* and meta_info.user references
- **Intelligent Validation**: Advanced validation with fix suggestions
- **Template System**: Comprehensive template library with import/export
- **Tutorial Integration**: Interactive learning system

### Key Design Principles
- **YAML Compliance**: Perfect compliance with yaml_syntex.md format
- **User Experience**: Intuitive interface for complex workflow creation
- **Extensibility**: Modular design for easy feature additions
- **Reliability**: Comprehensive testing and validation
- **Performance**: Efficient handling of complex workflows

### Technology Stack
- **Core**: Python 3.10+ with enhanced data structures
- **UI Framework**: PySide6 with custom enhanced components
- **YAML Processing**: Custom generator with format compliance
- **Validation**: Multi-layer validation with intelligent suggestions
- **Templates**: JSON-based template system with metadata

## 🎉 Success Metrics

- ✅ **100% Expression Coverage**: All 8 expression types fully implemented
- ✅ **Strict Moveworks Compliance**: Mandatory compound action structure enforced
- ✅ **Perfect YAML Compliance**: Matches yaml_syntex.md format exactly with compound action requirements
- ✅ **Enhanced Data Support**: Complete data.* and meta_info.user support
- ✅ **Comprehensive Testing**: All features tested and validated including compliance checks
- ✅ **User Experience**: Intuitive interface with Moveworks compliance guidance
- ✅ **Documentation**: Complete documentation with compound action examples

**The Enhanced Moveworks YAML Assistant is now the definitive solution for creating Moveworks-compliant Compound Action workflows!** 🚀
