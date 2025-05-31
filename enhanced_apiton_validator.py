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
class ValidationError:
    """Detailed validation error with location and context information."""
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    error_type: str = "general"
    remediation: Optional[str] = None
    educational_context: Optional[str] = None


@dataclass
class APIthonValidationResult:
    """Comprehensive APIthon validation result with detailed feedback."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    suggestions: List[str]
    resource_usage: Dict[str, Any]
    return_analysis: Dict[str, Any]
    citation_compliance: Dict[str, Any]
    private_member_violations: List[Dict[str, Any]]
    code_length_analysis: Dict[str, Any]

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
        if self.private_member_violations is None:
            self.private_member_violations = []
        if self.code_length_analysis is None:
            self.code_length_analysis = {}

    def add_error(self, message: str, line_number: Optional[int] = None,
                  error_type: str = "general", remediation: Optional[str] = None,
                  educational_context: Optional[str] = None, code_snippet: Optional[str] = None):
        """Add a detailed error to the validation result."""
        error = ValidationError(
            message=message,
            line_number=line_number,
            code_snippet=code_snippet,
            error_type=error_type,
            remediation=remediation,
            educational_context=educational_context
        )
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, message: str, line_number: Optional[int] = None,
                    error_type: str = "warning", remediation: Optional[str] = None,
                    educational_context: Optional[str] = None, code_snippet: Optional[str] = None):
        """Add a detailed warning to the validation result."""
        warning = ValidationError(
            message=message,
            line_number=line_number,
            code_snippet=code_snippet,
            error_type=error_type,
            remediation=remediation,
            educational_context=educational_context
        )
        self.warnings.append(warning)

    def get_error_messages(self) -> List[str]:
        """Get simple error messages for backward compatibility."""
        return [error.message for error in self.errors]

    def get_warning_messages(self) -> List[str]:
        """Get simple warning messages for backward compatibility."""
        return [warning.message for warning in self.warnings]


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
            citation_compliance={},
            private_member_violations=[],
            code_length_analysis={}
        )

        # Basic structural validation
        basic_errors = validate_script_step_structure(step)
        for error in basic_errors:
            result.add_error(error, error_type="structural")

        if not step.code or not step.code.strip():
            result.add_error(
                "Script code cannot be empty",
                error_type="structural",
                remediation="Add APIthon code to process data and return results",
                educational_context="APIthon scripts must contain at least one statement to process data"
            )
            return result

        # Enhanced private member detection
        self._detect_private_members(step.code, result)

        # Enhanced code length validation
        self._validate_enhanced_code_length(step.code, result)

        # Large literal detection (optional warnings)
        self._detect_large_literals(step.code, result)

        # Core APIthon validation with enhanced restrictions
        core_errors = self._enhanced_code_restrictions(step.code)
        for error in core_errors:
            result.add_error(error, error_type="restriction")

        syntax_errors = validate_apiton_syntax(step.code)
        for error in syntax_errors:
            result.add_error(error, error_type="syntax")

        data_ref_errors = validate_apiton_data_references(step.code, available_data_paths)
        for error in data_ref_errors:
            result.add_error(error, error_type="data_reference")

        # Enhanced validations
        self._validate_resource_constraints(step.code, result)
        self._analyze_return_value_logic(step.code, result)
        self._validate_citation_compliance(step, result)

        # Set overall validity
        result.is_valid = len(result.errors) == 0

        return result

    def _detect_private_members(self, code: str, result: APIthonValidationResult):
        """
        Enhanced private member detection with line number tracking.

        Detects any identifiers starting with a single underscore (_) in user-provided APIthon code.
        """
        lines = code.split('\n')
        private_violations = []

        # Regex pattern to find private identifiers
        private_pattern = r'\b_[a-zA-Z_][a-zA-Z0-9_]*\b'

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(private_pattern, line)
            for match in matches:
                identifier = match.group()
                # Skip double underscores (dunder methods) as they're handled elsewhere
                if not identifier.startswith('__'):
                    violation = {
                        'identifier': identifier,
                        'line_number': line_num,
                        'column': match.start(),
                        'line_content': line.strip()
                    }
                    private_violations.append(violation)

                    # Extract code snippet for context
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 1)
                    code_snippet = '\n'.join(f"{i+1:3}: {lines[i]}" for i in range(start_line, end_line))

                    result.add_error(
                        f"Private identifier '{identifier}' detected on line {line_num}",
                        line_number=line_num,
                        error_type="private_member",
                        code_snippet=code_snippet,
                        remediation=f"Rename '{identifier}' to remove the leading underscore (e.g., '{identifier[1:]}')",
                        educational_context="APIthon does not allow private identifiers (starting with _) as they are reserved for internal use"
                    )

        result.private_member_violations = private_violations

    def _validate_enhanced_code_length(self, code: str, result: APIthonValidationResult):
        """
        Enhanced code length validation with precise byte counting and overage reporting.
        """
        code_bytes = len(code.encode('utf-8'))
        result.code_length_analysis = {
            'code_bytes': code_bytes,
            'code_bytes_limit': self.constraints.max_code_bytes,
            'percentage_used': (code_bytes / self.constraints.max_code_bytes) * 100,
            'bytes_remaining': self.constraints.max_code_bytes - code_bytes
        }

        if code_bytes > self.constraints.max_code_bytes:
            overage = code_bytes - self.constraints.max_code_bytes
            result.add_error(
                f"Script code exceeds maximum size: {code_bytes} bytes > {self.constraints.max_code_bytes} bytes (overage: {overage} bytes)",
                error_type="code_length",
                remediation="Consider simplifying the script, removing comments, or breaking it into multiple steps",
                educational_context=f"APIthon scripts are limited to {self.constraints.max_code_bytes} bytes to ensure optimal performance"
            )
        elif code_bytes > self.constraints.max_code_bytes * 0.9:
            result.add_warning(
                f"Script code is approaching size limit: {code_bytes}/{self.constraints.max_code_bytes} bytes ({result.code_length_analysis['percentage_used']:.1f}%)",
                error_type="code_length_warning",
                remediation="Consider optimizing the script before adding more code",
                educational_context="Scripts approaching the size limit may need optimization for better maintainability"
            )

    def _detect_large_literals(self, code: str, result: APIthonValidationResult):
        """
        Detect large string literals and data structures that might approach size limits.
        """
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check string literals
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    string_size = len(node.value.encode('utf-8'))
                    if string_size > 1000:  # Warn for strings > 1KB
                        result.add_warning(
                            f"Large string literal detected: {string_size} bytes",
                            line_number=getattr(node, 'lineno', None),
                            error_type="large_literal",
                            remediation="Consider breaking large strings into smaller parts or using external data sources",
                            educational_context="Large string literals can impact script performance and readability"
                        )

                # Check list/dict literals
                elif isinstance(node, (ast.List, ast.Dict)):
                    # Estimate size based on number of elements
                    if isinstance(node, ast.List) and len(node.elts) > 50:
                        result.add_warning(
                            f"Large list literal with {len(node.elts)} elements detected",
                            line_number=getattr(node, 'lineno', None),
                            error_type="large_literal",
                            remediation="Consider processing data in smaller chunks or using iteration",
                            educational_context="Large data structures may approach serialization limits"
                        )
                    elif isinstance(node, ast.Dict) and len(node.keys) > 50:
                        result.add_warning(
                            f"Large dictionary literal with {len(node.keys)} keys detected",
                            line_number=getattr(node, 'lineno', None),
                            error_type="large_literal",
                            remediation="Consider processing data in smaller chunks or using iteration",
                            educational_context="Large data structures may approach serialization limits"
                        )
        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass

    def _enhanced_code_restrictions(self, code: str) -> List[str]:
        """
        Enhanced APIthon code restrictions with stricter import and class detection.

        Args:
            code: The APIthon script code to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Start with basic restrictions
        errors.extend(validate_apiton_code_restrictions(code))

        # Enhanced import statement detection
        enhanced_import_patterns = [
            (r'\bfrom\s+\w+(\.\w+)*\s+import\s+\w+', "Enhanced: 'from ... import' statements are not allowed in APIthon"),
            (r'\bfrom\s+\w+(\.\w+)*\s+import\s+\*', "Enhanced: 'from ... import *' statements are not allowed in APIthon"),
            (r'\bimport\s+\w+(\.\w+)*(\s+as\s+\w+)?', "Enhanced: Import statements with aliases are not allowed in APIthon"),
            (r'__import__\s*\(\s*["\'][\w\.]+["\']\s*\)', "Enhanced: Dynamic imports with __import__ are not allowed in APIthon"),
        ]

        # Enhanced class definition detection
        enhanced_class_patterns = [
            (r'^\s*class\s+\w+\s*\(.*\)\s*:', "Enhanced: Class definitions with inheritance are not allowed in APIthon"),
            (r'^\s*class\s+\w+\s*:', "Enhanced: Class definitions are not allowed in APIthon"),
            (r'^\s*class\s+\w+\s*\(\s*\)\s*:', "Enhanced: Empty class definitions are not allowed in APIthon"),
        ]

        # Check enhanced patterns
        for pattern, error_message in enhanced_import_patterns + enhanced_class_patterns:
            if re.search(pattern, code, re.MULTILINE):
                errors.append(error_message)

        return errors

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
        """Enhanced return value logic analysis with intelligent parsing and guidance."""
        try:
            tree = ast.parse(code)
            statements = tree.body

            if not statements:
                result.add_error(
                    "Script must contain at least one statement",
                    error_type="return_logic",
                    remediation="Add at least one statement to process data",
                    educational_context="APIthon scripts need statements to process data and produce output"
                )
                return

            last_statement = statements[-1]
            last_line_num = getattr(last_statement, 'lineno', len(code.split('\n')))

            result.return_analysis['has_explicit_return'] = isinstance(last_statement, ast.Return)
            result.return_analysis['last_statement_type'] = type(last_statement).__name__
            result.return_analysis['statement_count'] = len(statements)
            result.return_analysis['last_line_number'] = last_line_num

            # Enhanced analysis for different statement types
            if isinstance(last_statement, ast.Assign):
                # Last line is an assignment - likely mistake
                if hasattr(last_statement, 'targets') and last_statement.targets:
                    target = last_statement.targets[0]
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        result.add_warning(
                            f"Last line assigns to variable '{var_name}' but doesn't return it",
                            line_number=last_line_num,
                            error_type="return_logic",
                            remediation=f"Add 'return {var_name}' as the final line, or change to '{var_name}' (expression)",
                            educational_context="APIthon uses the result of the final expression as the output_key value. Assignments don't return values."
                        )
                        result.suggestions.append(f"Add 'return {var_name}' as the final line")
                        result.suggestions.append(f"Or change the last line to just '{var_name}' (without assignment)")
                        result.suggestions.append("Example: Instead of 'result = data.value * 2', use 'data.value * 2' or 'return data.value * 2'")

            elif isinstance(last_statement, ast.Expr):
                # Check if it's a method call that returns None
                if isinstance(last_statement.value, ast.Call):
                    self._check_none_returning_calls(last_statement.value, result, last_line_num)
                else:
                    # Good - expression that will return a value
                    result.return_analysis['returns_value'] = True

            elif isinstance(last_statement, ast.Return):
                # Explicit return - good practice
                result.return_analysis['returns_value'] = True
                result.return_analysis['explicit_return'] = True

            elif isinstance(last_statement, (ast.If, ast.For, ast.While)):
                # Control flow as last statement - might not return value
                result.add_warning(
                    f"Script ends with {type(last_statement).__name__} statement which may not return a value",
                    line_number=last_line_num,
                    error_type="return_logic",
                    remediation="Add a return statement or expression after the control flow",
                    educational_context="Control flow statements don't return values. Ensure your script ends with an expression or return statement."
                )

            # Check for missing return when script has multiple statements
            if len(statements) > 1 and not isinstance(last_statement, (ast.Return, ast.Expr)):
                result.add_warning(
                    "Multi-statement script should end with a return statement or expression",
                    line_number=last_line_num,
                    error_type="return_logic",
                    remediation="Add a return statement or ensure the last line is an expression",
                    educational_context="The output_key will receive the result of the final expression. Statements like assignments don't produce output."
                )

            # Provide educational examples based on script complexity
            if len(statements) == 1:
                result.suggestions.append("Single-statement example: 'data.user_info.name.upper()' returns the uppercase name")
            else:
                result.suggestions.append("Multi-statement example: Process data in multiple lines, then 'return final_result' or just 'final_result'")

        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass

    def _check_none_returning_calls(self, call_node: ast.Call, result: APIthonValidationResult, line_number: int = None):
        """Check for method calls that return None (in-place operations)."""
        none_returning_methods = {
            'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'sort', 'reverse',
            'update', 'setdefault', 'popitem'
        }

        if isinstance(call_node.func, ast.Attribute):
            method_name = call_node.func.attr
            if method_name in none_returning_methods:
                result.add_warning(
                    f"Method '{method_name}()' returns None and may not provide the expected output",
                    line_number=line_number,
                    error_type="return_logic",
                    remediation=f"Use the modified object directly instead of the '{method_name}()' method call",
                    educational_context=f"The '{method_name}()' method modifies the object in-place and returns None, not the modified object"
                )

                # Provide specific suggestions based on method
                if method_name in ['append', 'extend', 'insert']:
                    result.suggestions.append("Use the list variable after modification instead of the method call")
                    result.suggestions.append(f"Example: Instead of 'my_list.{method_name}(item)', use 'my_list.{method_name}(item); my_list'")
                elif method_name == 'update':
                    result.suggestions.append("Use the dictionary variable after update instead of the method call")
                    result.suggestions.append("Example: Instead of 'my_dict.update(data)', use 'my_dict.update(data); my_dict'")
                elif method_name in ['sort', 'reverse']:
                    result.suggestions.append("Use sorted() or reversed() functions, or the list variable after modification")
                    result.suggestions.append(f"Example: Use 'sorted(my_list)' instead of 'my_list.{method_name}()'")
                elif method_name in ['remove', 'pop']:
                    result.suggestions.append("These methods modify the list. Use the list variable after modification if you need the result")
                elif method_name == 'clear':
                    result.suggestions.append("This method empties the container. Use an empty literal instead if you need an empty result")

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
