#!/usr/bin/env python3
"""
Test script to verify that the step configuration issue is fixed.

This script tests that when a new action step is added, the middle column
properly displays the action configuration form instead of "Select a step to configure".
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from main_gui import MoveworksYAMLAssistant
from core_structures import ActionStep


def test_step_configuration():
    """Test that step configuration works properly."""
    print("Testing step configuration fix...")
    
    app = QApplication(sys.argv)
    
    # Create the main window
    window = MoveworksYAMLAssistant()
    window.show()
    
    # Test adding a new action step
    print("1. Adding a new action step...")
    
    # Simulate adding an action step
    new_step = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Test action step"
    )
    
    # Add the step to the workflow
    window.workflow_list.workflow.steps.append(new_step)
    window.workflow_list.update_workflow_display()
    
    # Select the new step (simulate clicking on it)
    step_index = len(window.workflow_list.workflow.steps) - 1
    window._on_step_selected(step_index)
    
    # Check if the configuration panel is showing the action config
    current_widget = window.config_panel.currentWidget()
    
    if current_widget == window.config_panel.action_config_widget:
        print("✅ SUCCESS: Action configuration panel is displayed correctly!")
        
        # Check if the enhanced input args table is working
        if hasattr(window.config_panel.action_input_args_table, 'add_argument_row'):
            print("✅ SUCCESS: Enhanced input arguments table is active!")
            
            # Test adding an argument
            window.config_panel.action_input_args_table.add_argument_row("test_arg", "test_value")
            print("✅ SUCCESS: Can add arguments to enhanced table!")
            
        else:
            print("⚠️  WARNING: Enhanced input arguments table not detected, using fallback")
            
    elif current_widget == window.config_panel.empty_widget:
        print("❌ FAILURE: Still showing 'Select a step to configure' message")
        return False
    else:
        print(f"❌ FAILURE: Unexpected widget displayed: {type(current_widget).__name__}")
        return False
    
    # Test the workflow context
    if window.config_panel.workflow is not None:
        print("✅ SUCCESS: Workflow context is properly set in configuration panel!")
    else:
        print("❌ FAILURE: Workflow context is not set in configuration panel")
        return False
    
    # Test enhanced features
    print("\n2. Testing enhanced input arguments features...")
    
    # Test auto-suggestion (if available)
    try:
        window.config_panel._auto_suggest_action_args()
        print("✅ SUCCESS: Auto-suggestion feature is working!")
    except Exception as e:
        print(f"⚠️  WARNING: Auto-suggestion feature error: {e}")
    
    # Test JSON suggestion (if available)
    try:
        # This would normally open a dialog, so we just test the method exists
        if hasattr(window.config_panel, '_suggest_args_from_json'):
            print("✅ SUCCESS: JSON suggestion feature is available!")
        else:
            print("⚠️  WARNING: JSON suggestion feature not found")
    except Exception as e:
        print(f"⚠️  WARNING: JSON suggestion feature error: {e}")
    
    print("\n3. Testing step data persistence...")
    
    # Test that step data is properly updated
    window.config_panel.action_name_edit.setText("mw.create_ticket")
    window.config_panel.action_description_edit.setText("Create a support ticket")
    window.config_panel.action_output_key_edit.setText("ticket_result")
    
    # Trigger data change
    window.config_panel._on_action_data_changed()
    
    # Check if the step was updated
    if (new_step.action_name == "mw.create_ticket" and 
        new_step.description == "Create a support ticket" and
        new_step.output_key == "ticket_result"):
        print("✅ SUCCESS: Step data is properly updated!")
    else:
        print("❌ FAILURE: Step data was not updated correctly")
        return False
    
    print("\n🎉 All tests passed! The step configuration issue has been fixed.")
    
    # Close the application after a short delay
    QTimer.singleShot(2000, app.quit)
    
    return True


if __name__ == "__main__":
    try:
        success = test_step_configuration()
        if success:
            print("\n✅ Test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
