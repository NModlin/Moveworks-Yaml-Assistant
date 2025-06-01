# Installation Guide

Complete installation instructions for the Moveworks YAML Assistant.

## 📋 System Requirements

### Operating System
- **Windows**: Windows 10 or later (64-bit)
- **macOS**: macOS 10.15 (Catalina) or later
- **Linux**: Ubuntu 18.04+, CentOS 7+, or equivalent

### Python Requirements
- **Python 3.10 or higher** (required)
- **Python 3.11 or 3.12** (recommended for best performance)

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Display**: 1024x768 minimum resolution

## 🚀 Quick Installation

### Option 1: Automatic Setup (Recommended)

The easiest way to install and run the application:

```bash
# Download and extract the project
# Navigate to the project directory
cd moveworks-yaml-assistant

# Automatic setup and launch
python run_app.py --setup-only
```

This will automatically:
- ✅ Check Python version compatibility
- ✅ Create a virtual environment
- ✅ Install all required dependencies
- ✅ Verify the installation

### Option 2: Manual Installation

If you prefer manual control:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch application
python run_app.py gui
```

## 🔧 Detailed Installation Steps

### Step 1: Verify Python Installation

**Check your Python version:**
```bash
python --version
# Should show Python 3.10.x or higher
```

**If Python is not installed or too old:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart your terminal/command prompt

### Step 2: Download the Application

**Option A: Git Clone (if you have Git)**
```bash
git clone <repository-url>
cd moveworks-yaml-assistant
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to your desired location
3. Open terminal in the extracted folder

### Step 3: Create Virtual Environment

**Why use a virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Makes installation cleaner and more manageable

**Create the environment:**
```bash
python -m venv .venv
```

### Step 4: Activate Virtual Environment

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Verify activation:**
Your command prompt should show `(.venv)` at the beginning.

### Step 5: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install application dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- PySide6 (GUI framework)
- PyYAML (YAML processing)
- Click (CLI interface)
- Additional utility libraries

### Step 6: Verify Installation

```bash
# Test basic functionality
python run_app.py test

# Launch the GUI application
python run_app.py gui
```

## 🛠️ Development Installation

For developers who want to contribute:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional)
pre-commit install

# Run tests to verify everything works
python -m pytest
```

## 🚨 Troubleshooting

### Common Issues

#### "Python 3.10+ required"
**Problem**: Your Python version is too old
**Solution**: 
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Use `python3` instead of `python` on macOS/Linux

#### "Permission denied" during installation
**Windows Solution:**
```powershell
# Run as Administrator or:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux Solution:**
```bash
# Don't use sudo with pip in virtual environment
# If needed, fix permissions:
sudo chown -R $USER ~/.local
```

#### PySide6 installation fails
**Solution:**
```bash
# Update pip and tools first
python -m pip install --upgrade pip setuptools wheel

# Install PySide6 separately
pip install PySide6

# If still failing:
pip install --no-cache-dir PySide6
```

#### Virtual environment not working
**Solution:**
```bash
# Delete and recreate
rm -rf .venv  # or rmdir /s .venv on Windows
python -m venv .venv

# Reactivate and reinstall
source .venv/bin/activate  # or .venv\Scripts\activate
pip install -r requirements.txt
```

### Platform-Specific Issues

**Windows:**
- Use PowerShell or Command Prompt (not Git Bash)
- Ensure Windows Defender allows Python execution
- Consider using Windows Terminal for better experience

**macOS:**
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew Python if system Python causes issues

**Linux:**
- Install development headers: `sudo apt-get install python3-dev`
- For Qt dependencies: `sudo apt-get install qt6-base-dev`

### Network Issues

**Corporate Firewall:**
```bash
# Use proxy
pip install --proxy http://proxy.company.com:port -r requirements.txt

# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Python version 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] Application launches with `python run_app.py gui`
- [ ] No error messages in the console
- [ ] GUI interface appears and is responsive

## 🚀 Next Steps

After successful installation:

1. **[Quick Start Guide](quick-start.md)** - Get familiar with the interface
2. **[Interactive Tutorials](tutorials.md)** - Learn through hands-on practice
3. **[User Interface Overview](ui-overview.md)** - Understand the application layout

## 📞 Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review the [FAQ](faq.md)
3. Search existing issues in the project repository
4. Create a new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

---

*Installation complete? Continue with the [Quick Start Guide](quick-start.md)*
