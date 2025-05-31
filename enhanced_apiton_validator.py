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
    validate_apiton_data_references,
    detect_import_statements_comprehensive
)


@dataclass
class ValidationError:
    """Enhanced validation error with comprehensive location and context information."""
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    error_type: str = "general"
    remediation: Optional[str] = None
    educational_context: Optional[str] = None
    step_number: Optional[int] = None
    step_type: Optional[str] = None
    field_name: Optional[str] = None
    severity: str = "error"  # error, warning, info
    auto_fix_available: bool = False
    auto_fix_data: Optional[Dict[str, Any]] = None

    def get_location_string(self) -> str:
        """Get a formatted location string for the error."""
        parts = []

        if self.step_number is not None:
            parts.append(f"Step {self.step_number}")

        if self.step_type:
            parts.append(f"({self.step_type})")

        if self.field_name:
            parts.append(f"→ {self.field_name}")

        if self.line_number is not None:
            parts.append(f"line {self.line_number}")

        return " ".join(parts) if parts else "Unknown location"

    def get_formatted_message(self) -> str:
        """Get a fully formatted error message with location and context."""
        location = self.get_location_string()

        formatted = f"{location}: {self.message}"

        if self.educational_context:
            formatted += f"\n  Why: {self.educational_context}"

        if self.remediation:
            formatted += f"\n  Fix: {self.remediation}"

        if self.auto_fix_available:
            formatted += "\n  ⚡ Auto-fix available"

        return formatted


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
    import_violations: List[Dict[str, str]]

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
        if self.import_violations is None:
            self.import_violations = []

    def add_error(self, message: str, line_number: Optional[int] = None,
                  error_type: str = "general", remediation: Optional[str] = None,
                  educational_context: Optional[str] = None, code_snippet: Optional[str] = None,
                  step_number: Optional[int] = None, step_type: Optional[str] = None,
                  field_name: Optional[str] = None, severity: str = "error",
                  auto_fix_available: bool = False, auto_fix_data: Optional[Dict[str, Any]] = None):
        """Add a detailed error to the validation result."""
        error = ValidationError(
            message=message,
            line_number=line_number,
            code_snippet=code_snippet,
            error_type=error_type,
            remediation=remediation,
            educational_context=educational_context,
            step_number=step_number,
            step_type=step_type,
            field_name=field_name,
            severity=severity,
            auto_fix_available=auto_fix_available,
            auto_fix_data=auto_fix_data
        )
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, message: str, line_number: Optional[int] = None,
                    error_type: str = "warning", remediation: Optional[str] = None,
                    educational_context: Optional[str] = None, code_snippet: Optional[str] = None,
                    step_number: Optional[int] = None, step_type: Optional[str] = None,
                    field_name: Optional[str] = None, auto_fix_available: bool = False,
                    auto_fix_data: Optional[Dict[str, Any]] = None):
        """Add a detailed warning to the validation result."""
        warning = ValidationError(
            message=message,
            line_number=line_number,
            code_snippet=code_snippet,
            error_type=error_type,
            remediation=remediation,
            educational_context=educational_context,
            step_number=step_number,
            step_type=step_type,
            field_name=field_name,
            severity="warning",
            auto_fix_available=auto_fix_available,
            auto_fix_data=auto_fix_data
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
            code_length_analysis={},
            import_violations=[]
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

        # Comprehensive import statement detection
        self._detect_comprehensive_imports(step.code, result)

        # Enhanced private member detection
        self._detect_private_members(step.code, result)

        # Enhanced code length validation
        self._validate_enhanced_code_length(step.code, result)

        # Resource limit validation
        self._validate_resource_limits(step.code, result)

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

    def _detect_comprehensive_imports(self, code: str, result: APIthonValidationResult):
        """
        Comprehensive import statement detection with detailed analysis and educational feedback.

        Uses the enhanced import detection from apiton_validator to provide detailed
        import violation information with specific remediation suggestions.
        """
        import_violations = detect_import_statements_comprehensive(code)
        result.import_violations = import_violations

        # Convert import violations to validation errors with enhanced messaging
        for violation in import_violations:
            result.add_error(
                violation['error_message'],
                line_number=violation.get('line_number'),
                error_type="import_statement",
                remediation=violation.get('remediation'),
                educational_context=violation.get('educational_context'),
                code_snippet=self._extract_code_snippet(code, violation.get('line_number', 1))
            )

            # Add specific suggestions based on import type
            if violation['type'] in ['simple_import', 'ast_import']:
                result.suggestions.append(f"Replace '{violation['matched_text']}' with built-in Python functions or data.* references")
            elif violation['type'] in ['from_import', 'ast_from_import']:
                result.suggestions.append(f"Remove '{violation['matched_text']}' and use built-in alternatives")
            elif violation['type'] == 'wildcard_import':
                result.suggestions.append(f"Remove '{violation['matched_text']}' and use specific built-in functions")
            elif violation['type'] == 'dynamic_import':
                result.suggestions.append(f"Remove '{violation['matched_text']}' and use direct data processing")

    def _extract_code_snippet(self, code: str, line_number: int, context_lines: int = 2) -> str:
        """
        Extract a code snippet around the specified line number for error context.

        Args:
            code: The full code string
            line_number: The line number to center the snippet around
            context_lines: Number of lines before and after to include

        Returns:
            Formatted code snippet with line numbers
        """
        lines = code.split('\n')
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)

        snippet_lines = []
        for i in range(start_line, end_line):
            line_num = i + 1
            prefix = ">>> " if line_num == line_number else "    "
            snippet_lines.append(f"{prefix}{line_num:3}: {lines[i]}")

        return '\n'.join(snippet_lines)

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
        """
        Comprehensive return value logic analysis with intelligent parsing and educational guidance.

        Analyzes the final statement in APIthon code to ensure proper return value handling,
        providing specific warnings and remediation for common patterns that result in None.
        """
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

            # Enhanced return analysis tracking
            result.return_analysis['has_explicit_return'] = isinstance(last_statement, ast.Return)
            result.return_analysis['last_statement_type'] = type(last_statement).__name__
            result.return_analysis['statement_count'] = len(statements)
            result.return_analysis['last_line_number'] = last_line_num
            result.return_analysis['is_single_statement'] = len(statements) == 1
            result.return_analysis['returns_value'] = False  # Will be set to True for valid patterns

            # Comprehensive analysis for different statement types
            if isinstance(last_statement, ast.Assign):
                # Last line is an assignment - this will result in None being assigned to output_key
                self._analyze_assignment_as_last_line(last_statement, last_line_num, result, statements)

            elif isinstance(last_statement, ast.Expr):
                # Expression statement - analyze what type of expression
                self._analyze_expression_as_last_line(last_statement, last_line_num, result, statements)

            elif isinstance(last_statement, ast.Return):
                # Explicit return - good practice
                self._analyze_explicit_return(last_statement, last_line_num, result, statements)

            elif isinstance(last_statement, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                # Control flow as last statement - analyze potential return issues
                self._analyze_control_flow_as_last_line(last_statement, last_line_num, result, statements)

            elif isinstance(last_statement, (ast.Pass, ast.Break, ast.Continue)):
                # Statements that definitely don't return values
                self._analyze_non_returning_statement(last_statement, last_line_num, result, statements)

            else:
                # Other statement types that might not return values
                self._analyze_other_statement_types(last_statement, last_line_num, result, statements)

            # Provide comprehensive educational guidance
            self._provide_return_logic_guidance(result, statements)

        except SyntaxError:
            # Syntax errors are handled elsewhere
            pass

    def _analyze_assignment_as_last_line(self, assignment: ast.Assign, line_number: int,
                                       result: APIthonValidationResult, statements: list):
        """
        Analyze assignment statements as the last line - this is a common mistake.

        Assignment statements don't return values, so the output_key will receive None.
        """
        if hasattr(assignment, 'targets') and assignment.targets:
            target = assignment.targets[0]
            if isinstance(target, ast.Name):
                var_name = target.id

                # Extract the assignment value for better context
                assignment_value = self._extract_assignment_value_description(assignment.value)

                # Create comprehensive warning message
                warning_msg = f"Last line assigns to variable '{var_name}' but doesn't return it - this will result in None being assigned to output_key"

                # Enhanced remediation with specific examples
                remediation_options = [
                    f"Option 1: Add 'return {var_name}' as the final line",
                    f"Option 2: Change to '{var_name}' (expression without assignment)",
                    f"Option 3: Use the assignment value directly: {assignment_value}"
                ]

                result.add_warning(
                    warning_msg,
                    line_number=line_number,
                    error_type="return_logic",
                    remediation="; ".join(remediation_options),
                    educational_context="APIthon uses the result of the final expression as the output_key value. Assignment statements return None, not the assigned value."
                )

                # Add specific suggestions with before/after examples
                result.suggestions.append(f"❌ Current: {var_name} = {assignment_value}")
                result.suggestions.append(f"✅ Fix 1: {var_name} = {assignment_value}; return {var_name}")
                result.suggestions.append(f"✅ Fix 2: {assignment_value}  # Direct expression")

                # Add context-specific guidance
                if len(statements) == 1:
                    result.suggestions.append("💡 Single-line tip: For one-line scripts, use expressions directly without assignment")
                else:
                    result.suggestions.append("💡 Multi-line tip: Process data in multiple lines, then return the final result")

    def _analyze_expression_as_last_line(self, expression: ast.Expr, line_number: int,
                                       result: APIthonValidationResult, statements: list):
        """
        Analyze expression statements as the last line - this is usually correct.

        Expression statements return their value, which is what we want for output_key.
        """
        if isinstance(expression.value, ast.Call):
            # Check if it's a method call that returns None
            self._check_none_returning_calls(expression.value, result, line_number)
        else:
            # Good - expression that will return a value
            result.return_analysis['returns_value'] = True
            result.return_analysis['last_line_pattern'] = 'expression'

            # Provide positive feedback for correct usage
            expr_description = self._extract_expression_description(expression.value)
            result.suggestions.append(f"✅ Good: Expression '{expr_description}' will return its value to output_key")

    def _analyze_explicit_return(self, return_stmt: ast.Return, line_number: int,
                               result: APIthonValidationResult, statements: list):
        """
        Analyze explicit return statements - this is the best practice.
        """
        result.return_analysis['returns_value'] = True
        result.return_analysis['explicit_return'] = True
        result.return_analysis['last_line_pattern'] = 'explicit_return'

        # Provide positive feedback
        if return_stmt.value:
            return_value_desc = self._extract_expression_description(return_stmt.value)
            result.suggestions.append(f"✅ Excellent: Explicit 'return {return_value_desc}' clearly shows the output value")
        else:
            result.add_warning(
                "Explicit 'return' statement without a value will return None",
                line_number=line_number,
                error_type="return_logic",
                remediation="Add a value after 'return' or remove the return statement if not needed",
                educational_context="Return statements without values return None, which may not be the intended output"
            )

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

    def _analyze_control_flow_as_last_line(self, control_flow: ast.stmt, line_number: int,
                                         result: APIthonValidationResult, statements: list):
        """
        Analyze control flow statements as the last line - these may not return values.
        """
        statement_type = type(control_flow).__name__

        result.add_warning(
            f"Script ends with {statement_type} statement which may not return a value",
            line_number=line_number,
            error_type="return_logic",
            remediation=f"Add a return statement or expression after the {statement_type}",
            educational_context="Control flow statements don't return values. Ensure your script ends with an expression or return statement."
        )

        # Provide specific guidance based on control flow type
        if isinstance(control_flow, ast.If):
            result.suggestions.append("💡 If statements: Ensure all branches return values, or add a final return/expression")
            result.suggestions.append("✅ Example: if condition: return value1; else: return value2")
        elif isinstance(control_flow, ast.For):
            result.suggestions.append("💡 For loops: Add a return statement after the loop to provide the final result")
            result.suggestions.append("✅ Example: for item in items: process(item); return processed_items")
        elif isinstance(control_flow, ast.While):
            result.suggestions.append("💡 While loops: Add a return statement after the loop")
        elif isinstance(control_flow, ast.With):
            result.suggestions.append("💡 With statements: Add a return statement after the with block")
        elif isinstance(control_flow, ast.Try):
            result.suggestions.append("💡 Try statements: Ensure all branches (try/except/finally) handle return values")

    def _analyze_non_returning_statement(self, statement: ast.stmt, line_number: int,
                                       result: APIthonValidationResult, statements: list):
        """
        Analyze statements that definitely don't return values.
        """
        statement_type = type(statement).__name__

        result.add_warning(
            f"Script ends with {statement_type} statement which returns None",
            line_number=line_number,
            error_type="return_logic",
            remediation=f"Add a return statement or expression after the {statement_type}",
            educational_context=f"{statement_type} statements don't produce output values for the output_key."
        )

    def _analyze_other_statement_types(self, statement: ast.stmt, line_number: int,
                                     result: APIthonValidationResult, statements: list):
        """
        Analyze other statement types that might not return values.
        """
        statement_type = type(statement).__name__

        result.add_warning(
            f"Script ends with {statement_type} statement - verify it returns the intended value",
            line_number=line_number,
            error_type="return_logic",
            remediation="Consider adding an explicit return statement or expression",
            educational_context="Ensure the final statement produces the value you want assigned to output_key."
        )

    def _provide_return_logic_guidance(self, result: APIthonValidationResult, statements: list):
        """
        Provide comprehensive educational guidance based on script structure.
        """
        statement_count = len(statements)

        if statement_count == 1:
            result.suggestions.append("📚 Single-statement scripts: Use expressions directly (e.g., 'data.user.name.upper()')")
        else:
            result.suggestions.append("📚 Multi-statement scripts: Process data in multiple lines, then 'return final_result' or just 'final_result'")

        # Add general best practices
        result.suggestions.append("🎯 Best practice: Use explicit 'return value' for clarity")
        result.suggestions.append("⚡ Quick fix: For assignments, either add 'return variable' or use the expression directly")

    def _extract_assignment_value_description(self, value_node: ast.expr) -> str:
        """
        Extract a human-readable description of an assignment value.
        """
        try:
            if isinstance(value_node, ast.Name):
                return value_node.id
            elif isinstance(value_node, ast.Constant):
                return repr(value_node.value)
            elif isinstance(value_node, ast.BinOp):
                left = self._extract_expression_description(value_node.left)
                right = self._extract_expression_description(value_node.right)
                op = self._get_operator_symbol(value_node.op)
                return f"{left} {op} {right}"
            elif isinstance(value_node, ast.Call):
                func_name = self._extract_expression_description(value_node.func)
                return f"{func_name}(...)"
            elif isinstance(value_node, ast.Dict):
                return "{...}"
            elif isinstance(value_node, ast.List):
                return "[...]"
            else:
                return "expression"
        except:
            return "expression"

    def _extract_expression_description(self, expr_node: ast.expr) -> str:
        """
        Extract a human-readable description of an expression.
        """
        try:
            if isinstance(expr_node, ast.Name):
                return expr_node.id
            elif isinstance(expr_node, ast.Constant):
                return repr(expr_node.value)
            elif isinstance(expr_node, ast.Attribute):
                value = self._extract_expression_description(expr_node.value)
                return f"{value}.{expr_node.attr}"
            elif isinstance(expr_node, ast.Call):
                func = self._extract_expression_description(expr_node.func)
                return f"{func}()"
            elif isinstance(expr_node, ast.BinOp):
                left = self._extract_expression_description(expr_node.left)
                right = self._extract_expression_description(expr_node.right)
                op = self._get_operator_symbol(expr_node.op)
                return f"{left} {op} {right}"
            else:
                return type(expr_node).__name__.lower()
        except:
            return "expression"

    def _get_operator_symbol(self, op: ast.operator) -> str:
        """Get the symbol for an AST operator."""
        op_map = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**', ast.FloorDiv: '//',
            ast.BitOr: '|', ast.BitAnd: '&', ast.BitXor: '^'
        }
        return op_map.get(type(op), '?')

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

    def _validate_resource_limits(self, code: str, result: APIthonValidationResult):
        """Validate resource limits including byte counts, string lengths, and numeric ranges."""
        # Code byte limit validation (4096 bytes)
        code_bytes = len(code.encode('utf-8'))
        result.resource_usage['code_bytes'] = code_bytes
        result.resource_usage['code_byte_limit'] = 4096

        if code_bytes > 4096:
            result.add_error(
                f"APIthon code exceeds 4096 byte limit: {code_bytes} bytes",
                error_type="resource_limit",
                remediation="Reduce code size by simplifying logic, removing comments, or splitting into multiple steps"
            )
        elif code_bytes > 3276:  # 80% warning
            result.add_warning(
                f"APIthon code approaching byte limit: {code_bytes}/4096 bytes ({code_bytes/4096*100:.1f}%)",
                remediation="Consider optimizing code to stay well under the 4096 byte limit"
            )
        elif code_bytes > 3891:  # 95% warning
            result.add_warning(
                f"APIthon code very close to byte limit: {code_bytes}/4096 bytes ({code_bytes/4096*100:.1f}%)",
                remediation="Urgent: Reduce code size to avoid exceeding the 4096 byte limit"
            )

        # String length validation (4096 characters maximum)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    self._check_string_length(node.value, result)
        except SyntaxError:
            pass

        # Numeric range validation (up to 4294967296)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    self._check_numeric_range(node.value, result)
        except SyntaxError:
            pass

        # List serialization size heuristic (2096 byte limit)
        self._validate_list_serialization_size(code, result)

    def _check_string_length(self, string_value: str, result: APIthonValidationResult):
        """Check if string length exceeds limits."""
        length = len(string_value)
        if length > 4096:
            result.add_error(
                f"String literal exceeds 4096 character limit: {length} characters",
                error_type="resource_limit",
                remediation="Break large strings into smaller parts or use external data sources"
            )
        elif length > 3276:  # 80% warning
            result.add_warning(
                f"String literal approaching character limit: {length}/4096 characters",
                remediation="Consider reducing string size to stay under the 4096 character limit"
            )

    def _check_numeric_range(self, numeric_value: float, result: APIthonValidationResult):
        """Check if numeric value exceeds range limits."""
        max_value = 4294967296  # 2^32
        if abs(numeric_value) > max_value:
            result.add_error(
                f"Numeric value exceeds range limit: {numeric_value} (max: ±{max_value})",
                error_type="resource_limit",
                remediation="Use smaller numeric values within the supported range"
            )
        elif abs(numeric_value) > max_value * 0.8:  # 80% warning
            result.add_warning(
                f"Numeric value approaching range limit: {numeric_value}",
                remediation="Consider using smaller values to stay within safe limits"
            )

    def _validate_list_serialization_size(self, code: str, result: APIthonValidationResult):
        """Validate estimated list serialization size using heuristics."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.List):
                    estimated_size = self._estimate_list_size(node)
                    result.resource_usage['estimated_list_size'] = estimated_size
                    result.resource_usage['list_size_limit'] = 2096

                    if estimated_size > 2096:
                        result.add_error(
                            f"List may exceed 2096 byte serialization limit: ~{estimated_size} bytes",
                            error_type="resource_limit",
                            remediation="Reduce list size or use simpler data structures"
                        )
                    elif estimated_size > 1676:  # 80% warning
                        result.add_warning(
                            f"List approaching serialization limit: ~{estimated_size}/2096 bytes",
                            remediation="Consider reducing list size to stay under the 2096 byte limit"
                        )
        except SyntaxError:
            pass

    def _estimate_list_size(self, list_node: ast.List) -> int:
        """Estimate the serialized size of a list node."""
        estimated_size = 2  # [] brackets

        for i, element in enumerate(list_node.elts):
            if i > 0:
                estimated_size += 2  # ", " separator

            if isinstance(element, ast.Constant):
                if isinstance(element.value, str):
                    estimated_size += len(element.value) + 2  # quotes
                elif isinstance(element.value, (int, float)):
                    estimated_size += len(str(element.value))
                elif isinstance(element.value, bool):
                    estimated_size += 4 if element.value else 5  # true/false
                else:
                    estimated_size += 10  # rough estimate for other types
            elif isinstance(element, ast.Dict):
                estimated_size += self._estimate_dict_size(element)
            elif isinstance(element, ast.List):
                estimated_size += self._estimate_list_size(element)
            else:
                estimated_size += 20  # rough estimate for complex expressions

        return estimated_size

    def _estimate_dict_size(self, dict_node: ast.Dict) -> int:
        """Estimate the serialized size of a dictionary node."""
        estimated_size = 2  # {} brackets

        for i, (key, value) in enumerate(zip(dict_node.keys, dict_node.values)):
            if i > 0:
                estimated_size += 2  # ", " separator

            # Key size
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                estimated_size += len(key.value) + 2  # quotes
            else:
                estimated_size += 10  # rough estimate

            estimated_size += 2  # ": " separator

            # Value size
            if isinstance(value, ast.Constant):
                if isinstance(value.value, str):
                    estimated_size += len(value.value) + 2  # quotes
                elif isinstance(value.value, (int, float)):
                    estimated_size += len(str(value.value))
                else:
                    estimated_size += 10
            elif isinstance(value, ast.Dict):
                estimated_size += self._estimate_dict_size(value)
            elif isinstance(value, ast.List):
                estimated_size += self._estimate_list_size(value)
            else:
                estimated_size += 20

        return estimated_size

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
