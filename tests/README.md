# Test Suite Organization

This directory contains the comprehensive test suite for the Moveworks YAML Assistant, organized by test type and functionality.

## 📁 Directory Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── core/              # Core functionality tests
│   ├── validation/        # Validation system tests
│   ├── ui/                # UI component tests
│   └── utils/             # Utility function tests
├── integration/           # Integration tests for component interactions
│   ├── workflow/          # Workflow creation and management
│   ├── tutorial/          # Tutorial system integration
│   └── compliance/        # Compliance validation integration
├── ui/                    # User interface and GUI tests
│   ├── dialogs/           # Dialog and window tests
│   ├── widgets/           # Widget functionality tests
│   └── interactions/      # User interaction tests
├── demo/                  # Demo scripts and examples
│   ├── features/          # Feature demonstration scripts
│   ├── compliance/        # Compliance feature demos
│   └── workflows/         # Workflow example demos
├── validation/            # Validation and compliance tests
│   ├── apiton/            # APIthon script validation
│   ├── yaml/              # YAML generation validation
│   └── compliance/        # Moveworks compliance tests
├── fixtures/              # Test data and fixtures
│   ├── workflows/         # Sample workflow data
│   ├── json/              # Sample JSON data
│   └── yaml/              # Expected YAML outputs
├── performance/           # Performance and load tests
└── e2e/                   # End-to-end tests
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Tests for individual components in isolation:
- **Core**: Data structures, workflow management, YAML generation
- **Validation**: Individual validation functions and rules
- **UI**: Individual widget and component functionality
- **Utils**: Utility functions and helper methods

### Integration Tests (`tests/integration/`)
Tests for component interactions and system integration:
- **Workflow**: Complete workflow creation and processing
- **Tutorial**: Tutorial system with main application
- **Compliance**: Validation system integration with UI

### UI Tests (`tests/ui/`)
Tests for user interface functionality:
- **Dialogs**: Modal dialogs and windows
- **Widgets**: Custom widgets and controls
- **Interactions**: User interaction patterns

### Demo Scripts (`tests/demo/`)
Demonstration scripts showing feature usage:
- **Features**: Individual feature demonstrations
- **Compliance**: Compliance feature showcases
- **Workflows**: Complete workflow examples

### Validation Tests (`tests/validation/`)
Comprehensive validation and compliance testing:
- **APIthon**: Script validation and restrictions
- **YAML**: Output format validation
- **Compliance**: Moveworks specification adherence

## 🚀 Running Tests

### All Tests
```bash
# Run complete test suite
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# UI tests
python -m pytest tests/ui/

# Validation tests
python -m pytest tests/validation/
```

### Individual Test Files
```bash
# Run specific test file
python -m pytest tests/unit/core/test_core_structures.py

# Run with verbose output
python -m pytest tests/unit/core/test_core_structures.py -v
```

### Demo Scripts
```bash
# Run feature demonstrations
python tests/demo/features/demo_comprehensive_features.py

# Run compliance demonstrations
python tests/demo/compliance/demo_compliance_features.py
```

## 📋 Test Standards

### Naming Conventions
- **Test files**: `test_*.py` for pytest compatibility
- **Demo files**: `demo_*.py` for demonstration scripts
- **Validation files**: `validate_*.py` for validation scripts
- **Verification files**: `verify_*.py` for verification scripts

### Test Structure
```python
#!/usr/bin/env python3
"""
Test description and purpose.
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestComponentName:
    """Test class for ComponentName."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Test implementation
        pass
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test implementation
        pass
```

### Documentation Requirements
- Clear test descriptions and purposes
- Comprehensive docstrings for test functions
- Comments explaining complex test logic
- Expected outcomes and assertions documented

## 🔧 Test Configuration

### pytest Configuration
See `pytest.ini` in project root for configuration settings:
- Test discovery patterns
- Coverage settings
- Output formatting
- Plugin configurations

### Test Dependencies
Development dependencies in `requirements-dev.txt`:
- `pytest` - Testing framework
- `pytest-qt` - PySide6/Qt testing support
- `pytest-cov` - Coverage reporting
- Additional testing utilities

## 📊 Test Coverage

### Coverage Goals
- **Unit Tests**: 90%+ coverage for core components
- **Integration Tests**: 80%+ coverage for component interactions
- **UI Tests**: 70%+ coverage for user interface components
- **Overall**: 85%+ total coverage

### Coverage Reports
```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

## 🐛 Debugging Tests

### Verbose Output
```bash
# Run with detailed output
python -m pytest tests/ -v -s

# Show local variables on failure
python -m pytest tests/ --tb=long
```

### Interactive Debugging
```bash
# Drop into debugger on failure
python -m pytest tests/ --pdb

# Drop into debugger on first failure
python -m pytest tests/ -x --pdb
```

### Logging
```bash
# Show log output during tests
python -m pytest tests/ --log-cli-level=DEBUG
```

## 📝 Contributing Tests

### Adding New Tests
1. **Choose appropriate directory** based on test type
2. **Follow naming conventions** for consistency
3. **Include comprehensive docstrings** for clarity
4. **Add test data to fixtures** if needed
5. **Update this README** if adding new categories

### Test Quality Guidelines
- **Test one thing at a time** - focused, specific tests
- **Use descriptive names** - clear test purpose
- **Include edge cases** - test boundary conditions
- **Mock external dependencies** - isolated unit tests
- **Assert meaningful outcomes** - verify expected behavior

## 🔄 Continuous Integration

### Automated Testing
Tests are automatically run on:
- Pull request creation
- Code commits to main branch
- Scheduled daily runs
- Release preparation

### Test Requirements
- All tests must pass before merge
- Coverage thresholds must be maintained
- No new linting or formatting issues
- Documentation must be updated

---

*For specific test implementation details, see individual test files and their documentation.*
