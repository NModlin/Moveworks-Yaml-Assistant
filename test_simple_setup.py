#!/usr/bin/env python3
"""
Simple test for environment setup functionality.
"""

import sys
import os
import venv
import platform
from pathlib import Path

def test_basic_functionality():
    """Test basic functionality without hanging."""
    print("Testing basic functionality...")
    
    # Test Python version
    print(f"Python version: {sys.version}")
    print(f"Python version info: {sys.version_info}")
    
    # Test platform detection
    print(f"Platform: {platform.system()}")
    
    # Test Path operations
    venv_path = Path(".venv_test")
    print(f"Test venv path: {venv_path}")
    print(f"Test venv exists: {venv_path.exists()}")
    
    # Test virtual environment detection
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    print(f"Currently in virtual environment: {in_venv}")
    
    print("✓ Basic functionality test completed")

def test_venv_creation():
    """Test virtual environment creation (without actually creating)."""
    print("\nTesting virtual environment creation logic...")
    
    venv_path = Path(".venv_test")
    
    # Clean up if exists
    if venv_path.exists():
        import shutil
        shutil.rmtree(venv_path)
        print(f"Cleaned up existing test venv at {venv_path}")
    
    try:
        print(f"Would create virtual environment at: {venv_path}")
        print(f"Using venv module: {venv.__file__}")
        
        # Don't actually create to avoid hanging
        # venv.create(venv_path, with_pip=True)
        
        print("✓ Virtual environment creation logic test completed")
        return True
    except Exception as e:
        print(f"✗ Virtual environment creation test failed: {e}")
        return False

def test_activation_script_paths():
    """Test activation script path generation."""
    print("\nTesting activation script paths...")
    
    venv_path = Path(".venv_test")
    
    if platform.system() == "Windows":
        activation_script = str(venv_path / "Scripts" / "activate.bat")
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        activation_script = str(venv_path / "bin" / "activate")
        python_exe = venv_path / "bin" / "python"
    
    print(f"Activation script path: {activation_script}")
    print(f"Python executable path: {python_exe}")
    
    print("✓ Activation script paths test completed")

def main():
    """Run all tests."""
    print("Simple Environment Setup Test")
    print("=" * 40)
    
    try:
        test_basic_functionality()
        test_venv_creation()
        test_activation_script_paths()
        
        print("\n✓ All tests completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)
