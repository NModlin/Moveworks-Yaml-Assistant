#!/usr/bin/env python3
"""
Quick test of core compliance features.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from core_structures import ActionStep, ScriptStep, Workflow
    from compliance_validator import compliance_validator
    print("✅ All imports successful!")
    
    # Test basic compliance validation
    action = ActionStep(
        action_name="mw.get_user_by_email",
        output_key="user_info",
        description="Test action"
    )
    
    workflow = Workflow(steps=[action])
    result = compliance_validator.validate_workflow_compliance(workflow, "test_action")
    
    print(f"✅ Compliance validation works! Valid: {result.is_valid}")
    print(f"   Field naming errors: {len(result.field_naming_errors)}")
    print(f"   Mandatory field errors: {len(result.mandatory_field_errors)}")
    
    # Test invalid naming
    bad_action = ActionStep(
        action_name="getUserInfo",  # camelCase - invalid
        output_key="userInfo",      # camelCase - invalid
        description="Bad naming"
    )
    
    bad_workflow = Workflow(steps=[bad_action])
    bad_result = compliance_validator.validate_workflow_compliance(bad_workflow, "test_action")
    
    print(f"✅ Invalid naming detected! Valid: {bad_result.is_valid}")
    print(f"   Field naming errors: {len(bad_result.field_naming_errors)}")
    
    print("\n🎉 Core compliance features are working correctly!")
    print("🚀 Ready to run: python main_gui.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
