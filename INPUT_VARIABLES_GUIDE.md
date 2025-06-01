# Input Variables Guide for Moveworks YAML Assistant

## Overview

The Input Variables feature allows you to define reusable variables that can be passed into your Moveworks Compound Action workflows. This enables dynamic workflows that can accept different inputs each time they're executed.

## Key Features

### ✨ **Variable Definition**
- Define variables with specific data types
- Add descriptions for documentation
- Set required/optional status
- Specify default values for optional variables

### 🔧 **Data Type Support**
- `string` - Text values
- `number` - Numeric values (floating point)
- `integer` - Whole numbers
- `boolean` - True/false values
- `array` - Lists of values
- `object` - Complex data structures
- `List[string]`, `List[number]`, `List[integer]`, `List[boolean]`, `List[object]` - Typed arrays
- `User`, `List[User]` - Moveworks user objects

### 🎯 **Integration Features**
- Auto-completion for `data.{variable_name}` references
- Real-time validation of variable references
- YAML generation with `input_variables` section
- Visual UI for managing variables

## Getting Started

### 1. Adding Input Variables

1. **Open the Input Variables Panel**: Located in the left panel of the main interface
2. **Click "➕ Add Variable"**: Opens the variable definition dialog
3. **Fill in the details**:
   - **Variable Name**: Must be `lowercase_snake_case` (e.g., `user_email`, `max_results`)
   - **Data Type**: Select from the dropdown
   - **Description**: Optional but recommended for documentation
   - **Required**: Toggle whether the variable is mandatory
   - **Default Value**: Optional default for non-required variables

### 2. Using Input Variables in Steps

Once defined, input variables can be referenced in your workflow steps using the format:
```
data.{variable_name}
```

#### Example in Action Steps:
```yaml
- action: mw.get_user_by_email
  input_args:
    email: data.user_email        # References input variable
    limit: data.max_results       # References input variable
  output_key: user_info
```

#### Example in Script Steps:
```python
# Access input variables in APIthon scripts
user_email = data.user_email
max_count = data.max_results

# Process the data
if user_email:
    result = {"email": user_email, "limit": max_count}
else:
    result = {"error": "No email provided"}

return result
```

## Complete Example

### Input Variables Definition:
```yaml
input_variables:
  user_email:
    type: string
    description: Email address of the user to look up
    required: true
  
  max_results:
    type: integer
    description: Maximum number of results to return
    required: false
    default: 10
  
  include_details:
    type: boolean
    description: Whether to include detailed user information
    required: false
    default: false
```

### Workflow Using Input Variables:
```yaml
action_name: user_lookup_workflow
input_variables:
  user_email:
    type: string
    description: Email address of the user to look up
    required: true
  max_results:
    type: integer
    description: Maximum number of results to return
    required: false
    default: 10

steps:
  - action: mw.get_user_by_email
    input_args:
      email: data.user_email
      limit: data.max_results
    output_key: user_info
    description: Look up user by email address
  
  - script:
      code: |
        # Process the user lookup results
        user = data.user_info
        search_email = data.user_email
        limit = data.max_results
        
        if user:
            result = {
                "found": True,
                "user_id": user.get("id"),
                "email": search_email,
                "search_limit": limit
            }
        else:
            result = {
                "found": False,
                "email": search_email,
                "search_limit": limit
            }
        
        return result
    output_key: processed_result
    description: Process user lookup results
```

## Best Practices

### 📝 **Naming Conventions**
- Use `lowercase_snake_case` for variable names
- Choose descriptive names that indicate the variable's purpose
- Examples: `user_email`, `target_department`, `approval_threshold`

### 📋 **Documentation**
- Always add descriptions to explain what each variable is for
- Include examples in descriptions when helpful
- Document any constraints or expected formats

### 🔧 **Data Types**
- Choose the most specific data type possible
- Use `integer` instead of `number` when only whole numbers are expected
- Use typed arrays (`List[string]`) instead of generic `array` when possible

### ⚡ **Default Values**
- Provide sensible defaults for optional variables
- Consider the most common use case when setting defaults
- Use defaults to reduce the burden on workflow users

### 🔍 **Validation**
- The system automatically validates variable references
- Undefined variables will show validation errors
- Use the auto-completion feature to avoid typos

## UI Features

### Input Variables Table
- **Name**: Variable identifier
- **Type**: Data type
- **Required**: Whether the variable is mandatory
- **Default**: Default value (if any)
- **Description**: Documentation

### Variable Management
- **Add**: Create new input variables
- **Edit**: Modify existing variables (double-click or context menu)
- **Delete**: Remove variables (context menu)
- **Validation**: Real-time validation with 300ms debouncing

### Auto-completion
- Type `data.` in input fields to see available variables
- Auto-completion includes both input variables and step outputs
- Input variables are prioritized in the suggestion list

## Technical Implementation

### Core Components
- `InputVariable` dataclass with validation
- `InputVariablesWidget` UI component
- Enhanced YAML generation with `input_variables` section
- Auto-completion integration in JSON Path Selector
- Validation system for undefined variable references

### Integration Points
- **Left Panel**: Input Variables widget between action name and step list
- **YAML Generation**: Automatic inclusion of `input_variables` section
- **Validation**: Real-time checking of variable references
- **Auto-completion**: Enhanced suggestions in input fields

## Troubleshooting

### Common Issues

**Variable name validation errors:**
- Ensure names use `lowercase_snake_case`
- Start with a letter, use only letters, numbers, and underscores

**Undefined variable references:**
- Check that the variable is defined in the Input Variables section
- Verify the variable name spelling (case-sensitive)
- Use the format `data.{variable_name}`

**Data type mismatches:**
- Ensure default values match the specified data type
- Use appropriate data types for your use case

### Getting Help
- Use the auto-completion feature to see available variables
- Check the validation panel for specific error messages
- Refer to the Moveworks documentation for data type specifications

## Migration from Existing Workflows

If you have existing workflows that could benefit from input variables:

1. **Identify hardcoded values** that could be made dynamic
2. **Create input variables** for these values
3. **Update step references** to use `data.{variable_name}`
4. **Test the workflow** to ensure proper functionality

This feature enhances workflow reusability and makes your Compound Actions more flexible and maintainable.
