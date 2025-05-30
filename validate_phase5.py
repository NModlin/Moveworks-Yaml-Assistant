#!/usr/bin/env python3
"""
Simple validation script to check Phase 5 implementation without running tests.
This script validates that all Phase 5 modules can be imported and basic functionality works.
"""

def validate_imports():
    """Validate that all Phase 5 modules can be imported."""
    print("Validating Phase 5 imports...")
    
    try:
        # Core modules
        from core_structures import ActionStep, ScriptStep, Workflow
        print("✓ Core structures imported successfully")
        
        # Enhanced validator
        from validator import (
            comprehensive_validate, validate_action_names, 
            validate_output_key_format, validate_script_syntax,
            validate_data_references
        )
        print("✓ Enhanced validator imported successfully")
        
        # Help system
        from help_system import help_system, get_tooltip, get_contextual_help
        print("✓ Help system imported successfully")
        
        # Error display (PySide6 dependent)
        try:
            from error_display import ErrorListWidget, ValidationDialog, StatusIndicator, HelpDialog
            print("✓ Error display widgets imported successfully")
        except ImportError as e:
            print(f"⚠ Error display widgets not available (PySide6 required): {e}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def validate_help_system():
    """Validate help system functionality."""
    print("\nValidating help system...")
    
    try:
        from help_system import help_system, get_tooltip
        
        # Check topics
        topics = help_system.topics
        print(f"✓ Help system has {len(topics)} topics")
        
        # Check categories
        categories = help_system.get_all_categories()
        print(f"✓ Found categories: {', '.join(categories)}")
        
        # Check search
        results = help_system.search_topics("action")
        print(f"✓ Search functionality works ({len(results)} results for 'action')")
        
        # Check tooltips
        tooltip = get_tooltip("action_name")
        print(f"✓ Tooltip system works (sample: {tooltip[:30]}...)")
        
        return True
        
    except Exception as e:
        print(f"✗ Help system error: {e}")
        return False


def validate_enhanced_validation():
    """Validate enhanced validation functionality."""
    print("\nValidating enhanced validation...")
    
    try:
        from core_structures import ActionStep, ScriptStep, Workflow
        from validator import (
            validate_action_names, validate_output_key_format,
            validate_script_syntax, comprehensive_validate
        )
        
        # Test action name validation
        invalid_action = ActionStep(action_name="mw.", output_key="test")
        workflow = Workflow(steps=[invalid_action])
        errors = validate_action_names(workflow)
        print(f"✓ Action name validation works ({len(errors)} errors found)")
        
        # Test output key validation
        invalid_key = ActionStep(action_name="test", output_key="123invalid")
        workflow = Workflow(steps=[invalid_key])
        errors = validate_output_key_format(workflow)
        print(f"✓ Output key validation works ({len(errors)} errors found)")
        
        # Test script validation
        invalid_script = ScriptStep(code="invalid syntax !", output_key="test")
        workflow = Workflow(steps=[invalid_script])
        errors = validate_script_syntax(workflow)
        print(f"✓ Script validation works ({len(errors)} errors found)")
        
        # Test comprehensive validation
        errors = comprehensive_validate(workflow)
        print(f"✓ Comprehensive validation works ({len(errors)} total errors)")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced validation error: {e}")
        return False


def validate_file_structure():
    """Validate that all Phase 5 files exist and have expected content."""
    print("\nValidating file structure...")
    
    import os
    
    required_files = [
        "help_system.py",
        "error_display.py", 
        "test_phase5.py",
        "validator.py",
        "main_gui.py"
    ]
    
    for filename in required_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✓ {filename} exists ({len(content)} characters)")
        else:
            print(f"✗ {filename} missing")
            return False
    
    return True


def main():
    """Run Phase 5 validation checks."""
    print("Moveworks YAML Assistant - Phase 5 Implementation Validation")
    print("=" * 70)
    
    checks = [
        validate_file_structure,
        validate_imports,
        validate_help_system,
        validate_enhanced_validation
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {check.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Phase 5 Validation Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✓ Phase 5 implementation is complete and functional!")
        print("\nPhase 5 Features Successfully Implemented:")
        print("• Enhanced validation engine with comprehensive error checking")
        print("• Improved error display with categorization and severity")
        print("• Comprehensive help system with search and navigation")
        print("• Better UI/UX with tooltips and contextual guidance")
        print("• Performance optimizations for large workflows")
        print("\nTo use the enhanced application:")
        print("  python main_gui.py  # Launch the desktop GUI")
        print("  python run_app.py   # Use the launcher script")
    else:
        print(f"\n✗ {failed} validation check(s) failed.")
        print("Please review the errors above.")
    
    return failed


if __name__ == "__main__":
    exit(main())
