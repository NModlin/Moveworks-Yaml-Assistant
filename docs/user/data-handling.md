# Data Handling Guide

Master data manipulation, JSON processing, and data flow patterns in the Moveworks YAML Assistant.

## 📊 Data Sources Overview

The Moveworks YAML Assistant works with two primary data sources:

### 1. Workflow Data (`data.*`)
Contains input variables and step outputs from your workflow.

**Structure**:
```json
{
  "data": {
    "input_variable_name": "value",
    "step_output_key": { "result": "data" },
    "another_output": ["list", "of", "items"]
  }
}
```

### 2. Meta Information (`meta_info.*`)
Contains contextual information about the current user and request.

**Structure**:
```json
{
  "meta_info": {
    "user": {
      "first_name": "John",
      "last_name": "Doe",
      "email_addr": "john.doe@company.com",
      "department": "Engineering",
      "role": "Developer",
      "record_id": "user_12345"
    },
    "request": {
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

## 🔍 Data Reference Patterns

### Basic Data References

**Input Variables**:
```yaml
# Reference workflow input
input_args:
  user_email: data.input_email
  user_id: data.user_id
```

**Step Outputs**:
```yaml
# Reference previous step output
input_args:
  user_data: data.user_lookup_result
  processed_info: data.processing_step_output
```

**Meta Information**:
```yaml
# Reference current user information
input_args:
  current_user: meta_info.user.email_addr
  department: meta_info.user.department
  user_name: meta_info.user.first_name
```

### Nested Data Access

**Deep Object Navigation**:
```yaml
# Access nested object properties
input_args:
  user_name: data.user_info.user.name
  manager_email: data.user_info.user.manager.email
  first_permission: data.user_info.permissions[0]
```

**Array Access**:
```yaml
# Access array elements
input_args:
  first_user: data.users_list[0]
  last_item: data.results[-1]
  specific_field: data.items[2].name
```

## 🛠️ JSON Path Selector

The JSON Path Selector provides a visual way to navigate and select data paths.

### Using the JSON Path Selector

1. **Add Sample Data**: Paste JSON output in any step
2. **Parse JSON**: Click "Parse & Save JSON Output"
3. **Open Selector**: Click `🔍 JSON Path Selector`
4. **Navigate Structure**: Use tree view to explore data
5. **Select Paths**: Click any path to copy it
6. **Use in Workflow**: Paste paths in data reference fields

### Example JSON Structure
```json
{
  "user": {
    "id": "emp_12345",
    "personal": {
      "name": "John Doe",
      "email": "john.doe@company.com"
    },
    "work": {
      "department": "Engineering",
      "role": "Senior Developer",
      "manager": {
        "name": "Jane Smith",
        "email": "jane.smith@company.com"
      }
    },
    "permissions": ["read", "write", "admin"],
    "projects": [
      {"name": "Project A", "status": "active"},
      {"name": "Project B", "status": "completed"}
    ]
  }
}
```

### Generated Paths
- `data.user_info.user.personal.name` → "John Doe"
- `data.user_info.user.work.department` → "Engineering"
- `data.user_info.user.manager.email` → "jane.smith@company.com"
- `data.user_info.user.permissions[0]` → "read"
- `data.user_info.user.projects[0].name` → "Project A"

## 🔄 Data Flow Patterns

### Sequential Data Flow
Each step builds on previous step outputs:

```yaml
steps:
# Step 1: Fetch user data
- action:
    action_name: get_user_by_email
    output_key: user_info
    input_args:
      email: data.input_email

# Step 2: Process user data (uses Step 1 output)
- script:
    code: |
      full_name = f"{user.first_name} {user.last_name}"
      return {"full_name": full_name, "department": user.department}
    input_args:
      user: data.user_info.user
    output_key: processed_user

# Step 3: Send notification (uses Step 2 output)
- action:
    action_name: send_notification
    output_key: notification_result
    input_args:
      recipient: data.processed_user.full_name
      message: f"Welcome to {data.processed_user.department}!"
```

### Parallel Data Flow
Multiple independent operations:

```yaml
parallel:
  branches:
  # Branch 1: Fetch user data
  - steps:
    - action:
        action_name: get_user_details
        output_key: user_details
        input_args:
          user_id: data.user_id
  
  # Branch 2: Fetch permissions (independent)
  - steps:
    - action:
        action_name: get_user_permissions
        output_key: user_permissions
        input_args:
          user_id: data.user_id
```

### Conditional Data Flow
Different paths based on data values:

```yaml
switch:
  cases:
  - condition: data.user_info.user.role == 'admin'
    steps:
    - action:
        action_name: fetch_admin_data
        output_key: admin_specific_data
        input_args:
          admin_id: data.user_info.user.id
  
  - condition: data.user_info.user.role == 'manager'
    steps:
    - action:
        action_name: fetch_team_data
        output_key: team_data
        input_args:
          manager_id: data.user_info.user.id
  
  default:
    steps:
    - script:
        code: 'return {"message": "Standard user access"}'
        output_key: standard_access
```

## 🧮 Data Transformation

### Script-Based Transformation

**Simple Transformations**:
```python
# Extract specific fields
user_summary = {
    "name": data.user_info.user.name,
    "email": data.user_info.user.email,
    "department": data.user_info.user.department
}
return user_summary
```

**List Processing**:
```python
# Process arrays of data
active_projects = [
    project for project in data.projects 
    if project.status == 'active'
]
return {"active_projects": active_projects}
```

**Data Aggregation**:
```python
# Calculate statistics
total_users = len(data.users_list)
departments = list(set(user.department for user in data.users_list))
summary = {
    "total_users": total_users,
    "unique_departments": len(departments),
    "departments": departments
}
return summary
```

### Return Expression Mapping

**Simple Mapping**:
```yaml
return:
  output_mapper:
    user_name: data.user_info.user.name
    user_email: data.user_info.user.email
    department: data.user_info.user.department
```

**Complex Expressions**:
```yaml
return:
  output_mapper:
    # Conditional expressions
    is_admin: data.user_info.user.role == 'admin'
    
    # String concatenation
    full_name: data.user_info.user.first_name + ' ' + data.user_info.user.last_name
    
    # Nested data access
    manager_email: data.user_info.user.manager.email
    
    # Meta information
    processed_by: meta_info.user.email_addr
    processed_at: meta_info.request.timestamp
```

## 🔧 Advanced Data Techniques

### Dynamic Data References

**Variable Path Construction**:
```python
# Build paths dynamically
field_name = "department"
user_field = getattr(data.user_info.user, field_name)
return {"dynamic_field": user_field}
```

**Conditional Data Access**:
```python
# Safe data access with fallbacks
manager_name = (
    data.user_info.user.manager.name 
    if hasattr(data.user_info.user, 'manager') 
    else "No manager assigned"
)
return {"manager": manager_name}
```

### Data Validation

**Type Checking**:
```python
# Validate data types
if isinstance(data.user_list, list) and len(data.user_list) > 0:
    first_user = data.user_list[0]
    return {"valid": True, "first_user": first_user}
else:
    return {"valid": False, "error": "Invalid user list"}
```

**Required Field Validation**:
```python
# Check for required fields
required_fields = ['name', 'email', 'department']
user = data.user_info.user

missing_fields = [
    field for field in required_fields 
    if not hasattr(user, field) or not getattr(user, field)
]

if missing_fields:
    return {"error": f"Missing fields: {missing_fields}"}
else:
    return {"valid": True, "user": user}
```

## 💡 Best Practices

### Data Reference Guidelines
1. **Use Descriptive Names**: Choose clear, meaningful output_key names
2. **Plan Data Flow**: Map out data dependencies before building
3. **Validate Early**: Check data structure and types early in workflows
4. **Handle Errors**: Provide fallbacks for missing or invalid data

### Performance Optimization
1. **Minimize Data Processing**: Keep scripts simple and focused
2. **Use Parallel Execution**: Process independent data streams concurrently
3. **Cache Results**: Store frequently accessed data in variables
4. **Avoid Deep Nesting**: Flatten complex data structures when possible

### Security Considerations
1. **Sanitize Input**: Validate and clean external data
2. **Limit Data Exposure**: Only include necessary data in outputs
3. **Use Meta Info Carefully**: Be mindful of user context data
4. **Validate Permissions**: Check user access before processing sensitive data

---

*For practical examples, see the [Interactive Tutorials](tutorials.md) and [Template Library](templates.md)*
