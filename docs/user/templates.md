# Template Library Guide

Master the Template Library to accelerate workflow development with ready-made, production-tested templates.

## 🎯 Template Library Overview

The Template Library provides a comprehensive collection of pre-built workflow templates covering common use cases, best practices, and advanced patterns. Each template is production-ready and follows Moveworks compliance standards.

### Key Benefits
- **Rapid Development**: Start with proven templates instead of building from scratch
- **Best Practices**: Templates follow established patterns and conventions
- **Learning Tool**: Study real-world implementations and techniques
- **Customizable**: Easily modify templates for your specific needs
- **Quality Assured**: All templates are tested and validated

## 📚 Template Categories

### 1. User Management
**Purpose**: User lifecycle operations, access management, and profile updates

**Available Templates**:
- **User Onboarding Workflow**: Complete new user setup process
- **User Offboarding Process**: Secure user deactivation and cleanup
- **Access Request Approval**: Multi-step approval workflow
- **Profile Update Notification**: User profile change notifications
- **Password Reset Automation**: Secure password reset process

**Example - User Onboarding**:
```yaml
action_name: user_onboarding_workflow
steps:
- action:
    action_name: mw.get_user_by_email
    output_key: user_info
    input_args:
      email: data.new_user_email

- switch:
    cases:
    - condition: data.user_info.user.department == 'Engineering'
      steps:
      - action:
          action_name: provision_dev_access
          output_key: dev_access_result
          input_args:
            user_id: data.user_info.user.id
    default:
      steps:
      - action:
          action_name: provision_standard_access
          output_key: standard_access_result
```

### 2. IT Service Management
**Purpose**: Ticket management, incident response, and service requests

**Available Templates**:
- **Incident Creation and Assignment**: Automated incident handling
- **Service Request Processing**: Standard service request workflow
- **Escalation Management**: Multi-tier escalation process
- **Status Update Notifications**: Automated status communications
- **Resolution Tracking**: Incident resolution and closure

### 3. Control Flow Patterns
**Purpose**: Advanced workflow logic and data processing

**Available Templates**:
- **Multi-Condition Routing**: Complex decision trees
- **Batch Processing Workflow**: Process multiple items efficiently
- **Parallel API Calls**: Concurrent external service integration
- **Data Transformation Pipeline**: Multi-step data processing
- **Conditional Notifications**: Smart notification routing

### 4. Error Handling & Recovery
**Purpose**: Robust error handling and fallback mechanisms

**Available Templates**:
- **API Failure Recovery**: Graceful API error handling
- **Retry Logic Implementation**: Intelligent retry strategies
- **Fallback Data Sources**: Alternative data retrieval
- **Error Notification System**: Comprehensive error reporting
- **Circuit Breaker Pattern**: Prevent cascade failures

## 🔧 Using Templates

### Accessing the Template Library

1. **Open Template Browser**: Click `📚 Templates` in the right panel
2. **Browse Categories**: Navigate through organized template categories
3. **Preview Templates**: View template details and YAML structure
4. **Apply Template**: Click any template to apply it to your workflow

### Template Application Process

**Step 1: Select Template**
- Browse available templates by category
- Read template descriptions and use cases
- Preview the YAML structure and components

**Step 2: Apply Template**
- Click "Apply Template" to load it into your workflow
- The template replaces your current workflow (save first if needed)
- All steps and configuration are automatically loaded

**Step 3: Customize Template**
- Modify action names, output keys, and input arguments
- Update data references to match your data sources
- Add or remove steps as needed for your use case

**Step 4: Validate and Test**
- Use real-time validation to check compliance
- Test with sample data to verify functionality
- Generate YAML and review the output

### Template Customization

**Common Customizations**:
- **Action Names**: Replace with your specific actions
- **Data References**: Update paths to match your data structure
- **Input Arguments**: Modify parameters for your requirements
- **Output Keys**: Change variable names for clarity
- **Conditions**: Adjust logic for your business rules

**Example Customization**:
```yaml
# Original template
input_args:
  user_email: data.user_email

# Customized for your data
input_args:
  user_email: data.employee_info.email_address
```

## 📝 Creating Custom Templates

### Template Structure

Templates are JSON files with metadata and workflow definition:

```json
{
  "name": "Custom User Workflow",
  "description": "Handles user-specific operations",
  "category": "User Management",
  "author": "Your Name",
  "version": "1.0",
  "tags": ["user", "automation", "workflow"],
  "workflow": {
    "action_name": "custom_user_workflow",
    "steps": [
      // Your workflow steps here
    ]
  }
}
```

### Template Best Practices

**Naming Conventions**:
- Use descriptive, clear template names
- Include the primary use case in the name
- Follow consistent naming patterns

**Documentation**:
- Provide clear descriptions of template purpose
- Include usage instructions and customization notes
- Document required input data and expected outputs

**Flexibility**:
- Design templates to be easily customizable
- Use generic variable names that can be easily replaced
- Include optional steps that can be removed if not needed

**Testing**:
- Test templates with realistic data
- Validate compliance and functionality
- Include sample input data in template documentation

## 🔄 Template Management

### Importing Templates

**From File**:
1. Click "Import Template" in the Template Library
2. Select your template JSON file
3. Review and confirm the import
4. Template appears in the appropriate category

**From URL**:
1. Use "Import from URL" option
2. Provide the template file URL
3. System downloads and validates the template
4. Confirm import to add to library

### Exporting Templates

**Export Current Workflow**:
1. Build your workflow in the application
2. Click "Export as Template" in the Template Library
3. Add metadata (name, description, category)
4. Save as JSON file for sharing

**Export Existing Template**:
1. Select template in the library
2. Click "Export Template"
3. Save to file for backup or sharing

### Sharing Templates

**Team Sharing**:
- Export templates as JSON files
- Share via version control systems
- Maintain template repositories for team access
- Document template usage and customization guidelines

**Community Sharing**:
- Contribute templates to community repositories
- Follow community guidelines and standards
- Include comprehensive documentation and examples

## 💡 Template Tips & Tricks

### Productivity Tips

1. **Start with Templates**: Always check for existing templates before building from scratch
2. **Customize Gradually**: Apply template first, then make incremental changes
3. **Save Variations**: Create multiple versions for different scenarios
4. **Document Changes**: Keep notes on customizations for future reference

### Advanced Techniques

**Template Composition**:
- Combine multiple templates for complex workflows
- Extract common patterns into reusable components
- Build template hierarchies for different complexity levels

**Dynamic Templates**:
- Use variables for commonly changed values
- Create templates with optional sections
- Design templates that adapt to different data structures

**Template Testing**:
- Create test data sets for template validation
- Build automated tests for critical templates
- Maintain template quality through regular review

## 🚀 Template Examples

### Simple API Integration
```yaml
action_name: simple_api_integration
steps:
- action:
    action_name: external_api_call
    output_key: api_response
    input_args:
      endpoint: data.api_endpoint
      parameters: data.request_params

- script:
    code: |
      # Process API response
      processed_data = {
        "status": api_response.status,
        "data": api_response.data,
        "timestamp": api_response.timestamp
      }
      return processed_data
    input_args:
      api_response: data.api_response
    output_key: processed_result
```

### Error Handling Pattern
```yaml
action_name: robust_api_call
steps:
- try_catch:
    output_key: api_call_result
    try:
      steps:
      - action:
          action_name: external_service_call
          output_key: service_response
          input_args:
            data: data.input_data
    catch:
      steps:
      - script:
          code: |
            return {
              "error": "Service unavailable",
              "fallback_data": "default_response",
              "retry_suggested": True
            }
          output_key: fallback_response
```

---

*For hands-on template practice, try the [Interactive Tutorials](tutorials.md)*
