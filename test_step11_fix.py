#!/usr/bin/env python3
"""
Test script to verify Step 11 fix for the tutorial system.
"""

import sys
from PySide6.QtWidgets import QApplication
from main_gui import MainWindow
from integrated_tutorial_system import InteractiveTutorialManager

def test_step11_fix():
    """Test that Step 11 can find and populate the JSON tree."""
    print("🧪 Testing Step 11 Fix")
    print("=" * 50)
    
    # Create application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    
    # Create tutorial manager
    tutorial_manager = InteractiveTutorialManager(window)
    
    # Test finding the JSON tree widget
    print("\n1. Testing JSON tree widget discovery:")
    json_tree = tutorial_manager._find_json_tree_widget()
    if json_tree:
        print(f"   ✅ Found JSON tree: {json_tree.__class__.__name__}")
        print(f"   📋 Object name: {json_tree.objectName()}")
        print(f"   🔧 Has populate_from_json: {hasattr(json_tree, 'populate_from_json')}")
    else:
        print(f"   ❌ JSON tree not found")
    
    # Test finding the enhanced JSON panel
    print("\n2. Testing enhanced JSON panel:")
    if hasattr(window, 'enhanced_json_panel'):
        panel = window.enhanced_json_panel
        print(f"   ✅ Found enhanced JSON panel: {panel.__class__.__name__}")
        print(f"   🔧 Has json_tree: {hasattr(panel, 'json_tree')}")
        print(f"   🔧 Has set_workflow: {hasattr(panel, 'set_workflow')}")
        print(f"   🔧 Has step_combo: {hasattr(panel, 'step_combo')}")
        
        # List available attributes
        attrs = [attr for attr in dir(panel) if not attr.startswith('_')]
        tree_attrs = [attr for attr in attrs if 'tree' in attr.lower()]
        print(f"   📋 Tree-related attributes: {tree_attrs}")
    else:
        print(f"   ❌ Enhanced JSON panel not found")
    
    # Test tab finding
    print("\n3. Testing tab discovery:")
    json_explorer_tab = tutorial_manager._find_tab("🔍 JSON Explorer")
    if json_explorer_tab:
        print(f"   ✅ Found JSON Explorer tab: {json_explorer_tab.__class__.__name__}")
    else:
        print(f"   ❌ JSON Explorer tab not found")
    
    yaml_preview_tab = tutorial_manager._find_tab("📄 YAML Preview")
    if yaml_preview_tab:
        print(f"   ✅ Found YAML Preview tab: {yaml_preview_tab.__class__.__name__}")
    else:
        print(f"   ❌ YAML Preview tab not found")
    
    print("\n✅ Test complete!")
    return window, tutorial_manager

if __name__ == "__main__":
    window, tutorial_manager = test_step11_fix()
    print("\n💡 You can now test the tutorial manually:")
    print("   1. Go to Tools > Tutorials > Interactive Basic Workflow")
    print("   2. Follow the tutorial to Step 11")
    print("   3. Check if the JSON tree is populated")
    
    # Show the window for manual testing
    window.show()
    
    # Don't exit immediately in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        sys.exit(QApplication.instance().exec())
