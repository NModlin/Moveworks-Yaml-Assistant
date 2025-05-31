#!/usr/bin/env python3
"""
Demonstration of APIthon Script Field Compliance Implementation.

This script showcases the comprehensive APIthon script field compliance
features implemented for the Moveworks YAML Assistant.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_structures import ScriptStep, Workflow
from compliance_validator import compliance_validator
from yaml_generator import generate_yaml_string


def demo_field_naming_compliance():
    """Demonstrate code field naming compliance."""
    print("🔧 Code Field Naming Compliance")
    print("-" * 50)
    
    # Valid script with proper code field
    valid_script = ScriptStep(
        code="user_name = data.user_info.name\nreturn {'greeting': f'Hello, {user_name}!'}",
        output_key="greeting_result"
    )
    
    workflow = Workflow(steps=[valid_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"✅ Valid script compliance: {result.is_valid}")
    if result.mandatory_field_errors:
        print(f"   Mandatory field errors: {len(result.mandatory_field_errors)}")
    if result.field_naming_errors:
        print(f"   Field naming errors: {len(result.field_naming_errors)}")
    
    print()


def demo_byte_limit_validation():
    """Demonstrate byte limit validation."""
    print("📏 Byte Limit Validation")
    print("-" * 50)
    
    # Script approaching byte limit
    approaching_limit_code = "# " + "x" * 3200 + "\nreturn {'status': 'approaching_limit'}"
    approaching_script = ScriptStep(
        code=approaching_limit_code,
        output_key="approaching_result"
    )
    
    workflow = Workflow(steps=[approaching_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"⚠️  Script approaching limit: {len(approaching_limit_code.encode('utf-8'))} bytes")
    if result.warnings:
        print(f"   Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            if "byte" in warning.lower():
                print(f"   📊 {warning}")
    
    # Script exceeding byte limit
    exceeding_limit_code = "# " + "x" * 4100 + "\nreturn {'status': 'exceeding_limit'}"
    exceeding_script = ScriptStep(
        code=exceeding_limit_code,
        output_key="exceeding_result"
    )
    
    workflow = Workflow(steps=[exceeding_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"❌ Script exceeding limit: {len(exceeding_limit_code.encode('utf-8'))} bytes")
    if result.apiton_errors:
        error_count = sum(1 for error in result.apiton_errors if "byte" in error.lower())
        print(f"   Byte limit errors: {error_count}")
    
    print()


def demo_private_method_detection():
    """Demonstrate private method detection."""
    print("🔒 Private Method Detection")
    print("-" * 50)
    
    # Script with private identifiers
    private_script = ScriptStep(
        code="_private_var = data.user_info\n_helper = lambda x: x.upper()\nreturn _helper(_private_var.name)",
        output_key="private_result"
    )
    
    workflow = Workflow(steps=[private_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"❌ Script with private identifiers: {result.is_valid}")
    if result.apiton_errors:
        private_errors = [error for error in result.apiton_errors if "private" in error.lower()]
        print(f"   Private identifier errors: {len(private_errors)}")
        for error in private_errors[:2]:  # Show first 2 errors
            if "Private identifiers not allowed" in error:
                print(f"   🚫 {error}")
    
    # Script without private identifiers
    public_script = ScriptStep(
        code="public_var = data.user_info\nhelper = lambda x: x.upper()\nreturn helper(public_var.name)",
        output_key="public_result"
    )
    
    workflow = Workflow(steps=[public_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"✅ Script without private identifiers: {result.is_valid}")
    
    print()


def demo_return_logic_validation():
    """Demonstrate return statement logic validation."""
    print("🔄 Return Logic Validation")
    print("-" * 50)
    
    # Script with missing return statement
    assignment_script = ScriptStep(
        code="user_name = data.user_info.name\nresult = {'greeting': f'Hello, {user_name}!'}",
        output_key="assignment_result"
    )
    
    workflow = Workflow(steps=[assignment_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"⚠️  Script with assignment as last line: {result.is_valid}")
    if result.suggestions:
        return_suggestions = [s for s in result.suggestions if "return" in s.lower()]
        print(f"   Return statement suggestions: {len(return_suggestions)}")
        for suggestion in return_suggestions[:1]:  # Show first suggestion
            print(f"   💡 {suggestion}")
    
    # Script with proper return statement
    return_script = ScriptStep(
        code="user_name = data.user_info.name\nresult = {'greeting': f'Hello, {user_name}!'}\nreturn result",
        output_key="return_result"
    )
    
    workflow = Workflow(steps=[return_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"✅ Script with proper return statement: {result.is_valid}")
    
    print()


def demo_yaml_generation():
    """Demonstrate YAML generation with literal block scalars."""
    print("📄 YAML Generation with Literal Block Scalars")
    print("-" * 50)
    
    # Multi-line script for literal block scalar demonstration
    multiline_script = ScriptStep(
        code="""# Process user information
user_name = data.user_info.name
user_email = meta_info.user.email

# Create response object
response = {
    'greeting': f'Hello, {user_name}!',
    'email': user_email,
    'timestamp': 'now',
    'status': 'processed'
}

return response""",
        output_key="processed_response",
        description="Process user information and create response"
    )
    
    workflow = Workflow(steps=[multiline_script])
    
    try:
        yaml_output = generate_yaml_string(workflow, "demo_multiline_script")
        print("✅ YAML generated successfully with literal block scalar:")
        print()
        
        # Show the YAML output with proper formatting
        lines = yaml_output.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            print(f"   {line}")
        
        if len(lines) > 20:
            print(f"   ... ({len(lines) - 20} more lines)")
            
    except Exception as e:
        print(f"❌ Error generating YAML: {e}")
    
    print()


def demo_comprehensive_validation():
    """Demonstrate comprehensive validation with multiple issues."""
    print("🔍 Comprehensive Validation Example")
    print("-" * 50)
    
    # Script with multiple compliance issues
    problematic_script = ScriptStep(
        code="_private_data = data.user_info\n" + "# " + "x" * 4000 + "\nresult = _private_data.name",
        output_key="problematic_result"
    )
    
    workflow = Workflow(steps=[problematic_script])
    result = compliance_validator.validate_workflow_compliance(workflow, "demo_workflow")
    
    print(f"❌ Script with multiple issues: {result.is_valid}")
    print(f"   📊 Total errors: {len(result.errors + result.mandatory_field_errors + result.field_naming_errors + result.apiton_errors)}")
    print(f"   ⚠️  Total warnings: {len(result.warnings)}")
    print(f"   💡 Total suggestions: {len(result.suggestions)}")
    
    # Show summary of issue types
    issue_types = []
    if any("private" in error.lower() for error in result.apiton_errors):
        issue_types.append("Private identifiers")
    if any("byte" in error.lower() for error in result.apiton_errors):
        issue_types.append("Byte limit exceeded")
    if any("return" in suggestion.lower() for suggestion in result.suggestions):
        issue_types.append("Missing return statement")
    
    print(f"   🚨 Issue types detected: {', '.join(issue_types)}")
    
    print()


def main():
    """Run the APIthon script compliance demonstration."""
    print("=" * 60)
    print("🚀 APIthon Script Field Compliance Demonstration")
    print("=" * 60)
    print()
    
    try:
        demo_field_naming_compliance()
        demo_byte_limit_validation()
        demo_private_method_detection()
        demo_return_logic_validation()
        demo_yaml_generation()
        demo_comprehensive_validation()
        
        print("=" * 60)
        print("✅ All demonstrations completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
