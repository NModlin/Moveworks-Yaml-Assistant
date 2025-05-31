# Environment Setup Guide

This guide provides comprehensive instructions for setting up the Moveworks YAML Assistant development and runtime environment.

## 📋 Prerequisites

### Python Version Requirements
- **Python 3.10 or higher** is required
- Python 3.11 or 3.12 recommended for best performance

### Verify Python Installation

**Windows (PowerShell/Command Prompt):**
```powershell
python --version
# or
python3 --version
```

**macOS/Linux (Terminal):**
```bash
python3 --version
```

**Expected Output:**
```
Python 3.10.x (or higher)
```

If Python is not installed or the version is too old, download from [python.org](https://www.python.org/downloads/).

## 🚀 Quick Setup (Recommended)

The easiest way to set up the environment is using the enhanced startup script:

```bash
# Automatic environment setup and launch
python run_app.py --setup-only

# Or setup and run GUI immediately
python run_app.py gui --setup-only
```

This will:
1. ✅ Check Python version compatibility
2. ✅ Create virtual environment in `.venv/`
3. ✅ Install all required dependencies
4. ✅ Provide activation instructions

## 🔧 Manual Setup

If you prefer manual control or the automatic setup fails:

### Step 1: Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Navigate to project directory
cd path\to\moveworks-yaml-assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
# Navigate to project directory
cd path\to\moveworks-yaml-assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
# Navigate to project directory
cd path/to/moveworks-yaml-assistant

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# For development (optional)
pip install -r requirements-dev.txt
```

### Step 3: Verify Installation

```bash
# Test basic functionality
python run_app.py test

# Launch GUI application
python run_app.py gui
```

## 🛠️ Development Environment

For contributors and developers:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=.

# Format code
black .
isort .

# Type checking
mypy .
```

## 🔍 Environment Verification

Use this checklist to verify your environment:

### ✅ Python Version Check
```bash
python --version
# Should show Python 3.10.x or higher
```

### ✅ Virtual Environment Check
```bash
# Should show path containing .venv
python -c "import sys; print(sys.prefix)"
```

### ✅ Dependencies Check
```bash
# Test critical imports
python -c "import PySide6; print('PySide6 OK')"
python -c "import yaml; print('PyYAML OK')"
python -c "import click; print('Click OK')"
```

### ✅ Application Launch Test
```bash
# Should launch without errors
python run_app.py gui
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue: "Python 3.10+ required"
**Solution:**
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. On Windows, ensure Python is added to PATH during installation
3. Use `python3` instead of `python` on macOS/Linux

#### Issue: "Permission denied" during installation
**Windows Solution:**
```powershell
# Run PowerShell as Administrator, or use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux Solution:**
```bash
# Don't use sudo with pip in virtual environment
# If needed, fix permissions:
sudo chown -R $USER ~/.local
```

#### Issue: PySide6 installation fails
**Solution:**
```bash
# Update pip and setuptools first
python -m pip install --upgrade pip setuptools wheel

# Install PySide6 separately
pip install PySide6

# If still failing, try:
pip install --no-cache-dir PySide6
```

#### Issue: "Virtual environment not activated"
**Solution:**
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Verify activation
python -c "import sys; print('venv' in sys.prefix)"
```

#### Issue: Import errors after installation
**Solution:**
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Network Issues

If you're behind a corporate firewall:

```bash
# Use corporate proxy
pip install --proxy http://proxy.company.com:port -r requirements.txt

# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

### Platform-Specific Notes

**Windows:**
- Use PowerShell or Command Prompt (not Git Bash for activation)
- Ensure Windows Defender doesn't block Python execution
- Consider using Windows Terminal for better experience

**macOS:**
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew Python if system Python is problematic

**Linux:**
- Install development headers: `sudo apt-get install python3-dev`
- For Qt dependencies: `sudo apt-get install qt6-base-dev`

## 📞 Getting Help

If you continue to experience issues:

1. **Check the console output** for specific error messages
2. **Run with verbose output**: `python run_app.py --setup-only -v`
3. **Check system requirements** in README.md
4. **Search existing issues** in the project repository
5. **Create a new issue** with:
   - Operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

## 🔗 Additional Resources

- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Project README](README.md)
