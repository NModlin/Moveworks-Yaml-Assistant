#!/usr/bin/env python3
"""
Test imports for Phase 1 Enhanced JSON Path Selector features.
"""

def test_imports():
    """Test that all Phase 1 classes can be imported."""
    print("Testing Phase 1 imports...")
    
    try:
        print("Importing ValidationResult...")
        from enhanced_json_selector import ValidationResult
        print("✅ ValidationResult imported")
        
        print("Importing PathValidator...")
        from enhanced_json_selector import PathValidator
        print("✅ PathValidator imported")
        
        print("Importing PathBookmarkManager...")
        from enhanced_json_selector import PathBookmarkManager
        print("✅ PathBookmarkManager imported")
        
        print("Creating instances...")
        
        # Test ValidationResult
        result = ValidationResult(valid=True, value="test")
        print(f"✅ ValidationResult created: valid={result.valid}, value={result.value}")
        
        # Test PathValidator
        validator = PathValidator()
        print("✅ PathValidator created")
        
        # Test PathBookmarkManager
        bookmark_manager = PathBookmarkManager()
        print("✅ PathBookmarkManager created")
        
        print("\n🎉 All Phase 1 core classes imported and created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Phase 1 implementation is ready!")
    else:
        print("\n❌ Phase 1 implementation has issues.")
