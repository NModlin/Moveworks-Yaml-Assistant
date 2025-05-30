"""
Demo script showing how to use the enhanced features programmatically.

This script demonstrates the key functionality of each enhanced feature
without requiring the GUI.
"""

import json
from core_structures import Workflow, ActionStep, ScriptStep


def demo_template_library():
    """Demonstrate the template library functionality."""
    print("=" * 50)
    print("TEMPLATE LIBRARY DEMO")
    print("=" * 50)
    
    from template_library import template_library
    
    # Show available templates
    print(f"Available templates: {len(template_library.templates)}")
    for template_id, template in template_library.templates.items():
        print(f"  - {template.name} ({template.category}, {template.difficulty})")
    
    print()
    
    # Get a specific template
    user_template = template_library.get_template("user_lookup")
    if user_template:
        print(f"Template: {user_template.name}")
        print(f"Description: {user_template.description}")
        print(f"Steps: {len(user_template.workflow.steps)}")
        
        for i, step in enumerate(user_template.workflow.steps):
            step_type = type(step).__name__
            description = getattr(step, 'description', 'No description')
            print(f"  Step {i+1}: {step_type} - {description}")
    
    print()
    
    # Search templates
    search_results = template_library.search_templates("user")
    print(f"Search for 'user' found {len(search_results)} templates:")
    for template in search_results:
        print(f"  - {template.name}")
    
    print()


def demo_contextual_examples():
    """Demonstrate the contextual examples system."""
    print("=" * 50)
    print("CONTEXTUAL EXAMPLES DEMO")
    print("=" * 50)
    
    from contextual_examples import examples_database
    
    # Show available examples
    print(f"Total examples: {len(examples_database.examples)}")
    
    # Show examples by context
    contexts = ["action_step", "script_step", "data_mapping", "best_practices"]
    for context in contexts:
        examples = examples_database.get_examples_by_context(context)
        print(f"\n{context.replace('_', ' ').title()} examples: {len(examples)}")
        for example in examples[:2]:  # Show first 2
            print(f"  - {example.title} ({example.difficulty})")
    
    # Show example details
    action_examples = examples_database.get_examples_by_context("action_step")
    if action_examples:
        example = action_examples[0]
        print(f"\nExample Details: {example.title}")
        print(f"Description: {example.description}")
        print(f"Code preview:")
        print("  " + "\n  ".join(example.code.split('\n')[:3]) + "...")
    
    print()


def demo_enhanced_validator():
    """Demonstrate the enhanced validator with fix suggestions."""
    print("=" * 50)
    print("ENHANCED VALIDATOR DEMO")
    print("=" * 50)
    
    from enhanced_validator import enhanced_validator
    
    # Create a workflow with various issues
    workflow = Workflow()
    
    # Add steps with different types of errors
    bad_action = ActionStep(
        action_name="",  # Missing action name
        output_key="",   # Missing output key
        description="Action with missing fields"
    )
    workflow.steps.append(bad_action)
    
    duplicate_action = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="result",  # Generic output key
        description="Action with generic output key"
    )
    workflow.steps.append(duplicate_action)
    
    bad_script = ScriptStep(
        code="",  # Missing code
        output_key="result",  # Duplicate output key
        description="Script with missing code"
    )
    workflow.steps.append(bad_script)
    
    script_no_return = ScriptStep(
        code="x = 1 + 1",  # No return statement
        output_key="calculation",
        description="Script without return statement"
    )
    workflow.steps.append(script_no_return)
    
    # Run enhanced validation
    errors = enhanced_validator.validate_with_suggestions(workflow)
    
    print(f"Found {len(errors)} validation issues:")
    print()
    
    # Show errors with suggestions
    for i, error in enumerate(errors[:5], 1):  # Show first 5
        print(f"{i}. {error.message}")
        print(f"   Severity: {error.severity}")
        
        if error.fix_suggestions:
            print(f"   Suggestions:")
            for suggestion in error.fix_suggestions[:2]:  # Show first 2
                print(f"     • {suggestion}")
        
        if error.quick_fixes:
            print(f"   Quick fixes available: {len(error.quick_fixes)}")
        
        print()
    
    # Show validation summary
    summary = enhanced_validator.get_validation_summary(errors)
    print("Validation Summary:")
    print(f"  Total issues: {summary['total_issues']}")
    print(f"  Errors: {summary['errors']}")
    print(f"  Warnings: {summary['warnings']}")
    print(f"  Info: {summary['info']}")
    print(f"  Fixable: {summary['fixable']}")
    print(f"  Ready for export: {summary['ready_for_export']}")
    
    print()


def demo_json_path_extraction():
    """Demonstrate JSON path extraction logic."""
    print("=" * 50)
    print("JSON PATH EXTRACTION DEMO")
    print("=" * 50)
    
    # Sample JSON data structure
    sample_data = {
        "user_info": {
            "user": {
                "id": "12345",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "manager": {
                    "id": "67890",
                    "name": "Jane Smith"
                }
            },
            "permissions": ["read", "write"],
            "active": True
        },
        "api_response": {
            "status": "success",
            "data": {
                "items": [
                    {"id": 1, "name": "Item 1", "value": 100},
                    {"id": 2, "name": "Item 2", "value": 200}
                ]
            }
        }
    }
    
    # Test various path extractions
    test_paths = [
        "data.user_info.user.name",
        "data.user_info.user.email",
        "data.user_info.user.manager.name",
        "data.user_info.permissions[0]",
        "data.api_response.data.items[1].name",
        "data.api_response.status"
    ]
    
    def extract_value_by_path(data, path):
        """Extract value from data using dot notation path."""
        if path.startswith('data.'):
            path = path[5:]
        
        parts = []
        current_part = ""
        in_brackets = False
        
        # Parse path with array indices
        for char in path:
            if char == '[':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_brackets = True
            elif char == ']':
                if in_brackets and current_part:
                    parts.append(int(current_part))
                    current_part = ""
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part)
        
        # Navigate through the data
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
            else:
                raise ValueError(f"Cannot navigate to {part} in {type(current)}")
        
        return current
    
    print("Testing JSON path extraction:")
    for path in test_paths:
        try:
            value = extract_value_by_path(sample_data, path)
            print(f"  {path} → {value}")
        except Exception as e:
            print(f"  {path} → ERROR: {e}")
    
    print()


def demo_tutorial_structure():
    """Demonstrate tutorial system structure."""
    print("=" * 50)
    print("TUTORIAL SYSTEM DEMO")
    print("=" * 50)
    
    from tutorial_system import TutorialStep
    
    # Create sample tutorial steps
    steps = [
        TutorialStep(
            title="Welcome",
            description="Welcome to the Moveworks YAML Assistant tutorial!",
            auto_advance=False
        ),
        TutorialStep(
            title="Add Action Step",
            description="Click the 'Add Action Step' button to add your first action.",
            target_element="add_action_button",
            action="click"
        ),
        TutorialStep(
            title="Configure Action",
            description="Enter the action name and output key for your step.",
            target_element="action_config_panel"
        ),
        TutorialStep(
            title="Complete",
            description="Congratulations! You've completed the tutorial.",
            auto_advance=False
        )
    ]
    
    print(f"Sample tutorial with {len(steps)} steps:")
    for i, step in enumerate(steps, 1):
        print(f"  Step {i}: {step.title}")
        print(f"    Description: {step.description}")
        if step.target_element:
            print(f"    Target: {step.target_element}")
        if step.action:
            print(f"    Action: {step.action}")
        print(f"    Auto-advance: {step.auto_advance}")
        print()


def main():
    """Run all demos."""
    print("MOVEWORKS YAML ASSISTANT - ENHANCED FEATURES DEMO")
    print("=" * 60)
    print()
    
    # Run all demos
    demo_template_library()
    demo_contextual_examples()
    demo_enhanced_validator()
    demo_json_path_extraction()
    demo_tutorial_structure()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print()
    print("To see these features in action, run the GUI application:")
    print("  python main_gui.py")
    print()
    print("Or run the test suite:")
    print("  python test_enhanced_features.py")


if __name__ == "__main__":
    main()
