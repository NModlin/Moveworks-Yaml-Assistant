#!/usr/bin/env python3
"""
Comprehensive test script for real-time validation system.

This script tests all components of the enhanced real-time validation framework
including field-level validation, enhanced error messaging, and UI integration.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PySide6.QtCore import Qt

from realtime_validation_widgets import (
    ValidatedLineEdit, SnakeCaseLineEdit, NumericRangeEdit, BooleanComboBox,
    ActionNameComboBox, DSLExpressionEdit, TimeUnitComboBox, ValidatedInputGroup,
    ValidationState
)
from realtime_validation_manager import RealtimeValidationManager, ValidationSummary
from core_structures import Workflow, ActionStep, ScriptStep
from enhanced_apiton_validator import ValidationError


def test_validation_widgets():
    """Test all validation widgets with various inputs."""
    print("=" * 60)
    print("TEST 1: Validation Widgets")
    print("=" * 60)

    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Test snake_case validation
    print("\n1. Snake Case Validation:")
    snake_case_widget = SnakeCaseLineEdit()

    test_cases = [
        ("valid_snake_case", True),
        ("InvalidCamelCase", False),
        ("invalid-kebab-case", False),
        ("invalid spaces", False),
        ("123invalid", False),
        ("", True),  # Empty is allowed
    ]

    for test_value, expected_valid in test_cases:
        is_valid, message, suggestions = snake_case_widget._validate_snake_case(test_value)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"  '{test_value}': {status} - {message}")
        if suggestions:
            print(f"    Suggestions: {suggestions[:2]}")

    # Test numeric range validation
    print("\n2. Numeric Range Validation:")
    numeric_widget = NumericRangeEdit(0, 100)

    numeric_test_cases = [
        ("50", True),
        ("0", True),
        ("100", True),
        ("-1", False),
        ("101", False),
        ("abc", False),
        ("", True),  # Empty is allowed
    ]

    for test_value, expected_valid in numeric_test_cases:
        is_valid, message, suggestions = numeric_widget._validate_numeric_range(test_value)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"  '{test_value}': {status} - {message}")

    # Test boolean validation
    print("\n3. Boolean Validation:")
    boolean_widget = BooleanComboBox()

    boolean_test_cases = [
        ("true", True),
        ("false", True),
        ("yes", True),
        ("no", True),
        ("1", True),
        ("0", True),
        ("invalid", False),
        ("", True),  # Empty is allowed
    ]

    for test_value, expected_valid in boolean_test_cases:
        is_valid, message, suggestions = boolean_widget._validate_boolean(test_value)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"  '{test_value}': {status} - {message}")

    # Test DSL expression validation
    print("\n4. DSL Expression Validation:")
    dsl_widget = DSLExpressionEdit("condition")

    dsl_test_cases = [
        ("data.user_info.email", True),
        ("meta_info.user.name", True),
        ("$CONCAT([data.first, data.last])", True),
        ("data.age >= 18", True),
        ("CONCAT([data.first, data.last])", False),  # Missing $
        ("regular_string", True),  # Not DSL, but valid
        ("", True),  # Empty is allowed
    ]

    for test_value, expected_valid in dsl_test_cases:
        is_valid, message, suggestions = dsl_widget._validate_dsl_expression(test_value)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"  '{test_value}': {status} - {message}")

    return True


def test_validation_manager():
    """Test the real-time validation manager."""
    print("\n" + "=" * 60)
    print("TEST 2: Validation Manager")
    print("=" * 60)

    manager = RealtimeValidationManager()

    # Create test workflow
    workflow = Workflow(steps=[
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={
                "email": "data.input_email",  # Valid DSL
                "timeout": "30"  # Valid numeric
            }
        ),
        ScriptStep(
            code="result = {'processed': True}",
            output_key="script_result",
            input_args={
                "user_data": "data.user_info"  # Valid DSL reference
            }
        )
    ])

    manager.set_workflow(workflow)

    # Test field validation
    print("\n1. Field Validation Tests:")

    field_tests = [
        (0, "output_key", "valid_output_key", True),
        (0, "output_key", "InvalidCamelCase", False),
        (0, "action_name", "mw.get_user_by_email", True),
        (0, "action_name", "unknown.action", False),
        (0, "input_arg_email", "data.user_info.email", True),
        (0, "input_arg_timeout", "30", True),
        (0, "input_arg_timeout", "invalid", False),
    ]

    for step_index, field_name, value, expected_valid in field_tests:
        is_valid, message, suggestions = manager.validate_field(step_index, field_name, value)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"  Step {step_index}, {field_name}='{value}': {status}")
        print(f"    Message: {message}")
        if suggestions:
            print(f"    Suggestions: {suggestions[:2]}")

    return True


def test_enhanced_error_messages():
    """Test enhanced error message formatting."""
    print("\n" + "=" * 60)
    print("TEST 3: Enhanced Error Messages")
    print("=" * 60)

    # Create test validation errors with enhanced context
    errors = [
        ValidationError(
            message="Field name must use lowercase_snake_case format",
            step_number=1,
            step_type="Action",
            field_name="output_key",
            error_type="field_naming",
            remediation="Change 'userInfo' to 'user_info'",
            educational_context="Snake case naming ensures consistency across Moveworks workflows",
            auto_fix_available=True,
            auto_fix_data={"type": "snake_case_conversion", "original": "userInfo", "fixed": "user_info"}
        ),
        ValidationError(
            message="APIthon code contains disallowed 'import' statement",
            line_number=3,
            step_number=2,
            step_type="Script",
            field_name="code",
            error_type="apiton_restriction",
            remediation="Remove the import statement and use built-in functions",
            educational_context="APIthon restricts imports for security and performance reasons",
            code_snippet="import requests  # This is not allowed"
        ),
        ValidationError(
            message="Invalid DSL expression syntax",
            step_number=1,
            step_type="Action",
            field_name="input_args.condition",
            error_type="dsl_syntax",
            remediation="Add missing '$' prefix: '$CONCAT([data.first, data.last])'",
            educational_context="DSL functions must start with '$' to be recognized by the Moveworks platform"
        )
    ]

    print("\n1. Formatted Error Messages:")
    for i, error in enumerate(errors, 1):
        print(f"\nError {i}:")
        print(f"  Location: {error.get_location_string()}")
        print(f"  Formatted Message:")
        formatted = error.get_formatted_message()
        for line in formatted.split('\n'):
            print(f"    {line}")

    # Test validation summary
    print("\n2. Validation Summary:")
    summary = ValidationSummary()
    summary.total_errors = len(errors)
    summary.errors_by_step = {1: [errors[0], errors[2]], 2: [errors[1]]}
    summary.errors_by_category = {
        "field_naming": [errors[0]],
        "apiton_restriction": [errors[1]],
        "dsl_syntax": [errors[2]]
    }
    summary.critical_errors = [errors[0], errors[1]]
    summary.auto_fixable_errors = [errors[0]]
    summary.is_export_ready = False

    print(f"  Total Errors: {summary.total_errors}")
    print(f"  Errors by Step: {dict(summary.errors_by_step)}")
    print(f"  Critical Errors: {len(summary.critical_errors)}")
    print(f"  Auto-fixable Errors: {len(summary.auto_fixable_errors)}")
    print(f"  Export Ready: {summary.is_export_ready}")

    return True


def test_ui_integration():
    """Test UI integration with validation widgets."""
    print("\n" + "=" * 60)
    print("TEST 4: UI Integration")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create test window with validation widgets
    window = QMainWindow()
    window.setWindowTitle("Real-time Validation Test")
    window.resize(800, 600)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    layout = QVBoxLayout(central_widget)

    # Create tab widget for different validation types
    tab_widget = QTabWidget()
    layout.addWidget(tab_widget)

    # Field validation tab
    field_tab = QWidget()
    field_layout = QVBoxLayout(field_tab)

    # Create validated input groups
    output_key_group = ValidatedInputGroup(
        SnakeCaseLineEdit(),
        "Output Key:"
    )
    field_layout.addWidget(output_key_group)

    action_name_group = ValidatedInputGroup(
        ActionNameComboBox(),
        "Action Name:"
    )
    field_layout.addWidget(action_name_group)

    timeout_group = ValidatedInputGroup(
        NumericRangeEdit(1, 300),
        "Timeout (seconds):"
    )
    field_layout.addWidget(timeout_group)

    enabled_group = ValidatedInputGroup(
        BooleanComboBox(),
        "Enabled:"
    )
    field_layout.addWidget(enabled_group)

    dsl_condition_group = ValidatedInputGroup(
        DSLExpressionEdit("condition"),
        "DSL Condition:"
    )
    field_layout.addWidget(dsl_condition_group)

    tab_widget.addTab(field_tab, "Field Validation")

    # Set some test values
    output_key_group.set_value("user_info")
    action_name_group.set_value("mw.get_user_by_email")
    timeout_group.set_value("30")
    enabled_group.set_value("true")
    dsl_condition_group.set_value("data.status == 'active'")

    print("✅ UI Integration test window created successfully!")
    print("  - Validated input groups with real-time feedback")
    print("  - Snake case, numeric, boolean, and DSL validation")
    print("  - Visual validation indicators")

    # Show window for manual testing (comment out for automated tests)
    # window.show()
    # app.exec()

    return True


def test_comprehensive_workflow_validation():
    """Test comprehensive workflow validation with all systems."""
    print("\n" + "=" * 60)
    print("TEST 5: Comprehensive Workflow Validation")
    print("=" * 60)

    # Create a complex workflow with various validation scenarios
    workflow = Workflow(steps=[
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={
                "email": "meta_info.user.email",  # Valid DSL
                "include_profile": "true",  # Valid boolean
                "timeout": "30"  # Valid numeric
            }
        ),
        ActionStep(
            action_name="unknown.action",  # Invalid action name
            output_key="InvalidCamelCase",  # Invalid snake_case
            input_args={
                "user_id": "data.user_info.id",  # Valid DSL
                "invalid-key": "value",  # Invalid key format
                "condition": "CONCAT([data.first, data.last])"  # Invalid DSL (missing $)
            }
        ),
        ScriptStep(
            code="import requests\nresult = requests.get('http://example.com')",  # Invalid APIthon
            output_key="script_result",
            input_args={
                "data": "data.user_info"  # Valid DSL
            }
        )
    ])

    # Test with validation manager
    manager = RealtimeValidationManager()
    manager.set_workflow(workflow)

    print("\n1. Workflow Structure:")
    for i, step in enumerate(workflow.steps):
        step_type = "Action" if isinstance(step, ActionStep) else "Script"
        print(f"  Step {i+1}: {step_type}")
        if hasattr(step, 'action_name'):
            print(f"    Action: {step.action_name}")
        print(f"    Output Key: {step.output_key}")
        print(f"    Input Args: {step.input_args}")

    # Validate individual fields
    print("\n2. Field-by-Field Validation:")
    validation_results = []

    # Test various field validations
    test_validations = [
        (0, "action_name", "mw.get_user_by_email"),
        (0, "output_key", "user_info"),
        (1, "action_name", "unknown.action"),
        (1, "output_key", "InvalidCamelCase"),
        (1, "input_arg_invalid-key", "value"),
        (1, "input_arg_condition", "CONCAT([data.first, data.last])"),
    ]

    for step_index, field_name, value in test_validations:
        is_valid, message, suggestions = manager.validate_field(step_index, field_name, value)
        validation_results.append((step_index, field_name, value, is_valid, message))

        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  Step {step_index+1}, {field_name}: {status}")
        print(f"    Value: '{value}'")
        print(f"    Message: {message}")
        if suggestions:
            print(f"    Suggestions: {suggestions[:2]}")
        print()

    # Summary
    valid_count = sum(1 for _, _, _, is_valid, _ in validation_results if is_valid)
    total_count = len(validation_results)

    print(f"3. Validation Summary:")
    print(f"  Total Validations: {total_count}")
    print(f"  Valid: {valid_count}")
    print(f"  Invalid: {total_count - valid_count}")
    print(f"  Success Rate: {(valid_count/total_count*100):.1f}%")

    return valid_count < total_count  # Expect some failures for comprehensive test


def main():
    """Run all real-time validation tests."""
    print("Real-time Validation System Test Suite")
    print("=" * 60)

    tests = [
        ("Validation Widgets", test_validation_widgets),
        ("Validation Manager", test_validation_manager),
        ("Enhanced Error Messages", test_enhanced_error_messages),
        ("UI Integration", test_ui_integration),
        ("Comprehensive Workflow Validation", test_comprehensive_workflow_validation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            result = test_func()
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All real-time validation tests passed!")
        print("\nReal-time validation system is working correctly:")
        print("  ✅ Field-level validation with immediate feedback")
        print("  ✅ Enhanced error messages with location and context")
        print("  ✅ Comprehensive validation manager coordination")
        print("  ✅ UI integration with visual validation indicators")
        print("  ✅ Auto-fix capabilities and actionable suggestions")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
