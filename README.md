# Moveworks YAML Assistant

A desktop application for creating and managing Moveworks Compound Action workflows using **Option A: PySide6 Desktop Application**.

## Overview

This application implements the plan outlined in `Project_Plan.md` using a Python-centric desktop solution with PySide6. It provides a user-friendly interface for:

- Creating action and script steps
- Defining JSON outputs for each step
- Mapping variables between steps using a visual JSON browser
- Real-time YAML preview and validation
- Saving/loading workflows

## Features

### Phase 1: Core Engine ✅
- **Core Data Structures**: ActionStep, ScriptStep, Workflow, DataContext classes
- **YAML Generation**: Convert workflows to valid Moveworks YAML format
- **Data Context Management**: Track input variables and step outputs
- **Validation Engine**: Comprehensive workflow validation
- **CLI Interface**: Command-line testing interface

### Phase 2: PySide6 Desktop UI ✅
- **Main Window**: Professional desktop application layout
- **Step List Management**: Add, remove, reorder workflow steps
- **Step Configuration Panel**: Dynamic forms for editing step properties
- **JSON Variable Selection**: Tree view for browsing and selecting JSON paths
- **Real-time YAML Preview**: Live updates with validation status
- **Save/Load Functionality**: Workflow persistence in JSON format

### Phase 3: Control Flow ✅
- **Switch Statements**: Conditional branching with multiple cases
- **For Loops**: Iteration over arrays with nested step execution
- **Parallel Execution**: Concurrent branch execution
- **Return Statements**: Early workflow termination with output mapping

### Phase 4: Error Handling & Built-in Actions ✅
- **Try/Catch Blocks**: Robust error handling with catch block execution
- **Raise Statements**: Custom error throwing and workflow termination
- **Built-in Actions Catalog**: Pre-configured Moveworks actions with typical JSON outputs
- **Error Data Mapping**: Access to error_data structure in catch blocks

## Installation

1. **Install Python 3.10+**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Use the startup script for easy launching:
```bash
# Launch the desktop GUI (default)
python run_app.py

# Or explicitly specify GUI
python run_app.py gui

# Launch CLI interface
python run_app.py cli

# Run tests
python run_app.py test

# Show help
python run_app.py help
```

### Desktop GUI Application

Run the main GUI application directly:
```bash
python main_gui.py
```

### Command Line Interface (for testing)

Test the core functionality:
```bash
python main_cli.py --help
```

Example CLI usage:
```bash
# Add an action step
python main_cli.py add_action

# Add a script step
python main_cli.py add_script

# Show current workflow steps
python main_cli.py show_steps

# Generate and display YAML
python main_cli.py show_yaml

# Validate workflow
python main_cli.py validate

# Save workflow
python main_cli.py save

# Load workflow
python main_cli.py load
```

### Core Functionality Testing

Run the test suite:
```bash
python test_core.py
```

## Application Structure

```
moveworks_yaml_assistant/
├── core_structures.py      # Data models (ActionStep, ScriptStep, Workflow, DataContext)
├── yaml_generator.py       # YAML generation logic
├── validator.py           # Workflow validation
├── main_gui.py            # PySide6 desktop application
├── main_cli.py            # Command-line interface
├── test_core.py           # Core functionality tests
├── run_app.py             # Startup script with dependency checking
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore patterns
├── Project_Plan.md        # Detailed implementation plan
└── README.md             # This file
```

## Key Components

### Core Data Structures
- **ActionStep**: Represents Moveworks actions with input/output mapping
- **ScriptStep**: Represents APIthon scripts with code and data handling
- **Workflow**: Container for sequences of steps
- **DataContext**: Manages data flow between steps

### GUI Components
- **WorkflowListWidget**: Step list with add/remove/reorder functionality
- **StepConfigurationPanel**: Dynamic forms for step editing
- **JsonVariableSelectionPanel**: Tree view for JSON path selection
- **YamlPreviewPanel**: Real-time YAML generation and validation

### Data Flow
1. User creates action/script steps
2. User provides JSON output examples for each step
3. JSON is parsed and made available for variable selection
4. User maps variables from previous steps to current step inputs
5. Real-time YAML generation shows the final workflow
6. Validation ensures correctness before export

## Workflow Creation Process

1. **Add Steps**: Use "Add Action Step" or "Add Script Step" buttons
2. **Configure Step**: Fill in action name, description, output key
3. **Define JSON Output**: Paste expected JSON output and parse it
4. **Map Input Variables**: Use the JSON browser to select paths from previous steps
5. **Validate**: Check for errors using F5 or the Edit menu
6. **Export**: Save workflow or export YAML

## Example Workflow

```yaml
steps:
- action_name: mw.get_user_by_email
  output_key: user_info
  description: Get user information by email
  input_args:
    email: data.input_email

- code: |
    user_name = data.user_info.user.name
    processed_result = {
        "greeting": f"Hello, {user_name}!",
        "user_id": data.user_info.user.id
    }
    return processed_result
  output_key: processed_data
  description: Process user information
```

## Implementation Status

- ✅ **Phase 1**: Core Engine & Basic YAML Generation
- ✅ **Phase 2**: PySide6 Desktop UI & Enhanced Data Mapping
- ✅ **Phase 3**: Control Flow & Advanced Data Transformation
- ✅ **Phase 4**: Built-in Actions & Error Handling
- 🔄 **Phase 5**: Advanced Validation & Polish (Future)

## Next Steps

The current implementation covers Phases 1-4 of the project plan. Phase 5 will add:

- Enhanced validation with data path verification
- UI/UX polish and improvements
- In-app help and documentation
- Advanced testing and quality assurance

## Architecture Decision

This implementation uses **Option A: PySide6 Desktop Application** as specified, providing:

- Native desktop performance
- Rich UI components for complex data editing
- No web server dependencies
- Offline functionality
- Professional desktop application experience

The choice aligns with the project's preference for Python-centric solutions and provides excellent support for the data-intensive workflow creation process.
