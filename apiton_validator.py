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

# Prohibited patterns in APIthon code
PROHIBITED_PATTERNS = [
    # Import statements
    (r'\bimport\s+\w+', "Import statements are not allowed in APIthon"),
    (r'\bfrom\s+\w+\s+import\b', "Import statements are not allowed in APIthon"),
    (r'__import__\s*\(', "Dynamic imports are not allowed in APIthon"),

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

    # Additional AST-based validation for more complex patterns
    try:
        tree = ast.parse(code)

        # Check for prohibited AST node types (only add if not already caught by regex)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                error_set.add("Import statements are not allowed in APIthon")
            elif isinstance(node, ast.ImportFrom):
                error_set.add("Import statements are not allowed in APIthon")
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