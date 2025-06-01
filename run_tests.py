#!/usr/bin/env python3
"""
Comprehensive test runner for the Moveworks YAML Assistant.

This script provides convenient ways to run different categories of tests
and generate coverage reports.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        print(f"\n🔍 {description}")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ Success")
        return True
    else:
        print(f"❌ Failed with exit code {result.returncode}")
        return False

def run_tests(test_path="tests/", markers=None, verbose=True, coverage=False, html_report=False):
    """Run tests with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
        if html_report:
            cmd.append("--cov-report=html")
    
    cmd.append(test_path)
    
    description = f"Running tests in {test_path}"
    if markers:
        description += f" with markers: {', '.join(markers)}"
    
    return run_command(cmd, description)

def run_demo_scripts():
    """Run demo scripts to verify functionality."""
    demo_dir = Path("tests/demo")
    if not demo_dir.exists():
        print("❌ Demo directory not found")
        return False
    
    success_count = 0
    total_count = 0
    
    for demo_file in demo_dir.rglob("demo_*.py"):
        total_count += 1
        print(f"\n🎬 Running demo: {demo_file.name}")
        
        cmd = ["python", str(demo_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {demo_file.name} completed successfully")
            success_count += 1
        else:
            print(f"❌ {demo_file.name} failed")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}...")
    
    print(f"\n📊 Demo Results: {success_count}/{total_count} demos passed")
    return success_count == total_count

def check_test_environment():
    """Check if the test environment is properly set up."""
    print("🔧 Checking test environment...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required packages
    required_packages = ["pytest", "PySide6", "yaml"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not found")
            return False
    
    # Check test directory structure
    test_dirs = ["tests/unit", "tests/integration", "tests/ui", "tests/demo", "tests/validation"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"✅ {test_dir} directory exists")
        else:
            print(f"⚠️ {test_dir} directory missing")
    
    return True

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run Moveworks YAML Assistant tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests only
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --demo             # Run demo scripts
  python run_tests.py --check            # Check test environment
  python run_tests.py --quick            # Run quick tests only
        """
    )
    
    # Test category options
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--ui", action="store_true", help="Run UI tests only")
    parser.add_argument("--demo", action="store_true", help="Run demo scripts")
    parser.add_argument("--validation", action="store_true", help="Run validation tests only")
    
    # Test filtering options
    parser.add_argument("--quick", action="store_true", help="Run quick tests only (exclude slow)")
    parser.add_argument("--slow", action="store_true", help="Run slow tests only")
    parser.add_argument("--markers", nargs="+", help="Run tests with specific markers")
    
    # Output options
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    
    # Environment options
    parser.add_argument("--check", action="store_true", help="Check test environment setup")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    
    args = parser.parse_args()
    
    # Check environment if requested
    if args.check:
        success = check_test_environment()
        return 0 if success else 1
    
    # Install dependencies if requested
    if args.install_deps:
        cmd = ["pip", "install", "-r", "requirements-dev.txt"]
        success = run_command(cmd, "Installing test dependencies")
        return 0 if success else 1
    
    print("🧪 MOVEWORKS YAML ASSISTANT - TEST RUNNER")
    print("=" * 50)
    
    # Determine what to run
    success = True
    
    if args.demo:
        success &= run_demo_scripts()
    elif args.unit:
        success &= run_tests("tests/unit/", verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    elif args.integration:
        success &= run_tests("tests/integration/", verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    elif args.ui:
        success &= run_tests("tests/ui/", verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    elif args.validation:
        success &= run_tests("tests/validation/", verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    elif args.quick:
        markers = ["not slow"]
        success &= run_tests("tests/", markers=markers, verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    elif args.slow:
        markers = ["slow"]
        success &= run_tests("tests/", markers=markers, verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    elif args.markers:
        success &= run_tests("tests/", markers=args.markers, verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    else:
        # Run all tests
        success &= run_tests("tests/", verbose=not args.quiet, coverage=args.coverage, html_report=args.html)
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        if args.coverage and args.html:
            print("📊 Coverage report generated: htmlcov/index.html")
    else:
        print("❌ Some tests failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
