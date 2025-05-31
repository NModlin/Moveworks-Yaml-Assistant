#!/usr/bin/env python3
"""
Diagnostic script to identify specific tutorial rendering issues.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_target_elements():
    """Check if tutorial target elements exist in main_gui.py."""
    print("🔍 Checking Tutorial Target Elements")
    print("=" * 50)
    
    # Read main_gui.py to find object names
    try:
        with open('main_gui.py', 'r', encoding='utf-8') as f:
            main_gui_content = f.read()
    except Exception as e:
        print(f"❌ Could not read main_gui.py: {e}")
        return False
    
    # Extract object names from main_gui.py
    import re
    object_name_pattern = r'setObjectName\(["\']([^"\']+)["\']\)'
    object_names = set(re.findall(object_name_pattern, main_gui_content))
    
    print(f"Found {len(object_names)} object names in main_gui.py:")
    for name in sorted(object_names):
        print(f"  ✅ {name}")
    
    # Check tutorial target elements
    try:
        from comprehensive_tutorial_system import ComprehensiveTutorialSystem
        
        class MockWindow:
            def findChild(self, widget_type, name):
                return None
        
        mock_window = MockWindow()
        system = ComprehensiveTutorialSystem(mock_window)
        tutorials = system.get_available_tutorials()
        
        print(f"\n🎯 Checking Target Elements in {len(tutorials)} Tutorials")
        print("=" * 50)
        
        missing_targets = set()
        all_targets = set()
        
        for tutorial in tutorials:
            print(f"\n📚 {tutorial.title}")
            for i, step in enumerate(tutorial.steps):
                if step.target_element:
                    all_targets.add(step.target_element)
                    if step.target_element not in object_names:
                        missing_targets.add(step.target_element)
                        print(f"  ❌ Step {i+1}: Missing target '{step.target_element}'")
                    else:
                        print(f"  ✅ Step {i+1}: Found target '{step.target_element}'")
        
        print(f"\n📊 Summary:")
        print(f"  Total target elements: {len(all_targets)}")
        print(f"  Missing target elements: {len(missing_targets)}")
        
        if missing_targets:
            print(f"\n❌ Missing Target Elements:")
            for target in sorted(missing_targets):
                print(f"  - {target}")
            return False
        else:
            print("✅ All target elements found!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking tutorials: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_tutorial_step_structure():
    """Check tutorial step structure for completeness."""
    print("\n🔍 Checking Tutorial Step Structure")
    print("=" * 50)
    
    try:
        from comprehensive_tutorial_system import ComprehensiveTutorialSystem
        
        class MockWindow:
            def findChild(self, widget_type, name):
                return None
        
        mock_window = MockWindow()
        system = ComprehensiveTutorialSystem(mock_window)
        tutorials = system.get_available_tutorials()
        
        issues_found = False
        
        for tutorial in tutorials:
            print(f"\n📚 {tutorial.title}")
            
            # Check tutorial fields
            if not tutorial.id:
                print(f"  ❌ Missing tutorial ID")
                issues_found = True
            if not tutorial.title:
                print(f"  ❌ Missing tutorial title")
                issues_found = True
            if not tutorial.description:
                print(f"  ❌ Missing tutorial description")
                issues_found = True
            if not tutorial.learning_objectives:
                print(f"  ❌ Missing learning objectives")
                issues_found = True
            if not tutorial.steps:
                print(f"  ❌ Missing tutorial steps")
                issues_found = True
            
            # Check step structure
            for i, step in enumerate(tutorial.steps):
                step_num = i + 1
                if not step.title:
                    print(f"  ❌ Step {step_num}: Missing title")
                    issues_found = True
                if not step.instruction:
                    print(f"  ❌ Step {step_num}: Missing instruction")
                    issues_found = True
                if not step.action_type:
                    print(f"  ❌ Step {step_num}: Missing action_type")
                    issues_found = True
                
                # Check action_type validity
                valid_action_types = ["info", "click", "type", "copy_paste", "wait", "validate"]
                if step.action_type not in valid_action_types:
                    print(f"  ❌ Step {step_num}: Invalid action_type '{step.action_type}'")
                    issues_found = True
            
            if not issues_found:
                print(f"  ✅ Tutorial structure is valid ({len(tutorial.steps)} steps)")
        
        return not issues_found
        
    except Exception as e:
        print(f"❌ Error checking tutorial structure: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_integration_manager():
    """Check tutorial integration manager."""
    print("\n🔍 Checking Tutorial Integration Manager")
    print("=" * 50)
    
    try:
        from tutorial_integration import TutorialIntegrationManager, TutorialSelectionWidget
        
        class MockWindow:
            def findChild(self, widget_type, name):
                return None
        
        mock_window = MockWindow()
        
        # Test integration manager
        manager = TutorialIntegrationManager(mock_window)
        print("✅ TutorialIntegrationManager created successfully")
        
        # Test tutorial system access
        tutorial_system = manager.get_tutorial_system()
        if tutorial_system:
            print("✅ Tutorial system accessible")
        else:
            print("❌ Tutorial system not accessible")
            return False
        
        # Test tutorial info methods
        info = manager.get_current_tutorial_info()
        if info is None:
            print("✅ Current tutorial info returns None when inactive")
        else:
            print(f"❌ Expected None, got {info}")
            return False
        
        active = manager.is_tutorial_active()
        if not active:
            print("✅ Tutorial active status returns False when inactive")
        else:
            print("❌ Expected False for tutorial active status")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking integration manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic checks."""
    print("🩺 Tutorial System Diagnostic")
    print("=" * 60)
    
    checks = [
        ("Target Elements", check_target_elements),
        ("Tutorial Step Structure", check_tutorial_step_structure),
        ("Integration Manager", check_integration_manager)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🔍 Running {check_name} Check...")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name} CHECK PASSED")
            else:
                print(f"❌ {check_name} CHECK FAILED")
        except Exception as e:
            print(f"❌ {check_name} CHECK FAILED with exception: {e}")
    
    print(f"\n📊 Diagnostic Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All diagnostic checks passed! Tutorial system should work correctly.")
        return True
    else:
        print("⚠️  Some checks failed. See specific issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
