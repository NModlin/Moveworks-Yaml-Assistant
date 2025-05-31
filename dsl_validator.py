"""
DSL Validator for Moveworks Data Mapping Syntax (DSL) expressions.

This module provides comprehensive validation for DSL expressions including:
- Basic syntax validation
- Function call validation
- Data path validation
- Parentheses matching
- Common pattern recognition
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DSLValidationResult:
    """Result of DSL validation with detailed feedback."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    detected_patterns: List[str]
    function_calls: List[str]
    data_references: List[str]


class DSLValidator:
    """
    Comprehensive validator for Moveworks DSL expressions.
    
    Provides basic syntax validation to catch common mistakes without
    implementing a full DSL parser.
    """
    
    def __init__(self):
        # Known DSL functions that should start with $
        self.dsl_functions = {
            'CONCAT', 'SPLIT', 'TEXT', 'IF', 'UPPER', 'LOWER', 'TRIM',
            'REPLACE', 'SUBSTRING', 'LENGTH', 'CONTAINS', 'STARTSWITH',
            'ENDSWITH', 'REGEX', 'FORMAT', 'DATE', 'TIME', 'NOW',
            # Bender functions
            'MAP', 'FILTER', 'CONDITIONAL', 'LOOKUP', 'INTEGER', 'STARTS_WITH'
        }

        # Bender function signatures for validation
        self.bender_functions = {
            'MAP': {'min_args': 2, 'max_args': 3, 'description': 'Transform array items'},
            'FILTER': {'min_args': 2, 'max_args': 2, 'description': 'Filter array items by condition'},
            'CONDITIONAL': {'min_args': 3, 'max_args': 3, 'description': 'IF...THEN...ELSE logic'},
            'LOOKUP': {'min_args': 2, 'max_args': 3, 'description': 'Lookup value in mapping object'},
            'INTEGER': {'min_args': 1, 'max_args': 1, 'description': 'Convert to integer'},
            'STARTS_WITH': {'min_args': 2, 'max_args': 2, 'description': 'Check if string starts with prefix'}
        }
        
        # Data reference patterns
        self.data_patterns = [
            r'\bdata\.[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*',  # data.field.subfield
            r'\bdata\.[a-zA-Z_][a-zA-Z0-9_]*\[[0-9]+\]',  # data.array[0]
            r'\bmeta_info\.[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*',  # meta_info.user.email
        ]
        
        # Operator patterns
        self.operators = ['==', '!=', '>=', '<=', '>', '<', '&&', '||', '!']
    
    def validate_dsl_expression(self, expression: str) -> DSLValidationResult:
        """
        Validate a DSL expression and provide detailed feedback.
        
        Args:
            expression: The DSL expression to validate
            
        Returns:
            DSLValidationResult with validation details
        """
        result = DSLValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            detected_patterns=[],
            function_calls=[],
            data_references=[]
        )
        
        if not expression or not expression.strip():
            result.errors.append("DSL expression cannot be empty")
            result.is_valid = False
            return result
        
        expression = expression.strip()
        
        # Check for basic syntax issues
        self._validate_parentheses(expression, result)
        self._validate_function_calls(expression, result)
        self._validate_data_references(expression, result)
        self._validate_operators(expression, result)
        self._detect_patterns(expression, result)
        self._provide_suggestions(expression, result)
        
        # Validate Bender functions
        self._validate_bender_functions(expression, result)

        # Set overall validity
        result.is_valid = len(result.errors) == 0

        return result
    
    def _validate_parentheses(self, expression: str, result: DSLValidationResult):
        """Check for matching parentheses."""
        stack = []
        for i, char in enumerate(expression):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    result.errors.append(f"Unmatched closing parenthesis at position {i}")
                else:
                    stack.pop()
        
        if stack:
            result.errors.append(f"Unmatched opening parenthesis at position {stack[-1]}")
    
    def _validate_function_calls(self, expression: str, result: DSLValidationResult):
        """Validate DSL function calls."""
        # Find potential function calls
        function_pattern = r'([A-Z_]+)\s*\('
        matches = re.finditer(function_pattern, expression)
        
        for match in matches:
            func_name = match.group(1)
            
            # Check if it should be a DSL function
            if func_name in self.dsl_functions:
                if not expression[match.start():match.start()+1] == '$':
                    # Check if $ is just before the function name
                    dollar_pos = match.start() - 1
                    if dollar_pos < 0 or expression[dollar_pos] != '$':
                        result.errors.append(f"DSL function '{func_name}' should start with '$' (use '${func_name}')")
                        result.suggestions.append(f"Change '{func_name}(' to '${func_name}('")
                else:
                    result.function_calls.append(f"${func_name}")
            
            # Check for unknown functions that might be typos
            elif func_name.isupper() and len(func_name) > 2:
                result.warnings.append(f"Unknown function '{func_name}' - did you mean a DSL function?")
                # Suggest similar DSL functions
                similar = [f for f in self.dsl_functions if f.startswith(func_name[:2])]
                if similar:
                    result.suggestions.append(f"Did you mean: {', '.join(f'${f}' for f in similar[:3])}?")
    
    def _validate_data_references(self, expression: str, result: DSLValidationResult):
        """Validate data references."""
        for pattern in self.data_patterns:
            matches = re.finditer(pattern, expression)
            for match in matches:
                data_ref = match.group()
                result.data_references.append(data_ref)
                
                # Check for common mistakes
                if '..' in data_ref:
                    result.errors.append(f"Invalid data reference '{data_ref}' - contains double dots")
                
                # Check for invalid characters
                if re.search(r'[^a-zA-Z0-9_.\[\]]', data_ref.replace('meta_info', '').replace('data', '')):
                    result.warnings.append(f"Data reference '{data_ref}' contains unusual characters")
    
    def _validate_operators(self, expression: str, result: DSLValidationResult):
        """Validate operators and comparisons."""
        # Check for single = instead of ==
        single_equals = re.finditer(r'(?<![=!<>])=(?![=])', expression)
        for match in single_equals:
            # Skip if it's part of a function parameter assignment
            context_start = max(0, match.start() - 10)
            context = expression[context_start:match.end() + 10]
            if not re.search(r'\$[A-Z_]+\([^)]*=', context):
                result.errors.append(f"Use '==' for comparison, not '=' at position {match.start()}")
                result.suggestions.append("Change '=' to '==' for equality comparison")
    
    def _detect_patterns(self, expression: str, result: DSLValidationResult):
        """Detect common DSL patterns."""
        patterns = {
            'data_reference': r'\bdata\.[a-zA-Z_][a-zA-Z0-9_.]*',
            'meta_info_reference': r'\bmeta_info\.[a-zA-Z_][a-zA-Z0-9_.]*',
            'function_call': r'\$[A-Z_]+\(',
            'comparison': r'(==|!=|>=|<=|>|<)',
            'logical_operator': r'(&&|\|\|)',
            'array_access': r'\[[0-9]+\]',
            'string_literal': r'"[^"]*"',
            'number_literal': r'\b\d+(\.\d+)?\b'
        }
        
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, expression):
                result.detected_patterns.append(pattern_name)
    
    def _provide_suggestions(self, expression: str, result: DSLValidationResult):
        """Provide helpful suggestions based on the expression."""
        # Suggest common patterns
        if 'data.' in expression and 'CONCAT' not in expression.upper():
            if ' + ' in expression:
                result.suggestions.append("For string concatenation, consider using $CONCAT([...]) instead of '+'")
        
        # Suggest meta_info usage
        if 'user' in expression.lower() and 'meta_info' not in expression:
            result.suggestions.append("For current user information, consider using meta_info.user.email or meta_info.user.name")
        
        # Suggest proper quoting
        if any(op in expression for op in self.operators) and '"' not in expression:
            result.suggestions.append("Remember to quote the entire DSL expression in YAML (e.g., condition: \"data.age >= 18\")")

    def _validate_bender_functions(self, expression: str, result: DSLValidationResult):
        """Validate Bender function calls and their arguments."""
        # Find all Bender function calls
        bender_pattern = r'\$(' + '|'.join(self.bender_functions.keys()) + r')\s*\('
        matches = re.finditer(bender_pattern, expression)

        for match in matches:
            func_name = match.group(1)
            func_info = self.bender_functions[func_name]

            # Find the complete function call
            start_pos = match.start()
            paren_count = 0
            end_pos = start_pos

            for i, char in enumerate(expression[match.end()-1:], match.end()-1):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        end_pos = i + 1
                        break

            if paren_count != 0:
                result.errors.append(f"Unmatched parentheses in ${func_name} function call")
                continue

            # Extract function arguments
            func_call = expression[start_pos:end_pos]
            args_str = func_call[func_call.find('(')+1:func_call.rfind(')')]

            # Simple argument counting (basic validation)
            if args_str.strip():
                # Count commas at top level (not inside nested parentheses)
                arg_count = self._count_top_level_commas(args_str) + 1
            else:
                arg_count = 0

            # Validate argument count
            min_args = func_info['min_args']
            max_args = func_info['max_args']

            if arg_count < min_args:
                result.errors.append(f"${func_name} requires at least {min_args} argument(s), got {arg_count}")
            elif arg_count > max_args:
                result.errors.append(f"${func_name} accepts at most {max_args} argument(s), got {arg_count}")
            else:
                result.suggestions.append(f"✓ ${func_name} function call looks valid")

            # Function-specific validation
            self._validate_specific_bender_function(func_name, args_str, result)

    def _count_top_level_commas(self, args_str: str) -> int:
        """Count commas at the top level (not inside nested parentheses or brackets)."""
        count = 0
        paren_depth = 0
        bracket_depth = 0

        for char in args_str:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == ',' and paren_depth == 0 and bracket_depth == 0:
                count += 1

        return count

    def _validate_specific_bender_function(self, func_name: str, args_str: str, result: DSLValidationResult):
        """Validate specific Bender function requirements."""
        if func_name == 'MAP':
            # MAP(items, converter, context?) - items should be array path, converter should be expression
            if 'data.' not in args_str:
                result.warnings.append("MAP function typically requires a data path for items parameter")

        elif func_name == 'FILTER':
            # FILTER(items, condition) - items should be array path, condition should be boolean expression
            if 'data.' not in args_str:
                result.warnings.append("FILTER function typically requires a data path for items parameter")
            if not any(op in args_str for op in ['==', '!=', '>', '<', '>=', '<=']):
                result.warnings.append("FILTER condition should typically include comparison operators")

        elif func_name == 'CONDITIONAL':
            # CONDITIONAL(condition, on_pass, on_fail) - condition should be boolean expression
            args = [arg.strip() for arg in args_str.split(',')]
            if len(args) >= 1 and not any(op in args[0] for op in ['==', '!=', '>', '<', '>=', '<=', '&&', '||']):
                result.warnings.append("CONDITIONAL condition should typically include comparison or logical operators")

        elif func_name == 'LOOKUP':
            # LOOKUP(mapping, key, default?) - mapping should be object path
            if 'data.' not in args_str:
                result.warnings.append("LOOKUP function typically requires a data path for mapping parameter")


def is_dsl_expression(value: str) -> bool:
    """
    Quick check if a string appears to be a DSL expression.
    
    Args:
        value: String to check
        
    Returns:
        True if the value appears to be a DSL expression
    """
    if not isinstance(value, str):
        return False
    
    # Quick patterns that indicate DSL
    dsl_indicators = [
        r'\bdata\.',
        r'\bmeta_info\.',
        r'\$[A-Z_]+\(',
        r'==|!=|>=|<=|>|<',
        r'&&|\|\|'
    ]
    
    return any(re.search(pattern, value) for pattern in dsl_indicators)


def validate_dsl_string(expression: str) -> Tuple[bool, List[str]]:
    """
    Simple validation function for backward compatibility.
    
    Args:
        expression: DSL expression to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = DSLValidator()
    result = validator.validate_dsl_expression(expression)
    return result.is_valid, result.errors


# Global validator instance
dsl_validator = DSLValidator()
