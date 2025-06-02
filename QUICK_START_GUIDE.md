# 🚀 Quick Start Guide - Moveworks YAML Assistant

Welcome to the Moveworks YAML Assistant! This guide will help you create your first workflow in just a few minutes.

## 🎯 Three Ways to Get Started

### 1. 🧙 Workflow Wizard (Recommended for Beginners)

The easiest way to create your first workflow:

1. **Launch the Wizard**
   - Open the application
   - Go to **File → 🧙 New Workflow Wizard...** (or press `Ctrl+Shift+N`)

2. **Choose Your Workflow Type**
   - Select from pre-built templates like:
     - **User Lookup** - Get user information by email
     - **Send Notification** - Send messages to users
     - **Approval Request** - Request manager approval
     - **Create Ticket** - Create support tickets
   - Or choose "Custom Workflow" to start from scratch

3. **Fill in Basic Information**
   - **Action Name**: Give your workflow a unique name (e.g., `user_onboarding_workflow`)
   - **Description**: Describe what your workflow does

4. **Define Input Variables**
   - Add variables your workflow needs (e.g., `user_email`, `message`)
   - Specify data types (string, number, boolean, etc.)
   - Mark required vs. optional variables

5. **Configure Steps**
   - The wizard will guide you through setting up workflow steps
   - Based on your template choice, some steps may be pre-configured

6. **Review and Create**
   - Review your workflow configuration
   - Click "Finish" to create your workflow

### 2. 📋 Templates (Quick Start)

Use pre-built templates for common scenarios:

1. **Access Templates**
   - Click the **📋 Apply Template** button in the left panel
   - Or go to **Tools → Template Library**

2. **Browse Templates**
   - Templates are organized by category:
     - **Getting Started** - Simple workflows for beginners
     - **User Management** - User lookup and management
     - **Communication** - Notifications and messaging
     - **Approvals** - Approval workflows
     - **IT Service Management** - Ticket creation and management

3. **Apply a Template**
   - Select a template that matches your needs
   - Click "Apply" to load it into the editor
   - Customize the template as needed

### 3. 🔧 Manual Creation (Advanced Users)

Build workflows from scratch using the full editor:

1. **Create New Workflow**
   - Go to **File → New Workflow** (or press `Ctrl+N`)

2. **Add Steps**
   - Click **➕ Add Step** in the left panel
   - Choose from 8 expression types:
     - **Action** - Call Moveworks functions
     - **Script** - Run custom APIthon code
     - **Switch** - Conditional logic
     - **For Loop** - Process lists of items
     - **Parallel** - Run steps simultaneously
     - **Return** - Return workflow results
     - **Raise** - Handle errors
     - **Try-Catch** - Error handling

3. **Configure Each Step**
   - Fill in required fields for each step
   - Use the **🎯 Data Helper** tab for selecting data paths

## 🎯 Using the Data Helper

The Data Helper makes it easy to reference data in your workflows:

### Common Data Sources

1. **📧 Input Variables** (`data.*`)
   - Variables passed to your workflow
   - Example: `data.user_email`, `data.message`

2. **👤 Current User** (`meta_info.user.*`)
   - Information about the user running the workflow
   - Example: `meta_info.user.email`, `meta_info.user.name`

3. **📋 Previous Steps** (`data.step_output.*`)
   - Output from previous workflow steps
   - Example: `data.user_info.user.id`, `data.email_result.status`

4. **✏️ Custom Path**
   - Enter any custom data path manually

### How to Use

1. Go to the **🎯 Data Helper** tab in the right panel
2. Click the appropriate data source button
3. Select from available options in the dialog
4. The path is automatically copied to your clipboard
5. Paste it into any input field that needs data

## 📝 Example: Creating a User Lookup Workflow

Let's create a simple workflow that looks up a user by email:

### Using the Wizard

1. **Start the Wizard**
   - File → 🧙 New Workflow Wizard...

2. **Select Template**
   - Choose "User Lookup - Get user details by email"

3. **Basic Information**
   - Action Name: `user_lookup_workflow`
   - Description: `Look up user information by email address`

4. **Input Variables**
   - Add variable: `user_email` (type: string, required: true)

5. **Review and Create**
   - The wizard creates a workflow with user lookup and validation steps

### Using Templates

1. **Apply Template**
   - Click **📋 Apply Template**
   - Select "Simple User Lookup" from Getting Started category

2. **Customize**
   - The template includes:
     - Action step to call `mw.get_user_by_email`
     - Script step to validate the result
   - Modify as needed for your use case

### Manual Creation

1. **Add Action Step**
   - Click **➕ Add Step** → **Action**
   - Action Name: `mw.get_user_by_email`
   - Output Key: `user_info`
   - Input Args: `{"email": "data.user_email"}`

2. **Add Validation Script**
   - Click **➕ Add Step** → **Script**
   - Output Key: `user_validation`
   - Code:
     ```python
     if hasattr(data.user_info, 'user') and data.user_info.user:
         return {
             "success": True,
             "user_id": data.user_info.user.id,
             "user_name": data.user_info.user.name
         }
     else:
         return {
             "success": False,
             "error": "User not found"
         }
     ```

## 🔍 Understanding the Interface

### Left Panel - Workflow Builder
- **Action Name** - Your workflow's unique identifier
- **Input Variables** - Data your workflow receives
- **Steps List** - The actions your workflow performs
- **Add/Remove/Reorder** buttons for managing steps

### Right Panel - Tools and Help
- **🎯 Data Helper** - Easy data path selection
- **📊 YAML Preview** - Real-time YAML output
- **🔍 JSON Explorer** - Browse workflow data structure
- **🐍 APIthon** - Script validation and help
- **📚 Examples** - Contextual examples and documentation

### Bottom Panel - Validation and Status
- **Validation Results** - Real-time error checking
- **Compliance Status** - Moveworks specification compliance
- **Help and Tips** - Contextual guidance

## ✅ Best Practices

### Naming Conventions
- Use `lowercase_snake_case` for all field names
- Make action names descriptive: `user_onboarding_workflow`
- Use clear output keys: `user_info`, `email_result`

### Data References
- Input variables: `data.variable_name`
- Step outputs: `data.output_key.field_name`
- User info: `meta_info.user.field_name`

### Error Handling
- Always validate API responses in scripts
- Use try-catch blocks for risky operations
- Provide meaningful error messages

### APIthon Scripts
- Keep scripts under 4096 bytes
- Always return a value (not None)
- Avoid imports, classes, and private methods
- Use simple, readable code

## 🆘 Getting Help

### In-App Help
- Hover over any field for tooltips
- Check the **📚 Examples** tab for contextual help
- Use the **🎯 Data Helper** for data path assistance

### Validation Messages
- Red indicators show errors that must be fixed
- Yellow indicators show warnings and suggestions
- Click on validation messages for detailed explanations

### Documentation
- **User Guide** - Comprehensive feature documentation
- **API Reference** - Moveworks action catalog
- **Tutorial System** - Interactive learning modules

## 🎉 Next Steps

Once you've created your first workflow:

1. **Test Your Workflow** - Use the validation system to check for errors
2. **Export YAML** - Copy the generated YAML for deployment
3. **Explore Advanced Features** - Try switch statements, loops, and parallel processing
4. **Create Templates** - Save your workflows as templates for reuse
5. **Learn More** - Explore the tutorial system for advanced techniques

Welcome to workflow automation with Moveworks! 🚀
