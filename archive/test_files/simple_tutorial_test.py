#!/usr/bin/env python3
"""
Simple test to check tutorial structure without GUI dependencies.
"""

def test_tutorial_target_elements():
    """Test tutorial target elements against main_gui.py object names."""
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
    
    # Define tutorial target elements (extracted from comprehensive_tutorial_system.py)
    tutorial_targets = {
        "compound_action_name_field",
        "add_action_button", 
        "action_config_panel",
        "json_output_field",
        "json_path_selector_button",
        "validate_button",
        "yaml_preview_panel",
        "add_script_btn",
        "add_switch_button",
        "add_try_catch_button",
        "import_curl_button",
        "progress_updates_section",
        "template_library_button",
        "switch_config_panel",
        "switch_case_panel",
        "switch_default_panel",
        "script_config_panel",
        "script_editor",
        "json_input_field",
        "try_block_panel",
        "catch_block_panel",
        "retry_config_panel",
        "finally_block_panel"
    }
    
    print(f"\n🎯 Checking {len(tutorial_targets)} Tutorial Target Elements")
    print("=" * 50)
    
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
        print(f"\n❌ Missing Target Elements Need to be Added:")
        for target in sorted(missing_targets):
            print(f"  - {target}")
        return False
    else:
        print("✅ All target elements found!")
        return True

def test_tutorial_structure():
    """Test basic tutorial structure without importing GUI components."""
    print("\n🔍 Checking Tutorial Structure")
    print("=" * 50)
    
    # Define expected tutorial structure
    expected_tutorials = [
        {
            "id": "module_1_basic_compound_action",
            "title": "Module 1: Your First Compound Action",
            "min_steps": 10
        },
        {
            "id": "module_2_it_automation", 
            "title": "Module 2: IT Automation",
            "min_steps": 10
        },
        {
            "id": "module_3_conditional_logic",
            "title": "Module 3: Conditional Logic", 
            "min_steps": 10
        },
        {
            "id": "module_4_data_processing",
            "title": "Module 4: Data Processing",
            "min_steps": 8
        },
        {
            "id": "module_5_error_handling",
            "title": "Module 5: Error Handling",
            "min_steps": 10
        }
    ]
    
    # Read comprehensive_tutorial_system.py to check structure
    try:
        with open('comprehensive_tutorial_system.py', 'r', encoding='utf-8') as f:
            tutorial_content = f.read()
    except Exception as e:
        print(f"❌ Could not read comprehensive_tutorial_system.py: {e}")
        return False
    
    issues_found = False
    
    for expected in expected_tutorials:
        tutorial_id = expected["id"]
        title = expected["title"]
        min_steps = expected["min_steps"]
        
        print(f"\n📚 Checking {title}")
        
        # Check if tutorial ID exists
        if tutorial_id not in tutorial_content:
            print(f"  ❌ Tutorial ID '{tutorial_id}' not found")
            issues_found = True
            continue
        
        # Check if title exists
        if title not in tutorial_content:
            print(f"  ❌ Tutorial title '{title}' not found")
            issues_found = True
        else:
            print(f"  ✅ Title found")
        
        # Count TutorialStep instances for this tutorial
        tutorial_section_start = tutorial_content.find(f'id="{tutorial_id}"')
        if tutorial_section_start == -1:
            print(f"  ❌ Could not find tutorial section")
            issues_found = True
            continue
        
        # Find the end of this tutorial (next tutorial or end of tutorials)
        next_tutorial_start = tutorial_content.find('Tutorial(', tutorial_section_start + 1)
        tutorial_section_end = next_tutorial_start if next_tutorial_start != -1 else len(tutorial_content)
        
        tutorial_section = tutorial_content[tutorial_section_start:tutorial_section_end]
        step_count = tutorial_section.count('TutorialStep(')
        
        if step_count >= min_steps:
            print(f"  ✅ Found {step_count} steps (minimum {min_steps})")
        else:
            print(f"  ❌ Found only {step_count} steps (minimum {min_steps})")
            issues_found = True
    
    # Check if tutorials are properly stored
    if '"module_1_basic_compound_action": module_1_tutorial' in tutorial_content:
        print(f"\n✅ Tutorials properly stored in dictionary")
    else:
        print(f"\n❌ Tutorials not properly stored")
        issues_found = True
    
    return not issues_found

def main():
    """Run simple tutorial tests."""
    print("🧪 Simple Tutorial Structure Test")
    print("=" * 60)
    
    tests = [
        ("Target Elements", test_tutorial_target_elements),
        ("Tutorial Structure", test_tutorial_structure)
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
        print("🎉 All tests passed! Tutorial structure is correct.")
        return True
    else:
        print("⚠️  Some tests failed. See specific issues above.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
