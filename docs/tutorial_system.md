# 🎓 Unified Tutorial System Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Plugin System](#plugin-system)
4. [Migration Guide](#migration-guide)
5. [Creating Custom Plugins](#creating-custom-plugins)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🌟 Overview

The **Unified Tutorial System** is a comprehensive, plugin-based tutorial framework that replaces all legacy tutorial implementations in the Moveworks YAML Assistant. It provides:

- **Plugin-Based Architecture**: Modular, extensible design for easy maintenance
- **Visual Consistency**: Exact styling preservation (#4a86e8 colors, proper spacing)
- **Enhanced User Experience**: Resizable panels, position memory, copy-paste functionality
- **Complete Content Migration**: 100% preservation of all existing tutorials
- **Comprehensive Cleanup**: Systematic replacement of legacy systems

### Key Features

- ✅ **Non-blocking Interactive Overlay** with visual highlighting
- ✅ **Resizable Tutorial Panels** with smart positioning (400x300px minimum)
- ✅ **Copy-Paste Functionality** with visual feedback
- ✅ **Position Memory** using QSettings
- ✅ **Plugin Management** with import/reload capabilities
- ✅ **Category Organization** with tabbed interface
- ✅ **Comprehensive Migration** from all legacy systems

## 🏗️ Architecture

### Core Components

```
tutorials/
├── __init__.py                     # Package exports
├── unified_tutorial_system.py     # Core system implementation
├── plugins/                       # Tutorial plugins
│   ├── __init__.py
│   ├── legacy_tutorials.py        # Migrated from tutorial_system.py
│   ├── interactive_tutorials.py   # Migrated from integrated_tutorial_system.py
│   ├── comprehensive_tutorials.py # Migrated from comprehensive_tutorial_system.py
│   └── custom_plugins/            # User-added plugins
├── resources/                     # Tutorial assets
│   ├── images/
│   └── templates/
└── utils/                         # Migration utilities
    ├── __init__.py
    └── migration.py               # Migration tools
```

### Class Hierarchy

```python
# Core Classes
UnifiedTutorialManager          # Main controller
├── PluginManager              # Plugin discovery and loading
├── UnifiedTutorialOverlay     # Non-blocking UI overlay
└── UnifiedTutorialSelectionDialog  # Tutorial browser

# Data Classes
UnifiedTutorial                # Complete tutorial definition
└── UnifiedTutorialStep        # Individual tutorial step

# Plugin System
TutorialPlugin (ABC)           # Base plugin interface
├── LegacyTutorialPlugin      # Legacy system migration
├── InteractiveTutorialPlugin # Interactive system migration
└── ComprehensiveTutorialPlugin # Comprehensive system migration
```

## 🔌 Plugin System

### Plugin Interface

All tutorial plugins must inherit from `TutorialPlugin` and implement:

```python
class TutorialPlugin(ABC):
    @abstractmethod
    def get_plugin_id(self) -> str:
        """Return unique plugin identifier."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def get_tutorials(self) -> List[UnifiedTutorial]:
        """Return list of tutorials."""
        pass
```

### Plugin Discovery

The `PluginManager` automatically discovers plugins in the `tutorials/plugins/` directory:

1. **Auto-Discovery**: Scans for `.py` files in plugin directory
2. **Dynamic Loading**: Imports and instantiates plugin classes
3. **Validation**: Validates plugin structure and tutorials
4. **Caching**: Caches tutorials for efficient access

### Plugin Management

- **Import Plugins**: Add new plugins via file dialog
- **Reload Plugins**: Refresh plugins without restarting
- **Plugin Info**: View metadata and tutorial counts
- **Error Handling**: Graceful handling of plugin failures

## 🔄 Migration Guide

### Pre-Migration Checklist

1. **Backup Legacy Files**: Ensure all tutorial files are backed up
2. **Document Dependencies**: List all files importing legacy systems
3. **Test Current Functionality**: Verify all tutorials work before migration

### Migration Process

#### Step 1: Backup Legacy Systems

```python
from tutorials.utils.migration import backup_legacy_files

# Backup all legacy tutorial files
backup_legacy_files(source_dir=".", backup_dir="archive/tutorials")
```

#### Step 2: Update Import Statements

```python
from tutorials.utils.migration import update_import_statements

# Dry run to see what would be changed
results = update_import_statements(dry_run=True)

# Perform actual updates
results = update_import_statements(dry_run=False)
```

#### Step 3: Validate Migration

```python
from tutorials.utils.migration import validate_migration

# Check migration completeness
validation_results = validate_migration()
```

#### Step 4: Update Main GUI Integration

Replace legacy tutorial manager initialization:

```python
# OLD - Legacy systems
self.tutorial_manager = TutorialManager(self)
self.interactive_tutorial_manager = InteractiveTutorialManager(self)
self.comprehensive_tutorial_manager = TutorialIntegrationManager(self)

# NEW - Unified system
from tutorials import UnifiedTutorialManager
self.unified_tutorial_manager = UnifiedTutorialManager(self)
```

#### Step 5: Update Menu Integration

```python
# Update tutorial menu to use unified system
unified_tutorial_action = QAction("🎓 Interactive Tutorial System", self)
unified_tutorial_action.triggered.connect(self._show_unified_tutorials)

def _show_unified_tutorials(self):
    self.unified_tutorial_manager.show_tutorial_selection()
```

### Post-Migration Tasks

1. **Remove Legacy Files**: After validation, remove old tutorial files
2. **Update Documentation**: Update all references to new system
3. **Test All Tutorials**: Verify every tutorial works in new system
4. **User Communication**: Inform users about the new system

## 🛠️ Creating Custom Plugins

### Basic Plugin Template

```python
from typing import Dict, Any, List
from tutorials.unified_tutorial_system import (
    TutorialPlugin, UnifiedTutorial, UnifiedTutorialStep,
    TutorialCategory, TutorialDifficulty
)

class MyCustomPlugin(TutorialPlugin):
    def get_plugin_id(self) -> str:
        return "my_custom_plugin"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "My Custom Tutorial Plugin",
            "version": "1.0.0",
            "description": "Custom tutorials for specific workflows",
            "author": "Your Name",
            "tutorial_count": 1
        }
    
    def get_tutorials(self) -> List[UnifiedTutorial]:
        return [
            UnifiedTutorial(
                id="my_custom_tutorial",
                title="My Custom Tutorial",
                description="A custom tutorial example",
                category=TutorialCategory.CUSTOM,
                difficulty=TutorialDifficulty.BEGINNER,
                estimated_time="10 minutes",
                learning_objectives=["Learn custom workflow"],
                steps=[
                    UnifiedTutorialStep(
                        title="Welcome",
                        description="Welcome to my custom tutorial",
                        instruction="This is a custom tutorial step",
                        action_type="info"
                    )
                ]
            )
        ]
```

### Advanced Plugin Features

#### Copy-Paste Functionality

```python
UnifiedTutorialStep(
    title="Configure Action",
    description="Set up your action step",
    instruction="Copy the action name below",
    target_element="action_name_field",
    action_type="copy_paste",
    copy_paste_data="my.custom.action"
)
```

#### JSON Examples

```python
UnifiedTutorialStep(
    title="Add JSON Data",
    description="Provide sample JSON",
    instruction="Copy the JSON example",
    action_type="copy_paste",
    copy_paste_data='{"user": {"name": "John"}}',
    sample_json={"user": {"name": "John", "email": "john@example.com"}}
)
```

#### Target Element Highlighting

```python
UnifiedTutorialStep(
    title="Click Button",
    description="Click the specified button",
    instruction="Click the 'Add Action' button",
    target_element="add_action_btn",
    action_type="click",
    highlight_color="#4a86e8"  # Custom highlight color
)
```

### Plugin Installation

1. **Create Plugin File**: Save your plugin as `my_plugin.py`
2. **Import via UI**: Use "📥 Import Plugin" button in tutorial selection
3. **Manual Installation**: Copy to `tutorials/plugins/` directory
4. **Reload Plugins**: Use "🔄 Reload Plugin" to refresh

## 📚 API Reference

### UnifiedTutorialManager

Main controller class for the tutorial system.

#### Methods

- `show_tutorial_selection()`: Display tutorial selection dialog
- `start_tutorial(tutorial_id: str) -> bool`: Start specific tutorial
- `is_tutorial_active() -> bool`: Check if tutorial is running
- `get_current_tutorial_info() -> Optional[Dict]`: Get current tutorial status
- `reload_plugins()`: Reload all plugins
- `import_plugin(file_path: str) -> bool`: Import plugin from file

### PluginManager

Manages plugin discovery, loading, and lifecycle.

#### Methods

- `discover_plugins() -> List[str]`: Find available plugins
- `load_plugin(plugin_name: str) -> bool`: Load specific plugin
- `load_all_plugins() -> int`: Load all discovered plugins
- `get_all_tutorials() -> List[UnifiedTutorial]`: Get all tutorials
- `get_tutorials_by_category(category) -> List[UnifiedTutorial]`: Filter by category

### UnifiedTutorialOverlay

Non-blocking tutorial overlay with visual highlighting.

#### Features

- **Resizable Panels**: 400x300px minimum, 600x800px maximum
- **Smart Positioning**: Avoids covering target elements
- **Position Memory**: Remembers user preferences
- **Visual Highlighting**: Exact color matching (#4a86e8)
- **Copy-Paste Integration**: One-click copying with feedback

## ✨ Best Practices

### Plugin Development

1. **Use Descriptive IDs**: Plugin IDs should be unique and descriptive
2. **Provide Rich Metadata**: Include version, description, author information
3. **Validate Tutorial Structure**: Ensure all required fields are present
4. **Handle Errors Gracefully**: Implement proper error handling
5. **Test Thoroughly**: Verify all tutorial steps work correctly

### Tutorial Content

1. **Clear Learning Objectives**: Define what users will learn
2. **Progressive Difficulty**: Build complexity gradually
3. **Practical Examples**: Use real-world scenarios
4. **Copy-Paste Ready**: Provide ready-to-use examples
5. **Visual Guidance**: Use target elements and highlighting

### Visual Consistency

1. **Color Scheme**: Use #4a86e8 for primary elements, #f8f8f8 for backgrounds
2. **Typography**: 16px for titles, standard fonts for content
3. **Spacing**: 16px margins, 12px element spacing
4. **Icons**: Use consistent emoji icons for categories and actions

## 🔧 Troubleshooting

### Common Issues

#### Plugin Loading Failures

**Problem**: Plugin fails to load
**Solution**: 
1. Check plugin syntax and imports
2. Verify plugin class inherits from `TutorialPlugin`
3. Ensure all required methods are implemented
4. Check console output for specific errors

#### Import Statement Errors

**Problem**: Legacy import statements still exist
**Solution**:
```python
from tutorials.utils.migration import find_import_statements
legacy_imports = find_import_statements()
# Review and update remaining imports
```

#### Tutorial Not Found

**Problem**: Tutorial ID not found when starting
**Solution**:
1. Verify plugin is loaded correctly
2. Check tutorial ID matches exactly
3. Reload plugins if recently added

#### Visual Styling Issues

**Problem**: Tutorial panels don't match expected styling
**Solution**:
1. Verify color codes (#4a86e8, #f8f8f8)
2. Check CSS syntax in style sheets
3. Ensure proper spacing values (16px, 12px)

### Debug Mode

Enable debug output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Plugin manager will output detailed loading information
plugin_manager = PluginManager()
plugin_manager.load_all_plugins()
```

### Migration Validation

If migration validation fails:

```python
from tutorials.utils.migration import validate_migration
results = validate_migration()

# Check specific issues
if not results['validation_passed']:
    print("Legacy imports found:", results['legacy_imports_found'])
    print("Plugin status:", results['plugin_status'])
```

## 📞 Support

For issues with the unified tutorial system:

1. **Check Documentation**: Review this guide and API reference
2. **Run Validation**: Use migration utilities to check system state
3. **Check Console Output**: Look for error messages and warnings
4. **Test with Simple Plugin**: Create minimal plugin to isolate issues
5. **Review Legacy Backup**: Compare with archived legacy systems if needed

The unified tutorial system provides a robust, maintainable foundation for tutorial content while preserving all existing functionality and improving the user experience.
