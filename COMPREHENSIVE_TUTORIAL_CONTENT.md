# Comprehensive Tutorial Content for Moveworks YAML Assistant

This document contains the complete tutorial content for the Moveworks YAML Assistant application, designed to integrate with the existing PySide6 overlay tutorial system.

## Tutorial System Overview

The tutorial content follows a progressive 6-module learning path, with each module building upon previous knowledge while demonstrating specific features of the YAML Assistant application.

### Learning Path Structure

1. **Module 1**: Your First Compound Action - Basic lookup and notification
2. **Module 2**: IT Automation - ServiceNow/Jira ticket creation  
3. **Module 3**: Conditional Logic - Approval routing with switch statements
4. **Module 4**: Data Processing - List handling with script steps
5. **Module 5**: Error Handling - Robust API calls with try-catch
6. **Module 6**: Advanced Integration - Multi-system workflows

---

## Module 1: Your First Compound Action - Simple Lookup and Notification

### Learning Objectives
- Understand basic compound action structure and YAML compliance
- Create your first `action` step with proper data flow
- Use the JSON Path Selector for basic data selection
- Generate compliant YAML with mandatory `action_name` and `steps` fields
- Validate workflow using the built-in compliance system

### Prerequisites
- Basic understanding of YAML syntax
- Familiarity with REST API concepts
- Moveworks YAML Assistant application installed and running

### Real-World Scenario
**Employee Onboarding Notification System**: When a new employee joins the company, HR needs to automatically look up their manager's information and send a welcome notification. This workflow demonstrates the fundamental pattern of data lookup followed by action execution.

### Key Concepts

#### Compound Action Structure
Every Moveworks compound action requires this mandatory structure:
```yaml
action_name: your_compound_action_name  # Top-level identifier
steps:                                  # Mandatory steps array
  - action:                            # Individual workflow steps
      action_name: mw.get_user_by_email
      output_key: user_info
      input_args:
        email: "data.input_email"
```

#### Data Flow Pattern
- **Input Variables**: `data.input_email` (provided when workflow executes)
- **Output Keys**: `data.user_info` (result from first step)
- **Data References**: Use `"data.field_name"` syntax for DSL expressions

#### JSON Path Selector Integration
The JSON Path Selector automatically populates when you select steps with parsed JSON output, allowing visual selection of data paths.

### Interactive Guided Steps

#### Step 1: Set Compound Action Name
**Action**: In the main interface, locate the "Compound Action Name" field at the top
**Instructions**: 
1. Click in the compound action name field
2. Enter: `employee_welcome_notification`
3. Notice how this becomes the top-level `action_name` in the YAML preview

**Copy-Paste Example**:
```
employee_welcome_notification
```

**Expected Outcome**: The YAML preview shows `action_name: employee_welcome_notification` at the top level.

#### Step 2: Add First Action Step
**Action**: Click "Add Step" → "Action Step"
**Instructions**:
1. Set Action Name: `mw.get_user_by_email`
2. Set Output Key: `user_info`
3. In Input Args, add:
   - Key: `email`
   - Value: `data.input_email`

**Copy-Paste Example**:
```yaml
action_name: mw.get_user_by_email
output_key: user_info
input_args:
  email: "data.input_email"
```

**Expected Outcome**: First step appears in the workflow with proper data referencing.

#### Step 3: Add Sample JSON Output
**Action**: In the Action Step configuration, find "User Provided JSON Output"
**Instructions**:
1. Click "Add Sample JSON"
2. Paste the following sample response:

**Copy-Paste Example**:
```json
{
  "user": {
    "id": "emp_12345",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "manager": {
      "id": "mgr_67890",
      "name": "Jane Smith",
      "email": "jane.smith@company.com"
    },
    "active": true
  }
}
```

**Expected Outcome**: JSON data is parsed and available for path selection in subsequent steps.

#### Step 4: Open JSON Path Selector
**Action**: Click "Tools" → "JSON Path Selector" or use the JSON Explorer tab
**Instructions**:
1. Select "Step 1: user_info" from the step dropdown
2. Explore the available data structure
3. Notice how the tree shows `data.user_info.user.name`, `data.user_info.user.manager.email`, etc.

**Expected Outcome**: JSON tree populates with selectable data paths from the first step.

#### Step 5: Add Notification Action
**Action**: Click "Add Step" → "Action Step"
**Instructions**:
1. Set Action Name: `mw.send_notification`
2. Set Output Key: `notification_result`
3. In Input Args, add:
   - Key: `recipient`
   - Value: Use JSON Path Selector to select `data.user_info.user.manager.email`
   - Key: `message`
   - Value: `Welcome to the team! Please reach out to help onboard our new team member.`

**Copy-Paste Example**:
```yaml
action_name: mw.send_notification
output_key: notification_result
input_args:
  recipient: "data.user_info.user.manager.email"
  message: "Welcome to the team! Please reach out to help onboard our new team member."
```

**Expected Outcome**: Second step configured with data reference from first step.

#### Step 6: Validate Compliance
**Action**: Click "Validate" button or check the validation panel
**Instructions**:
1. Review validation results
2. Ensure all mandatory fields are present
3. Verify DSL expressions are properly quoted
4. Check that `steps` array structure is correct

**Expected Outcome**: Green validation status with "Workflow is Moveworks compliant" message.

#### Step 7: Review Generated YAML
**Action**: Check the YAML Preview panel
**Instructions**:
1. Verify the complete structure matches Moveworks requirements
2. Notice the automatic DSL string quoting
3. Confirm proper indentation and field ordering

**Expected Outcome**: Complete, valid YAML ready for export.

### Complete Working Example

```yaml
action_name: employee_welcome_notification
steps:
  - action:
      action_name: mw.get_user_by_email
      output_key: user_info
      input_args:
        email: "data.input_email"
  - action:
      action_name: mw.send_notification
      output_key: notification_result
      input_args:
        recipient: "data.user_info.user.manager.email"
        message: "Welcome to the team! Please reach out to help onboard our new team member."
```

### Troubleshooting Section

#### Common Error: Missing Compound Action Name
**Problem**: YAML shows steps without top-level action_name
**Solution**: Ensure the compound action name field is filled before adding steps
**Prevention**: Always start with naming your compound action

#### Common Error: Unquoted DSL Expressions
**Problem**: Data references like `data.user_info.email` appear without quotes
**Solution**: The system should auto-quote DSL expressions; check validation panel
**Prevention**: Use the JSON Path Selector for automatic proper formatting

#### Common Error: Invalid JSON Sample
**Problem**: JSON Path Selector shows "No data available"
**Solution**: Verify JSON syntax in the sample output field
**Prevention**: Use the JSON validator or copy from working API responses

#### Common Error: Missing Output Keys
**Problem**: Cannot reference data from previous steps
**Solution**: Ensure each action step has a unique, descriptive output_key
**Prevention**: Use descriptive names like `user_info`, `notification_result`

### Summary
You've successfully created your first Moveworks compound action! Key learning points:

1. **Mandatory Structure**: Every compound action needs `action_name` and `steps` fields
2. **Data Flow**: Use `data.output_key` to reference results from previous steps
3. **DSL Quoting**: Data references are automatically quoted as strings in YAML
4. **JSON Path Selector**: Visual tool for selecting data paths from step outputs
5. **Validation**: Built-in compliance checking ensures Moveworks compatibility

### Next Steps
Ready for **Module 2: IT Automation**? You'll learn to:
- Import cURL commands and convert to action steps
- Use parameterization with `{{{VARIABLES}}}`
- Leverage the template library for common IT workflows
- Handle more complex input arguments and delay configurations

---

## Module 2: IT Automation - ServiceNow/Jira Ticket Creation

### Learning Objectives
- Import and convert cURL commands to action steps
- Use parameterization with `{{{VARIABLES}}}` for dynamic values
- Leverage the template library for common IT automation patterns
- Configure delay settings and progress updates for user experience
- Handle complex input arguments with nested data structures

### Prerequisites
- Completion of Module 1: Your First Compound Action
- Basic understanding of REST API authentication
- Familiarity with ServiceNow or Jira ticket systems

### Real-World Scenario
**Automated Incident Response**: When a critical system alert is triggered, IT needs to automatically create tickets in both ServiceNow for tracking and Jira for development team assignment. This workflow demonstrates enterprise IT automation with multiple system integration and proper error handling.

### Key Concepts

#### cURL Import and Conversion
The YAML Assistant can import cURL commands and automatically convert them to action steps:
```bash
curl -X POST "https://company.service-now.com/api/now/table/incident" \
  -H "Authorization: Bearer {{{SERVICENOW_TOKEN}}}" \
  -H "Content-Type: application/json" \
  -d '{"short_description": "Critical Alert", "urgency": "1"}'
```

#### Parameterization Patterns
Use `{{{VARIABLE_NAME}}}` for values that should be configurable:
- `{{{SERVICENOW_TOKEN}}}` - Authentication tokens
- `{{{ALERT_SEVERITY}}}` - Dynamic severity levels
- `{{{ASSIGNEE_GROUP}}}` - Team assignments

#### Template Library Integration
Access pre-built templates for common IT scenarios:
- ServiceNow incident creation
- Jira issue creation
- Slack notifications
- Email alerts

### Interactive Guided Steps

#### Step 1: Set Compound Action Name
**Action**: Enter compound action name
**Instructions**:
1. Set name: `critical_alert_incident_response`
2. Add description: "Automated incident response for critical system alerts"

**Copy-Paste Example**:
```
critical_alert_incident_response
```

#### Step 2: Import ServiceNow cURL Command
**Action**: Click "Import" → "From cURL"
**Instructions**:
1. Paste the ServiceNow cURL command
2. Review the auto-generated action step
3. Modify parameterized values as needed

**Copy-Paste Example**:
```bash
curl -X POST "https://company.service-now.com/api/now/table/incident" \
  -H "Authorization: Bearer {{{SERVICENOW_TOKEN}}}" \
  -H "Content-Type: application/json" \
  -d '{
    "short_description": "{{{ALERT_TITLE}}}",
    "description": "{{{ALERT_DESCRIPTION}}}",
    "urgency": "{{{ALERT_SEVERITY}}}",
    "category": "Software",
    "subcategory": "Application",
    "caller_id": "{{{REPORTER_ID}}}"
  }'
```

**Expected Outcome**: Action step created with proper HTTP configuration and parameterized input arguments.

#### Step 3: Configure ServiceNow Action Step
**Action**: Review and modify the imported action step
**Instructions**:
1. Set Output Key: `servicenow_incident`
2. Add delay configuration:
   - Delay Seconds: `5`
3. Add progress updates:
   - On Pending: `"Creating ServiceNow incident..."`
   - On Complete: `"ServiceNow incident created successfully"`

**Copy-Paste Example**:
```yaml
action:
  action_name: http_request
  output_key: servicenow_incident
  input_args:
    url: "https://company.service-now.com/api/now/table/incident"
    method: "POST"
    headers:
      Authorization: "Bearer {{{SERVICENOW_TOKEN}}}"
      Content-Type: "application/json"
    body:
      short_description: "{{{ALERT_TITLE}}}"
      description: "{{{ALERT_DESCRIPTION}}}"
      urgency: "{{{ALERT_SEVERITY}}}"
      category: "Software"
      subcategory: "Application"
      caller_id: "{{{REPORTER_ID}}}"
  delay_config:
    delay_seconds: 5
  progress_updates:
    on_pending: "Creating ServiceNow incident..."
    on_complete: "ServiceNow incident created successfully"
```

#### Step 4: Add Sample ServiceNow Response
**Action**: Add sample JSON output for the ServiceNow step
**Instructions**:
1. In the ServiceNow action step, add sample JSON output
2. This enables data path selection for subsequent steps

**Copy-Paste Example**:
```json
{
  "result": {
    "sys_id": "abc123def456",
    "number": "INC0012345",
    "short_description": "Critical Database Connection Failure",
    "state": "1",
    "urgency": "1",
    "priority": "1",
    "assigned_to": "",
    "assignment_group": "Database Team",
    "sys_created_on": "2024-01-15 10:30:00",
    "sys_updated_on": "2024-01-15 10:30:00"
  }
}
```

#### Step 5: Use Template Library for Jira Integration
**Action**: Click "Templates" → "IT Automation" → "Jira Issue Creation"
**Instructions**:
1. Select the Jira issue creation template
2. Customize for your environment
3. Link to ServiceNow incident data

**Copy-Paste Example**:
```yaml
action:
  action_name: http_request
  output_key: jira_issue
  input_args:
    url: "https://company.atlassian.net/rest/api/3/issue"
    method: "POST"
    headers:
      Authorization: "Bearer {{{JIRA_TOKEN}}}"
      Content-Type: "application/json"
    body:
      fields:
        project:
          key: "INFRA"
        summary: "ServiceNow Incident: {{{ALERT_TITLE}}}"
        description: |
          Critical alert requiring immediate attention.

          ServiceNow Incident: data.servicenow_incident.result.number
          Alert Details: {{{ALERT_DESCRIPTION}}}
          Severity: {{{ALERT_SEVERITY}}}
        issuetype:
          name: "Bug"
        priority:
          name: "Critical"
        assignee:
          accountId: "{{{JIRA_ASSIGNEE_ID}}}"
  delay_config:
    delay_seconds: 3
  progress_updates:
    on_pending: "Creating Jira issue..."
    on_complete: "Jira issue created successfully"
```

#### Step 6: Link ServiceNow and Jira Data
**Action**: Use JSON Path Selector to reference ServiceNow data in Jira step
**Instructions**:
1. Open JSON Path Selector
2. Select ServiceNow step data
3. Choose `data.servicenow_incident.result.number`
4. Use in Jira description field

**Expected Outcome**: Jira issue description includes ServiceNow incident number for cross-system tracking.

#### Step 7: Add Notification Step
**Action**: Add final notification step
**Instructions**:
1. Add action step for Slack notification
2. Include both ServiceNow and Jira references
3. Use template for consistent formatting

**Copy-Paste Example**:
```yaml
action:
  action_name: mw.send_slack_message
  output_key: notification_result
  input_args:
    channel: "#critical-alerts"
    message: |
      🚨 Critical Alert Response Initiated

      Alert: {{{ALERT_TITLE}}}
      ServiceNow: data.servicenow_incident.result.number
      Jira: data.jira_issue.key

      Both systems have been notified and tickets created.
    username: "AlertBot"
    icon_emoji: ":warning:"
```

### Complete Working Example

```yaml
action_name: critical_alert_incident_response
steps:
  - action:
      action_name: http_request
      output_key: servicenow_incident
      input_args:
        url: "https://company.service-now.com/api/now/table/incident"
        method: "POST"
        headers:
          Authorization: "Bearer {{{SERVICENOW_TOKEN}}}"
          Content-Type: "application/json"
        body:
          short_description: "{{{ALERT_TITLE}}}"
          description: "{{{ALERT_DESCRIPTION}}}"
          urgency: "{{{ALERT_SEVERITY}}}"
          category: "Software"
          subcategory: "Application"
          caller_id: "{{{REPORTER_ID}}}"
      delay_config:
        delay_seconds: 5
      progress_updates:
        on_pending: "Creating ServiceNow incident..."
        on_complete: "ServiceNow incident created successfully"
  - action:
      action_name: http_request
      output_key: jira_issue
      input_args:
        url: "https://company.atlassian.net/rest/api/3/issue"
        method: "POST"
        headers:
          Authorization: "Bearer {{{JIRA_TOKEN}}}"
          Content-Type: "application/json"
        body:
          fields:
            project:
              key: "INFRA"
            summary: "ServiceNow Incident: {{{ALERT_TITLE}}}"
            description: |
              Critical alert requiring immediate attention.

              ServiceNow Incident: "data.servicenow_incident.result.number"
              Alert Details: {{{ALERT_DESCRIPTION}}}
              Severity: {{{ALERT_SEVERITY}}}
            issuetype:
              name: "Bug"
            priority:
              name: "Critical"
            assignee:
              accountId: "{{{JIRA_ASSIGNEE_ID}}}"
      delay_config:
        delay_seconds: 3
      progress_updates:
        on_pending: "Creating Jira issue..."
        on_complete: "Jira issue created successfully"
  - action:
      action_name: mw.send_slack_message
      output_key: notification_result
      input_args:
        channel: "#critical-alerts"
        message: |
          🚨 Critical Alert Response Initiated

          Alert: {{{ALERT_TITLE}}}
          ServiceNow: "data.servicenow_incident.result.number"
          Jira: "data.jira_issue.key"

          Both systems have been notified and tickets created.
        username: "AlertBot"
        icon_emoji: ":warning:"
```

### Troubleshooting Section

#### Common Error: cURL Import Fails
**Problem**: Imported cURL doesn't convert properly
**Solution**: Ensure cURL uses standard format with proper escaping
**Prevention**: Test cURL commands independently before importing

#### Common Error: Authentication Token Issues
**Problem**: API calls fail with 401/403 errors
**Solution**: Verify `{{{TOKEN_NAME}}}` parameterization is correct
**Prevention**: Use consistent token naming conventions

#### Common Error: JSON Body Formatting
**Problem**: API rejects request body format
**Solution**: Validate JSON structure in the input_args body field
**Prevention**: Copy working API examples from system documentation

#### Common Error: Data Reference Syntax
**Problem**: Cannot access data from previous steps
**Solution**: Use proper DSL syntax: `"data.output_key.field.subfield"`
**Prevention**: Use JSON Path Selector for accurate path generation

### Summary
You've mastered IT automation workflows! Key learning points:

1. **cURL Import**: Streamlined conversion from command-line to action steps
2. **Parameterization**: `{{{VARIABLES}}}` for configurable, reusable workflows
3. **Template Library**: Pre-built patterns for common IT scenarios
4. **Cross-System Integration**: Linking data between ServiceNow, Jira, and notifications
5. **User Experience**: Progress updates and delays for better workflow feedback

### Next Steps
Ready for **Module 3: Conditional Logic**? You'll learn to:
- Create switch expressions for approval routing
- Use conditional data mapping with complex logic
- Implement SwitchStep class with multiple cases
- Handle default cases and nested conditional flows

---

## Module 3: Conditional Logic - Approval Routing with Switch Statements

### Learning Objectives
- Create `switch` expressions for conditional workflow branching
- Use conditional data mapping with complex business logic
- Implement SwitchStep class with multiple cases and default handling
- Handle nested conditional flows and data validation
- Integrate switch logic with the compliance validation system

### Prerequisites
- Completion of Module 2: IT Automation
- Understanding of conditional logic and boolean expressions
- Familiarity with business approval processes

### Real-World Scenario
**Expense Approval Routing System**: When employees submit expense reports, the approval process varies based on amount, department, and employee level. Expenses under $100 auto-approve, $100-$1000 go to managers, and over $1000 require director approval. This workflow demonstrates complex conditional logic with multiple decision points.

### Key Concepts

#### Switch Expression Structure
Switch expressions evaluate conditions and execute different steps based on results:
```yaml
switch:
  cases:
    - condition: "data.expense_amount < 100"
      steps:
        - action:
            action_name: mw.auto_approve_expense
    - condition: "data.expense_amount >= 100 && data.expense_amount <= 1000"
      steps:
        - action:
            action_name: mw.send_manager_approval
  default:
    steps:
      - action:
          action_name: mw.send_director_approval
  output_key: approval_routing_result
```

#### Conditional Data Mapping
Use DSL expressions for dynamic data evaluation:
- `data.expense_amount >= 1000` - Numeric comparisons
- `data.employee_level == 'senior'` - String equality
- `data.department == 'Engineering' && data.expense_amount > 500` - Complex logic

#### SwitchStep Class Integration
The YAML Assistant uses the SwitchStep class to manage conditional logic with proper validation and YAML generation.

### Interactive Guided Steps

#### Step 1: Set Compound Action Name
**Action**: Enter compound action name
**Instructions**:
1. Set name: `expense_approval_routing`
2. Add description: "Automated expense approval routing based on amount and employee level"

**Copy-Paste Example**:
```
expense_approval_routing
```

#### Step 2: Add Expense Validation Step
**Action**: Click "Add Step" → "Action Step"
**Instructions**:
1. Set Action Name: `mw.validate_expense_submission`
2. Set Output Key: `expense_validation`
3. Add input arguments for expense data

**Copy-Paste Example**:
```yaml
action:
  action_name: mw.validate_expense_submission
  output_key: expense_validation
  input_args:
    employee_id: "data.employee_id"
    expense_amount: "data.expense_amount"
    expense_category: "data.expense_category"
    receipt_attached: "data.receipt_attached"
```

#### Step 3: Add Sample Expense Data
**Action**: Add sample JSON output for expense validation
**Instructions**:
1. In the expense validation step, add sample JSON output
2. Include employee details and expense information

**Copy-Paste Example**:
```json
{
  "expense": {
    "id": "EXP-2024-001",
    "amount": 750.00,
    "category": "Travel",
    "description": "Client meeting travel expenses",
    "receipt_url": "https://receipts.company.com/exp001.pdf"
  },
  "employee": {
    "id": "emp_12345",
    "name": "John Doe",
    "department": "Sales",
    "level": "senior",
    "manager_id": "mgr_67890",
    "director_id": "dir_11111"
  },
  "validation": {
    "is_valid": true,
    "receipt_verified": true,
    "policy_compliant": true
  }
}
```

#### Step 4: Add Switch Expression
**Action**: Click "Add Step" → "Switch Step"
**Instructions**:
1. Set description: "Route approval based on expense amount and employee level"
2. Set output key: `approval_routing`
3. Begin adding cases for different approval scenarios

**Expected Outcome**: Switch step framework created, ready for case configuration.

#### Step 5: Configure Auto-Approval Case
**Action**: In the Switch step, click "Add Case"
**Instructions**:
1. Set condition: `data.expense_validation.expense.amount < 100 && data.expense_validation.validation.is_valid == true`
2. Add action step for auto-approval

**Copy-Paste Example**:
```yaml
condition: "data.expense_validation.expense.amount < 100 && data.expense_validation.validation.is_valid == true"
steps:
  - action:
      action_name: mw.auto_approve_expense
      output_key: auto_approval_result
      input_args:
        expense_id: "data.expense_validation.expense.id"
        approved_amount: "data.expense_validation.expense.amount"
        approval_reason: "Auto-approved: Amount under $100 threshold"
```

#### Step 6: Configure Manager Approval Case
**Action**: Add second case to the switch
**Instructions**:
1. Set condition for manager approval range
2. Add action step to notify manager

**Copy-Paste Example**:
```yaml
condition: "data.expense_validation.expense.amount >= 100 && data.expense_validation.expense.amount <= 1000"
steps:
  - action:
      action_name: mw.send_approval_request
      output_key: manager_approval_request
      input_args:
        approver_id: "data.expense_validation.employee.manager_id"
        expense_id: "data.expense_validation.expense.id"
        expense_amount: "data.expense_validation.expense.amount"
        employee_name: "data.expense_validation.employee.name"
        approval_type: "manager"
```

#### Step 7: Configure Default Case for Director Approval
**Action**: Add default case to the switch
**Instructions**:
1. Set default case for high-value expenses
2. Add action step for director notification

**Copy-Paste Example**:
```yaml
default:
  steps:
    - action:
        action_name: mw.send_approval_request
        output_key: director_approval_request
        input_args:
          approver_id: "data.expense_validation.employee.director_id"
          expense_id: "data.expense_validation.expense.id"
          expense_amount: "data.expense_validation.expense.amount"
          employee_name: "data.expense_validation.employee.name"
          approval_type: "director"
          escalation_reason: "Amount exceeds $1000 threshold"
```

### Complete Working Example

```yaml
action_name: expense_approval_routing
steps:
  - action:
      action_name: mw.validate_expense_submission
      output_key: expense_validation
      input_args:
        employee_id: "data.employee_id"
        expense_amount: "data.expense_amount"
        expense_category: "data.expense_category"
        receipt_attached: "data.receipt_attached"
  - switch:
      cases:
        - condition: "data.expense_validation.expense.amount < 100 && data.expense_validation.validation.is_valid == true"
          steps:
            - action:
                action_name: mw.auto_approve_expense
                output_key: auto_approval_result
                input_args:
                  expense_id: "data.expense_validation.expense.id"
                  approved_amount: "data.expense_validation.expense.amount"
                  approval_reason: "Auto-approved: Amount under $100 threshold"
        - condition: "data.expense_validation.expense.amount >= 100 && data.expense_validation.expense.amount <= 1000"
          steps:
            - action:
                action_name: mw.send_approval_request
                output_key: manager_approval_request
                input_args:
                  approver_id: "data.expense_validation.employee.manager_id"
                  expense_id: "data.expense_validation.expense.id"
                  expense_amount: "data.expense_validation.expense.amount"
                  employee_name: "data.expense_validation.employee.name"
                  approval_type: "manager"
      default:
        steps:
          - action:
              action_name: mw.send_approval_request
              output_key: director_approval_request
              input_args:
                approver_id: "data.expense_validation.employee.director_id"
                expense_id: "data.expense_validation.expense.id"
                expense_amount: "data.expense_validation.expense.amount"
                employee_name: "data.expense_validation.employee.name"
                approval_type: "director"
                escalation_reason: "Amount exceeds $1000 threshold"
      output_key: approval_routing
```

### Troubleshooting Section

#### Common Error: Invalid Condition Syntax
**Problem**: Switch conditions fail to evaluate properly
**Solution**: Use proper DSL syntax with quotes: `"data.field >= 100"`
**Prevention**: Test conditions with simple boolean expressions first

#### Common Error: Missing Default Case
**Problem**: Switch fails when no conditions match
**Solution**: Always include a default case for unmatched scenarios
**Prevention**: Plan for edge cases and unexpected data values

#### Common Error: Nested Data Access
**Problem**: Cannot access deeply nested JSON fields
**Solution**: Use JSON Path Selector to verify correct path syntax
**Prevention**: Test data paths with sample JSON before building conditions

#### Common Error: Boolean Logic Errors
**Problem**: Complex conditions with && and || don't work as expected
**Solution**: Use parentheses for grouping: `"(data.a > 5) && (data.b < 10)"`
**Prevention**: Break complex conditions into simpler, testable parts

### Summary
You've mastered conditional workflow logic! Key learning points:

1. **Switch Expressions**: Powerful branching logic for complex business rules
2. **Conditional Data Mapping**: Dynamic evaluation using DSL expressions
3. **SwitchStep Integration**: Proper YAML structure with cases and defaults
4. **Complex Logic**: Boolean operators and nested data access patterns
5. **Business Logic**: Real-world approval routing with multiple decision points

### Next Steps
Ready for **Module 4: Data Processing**? You'll learn to:
- Create script expressions for data manipulation
- Handle list processing with APIthon validation
- Implement 4096-byte limits and return value validation
- Process arrays and complex data transformations

---

## Module 4: Data Processing - List Handling with Script Steps

### Learning Objectives
- Create `script` expressions for complex data manipulation
- Handle list processing and array transformations
- Implement APIthon validation with 4096-byte limits
- Use return value validation and educational guidance
- Process complex data structures with proper error handling

### Prerequisites
- Completion of Module 3: Conditional Logic
- Basic Python programming knowledge
- Understanding of data structures (lists, dictionaries)

### Real-World Scenario
**Employee Performance Report Generation**: HR needs to process a list of employee performance data, calculate team averages, identify top performers, and generate summary reports. This workflow demonstrates complex data processing with APIthon scripts, including list manipulation, statistical calculations, and formatted output generation.

### Key Concepts

#### Script Expression Structure
Script expressions use APIthon (Python-like) code for data processing:
```yaml
script:
  code: |
    # Process employee performance data
    total_score = sum([emp.performance_score for emp in data.employee_list])
    avg_score = total_score / len(data.employee_list)

    top_performers = [emp for emp in data.employee_list if emp.performance_score > avg_score]

    result = {
        "average_score": avg_score,
        "top_performers": top_performers,
        "total_employees": len(data.employee_list)
    }
    return result
  output_key: performance_analysis
```

#### APIthon Validation Rules
- **4096-byte limit**: Code blocks cannot exceed 4096 bytes
- **No imports**: Cannot use import statements
- **No classes**: Cannot define classes
- **No private methods**: Cannot use underscore-prefixed identifiers
- **Return statements**: Module-level returns are allowed

#### Data Processing Patterns
- **List comprehensions**: `[item.field for item in data.list_name]`
- **Filtering**: `[item for item in data.list if item.score > 80]`
- **Aggregation**: `sum()`, `len()`, `max()`, `min()` functions
- **Dictionary creation**: Building structured output data

### Interactive Guided Steps

#### Step 1: Set Compound Action Name
**Action**: Enter compound action name
**Instructions**:
1. Set name: `employee_performance_analysis`
2. Add description: "Process employee performance data and generate analytics"

**Copy-Paste Example**:
```
employee_performance_analysis
```

#### Step 2: Add Data Retrieval Step
**Action**: Click "Add Step" → "Action Step"
**Instructions**:
1. Set Action Name: `mw.get_employee_performance_data`
2. Set Output Key: `employee_data`
3. Add input arguments for date range and department

**Copy-Paste Example**:
```yaml
action:
  action_name: mw.get_employee_performance_data
  output_key: employee_data
  input_args:
    department: "data.target_department"
    start_date: "data.report_start_date"
    end_date: "data.report_end_date"
    include_metrics: true
```

#### Step 3: Add Sample Employee Data
**Action**: Add sample JSON output for employee data
**Instructions**:
1. In the employee data step, add comprehensive sample JSON
2. Include multiple employees with performance metrics

**Copy-Paste Example**:
```json
{
  "employees": [
    {
      "id": "emp_001",
      "name": "Alice Johnson",
      "department": "Engineering",
      "performance_score": 92,
      "goals_completed": 8,
      "goals_total": 10,
      "peer_rating": 4.5,
      "manager_rating": 4.8,
      "projects": ["Project A", "Project B", "Project C"]
    },
    {
      "id": "emp_002",
      "name": "Bob Smith",
      "department": "Engineering",
      "performance_score": 78,
      "goals_completed": 6,
      "goals_total": 10,
      "peer_rating": 4.0,
      "manager_rating": 3.9,
      "projects": ["Project B", "Project D"]
    },
    {
      "id": "emp_003",
      "name": "Carol Davis",
      "department": "Engineering",
      "performance_score": 95,
      "goals_completed": 10,
      "goals_total": 10,
      "peer_rating": 4.9,
      "manager_rating": 4.7,
      "projects": ["Project A", "Project C", "Project E"]
    }
  ],
  "metadata": {
    "total_count": 3,
    "department": "Engineering",
    "report_period": "Q4 2024"
  }
}
```

#### Step 4: Add Performance Analysis Script
**Action**: Click "Add Step" → "Script Step"
**Instructions**:
1. Set Output Key: `performance_analysis`
2. Add comprehensive data processing script
3. Ensure script stays under 4096-byte limit

**Copy-Paste Example**:
```python
# Performance Analysis Script
employees = data.employee_data.employees

# Calculate basic statistics
total_employees = len(employees)
total_score = sum([emp.performance_score for emp in employees])
avg_score = total_score / total_employees if total_employees > 0 else 0

# Find top performers (above average)
top_performers = [
    {
        "name": emp.name,
        "score": emp.performance_score,
        "goals_completion": (emp.goals_completed / emp.goals_total) * 100
    }
    for emp in employees
    if emp.performance_score > avg_score
]

# Calculate goal completion rates
goal_completion_rates = [
    (emp.goals_completed / emp.goals_total) * 100
    for emp in employees
]
avg_goal_completion = sum(goal_completion_rates) / len(goal_completion_rates)

# Identify improvement opportunities
needs_improvement = [
    {
        "name": emp.name,
        "score": emp.performance_score,
        "gap": avg_score - emp.performance_score
    }
    for emp in employees
    if emp.performance_score < avg_score
]

# Generate summary report
result = {
    "summary": {
        "total_employees": total_employees,
        "average_score": round(avg_score, 2),
        "average_goal_completion": round(avg_goal_completion, 2),
        "top_performer_count": len(top_performers)
    },
    "top_performers": top_performers,
    "improvement_opportunities": needs_improvement,
    "department": data.employee_data.metadata.department,
    "report_period": data.employee_data.metadata.report_period
}

return result
```

#### Step 5: Validate Script Compliance
**Action**: Check APIthon validation panel
**Instructions**:
1. Verify script is under 4096 bytes
2. Check for prohibited patterns (imports, classes, private methods)
3. Confirm return statement is properly formatted

**Expected Outcome**: Green validation with "APIthon script is compliant" message.

#### Step 6: Add Report Generation Step
**Action**: Click "Add Step" → "Script Step"
**Instructions**:
1. Set Output Key: `formatted_report`
2. Create formatted report from analysis data

**Copy-Paste Example**:
```python
# Report Formatting Script
analysis = data.performance_analysis

# Create formatted report sections
header = f"Performance Report - {analysis.department} - {analysis.report_period}"

summary_section = f"""
SUMMARY STATISTICS:
- Total Employees: {analysis.summary.total_employees}
- Average Performance Score: {analysis.summary.average_score}
- Average Goal Completion: {analysis.summary.average_goal_completion}%
- Top Performers: {analysis.summary.top_performer_count}
"""

top_performers_section = "TOP PERFORMERS:\n"
for performer in analysis.top_performers:
    top_performers_section += f"- {performer.name}: {performer.score} (Goals: {performer.goals_completion:.1f}%)\n"

improvement_section = "IMPROVEMENT OPPORTUNITIES:\n"
for emp in analysis.improvement_opportunities:
    improvement_section += f"- {emp.name}: {emp.score} (Gap: {emp.gap:.1f} points)\n"

# Combine all sections
full_report = f"{header}\n{summary_section}\n{top_performers_section}\n{improvement_section}"

result = {
    "formatted_report": full_report,
    "report_sections": {
        "header": header,
        "summary": summary_section,
        "top_performers": top_performers_section,
        "improvement": improvement_section
    },
    "generated_at": "2024-01-15T10:30:00Z"
}

return result
```

### Complete Working Example

```yaml
action_name: employee_performance_analysis
steps:
  - action:
      action_name: mw.get_employee_performance_data
      output_key: employee_data
      input_args:
        department: "data.target_department"
        start_date: "data.report_start_date"
        end_date: "data.report_end_date"
        include_metrics: true
  - script:
      code: |
        # Performance Analysis Script
        employees = data.employee_data.employees

        # Calculate basic statistics
        total_employees = len(employees)
        total_score = sum([emp.performance_score for emp in employees])
        avg_score = total_score / total_employees if total_employees > 0 else 0

        # Find top performers (above average)
        top_performers = [
            {
                "name": emp.name,
                "score": emp.performance_score,
                "goals_completion": (emp.goals_completed / emp.goals_total) * 100
            }
            for emp in employees
            if emp.performance_score > avg_score
        ]

        # Calculate goal completion rates
        goal_completion_rates = [
            (emp.goals_completed / emp.goals_total) * 100
            for emp in employees
        ]
        avg_goal_completion = sum(goal_completion_rates) / len(goal_completion_rates)

        # Generate summary report
        result = {
            "summary": {
                "total_employees": total_employees,
                "average_score": round(avg_score, 2),
                "average_goal_completion": round(avg_goal_completion, 2),
                "top_performer_count": len(top_performers)
            },
            "top_performers": top_performers,
            "department": data.employee_data.metadata.department,
            "report_period": data.employee_data.metadata.report_period
        }

        return result
      output_key: performance_analysis
  - script:
      code: |
        # Report Formatting Script
        analysis = data.performance_analysis

        # Create formatted report sections
        header = f"Performance Report - {analysis.department} - {analysis.report_period}"

        summary_section = f"""
        SUMMARY STATISTICS:
        - Total Employees: {analysis.summary.total_employees}
        - Average Performance Score: {analysis.summary.average_score}
        - Average Goal Completion: {analysis.summary.average_goal_completion}%
        - Top Performers: {analysis.summary.top_performer_count}
        """

        top_performers_section = "TOP PERFORMERS:\n"
        for performer in analysis.top_performers:
            top_performers_section += f"- {performer.name}: {performer.score}\n"

        # Combine all sections
        full_report = f"{header}\n{summary_section}\n{top_performers_section}"

        result = {
            "formatted_report": full_report,
            "generated_at": "2024-01-15T10:30:00Z"
        }

        return result
      output_key: formatted_report
```

### Troubleshooting Section

#### Common Error: Script Exceeds 4096 Bytes
**Problem**: APIthon validation fails with "Script too large" error
**Solution**: Break complex scripts into multiple smaller script steps
**Prevention**: Use concise variable names and remove unnecessary comments

#### Common Error: Private Method Usage
**Problem**: Script uses underscore-prefixed identifiers
**Solution**: Remove or rename variables starting with underscores
**Prevention**: Use descriptive names without leading underscores

#### Common Error: Import Statement Detected
**Problem**: Script tries to import external libraries
**Solution**: Use only built-in Python functions and data structures
**Prevention**: Stick to basic Python operations: lists, dicts, strings, math

#### Common Error: Return Value Issues
**Problem**: Script doesn't return proper data structure
**Solution**: Always end scripts with `return result` where result is a dictionary
**Prevention**: Test return values with simple data structures first

### Summary
You've mastered data processing with APIthon scripts! Key learning points:

1. **Script Expressions**: Powerful data manipulation using Python-like syntax
2. **APIthon Validation**: 4096-byte limits and prohibited pattern detection
3. **List Processing**: Comprehensions, filtering, and aggregation operations
4. **Data Structures**: Building complex output with dictionaries and lists
5. **Return Values**: Proper script output formatting and validation

### Next Steps
Ready for **Module 5: Error Handling**? You'll learn to:
- Create try-catch expressions for robust error handling
- Handle API failures and network timeouts gracefully
- Implement TryCatchStep class with comprehensive error recovery
- Use status code handling and fallback mechanisms

---

## Module 5: Error Handling - Robust API Calls with Try-Catch

### Learning Objectives
- Create `try_catch` expressions for comprehensive error handling
- Handle API failures, network timeouts, and data validation errors
- Implement TryCatchStep class with proper error recovery patterns
- Use status code handling and fallback mechanisms
- Build resilient workflows that gracefully handle failures

### Prerequisites
- Completion of Module 4: Data Processing
- Understanding of HTTP status codes and API error patterns
- Familiarity with error handling concepts

### Real-World Scenario
**Multi-System Data Synchronization**: A workflow needs to synchronize employee data across multiple systems (HR, Payroll, Directory). If any system is unavailable or returns errors, the workflow should attempt alternative approaches, log failures appropriately, and ensure data consistency. This demonstrates enterprise-grade error handling with multiple fallback strategies.

### Key Concepts

#### Try-Catch Expression Structure
Try-catch expressions wrap potentially failing operations with error recovery:
```yaml
try_catch:
  try_steps:
    - action:
        action_name: mw.sync_hr_system
        output_key: hr_sync_result
  catch_block:
    steps:
      - action:
          action_name: mw.log_sync_failure
          output_key: failure_log
  on_status_code: ["400", "401", "403", "404", "500", "502", "503", "504"]
  output_key: sync_operation_result
```

#### Error Recovery Patterns
- **Graceful Degradation**: Continue with reduced functionality
- **Retry Logic**: Attempt operation multiple times with delays
- **Fallback Systems**: Switch to alternative data sources
- **Error Logging**: Comprehensive failure tracking and reporting

#### TryCatchStep Class Integration
The YAML Assistant uses TryCatchStep class to manage error handling with proper validation and YAML generation.

### Interactive Guided Steps

#### Step 1: Set Compound Action Name
**Action**: Enter compound action name
**Instructions**:
1. Set name: `resilient_employee_data_sync`
2. Add description: "Synchronize employee data across systems with comprehensive error handling"

**Copy-Paste Example**:
```
resilient_employee_data_sync
```

#### Step 2: Add Primary Data Sync with Try-Catch
**Action**: Click "Add Step" → "Try-Catch Step"
**Instructions**:
1. Set description: "Attempt primary HR system synchronization"
2. Set output key: `primary_sync_result`
3. Configure try steps for main operation

**Copy-Paste Example**:
```yaml
try_catch:
  try_steps:
    - action:
        action_name: mw.sync_hr_system
        output_key: hr_sync_attempt
        input_args:
          employee_id: "data.employee_id"
          sync_mode: "full"
          timeout_seconds: 30
  output_key: primary_sync_result
```

#### Step 3: Configure Error Recovery in Catch Block
**Action**: In the try-catch step, configure the catch block
**Instructions**:
1. Add error logging action
2. Add fallback data retrieval
3. Set appropriate status codes for triggering catch

**Copy-Paste Example**:
```yaml
catch_block:
  steps:
    - action:
        action_name: mw.log_error
        output_key: error_log
        input_args:
          error_type: "hr_sync_failure"
          employee_id: "data.employee_id"
          timestamp: "meta_info.current_timestamp"
          error_details: "Primary HR system unavailable"
    - action:
        action_name: mw.get_cached_employee_data
        output_key: fallback_data
        input_args:
          employee_id: "data.employee_id"
          cache_max_age: 24
on_status_code: ["400", "401", "403", "404", "500", "502", "503", "504"]
```

#### Step 4: Add Secondary System Sync with Retry Logic
**Action**: Click "Add Step" → "Try-Catch Step"
**Instructions**:
1. Set description: "Attempt payroll system sync with retry"
2. Add multiple retry attempts in try block
3. Configure comprehensive error handling

**Copy-Paste Example**:
```yaml
try_catch:
  try_steps:
    - action:
        action_name: mw.sync_payroll_system
        output_key: payroll_sync_attempt_1
        input_args:
          employee_id: "data.employee_id"
          hr_data: "data.primary_sync_result.hr_sync_attempt || data.primary_sync_result.fallback_data"
          retry_count: 1
        delay_config:
          delay_seconds: 2
    - script:
        code: |
          # Check if first attempt succeeded
          if hasattr(data.payroll_sync_attempt_1, 'success') and data.payroll_sync_attempt_1.success:
              result = {"sync_successful": True, "attempt": 1}
          else:
              result = {"sync_successful": False, "retry_needed": True}
          return result
        output_key: payroll_check_1
  catch_block:
    steps:
      - action:
          action_name: mw.sync_payroll_system
          output_key: payroll_sync_attempt_2
          input_args:
            employee_id: "data.employee_id"
            hr_data: "data.primary_sync_result.hr_sync_attempt || data.primary_sync_result.fallback_data"
            retry_count: 2
          delay_config:
            delay_seconds: 5
      - action:
          action_name: mw.log_error
          output_key: payroll_error_log
          input_args:
            error_type: "payroll_sync_retry"
            employee_id: "data.employee_id"
            retry_attempt: 2
  on_status_code: ["408", "429", "500", "502", "503", "504"]
  output_key: payroll_sync_result
```

#### Step 5: Add Final Validation and Reporting
**Action**: Click "Add Step" → "Script Step"
**Instructions**:
1. Set output key: `sync_validation_report`
2. Create comprehensive validation of all sync operations
3. Generate detailed status report

**Copy-Paste Example**:
```python
# Sync Validation and Reporting Script
hr_result = data.primary_sync_result
payroll_result = data.payroll_sync_result

# Determine overall sync status
hr_success = hasattr(hr_result, 'hr_sync_attempt') and hr_result.hr_sync_attempt
payroll_success = hasattr(payroll_result, 'payroll_sync_attempt_1') or hasattr(payroll_result, 'payroll_sync_attempt_2')

# Count successful operations
successful_syncs = []
failed_syncs = []

if hr_success:
    successful_syncs.append("HR System")
else:
    failed_syncs.append("HR System")

if payroll_success:
    successful_syncs.append("Payroll System")
else:
    failed_syncs.append("Payroll System")

# Generate comprehensive report
overall_status = "SUCCESS" if len(failed_syncs) == 0 else "PARTIAL" if len(successful_syncs) > 0 else "FAILED"

result = {
    "sync_summary": {
        "overall_status": overall_status,
        "successful_systems": successful_syncs,
        "failed_systems": failed_syncs,
        "total_systems": len(successful_syncs) + len(failed_syncs)
    },
    "detailed_results": {
        "hr_sync": {
            "status": "success" if hr_success else "failed",
            "used_fallback": hasattr(hr_result, 'fallback_data'),
            "data_source": "primary" if hr_success else "cache"
        },
        "payroll_sync": {
            "status": "success" if payroll_success else "failed",
            "retry_attempts": 2 if hasattr(payroll_result, 'payroll_sync_attempt_2') else 1,
            "final_attempt": "attempt_2" if hasattr(payroll_result, 'payroll_sync_attempt_2') else "attempt_1"
        }
    },
    "recommendations": {
        "requires_manual_review": len(failed_syncs) > 0,
        "retry_later": len(failed_syncs) == len(successful_syncs) + len(failed_syncs),
        "data_consistency_check": overall_status == "PARTIAL"
    },
    "employee_id": data.employee_id,
    "sync_timestamp": "2024-01-15T10:30:00Z"
}

return result
```

### Complete Working Example

```yaml
action_name: resilient_employee_data_sync
steps:
  - try_catch:
      try_steps:
        - action:
            action_name: mw.sync_hr_system
            output_key: hr_sync_attempt
            input_args:
              employee_id: "data.employee_id"
              sync_mode: "full"
              timeout_seconds: 30
      catch_block:
        steps:
          - action:
              action_name: mw.log_error
              output_key: error_log
              input_args:
                error_type: "hr_sync_failure"
                employee_id: "data.employee_id"
                timestamp: "meta_info.current_timestamp"
                error_details: "Primary HR system unavailable"
          - action:
              action_name: mw.get_cached_employee_data
              output_key: fallback_data
              input_args:
                employee_id: "data.employee_id"
                cache_max_age: 24
      on_status_code: ["400", "401", "403", "404", "500", "502", "503", "504"]
      output_key: primary_sync_result
  - try_catch:
      try_steps:
        - action:
            action_name: mw.sync_payroll_system
            output_key: payroll_sync_attempt_1
            input_args:
              employee_id: "data.employee_id"
              hr_data: "data.primary_sync_result.hr_sync_attempt || data.primary_sync_result.fallback_data"
              retry_count: 1
            delay_config:
              delay_seconds: 2
      catch_block:
        steps:
          - action:
              action_name: mw.sync_payroll_system
              output_key: payroll_sync_attempt_2
              input_args:
                employee_id: "data.employee_id"
                hr_data: "data.primary_sync_result.hr_sync_attempt || data.primary_sync_result.fallback_data"
                retry_count: 2
              delay_config:
                delay_seconds: 5
          - action:
              action_name: mw.log_error
              output_key: payroll_error_log
              input_args:
                error_type: "payroll_sync_retry"
                employee_id: "data.employee_id"
                retry_attempt: 2
      on_status_code: ["408", "429", "500", "502", "503", "504"]
      output_key: payroll_sync_result
  - script:
      code: |
        # Sync Validation and Reporting Script
        hr_result = data.primary_sync_result
        payroll_result = data.payroll_sync_result

        # Determine overall sync status
        hr_success = hasattr(hr_result, 'hr_sync_attempt') and hr_result.hr_sync_attempt
        payroll_success = hasattr(payroll_result, 'payroll_sync_attempt_1') or hasattr(payroll_result, 'payroll_sync_attempt_2')

        # Count successful operations
        successful_syncs = []
        failed_syncs = []

        if hr_success:
            successful_syncs.append("HR System")
        else:
            failed_syncs.append("HR System")

        if payroll_success:
            successful_syncs.append("Payroll System")
        else:
            failed_syncs.append("Payroll System")

        # Generate comprehensive report
        overall_status = "SUCCESS" if len(failed_syncs) == 0 else "PARTIAL" if len(successful_syncs) > 0 else "FAILED"

        result = {
            "sync_summary": {
                "overall_status": overall_status,
                "successful_systems": successful_syncs,
                "failed_systems": failed_syncs,
                "total_systems": len(successful_syncs) + len(failed_syncs)
            },
            "detailed_results": {
                "hr_sync": {
                    "status": "success" if hr_success else "failed",
                    "used_fallback": hasattr(hr_result, 'fallback_data'),
                    "data_source": "primary" if hr_success else "cache"
                },
                "payroll_sync": {
                    "status": "success" if payroll_success else "failed",
                    "retry_attempts": 2 if hasattr(payroll_result, 'payroll_sync_attempt_2') else 1,
                    "final_attempt": "attempt_2" if hasattr(payroll_result, 'payroll_sync_attempt_2') else "attempt_1"
                }
            },
            "recommendations": {
                "requires_manual_review": len(failed_syncs) > 0,
                "retry_later": len(failed_syncs) == len(successful_syncs) + len(failed_syncs),
                "data_consistency_check": overall_status == "PARTIAL"
            },
            "employee_id": data.employee_id,
            "sync_timestamp": "2024-01-15T10:30:00Z"
        }

        return result
      output_key: sync_validation_report
```

### Troubleshooting Section

#### Common Error: Incorrect Status Code Configuration
**Problem**: Catch block doesn't trigger for expected errors
**Solution**: Review HTTP status codes and ensure all relevant codes are included
**Prevention**: Use comprehensive status code lists: ["400", "401", "403", "404", "408", "429", "500", "502", "503", "504"]

#### Common Error: Missing Fallback Logic
**Problem**: Workflow fails completely when primary systems are down
**Solution**: Always include fallback actions in catch blocks
**Prevention**: Plan alternative data sources and degraded functionality paths

#### Common Error: Infinite Retry Loops
**Problem**: Retry logic continues indefinitely
**Solution**: Implement maximum retry counts and exponential backoff delays
**Prevention**: Set clear retry limits and escalation paths

#### Common Error: Poor Error Logging
**Problem**: Difficult to diagnose failures in production
**Solution**: Include comprehensive error context: timestamps, user info, error details
**Prevention**: Use structured logging with consistent error categorization

### Summary
You've mastered enterprise-grade error handling! Key learning points:

1. **Try-Catch Expressions**: Comprehensive error recovery with multiple fallback strategies
2. **Status Code Handling**: Precise control over which errors trigger recovery logic
3. **Retry Patterns**: Intelligent retry logic with delays and maximum attempt limits
4. **Graceful Degradation**: Maintaining functionality even when systems fail
5. **Error Reporting**: Detailed logging and status reporting for operational visibility

### Next Steps
Congratulations! You've completed all 5 core modules of the Moveworks YAML Assistant tutorial series. You now have comprehensive knowledge of:

- **Basic Compound Actions**: Structure, data flow, and validation
- **IT Automation**: cURL import, parameterization, and multi-system integration
- **Conditional Logic**: Switch expressions and complex business rules
- **Data Processing**: APIthon scripts and list manipulation
- **Error Handling**: Robust workflows with comprehensive recovery patterns

## Advanced Learning Recommendations

### Continue Your Journey
1. **Explore Advanced Expression Types**: Experiment with `for`, `parallel`, `return`, and `raise` expressions
2. **Build Complex Workflows**: Combine multiple expression types in sophisticated automation scenarios
3. **Master the Template Library**: Create and share reusable workflow patterns
4. **Optimize Performance**: Learn about workflow optimization and best practices

### Community and Resources
- **Moveworks Documentation**: Reference the official Moveworks platform documentation
- **DSL Playground**: Test complex DSL expressions in the Moveworks DSL & Data Mapper Playground
- **Best Practices**: Follow enterprise workflow design patterns and security guidelines
- **Community Forums**: Share workflows and learn from other developers

### Integration with YAML Assistant Features
You've learned to effectively use:
- **JSON Path Selector**: Visual data selection and path generation
- **Template Library**: Pre-built patterns and reusable components
- **Validation System**: Real-time compliance checking and error prevention
- **Compliance Validator**: Ensuring Moveworks platform compatibility
- **Tutorial System**: Interactive learning with hands-on practice

## Final Project Suggestion

**Challenge**: Create a comprehensive employee lifecycle management workflow that combines all learned concepts:

1. **Employee Onboarding** (Module 1): User lookup and manager notification
2. **System Provisioning** (Module 2): Multi-system account creation with cURL integration
3. **Access Level Assignment** (Module 3): Role-based access using switch logic
4. **Batch Processing** (Module 4): Process multiple new hires with script steps
5. **Error Recovery** (Module 5): Handle system failures gracefully with try-catch

This project will demonstrate mastery of all tutorial concepts while creating a practical, enterprise-ready workflow.

---

## Tutorial Integration Guide for Developers

### Implementing Tutorial Content in PySide6 System

This tutorial content is designed to integrate seamlessly with the existing PySide6 overlay tutorial system. Here's how to implement each module:

#### Tutorial Data Structure
```python
tutorial_modules = {
    "module_1": {
        "id": "basic_compound_action",
        "title": "Your First Compound Action",
        "description": "Basic lookup and notification workflow",
        "difficulty": "Beginner",
        "estimated_time": "15 minutes",
        "steps": [
            # Convert each guided step to TutorialStep objects
        ]
    },
    # ... additional modules
}
```

#### Integration Points
- **JSON Path Selector**: Tutorials reference specific UI elements for hands-on interaction
- **Template Library**: Steps include template selection and customization
- **Validation System**: Real-time feedback during tutorial progression
- **YAML Preview**: Continuous YAML generation demonstration

#### Copy-Paste Integration
Each tutorial includes copy-paste examples that can be:
- Automatically inserted into form fields during tutorial steps
- Provided in copyable text blocks within tutorial overlays
- Used as validation examples for user input

#### Progressive Disclosure
Tutorials build upon each other with clear prerequisites and learning objectives, ensuring users develop comprehensive understanding through hands-on practice.

This comprehensive tutorial system provides developers with the knowledge and practical experience needed to effectively use the Moveworks YAML Assistant for creating enterprise-grade compound action workflows.
