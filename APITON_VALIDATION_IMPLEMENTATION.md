# APIthon Validation Implementation Summary

## Overview

This document summarizes the comprehensive APIthon validation and generation system implemented for the Moveworks YAML Assistant. The system enforces strict compliance with APIthon (Moveworks' Python-like scripting language) restrictions and ensures proper YAML formatting for script blocks.

## ✅ Implemented Features

### 1. Comprehensive APIthon Code Restrictions

**File**: `apiton_validator.py`

The system actively prevents and validates against the following prohibited APIthon code patterns:

#### ❌ Prohibited Patterns (Enforced "No" List):
1. **Import statements** - `import`, `from...import`, `__import__()`
2. **Class definitions** - `class` keyword
3. **Private methods/properties** - identifiers starting with underscore (`_variable`, `_function()`)
4. **External library references** - non-APIthon built-ins
5. **Function definitions** - `def` keyword at module level
6. **Dangerous built-ins** - `eval()`, `exec()`, `compile()`, `globals()`, `locals()`, etc.
7. **File operations** - `open()`, file I/O
8. **System operations** - `os.*`, `sys.*`, `subprocess.*`

#### ✅ Allowed APIthon Features:
- Basic Python built-ins: `abs`, `all`, `any`, `bool`, `dict`, `enumerate`, `filter`, `float`, `int`, `len`, `list`, `map`, `max`, `min`, `range`, `reversed`, `round`, `set`, `sorted`, `str`, `sum`, `tuple`, `type`, `zip`
- String methods: `format`, `join`, `split`, `strip`, `replace`, `upper`, `lower`
- Data access patterns: `data.*`, `meta_info.*`
- Return statements at module level (APIthon-specific feature)
- Standard control flow: `if/else`, `for`, `while`
- List comprehensions and basic Python syntax

### 2. Required YAML Structure for Script Action Blocks

Every script step follows this exact structure:

```yaml
- script:
    code: |
      # APIthon code here with proper indentation
      user_name = data.user_info.name
      result = {"greeting": f"Hello, {user_name}!"}
      return result
    output_key: "result_variable_name"
    input_args:  # Optional
      local_var: "{{data.input_field}}"
      another_var: "{{meta_info.user.email}}"
```

#### Mandatory Fields:
- `code` (string): Contains the APIthon script using YAML literal block scalar (`|`) for multiline code
- `output_key` (string): Variable name for storing script results in workflow context

#### Optional Fields:
- `input_args` (dictionary): Maps workflow context variables to local script variables using Moveworks data reference syntax

### 3. YAML Formatting Requirements

**File**: `yaml_generator.py` (Enhanced)

1. **Literal Block Scalar**: Uses pipe character (`|`) for multiline code blocks
2. **Proper Indentation**: Maintains YAML indentation with Python indentation within code blocks
3. **Field Ordering**: `code`, `output_key`, `input_args` (when present)
4. **Data Reference Validation**: Supports `data.field_name`, `meta_info.user.property` patterns

### 4. Validation Rules

#### Structural Validation:
- Ensures all script blocks can execute independently (self-contained)
- Verifies proper data flow from input_args to code execution
- Validates output_key naming conventions (valid identifiers, no underscore prefix)
- Checks for compliance with Moveworks workflow data mapping syntax

#### Syntax Validation:
- Performs Python syntax checking with APIthon-specific allowances
- Allows return statements at module level (APIthon feature)
- Provides accurate line number reporting for syntax errors
- Wraps code in function context for validation while preserving original semantics

#### Data Reference Validation:
- Validates `data.*` and `meta_info.*` reference patterns
- Checks availability of referenced data paths in workflow context
- Ensures input_args values reference valid data context

### 5. Integration with Existing Architecture

**File**: `validator.py` (Updated)

- Integrated with existing PySide6-based UI framework
- Follows established manager class patterns and dialog structures
- Compatible with JSON Path Selector for data reference selection
- Maintains compatibility with template library and validation systems
- Integrated with tutorial and example systems

## 🧪 Testing and Validation

**File**: `test_apiton_validation.py`

Comprehensive test suite covering:

### Valid APIthon Scripts:
- Simple calculations with return statements
- Data processing with meta_info access
- Conditional logic and control flow
- List processing and iteration

### Invalid APIthon Scripts:
- Import statements (should fail)
- Class definitions (should fail)
- Function definitions (should fail)
- Private identifiers (should fail)
- Dangerous built-ins (should fail)
- File operations (should fail)
- Empty code (should fail)
- Invalid output keys (should fail)

### YAML Generation:
- Proper literal block scalar formatting (`|`)
- Correct field ordering and structure
- Multiline code preservation
- Input args mapping

### Integration Testing:
- Compatibility with main validation pipeline
- Error reporting and user feedback
- Workflow-level validation

## 📋 Usage Examples

### Valid APIthon Script Example:

```python
# Process user data with conditional logic
user_name = data.user_info.name
user_status = data.user_info.status

if user_status == "active":
    greeting = f"Welcome back, {user_name}!"
    status_code = 200
else:
    greeting = f"Hello, {user_name}. Please activate your account."
    status_code = 403

result = {
    "greeting": greeting,
    "status_code": status_code,
    "user_email": meta_info.user.email_addr,
    "timestamp": "2024-01-01T00:00:00Z"
}

return result
```

### Generated YAML Output:

```yaml
script:
  code: |
    # Process user data with conditional logic
    user_name = data.user_info.name
    user_status = data.user_info.status
    
    if user_status == "active":
        greeting = f"Welcome back, {user_name}!"
        status_code = 200
    else:
        greeting = f"Hello, {user_name}. Please activate your account."
        status_code = 403
    
    result = {
        "greeting": greeting,
        "status_code": status_code,
        "user_email": meta_info.user.email_addr,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    return result
  output_key: processed_user_data
  input_args:
    user_data: "{{data.user_info}}"
```

## 🔧 API Reference

### Main Validation Functions:

- `comprehensive_validate_apiton_script(step, available_data_paths)` - Complete validation of a single script step
- `validate_workflow_apiton_scripts(workflow, available_data_paths)` - Validate all script steps in a workflow
- `validate_apiton_code_restrictions(code)` - Check code against prohibited patterns
- `validate_apiton_syntax(code)` - Syntax validation with APIthon allowances
- `validate_script_step_structure(step)` - Structural validation of ScriptStep

### YAML Generation:

- `generate_yaml_string(workflow)` - Enhanced YAML generation with literal block scalars
- Automatic multiline code detection and formatting
- Proper field ordering and structure compliance

## 🎯 Benefits

1. **Strict Security**: Prevents execution of dangerous code patterns
2. **Compliance**: Ensures all scripts follow APIthon specifications
3. **User-Friendly**: Clear error messages and validation feedback
4. **Integration**: Seamless integration with existing Moveworks YAML Assistant
5. **Maintainable**: Modular design with comprehensive test coverage
6. **Extensible**: Easy to add new validation rules or modify existing ones

## 🚀 Future Enhancements

Potential areas for future improvement:
- Enhanced data path auto-completion
- Real-time syntax highlighting for APIthon code
- Interactive code examples and tutorials
- Performance optimization for large workflows
- Advanced static analysis for data flow validation
