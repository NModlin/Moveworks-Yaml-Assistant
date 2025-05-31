#!/usr/bin/env python3
"""
Test script for environment setup functionality.
"""

import sys
import os
from pathlib import Path

# Add current directory to path to import run_app
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that we can import the enhanced run_app functions."""
    print("Testing imports...")
    try:
        from run_app import (
            check_python_version,
            get_venv_path,
            is_in_venv,
            get_activation_script,
            print_status,
            print_header
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_python_version():
    """Test Python version checking."""
    print("\nTesting Python version check...")
    try:
        from run_app import check_python_version
        result = check_python_version()
        print(f"✓ Python version check result: {result}")
        return True
    except Exception as e:
        print(f"✗ Python version check error: {e}")
        return False

def test_venv_detection():
    """Test virtual environment detection."""
    print("\nTesting virtual environment detection...")
    try:
        from run_app import is_in_venv, get_venv_path, get_activation_script
        
        in_venv = is_in_venv()
        venv_path = get_venv_path()
        activation_script = get_activation_script()
        
        print(f"✓ In virtual environment: {in_venv}")
        print(f"✓ Virtual environment path: {venv_path}")
        print(f"✓ Activation script: {activation_script}")
        return True
    except Exception as e:
        print(f"✗ Virtual environment detection error: {e}")
        return False

def test_dependency_check():
    """Test dependency checking."""
    print("\nTesting dependency check...")
    try:
        from run_app import check_dependencies
        result = check_dependencies()
        print(f"✓ Dependency check result: {result}")
        return True
    except Exception as e:
        print(f"✗ Dependency check error: {e}")
        return False

def test_color_output():
    """Test colored output functions."""
    print("\nTesting colored output...")
    try:
        from run_app import print_status, print_header
        
        print_header("Test Header")
        print_status("Success message", "success")
        print_status("Error message", "error")
        print_status("Warning message", "warning")
        print_status("Info message", "info")
        print("✓ Colored output test completed")
        return True
    except Exception as e:
        print(f"✗ Colored output error: {e}")
        return False

def main():
    """Run all tests."""
    print("Environment Setup Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_python_version,
        test_venv_detection,
        test_dependency_check,
        test_color_output
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
