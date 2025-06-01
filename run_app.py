#!/usr/bin/env python3
"""
Enhanced Startup Script for the Moveworks YAML Assistant.

This script provides comprehensive environment management including:
- Automatic virtual environment detection and creation
- Dependency installation with proper error handling
- Platform-specific activation script handling
- Colored console output with progress indicators
- Setup-only mode for environment preparation
"""

import sys
import os
import subprocess
import importlib.util
import venv
import platform
from pathlib import Path
from typing import Optional, List, Tuple


# Color output utilities
class Colors:
    """ANSI color codes for console output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not supported."""
        if platform.system() == "Windows":
            # Try to enable ANSI support on Windows 10+
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # Fallback: disable colors
                for attr in dir(Colors):
                    if not attr.startswith('_') and attr != 'disable_on_windows':
                        setattr(Colors, attr, '')


def print_status(message: str, status: str = "info", prefix: str = ""):
    """Print a status message with color coding."""
    Colors.disable_on_windows()

    if status == "success":
        icon = f"{Colors.GREEN}✓{Colors.END}"
    elif status == "error":
        icon = f"{Colors.RED}✗{Colors.END}"
    elif status == "warning":
        icon = f"{Colors.YELLOW}⚠{Colors.END}"
    elif status == "info":
        icon = f"{Colors.BLUE}ℹ{Colors.END}"
    else:
        icon = ""

    print(f"{prefix}{icon} {message}")


def print_header(title: str):
    """Print a formatted header."""
    Colors.disable_on_windows()
    print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * len(title)}{Colors.END}")


def check_python_version() -> bool:
    """Check if Python version is 3.10 or higher."""
    if sys.version_info < (3, 10):
        print_status(f"Python 3.10+ required, but you have {sys.version}", "error")
        print_status("Please upgrade your Python installation.", "info", "  ")
        return False

    print_status(f"Python {sys.version.split()[0]} detected", "success")
    return True


def get_venv_path() -> Path:
    """Get the path to the virtual environment directory."""
    return Path(".venv")


def is_in_venv() -> bool:
    """Check if currently running in a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


def get_activation_script() -> str:
    """Get the appropriate activation script path for the current platform."""
    venv_path = get_venv_path()

    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "activate.bat")
    else:
        return str(venv_path / "bin" / "activate")


def create_virtual_environment() -> bool:
    """Create a virtual environment in the .venv directory."""
    venv_path = get_venv_path()

    if venv_path.exists():
        print_status(f"Virtual environment already exists at {venv_path}", "info")
        return True

    try:
        print_status(f"Creating virtual environment at {venv_path}...", "info")
        venv.create(venv_path, with_pip=True)
        print_status("Virtual environment created successfully", "success")
        return True
    except Exception as e:
        print_status(f"Failed to create virtual environment: {e}", "error")
        return False


def install_dependencies() -> bool:
    """Install dependencies from requirements.txt."""
    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print_status("requirements.txt not found", "error")
        return False

    # Get the appropriate Python executable
    venv_path = get_venv_path()
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        print_status(f"Python executable not found at {python_exe}", "error")
        return False

    try:
        print_status("Installing dependencies from requirements.txt...", "info")
        result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            check=True
        )
        print_status("Dependencies installed successfully", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {e}", "error")
        if e.stdout:
            print_status(f"stdout: {e.stdout}", "info", "  ")
        if e.stderr:
            print_status(f"stderr: {e.stderr}", "error", "  ")
        return False
    except Exception as e:
        print_status(f"Unexpected error during installation: {e}", "error")
        return False


def setup_environment() -> bool:
    """Set up the complete environment (venv + dependencies)."""
    print_header("Environment Setup")

    # Check Python version first
    if not check_python_version():
        return False

    # Create virtual environment if needed
    if not create_virtual_environment():
        return False

    # Install dependencies
    if not install_dependencies():
        return False

    print_status("Environment setup completed successfully!", "success")

    # Show activation instructions
    activation_script = get_activation_script()
    print_status("To activate the virtual environment manually:", "info")
    if platform.system() == "Windows":
        print_status(f"  {activation_script}", "info", "  ")
    else:
        print_status(f"  source {activation_script}", "info", "  ")

    return True


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    required_packages = [
        ('PySide6', 'PySide6'),
        ('yaml', 'PyYAML'),
        ('click', 'click')
    ]

    missing_packages = []
    available_packages = []

    for import_name, package_name in required_packages:
        if importlib.util.find_spec(import_name) is None:
            missing_packages.append(package_name)
        else:
            available_packages.append(package_name)

    # Report available packages
    for package in available_packages:
        print_status(f"{package} is available", "success")

    if missing_packages:
        print_status("Missing required dependencies:", "error")
        for package in missing_packages:
            print_status(f"{package}", "error", "  - ")

        print_status("Install them with:", "info")
        print_status(f"pip install {' '.join(missing_packages)}", "info", "  ")
        print_status("Or install all dependencies with:", "info")
        print_status("pip install -r requirements.txt", "info", "  ")

        # Suggest using setup mode
        print_status("Or run environment setup:", "info")
        print_status("python run_app.py --setup-only", "info", "  ")
        return False

    print_status("All required dependencies are available", "success")
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
        subprocess.run([sys.executable, "run_tests.py", "--unit"])
    except Exception as e:
        print(f"Error running tests: {e}")
        return False
    
    return True


def show_help():
    """Show help information."""
    print_header("Moveworks YAML Assistant - Enhanced Startup Script")
    print()
    print("Usage:")
    print("  python run_app.py [command] [options]")
    print()
    print("Commands:")
    print("  gui         - Launch the desktop GUI application (default)")
    print("  cli         - Launch the command-line interface")
    print("  test        - Run core functionality tests")
    print("  setup       - Set up virtual environment and dependencies")
    print("  help        - Show this help message")
    print()
    print("Options:")
    print("  --setup-only    - Set up environment without running the app")
    print("  --force-setup   - Force recreation of virtual environment")
    print()
    print("Examples:")
    print("  python run_app.py                    # Launch GUI")
    print("  python run_app.py gui                # Launch GUI")
    print("  python run_app.py cli                # Launch CLI")
    print("  python run_app.py test               # Run tests")
    print("  python run_app.py setup              # Set up environment")
    print("  python run_app.py --setup-only       # Set up environment only")
    print("  python run_app.py gui --setup-only   # Set up then launch GUI")
    print()
    print("Environment Management:")
    print("  The script automatically detects and manages virtual environments.")
    print("  If no virtual environment is found, it will create one in .venv/")
    print("  Dependencies are automatically installed from requirements.txt")
    print()
    print("For CLI help:")
    print("  python run_app.py cli --help")


def main():
    """Main entry point."""
    # Parse command line arguments
    args = sys.argv[1:]
    command = "gui"  # Default command
    setup_only = False
    force_setup = False

    # Parse arguments
    filtered_args = []
    for arg in args:
        if arg == "--setup-only":
            setup_only = True
        elif arg == "--force-setup":
            force_setup = True
        elif arg.startswith("-"):
            if arg in ["-h", "--help"]:
                show_help()
                return
            else:
                print_status(f"Unknown option: {arg}", "error")
                print_status("Use 'python run_app.py help' for usage information.", "info")
                sys.exit(1)
        else:
            filtered_args.append(arg)

    # Get command
    if filtered_args:
        command = filtered_args[0].lower()

    # Show help
    if command in ["help", "-h", "--help"]:
        show_help()
        return

    # Handle setup command or setup-only flag
    if command == "setup" or setup_only:
        if force_setup:
            venv_path = get_venv_path()
            if venv_path.exists():
                print_status(f"Removing existing virtual environment at {venv_path}...", "info")
                import shutil
                shutil.rmtree(venv_path)

        if not setup_environment():
            sys.exit(1)

        if setup_only:
            print_status("Environment setup completed. You can now run the application.", "success")
            return
        elif command == "setup":
            return

    # Check Python version
    print_header("Moveworks YAML Assistant")
    if not check_python_version():
        sys.exit(1)

    # Check if we're in a virtual environment
    if not is_in_venv():
        venv_path = get_venv_path()
        if venv_path.exists():
            print_status("Virtual environment detected but not activated", "warning")
            activation_script = get_activation_script()
            print_status("Please activate it first:", "info")
            if platform.system() == "Windows":
                print_status(f"  {activation_script}", "info", "  ")
            else:
                print_status(f"  source {activation_script}", "info", "  ")
            print_status("Or run with --setup-only to use automatic management", "info")
        else:
            print_status("No virtual environment found", "warning")
            print_status("Run with --setup-only to create one automatically", "info")

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
        print_status(f"Unknown command: {command}", "error")
        print_status("Use 'python run_app.py help' for usage information.", "info")
        sys.exit(1)


if __name__ == "__main__":
    main()
