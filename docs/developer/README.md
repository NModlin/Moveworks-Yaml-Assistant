# Developer Documentation

This directory contains technical documentation for developers working on or extending the Moveworks YAML Assistant.

## 📚 Documentation Structure

### Architecture & Design
- **[Architecture Overview](architecture.md)** - System design and components
- **[Core Structures](core-structures.md)** - Data models and workflow structures
- **[UI Framework](ui-framework.md)** - PySide6 implementation details
- **[Plugin System](plugin-system.md)** - Extensibility architecture

### API Reference
- **[Core API](api-reference.md)** - Main application APIs
- **[Validation API](validation-api.md)** - Validation system interfaces
- **[Tutorial API](tutorial-api.md)** - Tutorial system development
- **[Template API](template-api.md)** - Template system interfaces

### Development Guides
- **[Contributing Guide](contributing.md)** - How to contribute to the project
- **[Development Setup](development-setup.md)** - Development environment setup
- **[Testing Guide](testing.md)** - Testing strategies and frameworks
- **[Code Style Guide](code-style.md)** - Coding standards and conventions

### Extension Development
- **[Creating Plugins](creating-plugins.md)** - Plugin development guide
- **[Custom Validators](custom-validators.md)** - Extending validation system
- **[Custom Templates](custom-templates.md)** - Template development
- **[UI Extensions](ui-extensions.md)** - Extending the user interface

### Implementation Details
- **[YAML Generation](yaml-generation.md)** - YAML output system
- **[Validation System](validation-implementation.md)** - Validation architecture
- **[Data Flow](data-flow.md)** - Application data flow patterns
- **[Error Handling](error-handling.md)** - Error management strategies

## 🛠️ Development Environment

### Prerequisites
- Python 3.10+
- PySide6
- Development dependencies (see requirements-dev.txt)

### Quick Setup
```bash
# Clone and setup
git clone <repository>
cd moveworks-yaml-assistant

# Setup development environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Start development server
python run_app.py gui
```

## 🧪 Testing

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **UI Tests**: User interface testing
- **End-to-End Tests**: Complete workflow testing

### Running Tests
```bash
# All tests
python -m pytest

# Specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/ui/

# With coverage
python -m pytest --cov=. --cov-report=html
```

## 📦 Project Structure

```
moveworks-yaml-assistant/
├── core_structures.py          # Data models
├── main_gui.py                 # Main application
├── yaml_generator.py           # YAML output
├── validator.py                # Validation system
├── enhanced_*/                 # Enhanced features
├── tutorials/                  # Tutorial system
├── templates/                  # Template library
├── tests/                      # Test suite
└── docs/                       # Documentation
```

## 🔧 Key Components

### Core Engine
- **Workflow Management**: Creating and managing workflows
- **Expression Handling**: All 8 Moveworks expression types
- **Data Context**: Managing data flow and references
- **YAML Generation**: Compliant output generation

### Validation System
- **Compliance Validation**: Moveworks specification compliance
- **Real-time Validation**: Live feedback during editing
- **Error Reporting**: Detailed error messages and suggestions
- **Auto-fix Capabilities**: Automated correction suggestions

### User Interface
- **PySide6 Framework**: Modern Qt-based interface
- **Responsive Design**: Adaptive layout system
- **Accessibility**: Screen reader and keyboard navigation support
- **Theming**: Consistent visual design system

## 📋 Development Guidelines

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints for all public APIs
- Write comprehensive docstrings
- Maintain test coverage above 80%

### Git Workflow
- Use feature branches for development
- Write clear commit messages
- Include tests with all changes
- Update documentation for new features

### Documentation
- Update relevant documentation with changes
- Include examples in API documentation
- Maintain changelog for releases
- Write clear error messages

## 🚀 Release Process

1. **Feature Development**: Implement and test features
2. **Documentation Update**: Update all relevant documentation
3. **Testing**: Run comprehensive test suite
4. **Version Bump**: Update version numbers
5. **Release Notes**: Document changes and improvements
6. **Deployment**: Package and distribute release

## 📞 Support

### Getting Help
- Review existing documentation
- Check the issue tracker
- Join developer discussions
- Contact maintainers

### Contributing
- Read the [Contributing Guide](contributing.md)
- Follow the development setup instructions
- Submit pull requests with tests and documentation
- Participate in code reviews

---

*For user-focused documentation, see [User Documentation](../user/)*
