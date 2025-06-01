# Expression Types Guide

Complete reference for all 8 Moveworks expression types supported by the YAML Assistant.

## 📋 Expression Types Overview

The Moveworks YAML Assistant supports all 8 official Moveworks expression types:

| Expression | Category | Purpose | Complexity |
|------------|----------|---------|------------|
| **action** | Core | HTTP requests, API calls | ⭐ Basic |
| **script** | Core | Data processing, calculations | ⭐⭐ Intermediate |
| **switch** | Control Flow | Conditional logic | ⭐⭐ Intermediate |
| **for** | Control Flow | Iteration, loops | ⭐⭐⭐ Advanced |
| **parallel** | Control Flow | Concurrent execution | ⭐⭐⭐ Advanced |
| **return** | Output | Return processed data | ⭐⭐ Intermediate |
| **raise** | Error Handling | Throw custom errors | ⭐⭐ Intermediate |
| **try_catch** | Error Handling | Error recovery | ⭐⭐⭐ Advanced |

## 🎯 Core Expressions

### action - HTTP Requests and API Calls

**Purpose**: Execute HTTP requests or call native Moveworks actions.

**Required Fields**:
- `action_name`: The action to execute
- `output_key`: Variable to store the result

**Optional Fields**:
- `input_args`: Parameters for the action
- `delay_config`: Execution delay configuration
- `progress_updates`: User progress messages

**Example**:
```yaml
action:
  action_name: mw.get_user_by_email
  output_key: user_info
  input_args:
    email: data.input_email
  delay_config:
    seconds: "5"
  progress_updates:
    on_pending: "Looking up user..."
    on_complete: "User found successfully!"
```

**Common Use Cases**:
- Fetch user information
- Create tickets or records
- Send notifications
- Query external APIs

### script - Data Processing and Calculations

**Purpose**: Execute Python code for data transformation and processing.

**Required Fields**:
- `code`: Python code to execute
- `output_key`: Variable to store the result

**Optional Fields**:
- `input_args`: Variables available in the script

**Example**:
```yaml
script:
  code: |
    # Process user data
    full_name = f"{user.first_name} {user.last_name}"
    summary = {
        "name": full_name,
        "email": user.email,
        "department": user.department
    }
    return summary
  input_args:
    user: data.user_info.user
  output_key: user_summary
```

**APIthon Limitations**:
- Maximum 4096 bytes of code
- No imports allowed
- No class definitions
- No private methods (underscore-prefixed)
- Must return a value

## 🔀 Control Flow Expressions

### switch - Conditional Logic

**Purpose**: Execute different steps based on conditions (if/else logic).

**Required Fields**:
- `cases`: List of condition/steps pairs

**Optional Fields**:
- `default`: Steps to execute if no conditions match

**Example**:
```yaml
switch:
  cases:
  - condition: data.user_info.user.role == 'admin'
    steps:
    - action:
        action_name: send_admin_notification
        output_key: admin_notification
        input_args:
          message: "Admin access granted"
  - condition: data.user_info.user.role == 'manager'
    steps:
    - action:
        action_name: send_manager_notification
        output_key: manager_notification
  default:
    steps:
    - action:
        action_name: send_user_notification
        output_key: user_notification
        input_args:
          message: "Standard access granted"
```

### for - Iteration and Loops

**Purpose**: Execute steps for each item in a collection.

**Required Fields**:
- `each`: Variable name for current item
- `index`: Variable name for current index
- `in`: Collection to iterate over
- `output_key`: Variable to store results

**Optional Fields**:
- `steps`: Steps to execute for each item

**Example**:
```yaml
for:
  each: user
  index: user_index
  in: data.users_list
  output_key: notification_results
  steps:
  - action:
      action_name: send_welcome_email
      output_key: email_result
      input_args:
        user_email: user.email
        user_name: user.name
```

### parallel - Concurrent Execution

**Purpose**: Execute multiple operations simultaneously for better performance.

**Two Modes**:

**Mode 1: Parallel For Loop**
```yaml
parallel:
  for:
    each: user_id
    in: data.user_ids
    index_key: user_index
    output_key: parallel_results
    steps:
    - action:
        action_name: fetch_user_details
        output_key: user_details
        input_args:
          user_id: user_id
```

**Mode 2: Parallel Branches**
```yaml
parallel:
  branches:
  - steps:
    - action:
        action_name: fetch_user_data
        output_key: user_data
  - steps:
    - action:
        action_name: fetch_permissions
        output_key: permissions
```

## 📤 Output Expressions

### return - Return Processed Data

**Purpose**: Return structured data as the workflow output.

**Required Fields**:
- `output_mapper`: Dictionary mapping output keys to data paths

**Example**:
```yaml
return:
  output_mapper:
    user_name: data.user_info.user.name
    user_email: data.user_info.user.email
    department: data.user_info.user.department
    greeting: data.greeting_result.greeting
    processed_at: meta_info.request.timestamp
```

**Advanced Mapping**:
```yaml
return:
  output_mapper:
    # Simple data references
    user_id: data.user_info.user.id
    
    # Complex expressions
    is_admin: data.user_info.user.role == 'admin'
    full_name: data.user_info.user.first_name + ' ' + data.user_info.user.last_name
    
    # Nested data access
    manager_email: data.user_info.user.manager.email
```

## ⚠️ Error Handling Expressions

### raise - Throw Custom Errors

**Purpose**: Terminate workflow execution with a custom error message.

**Required Fields**:
- `message`: Error message to display

**Optional Fields**:
- `output_key`: Variable to store error information

**Example**:
```yaml
raise:
  message: "User not found in the system"
  output_key: error_info
```

**Conditional Error Raising**:
```yaml
switch:
  cases:
  - condition: data.user_info == null
    steps:
    - raise:
        message: "User lookup failed - invalid email address"
        output_key: lookup_error
  default:
    steps:
    - return:
        output_mapper:
          user_name: data.user_info.user.name
```

### try_catch - Error Recovery

**Purpose**: Handle errors gracefully and provide fallback behavior.

**Required Fields**:
- `output_key`: Variable to store try/catch results

**Optional Fields**:
- `status_codes`: HTTP status codes that trigger catch block

**Example**:
```yaml
try_catch:
  output_key: api_call_result
  status_codes: "400,404,500"
  try:
    steps:
    - action:
        action_name: external_api_call
        output_key: api_response
        input_args:
          user_id: data.user_id
  catch:
    steps:
    - script:
        code: |
          return {
            "error": "API call failed",
            "fallback_data": "default_user_info",
            "timestamp": "2024-01-01T00:00:00Z"
          }
        output_key: fallback_response
```

## 🎯 Best Practices

### Naming Conventions
- Use `lowercase_snake_case` for all field names
- Choose descriptive `output_key` names
- Use consistent naming patterns across workflows

### Data Flow
- Plan your data flow before building
- Use meaningful variable names
- Document complex data transformations

### Error Handling
- Always handle potential failure points
- Provide meaningful error messages
- Use try_catch for external API calls

### Performance
- Use parallel execution for independent operations
- Minimize data processing in scripts
- Cache frequently accessed data

## 🔧 Expression Configuration Tips

### action Steps
- Test API calls independently first
- Use realistic sample data
- Configure appropriate delays for external APIs

### script Steps
- Keep code simple and focused
- Use descriptive variable names
- Test logic with sample data

### Control Flow
- Plan conditions carefully
- Provide default cases
- Test all branches

### Error Handling
- Anticipate common failure scenarios
- Provide helpful error messages
- Include recovery mechanisms

## 📚 Learning Resources

### Interactive Tutorials
- **Basic Workflow Tutorial**: Learn action and script expressions
- **Control Flow Tutorial**: Master switch and for expressions
- **Advanced Tutorial**: Parallel execution and error handling

### Template Library
- Browse ready-made examples for each expression type
- Copy and customize templates for your needs
- Study real-world implementation patterns

### Practice Exercises
1. **User Management**: Create a user onboarding workflow
2. **Data Processing**: Build a data transformation pipeline
3. **Error Handling**: Implement robust error recovery
4. **Performance**: Optimize with parallel execution

---

*For hands-on practice with these expressions, try the [Interactive Tutorials](tutorials.md)*
