#!/usr/bin/env python3
"""
Test script for the Enhanced APIthon Validation System.

This script demonstrates all the new validation features including:
- Resource constraint validation (byte limits, serialization size, numeric ranges)
- Return value logic analysis (assignment vs expression detection)
- Reserved output_key handling (citation format validation)
- Real-time validation feedback
"""

import sys
from core_structures import ScriptStep, Workflow
from enhanced_apiton_validator import enhanced_apiton_validator, APIthonValidationResult


def test_resource_constraints():
    """Test resource constraint validation."""
    print("=" * 60)
    print("TESTING RESOURCE CONSTRAINTS")
    print("=" * 60)
    
    # Test 1: Code size validation
    print("\n1. Testing code size limits...")
    large_code = "# " + "x" * 5000  # Exceeds 4096 byte limit
    step = ScriptStep(code=large_code, output_key="test_result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Code size: {result.resource_usage.get('code_bytes', 0)} bytes")
    print(f"   Errors: {len(result.errors)}")
    if result.errors:
        print(f"   First error: {result.errors[0]}")
    
    # Test 2: String length validation
    print("\n2. Testing string length limits...")
    long_string_code = f'result = "{"x" * 5000}"'  # Long string literal
    step = ScriptStep(code=long_string_code, output_key="test_result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Errors: {len(result.errors)}")
    if result.errors:
        print(f"   First error: {result.errors[0]}")
    
    # Test 3: Numeric range validation
    print("\n3. Testing numeric value limits...")
    large_number_code = "result = 5000000000"  # Exceeds uint32 max
    step = ScriptStep(code=large_number_code, output_key="test_result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Errors: {len(result.errors)}")
    if result.errors:
        print(f"   First error: {result.errors[0]}")


def test_return_value_analysis():
    """Test return value logic analysis."""
    print("\n" + "=" * 60)
    print("TESTING RETURN VALUE ANALYSIS")
    print("=" * 60)
    
    # Test 1: Assignment as last line (common mistake)
    print("\n1. Testing assignment as last line...")
    assignment_code = """
user_name = data.user_info.name
result = {"greeting": f"Hello, {user_name}!"}
"""
    step = ScriptStep(code=assignment_code, output_key="test_result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Return analysis: {result.return_analysis}")
    print(f"   Warnings: {len(result.warnings)}")
    if result.warnings:
        print(f"   First warning: {result.warnings[0]}")
    print(f"   Suggestions: {result.suggestions}")
    
    # Test 2: In-place operation as last line
    print("\n2. Testing in-place operation as last line...")
    inplace_code = """
my_list = [1, 2, 3]
my_list.append(4)
"""
    step = ScriptStep(code=inplace_code, output_key="test_result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Warnings: {len(result.warnings)}")
    if result.warnings:
        print(f"   First warning: {result.warnings[0]}")
    print(f"   Suggestions: {result.suggestions}")
    
    # Test 3: Proper return statement
    print("\n3. Testing proper return statement...")
    proper_code = """
user_name = data.user_info.name
result = {"greeting": f"Hello, {user_name}!"}
return result
"""
    step = ScriptStep(code=proper_code, output_key="test_result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Return analysis: {result.return_analysis}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Is valid: {result.is_valid}")


def test_citation_compliance():
    """Test citation compliance for reserved output_key names."""
    print("\n" + "=" * 60)
    print("TESTING CITATION COMPLIANCE")
    print("=" * 60)
    
    # Test 1: output_key "result" with citation fields
    print("\n1. Testing 'result' output_key with citation fields...")
    citation_code = """
return {
    "id": "123",
    "friendly_id": "item_123",
    "title": "Sample Item",
    "url": "https://example.com/item/123",
    "snippet": "This is a sample item description"
}
"""
    step = ScriptStep(code=citation_code, output_key="result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Citation compliance: {result.citation_compliance}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Suggestions: {result.suggestions}")
    
    # Test 2: output_key "result" without citation fields
    print("\n2. Testing 'result' output_key without citation fields...")
    non_citation_code = """
return {
    "message": "Hello World",
    "status": "success"
}
"""
    step = ScriptStep(code=non_citation_code, output_key="result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Citation compliance: {result.citation_compliance}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Suggestions: {result.suggestions}")
    
    # Test 3: output_key "results" (multiple citations)
    print("\n3. Testing 'results' output_key...")
    step = ScriptStep(code="return []", output_key="results")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Citation compliance: {result.citation_compliance}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Suggestions: {result.suggestions}")
    
    # Test 4: Regular output_key (not reserved)
    print("\n4. Testing regular output_key...")
    step = ScriptStep(code="return {'data': 'value'}", output_key="my_data")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"   Citation compliance: {result.citation_compliance}")
    print(f"   Is reserved: {result.citation_compliance.get('is_reserved', False)}")


def test_comprehensive_validation():
    """Test comprehensive validation with multiple issues."""
    print("\n" + "=" * 60)
    print("TESTING COMPREHENSIVE VALIDATION")
    print("=" * 60)
    
    # Create a script with multiple validation issues
    problematic_code = """
import json  # Not allowed
user_name = data.user_info.name
_private_var = "secret"  # Not allowed
result = {"greeting": f"Hello, {user_name}!"}
# Missing return statement
"""
    
    step = ScriptStep(code=problematic_code, output_key="result")
    result = enhanced_apiton_validator.comprehensive_validate(step)
    
    print(f"\nComprehensive validation results:")
    print(f"   Is valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Suggestions: {len(result.suggestions)}")
    
    print(f"\nErrors:")
    for i, error in enumerate(result.errors, 1):
        print(f"   {i}. {error}")
    
    print(f"\nWarnings:")
    for i, warning in enumerate(result.warnings, 1):
        print(f"   {i}. {warning}")
    
    print(f"\nSuggestions:")
    for i, suggestion in enumerate(result.suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    print(f"\nResource usage: {result.resource_usage}")
    print(f"Return analysis: {result.return_analysis}")
    print(f"Citation compliance: {result.citation_compliance}")


def test_valid_script():
    """Test a completely valid APIthon script."""
    print("\n" + "=" * 60)
    print("TESTING VALID SCRIPT")
    print("=" * 60)
    
    valid_code = """
# Process user information
user_name = data.user_info.name
user_email = meta_info.user.email
processed_data = {
    "greeting": f"Hello, {user_name}!",
    "contact": user_email,
    "timestamp": "2024-01-01",
    "status": "processed"
}
return processed_data
"""
    
    step = ScriptStep(code=valid_code, output_key="processed_info")
    available_paths = {"data.user_info.name", "meta_info.user.email"}
    result = enhanced_apiton_validator.comprehensive_validate(step, available_paths)
    
    print(f"\nValid script validation results:")
    print(f"   Is valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Code size: {result.resource_usage.get('code_bytes', 0)} bytes")
    print(f"   Return type: {result.return_analysis.get('last_statement_type', 'Unknown')}")
    print(f"   Has explicit return: {result.return_analysis.get('has_explicit_return', False)}")


def main():
    """Run all enhanced APIthon validation tests."""
    print("Enhanced APIthon Validation System Test Suite")
    print("=" * 60)
    
    try:
        test_resource_constraints()
        test_return_value_analysis()
        test_citation_compliance()
        test_comprehensive_validation()
        test_valid_script()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
