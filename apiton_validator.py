"""
APIthon Validation Module for Moveworks YAML Assistant.

This module provides comprehensive validation for APIthon (Moveworks' Python-like scripting language)
script blocks, enforcing strict compliance with APIthon restrictions and YAML formatting requirements.

APIthon Code Restrictions (Enforced "No" List):
1. Any import statements (import, from...import, __import__)
2. Class definitions (class keyword)
3. Private methods or properties (identifiers starting with underscore)
4. External library references or non-APIthon built-ins
5. Non-Python syntax or unsupported Python features
6. Function definitions at module level (def keyword outside of inline expressions)

Required YAML Structure:
- script:
    code: |
      # APIthon code with proper indentation
    output_key: "result_variable_name"
    input_args:  # Optional
      local_var: "{{data.input_field}}"
"""

import ast
import re
from typing import List, Dict, Any, Set
from core_structures import ScriptStep, Workflow


# APIthon built-in functions and allowed identifiers
APITON_ALLOWED_BUILTINS = {
    # Basic Python built-ins allowed in APIthon
    'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 'float',
    'int', 'len', 'list', 'map', 'max', 'min', 'range', 'reversed', 'round',
    'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip',

    # String methods and operations
    'format', 'join', 'split', 'strip', 'replace', 'upper', 'lower',

    # APIthon-specific allowed functions
    'print',  # For debugging

    # Data access patterns
    'data', 'meta_info'
}

# Comprehensive prohibited patterns in APIthon code
PROHIBITED_PATTERNS = [
    # Enhanced import statement detection - covers all import variations
    (r'\bimport\s+[\w\.]+(?:\s*,\s*[\w\.]+)*(?:\s+as\s+\w+)?', "Import statements are not allowed in APIthon"),
    (r'\bfrom\s+[\w\.]+\s+import\s+[\w\*]+(?:\s*,\s*[\w\*]+)*(?:\s+as\s+\w+)?', "Import statements are not allowed in APIthon"),
    (r'\bfrom\s+[\w\.]+\s+import\s+\*', "Wildcard imports (from ... import *) are not allowed in APIthon"),
    (r'__import__\s*\(', "Dynamic imports with __import__() are not allowed in APIthon"),

    # Multi-line import detection
    (r'\bimport\s+\(', "Multi-line import statements are not allowed in APIthon"),
    (r'\bfrom\s+[\w\.]+\s+import\s+\(', "Multi-line from...import statements are not allowed in APIthon"),

    # Nested import detection (within functions, conditionals, etc.)
    (r'^\s+import\s+', "Import statements within code blocks are not allowed in APIthon"),
    (r'^\s+from\s+[\w\.]+\s+import\s+', "Import statements within code blocks are not allowed in APIthon"),

    # Class definitions
    (r'\bclass\s+\w+', "Class definitions are not allowed in APIthon"),

    # Function definitions at module level
    (r'^\s*def\s+\w+\s*\(', "Function definitions at module level are not allowed in APIthon"),

    # Private identifiers (starting with underscore)
    (r'\b_\w+', "Private identifiers (starting with underscore) are not allowed in APIthon"),

    # Dangerous built-ins
    (r'\beval\s*\(', "eval() function is not allowed in APIthon"),
    (r'\bexec\s*\(', "exec() function is not allowed in APIthon"),
    (r'\bcompile\s*\(', "compile() function is not allowed in APIthon"),
    (r'\bglobals\s*\(', "globals() function is not allowed in APIthon"),
    (r'\blocals\s*\(', "locals() function is not allowed in APIthon"),
    (r'\bvars\s*\(', "vars() function is not allowed in APIthon"),
    (r'\bdir\s*\(', "dir() function is not allowed in APIthon"),
    (r'\bhasattr\s*\(', "hasattr() function is not allowed in APIthon"),
    (r'\bgetattr\s*\(', "getattr() function is not allowed in APIthon"),
    (r'\bsetattr\s*\(', "setattr() function is not allowed in APIthon"),
    (r'\bdelattr\s*\(', "delattr() function is not allowed in APIthon"),

    # File operations
    (r'\bopen\s*\(', "File operations are not allowed in APIthon"),
    (r'\bfile\s*\(', "File operations are not allowed in APIthon"),

    # System operations
    (r'\bos\.', "OS module operations are not allowed in APIthon"),
    (r'\bsys\.', "System module operations are not allowed in APIthon"),
    (r'\bsubprocess\.', "Subprocess operations are not allowed in APIthon"),
]


def validate_apiton_code_restrictions(code: str) -> List[str]:
    """
    Validate APIthon code against prohibited patterns and restrictions.

    Args:
        code: The APIthon script code to validate

    Returns:
        List of validation error messages
    """
    error_set = set()  # Use set to avoid duplicate errors

    if not code or not code.strip():
        return ["Script code cannot be empty"]

    # Check for prohibited patterns using regex
    for pattern, error_message in PROHIBITED_PATTERNS:
        if re.search(pattern, code, re.MULTILINE):
            error_set.add(error_message)

    # Enhanced AST-based validation for comprehensive import detection
    try:
        tree = ast.parse(code)

        # Check for prohibited AST node types with detailed import analysis
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Extract specific import names for detailed error messages
                import_names = [alias.name for alias in node.names]
                if len(import_names) == 1:
                    error_set.add(f"Import statement 'import {import_names[0]}' is not allowed in APIthon")
                else:
                    error_set.add(f"Import statements 'import {', '.join(import_names)}' are not allowed in APIthon")

            elif isinstance(node, ast.ImportFrom):
                # Extract from...import details for specific error messages
                module_name = node.module or "unknown"
                import_names = [alias.name for alias in node.names]
                if '*' in [alias.name for alias in node.names]:
                    error_set.add(f"Wildcard import 'from {module_name} import *' is not allowed in APIthon")
                elif len(import_names) == 1:
                    error_set.add(f"Import statement 'from {module_name} import {import_names[0]}' is not allowed in APIthon")
                else:
                    error_set.add(f"Import statement 'from {module_name} import {', '.join(import_names)}' is not allowed in APIthon")

            elif isinstance(node, ast.ClassDef):
                error_set.add("Class definitions are not allowed in APIthon")
            elif isinstance(node, ast.FunctionDef):
                error_set.add("Function definitions are not allowed in APIthon")
            elif isinstance(node, ast.AsyncFunctionDef):
                error_set.add("Async function definitions are not allowed in APIthon")
            elif isinstance(node, ast.Global):
                error_set.add("Global statements are not allowed in APIthon")
            elif isinstance(node, ast.Nonlocal):
                error_set.add("Nonlocal statements are not allowed in APIthon")

    except SyntaxError:
        # Syntax errors will be caught by the main syntax validation
        pass

    return list(error_set)


def detect_import_statements_comprehensive(code: str) -> List[Dict[str, str]]:
    """
    Comprehensive import statement detection with detailed analysis and educational feedback.

    Args:
        code: The APIthon script code to analyze

    Returns:
        List of dictionaries containing import details with error messages and remediation
    """
    import_violations = []

    if not code or not code.strip():
        return import_violations

    # Enhanced regex patterns for specific import types
    import_patterns = [
        {
            'pattern': r'\bimport\s+([\w\.]+)(?:\s+as\s+(\w+))?',
            'type': 'simple_import',
            'description': 'Simple import statement'
        },
        {
            'pattern': r'\bfrom\s+([\w\.]+)\s+import\s+([\w\*]+)(?:\s+as\s+(\w+))?',
            'type': 'from_import',
            'description': 'From...import statement'
        },
        {
            'pattern': r'\bfrom\s+([\w\.]+)\s+import\s+\*',
            'type': 'wildcard_import',
            'description': 'Wildcard import (from ... import *)'
        },
        {
            'pattern': r'__import__\s*\(\s*["\']([^"\']+)["\']\s*\)',
            'type': 'dynamic_import',
            'description': 'Dynamic import with __import__()'
        }
    ]

    # Check each pattern
    for pattern_info in import_patterns:
        matches = re.finditer(pattern_info['pattern'], code, re.MULTILINE)
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            matched_text = match.group(0)

            violation = {
                'type': pattern_info['type'],
                'description': pattern_info['description'],
                'line_number': line_num,
                'matched_text': matched_text,
                'error_message': f"Line {line_num}: {pattern_info['description']} '{matched_text}' is not allowed in APIthon",
                'remediation': _get_import_remediation(pattern_info['type'], matched_text),
                'educational_context': "APIthon runs in a sandboxed environment and doesn't support external module imports. Use built-in Python functions or data.* references instead."
            }
            import_violations.append(violation)

    # AST-based detection for complex cases
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line_num = getattr(node, 'lineno', 0)

                if isinstance(node, ast.Import):
                    for alias in node.names:
                        violation = {
                            'type': 'ast_import',
                            'description': 'Import statement (AST detected)',
                            'line_number': line_num,
                            'matched_text': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""),
                            'error_message': f"Line {line_num}: Import statement 'import {alias.name}' is not allowed in APIthon",
                            'remediation': _get_import_remediation('simple_import', alias.name),
                            'educational_context': "APIthon scripts cannot import external modules. Use built-in functions or process data using data.* references."
                        }
                        import_violations.append(violation)

                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module or "unknown"
                    for alias in node.names:
                        import_text = f"from {module_name} import {alias.name}"
                        violation = {
                            'type': 'ast_from_import',
                            'description': 'From...import statement (AST detected)',
                            'line_number': line_num,
                            'matched_text': import_text,
                            'error_message': f"Line {line_num}: Import statement '{import_text}' is not allowed in APIthon",
                            'remediation': _get_import_remediation('from_import', f"{module_name}.{alias.name}"),
                            'educational_context': "APIthon cannot access external modules. Use built-in Python functions or data processing patterns instead."
                        }
                        import_violations.append(violation)

    except SyntaxError:
        # Syntax errors are handled elsewhere
        pass

    return import_violations


def _get_import_remediation(import_type: str, import_text: str) -> str:
    """
    Get specific remediation suggestions based on import type and content.

    Args:
        import_type: Type of import detected
        import_text: The import statement text

    Returns:
        Specific remediation suggestion
    """
    common_remediations = {
        'json': "Use built-in dict() and list() operations instead of json module",
        'os': "Use data.* references to access environment or system information",
        'sys': "Use data.* references for system information",
        'datetime': "Use string formatting or data.* references for date/time values",
        'time': "Use data.* references for timestamp values",
        'requests': "Use action steps (e.g., mw.http_request) for HTTP operations",
        'urllib': "Use action steps for URL operations",
        're': "Use built-in string methods like .replace(), .split(), .find() instead",
        'math': "Use built-in arithmetic operators (+, -, *, /, **, %) instead",
        'random': "Use data.* references for random values or predefined lists"
    }

    # Extract module name from import text
    module_name = import_text.lower()
    for module, suggestion in common_remediations.items():
        if module in module_name:
            return suggestion

    # Generic remediation
    if import_type in ['simple_import', 'ast_import']:
        return "Remove the import statement and use built-in Python functions or data.* references"
    elif import_type in ['from_import', 'ast_from_import']:
        return "Remove the import statement and use built-in alternatives or data.* references"
    elif import_type == 'wildcard_import':
        return "Remove the wildcard import and use specific built-in functions instead"
    elif import_type == 'dynamic_import':
        return "Remove the dynamic import and use direct data processing instead"
    else:
        return "Use built-in Python functions or data.* references instead of importing external modules"


def validate_apiton_syntax(code: str) -> List[str]:
    """
    Validate APIthon script syntax, allowing return statements at module level.

    Args:
        code: The APIthon script code to validate

    Returns:
        List of syntax validation error messages
    """
    errors = []

    if not code or not code.strip():
        return ["Script code cannot be empty"]

    # APIthon allows return statements at module level, so we need special handling
    try:
        # First, try to compile as-is (this will fail if there are return statements at module level)
        try:
            compile(code, '<apiton_script>', 'exec')
        except SyntaxError as e:
            # Check if the error is due to return statement at module level
            if "'return' outside function" in str(e):
                # Wrap in a function to validate the rest of the syntax
                wrapped_code = f"def apiton_script():\n"
                indented_code = '\n'.join(f"    {line}" for line in code.split('\n'))
                wrapped_code += indented_code

                try:
                    compile(wrapped_code, '<apiton_script_wrapped>', 'exec')
                    # If this succeeds, the return statement is the only issue, which is allowed in APIthon
                except SyntaxError as wrapped_e:
                    # There are other syntax errors
                    error_msg = str(wrapped_e)
                    if hasattr(wrapped_e, 'lineno') and wrapped_e.lineno and wrapped_e.lineno > 1:
                        # Adjust line numbers for the original code
                        adjusted_lineno = wrapped_e.lineno - 1
                        error_msg = error_msg.replace(f"line {wrapped_e.lineno}", f"line {adjusted_lineno}")
                    errors.append(f"Script syntax error - {error_msg}")
            else:
                # Other syntax error
                errors.append(f"Script syntax error - {str(e)}")

    except Exception as e:
        errors.append(f"Script compilation error - {str(e)}")

    return errors


def validate_apiton_data_references(code: str, available_data_paths: Set[str] = None) -> List[str]:
    """
    Validate data reference patterns in APIthon code.

    Args:
        code: The APIthon script code to validate
        available_data_paths: Set of available data paths for validation

    Returns:
        List of data reference validation error messages
    """
    errors = []

    if not code:
        return errors

    # Find data reference patterns
    data_patterns = [
        r'\bdata\.[\w\.]+',
        r'\bmeta_info\.[\w\.]+',
    ]

    found_references = set()
    for pattern in data_patterns:
        matches = re.findall(pattern, code)
        found_references.update(matches)

    # Validate each reference if we have available paths
    if available_data_paths:
        for ref in found_references:
            if ref not in available_data_paths:
                errors.append(f"Data reference '{ref}' is not available in the current context")

    return errors


def validate_script_step_structure(step: ScriptStep) -> List[str]:
    """
    Validate the structure of a ScriptStep for APIthon compliance.

    Args:
        step: The ScriptStep to validate

    Returns:
        List of structural validation error messages
    """
    errors = []

    # Validate required fields
    if not step.code or not step.code.strip():
        errors.append("Script step must have non-empty code")

    if not step.output_key or not step.output_key.strip():
        errors.append("Script step must have a valid output_key")

    # Validate output_key format
    if step.output_key:
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', step.output_key):
            errors.append(f"Output key '{step.output_key}' must be a valid identifier")

        if step.output_key.startswith('_'):
            errors.append(f"Output key '{step.output_key}' cannot start with underscore")

    # Validate input_args structure
    if step.input_args:
        if not isinstance(step.input_args, dict):
            errors.append("input_args must be a dictionary")
        else:
            for key, value in step.input_args.items():
                if not isinstance(key, str):
                    errors.append(f"input_args key '{key}' must be a string")

                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                    errors.append(f"input_args key '{key}' must be a valid identifier")

                # Validate data reference format in values
                if isinstance(value, str):
                    if not (value.startswith('data.') or value.startswith('meta_info.') or
                           value.startswith('{{data.') or value.startswith('{{meta_info.')):
                        errors.append(f"input_args value '{value}' should reference data context (data.* or meta_info.*)")

    return errors


def comprehensive_validate_apiton_script(step: ScriptStep, available_data_paths: Set[str] = None) -> List[str]:
    """
    Perform comprehensive APIthon validation on a script step.

    Args:
        step: The ScriptStep to validate
        available_data_paths: Set of available data paths for validation

    Returns:
        List of all validation error messages
    """
    all_errors = []

    # Structural validation
    all_errors.extend(validate_script_step_structure(step))

    # Only proceed with code validation if we have valid code
    if step.code and step.code.strip():
        # APIthon code restrictions
        all_errors.extend(validate_apiton_code_restrictions(step.code))

        # Syntax validation
        all_errors.extend(validate_apiton_syntax(step.code))

        # Data reference validation
        all_errors.extend(validate_apiton_data_references(step.code, available_data_paths))

    return all_errors


def validate_workflow_apiton_scripts(workflow: Workflow, available_data_paths: Set[str] = None) -> List[str]:
    """
    Validate all APIthon script steps in a workflow.

    Args:
        workflow: The Workflow to validate
        available_data_paths: Set of available data paths for validation

    Returns:
        List of all APIthon validation error messages
    """
    all_errors = []

    for i, step in enumerate(workflow.steps):
        step_num = i + 1

        if isinstance(step, ScriptStep):
            step_errors = comprehensive_validate_apiton_script(step, available_data_paths)

            # Prefix errors with step number
            for error in step_errors:
                all_errors.append(f"Step {step_num}: {error}")

    return all_errors


def generate_apiton_examples() -> Dict[str, Dict[str, str]]:
    """
    Generate examples of valid and invalid APIthon code for documentation and testing.

    Returns:
        Dictionary with 'valid' and 'invalid' examples
    """
    examples = {
        'valid': {
            'simple_calculation': """
# Simple calculation with return
result = data.input_value * 2
return {"doubled": result}
""",
            'data_processing': """
# Process user data
user_name = data.user_info.name
user_email = meta_info.user.email_addr
processed = {
    "greeting": f"Hello, {user_name}!",
    "contact": user_email,
    "timestamp": "2024-01-01"
}
return processed
""",
            'conditional_logic': """
# Conditional processing
if data.status == "active":
    result = {"message": "User is active", "code": 200}
else:
    result = {"message": "User is inactive", "code": 404}
return result
""",
            'list_processing': """
# Process list data
items = data.item_list
processed_items = []
for item in items:
    processed_items.append({
        "id": item.get("id"),
        "name": item.get("name", "Unknown"),
        "processed": True
    })
return {"items": processed_items, "count": len(processed_items)}
"""
        },
        'invalid': {
            'import_statement': """
import json  # ❌ Not allowed
return {"error": "imports not allowed"}
""",
            'class_definition': """
class MyClass:  # ❌ Not allowed
    def __init__(self):
        pass
return {}
""",
            'function_definition': """
def my_function():  # ❌ Not allowed
    return "hello"
return {"result": my_function()}
""",
            'private_identifier': """
_private_var = "secret"  # ❌ Not allowed
return {"value": _private_var}
""",
            'dangerous_builtin': """
result = eval("1 + 1")  # ❌ Not allowed
return {"result": result}
""",
            'file_operations': """
with open("file.txt") as f:  # ❌ Not allowed
    content = f.read()
return {"content": content}
"""
        }
    }

    return examples