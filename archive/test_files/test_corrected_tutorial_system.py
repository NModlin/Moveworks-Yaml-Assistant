#!/usr/bin/env python3
"""
Test the corrected comprehensive tutorial system.
"""

def test_tutorial_target_elements():
    """Test that all tutorial target elements exist in main_gui.py."""
    print("🔍 Testing Corrected Tutorial Target Elements")
    print("=" * 60)
    
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
    
    # Read comprehensive_tutorial_system.py to find target elements
    try:
        with open('comprehensive_tutorial_system.py', 'r', encoding='utf-8') as f:
            tutorial_content = f.read()
    except Exception as e:
        print(f"❌ Could not read comprehensive_tutorial_system.py: {e}")
        return False
    
    # Extract target elements from tutorials
    target_pattern = r'target_element="([^"]+)"'
    tutorial_targets = set(re.findall(target_pattern, tutorial_content))
    
    print(f"\n🎯 Found {len(tutorial_targets)} target elements in tutorials:")
    
    missing_targets = []
    found_targets = []
    
    for target in tutorial_targets:
        if target in object_names:
            found_targets.append(target)
            print(f"  ✅ {target}")
        else:
            missing_targets.append(target)
            print(f"  ❌ {target} - MISSING")
    
    print(f"\n📊 Summary:")
    print(f"  Found targets: {len(found_targets)}")
    print(f"  Missing targets: {len(missing_targets)}")
    
    if missing_targets:
        print(f"\n❌ Missing Target Elements:")
        for target in sorted(missing_targets):
            print(f"  - {target}")
        return False
    else:
        print("✅ All target elements found!")
        return True

def test_tutorial_structure():
    """Test tutorial structure and content."""
    print("\n🔍 Testing Tutorial Structure")
    print("=" * 60)
    
    # Test basic structure without importing GUI components
    try:
        # Read the file content
        with open('comprehensive_tutorial_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required classes and functions
        required_elements = [
            'class TutorialDifficulty',
            'class TutorialCategory', 
            'class TutorialStep',
            'class Tutorial',
            'class ComprehensiveTutorialSystem',
            'def _initialize_tutorials',
            'def get_available_tutorials',
            'def start_tutorial'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
            else:
                print(f"  ✅ {element}")
        
        if missing_elements:
            print(f"\n❌ Missing elements:")
            for element in missing_elements:
                print(f"  - {element}")
            return False
        
        # Check for tutorial definitions
        tutorial_ids = [
            'module_1_basic_compound_action',
            'module_2_it_automation',
            'module_3_conditional_logic',
            'module_4_data_processing',
            'module_5_error_handling'
        ]
        
        missing_tutorials = []
        for tutorial_id in tutorial_ids:
            if f'"{tutorial_id}"' not in content:
                missing_tutorials.append(tutorial_id)
            else:
                print(f"  ✅ Tutorial: {tutorial_id}")
        
        if missing_tutorials:
            print(f"\n❌ Missing tutorials:")
            for tutorial in missing_tutorials:
                print(f"  - {tutorial}")
            return False
        
        # Check for proper tutorial storage
        if '"module_1_basic_compound_action": module_1_tutorial' in content:
            print("  ✅ Tutorials properly stored in dictionary")
        else:
            print("  ❌ Tutorials not properly stored")
            return False
        
        print("\n✅ Tutorial structure is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking tutorial structure: {e}")
        return False

def test_tutorial_integration():
    """Test tutorial integration components."""
    print("\n🔍 Testing Tutorial Integration")
    print("=" * 60)
    
    try:
        # Check if tutorial_integration.py exists and has required components
        with open('tutorial_integration.py', 'r', encoding='utf-8') as f:
            integration_content = f.read()
        
        required_integration_elements = [
            'class TutorialIntegrationManager',
            'class TutorialSelectionWidget',
            'def get_tutorial_system',
            'def is_tutorial_active',
            'def get_current_tutorial_info'
        ]
        
        missing_integration = []
        for element in required_integration_elements:
            if element not in integration_content:
                missing_integration.append(element)
            else:
                print(f"  ✅ {element}")
        
        if missing_integration:
            print(f"\n❌ Missing integration elements:")
            for element in missing_integration:
                print(f"  - {element}")
            return False
        
        print("\n✅ Tutorial integration is valid!")
        return True
        
    except FileNotFoundError:
        print("❌ tutorial_integration.py not found")
        return False
    except Exception as e:
        print(f"❌ Error checking tutorial integration: {e}")
        return False

def main():
    """Run all corrected tutorial tests."""
    print("🧪 Corrected Tutorial System Test")
    print("=" * 70)
    
    tests = [
        ("Target Elements", test_tutorial_target_elements),
        ("Tutorial Structure", test_tutorial_structure),
        ("Tutorial Integration", test_tutorial_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} TEST PASSED")
            else:
                print(f"❌ {test_name} TEST FAILED")
        except Exception as e:
            print(f"❌ {test_name} TEST FAILED with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Tutorial system is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
