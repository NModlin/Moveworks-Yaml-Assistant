"""
Command Line Interface for the Moveworks YAML Assistant.

This CLI provides basic functionality to test the core engine before
implementing the full PySide6 GUI.
"""

import click
import json
from typing import List
from core_structures import ActionStep, ScriptStep, Workflow, DataContext
from yaml_generator import generate_yaml_string
from validator import comprehensive_validate

# Global workflow storage for CLI session
current_workflow = Workflow()


@click.group()
def cli():
    """Moveworks YAML Assistant CLI - Test the core functionality."""
    pass


@cli.command()
def add_action():
    """Add an action step to the current workflow."""
    click.echo("Adding a new Action Step...")
    
    # Get basic information
    action_name = click.prompt("Action name (e.g., mw.get_user_by_email)")
    description = click.prompt("Description (optional)", default="", show_default=False)
    output_key = click.prompt("Output key")
    
    # Get input arguments
    input_args = {}
    click.echo("\nInput arguments (press Enter with empty key to finish):")
    while True:
        key = click.prompt("  Argument key", default="", show_default=False)
        if not key:
            break
        value = click.prompt(f"  Value for '{key}'")
        input_args[key] = value
    
    # Get JSON output
    click.echo("\nEnter the JSON output this action will produce:")
    click.echo("(You can paste multi-line JSON. Type 'END' on a new line when finished)")
    
    json_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        json_lines.append(line)
    
    json_output = '\n'.join(json_lines)
    
    # Create the action step
    action_step = ActionStep(
        action_name=action_name,
        output_key=output_key,
        description=description if description else None,
        input_args=input_args,
        user_provided_json_output=json_output if json_output.strip() else None
    )
    
    current_workflow.steps.append(action_step)
    click.echo(f"✓ Added action step '{action_name}' with output key '{output_key}'")


@cli.command()
def add_script():
    """Add a script step to the current workflow."""
    click.echo("Adding a new Script Step...")
    
    # Get basic information
    description = click.prompt("Description (optional)", default="", show_default=False)
    output_key = click.prompt("Output key")
    
    # Get input arguments
    input_args = {}
    click.echo("\nInput arguments (press Enter with empty key to finish):")
    while True:
        key = click.prompt("  Argument key", default="", show_default=False)
        if not key:
            break
        value = click.prompt(f"  Value for '{key}'")
        input_args[key] = value
    
    # Get script code
    click.echo("\nEnter the APIthon script code:")
    click.echo("(You can paste multi-line code. Type 'END' on a new line when finished)")
    
    code_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        code_lines.append(line)
    
    code = '\n'.join(code_lines)
    
    # Get JSON output
    click.echo("\nEnter the JSON output this script will produce:")
    click.echo("(You can paste multi-line JSON. Type 'END' on a new line when finished)")
    
    json_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        json_lines.append(line)
    
    json_output = '\n'.join(json_lines)
    
    # Create the script step
    script_step = ScriptStep(
        code=code,
        output_key=output_key,
        description=description if description else None,
        input_args=input_args,
        user_provided_json_output=json_output if json_output.strip() else None
    )
    
    current_workflow.steps.append(script_step)
    click.echo(f"✓ Added script step with output key '{output_key}'")


@cli.command()
def show_steps():
    """Show all steps in the current workflow."""
    if not current_workflow.steps:
        click.echo("No steps in the current workflow.")
        return
    
    click.echo(f"Current workflow has {len(current_workflow.steps)} step(s):")
    
    for i, step in enumerate(current_workflow.steps, 1):
        if isinstance(step, ActionStep):
            click.echo(f"  {i}. Action: {step.action_name} -> {step.output_key}")
            if step.description:
                click.echo(f"     Description: {step.description}")
        elif isinstance(step, ScriptStep):
            click.echo(f"  {i}. Script -> {step.output_key}")
            if step.description:
                click.echo(f"     Description: {step.description}")


@cli.command()
def show_yaml():
    """Generate and display the YAML for the current workflow."""
    if not current_workflow.steps:
        click.echo("No steps in the current workflow. Add some steps first.")
        return
    
    try:
        yaml_output = generate_yaml_string(current_workflow)
        click.echo("Generated YAML:")
        click.echo("=" * 50)
        click.echo(yaml_output)
        click.echo("=" * 50)
    except Exception as e:
        click.echo(f"Error generating YAML: {e}")


@cli.command()
def validate():
    """Validate the current workflow."""
    if not current_workflow.steps:
        click.echo("No steps in the current workflow. Add some steps first.")
        return
    
    # Create a basic data context for validation
    initial_context = DataContext()
    
    errors = comprehensive_validate(current_workflow, initial_context)
    
    if errors:
        click.echo(f"❌ Validation failed with {len(errors)} error(s):")
        for error in errors:
            click.echo(f"  - {error}")
    else:
        click.echo("✅ Workflow validation passed!")


@cli.command()
def clear():
    """Clear the current workflow."""
    global current_workflow
    current_workflow = Workflow()
    click.echo("✓ Workflow cleared.")


@cli.command()
def save():
    """Save the current workflow to a file."""
    if not current_workflow.steps:
        click.echo("No steps in the current workflow. Add some steps first.")
        return
    
    filename = click.prompt("Filename", default="workflow.json")
    
    try:
        # Convert workflow to JSON-serializable format
        workflow_data = {
            "steps": []
        }
        
        for step in current_workflow.steps:
            if isinstance(step, ActionStep):
                step_data = {
                    "type": "action",
                    "action_name": step.action_name,
                    "output_key": step.output_key,
                    "description": step.description,
                    "input_args": step.input_args,
                    "progress_updates": step.progress_updates,
                    "delay_config": step.delay_config,
                    "user_provided_json_output": step.user_provided_json_output
                }
            elif isinstance(step, ScriptStep):
                step_data = {
                    "type": "script",
                    "code": step.code,
                    "output_key": step.output_key,
                    "description": step.description,
                    "input_args": step.input_args,
                    "user_provided_json_output": step.user_provided_json_output
                }
            
            workflow_data["steps"].append(step_data)
        
        with open(filename, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        click.echo(f"✓ Workflow saved to {filename}")
    
    except Exception as e:
        click.echo(f"Error saving workflow: {e}")


@cli.command()
def load():
    """Load a workflow from a file."""
    filename = click.prompt("Filename", default="workflow.json")
    
    try:
        with open(filename, 'r') as f:
            workflow_data = json.load(f)
        
        global current_workflow
        current_workflow = Workflow()
        
        for step_data in workflow_data.get("steps", []):
            if step_data["type"] == "action":
                step = ActionStep(
                    action_name=step_data["action_name"],
                    output_key=step_data["output_key"],
                    description=step_data.get("description"),
                    input_args=step_data.get("input_args", {}),
                    progress_updates=step_data.get("progress_updates"),
                    delay_config=step_data.get("delay_config"),
                    user_provided_json_output=step_data.get("user_provided_json_output")
                )
            elif step_data["type"] == "script":
                step = ScriptStep(
                    code=step_data["code"],
                    output_key=step_data["output_key"],
                    description=step_data.get("description"),
                    input_args=step_data.get("input_args", {}),
                    user_provided_json_output=step_data.get("user_provided_json_output")
                )
            
            current_workflow.steps.append(step)
        
        click.echo(f"✓ Workflow loaded from {filename} ({len(current_workflow.steps)} steps)")
    
    except Exception as e:
        click.echo(f"Error loading workflow: {e}")


if __name__ == "__main__":
    cli()
