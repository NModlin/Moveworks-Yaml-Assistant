# Troubleshooting Guide

Solutions to common issues and problems when using the Moveworks YAML Assistant.

## 🚨 Installation Issues

### Python Version Problems

**Issue**: "Python 3.10+ required" error
**Symptoms**: Application won't start, version error messages
**Solution**:
```bash
# Check your Python version
python --version

# If too old, install Python 3.10+ from python.org
# On macOS/Linux, try:
python3 --version
python3.10 --version
```

**Issue**: "python command not found"
**Solution**:
- **Windows**: Reinstall Python with "Add to PATH" checked
- **macOS**: Use `python3` instead of `python`
- **Linux**: Install Python: `sudo apt-get install python3.10`

### Dependency Installation Problems

**Issue**: PySide6 installation fails
**Solution**:
```bash
# Update pip first
python -m pip install --upgrade pip setuptools wheel

# Install PySide6 separately
pip install PySide6

# If still failing, clear cache
pip install --no-cache-dir PySide6
```

**Issue**: Permission denied during installation
**Solution**:
```bash
# Windows (run as Administrator or):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# macOS/Linux (don't use sudo with virtual environments):
# Fix permissions if needed:
sudo chown -R $USER ~/.local
```

### Virtual Environment Issues

**Issue**: Virtual environment not activating
**Solution**:
```bash
# Delete and recreate
rm -rf .venv  # or rmdir /s .venv on Windows
python -m venv .venv

# Activate properly
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Verify activation (should show .venv in path)
which python
```

## 🖥️ Application Launch Issues

### Application Won't Start

**Issue**: Application crashes on startup
**Symptoms**: Error messages, immediate exit, import errors
**Diagnostic Steps**:
```bash
# Test basic functionality
python run_app.py test

# Check for missing dependencies
python -c "import PySide6; print('PySide6 OK')"
python -c "import yaml; print('PyYAML OK')"

# Run with verbose output
python run_app.py gui --verbose
```

**Common Solutions**:
1. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
2. **Clear Python cache**: Delete `__pycache__` directories
3. **Check file permissions**: Ensure all files are readable
4. **Update graphics drivers**: For Qt/PySide6 display issues

### GUI Display Problems

**Issue**: Interface appears corrupted or blank
**Solution**:
- Update graphics drivers
- Try different display scaling settings
- Check Qt environment variables:
```bash
export QT_AUTO_SCREEN_SCALE_FACTOR=1
python run_app.py gui
```

**Issue**: Text is too small or too large
**Solution**:
- Adjust system display scaling
- Use application font size settings
- Check high DPI display settings

## ⚠️ Validation Errors

### Field Naming Issues

**Issue**: "Field names must use lowercase_snake_case"
**Examples of Invalid Names**: `actionName`, `Action-Name`, `Action Name`
**Correct Format**: `action_name`, `output_key`, `user_info`

**Solution**:
```yaml
# Wrong
actionName: my_action
outputKey: result

# Correct
action_name: my_action
output_key: result
```

### Required Field Errors

**Issue**: "Required field missing" validation errors
**Common Missing Fields**:
- `action_name` in action steps
- `output_key` in action/script steps
- `code` in script steps

**Solution**: Ensure all mandatory fields are filled:
```yaml
action:
  action_name: required_field  # ✅ Required
  output_key: required_field   # ✅ Required
  input_args:                  # ❓ Optional
    param: value
```

### Data Reference Errors

**Issue**: "Invalid data reference" errors
**Common Problems**:
- Typos in data paths: `data.user_inf` instead of `data.user_info`
- Missing step outputs: Referencing `data.step2` before step2 exists
- Incorrect syntax: `data[user_info]` instead of `data.user_info`

**Solution**:
```yaml
# Wrong
input_args:
  user_data: data.user_inf.user  # Typo
  
# Correct
input_args:
  user_data: data.user_info.user  # Correct reference
```

## 🔧 Workflow Building Issues

### JSON Path Selector Problems

**Issue**: JSON Path Selector shows "No data available"
**Solution**:
1. Add sample JSON data to a step
2. Click "Parse & Save JSON Output"
3. Ensure JSON is valid (use a JSON validator)
4. Refresh the JSON Path Selector

**Issue**: Selected paths don't work in workflow
**Solution**:
- Verify the step that generates the data exists
- Check that output_key matches the path prefix
- Ensure step order is correct (data must be generated before use)

### Script Validation Errors

**Issue**: "APIthon script exceeds 4096 bytes"
**Solution**:
- Simplify the script logic
- Remove unnecessary comments and whitespace
- Split complex operations into multiple script steps
- Use more concise Python syntax

**Issue**: "Import statements not allowed"
**Solution**:
```python
# Wrong
import json
import datetime

# Correct - use built-in functions only
data = {"timestamp": "2024-01-01"}
result = len(data)
```

**Issue**: "Script must return a value"
**Solution**:
```python
# Wrong
user_name = data.user.name
processed = user_name.upper()

# Correct
user_name = data.user.name
processed = user_name.upper()
return processed  # ✅ Always return a value
```

## 🎓 Tutorial System Issues

### Tutorial Won't Start

**Issue**: Tutorial menu is grayed out or unresponsive
**Solution**:
1. Ensure application is fully loaded
2. Close any open dialogs
3. Try restarting the application
4. Check console for error messages

**Issue**: Tutorial overlay doesn't appear
**Solution**:
- Resize the application window
- Check if tutorial panel is behind other windows
- Try different tutorial modules
- Restart tutorial system: `Tools` → `Tutorials` → `Reset Tutorial System`

### Copy-Paste Not Working

**Issue**: Copy buttons don't copy to clipboard
**Solution**:
1. Click the "📋 Copy to Clipboard" button (not just the text)
2. Check clipboard permissions in your browser/OS
3. Try manual copy-paste (Ctrl+C/Ctrl+V)
4. Ensure no other applications are blocking clipboard access

## 📊 Performance Issues

### Slow Application Response

**Issue**: Application becomes unresponsive or slow
**Symptoms**: Long delays, freezing interface, high CPU usage
**Solutions**:
1. **Reduce workflow complexity**: Simplify large workflows
2. **Clear application cache**: Restart the application
3. **Check system resources**: Close other applications
4. **Update dependencies**: `pip install -r requirements.txt --upgrade`

### Memory Usage Problems

**Issue**: High memory consumption
**Solutions**:
- Limit JSON data size in steps
- Avoid very large workflows (>50 steps)
- Restart application periodically during long sessions
- Close unused dialogs and panels

## 🔍 Debugging Techniques

### Enable Debug Mode

```bash
# Run with debug output
python run_app.py gui --debug

# Check log files (if available)
tail -f application.log
```

### Validate YAML Output

```bash
# Test generated YAML
python -c "import yaml; yaml.safe_load(open('workflow.yaml'))"

# Validate against Moveworks schema
python validate_workflow.py workflow.yaml
```

### Check Application State

```bash
# Verify installation
python run_app.py test

# Check component functionality
python test_core.py
python test_enhanced_features.py
```

## 📞 Getting Additional Help

### Before Seeking Help

1. **Check this troubleshooting guide** for your specific issue
2. **Review error messages carefully** - they often contain solution hints
3. **Try the basic solutions** (restart, reinstall, clear cache)
4. **Test with a simple workflow** to isolate the problem

### When Reporting Issues

Include this information:
- **Operating system and version**
- **Python version** (`python --version`)
- **Complete error message** (copy the full text)
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Screenshots** if relevant

### Support Channels

1. **Documentation**: Check all relevant documentation first
2. **FAQ**: Review frequently asked questions
3. **Issue Tracker**: Search existing issues in the project repository
4. **Community Forums**: Join discussions with other users
5. **Direct Support**: Contact maintainers for critical issues

### Self-Help Resources

- **[Installation Guide](installation.md)**: Complete setup instructions
- **[Quick Start Guide](quick-start.md)**: Basic usage guidance
- **[Expression Types Guide](expression-types.md)**: Detailed reference
- **[Interactive Tutorials](tutorials.md)**: Hands-on learning
- **[Template Library](templates.md)**: Working examples

---

*Still having issues? Check the [FAQ](faq.md) or contact support with detailed information about your problem.*
