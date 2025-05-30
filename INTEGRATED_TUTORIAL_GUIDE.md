# Integrated Tutorial System Guide

## 🎯 Overview

The Moveworks YAML Assistant now includes an **Interactive Tutorial System** that provides hands-on, step-by-step guidance directly within the actual application. Unlike traditional tutorials, this system overlays the real UI and guides you through creating actual workflows with copy-paste examples and real-time feedback.

## 🚀 Getting Started

### Starting the Interactive Tutorial

1. **Open the Application**: Launch the Moveworks YAML Assistant
2. **Access Tutorials**: Go to `Tools → 📚 Tutorials → 🎯 Interactive Basic Workflow`
3. **Begin Learning**: The tutorial overlay will appear with step-by-step guidance

### Tutorial Interface

The interactive tutorial features:
- **Visual Overlay**: Semi-transparent overlay that highlights target UI elements
- **Instruction Panel**: Detailed step-by-step instructions with copy-paste examples
- **Progress Tracking**: Visual progress bar showing your advancement
- **Navigation Controls**: Previous/Next buttons with skip options

## 📚 Available Tutorial

### Interactive Basic Workflow (12 minutes)
**Perfect for beginners learning workflow creation**

**What You'll Learn:**
- Adding and configuring action steps
- Working with JSON data and parsing
- Using the JSON Path Selector effectively
- Creating data processing scripts
- Generating complete YAML workflows

**What You'll Build:**
A complete user lookup workflow that:
1. Fetches user data via API call
2. Processes the data with a script
3. Generates production-ready YAML

## 🎓 Step-by-Step Tutorial Walkthrough

### Phase 1: Introduction and Setup
**Steps 1-2: Welcome and First Action**
- Introduction to workflow concepts
- Adding your first action step
- Understanding the UI layout

### Phase 2: Action Configuration
**Steps 3-7: Configure the Action Step**
- **Step 3**: Set action name to `mw.get_user_by_email`
- **Step 4**: Set output key to `user_info`
- **Step 5**: Add input arguments (email parameter)
- **Step 6**: Provide sample JSON output
- **Step 7**: Parse JSON data for later use

**Copy-Paste Example for Step 6:**
```json
{
  "user": {
    "id": "emp_12345",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "manager": {
      "name": "Jane Smith",
      "email": "jane.smith@company.com"
    },
    "permissions": ["read", "write", "admin"]
  }
}
```

### Phase 3: Data Exploration
**Steps 8-11: Understanding Data Flow**
- **Step 8**: View generated YAML in real-time
- **Step 9**: Add a script step for data processing
- **Step 10**: Open JSON Path Selector
- **Step 11**: Explore available data structure

### Phase 4: Script Creation
**Steps 12-14: Create Processing Script**
- **Step 12**: Write script using selected data paths
- **Step 13**: Set script output key
- **Step 14**: View complete workflow YAML

**Copy-Paste Example for Step 12:**
```python
# Extract user information
user_name = data.user_info.user.name
user_email = data.user_info.user.email
user_dept = data.user_info.user.department

# Create a greeting message
greeting = f"Hello, {user_name}!"
summary = f"User {user_name} from {user_dept} department"

# Return processed data
return {
    "greeting": greeting,
    "user_name": user_name,
    "user_email": user_email,
    "summary": summary
}
```

## 🎨 Interactive Features

### Visual Guidance
- **Target Highlighting**: Pulsing green borders around UI elements you need to interact with
- **Smart Positioning**: Instruction panels automatically position to avoid blocking content
- **Progress Indicators**: Visual progress bar and step counters

### Copy-Paste Examples
- **One-Click Copying**: Click "📋 Copy to Clipboard" to copy example text
- **Real Data**: All examples use realistic, production-like data
- **Immediate Feedback**: See results instantly as you paste and configure

### Navigation Controls
- **Previous/Next**: Move between tutorial steps at your own pace
- **Skip Tutorial**: Exit at any time if you want to explore on your own
- **Progress Tracking**: Always know where you are in the tutorial

## 🛠️ JSON Path Selection Learning

The tutorial provides comprehensive training on JSON path selection:

### Basic Paths You'll Learn
- `data.user_info.user.name` - Access user's name
- `data.user_info.user.email` - Access user's email
- `data.user_info.user.department` - Access user's department
- `data.user_info.user.manager.name` - Access nested manager information

### Advanced Concepts
- Understanding data flow between workflow steps
- How output keys create data references
- Using the JSON Path Selector effectively
- Exploring complex nested data structures

## 📄 YAML Generation

Throughout the tutorial, you'll see real-time YAML generation:

### Action Step YAML
```yaml
action:
  action_name: mw.get_user_by_email
  output_key: user_info
  input_args:
    email: data.input_email
```

### Complete Workflow YAML
```yaml
steps:
  - action:
      action_name: mw.get_user_by_email
      output_key: user_info
      input_args:
        email: data.input_email
        
  - script:
      code: |
        user_name = data.user_info.user.name
        greeting = f"Hello, {user_name}!"
        return {"greeting": greeting, "user_name": user_name}
      output_key: greeting_result
```

## 🎯 Learning Outcomes

After completing the interactive tutorial, you will:

### ✅ Core Skills
- **Create Action Steps**: Configure API calls with proper parameters
- **Handle JSON Data**: Parse and work with API response data
- **Use JSON Path Selector**: Navigate and select data from complex structures
- **Write Processing Scripts**: Create scripts that transform and process data
- **Generate YAML**: Produce valid, production-ready workflow YAML

### ✅ Advanced Understanding
- **Data Flow**: Understand how data moves between workflow steps
- **Reference Patterns**: Use `data.output_key.path` syntax correctly
- **Best Practices**: Follow Moveworks workflow conventions
- **Real-World Application**: Apply skills to actual workflow creation

## 🚀 Next Steps

After completing the interactive tutorial:

1. **Explore Templates**: Browse the Template Library for more complex examples
2. **Create Your Own**: Start building workflows for your specific use cases
3. **Advanced Features**: Learn about switch statements, loops, and error handling
4. **Production Deployment**: Use your generated YAML in actual Moveworks workflows

## 💡 Tips for Success

### During the Tutorial
- **Take Your Time**: Don't rush through steps - understanding is more important than speed
- **Use Copy-Paste**: The provided examples are tested and ready to use
- **Explore**: Click around and explore the UI when prompted
- **Ask Questions**: Use the help system if you need clarification

### After the Tutorial
- **Practice**: Create several workflows to reinforce your learning
- **Experiment**: Try different JSON structures and data transformations
- **Share**: Help others learn by sharing your workflow examples
- **Feedback**: Provide feedback to improve the tutorial experience

## 🔧 Technical Integration

The interactive tutorial system:
- **Uses Real Components**: Works with actual application UI elements
- **Provides Real Data**: All examples use realistic JSON structures
- **Generates Real YAML**: Output is production-ready workflow code
- **Integrates Seamlessly**: No separate tutorial environment needed

This ensures that skills learned in the tutorial transfer directly to real workflow creation, making you productive immediately after completion.

## 🎉 Ready to Learn!

The Interactive Tutorial System provides the fastest, most effective way to learn the Moveworks YAML Assistant. With hands-on guidance, copy-paste examples, and real-time feedback, you'll be creating sophisticated workflows in just 12 minutes!

Start your learning journey: `Tools → 📚 Tutorials → 🎯 Interactive Basic Workflow`
