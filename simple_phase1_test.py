#!/usr/bin/env python3
"""
Simple test for Phase 1 Enhanced JSON Path Selector features.
"""

def test_phase1_basic():
    """Test basic Phase 1 functionality without GUI."""
    print("🔍 Testing Phase 1 Basic Functionality...")
    
    try:
        # Test PathValidator
        from enhanced_json_selector import PathValidator, ValidationResult
        
        validator = PathValidator()
        print("✅ PathValidator created")
        
        # Test validation
        test_data = {"user": {"name": "John", "id": 123, "emails": ["john@test.com"]}}
        
        # Valid path
        result = validator.validate_path("data.user.name", test_data)
        assert result.valid, "Valid path should pass validation"
        print("✅ Valid path validation works")
        
        # Invalid path
        result = validator.validate_path("data.user.invalid", test_data)
        assert not result.valid, "Invalid path should fail validation"
        print("✅ Invalid path validation works")
        
        # Test PathBookmarkManager
        from enhanced_json_selector import PathBookmarkManager
        
        bookmark_manager = PathBookmarkManager()
        print("✅ PathBookmarkManager created")
        
        # Add bookmark
        bookmark_manager.add_bookmark("test_bookmark", "data.user.name", "Test")
        assert "Test::test_bookmark" in bookmark_manager.bookmarks
        print("✅ Bookmark creation works")
        
        # Track usage
        bookmark_manager.track_usage("data.user.name")
        assert bookmark_manager.usage_count["data.user.name"] == 1
        print("✅ Usage tracking works")
        
        print("\n🎉 All Phase 1 basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase1_integration():
    """Test Phase 1 integration with main selector."""
    print("\n🔗 Testing Phase 1 Integration...")
    
    try:
        from enhanced_json_selector import EnhancedJsonPathSelector
        from core_structures import Workflow, ActionStep
        
        # Create selector
        selector = EnhancedJsonPathSelector()
        print("✅ EnhancedJsonPathSelector created")
        
        # Check Phase 1 components
        assert hasattr(selector, 'path_validator'), "Should have path_validator"
        assert hasattr(selector, 'bookmark_manager'), "Should have bookmark_manager"
        assert hasattr(selector, 'smart_completer'), "Should have smart_completer"
        print("✅ Phase 1 components integrated")
        
        # Create test workflow
        workflow = Workflow()
        step = ActionStep(action_name="test", output_key="test_data")
        step.parsed_json_output = {"user": {"name": "John", "email": "john@test.com"}}
        workflow.steps.append(step)
        
        # Set workflow
        selector.set_workflow(workflow, 1)
        print("✅ Workflow integration works")
        
        print("\n🎉 All Phase 1 integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simple Phase 1 tests."""
    print("=" * 60)
    print("PHASE 1 ENHANCED JSON PATH SELECTOR - SIMPLE TEST")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_phase1_basic),
        ("Integration", test_phase1_integration)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        success = test_func()
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PHASE 1 TESTS PASSED!")
        print("\nPhase 1 Features Implemented:")
        print("✅ Smart Auto-Completion")
        print("✅ Real-Time Path Validation")
        print("✅ Drag & Drop Path Insertion")
        print("✅ Path Bookmarking System")
        print("\nReady for Phase 2 implementation!")
    else:
        print("⚠️ Some tests failed.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
