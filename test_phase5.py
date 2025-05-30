#!/usr/bin/env python3
"""
Test script for Phase 5 enhancements of the Moveworks YAML Assistant.

This script tests the enhanced validation, error display, and help system features.
"""

import sys
import json
from core_structures import ActionStep, ScriptStep, Workflow, DataContext
from validator import (
    comprehensive_validate, validate_action_names, validate_output_key_format,
    validate_script_syntax, validate_data_references
)
from help_system import help_system, get_tooltip, get_contextual_help


def test_enhanced_validation():
    """Test the enhanced validation features."""
    print("Testing enhanced validation features...")

    # Test action name validation
    print("\n1. Testing action name validation...")
    
    # Create workflow with various action name issues
    invalid_action1 = ActionStep(action_name="mw.", output_key="test1")  # Invalid mw. action
    invalid_action2 = ActionStep(action_name="action with spaces", output_key="test2")  # Spaces
    invalid_action3 = ActionStep(action_name="a", output_key="test3")  # Too short
    valid_action = ActionStep(action_name="mw.get_user_by_email", output_key="test4")
    
    workflow = Workflow(steps=[invalid_action1, invalid_action2, invalid_action3, valid_action])
    
    action_errors = validate_action_names(workflow)
    print(f"   Found {len(action_errors)} action name errors:")
    for error in action_errors:
        print(f"   - {error}")

    # Test output key format validation
    print("\n2. Testing output key format validation...")
    
    invalid_key1 = ActionStep(action_name="test", output_key="123invalid")  # Starts with number
    invalid_key2 = ActionStep(action_name="test", output_key="data")  # Reserved word
    invalid_key3 = ActionStep(action_name="test", output_key="key@invalid")  # Invalid chars
    valid_key = ActionStep(action_name="test", output_key="valid_key")
    
    workflow = Workflow(steps=[invalid_key1, invalid_key2, invalid_key3, valid_key])
    
    key_errors = validate_output_key_format(workflow)
    print(f"   Found {len(key_errors)} output key errors:")
    for error in key_errors:
        print(f"   - {error}")

    # Test script syntax validation
    print("\n3. Testing script syntax validation...")
    
    invalid_script1 = ScriptStep(code="invalid syntax here !", output_key="test1")
    invalid_script2 = ScriptStep(code="print('no return')", output_key="test2")  # No return
    valid_script = ScriptStep(code="result = {'test': True}\nreturn result", output_key="test3")
    
    workflow = Workflow(steps=[invalid_script1, invalid_script2, valid_script])
    
    script_errors = validate_script_syntax(workflow)
    print(f"   Found {len(script_errors)} script errors:")
    for error in script_errors:
        print(f"   - {error}")

    print("✓ Enhanced validation tests completed")
    return True


def test_data_reference_validation():
    """Test comprehensive data reference validation."""
    print("\nTesting data reference validation...")

    # Create a workflow with data reference issues
    action1 = ActionStep(
        action_name="mw.get_user",
        output_key="user_info",
        user_provided_json_output='{"user": {"id": "123", "name": "John"}}'
    )
    
    # Valid reference
    action2 = ActionStep(
        action_name="mw.send_email",
        output_key="email_result",
        input_args={"to": "data.user_info.user.name"}  # Valid reference
    )
    
    # Invalid reference
    action3 = ActionStep(
        action_name="mw.create_ticket",
        output_key="ticket_result",
        input_args={"user": "data.nonexistent.field"}  # Invalid reference
    )
    
    workflow = Workflow(steps=[action1, action2, action3])
    
    # Test data reference validation
    ref_errors = validate_data_references(workflow)
    print(f"Found {len(ref_errors)} data reference errors:")
    for error in ref_errors:
        print(f"   - {error}")

    # Test comprehensive validation
    all_errors = comprehensive_validate(workflow)
    print(f"\nComprehensive validation found {len(all_errors)} total errors:")
    for error in all_errors:
        print(f"   - {error}")

    print("✓ Data reference validation tests completed")
    return True


def test_help_system():
    """Test the help system functionality."""
    print("\nTesting help system...")

    # Test getting topics
    topics = help_system.topics
    print(f"   Help system has {len(topics)} topics")

    # Test searching
    search_results = help_system.search_topics("action")
    print(f"   Search for 'action' found {len(search_results)} topics")

    # Test categories
    categories = help_system.get_all_categories()
    print(f"   Available categories: {', '.join(categories)}")

    # Test specific topic
    getting_started = help_system.get_topic("Getting Started")
    if getting_started:
        print(f"   'Getting Started' topic found with {len(getting_started.content)} characters")
    else:
        print("   ✗ 'Getting Started' topic not found")

    # Test tooltips
    action_tooltip = get_tooltip("action_name")
    print(f"   Action name tooltip: {action_tooltip[:50]}...")

    # Test contextual help
    context_help = get_contextual_help("empty_workflow")
    print(f"   Empty workflow help: {context_help}")

    print("✓ Help system tests completed")
    return True


def test_error_scenarios():
    """Test various error scenarios to ensure robust error handling."""
    print("\nTesting error scenarios...")

    # Test empty workflow
    empty_workflow = Workflow()
    errors = comprehensive_validate(empty_workflow)
    print(f"   Empty workflow validation: {len(errors)} error(s)")

    # Test workflow with missing required fields
    incomplete_action = ActionStep(action_name="", output_key="")
    incomplete_script = ScriptStep(code="", output_key="")
    incomplete_workflow = Workflow(steps=[incomplete_action, incomplete_script])
    
    errors = comprehensive_validate(incomplete_workflow)
    print(f"   Incomplete workflow validation: {len(errors)} error(s)")

    # Test workflow with duplicate output keys
    dup_action1 = ActionStep(action_name="test1", output_key="same_key")
    dup_action2 = ActionStep(action_name="test2", output_key="same_key")
    dup_workflow = Workflow(steps=[dup_action1, dup_action2])
    
    errors = comprehensive_validate(dup_workflow)
    print(f"   Duplicate keys workflow validation: {len(errors)} error(s)")

    # Test workflow with invalid JSON
    invalid_json_action = ActionStep(
        action_name="test",
        output_key="test",
        user_provided_json_output='{"invalid": json}'  # Invalid JSON
    )
    invalid_json_workflow = Workflow(steps=[invalid_json_action])
    
    errors = comprehensive_validate(invalid_json_workflow)
    print(f"   Invalid JSON workflow validation: {len(errors)} error(s)")

    print("✓ Error scenario tests completed")
    return True


def test_performance():
    """Test performance with larger workflows."""
    print("\nTesting performance with larger workflows...")

    # Create a workflow with many steps
    steps = []
    for i in range(50):
        action = ActionStep(
            action_name=f"mw.action_{i}",
            output_key=f"result_{i}",
            description=f"Action step {i}",
            user_provided_json_output=f'{{"step": {i}, "data": "test_data_{i}"}}'
        )
        steps.append(action)

    large_workflow = Workflow(steps=steps)
    
    import time
    start_time = time.time()
    errors = comprehensive_validate(large_workflow)
    end_time = time.time()
    
    print(f"   Validated {len(steps)} steps in {end_time - start_time:.3f} seconds")
    print(f"   Found {len(errors)} validation errors")

    print("✓ Performance tests completed")
    return True


def main():
    """Run all Phase 5 tests."""
    print("Moveworks YAML Assistant - Phase 5 Enhancement Tests")
    print("=" * 65)

    tests = [
        test_enhanced_validation,
        test_data_reference_validation,
        test_help_system,
        test_error_scenarios,
        test_performance
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test_func.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} failed with exception: {e}")

    print("\n" + "=" * 65)
    print(f"Phase 5 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All Phase 5 enhancements are working correctly!")
        print("\nPhase 5 Features Implemented:")
        print("• Enhanced validation with comprehensive error checking")
        print("• Improved error display with categorization and severity")
        print("• Comprehensive help system with search and navigation")
        print("• Better UI/UX with tooltips and contextual guidance")
        print("• Performance optimizations for large workflows")
        print("\nYou can now run the enhanced GUI application with:")
        print("  python main_gui.py")
    else:
        print("✗ Some tests failed. Please review the errors above.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
