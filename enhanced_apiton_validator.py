"""
Enhanced APIthon Validation Module for Moveworks YAML Assistant.

This module provides comprehensive APIthon validation including resource constraints,
return value logic analysis, and reserved output_key handling with educational features.
"""

import ast
import sys
import json
import re
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass
from core_structures import ScriptStep, Workflow
from apiton_validator import (
    validate_apiton_code_restrictions,
    validate_apiton_syntax,
    validate_script_step_structure,
    validate_apiton_data_references
)


@dataclass
class APIthonValidationResult:
    """Comprehensive APIthon validation result with detailed feedback."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    resource_usage: Dict[str, Any]
    return_analysis: Dict[str, Any]
    citation_compliance: Dict[str, Any]

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []
        if self.resource_usage is None:
            self.resource_usage = {}
        if self.return_analysis is None:
            self.return_analysis = {}
        if self.citation_compliance is None:
            self.citation_compliance = {}


@dataclass
class ResourceConstraints:
    """APIthon resource constraints configuration."""
    max_code_bytes: int = 4096
    max_serialized_bytes: int = 2096
    max_string_length: int = 4096
    max_uint32_value: int = 4294967295
    min_uint32_value: int = 0


class EnhancedAPIthonValidator:
    """Enhanced APIthon validator with comprehensive constraint checking."""

    def __init__(self):
        self.constraints = ResourceConstraints()
        self.citation_fields = {'id', 'friendly_id', 'title', 'url', 'snippet'}

    def comprehensive_validate(self, step: ScriptStep, available_data_paths: Set[str] = None) -> APIthonValidationResult:
        """
        Perform comprehensive APIthon validation with all enhancements.

        Args:
            step: The ScriptStep to validate
            available_data_paths: Set of available data paths for validation

        Returns:
            APIthonValidationResult with detailed validation feedback
        """
        result = APIthonValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            resource_usage={},
            return_analysis={},
            citation_compliance={}
        )

        # Basic structural validation
        basic_errors = validate_script_step_structure(step)
        result.errors.extend(basic_errors)

        if not step.code or not step.code.strip():
            result.is_valid = False
            return result

        # Core APIthon validation
        result.errors.extend(validate_apiton_code_restrictions(step.code))
        result.errors.extend(validate_apiton_syntax(step.code))
        result.errors.extend(validate_apiton_data_references(step.code, available_data_paths))

        # Enhanced validations
        self._validate_resource_constraints(step.code, result)
        self._analyze_return_value_logic(step.code, result)
        self._validate_citation_compliance(step, result)

        # Set overall validity
        result.is_valid = len(result.errors) == 0

        return result

    def _validate_resource_constraints(self, code: str, result: APIthonValidationResult):
        """Validate APIthon resource constraints."""
        # Code byte size validation
        code_bytes = len(code.encode('utf-8'))
        result.resource_usage['code_bytes'] = code_bytes
        result.resource_usage['code_bytes_limit'] = self.constraints.max_code_bytes

        if code_bytes > self.constraints.max_code_bytes:
            result.errors.append(
                f"Script code exceeds maximum size: {code_bytes} bytes > {self.constraints.max_code_bytes} bytes. "
                f"Consider simplifying the script or breaking it into multiple steps."
            )
        elif code_bytes > self.constraints.max_code_bytes * 0.8:
            result.warnings.append(
                f"Script code is approaching size limit: {code_bytes}/{self.constraints.max_code_bytes} bytes"
            )

        # String length validation
        self._validate_string_lengths(code, result)

        # Numeric value validation
        self._validate_numeric_values(code, result)

    def _validate_string_lengths(self, code: str, result: APIthonValidationResult):
        """Validate string literal lengths in the code."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Str):  # Python < 3.8
                    self._check_string_length(node.s, result)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):  # Python >= 3.8
                    self._check_string_length(node.value, result)
        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass

    def _check_string_length(self, string_value: str, result: APIthonValidationResult):
        """Check individual string length against constraints."""
        if len(string_value) > self.constraints.max_string_length:
            result.errors.append(
                f"String literal exceeds maximum length: {len(string_value)} > {self.constraints.max_string_length} characters"
            )
        elif len(string_value) > self.constraints.max_string_length * 0.8:
            result.warnings.append(
                f"String literal is approaching length limit: {len(string_value)}/{self.constraints.max_string_length} characters"
            )

    def _validate_numeric_values(self, code: str, result: APIthonValidationResult):
        """Validate numeric values are within uint32 range."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Num):  # Python < 3.8
                    self._check_numeric_value(node.n, result)
                elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):  # Python >= 3.8
                    self._check_numeric_value(node.value, result)
        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass

    def _check_numeric_value(self, value: Any, result: APIthonValidationResult):
        """Check individual numeric value against uint32 constraints."""
        if isinstance(value, int):
            if value < self.constraints.min_uint32_value or value > self.constraints.max_uint32_value:
                result.errors.append(
                    f"Integer value {value} is outside uint32 range "
                    f"({self.constraints.min_uint32_value} to {self.constraints.max_uint32_value})"
                )

    def _analyze_return_value_logic(self, code: str, result: APIthonValidationResult):
        """Analyze return value logic and detect common mistakes."""
        try:
            tree = ast.parse(code)
            statements = tree.body

            if not statements:
                result.errors.append("Script must contain at least one statement")
                return

            last_statement = statements[-1]
            result.return_analysis['has_explicit_return'] = isinstance(last_statement, ast.Return)
            result.return_analysis['last_statement_type'] = type(last_statement).__name__

            # Check for common return value mistakes
            if isinstance(last_statement, ast.Assign):
                # Last line is an assignment - likely mistake
                if hasattr(last_statement, 'targets') and last_statement.targets:
                    target = last_statement.targets[0]
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        result.warnings.append(
                            f"Last line assigns to variable '{var_name}' but doesn't return it. "
                            f"Consider adding 'return {var_name}' or change to '{var_name}' (expression)."
                        )
                        result.suggestions.append(f"Add 'return {var_name}' as the final line")
                        result.suggestions.append(f"Or change the last line to just '{var_name}' (without assignment)")

            elif isinstance(last_statement, ast.Expr):
                # Check if it's a method call that returns None
                if isinstance(last_statement.value, ast.Call):
                    self._check_none_returning_calls(last_statement.value, result)

            # Check for missing return when script has multiple statements
            if len(statements) > 1 and not isinstance(last_statement, ast.Return):
                if not isinstance(last_statement, ast.Expr):
                    result.warnings.append(
                        "Multi-statement script should end with a return statement or expression. "
                        "The output_key will receive the result of the final expression."
                    )
                    result.suggestions.append("Add a return statement or ensure the last line is an expression")

        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass

    def _check_none_returning_calls(self, call_node: ast.Call, result: APIthonValidationResult):
        """Check for method calls that return None (in-place operations)."""
        none_returning_methods = {
            'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'sort', 'reverse',
            'update', 'setdefault', 'popitem'
        }

        if isinstance(call_node.func, ast.Attribute):
            method_name = call_node.func.attr
            if method_name in none_returning_methods:
                result.warnings.append(
                    f"Method '{method_name}()' returns None and may not provide the expected output. "
                    f"Consider using the modified object directly instead."
                )

                # Provide specific suggestions based on method
                if method_name in ['append', 'extend', 'insert']:
                    result.suggestions.append("Use the list variable after modification instead of the method call")
                elif method_name == 'update':
                    result.suggestions.append("Use the dictionary variable after update instead of the method call")
                elif method_name in ['sort', 'reverse']:
                    result.suggestions.append("Use sorted() or reversed() functions, or the list variable after modification")

    def _validate_citation_compliance(self, step: ScriptStep, result: APIthonValidationResult):
        """Validate citation compliance for reserved output_key names."""
        if not step.output_key:
            return

        output_key = step.output_key.lower()
        result.citation_compliance['output_key'] = step.output_key
        result.citation_compliance['is_reserved'] = output_key in ['result', 'results']

        if output_key == 'result':
            self._validate_single_citation_format(step.code, result)
        elif output_key == 'results':
            self._validate_multiple_citation_format(step.code, result)
        else:
            result.citation_compliance['compliance_status'] = 'not_applicable'

    def _validate_single_citation_format(self, code: str, result: APIthonValidationResult):
        """Validate that script returns a single citation-compatible dictionary."""
        result.citation_compliance['expected_format'] = 'single_citation_dict'
        result.citation_compliance['required_fields'] = list(self.citation_fields)

        # Analyze the return structure
        try:
            tree = ast.parse(code)
            return_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Return)]

            if not return_nodes:
                # Check if last statement is a dict expression
                if tree.body:
                    last_stmt = tree.body[-1]
                    if isinstance(last_stmt, ast.Expr) and isinstance(last_stmt.value, ast.Dict):
                        self._check_citation_dict_structure(last_stmt.value, result, 'single')
                    else:
                        result.warnings.append(
                            "output_key 'result' suggests citation format. "
                            "Script should return a dictionary with citation fields (id, friendly_id, title, url, snippet)."
                        )
            else:
                # Check return statement structure
                for return_node in return_nodes:
                    if return_node.value and isinstance(return_node.value, ast.Dict):
                        self._check_citation_dict_structure(return_node.value, result, 'single')

        except SyntaxError:
            pass

    def _validate_multiple_citation_format(self, code: str, result: APIthonValidationResult):
        """Validate that script returns a list of citation-compatible dictionaries."""
        result.citation_compliance['expected_format'] = 'citation_list'
        result.citation_compliance['required_fields'] = list(self.citation_fields)

        result.warnings.append(
            "output_key 'results' suggests multiple citations format. "
            "Script should return a list of dictionaries, each with citation fields (id, friendly_id, title, url, snippet)."
        )
        result.suggestions.append("Return a list like: [{'id': '1', 'friendly_id': 'item1', 'title': '...', 'url': '...', 'snippet': '...'}]")

    def _check_citation_dict_structure(self, dict_node: ast.Dict, result: APIthonValidationResult, format_type: str):
        """Check if a dictionary node has citation-compatible structure."""
        if not dict_node.keys:
            return

        # Extract string keys from the dictionary
        dict_keys = set()
        for key in dict_node.keys:
            if isinstance(key, ast.Str):  # Python < 3.8
                dict_keys.add(key.s)
            elif isinstance(key, ast.Constant) and isinstance(key.value, str):  # Python >= 3.8
                dict_keys.add(key.value)

        # Check for citation fields
        found_citation_fields = dict_keys.intersection(self.citation_fields)
        missing_citation_fields = self.citation_fields - dict_keys

        result.citation_compliance['found_fields'] = list(found_citation_fields)
        result.citation_compliance['missing_fields'] = list(missing_citation_fields)

        if found_citation_fields:
            result.citation_compliance['compliance_status'] = 'partial'
            if missing_citation_fields:
                result.suggestions.append(
                    f"Consider adding missing citation fields: {', '.join(missing_citation_fields)}"
                )
        else:
            result.citation_compliance['compliance_status'] = 'non_compliant'
            result.suggestions.append(
                f"For output_key '{result.citation_compliance['output_key']}', consider using citation fields: "
                f"{', '.join(self.citation_fields)}"
            )
            result.suggestions.append(
                "Or use a different output_key name if citation format is not intended"
            )


# Global instance for easy access
enhanced_apiton_validator = EnhancedAPIthonValidator()
