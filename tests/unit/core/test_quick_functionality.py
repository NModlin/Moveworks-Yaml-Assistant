#!/usr/bin/env python3
"""Quick test to verify basic functionality."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_basic_imports():
    """Test basic imports."""
    print("Testing basic imports...")
    
    try:
        # Test PySide6
        from PySide6.QtWidgets import QApplication, QDialog
        print("✓ PySide6 imported")
        
        # Test tutorial system
        from tutorials.unified_tutorial_system import TutorialCategory, TutorialDifficulty
        print("✓ Tutorial system imported")
        
        # Test tutorial builder
        from tutorial_builder import TutorialTemplate
        print("✓ Tutorial builder imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_template_creation():
    """Test template creation."""
    print("Testing template creation...")
    
    try:
        from tutorial_builder import TutorialTemplate
        from tutorials.unified_tutorial_system import TutorialCategory, TutorialDifficulty
        
        template = TutorialTemplate(
            id="test",
            name="Test Template",
            description="Test",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="5 min",
            learning_objectives=["Test"],
            step_templates=[{"title": "Test", "description": "Test", "instruction": "Test", "action_type": "info"}]
        )
        
        print("✓ Template created successfully")
        return True
    except Exception as e:
        print(f"✗ Template creation failed: {e}")
        return False

def test_main_gui_methods():
    """Test main GUI methods exist."""
    print("Testing main GUI integration...")
    
    try:
        import main_gui
        
        # Check methods exist
        assert hasattr(main_gui.MainWindow, '_show_tutorial_builder')
        assert hasattr(main_gui.MainWindow, '_on_tutorial_created')
        
        print("✓ Main GUI methods exist")
        return True
    except Exception as e:
        print(f"✗ Main GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("QUICK SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_template_creation,
        test_main_gui_methods
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All basic tests passed!")
    else:
        print("⚠️ Some tests failed")
