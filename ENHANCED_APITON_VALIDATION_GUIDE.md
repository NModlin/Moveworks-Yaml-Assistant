# Enhanced APIthon Validation System Guide

## Overview

The Enhanced APIthon Validation System provides comprehensive validation, constraint checking, and educational feedback for APIthon scripts in the Moveworks YAML Assistant. This system goes beyond basic syntax checking to provide intelligent analysis and user guidance.

## Key Features

### 1. Resource Constraint Validation

The system enforces strict resource limits to ensure APIthon scripts run efficiently:

#### Code Size Limits
- **Maximum script size**: 4,096 bytes
- **Visual indicators**: Progress bars show current usage
- **Warnings**: Alerts when approaching 80% of limit
- **Errors**: Prevents scripts exceeding the limit

#### String Length Validation
- **Maximum string length**: 4,096 characters per string literal
- **Real-time checking**: Validates all string literals in the code
- **Educational feedback**: Explains why limits exist

#### Numeric Range Validation
- **Range**: 0 to 4,294,967,295 (unsigned 32-bit integer)
- **Automatic detection**: Scans all numeric literals
- **Clear error messages**: Explains the valid range

### 2. Return Value Logic Analysis

Detects common mistakes in APIthon script return logic:

#### Assignment vs Expression Detection
```python
# ❌ Common mistake - assignment as last line
result = {"data": "value"}

# ✅ Correct - expression or explicit return
result = {"data": "value"}
return result
# OR
{"data": "value"}  # Expression
```

#### In-Place Operation Detection
```python
# ❌ Returns None
my_list.append(item)

# ✅ Returns the modified list
my_list.append(item)
my_list  # or return my_list
```

#### Educational Suggestions
- Explains how APIthon return values work
- Provides specific fix suggestions
- Shows correct patterns

### 3. Reserved output_key Validation

Special handling for Moveworks citation formats:

#### "result" output_key
- **Expected format**: Single citation dictionary
- **Required fields**: `id`, `friendly_id`, `title`, `url`, `snippet`
- **Validation**: Checks for citation field presence
- **Suggestions**: Guides users to proper citation format

#### "results" output_key  
- **Expected format**: List of citation dictionaries
- **Validation**: Ensures list structure
- **Educational feedback**: Explains multiple citation format

#### Alternative Suggestions
- Recommends different output_key names if citation format not intended
- Explains when to use reserved names

### 4. Real-Time Validation UI

#### Visual Indicators
- **Status badges**: ✓ Valid, ⚠️ Warnings, ❌ Errors
- **Progress bars**: Resource usage visualization
- **Color coding**: Green (good), Orange (warning), Red (error)

#### Feedback Panels
- **Categorized messages**: Errors, warnings, suggestions
- **Contextual help**: Explains each validation issue
- **Fix suggestions**: Actionable recommendations

#### Educational Tooltips
- **Hover help**: Explains validation rules
- **Examples**: Shows correct patterns
- **Best practices**: APIthon coding guidelines

## Usage Examples

### Basic Validation
```python
from enhanced_apiton_validator import enhanced_apiton_validator
from core_structures import ScriptStep

# Create a script step
step = ScriptStep(
    code="user_name = data.user_info.name\nreturn {'greeting': f'Hello, {user_name}!'}",
    output_key="greeting_result"
)

# Validate with available data paths
available_paths = {"data.user_info.name", "meta_info.user.email"}
result = enhanced_apiton_validator.comprehensive_validate(step, available_paths)

# Check results
print(f"Valid: {result.is_valid}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
print(f"Suggestions: {result.suggestions}")
```

### Resource Usage Monitoring
```python
# Check resource usage
print(f"Code size: {result.resource_usage['code_bytes']} bytes")
print(f"Limit: {result.resource_usage['code_bytes_limit']} bytes")

# Get usage percentage
usage_percent = (result.resource_usage['code_bytes'] / 
                result.resource_usage['code_bytes_limit']) * 100
print(f"Usage: {usage_percent:.1f}%")
```

### Return Analysis
```python
# Analyze return value logic
return_info = result.return_analysis
print(f"Last statement type: {return_info['last_statement_type']}")
print(f"Has explicit return: {return_info['has_explicit_return']}")

# Check for common mistakes
if return_info['last_statement_type'] == 'Assign':
    print("Warning: Last line is an assignment, not a return value")
```

### Citation Compliance
```python
# Check citation format compliance
citation_info = result.citation_compliance
if citation_info['is_reserved']:
    print(f"Output key '{citation_info['output_key']}' is reserved for citations")
    print(f"Compliance status: {citation_info['compliance_status']}")
    print(f"Found fields: {citation_info['found_fields']}")
    print(f"Missing fields: {citation_info['missing_fields']}")
```

## Integration with Main GUI

### Enhanced Script Editor
- **Real-time validation**: Updates as you type (with debouncing)
- **Visual feedback**: Immediate status indicators
- **Contextual help**: Built-in help system
- **Fix suggestions**: Actionable recommendations

### Validation Panels
- **APIthon tab**: Dedicated validation display
- **Resource monitoring**: Live usage tracking
- **Return analysis**: Logic validation feedback
- **Citation compliance**: Format checking

### Educational Features
- **Interactive help**: Explains APIthon rules
- **Examples**: Shows correct patterns
- **Best practices**: Coding guidelines
- **Fix suggestions**: Automated recommendations

## Testing

### Run Validation Tests
```bash
python test_enhanced_apiton_validation.py
```

### Demo Script Editor
```bash
python demo_enhanced_script_editor.py
```

### Test Scenarios
1. **Resource constraints**: Large scripts, long strings, big numbers
2. **Return logic**: Assignment issues, in-place operations
3. **Citation format**: Reserved output_key validation
4. **Comprehensive**: Multiple validation issues
5. **Valid scripts**: Proper APIthon code

## Best Practices

### Writing Efficient APIthon Scripts
1. **Keep scripts concise**: Stay well under 4,096 byte limit
2. **Use explicit returns**: Make return values clear
3. **Avoid long strings**: Break up large text into smaller pieces
4. **Use appropriate data types**: Stay within numeric ranges

### Citation Format Guidelines
1. **Use "result" for single items**: Include all required citation fields
2. **Use "results" for lists**: Array of citation objects
3. **Choose descriptive names**: For non-citation output_keys
4. **Include all fields**: id, friendly_id, title, url, snippet

### Error Resolution
1. **Read error messages carefully**: They provide specific guidance
2. **Check suggestions**: Often include fix recommendations
3. **Use the help system**: Explains APIthon rules and patterns
4. **Test incrementally**: Validate as you write code

## API Reference

### Enhanced Validator
- `enhanced_apiton_validator.comprehensive_validate(step, available_paths)`
- Returns `APIthonValidationResult` with detailed feedback

### Validation Result
- `is_valid`: Boolean validation status
- `errors`: List of error messages
- `warnings`: List of warning messages  
- `suggestions`: List of improvement suggestions
- `resource_usage`: Resource constraint information
- `return_analysis`: Return value logic analysis
- `citation_compliance`: Citation format validation

### UI Components
- `EnhancedScriptEditor`: Real-time validation editor
- `APIthonValidationWidget`: Detailed validation display
- `ValidationIndicator`: Visual status indicator
- `FeedbackPanel`: Categorized feedback display

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all dependencies are installed
2. **UI not updating**: Check signal connections
3. **Validation not running**: Verify script step is set
4. **Performance issues**: Large scripts may cause delays

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export APITON_DEBUG=1
python your_script.py
```

This comprehensive validation system ensures APIthon scripts are not only syntactically correct but also follow best practices and resource constraints for optimal performance in the Moveworks platform.
