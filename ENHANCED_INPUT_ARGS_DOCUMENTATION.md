# Enhanced Input Arguments System Documentation

## Overview

The Enhanced Input Arguments System for the Moveworks YAML Assistant provides intelligent auto-completion, validation, and suggestion features for input arguments in both Action and Script steps. This system significantly improves the user experience by reducing manual typing and preventing common errors.

## Key Features

### 1. **Auto-Suggestion from Action Catalog**
- Automatically suggests required and optional parameters based on the selected Moveworks action
- Integrates with the MW_ACTIONS_CATALOG to provide accurate parameter specifications
- Shows parameter types, descriptions, and whether they are required

### 2. **JSON-Based Argument Detection**
- Allows users to paste JSON examples to automatically detect potential input arguments
- Converts camelCase JSON keys to snake_case argument names
- Provides intelligent suggestions based on JSON structure analysis

### 3. **Data Path Auto-Completion**
- Suggests data paths from previous workflow steps (data.step_output.field)
- Includes common meta_info paths (meta_info.user.email, etc.)
- Provides contextual suggestions based on step outputs and JSON structures

### 4. **Drag-and-Drop Support**
- Supports dragging data paths from the JSON Path Selector
- Automatically populates argument values when paths are dropped
- Integrates seamlessly with existing workflow tools

### 5. **Real-Time Validation**
- Validates argument names for lowercase_snake_case format
- Validates DSL expressions in argument values
- Provides immediate visual feedback with error indicators
- Debounced validation (300ms delay) for optimal performance

### 6. **Array-Type Input Handling**
- Properly formats and validates array-type input arguments
- Supports complex data structures and nested objects
- Maintains Moveworks DSL compliance for all data types

## Implementation Details

### Core Components

#### `EnhancedInputArgsTable`
- Custom QTableWidget with enhanced functionality
- Supports both action and script step types
- Provides context-aware suggestions and validation

#### `InputArgsSuggestionEngine`
- Analyzes workflow context to generate relevant suggestions
- Integrates with MW_ACTIONS_CATALOG for action-specific parameters
- Extracts data paths from previous step outputs

### Integration Points

#### Main GUI Integration
```python
# Enhanced table replaces standard QTableWidget
self.action_input_args_table = EnhancedInputArgsTable(step_type="action")
self.script_input_args_table = EnhancedInputArgsTable(step_type="script")

# Set workflow context for suggestions
self.action_input_args_table.set_context(workflow, current_step, step_index)
```

#### Backward Compatibility
- Maintains full compatibility with existing YAML parsing and generation
- Fallback methods ensure functionality with regular QTableWidget
- No breaking changes to existing workflow structures

## User Interface Enhancements

### New Buttons
1. **"Auto-Suggest from Action"** - Populates required arguments based on selected action
2. **"Suggest from JSON"** - Opens dialog for JSON-based argument detection
3. **Enhanced "Add Argument"** - Adds rows with intelligent tooltips
4. **"Remove Selected"** - Removes selected rows with validation updates

### Interactive Features
- **Double-click argument names** - Shows action-specific parameter suggestions
- **Double-click values** - Shows data path suggestions from workflow context
- **Drag-and-drop** - Accepts data paths from JSON Path Selector
- **Real-time validation** - Visual indicators for validation status

## Usage Examples

### 1. Auto-Populating Action Arguments
```python
# User selects "mw.get_user_by_email" action
# Clicks "Auto-Suggest from Action" button
# Table automatically populates with:
# - email (required, string) - empty value for user input
```

### 2. JSON-Based Suggestions
```python
# User pastes JSON:
{
  "ticketTitle": "Support Request",
  "assigneeEmail": "support@company.com",
  "priorityLevel": "high"
}

# System suggests:
# - ticket_title (string)
# - assignee_email (string) 
# - priority_level (string)
```

### 3. Data Path Suggestions
```python
# Previous step output: data.user_info.user.email
# System suggests for new arguments:
# - data.user_info.user.email
# - data.user_info.user.name
# - data.user_info.user.department
# - meta_info.user.email
```

## Validation Rules

### Argument Names
- Must use lowercase_snake_case format
- Must start with a letter
- Can contain letters, numbers, and underscores
- Real-time validation with visual feedback

### Argument Values
- DSL expressions (data.*, meta_info.*) are validated
- String literals are accepted without validation
- Complex expressions are parsed and validated
- Invalid references show specific error messages

## Technical Specifications

### Performance
- Debounced validation (300ms) prevents excessive processing
- Efficient suggestion caching for repeated operations
- Minimal memory footprint with lazy loading

### Compatibility
- Maintains strict Moveworks YAML compliance
- Preserves all existing validation rules
- Compatible with all compound action expression types
- Supports both single and multiple expression workflows

### Error Handling
- Graceful fallback to standard table functionality
- Comprehensive error messages with actionable suggestions
- Non-blocking validation that doesn't interrupt user workflow

## Configuration

### Customization Options
- Suggestion engine can be configured for specific action catalogs
- Validation rules can be extended for custom requirements
- UI styling follows existing design constants

### Integration Settings
- Automatic context detection from workflow state
- Configurable suggestion limits and display options
- Extensible architecture for future enhancements

## Future Enhancements

### Planned Features
1. **Smart Templates** - Pre-configured argument sets for common patterns
2. **Argument Dependencies** - Show relationships between arguments
3. **Advanced Validation** - Type checking and value range validation
4. **Export/Import** - Save and load argument configurations
5. **Analytics** - Usage patterns and optimization suggestions

### Extension Points
- Plugin architecture for custom suggestion engines
- API for external tool integration
- Configurable validation rule sets
- Custom UI themes and layouts

## Testing and Verification

### Test Coverage
- Unit tests for all suggestion engine components
- Integration tests with existing workflow validation
- UI tests for interactive features
- Performance tests for large workflows

### Verification Process
- Backward compatibility testing with existing YAML files
- Cross-platform testing (Windows, macOS, Linux)
- Accessibility testing for screen readers
- User acceptance testing with real workflows

## Conclusion

The Enhanced Input Arguments System significantly improves the Moveworks YAML Assistant's usability while maintaining full backward compatibility and strict compliance with Moveworks specifications. The system provides intelligent assistance that reduces errors, speeds up workflow creation, and enhances the overall user experience.
