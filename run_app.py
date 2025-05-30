#!/usr/bin/env python3
"""
Startup script for the Moveworks YAML Assistant.

This script provides a simple way to launch the application with proper
error handling and dependency checking.
"""

import sys
import subprocess
import importlib.util


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    if sys.version_info < (3, 10):
        print(f"Error: Python 3.10+ required, but you have {sys.version}")
        print("Please upgrade your Python installation.")
        return False
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        ('PySide6', 'PySide6'),
        ('yaml', 'PyYAML'),
        ('click', 'click')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        if importlib.util.find_spec(import_name) is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Error: Missing required dependencies:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing_packages)}")
        print("\nOr install all dependencies with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def run_gui():
    """Run the GUI application."""
    try:
        from main_gui import main
        print("Starting Moveworks YAML Assistant...")
        main()
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        return False
    except Exception as e:
        print(f"Error running application: {e}")
        return False
    
    return True


def run_cli():
    """Run the CLI application."""
    try:
        subprocess.run([sys.executable, "main_cli.py"] + sys.argv[2:])
    except Exception as e:
        print(f"Error running CLI: {e}")
        return False
    
    return True


def run_tests():
    """Run the core functionality tests."""
    try:
        subprocess.run([sys.executable, "test_core.py"])
    except Exception as e:
        print(f"Error running tests: {e}")
        return False
    
    return True


def show_help():
    """Show help information."""
    print("Moveworks YAML Assistant - Startup Script")
    print("=" * 50)
    print()
    print("Usage:")
    print("  python run_app.py [command]")
    print()
    print("Commands:")
    print("  gui     - Launch the desktop GUI application (default)")
    print("  cli     - Launch the command-line interface")
    print("  test    - Run core functionality tests")
    print("  help    - Show this help message")
    print()
    print("Examples:")
    print("  python run_app.py          # Launch GUI")
    print("  python run_app.py gui      # Launch GUI")
    print("  python run_app.py cli      # Launch CLI")
    print("  python run_app.py test     # Run tests")
    print()
    print("For CLI help:")
    print("  python run_app.py cli --help")


def main():
    """Main entry point."""
    # Parse command line arguments
    command = "gui"  # Default command
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    
    # Show help
    if command in ["help", "-h", "--help"]:
        show_help()
        return
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies (except for help and test commands)
    if command not in ["help", "test"]:
        if not check_dependencies():
            sys.exit(1)
    
    # Run the appropriate command
    if command == "gui":
        if not run_gui():
            sys.exit(1)
    elif command == "cli":
        if not run_cli():
            sys.exit(1)
    elif command == "test":
        if not run_tests():
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        print("Use 'python run_app.py help' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
