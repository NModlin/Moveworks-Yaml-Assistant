# Enhanced Moveworks YAML Assistant - Quick Reference

## 🚀 Getting Started
```bash
# Launch the enhanced application
python main_gui.py

# Run comprehensive tests
python test_enhanced_features.py

# See all features in action
python demo_comprehensive_features.py
```

## 🎯 All 8 Expression Types

### 1. Action - HTTP Requests & Native Actions
```yaml
action:
  action_name: "mw.get_user_by_email"
  output_key: "user_info"
  input_args:
    email: "data.user_email"
  delay_config:
    seconds: "10"
  progress_updates:
    on_pending: "Fetching user..."
    on_complete: "User found!"
```

### 2. Script - APIthon Code Execution
```yaml
script:
  output_key: "processed_data"
  input_args:
    user: "data.user_info"
  code: |
    result = {
        "greeting": f"Hello, {user.name}!",
        "id": user.id
    }
    return result
```

### 3. Switch - Conditional Logic
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

### 4. For - Collection Iteration
```yaml
for:
  each: "user"
  index: "user_index"
  in: "data.users"
  output_key: "processed_users"
  steps:
  - action:
      action_name: "process_user"
      output_key: "user_result"
      input_args:
        user_data: "user"
```

### 5. Parallel - Concurrent Execution
**Branches Mode:**
```yaml
parallel:
  branches:
  - name: "logging"
    steps:
    - action:
        action_name: "log_event"
        output_key: "log_result"
  - name: "notification"
    steps:
    - action:
        action_name: "send_email"
        output_key: "email_result"
```

**Parallel For Mode:**
```yaml
parallel:
  for:
    each: "item"
    in: "data.items"
    output_key: "parallel_results"
    steps:
    - action:
        action_name: "process_parallel"
        output_key: "item_result"
```

### 6. Return - Structured Output
```yaml
return:
  output_mapper:
    MAP():
      converter:
        id: "item.id"
        name: "item.name.$TITLECASE()"
      items: "data.processed_items"
```

### 7. Raise - Error Handling
```yaml
raise:
  output_key: "error_info"
  message: "Processing failed - please try again"
```

### 8. Try-Catch - Error Recovery
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
        action_name: "handle_error"
        output_key: "error_handled"
```

## 📊 Data References

### Data Paths
- `data.input_variable` - Input variables
- `data.step_output` - Previous step outputs
- `data.step_output.nested.field` - Nested data

### Meta Info (NEW!)
- `meta_info.user.first_name` - User's first name
- `meta_info.user.last_name` - User's last name
- `meta_info.user.email_addr` - User's email
- `meta_info.user.department` - User's department
- `meta_info.user.role` - User's role
- `meta_info.user.record_id` - User's record ID

## 🎓 Enhanced Features

### Template Library
- **Browse**: File → Template Library
- **8 Templates**: All expression types covered
- **Categories**: User Management, IT Service, Control Flow, Error Handling
- **Apply**: One-click workflow creation

### Interactive Tutorials
- **Access**: Tools → Interactive Tutorials
- **Progressive**: Basic to advanced
- **Hands-on**: Real examples and practice
- **Contextual**: Help based on current task

### Enhanced Validation
- **Run**: F5 or Tools → Validate
- **Fix Suggestions**: Actionable advice for issues
- **Quick Fixes**: Automated corrections
- **Severity Levels**: Error, Warning, Info

### JSON Path Selector
- **Visual**: Tree view of JSON structures
- **Meta Info**: Access user context data
- **Real-time**: Validation of data paths
- **Copy**: Click to copy paths

## ⌨️ Keyboard Shortcuts
- **F1**: Help system
- **F5**: Validate workflow
- **Ctrl+N**: New workflow
- **Ctrl+O**: Open workflow
- **Ctrl+S**: Save workflow
- **Ctrl+E**: Export YAML
- **Ctrl+T**: Template browser

## 🔧 Best Practices

### Expression Selection
- **action**: External APIs, Moveworks actions
- **script**: Data processing, calculations
- **switch**: Multiple conditions
- **for**: Process collections
- **parallel**: Independent operations
- **return**: Structured output
- **raise**: Error conditions
- **try_catch**: Error recovery

### Data Flow
1. Plan your data flow first
2. Use descriptive output_key names
3. Validate all data references
4. Include error handling
5. Test thoroughly

### YAML Format
- **Single expression**: No 'steps' wrapper
- **Multiple expressions**: 'steps' wrapper
- **Perfect compliance**: Matches yaml_syntex.md

## 🎉 Quick Start Workflow

1. **Launch**: `python main_gui.py`
2. **Template**: Browse template library
3. **Tutorial**: Try interactive tutorials
4. **Build**: Add expressions and configure
5. **Validate**: F5 to check for issues
6. **Export**: Generate compliant YAML

## 📁 File Structure
```
enhanced_moveworks_yaml_assistant/
├── 🏗️ Core Engine
│   ├── core_structures.py      # All expression types
│   ├── yaml_generator.py       # Perfect YAML compliance
│   └── validator.py           # Basic validation
├── 🎯 Enhanced Features
│   ├── enhanced_validator.py   # Smart validation
│   ├── template_library.py     # Template system
│   ├── tutorial_system.py      # Interactive tutorials
│   └── enhanced_json_selector.py # JSON path selection
├── 🖥️ Interface
│   ├── main_gui.py            # Enhanced desktop app
│   └── run_app.py             # Startup script
└── 🧪 Testing
    ├── test_enhanced_features.py # Comprehensive tests
    └── demo_comprehensive_features.py # Feature demo
```

## 🆘 Need Help?
- **F1**: Built-in help system
- **Tutorials**: Interactive step-by-step guidance
- **Templates**: Ready-to-use examples
- **Validation**: Actionable fix suggestions
- **Examples**: Context-aware code samples

**The Enhanced Moveworks YAML Assistant makes complex workflow creation simple!** 🚀
