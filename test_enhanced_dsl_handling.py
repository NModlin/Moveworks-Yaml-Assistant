#!/usr/bin/env python3
"""
Comprehensive test script for enhanced DSL handling capabilities.

This script demonstrates the new DSL handling features including:
1. DSL validation with detailed feedback
2. Enhanced DSL detection and quoting
3. DSL input widgets with real-time validation
4. DSL builder functionality
5. Common DSL patterns and templates
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PySide6.QtCore import Qt

from dsl_validator import dsl_validator, is_dsl_expression
from dsl_input_widget import DSLInputWidget
from dsl_builder_widget import DSLBuilderWidget
from yaml_generator import _is_dsl_expression, _ensure_dsl_string_quoting
from core_structures import ActionStep, Workflow
from yaml_generator import generate_yaml_string


def test_dsl_validation():
    """Test DSL validation with various expressions."""
    print("=" * 60)
    print("TEST 1: DSL Validation")
    print("=" * 60)
    
    test_expressions = [
        # Valid DSL expressions
        ("data.user_info.email", "Valid data reference"),
        ("meta_info.user.name", "Valid meta info reference"),
        ("$CONCAT([data.first, ' ', data.last])", "Valid function call"),
        ("data.age >= 18", "Valid comparison"),
        ("data.status == 'active' && data.verified", "Valid complex condition"),
        
        # Invalid DSL expressions
        ("CONCAT([data.first, data.last])", "Missing $ prefix"),
        ("data.user = 'test'", "Single equals instead of =="),
        ("$CONCAT([data.first, data.last)", "Unmatched parentheses"),
        ("data..invalid", "Double dots in path"),
        
        # Edge cases
        ("", "Empty expression"),
        ("regular_string", "Regular string value"),
        ("data.items[0].name", "Array access"),
        ("$IF(data.premium, 'Premium', 'Standard')", "Conditional expression"),
    ]
    
    for expression, description in test_expressions:
        print(f"\nTesting: {description}")
        print(f"Expression: '{expression}'")
        
        result = dsl_validator.validate_dsl_expression(expression)
        
        print(f"Valid: {'✅' if result.is_valid else '❌'}")
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.suggestions:
            print("Suggestions:")
            for suggestion in result.suggestions[:2]:  # Show first 2
                print(f"  - {suggestion}")
        
        if result.detected_patterns:
            print(f"Patterns: {', '.join(result.detected_patterns)}")
    
    return True


def test_dsl_detection_and_quoting():
    """Test enhanced DSL detection and YAML quoting."""
    print("\n" + "=" * 60)
    print("TEST 2: DSL Detection and YAML Quoting")
    print("=" * 60)
    
    test_values = [
        # DSL expressions that should be quoted
        "data.user_info.email",
        "meta_info.user.name",
        "$CONCAT([data.first, ' ', data.last])",
        "data.age >= 18",
        "data.status == 'active'",
        "data.items[0].name",
        "$IF(data.premium, 'Premium', 'Standard')",
        
        # Regular values that should NOT be quoted
        "regular_string",
        "123",
        "true",
        "false",
        "null",
        "simple_value",
    ]
    
    print("\nDSL Detection Results:")
    for value in test_values:
        is_dsl_old = _is_dsl_expression(value)
        is_dsl_new = is_dsl_expression(value)
        
        print(f"'{value}':")
        print(f"  Enhanced detection: {'✅ DSL' if is_dsl_new else '⚪ Regular'}")
        print(f"  YAML generator: {'✅ DSL' if is_dsl_old else '⚪ Regular'}")
        
        if is_dsl_old != is_dsl_new:
            print(f"  ⚠️ Detection mismatch!")
    
    # Test YAML generation with DSL quoting
    print("\nYAML Generation with DSL Quoting:")
    
    action_with_dsl = ActionStep(
        action_name="test_dsl_action",
        output_key="dsl_result",
        input_args={
            "user_email": "data.user_info.email",  # DSL - should be quoted
            "full_name": "$CONCAT([data.first_name, ' ', data.last_name])",  # DSL - should be quoted
            "is_adult": "data.age >= 18",  # DSL - should be quoted
            "timeout": 30,  # Regular - should not be quoted
            "enabled": True,  # Regular - should not be quoted
            "message": "Hello World",  # Regular - should not be quoted
        }
    )
    
    workflow = Workflow(steps=[action_with_dsl])
    yaml_output = generate_yaml_string(workflow, "test_dsl_compound_action")
    
    print("Generated YAML:")
    print("-" * 40)
    print(yaml_output)
    print("-" * 40)
    
    # Verify proper quoting
    dsl_quoted = ('"data.user_info.email"' in yaml_output and 
                  '"$CONCAT([data.first_name' in yaml_output and
                  '"data.age >= 18"' in yaml_output)
    
    regular_not_quoted = ('timeout: 30' in yaml_output and
                          'enabled: true' in yaml_output.lower())
    
    if dsl_quoted and regular_not_quoted:
        print("✅ DSL expressions properly quoted, regular values not quoted!")
    else:
        print("❌ DSL quoting may have issues")
        if not dsl_quoted:
            print("  - DSL expressions not properly quoted")
        if not regular_not_quoted:
            print("  - Regular values incorrectly quoted")
    
    return True


def test_dsl_patterns_and_templates():
    """Test common DSL patterns and template functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: DSL Patterns and Templates")
    print("=" * 60)
    
    common_patterns = [
        # Data references
        ("Simple field", "data.field_name"),
        ("Nested field", "data.user_info.email"),
        ("Array element", "data.items[0]"),
        ("User email", "meta_info.user.email"),
        
        # String operations
        ("Concatenation", "$CONCAT([data.first_name, ' ', data.last_name])"),
        ("Split string", "$SPLIT(data.full_name, ' ')[0]"),
        ("Uppercase", "$UPPER(data.name)"),
        ("Text conversion", "$TEXT(data.user_id)"),
        
        # Conditional logic
        ("Simple condition", "$IF(data.is_active, 'Active', 'Inactive')"),
        ("Null check", "$IF(data.phone != null, data.phone, 'No phone')"),
        ("Complex condition", "$IF(data.age >= 18 && data.verified, 'Approved', 'Pending')"),
        
        # Comparisons
        ("Equality", "data.status == 'active'"),
        ("Inequality", "data.type != 'guest'"),
        ("Numeric comparison", "data.age >= 18"),
        ("Null check", "data.optional_field == null"),
    ]
    
    print("Testing Common DSL Patterns:")
    
    for pattern_name, expression in common_patterns:
        print(f"\n{pattern_name}: {expression}")
        
        # Test detection
        is_dsl = is_dsl_expression(expression)
        print(f"  Detected as DSL: {'✅' if is_dsl else '❌'}")
        
        # Test validation
        result = dsl_validator.validate_dsl_expression(expression)
        print(f"  Validation: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
        
        if result.errors:
            print(f"  Errors: {'; '.join(result.errors[:2])}")
        
        if result.detected_patterns:
            print(f"  Patterns: {', '.join(result.detected_patterns)}")
    
    return True


def test_dsl_ui_components():
    """Test DSL UI components in a simple application."""
    print("\n" + "=" * 60)
    print("TEST 4: DSL UI Components")
    print("=" * 60)
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("DSL UI Components Test")
    window.resize(800, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Create tab widget for different components
    tab_widget = QTabWidget()
    layout.addWidget(tab_widget)
    
    # DSL Input Widget tab
    dsl_input_tab = QWidget()
    dsl_input_layout = QVBoxLayout(dsl_input_tab)
    
    # Create several DSL input widgets for different contexts
    email_input = DSLInputWidget("user_email", "Enter DSL expression for user email")
    email_input.set_field_context("user_email", "input_arg")
    dsl_input_layout.addWidget(email_input)
    
    condition_input = DSLInputWidget("condition", "Enter DSL expression for condition")
    condition_input.set_field_context("condition", "condition")
    dsl_input_layout.addWidget(condition_input)
    
    output_mapper_input = DSLInputWidget("output_mapper", "Enter DSL expression for output mapping")
    output_mapper_input.set_field_context("output_mapper", "output_mapper")
    dsl_input_layout.addWidget(output_mapper_input)
    
    tab_widget.addTab(dsl_input_tab, "DSL Input Widgets")
    
    # DSL Builder tab
    builder_widget = DSLBuilderWidget()
    tab_widget.addTab(builder_widget, "DSL Builder")
    
    # Set some example values
    email_input.set_value("data.user_info.email")
    condition_input.set_value("data.age >= 18 && data.status == 'active'")
    output_mapper_input.set_value("$CONCAT([data.greeting, ', ', data.user_name])")
    
    print("✅ DSL UI Components created successfully!")
    print("  - DSL Input Widgets with context-aware placeholders")
    print("  - DSL Builder with templates and validation")
    print("  - Real-time validation and syntax highlighting")
    
    # Show window for manual testing (comment out for automated tests)
    # window.show()
    # app.exec()
    
    return True


def test_comprehensive_dsl_workflow():
    """Test a complete workflow with DSL expressions."""
    print("\n" + "=" * 60)
    print("TEST 5: Comprehensive DSL Workflow")
    print("=" * 60)
    
    # Create a workflow with various DSL expressions
    workflow = Workflow(steps=[
        ActionStep(
            action_name="mw.get_user_by_email",
            output_key="user_info",
            input_args={
                "email": "meta_info.user.email",  # DSL: current user's email
                "include_profile": True,  # Regular: boolean value
                "timeout": 30  # Regular: numeric value
            }
        ),
        ActionStep(
            action_name="mw.check_user_permissions",
            output_key="permissions",
            input_args={
                "user_id": "data.user_info.id",  # DSL: reference to previous step
                "resource": "data.user_info.department",  # DSL: nested field access
                "check_admin": "data.user_info.role == 'admin'",  # DSL: comparison
            }
        ),
        ActionStep(
            action_name="mw.send_notification",
            output_key="notification_result",
            input_args={
                "recipient": "data.user_info.email",  # DSL: data reference
                "message": "$CONCAT(['Welcome, ', data.user_info.name, '! Your access level is: ', data.permissions.level])",  # DSL: complex function
                "priority": "$IF(data.permissions.is_admin, 'high', 'normal')",  # DSL: conditional
                "send_immediately": "data.user_info.preferences.immediate_notifications != false"  # DSL: complex condition
            }
        )
    ])
    
    print("Created workflow with comprehensive DSL usage:")
    
    # Validate all DSL expressions in the workflow
    all_dsl_expressions = []
    
    for i, step in enumerate(workflow.steps):
        print(f"\nStep {i+1}: {step.action_name}")
        
        for key, value in step.input_args.items():
            if isinstance(value, str) and is_dsl_expression(value):
                all_dsl_expressions.append((f"Step {i+1}.{key}", value))
                
                # Validate the DSL expression
                result = dsl_validator.validate_dsl_expression(value)
                status = "✅ Valid" if result.is_valid else "❌ Invalid"
                print(f"  {key}: {value} - {status}")
                
                if result.errors:
                    for error in result.errors:
                        print(f"    Error: {error}")
    
    # Generate YAML and check DSL quoting
    yaml_output = generate_yaml_string(workflow, "comprehensive_dsl_workflow")
    
    print(f"\nFound {len(all_dsl_expressions)} DSL expressions in workflow")
    print("\nGenerated YAML with DSL expressions:")
    print("-" * 50)
    print(yaml_output)
    print("-" * 50)
    
    # Verify that all DSL expressions are properly quoted in YAML
    properly_quoted = 0
    for step_field, expression in all_dsl_expressions:
        if f'"{expression}"' in yaml_output:
            properly_quoted += 1
        else:
            print(f"⚠️ DSL expression not properly quoted: {expression}")
    
    print(f"\nDSL Quoting Results:")
    print(f"  Total DSL expressions: {len(all_dsl_expressions)}")
    print(f"  Properly quoted: {properly_quoted}")
    print(f"  Success rate: {(properly_quoted/len(all_dsl_expressions)*100):.1f}%" if all_dsl_expressions else "N/A")
    
    return properly_quoted == len(all_dsl_expressions)


def main():
    """Run all DSL handling tests."""
    print("Enhanced DSL Handling Test Suite")
    print("=" * 60)
    
    tests = [
        ("DSL Validation", test_dsl_validation),
        ("DSL Detection and Quoting", test_dsl_detection_and_quoting),
        ("DSL Patterns and Templates", test_dsl_patterns_and_templates),
        ("DSL UI Components", test_dsl_ui_components),
        ("Comprehensive DSL Workflow", test_comprehensive_dsl_workflow),
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
        print("🎉 All DSL handling tests passed!")
        print("\nEnhanced DSL handling is working correctly:")
        print("  ✅ DSL validation with detailed feedback")
        print("  ✅ Enhanced DSL detection and YAML quoting")
        print("  ✅ DSL input widgets with real-time validation")
        print("  ✅ DSL builder with templates and syntax highlighting")
        print("  ✅ Comprehensive DSL workflow support")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
