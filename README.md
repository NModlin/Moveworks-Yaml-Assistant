# Moveworks YAML Assistant

A comprehensive desktop application for creating and managing Moveworks Compound Action workflows with complete support for all expression types, strict Moveworks compliance, and advanced features.

## 🚀 Overview

The Moveworks YAML Assistant is the definitive solution for building complex Compound Action workflows. It provides complete support for all 8 Moveworks expression types, strict Moveworks compound action compliance, advanced data handling with `meta_info.user` support, intelligent validation with fix suggestions, and a comprehensive template library.

**Key Features:**
- ✅ **Complete Expression Support**: All 8 Moveworks expression types (action, script, switch, for, parallel, return, raise, try_catch)
- ✅ **Strict Moveworks Compliance**: Enforced compound action structure with validation
- ✅ **Perfect YAML Generation**: Compliant output matching official Moveworks specifications
- ✅ **Advanced Data Handling**: Full support for `data.*` and `meta_info.user` references
- ✅ **Interactive Tutorial System**: Step-by-step learning with hands-on practice
- ✅ **Comprehensive Template Library**: Ready-to-use templates for common workflows
- ✅ **Real-time Validation**: Intelligent validation with actionable fix suggestions
- ✅ **JSON Path Selector**: Visual data navigation and selection tool
- ✅ **Enhanced UI/UX**: Modern PySide6 interface with accessibility features

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

## 📦 Quick Installation

### Option 1: Automatic Setup (Recommended)
```bash
# Navigate to project directory
cd moveworks-yaml-assistant

# Automatic setup and launch
python run_app.py --setup-only
```

### Option 2: Manual Installation
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Launch application
python run_app.py gui
```

**System Requirements:**
- Python 3.10+ (required)
- 4GB RAM (8GB recommended)
- 500MB free storage

📖 **[Complete Installation Guide](docs/user/installation.md)**

## 🚀 Quick Start

### Launch the Application
```bash
python run_app.py gui
```

### Create Your First Workflow (3 steps)
1. **Set Compound Action Name**: `user_lookup_workflow`
2. **Add Action Step**:
   - Action Name: `mw.get_user_by_email`
   - Output Key: `user_info`
   - Input Args: `email` → `data.input_email`
3. **Generate YAML**: Click "Generate YAML"

**Result:**
```yaml
action_name: user_lookup_workflow
steps:
- action:
    action_name: mw.get_user_by_email
    output_key: user_info
    input_args:
      email: data.input_email
```

📖 **[Complete Quick Start Guide](docs/user/quick-start.md)**

## 🎓 Learning & Tutorials

### Interactive Tutorial System
Learn through hands-on practice with overlay tutorials:

1. **Access Tutorials**: `Tools` → `📚 Tutorials`
2. **Start with Basics**: `🎯 Interactive Basic Workflow`
3. **Follow Along**: Step-by-step guidance with copy-paste examples
4. **Practice**: Complete all tutorial modules

**Available Tutorials:**
- **Basic Workflow** (12 min): Action steps, JSON handling, script writing
- **Control Flow** (15 min): Switch statements, loops, conditional logic
- **Advanced Features** (20 min): Parallel execution, error handling

📖 **[Complete Tutorial Guide](docs/user/tutorials.md)**

## 🧪 Testing & Validation

### Run Tests
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --ui            # UI tests only
python run_tests.py --demo          # Demo scripts

# Run with coverage
python run_tests.py --coverage --html

# Quick tests (exclude slow tests)
python run_tests.py --quick

# Check test environment
python run_tests.py --check
```

### Test Organization
- **Unit Tests** (`tests/unit/`): Individual component testing
- **Integration Tests** (`tests/integration/`): Component interaction testing
- **UI Tests** (`tests/ui/`): User interface testing
- **Demo Scripts** (`tests/demo/`): Feature demonstrations
- **Validation Tests** (`tests/validation/`): Compliance and validation testing

### Validation Features
- **Real-time Validation**: Immediate feedback as you build
- **Compliance Checking**: Ensures Moveworks specification adherence
- **Auto-fix Suggestions**: Actionable recommendations for issues
- **Error Prevention**: Catches common mistakes before export

## 📁 Project Structure

```
moveworks-yaml-assistant/
├── 🏗️ Core Engine
│   ├── core_structures.py          # Data models for all 8 expression types
│   ├── yaml_generator.py           # Compliant YAML generation
│   ├── validator.py                # Basic validation engine
│   └── enhanced_validator.py       # Advanced validation with suggestions
│
├── 🎯 Advanced Features
│   ├── template_library.py         # Template system with import/export
│   ├── enhanced_json_selector.py   # Visual JSON path selection
│   ├── bender_function_builder.py  # Advanced data processing functions
│   ├── compliance_validator.py     # Moveworks compliance checking
│   └── contextual_examples.py      # Context-aware examples
│
├── 🖥️ User Interface
│   ├── main_gui.py                 # Main PySide6 desktop application
│   ├── main_cli.py                 # Command-line interface
│   ├── run_app.py                  # Application launcher
│   └── error_display.py            # Enhanced error reporting
│
├── 🎓 Tutorial System
│   ├── tutorials/                  # Interactive tutorial framework
│   │   ├── unified_tutorial_system.py
│   │   ├── plugins/                # Tutorial plugins
│   │   └── resources/              # Tutorial assets
│   └── tutorial_data.py            # Tutorial content and data
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── user/                   # User documentation
│   │   └── developer/              # Developer documentation
│   ├── yaml_syntex.md              # Official YAML syntax reference
│   ├── data_bank.md                # Data reference patterns
│   └── ENVIRONMENT_SETUP.md        # Installation and setup guide
│
├── 🧪 Testing
│   ├── tests/
│   │   ├── unit/                   # Unit tests for individual components
│   │   ├── integration/            # Integration tests for component interactions
│   │   ├── ui/                     # User interface and GUI tests
│   │   ├── demo/                   # Demo scripts and examples
│   │   ├── validation/             # Validation and compliance tests
│   │   └── fixtures/               # Test data and fixtures
│   ├── run_tests.py                # Comprehensive test runner
│   └── pytest.ini                 # Test configuration
│
└── 📦 Configuration
    ├── requirements.txt            # Python dependencies
    ├── requirements-dev.txt        # Development dependencies
    └── templates/                  # Workflow templates
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

## 📚 Documentation

### User Documentation
- **[Installation Guide](docs/user/installation.md)** - Complete setup instructions
- **[Quick Start Guide](docs/user/quick-start.md)** - Get up and running in 5 minutes
- **[Expression Types Guide](docs/user/expression-types.md)** - Complete reference for all 8 expression types
- **[Interactive Tutorials](docs/user/tutorials.md)** - Step-by-step learning system
- **[Data Handling Guide](docs/user/data-handling.md)** - Advanced data manipulation techniques
- **[Template Library](docs/user/templates.md)** - Using and creating workflow templates
- **[JSON Path Selector](docs/user/json-path-selector.md)** - Visual data navigation tool
- **[Troubleshooting](docs/user/troubleshooting.md)** - Common issues and solutions

### Developer Documentation
- **[Architecture Overview](docs/developer/architecture.md)** - System design and components
- **[API Reference](docs/developer/api-reference.md)** - Core application APIs
- **[Contributing Guide](docs/developer/contributing.md)** - How to contribute to the project
- **[Plugin Development](docs/developer/creating-plugins.md)** - Extending the system
- **[Testing Guide](docs/developer/testing.md)** - Testing strategies and frameworks

### Reference Documentation
- **[YAML Syntax Reference](yaml_syntex.md)** - Official Moveworks YAML syntax
- **[Data Bank Reference](data_bank.md)** - Available data sources and patterns
- **[Environment Setup](ENVIRONMENT_SETUP.md)** - Detailed installation guide

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer/contributing.md) for details on:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

## 📞 Support

- **Documentation**: Check the comprehensive guides in `/docs/`
- **Issues**: Report bugs and request features via the project repository
- **Discussions**: Join community discussions for questions and ideas

## 🏆 Project Status

- ✅ **Complete Expression Support**: All 8 Moveworks expression types implemented
- ✅ **Strict Compliance**: Full adherence to Moveworks specifications
- ✅ **Production Ready**: Comprehensive testing and validation
- ✅ **User Friendly**: Intuitive interface with guided learning
- ✅ **Well Documented**: Extensive user and developer documentation
- ✅ **Actively Maintained**: Regular updates and improvements

**The Moveworks YAML Assistant is the definitive solution for creating Moveworks-compliant Compound Action workflows!** 🚀
