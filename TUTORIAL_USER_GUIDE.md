# Interactive Tutorial User Guide

## 🎯 Welcome to Interactive Learning!

The Moveworks YAML Assistant now includes a comprehensive **Interactive Tutorial System** that teaches you workflow creation through hands-on experience. Unlike traditional tutorials, this system overlays the actual application and guides you through creating real workflows with copy-paste examples and immediate feedback.

## 🚀 Getting Started

### Step 1: Launch the Application
```bash
python run_app.py
```

### Step 2: Access the Interactive Tutorial
1. **Open the Tutorial Menu**: Go to `Tools → 📚 Tutorials`
2. **Select Interactive Tutorial**: Click `🎯 Interactive Basic Workflow`
3. **Begin Learning**: The tutorial overlay will appear with step-by-step guidance

## 📚 What You'll Learn (12 minutes)

### 🎓 Core Skills
- **Action Step Creation**: Configure API calls with proper parameters
- **JSON Data Handling**: Parse and work with realistic API response data
- **JSON Path Selection**: Navigate complex data structures effectively
- **Script Writing**: Create data processing scripts with proper syntax
- **YAML Generation**: Produce valid, production-ready workflow code

### 🛠️ Practical Experience
- **Real UI Interaction**: Work with actual application components
- **Copy-Paste Examples**: Ready-to-use code and configuration
- **Immediate Feedback**: See results instantly as you work
- **Progressive Learning**: Build from simple to sophisticated concepts

## 🎨 Tutorial Features

### Visual Guidance
- **Overlay System**: Semi-transparent overlay highlights target UI elements
- **Animated Highlighting**: Pulsing green borders draw attention to interactive elements
- **Smart Positioning**: Instruction panels automatically position to avoid blocking content
- **Progress Tracking**: Visual progress bar and step indicators

### Interactive Elements
- **Copy-Paste Examples**: One-click copying of realistic data examples
- **Step Navigation**: Previous/Next buttons with skip options
- **Real-Time Validation**: Immediate feedback on your actions
- **Visual Feedback**: Confirmation of completed actions

## 📋 Copy-Paste Examples You'll Use

### Action Configuration
```
Action Name: mw.get_user_by_email
Output Key: user_info
Input Argument Key: email
Input Argument Value: data.input_email
```

### Sample JSON Data
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

### Processing Script
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

## 🎯 Step-by-Step Tutorial Flow

### Phase 1: Introduction (Steps 1-2)
- **Welcome**: Introduction to interactive workflow creation
- **First Action**: Adding your first action step to the workflow

### Phase 2: Action Configuration (Steps 3-7)
- **Action Name**: Configure with `mw.get_user_by_email`
- **Output Key**: Set to `user_info` for data referencing
- **Input Arguments**: Add email parameter configuration
- **JSON Data**: Provide realistic sample API response
- **Parse JSON**: Make data available for selection

### Phase 3: Data Exploration (Steps 8-11)
- **YAML Preview**: View real-time YAML generation
- **Script Step**: Add data processing step
- **JSON Explorer**: Open the JSON Path Selector
- **Data Structure**: Explore available data paths

### Phase 4: Script Creation (Steps 12-15)
- **Processing Script**: Write script using selected data paths
- **Output Key**: Configure script output for data flow
- **Complete Workflow**: View final YAML output
- **Congratulations**: Summary of skills learned

## 🎨 Using the Tutorial Interface

### Instruction Panel
- **Step Title**: Clear description of current step
- **Description**: Context and explanation
- **Instructions**: Detailed guidance on what to do
- **Copy-Paste Section**: Ready-to-use examples (when applicable)

### Navigation Controls
- **Previous**: Go back to review previous steps
- **Next**: Proceed to the next step
- **Skip Tutorial**: Exit tutorial at any time
- **Progress Bar**: Visual indication of completion

### Copy-Paste Functionality
1. **See the Example**: Copy-paste sections appear when relevant
2. **Click Copy**: Use "📋 Copy to Clipboard" button
3. **Paste in Field**: Paste into the highlighted UI field
4. **See Results**: Watch immediate YAML generation

## 🛠️ JSON Path Selection Learning

### Basic Paths You'll Master
- `data.user_info.user.name` - Access user's name
- `data.user_info.user.email` - Access user's email
- `data.user_info.user.department` - Access user's department
- `data.user_info.user.manager.name` - Access nested manager information

### Understanding Data Flow
```
Step 1 (Action) → data.user_info
Step 2 (Script) → data.greeting_result
```

### JSON Path Selector Features
- **Auto-Population**: Automatically loads data when steps are selected
- **Tree Visualization**: Hierarchical view of JSON structure
- **Path Preview**: See exact path syntax before selection
- **One-Click Copy**: Copy paths to clipboard instantly

## 📄 YAML Output You'll Generate

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

## 💡 Tips for Success

### During the Tutorial
- **Take Your Time**: Don't rush - understanding is more important than speed
- **Use Copy-Paste**: The provided examples are tested and ready to use
- **Explore the UI**: Click around and explore when prompted
- **Read Instructions**: Each step includes important context and explanations

### After the Tutorial
- **Practice**: Create several workflows to reinforce your learning
- **Experiment**: Try different JSON structures and data transformations
- **Explore Templates**: Browse the Template Library for more complex examples
- **Create Your Own**: Start building workflows for your specific use cases

## 🚀 Next Steps

After completing the interactive tutorial:

1. **Explore Advanced Features**: Learn about switch statements, loops, and error handling
2. **Browse Templates**: Check out the Template Library for more complex examples
3. **Create Production Workflows**: Apply your skills to real-world scenarios
4. **Share Knowledge**: Help others learn by sharing your workflow examples

## 🔧 Troubleshooting

### Common Issues
- **Tutorial Won't Start**: Ensure the application is fully loaded before accessing tutorials
- **Copy-Paste Not Working**: Make sure to click the "📋 Copy to Clipboard" button first
- **UI Elements Not Highlighted**: Try resizing the window if panels are cut off
- **Steps Not Advancing**: Follow instructions completely before clicking "Next"

### Getting Help
- **Built-in Help**: Use `Help → Help Topics` for additional guidance
- **Documentation**: Review the comprehensive user documentation
- **Examples**: Check the Template Library for workflow examples

## 🎉 Ready to Learn!

The Interactive Tutorial System provides the fastest, most effective way to learn the Moveworks YAML Assistant. With hands-on guidance, copy-paste examples, and real-time feedback, you'll be creating sophisticated workflows in just 12 minutes!

**Start your learning journey now:**
`Tools → 📚 Tutorials → 🎯 Interactive Basic Workflow`

Happy learning! 🚀
