#!/usr/bin/env python3
"""
Basic test for comprehensive tutorial system without GUI dependencies.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports without GUI."""
    try:
        # Test enum imports
        from comprehensive_tutorial_system import TutorialDifficulty, TutorialCategory
        print("✅ Enums imported successfully")
        
        # Test dataclass imports
        from comprehensive_tutorial_system import TutorialStep, Tutorial
        print("✅ Dataclasses imported successfully")
        
        # Test basic tutorial step creation
        step = TutorialStep(
            title="Test Step",
            description="Test description",
            instruction="Test instruction"
        )
        print(f"✅ TutorialStep created: {step.title}")
        
        # Test basic tutorial creation
        tutorial = Tutorial(
            id="test_tutorial",
            title="Test Tutorial",
            description="Test description",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="5 minutes",
            steps=[step]
        )
        print(f"✅ Tutorial created: {tutorial.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tutorial_system_structure():
    """Test tutorial system structure without GUI components."""
    try:
        # Mock the GUI components
        class MockWindow:
            def findChild(self, widget_type, name):
                return None
        
        # Import the system class
        from comprehensive_tutorial_system import ComprehensiveTutorialSystem
        
        # Create mock window
        mock_window = MockWindow()
        
        # Create tutorial system
        system = ComprehensiveTutorialSystem(mock_window)
        print("✅ ComprehensiveTutorialSystem created")
        
        # Test getting tutorials
        tutorials = system.get_available_tutorials()
        print(f"✅ Found {len(tutorials)} tutorials")
        
        # Test each tutorial
        expected_ids = [
            "module_1_basic_compound_action",
            "module_2_it_automation",
            "module_3_conditional_logic", 
            "module_4_data_processing",
            "module_5_error_handling"
        ]
        
        actual_ids = [t.id for t in tutorials]
        
        for expected_id in expected_ids:
            if expected_id in actual_ids:
                tutorial = next(t for t in tutorials if t.id == expected_id)
                print(f"✅ {expected_id}: {tutorial.title} ({len(tutorial.steps)} steps)")
            else:
                print(f"❌ Missing tutorial: {expected_id}")
                return False
        
        # Test tutorial content
        for tutorial in tutorials:
            if not tutorial.steps:
                print(f"❌ Tutorial {tutorial.id} has no steps")
                return False
            
            for i, step in enumerate(tutorial.steps):
                if not step.title or not step.instruction:
                    print(f"❌ Tutorial {tutorial.id} step {i+1} missing title or instruction")
                    return False
        
        print("✅ All tutorial content validated")
        return True
        
    except Exception as e:
        print(f"❌ Tutorial system error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tutorial_integration():
    """Test tutorial integration components."""
    try:
        from tutorial_integration import TutorialIntegrationManager
        print("✅ TutorialIntegrationManager imported")
        
        # Mock window
        class MockWindow:
            def findChild(self, widget_type, name):
                return None
        
        mock_window = MockWindow()
        integration_manager = TutorialIntegrationManager(mock_window)
        print("✅ TutorialIntegrationManager created")
        
        # Test getting tutorial system
        tutorial_system = integration_manager.get_tutorial_system()
        print("✅ Tutorial system accessible through integration manager")
        
        # Test tutorial info
        info = integration_manager.get_current_tutorial_info()
        if info is None:
            print("✅ Current tutorial info correctly returns None when inactive")
        else:
            print(f"❌ Expected None, got {info}")
            return False
        
        # Test is_tutorial_active
        if not integration_manager.is_tutorial_active():
            print("✅ Tutorial active status correctly returns False when inactive")
        else:
            print("❌ Expected False for tutorial active status")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all basic tests."""
    print("🧪 Basic Tutorial System Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Tutorial System Structure", test_tutorial_system_structure),
        ("Tutorial Integration", test_tutorial_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Tutorial system structure is correct.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
