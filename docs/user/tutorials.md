# Interactive Tutorial System

Learn the Moveworks YAML Assistant through hands-on, interactive tutorials that guide you step-by-step through real workflow creation.

## 🎯 Tutorial Overview

The Interactive Tutorial System provides immersive learning experiences that overlay the actual application interface, allowing you to learn by doing with real examples and immediate feedback.

### Key Features
- **Overlay Interface**: Tutorials appear over the actual application
- **Step-by-Step Guidance**: Clear instructions for each action
- **Copy-Paste Examples**: Ready-to-use code and configuration
- **Real-Time Feedback**: Immediate validation and results
- **Progressive Learning**: Build skills from basic to advanced

## 🚀 Getting Started

### Accessing Tutorials

1. **Launch the Application**: `python run_app.py gui`
2. **Open Tutorial Menu**: `Tools` → `📚 Tutorials`
3. **Select Tutorial**: Choose from available tutorial options
4. **Begin Learning**: Follow the interactive guidance

### Tutorial Interface

**Instruction Panel**:
- **Step Title**: Clear description of current step
- **Description**: Context and explanation
- **Instructions**: Detailed guidance on what to do
- **Copy-Paste Section**: Ready-to-use examples

**Navigation Controls**:
- **Previous**: Review previous steps
- **Next**: Proceed to next step
- **Skip Tutorial**: Exit at any time
- **Progress Bar**: Visual completion indicator

## 📚 Available Tutorials

### 1. Interactive Basic Workflow (12 minutes)
**Perfect for beginners** - Learn fundamental workflow creation

**What You'll Learn**:
- Creating action steps
- Configuring input arguments
- Working with JSON data
- Using the JSON Path Selector
- Writing processing scripts
- Generating YAML output

**Tutorial Flow**:
1. **Introduction** (Steps 1-2): Welcome and first action
2. **Action Configuration** (Steps 3-7): Complete action setup
3. **Data Exploration** (Steps 8-11): JSON handling and path selection
4. **Script Creation** (Steps 12-15): Data processing and completion

**Copy-Paste Examples Provided**:
```
Action Name: mw.get_user_by_email
Output Key: user_info
Input Arguments: email → data.input_email

Sample JSON Data:
{
  "user": {
    "id": "emp_12345",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering"
  }
}

Processing Script:
user_name = data.user_info.user.name
greeting = f"Hello, {user_name}!"
return {"greeting": greeting, "user_name": user_name}
```

### 2. Control Flow Tutorial (15 minutes)
**Intermediate level** - Master conditional logic and loops

**What You'll Learn**:
- Switch expressions for conditional logic
- For loops for iteration
- Nested step configuration
- Complex data flow patterns

**Key Concepts**:
- Condition evaluation
- Case-based routing
- Loop iteration patterns
- Data collection and aggregation

### 3. Advanced Features Tutorial (20 minutes)
**Advanced level** - Parallel execution and error handling

**What You'll Learn**:
- Parallel execution strategies
- Error handling with try_catch
- Performance optimization
- Complex workflow patterns

**Advanced Topics**:
- Concurrent API calls
- Error recovery mechanisms
- Fallback strategies
- Performance best practices

## 🎨 Tutorial Features

### Visual Guidance
- **Overlay System**: Semi-transparent overlay highlights target elements
- **Animated Highlighting**: Pulsing borders draw attention to interactive areas
- **Smart Positioning**: Instruction panels avoid blocking important content
- **Progress Tracking**: Visual indicators show completion status

### Interactive Elements
- **One-Click Copy**: Copy examples to clipboard instantly
- **Real-Time Validation**: See validation results as you work
- **Live YAML Preview**: Watch YAML generation in real-time
- **Contextual Help**: Additional information when needed

### Learning Support
- **Detailed Explanations**: Context for each step and concept
- **Best Practices**: Learn proper techniques and conventions
- **Common Pitfalls**: Avoid typical mistakes and issues
- **Troubleshooting**: Solutions for common problems

## 📋 Tutorial Walkthrough Example

### Basic Workflow Tutorial - Step by Step

**Step 1: Welcome**
- Introduction to interactive learning
- Overview of what you'll build
- Interface orientation

**Step 3: Action Configuration**
```
Copy this Action Name: mw.get_user_by_email
Paste it in the highlighted field
```

**Step 5: Input Arguments**
```
Key: email
Value: data.input_email
Click "Add Argument" to save
```

**Step 7: JSON Data**
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
    }
  }
}
```

**Step 12: Processing Script**
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

## 🎯 Learning Outcomes

### After Basic Tutorial
- ✅ Understand workflow structure
- ✅ Configure action steps confidently
- ✅ Work with JSON data effectively
- ✅ Use JSON Path Selector efficiently
- ✅ Write basic processing scripts
- ✅ Generate valid YAML output

### After Control Flow Tutorial
- ✅ Implement conditional logic
- ✅ Create iterative processes
- ✅ Handle complex data flows
- ✅ Design multi-step workflows

### After Advanced Tutorial
- ✅ Optimize workflow performance
- ✅ Implement error handling
- ✅ Design robust systems
- ✅ Apply best practices

## 💡 Tutorial Tips

### During Tutorials
- **Take Your Time**: Understanding is more important than speed
- **Use Copy-Paste**: Provided examples are tested and ready to use
- **Explore Freely**: Click around and explore when prompted
- **Read Carefully**: Each step includes important context

### After Tutorials
- **Practice Regularly**: Create several workflows to reinforce learning
- **Experiment**: Try different JSON structures and transformations
- **Use Templates**: Browse the Template Library for more examples
- **Build Real Workflows**: Apply skills to actual use cases

## 🔧 Troubleshooting

### Common Issues

**Tutorial Won't Start**:
- Ensure application is fully loaded
- Try refreshing or restarting the application
- Check that no other dialogs are open

**Copy-Paste Not Working**:
- Click the "📋 Copy to Clipboard" button first
- Ensure clipboard permissions are enabled
- Try manual copy-paste if automatic fails

**UI Elements Not Highlighted**:
- Try resizing the application window
- Ensure panels aren't collapsed or hidden
- Restart tutorial if highlighting is missing

**Steps Not Advancing**:
- Complete all instructions before clicking "Next"
- Check for validation errors that need fixing
- Ensure required fields are filled

### Getting Help
- **Built-in Help**: Use `Help` → `Help Topics` for additional guidance
- **Documentation**: Review comprehensive user documentation
- **Examples**: Check Template Library for workflow examples
- **Support**: Contact support with specific issues

## 🚀 Next Steps

After completing tutorials:

1. **Explore Templates**: Browse the Template Library for more complex examples
2. **Create Real Workflows**: Apply your skills to actual business scenarios
3. **Advanced Features**: Learn about [Bender Functions](bender-functions.md)
4. **Share Knowledge**: Export and share your workflow templates
5. **Contribute**: Help improve tutorials with feedback and suggestions

## 📖 Related Documentation

- **[Expression Types Guide](expression-types.md)** - Detailed reference for all expressions
- **[Data Handling](data-handling.md)** - Advanced data manipulation techniques
- **[Template Library](templates.md)** - Complete template documentation
- **[JSON Path Selector](json-path-selector.md)** - Advanced data selection guide

---

*Ready to start learning? Launch the application and go to `Tools` → `📚 Tutorials`*
