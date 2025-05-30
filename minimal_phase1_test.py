#!/usr/bin/env python3
"""
Minimal test for Phase 1 Enhanced JSON Path Selector features.
Tests only the core logic without GUI components.
"""

def test_path_validator():
    """Test PathValidator core functionality."""
    print("🔍 Testing PathValidator...")
    
    try:
        # Import the validator
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Test the core validation logic
        from enhanced_json_selector import PathValidator
        
        validator = PathValidator()
        print("✅ PathValidator created successfully")
        
        # Test data
        test_data = {
            "user": {
                "name": "John Doe",
                "id": 12345,
                "emails": ["john@test.com", "john.doe@company.com"],
                "profile": {
                    "department": "Engineering",
                    "manager": {
                        "name": "Jane Smith",
                        "id": 67890
                    }
                }
            },
            "tickets": [
                {"id": "TKT-001", "title": "Test Ticket", "status": "open"},
                {"id": "TKT-002", "title": "Another Ticket", "status": "closed"}
            ]
        }
        
        # Test valid paths
        valid_paths = [
            "data.user.name",
            "data.user.emails[0]",
            "data.user.profile.department",
            "data.user.profile.manager.name",
            "data.tickets[0].title",
            "data.tickets[1].status"
        ]
        
        for path in valid_paths:
            result = validator.validate_path(path, test_data)
            if result.valid:
                print(f"✅ Valid path: {path} -> {result.value}")
            else:
                print(f"❌ Expected valid but got invalid: {path}")
                return False
        
        # Test invalid paths
        invalid_paths = [
            "data.user.invalid_field",
            "data.user.emails[99]",
            "data.nonexistent.field",
            "data.tickets[5].title"
        ]
        
        for path in invalid_paths:
            result = validator.validate_path(path, test_data)
            if not result.valid:
                print(f"✅ Invalid path correctly detected: {path}")
            else:
                print(f"❌ Expected invalid but got valid: {path}")
                return False
        
        print("✅ PathValidator tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PathValidator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bookmark_manager():
    """Test PathBookmarkManager core functionality."""
    print("\n📌 Testing PathBookmarkManager...")
    
    try:
        from enhanced_json_selector import PathBookmarkManager
        
        # Create bookmark manager
        manager = PathBookmarkManager()
        print("✅ PathBookmarkManager created successfully")
        
        # Test adding bookmarks
        manager.add_bookmark("User Name", "data.user.name", "User Info")
        manager.add_bookmark("User Email", "data.user.emails[0]", "User Info")
        manager.add_bookmark("First Ticket", "data.tickets[0].title", "Tickets")
        
        print(f"✅ Added 3 bookmarks, total: {len(manager.bookmarks)}")
        
        # Test getting bookmarks by category
        user_bookmarks = manager.get_bookmarks_by_category("User Info")
        ticket_bookmarks = manager.get_bookmarks_by_category("Tickets")
        
        if len(user_bookmarks) == 2 and len(ticket_bookmarks) == 1:
            print("✅ Category filtering works correctly")
        else:
            print(f"❌ Category filtering failed: User Info={len(user_bookmarks)}, Tickets={len(ticket_bookmarks)}")
            return False
        
        # Test usage tracking
        manager.track_usage("data.user.name")
        manager.track_usage("data.user.name")
        manager.track_usage("data.user.emails[0]")
        
        frequent_paths = manager.get_frequent_paths(2)
        if "data.user.name" in frequent_paths and "data.user.emails[0]" in frequent_paths:
            print("✅ Usage tracking works correctly")
        else:
            print(f"❌ Usage tracking failed: {frequent_paths}")
            return False
        
        print("✅ PathBookmarkManager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PathBookmarkManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_result():
    """Test ValidationResult class."""
    print("\n✅ Testing ValidationResult...")
    
    try:
        from enhanced_json_selector import ValidationResult
        
        # Test valid result
        valid_result = ValidationResult(valid=True, value="John Doe")
        if valid_result.valid and valid_result.value == "John Doe" and valid_result.value_type == "str":
            print("✅ Valid ValidationResult works correctly")
        else:
            print("❌ Valid ValidationResult failed")
            return False
        
        # Test invalid result with suggestions
        invalid_result = ValidationResult(
            valid=False, 
            error="Field not found", 
            suggestions=["data.user.name", "data.user.email"]
        )
        if not invalid_result.valid and len(invalid_result.suggestions) == 2:
            print("✅ Invalid ValidationResult with suggestions works correctly")
        else:
            print("❌ Invalid ValidationResult failed")
            return False
        
        print("✅ ValidationResult tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ValidationResult test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run minimal Phase 1 tests."""
    print("=" * 60)
    print("PHASE 1 ENHANCED JSON PATH SELECTOR - MINIMAL TEST")
    print("=" * 60)
    print("Testing core functionality without GUI components...")
    
    tests = [
        ("ValidationResult", test_validation_result),
        ("PathValidator", test_path_validator),
        ("PathBookmarkManager", test_bookmark_manager)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        success = test_func()
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PHASE 1 CORE TESTS PASSED!")
        print("\nPhase 1 Core Features Verified:")
        print("✅ ValidationResult class")
        print("✅ PathValidator with intelligent suggestions")
        print("✅ PathBookmarkManager with categories and usage tracking")
        print("\nCore logic is ready for GUI integration!")
    else:
        print("⚠️ Some core tests failed.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
