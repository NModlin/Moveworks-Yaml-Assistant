# Quick Start Guide

Get up and running with the Moveworks YAML Assistant in 5 minutes.

## 🚀 Launch the Application

```bash
# Navigate to your project directory
cd moveworks-yaml-assistant

# Activate virtual environment (if not already active)
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Launch the GUI application
python run_app.py gui
```

## 🎯 Your First Workflow

Let's create a simple user lookup workflow in 3 steps:

### Step 1: Set Compound Action Name
1. In the **Compound Action Name** field at the top, enter:
   ```
   user_lookup_workflow
   ```
2. Notice the YAML preview updates automatically

### Step 2: Add an Action Step
1. Click **"Add Step"** → **"Action"**
2. Fill in the action configuration:
   - **Action Name**: `mw.get_user_by_email`
   - **Output Key**: `user_info`
   - **Input Arguments**: 
     - Key: `email`
     - Value: `data.input_email`

### Step 3: Generate YAML
1. Click **"Generate YAML"** in the bottom panel
2. Your workflow YAML is ready!

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

## 🎓 Learn with Interactive Tutorials

The fastest way to master the application:

1. **Access Tutorials**: `Tools` → `📚 Tutorials`
2. **Start with Basics**: Click `🎯 Interactive Basic Workflow`
3. **Follow Along**: The tutorial overlays the actual interface
4. **Copy Examples**: Use provided copy-paste examples
5. **Practice**: Complete all 15 interactive steps

**Tutorial Topics:**
- ✅ Basic workflow creation
- ✅ JSON data handling
- ✅ Data path selection
- ✅ Script writing
- ✅ YAML generation

## 🛠️ Essential Features Overview

### Expression Types
The application supports all 8 Moveworks expression types:

| Type | Purpose | Example Use Case |
|------|---------|------------------|
| **action** | HTTP requests, API calls | Fetch user data |
| **script** | Data processing | Transform JSON data |
| **switch** | Conditional logic | Route based on user role |
| **for** | Iteration | Process multiple users |
| **parallel** | Concurrent execution | Parallel API calls |
| **return** | Output data | Return processed results |
| **raise** | Error handling | Throw custom errors |
| **try_catch** | Error recovery | Handle API failures |

### Key Interface Areas

**Left Panel - Workflow Steps:**
- Add, edit, and reorder workflow steps
- Visual step indicators and validation status

**Center Panel - Step Configuration:**
- Configure selected step properties
- Real-time validation feedback
- Context-sensitive help

**Right Panel - Tools:**
- YAML preview and generation
- JSON Path Selector
- Template library
- Validation results

## 📚 Template Library

Speed up development with ready-made templates:

1. **Access Templates**: Click `📚 Templates` in the right panel
2. **Browse Categories**: 
   - User Management
   - IT Service Management
   - Control Flow
   - Error Handling
3. **Apply Template**: Click any template to apply it
4. **Customize**: Modify the template for your needs

**Popular Templates:**
- User Onboarding Workflow
- Ticket Creation and Assignment
- Multi-step Approval Process
- Error Handling with Fallbacks

## 🔍 JSON Path Selector

Work with complex JSON data easily:

1. **Add JSON Data**: In any step, paste sample JSON output
2. **Parse JSON**: Click "Parse & Save JSON Output"
3. **Open Selector**: Click `🔍 JSON Path Selector`
4. **Navigate Data**: Use the tree view to explore structure
5. **Select Paths**: Click any path to copy it
6. **Use in Steps**: Paste paths in data reference fields

**Example JSON Paths:**
- `data.user_info.user.name` - User's name
- `data.user_info.user.email` - User's email
- `meta_info.user.department` - Current user's department

## ✅ Validation System

The application provides real-time validation:

**Validation Indicators:**
- 🟢 **Green**: Valid and compliant
- 🟡 **Yellow**: Warning or suggestion
- 🔴 **Red**: Error that must be fixed

**Common Validations:**
- Field naming (must use lowercase_snake_case)
- Required fields (action_name, output_key, etc.)
- Data reference syntax
- YAML structure compliance

**Auto-Fix Suggestions:**
- Click validation messages for fix suggestions
- Many issues can be auto-corrected
- Detailed explanations for complex issues

## 🎨 Customization Options

### UI Preferences
- **Font Size**: Adjust for readability
- **Panel Layout**: Resize panels to your preference
- **Theme**: Light theme optimized for clarity

### Workflow Preferences
- **Default Values**: Set common default values
- **Validation Level**: Adjust validation strictness
- **Auto-Save**: Enable automatic saving

## 📋 Common Workflows

### Simple API Call
```yaml
action_name: simple_api_call
steps:
- action:
    action_name: your_api_action
    output_key: api_result
    input_args:
      param1: data.input_value
```

### Data Processing
```yaml
action_name: data_processing
steps:
- action:
    action_name: fetch_data
    output_key: raw_data
- script:
    code: "processed = [item['name'] for item in raw_data]; processed"
    output_key: processed_data
```

### Conditional Logic
```yaml
action_name: conditional_workflow
steps:
- switch:
    cases:
    - condition: data.user_role == 'admin'
      steps:
      - action:
          action_name: admin_action
          output_key: admin_result
    default:
      steps:
      - action:
          action_name: user_action
          output_key: user_result
```

## 🚀 Next Steps

Now that you're familiar with the basics:

1. **Complete Tutorials**: Finish all interactive tutorials
2. **Explore Templates**: Try different template categories
3. **Build Real Workflows**: Create workflows for your use cases
4. **Advanced Features**: Learn about [Bender Functions](bender-functions.md)
5. **Share Knowledge**: Export and share your templates

## 📖 Additional Resources

- **[Expression Types Guide](expression-types.md)** - Detailed reference for all expression types
- **[Data Handling](data-handling.md)** - Advanced data manipulation techniques
- **[Template Library](templates.md)** - Complete template documentation
- **[Troubleshooting](troubleshooting.md)** - Solutions to common issues

## 💡 Pro Tips

1. **Use Templates**: Start with templates and customize them
2. **Test with Real Data**: Use actual JSON responses in development
3. **Validate Early**: Check validation status frequently
4. **Save Often**: Export your workflows regularly
5. **Learn Incrementally**: Master one expression type at a time

---

*Ready for more? Continue with [Expression Types Guide](expression-types.md)*
