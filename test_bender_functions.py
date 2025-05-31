#!/usr/bin/env python3
"""
Test script for Bender function support in the Moveworks YAML Assistant.

This script demonstrates the enhanced Bender function validation and builder capabilities.
"""

import sys
from dsl_validator import dsl_validator
from enhanced_apiton_validator import enhanced_apiton_validator
from core_structures import ScriptStep


def test_bender_function_validation():
    """Test Bender function validation capabilities."""
    print("=" * 80)
    print("TESTING BENDER FUNCTION VALIDATION")
    print("=" * 80)
    
    test_cases = [
        # Valid Bender functions
        ("$MAP(data.users, {\"id\": \"item.id\", \"name\": \"item.name\"})", "Valid MAP function"),
        ("$FILTER(data.items, item.status == 'active')", "Valid FILTER function"),
        ("$CONDITIONAL(data.age >= 18, 'Adult', 'Minor')", "Valid CONDITIONAL function"),
        ("$LOOKUP(data.roles, data.user_id, 'default')", "Valid LOOKUP function"),
        ("$CONCAT([data.first_name, ' ', data.last_name])", "Valid CONCAT function"),
        
        # Invalid Bender functions
        ("$MAP(data.users)", "Invalid MAP - missing converter"),
        ("$FILTER(data.items)", "Invalid FILTER - missing condition"),
        ("$CONDITIONAL(data.age >= 18, 'Adult')", "Invalid CONDITIONAL - missing on_fail"),
        ("$LOOKUP(data.roles)", "Invalid LOOKUP - missing key"),
        ("$MAP(data.users, converter, extra, toomany)", "Invalid MAP - too many arguments"),
        
        # Mixed expressions
        ("data.user_name + ' - ' + $CONDITIONAL(data.is_admin, 'Admin', 'User')", "Mixed DSL with Bender"),
        ("$FILTER(data.users, item.age >= 18 && item.status == 'active')", "Complex FILTER condition"),
    ]
    
    for expression, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"Expression: {expression}")
        
        result = dsl_validator.validate_dsl_expression(expression)
        
        if result.is_valid:
            print("✅ VALID")
            if result.suggestions:
                print("💡 Suggestions:")
                for suggestion in result.suggestions:
                    print(f"   - {suggestion}")
        else:
            print("❌ INVALID")
            print("🚨 Errors:")
            for error in result.errors:
                print(f"   - {error}")
            if result.warnings:
                print("⚠️ Warnings:")
                for warning in result.warnings:
                    print(f"   - {warning}")
        
        print("-" * 60)


def test_enhanced_apiton_validation():
    """Test enhanced APIthon validation with resource limits."""
    print("\n" + "=" * 80)
    print("TESTING ENHANCED APITON VALIDATION")
    print("=" * 80)
    
    test_scripts = [
        # Normal script
        ("result = data.user_info['name'].upper()", "Normal script"),
        
        # Large script approaching byte limit
        ("# " + "x" * 4000 + "\nresult = 'test'", "Large script approaching byte limit"),
        
        # Script with large string literal
        ("large_string = '" + "x" * 5000 + "'\nresult = large_string", "Script with large string"),
        
        # Script with large numeric value
        ("big_number = 5000000000\nresult = big_number", "Script with large numeric value"),
        
        # Script with large list
        ("big_list = " + str(list(range(1000))) + "\nresult = big_list", "Script with large list"),
        
        # Script with import statement
        ("import json\nresult = json.dumps(data.user_info)", "Script with import statement"),
        
        # Script with private method
        ("def _private_method():\n    return 'secret'\nresult = _private_method()", "Script with private method"),
    ]
    
    for code, description in test_scripts:
        print(f"\nTesting: {description}")
        print(f"Code length: {len(code)} characters, {len(code.encode('utf-8'))} bytes")
        
        step = ScriptStep(code=code, output_key="test_result")
        result = enhanced_apiton_validator.comprehensive_validate(step)
        
        if result.is_valid:
            print("✅ VALID")
        else:
            print("❌ INVALID")
        
        # Show resource usage
        if result.resource_usage:
            print("📊 Resource Usage:")
            for key, value in result.resource_usage.items():
                print(f"   {key}: {value}")
        
        # Show errors
        if result.errors:
            print("🚨 Errors:")
            for error in result.errors:
                if hasattr(error, 'message'):
                    print(f"   - {error.message}")
                else:
                    print(f"   - {error}")
        
        # Show warnings
        if result.warnings:
            print("⚠️ Warnings:")
            for warning in result.warnings:
                if hasattr(warning, 'message'):
                    print(f"   - {warning.message}")
                else:
                    print(f"   - {warning}")
        
        print("-" * 60)


def test_bender_function_examples():
    """Show examples of Bender function usage."""
    print("\n" + "=" * 80)
    print("BENDER FUNCTION EXAMPLES")
    print("=" * 80)
    
    examples = {
        "MAP Function": [
            "$MAP(data.users, {\"id\": \"item.id\", \"display_name\": \"$CONCAT([item.first_name, ' ', item.last_name])\"})",
            "$MAP(data.items, item.name)",
            "$MAP(data.products, {\"name\": \"item.title\", \"price\": \"item.cost\"}, {\"currency\": \"USD\"})"
        ],
        "FILTER Function": [
            "$FILTER(data.users, item.status == 'active')",
            "$FILTER(data.items, item.price > 100)",
            "$FILTER(data.employees, item.department == 'Engineering' && item.level >= 3)"
        ],
        "CONDITIONAL Function": [
            "$CONDITIONAL(data.user.age >= 18, 'Adult', 'Minor')",
            "$CONDITIONAL(data.is_premium, 'Premium User', 'Standard User')",
            "$CONDITIONAL(data.score >= 80, 'Pass', 'Fail')"
        ],
        "LOOKUP Function": [
            "$LOOKUP(data.user_roles, data.user_id)",
            "$LOOKUP(data.department_mapping, data.dept_code, 'Unknown')",
            "$LOOKUP(data.config, 'max_retries', 3)"
        ],
        "CONCAT Function": [
            "$CONCAT([data.first_name, ' ', data.last_name])",
            "$CONCAT(data.address_parts, ', ')",
            "$CONCAT(['Hello, ', data.user_name, '!'])"
        ]
    }
    
    for category, function_examples in examples.items():
        print(f"\n{category}:")
        print("=" * len(category))
        
        for i, example in enumerate(function_examples, 1):
            print(f"{i}. {example}")
            
            # Validate each example
            result = dsl_validator.validate_dsl_expression(example)
            if result.is_valid:
                print("   ✅ Valid")
            else:
                print("   ❌ Invalid:")
                for error in result.errors:
                    print(f"      - {error}")
        
        print()


def main():
    """Run all Bender function tests."""
    print("🔧 MOVEWORKS YAML ASSISTANT - BENDER FUNCTION TESTING")
    print("=" * 80)
    
    try:
        # Test Bender function validation
        test_bender_function_validation()
        
        # Test enhanced APIthon validation
        test_enhanced_apiton_validation()
        
        # Show Bender function examples
        test_bender_function_examples()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
