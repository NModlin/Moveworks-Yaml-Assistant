#!/usr/bin/env python3
"""Simple test for input variables functionality."""

# Test basic InputVariable creation
try:
    from core_structures import InputVariable, Workflow, ActionStep
    print("✓ Successfully imported core structures")
    
    # Test creating an input variable
    var = InputVariable(
        name="test_email",
        data_type="string",
        description="Test email variable"
    )
    print(f"✓ Created input variable: {var.name}")
    
    # Test workflow with input variables
    workflow = Workflow()
    workflow.add_input_variable(var)
    print(f"✓ Added variable to workflow. Count: {len(workflow.input_variables)}")
    
    # Test YAML generation
    from yaml_generator import generate_yaml_string
    
    # Add a simple step
    step = ActionStep(
        action_name="test.action",
        output_key="test_output",
        input_args={"email": "data.test_email"}
    )
    workflow.steps = [step]
    
    yaml_output = generate_yaml_string(workflow, "test_action")
    print("✓ Generated YAML successfully")
    
    # Check if input_variables section exists
    if "input_variables:" in yaml_output:
        print("✓ YAML contains input_variables section")
    else:
        print("✗ YAML missing input_variables section")
    
    print("\nGenerated YAML:")
    print("=" * 40)
    print(yaml_output)
    print("=" * 40)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
