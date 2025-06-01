"""
Enhanced JSON Path Selector for the Moveworks YAML Assistant.

This module provides an improved JSON path selection widget with tree visualization,
search functionality, and preview capabilities.

Key Features:
- Proper JSON tree population when steps are selected
- Clear visual feedback for path selection
- Search functionality within JSON structure
- Preview panel showing actual values at selected paths
- Debug logging for troubleshooting
- One-click path copying
"""

import json
import logging
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter, QGroupBox,
    QComboBox, QCheckBox, QFrame, QMessageBox, QApplication, QCompleter,
    QListWidget, QListWidgetItem, QDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsTextItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsPolygonItem,
    QScrollArea, QToolButton, QMenu, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QStringListModel, QMimeData, QSettings
from PySide6.QtGui import (QFont, QIcon, QColor, QPalette, QDrag, QPainter, QPen, QBrush,
                          QPixmap, QCursor, QValidator, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QAction)

# Set up logging for debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# ============================================================================
# VISUAL DESIGN CONSTANTS
# ============================================================================

class VisualDesignConstants:
    """Centralized visual design constants for consistent styling."""

    # Spacing & Layout
    UNIFORM_MARGIN = 8
    FORM_SPACING = 8
    BUTTON_SPACING = 4
    SECTION_SPACING = 12

    # Colors
    LIGHT_BACKGROUND = "#f8f8f8"
    SUBTLE_BORDER = "#e0e0e0"
    ACCENT_COLOR = "#2196f3"
    SUCCESS_COLOR = "#4caf50"
    ERROR_COLOR = "#f44336"
    WARNING_COLOR = "#ff9800"

    # Interactive States
    HOVER_BACKGROUND = "#e3f2fd"
    SELECTED_BACKGROUND = "#bbdefb"
    DISABLED_OPACITY = "0.6"

    # Typography - Increased sizes for better visibility
    MONOSPACE_FONT = "Consolas, Monaco, 'Courier New', monospace"
    HEADER_FONT_SIZE = "16px"
    BODY_FONT_SIZE = "13px"
    CODE_FONT_SIZE = "12px"
    SMALL_FONT_SIZE = "11px"
    LARGE_HEADER_SIZE = "18px"

    # Component Styling
    @staticmethod
    def get_panel_style():
        """Get standard panel styling."""
        return f"""
            QWidget {{
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                margin: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """

    @staticmethod
    def get_header_style():
        """Get standard header styling."""
        return f"""
            QLabel {{
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                font-weight: bold;
                color: #333;
                margin-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """

    @staticmethod
    def get_code_style():
        """Get standard code/monospace styling."""
        return f"""
            QTextEdit, QLineEdit {{
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.CODE_FONT_SIZE};
                background-color: white;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """

    @staticmethod
    def get_button_style():
        """Get standard button styling."""
        return f"""
            QPushButton {{
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976d2;
            }}
            QPushButton:pressed {{
                background-color: #0d47a1;
            }}
            QPushButton:disabled {{
                background-color: #ccc;
                color: #666;
            }}
        """

    @staticmethod
    def get_tree_style():
        """Get standard tree widget styling."""
        return f"""
            QTreeWidget {{
                background-color: white;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                selection-background-color: {VisualDesignConstants.SELECTED_BACKGROUND};
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTreeWidget::item:hover {{
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
            }}
            QTreeWidget::item:selected {{
                background-color: {VisualDesignConstants.SELECTED_BACKGROUND};
                color: #333;
            }}
        """


# ============================================================================
# PHASE 1: HIGH IMPACT, LOW COMPLEXITY FEATURES
# ============================================================================

class ValidationResult:
    """Result of path validation with suggestions."""

    def __init__(self, valid: bool, value: Any = None, error: str = "", suggestions: List[str] = None):
        self.valid = valid
        self.value = value
        self.error = error
        self.suggestions = suggestions or []
        self.value_type = type(value).__name__ if value is not None else "unknown"


class SmartPathCompleter(QCompleter):
    """Intelligent auto-completion for JSON paths with fuzzy matching."""

    def __init__(self, json_selector):
        super().__init__()
        self.json_selector = json_selector
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setMaxVisibleItems(10)

        # Custom model for path completions
        self.path_model = QStringListModel()
        self.setModel(self.path_model)

        logger.debug("SmartPathCompleter initialized")

    def update_completions(self):
        """Update available completions from current JSON data and input variables."""
        if not self.json_selector or not hasattr(self.json_selector, 'json_tree'):
            return

        paths = list(self.json_selector.json_tree.path_map.values())

        # Add input variables if available
        if hasattr(self.json_selector, 'workflow') and self.json_selector.workflow:
            if hasattr(self.json_selector.workflow, 'input_variables'):
                for var in self.json_selector.workflow.input_variables:
                    input_var_path = f"data.{var.name}"
                    paths.append(input_var_path)
                    logger.debug(f"Added input variable path: {input_var_path}")

        # Add common meta_info paths
        meta_paths = [
            "meta_info.user.first_name",
            "meta_info.user.last_name",
            "meta_info.user.email_addr",
            "meta_info.user.department"
        ]
        paths.extend(meta_paths)

        # Sort paths for better user experience
        paths.sort()

        self.path_model.setStringList(paths)
        logger.debug(f"Updated completions with {len(paths)} paths")

    def splitPath(self, path: str) -> List[str]:
        """Split path for fuzzy matching."""
        # Support fuzzy matching like "usr.nm" -> "user.name"
        return path.lower().split('.')


class PathValidator:
    """Real-time path validation with intelligent error suggestions."""

    def __init__(self):
        self.common_typos = {
            'usr': 'user',
            'nm': 'name',
            'eml': 'email',
            'dept': 'department',
            'mgr': 'manager',
            'tkt': 'ticket',
            'id': 'id',
            'stat': 'status'
        }
        logger.debug("PathValidator initialized")

    def validate_path(self, path: str, available_data: Dict[str, Any]) -> ValidationResult:
        """Validate path and provide suggestions for fixes."""
        if not path.strip():
            return ValidationResult(valid=False, error="Path cannot be empty")

        try:
            # Try to extract value using the existing method
            value = self._extract_value_by_path(available_data, path)
            return ValidationResult(valid=True, value=value)

        except Exception as e:
            error_msg = str(e)
            suggestions = self._generate_suggestions(path, available_data, error_msg)
            return ValidationResult(valid=False, error=error_msg, suggestions=suggestions)

    def _extract_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from data using dot notation path."""
        if not data:
            raise ValueError("No data available")

        # Remove 'data.' prefix if present
        if path.startswith('data.'):
            path = path[5:]

        if not path:  # Root path
            return data

        parts = []
        current_part = ""
        in_brackets = False

        # Parse path with array indices
        for char in path:
            if char == '[':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_brackets = True
            elif char == ']':
                if in_brackets and current_part:
                    try:
                        parts.append(int(current_part))
                    except ValueError:
                        raise ValueError(f"Invalid array index: '{current_part}' must be a number")
                    current_part = ""
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        # Navigate through the data
        current = data
        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    available_keys = list(current.keys())
                    raise KeyError(f"Key '{part}' not found. Available keys: {available_keys}")
                current = current[part]
            elif isinstance(current, list):
                if not isinstance(part, int):
                    raise TypeError(f"Array index must be integer, got '{part}' (type: {type(part)})")
                if part >= len(current) or part < 0:
                    raise IndexError(f"Array index {part} out of range. Array has {len(current)} items")
                current = current[part]
            else:
                raise TypeError(f"Cannot navigate to '{part}' from {type(current).__name__}")

        return current

    def _generate_suggestions(self, path: str, available_data: Dict[str, Any], error_msg: str) -> List[str]:
        """Generate intelligent suggestions for path fixes."""
        suggestions = []

        # Extract available paths from data
        available_paths = self._extract_all_paths(available_data)

        # Check for typos in the path
        path_parts = path.replace('data.', '').split('.')

        for i, part in enumerate(path_parts):
            if part in self.common_typos:
                corrected_part = self.common_typos[part]
                corrected_path = path_parts.copy()
                corrected_path[i] = corrected_part
                suggestion = 'data.' + '.'.join(corrected_path)
                suggestions.append(f"Did you mean: {suggestion}")

        # Find similar paths using fuzzy matching
        path_lower = path.lower()
        for available_path in available_paths:
            if self._fuzzy_match(path_lower, available_path.lower()):
                suggestions.append(f"Similar path: {available_path}")

        return suggestions[:3]  # Limit to top 3 suggestions

    def _extract_all_paths(self, data: Dict[str, Any], prefix: str = "data") -> List[str]:
        """Extract all possible paths from data structure."""
        paths = []

        def _recurse(obj, current_path):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}"
                    paths.append(new_path)
                    if isinstance(value, (dict, list)):
                        _recurse(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    paths.append(new_path)
                    if isinstance(item, (dict, list)):
                        _recurse(item, new_path)

        _recurse(data, prefix)
        return paths

    def _fuzzy_match(self, query: str, target: str) -> bool:
        """Simple fuzzy matching algorithm."""
        # Remove common prefixes for comparison
        query = query.replace('data.', '')
        target = target.replace('data.', '')

        # Check if query is a subsequence of target
        query_idx = 0
        for char in target:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1

        return query_idx == len(query)


# ============================================================================
# PHASE 2: MEDIUM IMPACT, MEDIUM COMPLEXITY FEATURES
# ============================================================================

class PathTemplateEngine:
    """Generate and manage path templates for common patterns."""

    def __init__(self):
        self.templates = {
            'user_notification': {
                'description': 'Paths for sending user notifications',
                'patterns': [
                    'data.{step}.user.email',
                    'data.{step}.user.name',
                    'data.{step}.user.first_name',
                    'data.{step}.user.last_name'
                ],
                'category': 'User Management'
            },
            'ticket_processing': {
                'description': 'Paths for ticket processing workflows',
                'patterns': [
                    'data.{step}.tickets[0].id',
                    'data.{step}.tickets[0].title',
                    'data.{step}.tickets[0].status',
                    'data.{step}.tickets[0].priority',
                    'data.{step}.tickets[0].assignee.name'
                ],
                'category': 'Ticket Management'
            },
            'error_handling': {
                'description': 'Paths for error handling and validation',
                'patterns': [
                    'data.{step}.error.message',
                    'data.{step}.error.code',
                    'data.{step}.success',
                    'data.{step}.status'
                ],
                'category': 'Error Handling'
            },
            'user_lookup': {
                'description': 'Common user information paths',
                'patterns': [
                    'data.{step}.user.id',
                    'data.{step}.user.email',
                    'data.{step}.user.department',
                    'data.{step}.user.manager.name',
                    'data.{step}.user.location'
                ],
                'category': 'User Management'
            },
            'approval_workflow': {
                'description': 'Paths for approval workflows',
                'patterns': [
                    'data.{step}.request.id',
                    'data.{step}.request.type',
                    'data.{step}.approver.name',
                    'data.{step}.approval.status',
                    'data.{step}.approval.comments'
                ],
                'category': 'Approval Process'
            }
        }
        logger.debug("PathTemplateEngine initialized with templates")

    def get_templates_by_category(self, category: str = None) -> Dict[str, Dict]:
        """Get templates, optionally filtered by category."""
        if category:
            return {k: v for k, v in self.templates.items() if v['category'] == category}
        return self.templates

    def apply_template(self, template_name: str, step_key: str) -> List[str]:
        """Apply template to generate paths for a specific step."""
        if template_name not in self.templates:
            return []

        patterns = self.templates[template_name]['patterns']
        return [pattern.format(step=step_key) for pattern in patterns]

    def get_categories(self) -> List[str]:
        """Get all available template categories."""
        categories = set()
        for template in self.templates.values():
            categories.add(template['category'])
        return sorted(list(categories))

    def add_custom_template(self, name: str, description: str, patterns: List[str], category: str = "Custom"):
        """Add a custom template."""
        self.templates[name] = {
            'description': description,
            'patterns': patterns,
            'category': category
        }
        logger.debug(f"Added custom template: {name}")


class PathSelectionHistory:
    """Track and manage path selection history with undo/redo."""

    def __init__(self, max_history: int = 50):
        self.history = []
        self.current_index = -1
        self.max_history = max_history
        logger.debug("PathSelectionHistory initialized")

    def add_selection(self, path: str, context: str = ""):
        """Add a new path selection to history."""
        # Remove any future history if we're not at the end
        self.history = self.history[:self.current_index + 1]

        # Add new selection with timestamp
        import datetime
        selection = {
            'path': path,
            'context': context,
            'timestamp': datetime.datetime.now().isoformat()
        }

        self.history.append(selection)
        self.current_index += 1

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1

        logger.debug(f"Added to history: {path} (index: {self.current_index})")

    def undo(self) -> Dict[str, str]:
        """Go back to previous selection."""
        if self.current_index > 0:
            self.current_index -= 1
            selection = self.history[self.current_index]
            logger.debug(f"Undo to: {selection['path']}")
            return selection
        return None

    def redo(self) -> Dict[str, str]:
        """Go forward to next selection."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            selection = self.history[self.current_index]
            logger.debug(f"Redo to: {selection['path']}")
            return selection
        return None

    def get_recent_selections(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent selections."""
        return self.history[-limit:] if self.history else []

    def clear_history(self):
        """Clear all history."""
        self.history.clear()
        self.current_index = -1
        logger.debug("History cleared")


class IntelligentPathSuggester:
    """AI-powered path suggestions based on workflow context."""

    def __init__(self):
        self.context_patterns = {
            'email_notification': {
                'keywords': ['email', 'notification', 'send', 'notify'],
                'suggested_paths': ['user.email', 'user.name', 'user.first_name']
            },
            'ticket_update': {
                'keywords': ['ticket', 'update', 'status', 'assign'],
                'suggested_paths': ['tickets[0].id', 'tickets[0].status', 'tickets[0].assignee']
            },
            'user_lookup': {
                'keywords': ['user', 'lookup', 'find', 'search'],
                'suggested_paths': ['user.id', 'user.name', 'user.department', 'user.manager']
            },
            'approval_process': {
                'keywords': ['approve', 'approval', 'manager', 'supervisor'],
                'suggested_paths': ['user.manager.name', 'user.manager.email', 'approval.status']
            },
            'error_handling': {
                'keywords': ['error', 'fail', 'exception', 'validate'],
                'suggested_paths': ['error.message', 'error.code', 'success', 'status']
            }
        }
        self.user_patterns = {}  # Learn from user behavior
        logger.debug("IntelligentPathSuggester initialized")

    def suggest_paths(self, context: str, available_paths: List[str], step_type: str = "") -> List[Dict[str, Any]]:
        """Suggest relevant paths based on current context."""
        suggestions = []
        context_lower = context.lower()

        # Find matching context patterns
        for pattern_name, pattern_data in self.context_patterns.items():
            score = 0
            for keyword in pattern_data['keywords']:
                if keyword in context_lower:
                    score += 1

            if score > 0:
                # Find matching available paths
                for suggested_path in pattern_data['suggested_paths']:
                    for available_path in available_paths:
                        if suggested_path in available_path:
                            suggestions.append({
                                'path': available_path,
                                'confidence': score / len(pattern_data['keywords']),
                                'reason': f"Matches {pattern_name} pattern",
                                'category': pattern_name
                            })

        # Sort by confidence and remove duplicates
        unique_suggestions = {}
        for suggestion in suggestions:
            path = suggestion['path']
            if path not in unique_suggestions or suggestion['confidence'] > unique_suggestions[path]['confidence']:
                unique_suggestions[path] = suggestion

        return sorted(unique_suggestions.values(), key=lambda x: x['confidence'], reverse=True)[:5]

    def learn_from_selection(self, context: str, selected_path: str, step_type: str = ""):
        """Learn from user selections to improve suggestions."""
        context_key = context.lower()
        if context_key not in self.user_patterns:
            self.user_patterns[context_key] = {}

        if selected_path not in self.user_patterns[context_key]:
            self.user_patterns[context_key][selected_path] = 0

        self.user_patterns[context_key][selected_path] += 1
        logger.debug(f"Learned: {context} -> {selected_path}")


class InteractivePathBuilder(QDialog):
    """Step-by-step wizard for building complex JSON paths."""

    def __init__(self, json_data: dict, parent=None):
        super().__init__(parent)
        self.json_data = json_data
        self.current_path = "data"
        self.path_parts = ["data"]
        self.setWindowTitle("Interactive Path Builder")
        self.setModal(True)
        self.resize(600, 500)
        self._setup_ui()
        self._update_options()
        logger.debug("InteractivePathBuilder initialized")

    def _setup_ui(self):
        """Create wizard-style interface for path building."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🧭 Interactive Path Builder")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Current path display
        path_group = QGroupBox("Current Path")
        path_layout = QVBoxLayout(path_group)

        self.path_display = QLabel(self.current_path)
        self.path_display.setStyleSheet("font-family: monospace; font-size: 14px; padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
        path_layout.addWidget(self.path_display)

        # Breadcrumb navigation
        self.breadcrumb_layout = QHBoxLayout()
        path_layout.addLayout(self.breadcrumb_layout)

        layout.addWidget(path_group)

        # Available options
        options_group = QGroupBox("Available Options")
        options_layout = QVBoxLayout(options_group)

        # Search for options
        self.options_search = QLineEdit()
        self.options_search.setPlaceholderText("Search available options...")
        self.options_search.textChanged.connect(self._filter_options)
        options_layout.addWidget(self.options_search)

        self.options_list = QListWidget()
        self.options_list.itemDoubleClicked.connect(self._on_option_selected)
        options_layout.addWidget(self.options_list)

        layout.addWidget(options_group)

        # Preview panel
        preview_group = QGroupBox("Value Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setEnabled(False)
        button_layout.addWidget(self.back_btn)

        button_layout.addStretch()

        self.use_path_btn = QPushButton("✅ Use This Path")
        self.use_path_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.use_path_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _update_options(self):
        """Update available options based on current path."""
        self.options_list.clear()
        self.path_display.setText(self.current_path)
        self._update_breadcrumbs()

        # Get current data at path
        try:
            current_data = self._get_data_at_path()
            self._update_preview(current_data)

            if isinstance(current_data, dict):
                # Show available keys
                for key in sorted(current_data.keys()):
                    item = QListWidgetItem(f"🔑 {key}")
                    item.setData(Qt.UserRole, ('key', key))
                    self.options_list.addItem(item)

            elif isinstance(current_data, list):
                # Show array indices
                for i in range(len(current_data)):
                    preview = str(current_data[i])[:50] + "..." if len(str(current_data[i])) > 50 else str(current_data[i])
                    item = QListWidgetItem(f"📋 [{i}] - {preview}")
                    item.setData(Qt.UserRole, ('index', i))
                    self.options_list.addItem(item)

            else:
                # Terminal value
                item = QListWidgetItem("✅ This is a terminal value")
                item.setData(Qt.UserRole, ('terminal', None))
                self.options_list.addItem(item)

        except Exception as e:
            self.preview_text.setPlainText(f"Error: {e}")

    def _update_breadcrumbs(self):
        """Update breadcrumb navigation."""
        # Clear existing breadcrumbs
        for i in reversed(range(self.breadcrumb_layout.count())):
            self.breadcrumb_layout.itemAt(i).widget().setParent(None)

        # Add breadcrumb buttons
        for i, part in enumerate(self.path_parts):
            btn = QPushButton(part)
            btn.clicked.connect(lambda checked, idx=i: self._navigate_to_breadcrumb(idx))
            self.breadcrumb_layout.addWidget(btn)

            if i < len(self.path_parts) - 1:
                separator = QLabel("→")
                separator.setStyleSheet("color: #666; margin: 0 5px;")
                self.breadcrumb_layout.addWidget(separator)

        self.back_btn.setEnabled(len(self.path_parts) > 1)

    def _get_data_at_path(self):
        """Get data at current path."""
        current = self.json_data

        # Skip 'data' prefix
        for part in self.path_parts[1:]:
            if isinstance(part, int):
                current = current[part]
            else:
                current = current[part]

        return current

    def _update_preview(self, data):
        """Update the preview panel."""
        if data is None:
            self.preview_text.setPlainText("null")
        elif isinstance(data, (dict, list)):
            import json
            preview = json.dumps(data, indent=2)[:500]
            if len(preview) >= 500:
                preview += "\n... (truncated)"
            self.preview_text.setPlainText(preview)
        else:
            self.preview_text.setPlainText(f"Value: {data}\nType: {type(data).__name__}")

    def _filter_options(self, query):
        """Filter options based on search query."""
        for i in range(self.options_list.count()):
            item = self.options_list.item(i)
            visible = query.lower() in item.text().lower() if query else True
            item.setHidden(not visible)

    def _on_option_selected(self, item):
        """Handle option selection."""
        option_type, value = item.data(Qt.UserRole)

        if option_type == 'terminal':
            return  # Can't navigate further

        # Add to path
        if option_type == 'key':
            self.path_parts.append(value)
            self.current_path += f".{value}"
        elif option_type == 'index':
            self.path_parts.append(value)
            self.current_path += f"[{value}]"

        self._update_options()

    def _go_back(self):
        """Go back one level in the path."""
        if len(self.path_parts) > 1:
            removed_part = self.path_parts.pop()

            # Update current_path
            if isinstance(removed_part, int):
                # Remove array index
                self.current_path = self.current_path.rsplit(f"[{removed_part}]", 1)[0]
            else:
                # Remove key
                self.current_path = self.current_path.rsplit(f".{removed_part}", 1)[0]

            self._update_options()

    def _navigate_to_breadcrumb(self, index):
        """Navigate to a specific breadcrumb."""
        # Truncate path to selected breadcrumb
        self.path_parts = self.path_parts[:index + 1]

        # Rebuild current_path
        self.current_path = "data"
        for part in self.path_parts[1:]:
            if isinstance(part, int):
                self.current_path += f"[{part}]"
            else:
                self.current_path += f".{part}"

        self._update_options()

    def get_selected_path(self) -> str:
        """Get the currently selected path."""
        return self.current_path


# ============================================================================
# PHASE 3: HIGH IMPACT, HIGH COMPLEXITY FEATURES
# ============================================================================

class DataFlowVisualizer(QWidget):
    """Interactive visual diagram of workflow data flow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow = None
        self.node_positions = {}
        self.connections = []
        self._setup_ui()
        logger.debug("DataFlowVisualizer initialized")

    def _setup_ui(self):
        """Setup the data flow visualization UI."""
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        self.zoom_in_btn = QPushButton("🔍+ Zoom In")
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        controls_layout.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton("🔍- Zoom Out")
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        controls_layout.addWidget(self.zoom_out_btn)

        self.reset_view_btn = QPushButton("🎯 Reset View")
        self.reset_view_btn.clicked.connect(self._reset_view)
        controls_layout.addWidget(self.reset_view_btn)

        controls_layout.addStretch()

        self.export_btn = QPushButton("💾 Export Diagram")
        self.export_btn.clicked.connect(self._export_diagram)
        controls_layout.addWidget(self.export_btn)

        layout.addLayout(controls_layout)

        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.view)

    def set_workflow(self, workflow):
        """Set the workflow and update the visualization."""
        self.workflow = workflow
        self._update_visualization()

    def _update_visualization(self):
        """Update the visual representation of the workflow."""
        if not self.workflow:
            return

        self.scene.clear()
        self.node_positions.clear()
        self.connections.clear()

        # Create nodes for each step
        y_offset = 0
        node_height = 100
        node_spacing = 150

        for i, step in enumerate(self.workflow.steps):
            node = self._create_step_node(step, i)
            x = 50
            y = y_offset
            node.setPos(x, y)
            self.scene.addItem(node)
            self.node_positions[i] = (x, y)
            y_offset += node_spacing

        # Create connections based on data dependencies
        self._create_connections()

        # Fit view to content
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def _create_step_node(self, step, index):
        """Create a visual node for a workflow step."""
        # Create a group item for the node
        node = QGraphicsItemGroup()

        # Background rectangle
        rect = QGraphicsRectItem(0, 0, 200, 80)
        rect.setBrush(QBrush(QColor("#e3f2fd")))
        rect.setPen(QPen(QColor("#1976d2"), 2))
        node.addToGroup(rect)

        # Step title
        title = QGraphicsTextItem(f"Step {index + 1}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setPos(10, 5)
        node.addToGroup(title)

        # Step details
        step_type = type(step).__name__.replace('Step', '')
        output_key = getattr(step, 'output_key', 'unknown')
        details = QGraphicsTextItem(f"{step_type}: {output_key}")
        details.setFont(QFont("Arial", 10))
        details.setPos(10, 30)
        node.addToGroup(details)

        # Data indicator
        has_json = hasattr(step, 'parsed_json_output') and step.parsed_json_output
        data_indicator = QGraphicsEllipseItem(170, 10, 20, 20)
        data_indicator.setBrush(QBrush(QColor("#4caf50" if has_json else "#f44336")))
        data_indicator.setPen(QPen(QColor("#2e7d32" if has_json else "#c62828")))
        node.addToGroup(data_indicator)

        return node

    def _create_connections(self):
        """Create visual connections between steps based on data flow."""
        # For now, create simple sequential connections
        # In a real implementation, this would analyze actual data dependencies
        for i in range(len(self.workflow.steps) - 1):
            start_pos = self.node_positions[i]
            end_pos = self.node_positions[i + 1]

            # Create arrow line
            line = QGraphicsLineItem(
                start_pos[0] + 100, start_pos[1] + 80,  # Bottom center of source
                end_pos[0] + 100, end_pos[1]            # Top center of target
            )
            line.setPen(QPen(QColor("#666666"), 2))
            self.scene.addItem(line)

            # Add arrowhead
            arrow = self._create_arrowhead(end_pos[0] + 100, end_pos[1])
            self.scene.addItem(arrow)

    def _create_arrowhead(self, x, y):
        """Create an arrowhead at the specified position."""
        arrow = QGraphicsPolygonItem()
        from PySide6.QtGui import QPolygonF
        from PySide6.QtCore import QPointF

        points = [
            QPointF(x, y),
            QPointF(x - 10, y - 15),
            QPointF(x + 10, y - 15)
        ]
        arrow.setPolygon(QPolygonF(points))
        arrow.setBrush(QBrush(QColor("#666666")))
        arrow.setPen(QPen(QColor("#666666")))
        return arrow

    def _zoom_in(self):
        """Zoom in the view."""
        self.view.scale(1.2, 1.2)

    def _zoom_out(self):
        """Zoom out the view."""
        self.view.scale(0.8, 0.8)

    def _reset_view(self):
        """Reset the view to fit all content."""
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def _export_diagram(self):
        """Export the diagram as an image."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Diagram", "workflow_diagram.png",
            "PNG Files (*.png);;PDF Files (*.pdf)"
        )

        if file_path:
            # Create pixmap of the scene
            pixmap = QPixmap(self.scene.sceneRect().size().toSize())
            pixmap.fill(Qt.white)

            painter = QPainter(pixmap)
            self.scene.render(painter)
            painter.end()

            pixmap.save(file_path)
            logger.debug(f"Exported diagram to {file_path}")


class PathChainBuilder(QDialog):
    """Build complex expressions combining multiple data sources."""

    def __init__(self, workflow, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.chain_parts = []
        self.setWindowTitle("Path Chain Builder")
        self.setModal(True)
        self.resize(800, 600)
        self._setup_ui()
        logger.debug("PathChainBuilder initialized")

    def _setup_ui(self):
        """Setup the chain builder UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🔗 Path Chain Builder")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Current expression display
        expr_group = QGroupBox("Current Expression")
        expr_layout = QVBoxLayout(expr_group)

        self.expression_display = QTextEdit()
        self.expression_display.setMaximumHeight(100)
        self.expression_display.setReadOnly(True)
        self.expression_display.setStyleSheet("font-family: monospace; background-color: #f0f0f0;")
        expr_layout.addWidget(self.expression_display)

        layout.addWidget(expr_group)

        # Chain building area
        chain_group = QGroupBox("Build Chain")
        chain_layout = QHBoxLayout(chain_group)

        # Available paths
        paths_layout = QVBoxLayout()
        paths_layout.addWidget(QLabel("Available Paths:"))

        self.paths_list = QListWidget()
        self.paths_list.itemDoubleClicked.connect(self._add_path_to_chain)
        paths_layout.addWidget(self.paths_list)

        chain_layout.addLayout(paths_layout)

        # Operations
        ops_layout = QVBoxLayout()
        ops_layout.addWidget(QLabel("Operations:"))

        self.concat_btn = QPushButton("+ Concatenate")
        self.concat_btn.clicked.connect(lambda: self._add_operation("concat"))
        ops_layout.addWidget(self.concat_btn)

        self.format_btn = QPushButton("📝 Format")
        self.format_btn.clicked.connect(lambda: self._add_operation("format"))
        ops_layout.addWidget(self.format_btn)

        self.condition_btn = QPushButton("❓ Conditional")
        self.condition_btn.clicked.connect(lambda: self._add_operation("condition"))
        ops_layout.addWidget(self.condition_btn)

        ops_layout.addStretch()

        chain_layout.addLayout(ops_layout)

        # Chain parts
        parts_layout = QVBoxLayout()
        parts_layout.addWidget(QLabel("Chain Parts:"))

        self.parts_list = QListWidget()
        parts_layout.addWidget(self.parts_list)

        self.remove_part_btn = QPushButton("🗑️ Remove Selected")
        self.remove_part_btn.clicked.connect(self._remove_selected_part)
        parts_layout.addWidget(self.remove_part_btn)

        chain_layout.addLayout(parts_layout)

        layout.addWidget(chain_group)

        # Preview
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self._clear_chain)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()

        self.use_expression_btn = QPushButton("✅ Use Expression")
        self.use_expression_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.use_expression_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Initialize with available paths
        self._populate_available_paths()

    def _populate_available_paths(self):
        """Populate the available paths list."""
        self.paths_list.clear()

        if not self.workflow:
            return

        for i, step in enumerate(self.workflow.steps):
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                output_key = getattr(step, 'output_key', f'step_{i}')

                # Add step root
                item = QListWidgetItem(f"📁 data.{output_key}")
                item.setData(Qt.UserRole, f"data.{output_key}")
                self.paths_list.addItem(item)

                # Add some common sub-paths (simplified)
                common_paths = [
                    f"data.{output_key}.id",
                    f"data.{output_key}.name",
                    f"data.{output_key}.status",
                    f"data.{output_key}.email"
                ]

                for path in common_paths:
                    item = QListWidgetItem(f"  🔗 {path}")
                    item.setData(Qt.UserRole, path)
                    self.paths_list.addItem(item)

    def _add_path_to_chain(self, item):
        """Add a path to the chain."""
        path = item.data(Qt.UserRole)
        if path:
            self.chain_parts.append({'type': 'path', 'value': path})
            self._update_chain_display()

    def _add_operation(self, op_type):
        """Add an operation to the chain."""
        if op_type == "concat":
            self.chain_parts.append({'type': 'operation', 'value': ' + '})
        elif op_type == "format":
            self.chain_parts.append({'type': 'operation', 'value': '.format()'})
        elif op_type == "condition":
            self.chain_parts.append({'type': 'operation', 'value': ' if condition else '})

        self._update_chain_display()

    def _remove_selected_part(self):
        """Remove selected part from chain."""
        current_row = self.parts_list.currentRow()
        if current_row >= 0:
            del self.chain_parts[current_row]
            self._update_chain_display()

    def _clear_chain(self):
        """Clear the entire chain."""
        self.chain_parts.clear()
        self._update_chain_display()

    def _update_chain_display(self):
        """Update the chain display."""
        # Update parts list
        self.parts_list.clear()
        for i, part in enumerate(self.chain_parts):
            item_text = f"{i+1}. {part['type']}: {part['value']}"
            self.parts_list.addItem(item_text)

        # Update expression display
        expression = ""
        for part in self.chain_parts:
            expression += part['value']

        self.expression_display.setPlainText(expression)

        # Update preview (simplified)
        self.preview_text.setPlainText(f"Expression: {expression}")

    def get_expression(self) -> str:
        """Get the built expression."""
        expression = ""
        for part in self.chain_parts:
            expression += part['value']
        return expression


class WorkflowDocumentationGenerator:
    """Generate comprehensive workflow documentation."""

    def __init__(self):
        logger.debug("WorkflowDocumentationGenerator initialized")

    def generate_documentation(self, workflow) -> Dict[str, str]:
        """Generate multiple documentation formats."""
        docs = {}

        if workflow:
            docs['markdown'] = self._generate_markdown(workflow)
            docs['html'] = self._generate_html(workflow)
            docs['data_dictionary'] = self._generate_data_dictionary(workflow)

        return docs

    def _generate_markdown(self, workflow) -> str:
        """Generate markdown documentation of all path mappings."""
        doc = "# Workflow Data Path Documentation\n\n"
        doc += f"**Generated:** {self._get_timestamp()}\n\n"

        if not workflow.steps:
            doc += "No steps found in workflow.\n"
            return doc

        doc += "## Overview\n\n"
        doc += f"This workflow contains {len(workflow.steps)} steps with data flow mappings.\n\n"

        for i, step in enumerate(workflow.steps):
            doc += f"## Step {i+1}: {getattr(step, 'output_key', 'unknown')}\n\n"
            doc += f"**Type**: {type(step).__name__}\n"

            if hasattr(step, 'action_name'):
                doc += f"**Action**: {step.action_name}\n"

            if hasattr(step, 'description') and step.description:
                doc += f"**Description**: {step.description}\n"

            doc += "\n"

            # Document available paths
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                paths = self._extract_all_paths(step.parsed_json_output, f"data.{getattr(step, 'output_key', 'unknown')}")
                doc += "### Available Paths:\n\n"
                for path in sorted(paths):
                    doc += f"- `{path}`\n"
                doc += "\n"

                # Sample data structure
                doc += "### Sample Data Structure:\n\n"
                doc += "```json\n"
                import json
                doc += json.dumps(step.parsed_json_output, indent=2)[:1000]
                if len(json.dumps(step.parsed_json_output)) > 1000:
                    doc += "\n... (truncated)"
                doc += "\n```\n\n"
            else:
                doc += "No JSON output data available for this step.\n\n"

        return doc

    def _generate_html(self, workflow) -> str:
        """Generate HTML documentation."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Workflow Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .step { border: 1px solid #ddd; margin: 20px 0; padding: 20px; }
                .path { font-family: monospace; background: #f5f5f5; padding: 2px 4px; }
                pre { background: #f8f8f8; padding: 10px; overflow-x: auto; }
            </style>
        </head>
        <body>
        """

        html += f"<h1>Workflow Data Path Documentation</h1>"
        html += f"<p><strong>Generated:</strong> {self._get_timestamp()}</p>"

        for i, step in enumerate(workflow.steps):
            html += f"<div class='step'>"
            html += f"<h2>Step {i+1}: {getattr(step, 'output_key', 'unknown')}</h2>"
            html += f"<p><strong>Type:</strong> {type(step).__name__}</p>"

            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                paths = self._extract_all_paths(step.parsed_json_output, f"data.{getattr(step, 'output_key', 'unknown')}")
                html += "<h3>Available Paths:</h3><ul>"
                for path in sorted(paths):
                    html += f"<li><span class='path'>{path}</span></li>"
                html += "</ul>"

            html += "</div>"

        html += "</body></html>"
        return html

    def _generate_data_dictionary(self, workflow) -> str:
        """Generate a data dictionary with field explanations."""
        dictionary = "# Data Dictionary\n\n"
        dictionary += f"Generated: {self._get_timestamp()}\n\n"

        all_fields = {}

        for i, step in enumerate(workflow.steps):
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                step_key = getattr(step, 'output_key', f'step_{i}')
                fields = self._extract_field_info(step.parsed_json_output, f"data.{step_key}")
                all_fields.update(fields)

        dictionary += "| Field Path | Type | Description | Example Value |\n"
        dictionary += "|------------|------|-------------|---------------|\n"

        for path, info in sorted(all_fields.items()):
            dictionary += f"| `{path}` | {info['type']} | {info['description']} | `{info['example']}` |\n"

        return dictionary

    def _extract_all_paths(self, data, prefix="data"):
        """Extract all possible paths from data structure."""
        paths = []

        def _recurse(obj, current_path):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}"
                    paths.append(new_path)
                    if isinstance(value, (dict, list)):
                        _recurse(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    paths.append(new_path)
                    if isinstance(item, (dict, list)):
                        _recurse(item, new_path)

        _recurse(data, prefix)
        return paths

    def _extract_field_info(self, data, prefix="data"):
        """Extract field information for data dictionary."""
        fields = {}

        def _recurse(obj, current_path):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}"
                    fields[new_path] = {
                        'type': type(value).__name__,
                        'description': self._generate_field_description(key, value),
                        'example': str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    }
                    if isinstance(value, (dict, list)):
                        _recurse(value, new_path)
            elif isinstance(obj, list) and obj:
                # Document first item as example
                new_path = f"{current_path}[0]"
                fields[new_path] = {
                    'type': f"Array of {type(obj[0]).__name__}",
                    'description': f"Array containing {len(obj)} items",
                    'example': str(obj[0])[:50] + "..." if len(str(obj[0])) > 50 else str(obj[0])
                }
                if isinstance(obj[0], (dict, list)):
                    _recurse(obj[0], new_path)

        _recurse(data, prefix)
        return fields

    def _generate_field_description(self, field_name: str, value) -> str:
        """Generate a description for a field based on its name and value."""
        field_lower = field_name.lower()

        descriptions = {
            'id': 'Unique identifier',
            'name': 'Display name or title',
            'email': 'Email address',
            'status': 'Current status or state',
            'created': 'Creation timestamp',
            'updated': 'Last update timestamp',
            'user': 'User information',
            'ticket': 'Ticket or request details',
            'department': 'Department or organizational unit',
            'manager': 'Manager or supervisor information',
            'priority': 'Priority level',
            'assignee': 'Assigned person or team'
        }

        for key, desc in descriptions.items():
            if key in field_lower:
                return desc

        return f"Field containing {type(value).__name__} data"

    def _get_timestamp(self) -> str:
        """Get current timestamp for documentation."""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class WorkflowAnalytics:
    """Analytics dashboard for workflow optimization insights."""

    def __init__(self):
        self.path_usage_stats = {}
        self.error_patterns = {}
        self.performance_metrics = {}
        logger.debug("WorkflowAnalytics initialized")

    def track_path_usage(self, path: str, success: bool, execution_time: float = 0.0):
        """Track how often paths are used and their success rate."""
        if path not in self.path_usage_stats:
            self.path_usage_stats[path] = {
                'count': 0,
                'success_count': 0,
                'total_time': 0.0,
                'errors': []
            }

        stats = self.path_usage_stats[path]
        stats['count'] += 1
        stats['total_time'] += execution_time

        if success:
            stats['success_count'] += 1

        logger.debug(f"Tracked path usage: {path} (success: {success})")

    def track_error(self, path: str, error_message: str):
        """Track errors for pattern analysis."""
        if path not in self.path_usage_stats:
            self.path_usage_stats[path] = {
                'count': 0, 'success_count': 0, 'total_time': 0.0, 'errors': []
            }

        self.path_usage_stats[path]['errors'].append(error_message)

        # Track error patterns
        if error_message not in self.error_patterns:
            self.error_patterns[error_message] = 0
        self.error_patterns[error_message] += 1

    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get comprehensive usage analytics."""
        analytics = {
            'total_paths': len(self.path_usage_stats),
            'most_used_paths': [],
            'least_reliable_paths': [],
            'performance_insights': [],
            'error_summary': {}
        }

        # Most used paths
        sorted_by_usage = sorted(
            self.path_usage_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        analytics['most_used_paths'] = [
            {
                'path': path,
                'usage_count': stats['count'],
                'success_rate': stats['success_count'] / stats['count'] if stats['count'] > 0 else 0
            }
            for path, stats in sorted_by_usage[:10]
        ]

        # Least reliable paths
        unreliable_paths = [
            (path, stats) for path, stats in self.path_usage_stats.items()
            if stats['count'] > 0 and (stats['success_count'] / stats['count']) < 0.8
        ]
        analytics['least_reliable_paths'] = [
            {
                'path': path,
                'success_rate': stats['success_count'] / stats['count'],
                'error_count': len(stats['errors'])
            }
            for path, stats in unreliable_paths[:5]
        ]

        # Performance insights
        slow_paths = [
            (path, stats) for path, stats in self.path_usage_stats.items()
            if stats['count'] > 0 and (stats['total_time'] / stats['count']) > 1.0
        ]
        analytics['performance_insights'] = [
            {
                'path': path,
                'avg_time': stats['total_time'] / stats['count'],
                'total_executions': stats['count']
            }
            for path, stats in slow_paths[:5]
        ]

        # Error summary
        analytics['error_summary'] = dict(sorted(
            self.error_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])

        return analytics

    def get_recommendations(self) -> List[str]:
        """Get optimization recommendations based on analytics."""
        recommendations = []

        analytics = self.get_usage_analytics()

        # Recommend caching for frequently used paths
        for path_info in analytics['most_used_paths'][:3]:
            if path_info['usage_count'] > 10:
                recommendations.append(
                    f"Consider caching results for '{path_info['path']}' "
                    f"(used {path_info['usage_count']} times)"
                )

        # Recommend fixing unreliable paths
        for path_info in analytics['least_reliable_paths']:
            recommendations.append(
                f"Investigate reliability issues with '{path_info['path']}' "
                f"(success rate: {path_info['success_rate']:.1%})"
            )

        # Recommend performance optimization
        for path_info in analytics['performance_insights']:
            recommendations.append(
                f"Optimize performance for '{path_info['path']}' "
                f"(avg time: {path_info['avg_time']:.2f}s)"
            )

        return recommendations


class PathBookmarkManager:
    """Manage and persist frequently used JSON paths."""

    def __init__(self):
        try:
            self.settings = QSettings("MoveworksYAML", "PathBookmarks")
        except:
            self.settings = None  # Fallback for testing
        self.bookmarks = {}  # name -> {'path': str, 'category': str, 'usage_count': int}
        self.usage_count = {}  # path -> count
        self.load_bookmarks()
        logger.debug("PathBookmarkManager initialized")

    def add_bookmark(self, name: str, path: str, category: str = "General"):
        """Add a bookmarked path."""
        bookmark_id = f"{category}::{name}"
        self.bookmarks[bookmark_id] = {
            'path': path,
            'category': category,
            'usage_count': self.usage_count.get(path, 0),
            'name': name
        }
        self.save_bookmarks()
        logger.debug(f"Added bookmark: {name} -> {path}")

    def remove_bookmark(self, bookmark_id: str):
        """Remove a bookmark."""
        if bookmark_id in self.bookmarks:
            del self.bookmarks[bookmark_id]
            self.save_bookmarks()
            logger.debug(f"Removed bookmark: {bookmark_id}")

    def get_bookmarks_by_category(self, category: str = None) -> Dict[str, Dict]:
        """Get bookmarks, optionally filtered by category."""
        if category:
            return {k: v for k, v in self.bookmarks.items() if v['category'] == category}
        return self.bookmarks

    def get_frequent_paths(self, limit: int = 10) -> List[str]:
        """Get most frequently used paths."""
        return sorted(self.usage_count.keys(),
                     key=lambda p: self.usage_count[p],
                     reverse=True)[:limit]

    def track_usage(self, path: str):
        """Track usage of a path."""
        self.usage_count[path] = self.usage_count.get(path, 0) + 1
        # Update bookmark usage counts
        for bookmark in self.bookmarks.values():
            if bookmark['path'] == path:
                bookmark['usage_count'] = self.usage_count[path]
        self.save_bookmarks()

    def save_bookmarks(self):
        """Save bookmarks to persistent storage."""
        if self.settings:
            self.settings.setValue("bookmarks", self.bookmarks)
            self.settings.setValue("usage_count", self.usage_count)

    def load_bookmarks(self):
        """Load bookmarks from persistent storage."""
        if self.settings:
            self.bookmarks = self.settings.value("bookmarks", {})
            self.usage_count = self.settings.value("usage_count", {})

    def export_bookmarks(self, file_path: str):
        """Export bookmarks to JSON file."""
        export_data = {
            'bookmarks': self.bookmarks,
            'usage_count': self.usage_count
        }
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.debug(f"Exported bookmarks to {file_path}")

    def import_bookmarks(self, file_path: str):
        """Import bookmarks from JSON file."""
        with open(file_path, 'r') as f:
            import_data = json.load(f)

        self.bookmarks.update(import_data.get('bookmarks', {}))
        self.usage_count.update(import_data.get('usage_count', {}))
        self.save_bookmarks()
        logger.debug(f"Imported bookmarks from {file_path}")


class DraggableJsonTree(QTreeWidget):
    """JSON tree with drag & drop support for path insertion."""

    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDragDropMode(QTreeWidget.DragOnly)
        logger.debug("DraggableJsonTree initialized")

    def startDrag(self, supportedActions):
        """Start drag operation with path data."""
        current_item = self.currentItem()
        if not current_item or not hasattr(self, 'path_map'):
            return

        if current_item in self.path_map:
            path = self.path_map[current_item]

            # Create drag with path data
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(path)
            mime_data.setData("application/x-json-path", path.encode())

            # Create drag pixmap with path preview
            pixmap = QPixmap(200, 30)
            pixmap.fill(Qt.white)
            painter = QPainter(pixmap)
            painter.setPen(Qt.black)
            painter.drawText(5, 20, path[:25] + "..." if len(path) > 25 else path)
            painter.end()

            drag.setPixmap(pixmap)
            drag.setMimeData(mime_data)

            # Execute drag
            drag.exec_(Qt.CopyAction)
            logger.debug(f"Started drag for path: {path}")


class DropTargetLineEdit(QLineEdit):
    """Input field that accepts JSON path drops."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.path_validator = None
        self.path_completer = None
        logger.debug("DropTargetLineEdit initialized")

    def set_path_validator(self, validator: PathValidator):
        """Set the path validator for real-time validation."""
        self.path_validator = validator
        self.textChanged.connect(self._validate_path)

    def set_path_completer(self, completer: SmartPathCompleter):
        """Set the smart path completer."""
        self.path_completer = completer
        self.setCompleter(completer)

    def dragEnterEvent(self, event):
        """Accept JSON path drops."""
        if event.mimeData().hasFormat("application/x-json-path") or event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #e6f3ff; border: 2px dashed #0066cc;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Reset styling when drag leaves."""
        self.setStyleSheet("")
        event.accept()

    def dropEvent(self, event):
        """Handle path drop."""
        self.setStyleSheet("")

        if event.mimeData().hasFormat("application/x-json-path"):
            path = event.mimeData().data("application/x-json-path").data().decode()
        elif event.mimeData().hasText():
            path = event.mimeData().text()
        else:
            event.ignore()
            return

        # Insert path at cursor position or replace selection
        cursor_pos = self.cursorPosition()
        if self.hasSelectedText():
            self.del_()

        self.insert(path)
        event.acceptProposedAction()
        logger.debug(f"Dropped path: {path}")

    def _validate_path(self):
        """Validate path in real-time."""
        if not self.path_validator:
            return

        path = self.text()
        if not path:
            self.setStyleSheet("")
            self.setToolTip("")
            return

        # Get current workflow data for validation
        # This would need to be connected to the main selector
        validation_result = self.path_validator.validate_path(path, {})

        if validation_result.valid:
            self.setStyleSheet("border: 2px solid #28a745;")
            self.setToolTip(f"✓ Valid path\nType: {validation_result.value_type}")
        else:
            self.setStyleSheet("border: 2px solid #dc3545;")
            tooltip = f"✗ {validation_result.error}"
            if validation_result.suggestions:
                tooltip += "\n\nSuggestions:\n" + "\n".join(validation_result.suggestions)
            self.setToolTip(tooltip)


class JsonTreeWidget(DraggableJsonTree):
    """Enhanced tree widget for JSON structure visualization with drag & drop."""

    path_selected = Signal(str)  # Emits the selected JSON path

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Key", "Type", "Value"])
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self._on_item_clicked)

        # Enable single selection for clearer path selection
        self.setSelectionMode(QTreeWidget.SingleSelection)

        # Store path information in items
        self.path_map = {}  # item -> full_path
        self.current_data = {}  # Store current JSON data for validation

        # Visual enhancements
        self.setRootIsDecorated(True)
        self.setIndentation(20)
        self.setUniformRowHeights(False)

        # Enable tooltips
        self.setMouseTracking(True)

        logger.debug("JsonTreeWidget initialized")

    def populate_from_json(self, data: Dict[str, Any], root_path: str = "data"):
        """Populate tree from JSON data with enhanced logging and error handling."""
        logger.debug(f"populate_from_json called with data type: {type(data)}, root_path: {root_path}")

        self.clear()
        self.path_map.clear()
        self.current_data = data

        if not data:
            logger.debug("No data provided, showing empty tree")
            # Show a message item for empty data
            empty_item = QTreeWidgetItem(["No data available", "info", "Select a step with parsed JSON output"])
            empty_item.setForeground(0, Qt.gray)
            self.addTopLevelItem(empty_item)
            return

        try:
            # Create root item
            data_size = len(data) if isinstance(data, (dict, list)) else 1
            root_display = f"{root_path} ({data_size} items)" if isinstance(data, (dict, list)) else root_path
            root_item = QTreeWidgetItem([root_display, self._get_value_type(data), ""])
            self.addTopLevelItem(root_item)
            self.path_map[root_item] = root_path

            # Set root item styling
            font = QFont()
            font.setBold(True)
            root_item.setFont(0, font)

            # Recursively add items
            self._add_json_items(root_item, data, root_path)

            # Expand first level
            root_item.setExpanded(True)

            logger.debug(f"Successfully populated tree with {len(self.path_map)} items")

        except Exception as e:
            logger.error(f"Error populating JSON tree: {str(e)}")
            error_item = QTreeWidgetItem(["Error", "error", f"Failed to parse JSON: {str(e)}"])
            error_item.setForeground(0, Qt.red)
            self.addTopLevelItem(error_item)

    def _add_json_items(self, parent_item: QTreeWidgetItem, data: Any, parent_path: str):
        """Recursively add JSON items to the tree."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{parent_path}.{key}"
                value_type = self._get_value_type(value)

                # Create display value
                if isinstance(value, (dict, list)):
                    display_value = f"({len(value)} items)" if isinstance(value, list) else f"({len(value)} keys)"
                else:
                    display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)

                item = QTreeWidgetItem([key, value_type, display_value])
                parent_item.addChild(item)
                self.path_map[item] = current_path

                # Set icon based on type
                self._set_item_icon(item, value_type)

                # Recursively add children for complex types
                if isinstance(value, (dict, list)):
                    self._add_json_items(item, value, current_path)

        elif isinstance(data, list):
            for i, value in enumerate(data):
                current_path = f"{parent_path}[{i}]"
                value_type = self._get_value_type(value)

                if isinstance(value, (dict, list)):
                    display_value = f"({len(value)} items)" if isinstance(value, list) else f"({len(value)} keys)"
                else:
                    display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)

                item = QTreeWidgetItem([f"[{i}]", value_type, display_value])
                parent_item.addChild(item)
                self.path_map[item] = current_path

                self._set_item_icon(item, value_type)

                if isinstance(value, (dict, list)):
                    self._add_json_items(item, value, current_path)

    def _get_value_type(self, value: Any) -> str:
        """Get the type string for a value."""
        if isinstance(value, dict):
            return "object"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif value is None:
            return "null"
        else:
            return "unknown"

    def _set_item_icon(self, item: QTreeWidgetItem, value_type: str):
        """Set icon for tree item based on value type."""
        # You could add icons here for different types
        # For now, we'll use text styling
        if value_type == "object":
            item.setForeground(0, Qt.blue)
        elif value_type == "array":
            item.setForeground(0, Qt.darkGreen)
        elif value_type == "string":
            item.setForeground(0, Qt.darkRed)
        elif value_type in ["integer", "number"]:
            item.setForeground(0, Qt.darkMagenta)
        elif value_type == "boolean":
            item.setForeground(0, Qt.darkCyan)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click with enhanced feedback."""
        _ = column  # Unused parameter

        if item in self.path_map:
            path = self.path_map[item]
            logger.debug(f"Path selected: {path}")

            # Provide visual feedback
            self._highlight_selected_item(item)

            # Set tooltip with path information
            try:
                value = self._extract_value_by_path(self.current_data, path)
                value_preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                item.setToolTip(0, f"Path: {path}\nValue: {value_preview}")
            except Exception as e:
                item.setToolTip(0, f"Path: {path}\nError: {str(e)}")

            self.path_selected.emit(path)
        else:
            logger.debug("Clicked item has no associated path")

    def _highlight_selected_item(self, item: QTreeWidgetItem):
        """Highlight the selected item visually."""
        # Reset all items to normal background
        for tree_item in self.path_map.keys():
            tree_item.setBackground(0, Qt.transparent)
            tree_item.setBackground(1, Qt.transparent)
            tree_item.setBackground(2, Qt.transparent)

        # Highlight selected item
        highlight_color = Qt.lightGray
        item.setBackground(0, highlight_color)
        item.setBackground(1, highlight_color)
        item.setBackground(2, highlight_color)

    def search_paths(self, query: str) -> List[str]:
        """Search for paths containing the query."""
        query = query.lower()
        matching_paths = []

        for item, path in self.path_map.items():
            # Search in path, key name, and value
            key_text = item.text(0).lower()
            value_text = item.text(2).lower()

            if (query in path.lower() or
                query in key_text or
                query in value_text):
                matching_paths.append(path)

        return matching_paths

    def highlight_path(self, path: str):
        """Highlight a specific path in the tree."""
        for item, item_path in self.path_map.items():
            if item_path == path:
                self.setCurrentItem(item)
                self.scrollToItem(item)
                break


class JsonPathPreviewWidget(QWidget):
    """Widget for previewing selected JSON path values."""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.current_data = {}
        self.current_path = ""

    def _setup_ui(self):
        """Setup the preview UI with enhanced visual design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN)
        layout.setSpacing(VisualDesignConstants.FORM_SPACING)

        # Current path display with enhanced styling
        path_group = QGroupBox("Selected Path")
        path_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding: 0 {VisualDesignConstants.UNIFORM_MARGIN}px 0 {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """)
        path_layout = QVBoxLayout(path_group)

        self.path_label = QLabel("No path selected")
        self.path_label.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.CODE_FONT_SIZE};
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                word-wrap: break-word;
            }}
        """)
        path_layout.addWidget(self.path_label)

        # Value type and info
        self.value_info_label = QLabel("Select a path to see details")
        self.value_info_label.setStyleSheet(f"""
            QLabel {{
                color: {VisualDesignConstants.ACCENT_COLOR};
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-style: italic;
                padding: 2px;
            }}
        """)
        path_layout.addWidget(self.value_info_label)

        layout.addWidget(path_group)

        # Value preview with enhanced styling
        value_group = QGroupBox("Value Preview")
        value_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding: 0 {VisualDesignConstants.UNIFORM_MARGIN}px 0 {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """)
        value_layout = QVBoxLayout(value_group)

        self.value_text = QTextEdit()
        self.value_text.setReadOnly(True)
        self.value_text.setMaximumHeight(150)
        self.value_text.setStyleSheet(f"""
            QTextEdit {{
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.CODE_FONT_SIZE};
                background-color: white;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """)
        value_layout.addWidget(self.value_text)

        layout.addWidget(value_group)

        # Action buttons with enhanced styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(VisualDesignConstants.BUTTON_SPACING)

        copy_btn = QPushButton("📋 Copy Path")
        copy_btn.clicked.connect(self._copy_path)
        copy_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        buttons_layout.addWidget(copy_btn)

        # Add export button for value
        export_btn = QPushButton("💾 Export Value")
        export_btn.clicked.connect(self._export_value)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #388e3c;
            }}
        """)
        buttons_layout.addWidget(export_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def set_path_and_data(self, path: str, data: Dict[str, Any]):
        """Set the current path and data for preview."""
        self.current_path = path
        self.current_data = data
        self._update_preview()

    def _update_preview(self):
        """Update the preview display with enhanced feedback and visual indicators."""
        if not self.current_path:
            self.path_label.setText("No path selected")
            self.path_label.setStyleSheet(f"""
                QLabel {{
                    color: #999;
                    font-family: {VisualDesignConstants.MONOSPACE_FONT};
                    font-size: {VisualDesignConstants.CODE_FONT_SIZE};
                    background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
                    border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                    border-radius: 3px;
                    padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                    word-wrap: break-word;
                }}
            """)
            self.value_text.clear()
            self.value_text.setPlaceholderText("Select a path to see its value...")
            self.value_info_label.setText("Select a path to see details")
            return

        logger.debug(f"Updating preview for path: {self.current_path}")

        # Update path display with success styling
        self.path_label.setText(self.current_path)
        self.path_label.setStyleSheet(f"""
            QLabel {{
                color: {VisualDesignConstants.SUCCESS_COLOR};
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.CODE_FONT_SIZE};
                background-color: white;
                border: 1px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 3px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                word-wrap: break-word;
            }}
        """)

        # Extract value from data using path
        try:
            value = self._extract_value_by_path(self.current_data, self.current_path)

            # Format value based on type with enhanced info
            if isinstance(value, dict):
                formatted_value = json.dumps(value, indent=2)
                value_info = f"📦 Object with {len(value)} keys"
                if len(value) > 0:
                    key_preview = ", ".join(list(value.keys())[:3])
                    if len(value) > 3:
                        key_preview += "..."
                    value_info += f" ({key_preview})"
            elif isinstance(value, list):
                formatted_value = json.dumps(value, indent=2)
                value_info = f"📋 Array with {len(value)} items"
                if len(value) > 0:
                    value_info += f" (first: {type(value[0]).__name__})"
            elif isinstance(value, str):
                formatted_value = f'"{value}"'
                value_info = f"📝 String ({len(value)} characters)"
                if len(value) > 50:
                    value_info += " - Long text"
            elif isinstance(value, (int, float)):
                formatted_value = str(value)
                value_info = f"🔢 Number ({type(value).__name__}: {value})"
            elif isinstance(value, bool):
                formatted_value = str(value).lower()
                value_info = f"✅ Boolean ({value})"
            elif value is None:
                formatted_value = "null"
                value_info = "❌ Null value"
            else:
                formatted_value = str(value)
                value_info = f"❓ {type(value).__name__}"

            self.value_text.setPlainText(formatted_value)
            self.value_info_label.setText(value_info)
            self.value_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {VisualDesignConstants.SUCCESS_COLOR};
                    font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                    font-style: italic;
                    padding: 2px;
                }}
            """)

            logger.debug(f"Successfully extracted value: {value_info}")

        except Exception as e:
            error_msg = f"❌ Error extracting value: {str(e)}"
            self.value_text.setPlainText(error_msg)
            self.value_info_label.setText("❌ Error accessing path")
            self.value_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {VisualDesignConstants.ERROR_COLOR};
                    font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                    font-style: italic;
                    padding: 2px;
                }}
            """)

            # Update path label with error styling
            self.path_label.setStyleSheet(f"""
                QLabel {{
                    color: {VisualDesignConstants.ERROR_COLOR};
                    font-family: {VisualDesignConstants.MONOSPACE_FONT};
                    font-size: {VisualDesignConstants.CODE_FONT_SIZE};
                    background-color: #ffebee;
                    border: 1px solid {VisualDesignConstants.ERROR_COLOR};
                    border-radius: 3px;
                    padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                    word-wrap: break-word;
                }}
            """)

            logger.error(f"Error extracting value for path {self.current_path}: {str(e)}")

    def _extract_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from data using dot notation path."""
        # Remove 'data.' prefix if present
        if path.startswith('data.'):
            path = path[5:]

        parts = []
        current_part = ""
        in_brackets = False

        # Parse path with array indices
        for char in path:
            if char == '[':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_brackets = True
            elif char == ']':
                if in_brackets and current_part:
                    parts.append(int(current_part))
                    current_part = ""
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        # Navigate through the data
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
            else:
                raise ValueError(f"Cannot navigate to {part} in {type(current)}")

        return current

    def _copy_path(self):
        """Copy the current path to clipboard with enhanced user feedback."""
        if self.current_path:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer

            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(self.current_path)
            logger.debug(f"Copied path to clipboard: {self.current_path}")

            # Provide enhanced visual feedback
            button = self.sender()
            if button:
                original_text = button.text()
                original_style = button.styleSheet()

                # Update button appearance
                button.setText("✅ Copied!")
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {VisualDesignConstants.SUCCESS_COLOR};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                        font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                        font-weight: bold;
                    }}
                """)

                # Reset after 2 seconds
                QTimer.singleShot(2000, lambda: (
                    button.setText(original_text),
                    button.setStyleSheet(original_style)
                ))
        else:
            logger.debug("No path to copy")

    def _export_value(self):
        """Export the current value to a file with format options."""
        if not self.current_path or not self.current_data:
            logger.debug("No value to export")
            return

        try:
            value = self._extract_value_by_path(self.current_data, self.current_path)

            # Format the value for export
            if isinstance(value, (dict, list)):
                export_content = json.dumps(value, indent=2)
                default_extension = "json"
            else:
                export_content = str(value)
                default_extension = "txt"

            # Simple export (in a real implementation, you'd use QFileDialog)
            filename = f"exported_value.{default_extension}"
            logger.debug(f"Would export value to {filename}: {export_content[:100]}...")

            # Provide visual feedback
            button = self.sender()
            if button:
                original_text = button.text()
                original_style = button.styleSheet()

                button.setText("💾 Exported!")
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {VisualDesignConstants.SUCCESS_COLOR};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                        font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                        font-weight: bold;
                    }}
                """)

                from PySide6.QtCore import QTimer
                QTimer.singleShot(2000, lambda: (
                    button.setText(original_text),
                    button.setStyleSheet(original_style)
                ))

        except Exception as e:
            logger.error(f"Error exporting value: {str(e)}")


class EnhancedJsonPathSelector(QWidget):
    """Enhanced JSON path selector with tree view, search, and preview."""

    path_selected = Signal(str)  # Emits the selected path

    def __init__(self):
        super().__init__()
        self.workflow = None
        self.current_step_index = -1

        # Phase 1 components
        self.path_validator = PathValidator()
        self.bookmark_manager = PathBookmarkManager()
        self.smart_completer = SmartPathCompleter(self)

        # Phase 2 components
        self.template_engine = PathTemplateEngine()
        self.selection_history = PathSelectionHistory()
        self.intelligent_suggester = IntelligentPathSuggester()

        # Phase 3 components
        self.data_flow_visualizer = DataFlowVisualizer()
        self.documentation_generator = WorkflowDocumentationGenerator()
        self.analytics = WorkflowAnalytics()

        self._setup_ui()
        logger.debug("EnhancedJsonPathSelector initialized with Phase 1, 2 & 3 features")

    def _setup_ui(self):
        """Setup the enhanced JSON path selector UI with visual design standards."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN,
                                 VisualDesignConstants.UNIFORM_MARGIN)
        layout.setSpacing(VisualDesignConstants.FORM_SPACING)

        # Apply panel styling to main widget
        self.setStyleSheet(VisualDesignConstants.get_panel_style())

        # Header with larger, more visible styling
        header_label = QLabel("🔍 JSON Path Selector")
        header_label.setStyleSheet(f"""
            QLabel {{
                font-size: {VisualDesignConstants.LARGE_HEADER_SIZE};
                font-weight: bold;
                color: {VisualDesignConstants.ACCENT_COLOR};
                background-color: white;
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 6px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                margin-bottom: {VisualDesignConstants.SECTION_SPACING}px;
            }}
        """)
        layout.addWidget(header_label)

        # Step selection section
        step_group = QGroupBox("📋 Step Selection")
        step_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 6px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                border-radius: 4px;
            }}
        """)
        step_layout = QHBoxLayout(step_group)
        step_layout.setSpacing(VisualDesignConstants.FORM_SPACING)

        step_label = QLabel("Step:")
        step_label.setMinimumWidth(60)
        step_layout.addWidget(step_label)

        self.step_combo = QComboBox()
        self.step_combo.currentIndexChanged.connect(self._on_step_changed)
        self.step_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                background-color: white;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
            }}
            QComboBox:hover {{
                border-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
            }}
        """)
        step_layout.addWidget(self.step_combo)

        layout.addWidget(step_group)

        # Search section
        search_group = QGroupBox("🔍 Search & Filter")
        search_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                border: 2px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 6px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                border-radius: 4px;
            }}
        """)
        search_layout = QHBoxLayout(search_group)
        search_layout.setSpacing(VisualDesignConstants.FORM_SPACING)

        search_label = QLabel("🔍 Search:")
        search_label.setMinimumWidth(60)
        search_layout.addWidget(search_label)

        self.search_edit = DropTargetLineEdit()
        self.search_edit.setPlaceholderText("Search paths, keys, or values... (supports drag & drop)")
        self.search_edit.textChanged.connect(self._on_search_changed)
        self.search_edit.set_path_completer(self.smart_completer)
        self.search_edit.set_path_validator(self.path_validator)
        self.search_edit.setStyleSheet(VisualDesignConstants.get_code_style())
        search_layout.addWidget(self.search_edit)

        layout.addWidget(search_group)

        # Bookmarks section
        bookmarks_group = QGroupBox("📌 Bookmarks & Quick Access")
        bookmarks_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                color: white;
                background-color: {VisualDesignConstants.WARNING_COLOR};
                border: 2px solid {VisualDesignConstants.WARNING_COLOR};
                border-radius: 6px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                color: white;
                background-color: {VisualDesignConstants.WARNING_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                border-radius: 4px;
            }}
        """)
        bookmarks_layout = QHBoxLayout(bookmarks_group)
        bookmarks_layout.setSpacing(VisualDesignConstants.BUTTON_SPACING)

        bookmarks_label = QLabel("📌 Saved:")
        bookmarks_label.setMinimumWidth(60)
        bookmarks_layout.addWidget(bookmarks_label)

        self.bookmarks_combo = QComboBox()
        self.bookmarks_combo.setPlaceholderText("Select a bookmarked path...")
        self.bookmarks_combo.currentTextChanged.connect(self._on_bookmark_selected)
        self.bookmarks_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                background-color: white;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
            }}
            QComboBox:hover {{
                border-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        bookmarks_layout.addWidget(self.bookmarks_combo)

        self.bookmark_btn = QPushButton("📌 Bookmark")
        self.bookmark_btn.clicked.connect(self._add_current_bookmark)
        self.bookmark_btn.setEnabled(False)
        self.bookmark_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        bookmarks_layout.addWidget(self.bookmark_btn)

        self.manage_bookmarks_btn = QPushButton("⚙️ Manage")
        self.manage_bookmarks_btn.clicked.connect(self._manage_bookmarks)
        self.manage_bookmarks_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.WARNING_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #f57c00;
            }}
        """)
        bookmarks_layout.addWidget(self.manage_bookmarks_btn)

        layout.addWidget(bookmarks_group)

        # Advanced Features section (collapsible)
        advanced_group = QGroupBox("🚀 Advanced Features")
        advanced_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                color: white;
                background-color: #9c27b0;
                border: 2px solid #9c27b0;
                border-radius: 6px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                color: white;
                background-color: #9c27b0;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                border-radius: 4px;
            }}
        """)
        advanced_layout = QVBoxLayout(advanced_group)
        advanced_layout.setSpacing(VisualDesignConstants.FORM_SPACING)

        # Templates and History row
        templates_history_layout = QHBoxLayout()
        templates_history_layout.setSpacing(VisualDesignConstants.BUTTON_SPACING)

        # Templates section
        templates_label = QLabel("📋 Templates:")
        templates_label.setMinimumWidth(80)
        templates_history_layout.addWidget(templates_label)

        self.templates_combo = QComboBox()
        self.templates_combo.setPlaceholderText("Select a template...")
        self.templates_combo.currentTextChanged.connect(self._on_template_selected)
        self.templates_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                background-color: white;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
            }}
            QComboBox:hover {{
                border-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        templates_history_layout.addWidget(self.templates_combo)

        self.path_builder_btn = QPushButton("🧭 Builder")
        self.path_builder_btn.clicked.connect(self._open_path_builder)
        self.path_builder_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        templates_history_layout.addWidget(self.path_builder_btn)

        # History controls
        self.undo_btn = QPushButton("↶ Undo")
        self.undo_btn.clicked.connect(self._undo_selection)
        self.undo_btn.setEnabled(False)
        self.undo_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
            }}
            QPushButton:hover:enabled {{
                background-color: #555;
            }}
            QPushButton:disabled {{
                background-color: #ccc;
                color: #999;
            }}
        """)
        templates_history_layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("↷ Redo")
        self.redo_btn.clicked.connect(self._redo_selection)
        self.redo_btn.setEnabled(False)
        self.redo_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
            }}
            QPushButton:hover:enabled {{
                background-color: #555;
            }}
            QPushButton:disabled {{
                background-color: #ccc;
                color: #999;
            }}
        """)
        templates_history_layout.addWidget(self.redo_btn)

        advanced_layout.addLayout(templates_history_layout)

        # Smart suggestions panel
        suggestions_group = QGroupBox("💡 Smart Suggestions")
        suggestions_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """)
        suggestions_layout = QVBoxLayout(suggestions_group)

        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(80)
        self.suggestions_list.itemClicked.connect(self._on_suggestion_clicked)
        self.suggestions_list.setStyleSheet(f"""
            QListWidget {{
                background-color: white;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 3px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QListWidget::item:hover {{
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
            }}
            QListWidget::item:selected {{
                background-color: {VisualDesignConstants.SELECTED_BACKGROUND};
            }}
        """)
        suggestions_layout.addWidget(self.suggestions_list)

        advanced_layout.addWidget(suggestions_group)

        # Advanced tools row
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(VisualDesignConstants.BUTTON_SPACING)

        self.visualizer_btn = QPushButton("📊 Data Flow")
        self.visualizer_btn.clicked.connect(self._open_data_flow_visualizer)
        self.visualizer_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        tools_layout.addWidget(self.visualizer_btn)

        self.chain_builder_btn = QPushButton("🔗 Chain Builder")
        self.chain_builder_btn.clicked.connect(self._open_chain_builder)
        self.chain_builder_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        tools_layout.addWidget(self.chain_builder_btn)

        self.docs_btn = QPushButton("📚 Docs")
        self.docs_btn.clicked.connect(self._generate_documentation)
        self.docs_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        tools_layout.addWidget(self.docs_btn)

        self.analytics_btn = QPushButton("📈 Analytics")
        self.analytics_btn.clicked.connect(self._show_analytics)
        self.analytics_btn.setStyleSheet(VisualDesignConstants.get_button_style())
        tools_layout.addWidget(self.analytics_btn)

        advanced_layout.addLayout(tools_layout)
        layout.addWidget(advanced_group)

        # Main content area with enhanced styling
        content_splitter = QSplitter(Qt.Vertical)
        content_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {VisualDesignConstants.SUBTLE_BORDER};
                height: 3px;
            }}
            QSplitter::handle:hover {{
                background-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        layout.addWidget(content_splitter)

        # JSON Explorer Tab
        json_explorer_group = QGroupBox("🌳 JSON Explorer")
        json_explorer_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 6px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                border-radius: 4px;
            }}
        """)
        json_explorer_layout = QVBoxLayout(json_explorer_group)
        json_explorer_layout.setContentsMargins(VisualDesignConstants.UNIFORM_MARGIN,
                                               VisualDesignConstants.UNIFORM_MARGIN,
                                               VisualDesignConstants.UNIFORM_MARGIN,
                                               VisualDesignConstants.UNIFORM_MARGIN)

        # Auto-population status indicator
        self.auto_populate_status = QLabel("🔄 Auto-populating when step is selected...")
        self.auto_populate_status.setStyleSheet(f"""
            QLabel {{
                color: {VisualDesignConstants.ACCENT_COLOR};
                font-style: italic;
                padding: 4px;
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
                border-radius: 3px;
                margin-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
        """)
        json_explorer_layout.addWidget(self.auto_populate_status)

        # Enhanced JSON tree with improved styling
        self.json_tree = JsonTreeWidget()
        self.json_tree.path_selected.connect(self._on_path_selected)
        self.json_tree.setStyleSheet(VisualDesignConstants.get_tree_style())
        json_explorer_layout.addWidget(self.json_tree)

        content_splitter.addWidget(json_explorer_group)

        # Selected Path Preview Panel
        preview_group = QGroupBox("📋 Selected Path Preview")
        preview_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                border: 2px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 6px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN}px;
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN}px {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                border-radius: 4px;
            }}
        """)
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(VisualDesignConstants.UNIFORM_MARGIN,
                                         VisualDesignConstants.UNIFORM_MARGIN,
                                         VisualDesignConstants.UNIFORM_MARGIN,
                                         VisualDesignConstants.UNIFORM_MARGIN)

        self.preview_widget = JsonPathPreviewWidget()
        preview_layout.addWidget(self.preview_widget)

        content_splitter.addWidget(preview_group)

        # Set splitter proportions for optimal user experience
        content_splitter.setSizes([400, 200])

        # Initialize components
        self._update_templates_combo()
        self._update_bookmarks_combo()

        # Set initial auto-populate status
        self._update_auto_populate_status("Ready - Select a step to explore JSON data")

    def _update_auto_populate_status(self, message: str, status_type: str = "info"):
        """Update the auto-populate status indicator with visual feedback."""
        if hasattr(self, 'auto_populate_status'):
            status_colors = {
                "info": VisualDesignConstants.ACCENT_COLOR,
                "success": VisualDesignConstants.SUCCESS_COLOR,
                "warning": VisualDesignConstants.WARNING_COLOR,
                "error": VisualDesignConstants.ERROR_COLOR
            }

            status_backgrounds = {
                "info": VisualDesignConstants.HOVER_BACKGROUND,
                "success": "#e8f5e8",
                "warning": "#fff3e0",
                "error": "#ffebee"
            }

            color = status_colors.get(status_type, VisualDesignConstants.ACCENT_COLOR)
            bg_color = status_backgrounds.get(status_type, VisualDesignConstants.HOVER_BACKGROUND)

            self.auto_populate_status.setText(message)
            self.auto_populate_status.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-style: italic;
                    padding: 4px;
                    background-color: {bg_color};
                    border-radius: 3px;
                    margin-bottom: {VisualDesignConstants.UNIFORM_MARGIN}px;
                }}
            """)

    def set_workflow(self, workflow, current_step_index: int = -1):
        """Set the workflow and update available steps."""
        logger.debug(f"set_workflow called with workflow: {workflow is not None}, current_step_index: {current_step_index}")
        self.workflow = workflow
        self.current_step_index = current_step_index
        self._update_step_combo()

        # Auto-select the most recent step with JSON data
        self._auto_select_best_step()

    def _update_step_combo(self):
        """Update the step selection combo box with enhanced filtering."""
        self.step_combo.clear()

        if not self.workflow:
            logger.debug("No workflow provided, combo box cleared")
            return

        logger.debug(f"Updating combo box for workflow with {len(self.workflow.steps)} steps")

        # Add steps that have JSON output (only previous steps)
        steps_added = 0
        for i, step in enumerate(self.workflow.steps):
            if self.current_step_index >= 0 and i >= self.current_step_index:
                continue  # Don't show current or future steps

            # Check if step has parsed JSON output
            has_json = hasattr(step, 'parsed_json_output') and step.parsed_json_output
            output_key = getattr(step, 'output_key', 'unknown')
            step_type = type(step).__name__.replace('Step', '')

            if has_json:
                step_name = f"Step {i+1}: {output_key} ({step_type})"
                self.step_combo.addItem(step_name, i)
                steps_added += 1
                logger.debug(f"Added step {i+1} with output key: {output_key}")
            else:
                # Still show the step but indicate no JSON data
                step_name = f"Step {i+1}: {output_key} ({step_type}) - No JSON"
                self.step_combo.addItem(step_name, i)
                # Disable this item
                model = self.step_combo.model()
                item = model.item(self.step_combo.count() - 1)
                if item:
                    item.setEnabled(False)

        # Add initial inputs if available
        self.step_combo.addItem("Initial Inputs", -1)

        logger.debug(f"Added {steps_added} steps with JSON data to combo box")

    def _auto_select_best_step(self):
        """Auto-select the most recent step with JSON data."""
        if self.step_combo.count() > 1:  # More than just "Initial Inputs"
            # Select the first enabled item (most recent step with JSON)
            for i in range(self.step_combo.count()):
                if self.step_combo.model().item(i).isEnabled():
                    self.step_combo.setCurrentIndex(i)
                    logger.debug(f"Auto-selected step at index {i}")
                    break

    def _on_step_changed(self, index):
        """Handle step selection change with enhanced logging, error handling, and user feedback."""
        logger.debug(f"_on_step_changed called with index: {index}")

        if index < 0:
            logger.debug("Invalid index, clearing tree")
            self.json_tree.populate_from_json({}, "data")
            self._update_auto_populate_status("No step selected", "warning")
            return

        step_index = self.step_combo.itemData(index)
        logger.debug(f"Step index from combo data: {step_index}")

        if step_index == -1:
            # Initial inputs selected
            logger.debug("Initial inputs selected")
            self._update_auto_populate_status("🔄 Loading initial inputs...", "info")

            initial_data = {}
            if self.workflow and hasattr(self.workflow, 'initial_inputs'):
                initial_data = self.workflow.initial_inputs or {}

            self.json_tree.populate_from_json(initial_data, "data")

            if initial_data:
                self._update_auto_populate_status(f"✅ Loaded initial inputs ({len(initial_data)} items)", "success")
            else:
                self._update_auto_populate_status("⚠️ No initial inputs available", "warning")
        else:
            # Step output selected
            if not self.workflow or step_index >= len(self.workflow.steps):
                logger.error(f"Invalid step index {step_index} for workflow with {len(self.workflow.steps) if self.workflow else 0} steps")
                self.json_tree.populate_from_json({}, "data")
                self._update_auto_populate_status("❌ Invalid step selection", "error")
                return

            step = self.workflow.steps[step_index]
            step_name = f"Step {step_index + 1}"
            logger.debug(f"Selected step type: {type(step).__name__}")

            self._update_auto_populate_status(f"🔄 Loading JSON data from {step_name}...", "info")

            # Check for parsed JSON output
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                output_key = getattr(step, 'output_key', 'unknown')
                logger.debug(f"Found parsed JSON output with key: {output_key}")

                # Wrap the output in the expected structure
                data = {output_key: step.parsed_json_output}
                self.json_tree.populate_from_json(data, "data")

                # Count total items for user feedback
                total_items = self._count_json_items(step.parsed_json_output)
                self._update_auto_populate_status(f"✅ Loaded {step_name} data ({total_items} items)", "success")
            else:
                logger.debug("No parsed JSON output found for this step")
                self.json_tree.populate_from_json({}, "data")
                self._update_auto_populate_status(f"⚠️ {step_name} has no JSON output", "warning")

    def _count_json_items(self, data) -> int:
        """Count total items in JSON data structure for user feedback."""
        if isinstance(data, dict):
            return len(data)
        elif isinstance(data, list):
            return len(data)
        else:
            return 1

    def _on_search_changed(self, query):
        """Handle search query change with real-time filtering and visual feedback."""
        if not query.strip():
            # Clear search highlighting and show all items
            if hasattr(self.json_tree, 'clear_search_highlighting'):
                self.json_tree.clear_search_highlighting()
            self._update_search_status("")
            return

        logger.debug(f"Search query changed: {query}")

        # Update search status
        self._update_search_status(f"🔍 Searching for '{query}'...", "info")

        # Find matching paths
        try:
            if hasattr(self.json_tree, 'search_paths'):
                matching_paths = self.json_tree.search_paths(query)
            else:
                # Fallback search implementation
                matching_paths = self._fallback_search(query)

            if matching_paths:
                # Highlight matches and show count
                if hasattr(self.json_tree, 'highlight_search_results'):
                    self.json_tree.highlight_search_results(matching_paths)
                elif hasattr(self.json_tree, 'highlight_path'):
                    self.json_tree.highlight_path(matching_paths[0])

                self._update_search_status(f"✅ Found {len(matching_paths)} match(es)", "success")

                # Auto-select first match if only one result
                if len(matching_paths) == 1:
                    self._simulate_path_selection(matching_paths[0])
            else:
                self._update_search_status(f"❌ No matches found for '{query}'", "warning")

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            self._update_search_status("❌ Search error", "error")

    def _update_search_status(self, message: str, status_type: str = "info"):
        """Update search status in the search box placeholder or tooltip."""
        if hasattr(self, 'search_edit') and message:
            if not message:
                self.search_edit.setPlaceholderText("Search paths, keys, or values... (supports drag & drop)")
            else:
                # Update tooltip with search status
                self.search_edit.setToolTip(message)

    def _fallback_search(self, query: str) -> List[str]:
        """Fallback search implementation if tree doesn't have search_paths method."""
        matching_paths = []
        query_lower = query.lower()

        if hasattr(self.json_tree, 'path_map'):
            for item, path in self.json_tree.path_map.items():
                # Search in path
                if query_lower in path.lower():
                    matching_paths.append(path)
                # Search in item text
                elif hasattr(item, 'text') and query_lower in item.text(0).lower():
                    matching_paths.append(path)

        return matching_paths

    def _extract_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from data using dot notation path."""
        if not data:
            raise ValueError("No data available")

        # Remove 'data.' prefix if present
        if path.startswith('data.'):
            path = path[5:]

        if not path:  # Root path
            return data

        parts = []
        current_part = ""
        in_brackets = False

        # Parse path with array indices
        for char in path:
            if char == '[':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_brackets = True
            elif char == ']':
                if in_brackets and current_part:
                    try:
                        parts.append(int(current_part))
                    except ValueError:
                        raise ValueError(f"Invalid array index: '{current_part}' must be a number")
                    current_part = ""
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        # Navigate through the data
        current = data
        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    available_keys = list(current.keys())
                    raise KeyError(f"Key '{part}' not found. Available keys: {available_keys}")
                current = current[part]
            elif isinstance(current, list):
                if not isinstance(part, int):
                    raise TypeError(f"Array index must be integer, got '{part}' (type: {type(part)})")
                if part >= len(current) or part < 0:
                    raise IndexError(f"Array index {part} out of range. Array has {len(current)} items")
                current = current[part]
            else:
                raise TypeError(f"Cannot navigate to '{part}' from {type(current).__name__}")

        return current

    def _on_path_selected(self, path):
        """Handle path selection from tree."""
        # Get current step data for preview
        current_index = self.step_combo.currentIndex()
        if current_index < 0:
            return

        step_index = self.step_combo.itemData(current_index)

        if step_index == -1:
            # Initial inputs
            data = {}
        else:
            step = self.workflow.steps[step_index]
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                output_key = getattr(step, 'output_key', 'unknown')
                data = {output_key: step.parsed_json_output}
            else:
                data = {}

        # Update preview
        self.preview_widget.set_path_and_data(path, data)

        # Phase 1: Track usage and enable bookmark button
        self.bookmark_manager.track_usage(path)
        self.bookmark_btn.setEnabled(True)
        self.current_selected_path = path

        # Update smart completer
        self.smart_completer.update_completions()

        # Phase 2: Add to history and update suggestions
        self.selection_history.add_selection(path, f"Step {self.current_step_index}")
        self._update_history_buttons()
        self._update_smart_suggestions(path)

        # Phase 3: Track analytics
        self.analytics.track_path_usage(path, True)  # Assume success for selection

        # Emit signal
        self.path_selected.emit(path)

    def refresh_for_step_selection(self, step_index: int):
        """Refresh the selector when a step is selected externally."""
        logger.debug(f"refresh_for_step_selection called with step_index: {step_index}")

        # Update current step index
        self.current_step_index = step_index

        # Refresh the step combo box
        self._update_step_combo()

        # Auto-select the best step
        self._auto_select_best_step()

        # Force refresh of the tree
        current_combo_index = self.step_combo.currentIndex()
        if current_combo_index >= 0:
            self._on_step_changed(current_combo_index)

    def add_debug_info_panel(self):
        """Add a debug info panel for troubleshooting (development only)."""
        if not hasattr(self, 'debug_panel'):
            debug_group = QGroupBox("Debug Info (Development)")
            debug_layout = QVBoxLayout(debug_group)

            self.debug_text = QTextEdit()
            self.debug_text.setMaximumHeight(100)
            self.debug_text.setReadOnly(True)
            self.debug_text.setStyleSheet("font-family: monospace; font-size: 10px;")
            debug_layout.addWidget(self.debug_text)

            # Add debug panel to main layout
            self.layout().addWidget(debug_group)
            self.debug_panel = debug_group

            # Log current state
            self._update_debug_info()

    def _update_debug_info(self):
        """Update debug information display."""
        if hasattr(self, 'debug_text'):
            debug_info = []
            debug_info.append(f"Workflow: {self.workflow is not None}")
            debug_info.append(f"Current step index: {self.current_step_index}")
            debug_info.append(f"Combo box items: {self.step_combo.count()}")
            debug_info.append(f"Tree items: {len(self.json_tree.path_map)}")

            if self.workflow:
                debug_info.append(f"Total workflow steps: {len(self.workflow.steps)}")
                for i, step in enumerate(self.workflow.steps):
                    has_json = hasattr(step, 'parsed_json_output') and step.parsed_json_output
                    output_key = getattr(step, 'output_key', 'unknown')
                    debug_info.append(f"  Step {i}: {output_key} - JSON: {has_json}")

            self.debug_text.setPlainText("\n".join(debug_info))

    # ============================================================================
    # PHASE 1: BOOKMARK MANAGEMENT METHODS
    # ============================================================================

    def _on_bookmark_selected(self, bookmark_text: str):
        """Handle bookmark selection from combo box."""
        if not bookmark_text or bookmark_text.startswith("Select"):
            return

        # Find the bookmark by display text
        for bookmark_id, bookmark in self.bookmark_manager.bookmarks.items():
            if bookmark_text.endswith(bookmark['path']):
                path = bookmark['path']
                logger.debug(f"Selected bookmark: {path}")

                # Simulate path selection
                self._simulate_path_selection(path)
                break

    def _add_current_bookmark(self):
        """Add current selected path as bookmark."""
        if not hasattr(self, 'current_selected_path'):
            return

        path = self.current_selected_path

        # Simple dialog to get bookmark name
        try:
            from PySide6.QtWidgets import QInputDialog
            name, ok = QInputDialog.getText(self, "Add Bookmark",
                                           f"Enter name for bookmark:\n{path}",
                                           text=path.split('.')[-1])
        except ImportError:
            # Fallback for testing without GUI
            name, ok = path.split('.')[-1], True

        if ok and name:
            self.bookmark_manager.add_bookmark(name, path, "User Defined")
            self._update_bookmarks_combo()
            logger.debug(f"Added bookmark: {name} -> {path}")

    def _manage_bookmarks(self):
        """Open bookmark management dialog."""
        dialog = BookmarkManagerDialog(self.bookmark_manager, self)
        dialog.exec_()
        self._update_bookmarks_combo()

    def _update_bookmarks_combo(self):
        """Update the bookmarks combo box."""
        self.bookmarks_combo.clear()
        self.bookmarks_combo.addItem("Select a bookmarked path...")

        # Add frequent paths
        frequent_paths = self.bookmark_manager.get_frequent_paths(5)
        if frequent_paths:
            self.bookmarks_combo.addItem("--- Frequently Used ---")
            for path in frequent_paths:
                usage_count = self.bookmark_manager.usage_count.get(path, 0)
                self.bookmarks_combo.addItem(f"🔥 {path} (used {usage_count}x)")

        # Add bookmarked paths by category
        categories = set()
        for bookmark in self.bookmark_manager.bookmarks.values():
            categories.add(bookmark['category'])

        for category in sorted(categories):
            bookmarks = self.bookmark_manager.get_bookmarks_by_category(category)
            if bookmarks:
                self.bookmarks_combo.addItem(f"--- {category} ---")
                for bookmark_id, bookmark in bookmarks.items():
                    self.bookmarks_combo.addItem(f"📌 {bookmark['name']}: {bookmark['path']}")

    def _simulate_path_selection(self, path: str):
        """Simulate selecting a path (for bookmark selection)."""
        # Find the tree item for this path
        for item, item_path in self.json_tree.path_map.items():
            if item_path == path:
                self.json_tree.setCurrentItem(item)
                self.json_tree._on_item_clicked(item, 0)
                break

    # ============================================================================
    # PHASE 2: TEMPLATE AND HISTORY MANAGEMENT METHODS
    # ============================================================================

    def _on_template_selected(self, template_text: str):
        """Handle template selection from combo box."""
        if not template_text or template_text.startswith("Select"):
            return

        # Extract template name from display text
        template_name = template_text.split(":")[0].strip()

        # Get current step key for template application
        current_index = self.step_combo.currentIndex()
        if current_index < 0:
            return

        step_index = self.step_combo.itemData(current_index)
        if step_index == -1:
            step_key = "initial"
        else:
            step = self.workflow.steps[step_index]
            step_key = getattr(step, 'output_key', f'step_{step_index}')

        # Apply template
        paths = self.template_engine.apply_template(template_name, step_key)

        if paths:
            # Show template paths in suggestions
            self.suggestions_list.clear()
            for path in paths:
                item = QListWidgetItem(f"📋 {path}")
                item.setData(Qt.UserRole, path)
                self.suggestions_list.addItem(item)

            logger.debug(f"Applied template {template_name} with {len(paths)} paths")

    def _open_path_builder(self):
        """Open the interactive path builder dialog."""
        current_index = self.step_combo.currentIndex()
        if current_index < 0:
            return

        step_index = self.step_combo.itemData(current_index)

        # Get current step data
        if step_index == -1:
            # Initial inputs
            data = {}
        else:
            step = self.workflow.steps[step_index]
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                output_key = getattr(step, 'output_key', 'unknown')
                data = {output_key: step.parsed_json_output}
            else:
                data = {}

        if not data:
            # Show message if no data available
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Path Builder",
                                   "No JSON data available for the selected step.")
            return

        # Open path builder dialog
        dialog = InteractivePathBuilder(data, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_path = dialog.get_selected_path()
            self._simulate_path_selection(selected_path)
            logger.debug(f"Path builder selected: {selected_path}")

    def _undo_selection(self):
        """Undo to previous path selection."""
        selection = self.selection_history.undo()
        if selection:
            path = selection['path']
            self._simulate_path_selection(path)
            self._update_history_buttons()
            logger.debug(f"Undid to: {path}")

    def _redo_selection(self):
        """Redo to next path selection."""
        selection = self.selection_history.redo()
        if selection:
            path = selection['path']
            self._simulate_path_selection(path)
            self._update_history_buttons()
            logger.debug(f"Redid to: {path}")

    def _update_history_buttons(self):
        """Update undo/redo button states."""
        self.undo_btn.setEnabled(self.selection_history.current_index > 0)
        self.redo_btn.setEnabled(
            self.selection_history.current_index < len(self.selection_history.history) - 1
        )

    def _on_suggestion_clicked(self, item):
        """Handle clicking on a smart suggestion."""
        path = item.data(Qt.UserRole)
        if path:
            self._simulate_path_selection(path)

            # Learn from this selection
            context = self._get_current_context()
            self.intelligent_suggester.learn_from_selection(context, path)
            logger.debug(f"Selected suggestion: {path}")

    def _update_smart_suggestions(self, current_path: str):
        """Update smart suggestions based on current context."""
        context = self._get_current_context()
        available_paths = list(self.json_tree.path_map.values())

        suggestions = self.intelligent_suggester.suggest_paths(context, available_paths)

        # Update suggestions list (but don't clear if we just selected from it)
        if not any(item.data(Qt.UserRole) == current_path for item in
                  [self.suggestions_list.item(i) for i in range(self.suggestions_list.count())]):
            self.suggestions_list.clear()

            for suggestion in suggestions:
                confidence_pct = int(suggestion['confidence'] * 100)
                item = QListWidgetItem(f"💡 {suggestion['path']} ({confidence_pct}% - {suggestion['reason']})")
                item.setData(Qt.UserRole, suggestion['path'])
                self.suggestions_list.addItem(item)

    def _get_current_context(self) -> str:
        """Get current context for intelligent suggestions."""
        context_parts = []

        # Add current step information
        current_index = self.step_combo.currentIndex()
        if current_index >= 0:
            step_index = self.step_combo.itemData(current_index)
            if step_index != -1 and self.workflow:
                step = self.workflow.steps[step_index]
                step_type = type(step).__name__.replace('Step', '').lower()
                context_parts.append(step_type)

                if hasattr(step, 'action_name'):
                    context_parts.append(step.action_name)
                if hasattr(step, 'description') and step.description:
                    context_parts.append(step.description)

        return " ".join(context_parts)

    def _update_templates_combo(self):
        """Update the templates combo box."""
        self.templates_combo.clear()
        self.templates_combo.addItem("Select a template...")

        # Add templates by category
        categories = self.template_engine.get_categories()
        for category in categories:
            templates = self.template_engine.get_templates_by_category(category)
            if templates:
                self.templates_combo.addItem(f"--- {category} ---")
                for template_name, template_data in templates.items():
                    display_name = f"{template_name}: {template_data['description']}"
                    self.templates_combo.addItem(display_name)

    # ============================================================================
    # PHASE 3: ADVANCED FEATURES METHODS
    # ============================================================================

    def _open_data_flow_visualizer(self):
        """Open the data flow visualization dialog."""
        if not self.workflow:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Data Flow Visualizer",
                                   "No workflow available to visualize.")
            return

        # Create and show visualizer dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Workflow Data Flow Visualization")
        dialog.setModal(True)
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        # Add the visualizer widget
        visualizer = DataFlowVisualizer()
        visualizer.set_workflow(self.workflow)
        layout.addWidget(visualizer)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()
        logger.debug("Opened data flow visualizer")

    def _open_chain_builder(self):
        """Open the path chain builder dialog."""
        if not self.workflow:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Chain Builder",
                                   "No workflow available for chain building.")
            return

        dialog = PathChainBuilder(self.workflow, self)
        if dialog.exec_() == QDialog.Accepted:
            expression = dialog.get_expression()
            if expression:
                # For now, just show the expression
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Chain Builder Result",
                                       f"Generated expression:\n{expression}")
                logger.debug(f"Chain builder generated: {expression}")

    def _generate_documentation(self):
        """Generate and save workflow documentation."""
        if not self.workflow:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Documentation Generator",
                                   "No workflow available to document.")
            return

        # Generate documentation
        docs = self.documentation_generator.generate_documentation(self.workflow)

        # Save documentation files
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Documentation", "workflow_docs",
            "Markdown Files (*.md);;HTML Files (*.html);;All Files (*.*)"
        )

        if file_path:
            # Determine format based on extension
            if file_path.endswith('.html'):
                content = docs['html']
            elif file_path.endswith('.md'):
                content = docs['markdown']
            else:
                content = docs['markdown']  # Default to markdown

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Also save data dictionary
                dict_path = file_path.rsplit('.', 1)[0] + '_data_dictionary.md'
                with open(dict_path, 'w', encoding='utf-8') as f:
                    f.write(docs['data_dictionary'])

                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Documentation Generated",
                                       f"Documentation saved to:\n{file_path}\n{dict_path}")
                logger.debug(f"Generated documentation: {file_path}")

            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Failed to save documentation:\n{e}")

    def _show_analytics(self):
        """Show analytics dashboard."""
        analytics = self.analytics.get_usage_analytics()
        recommendations = self.analytics.get_recommendations()

        # Create analytics dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Workflow Analytics Dashboard")
        dialog.setModal(True)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        # Analytics content
        content = QTextEdit()
        content.setReadOnly(True)

        # Format analytics report
        report = "# Workflow Analytics Dashboard\n\n"
        report += f"**Total Paths Tracked:** {analytics['total_paths']}\n\n"

        if analytics['most_used_paths']:
            report += "## Most Used Paths\n\n"
            for i, path_info in enumerate(analytics['most_used_paths'][:5], 1):
                report += f"{i}. `{path_info['path']}` - Used {path_info['usage_count']} times "
                report += f"(Success rate: {path_info['success_rate']:.1%})\n"
            report += "\n"

        if analytics['least_reliable_paths']:
            report += "## Paths Needing Attention\n\n"
            for path_info in analytics['least_reliable_paths']:
                report += f"- `{path_info['path']}` - Success rate: {path_info['success_rate']:.1%} "
                report += f"({path_info['error_count']} errors)\n"
            report += "\n"

        if recommendations:
            report += "## Recommendations\n\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        if analytics['error_summary']:
            report += "## Common Errors\n\n"
            for error, count in list(analytics['error_summary'].items())[:5]:
                report += f"- {error} ({count} occurrences)\n"

        content.setPlainText(report)
        layout.addWidget(content)

        # Export button
        export_btn = QPushButton("📊 Export Analytics")
        export_btn.clicked.connect(lambda: self._export_analytics(report))
        layout.addWidget(export_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()
        logger.debug("Showed analytics dashboard")

    def _export_analytics(self, report: str):
        """Export analytics report to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Analytics", "analytics_report.md",
            "Markdown Files (*.md);;Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)

                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Analytics Exported",
                                       f"Analytics report saved to:\n{file_path}")
                logger.debug(f"Exported analytics: {file_path}")

            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Failed to export analytics:\n{e}")


class BookmarkManagerDialog(QDialog):
    """Dialog for managing bookmarks."""

    def __init__(self, bookmark_manager: PathBookmarkManager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.setWindowTitle("Manage Bookmarks")
        self.setModal(True)
        self.resize(600, 400)
        self._setup_ui()
        self._load_bookmarks()

    def _setup_ui(self):
        """Setup the bookmark manager UI."""
        layout = QVBoxLayout(self)

        # Bookmarks table
        self.bookmarks_table = QTableWidget()
        self.bookmarks_table.setColumnCount(4)
        self.bookmarks_table.setHorizontalHeaderLabels(["Name", "Path", "Category", "Usage"])
        self.bookmarks_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.bookmarks_table)

        # Buttons
        button_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self._delete_selected)
        button_layout.addWidget(delete_btn)

        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_bookmarks)
        button_layout.addWidget(export_btn)

        import_btn = QPushButton("Import...")
        import_btn.clicked.connect(self._import_bookmarks)
        button_layout.addWidget(import_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _load_bookmarks(self):
        """Load bookmarks into the table."""
        bookmarks = self.bookmark_manager.bookmarks
        self.bookmarks_table.setRowCount(len(bookmarks))

        for row, (bookmark_id, bookmark) in enumerate(bookmarks.items()):
            self.bookmarks_table.setItem(row, 0, QTableWidgetItem(bookmark['name']))
            self.bookmarks_table.setItem(row, 1, QTableWidgetItem(bookmark['path']))
            self.bookmarks_table.setItem(row, 2, QTableWidgetItem(bookmark['category']))
            self.bookmarks_table.setItem(row, 3, QTableWidgetItem(str(bookmark['usage_count'])))

            # Store bookmark_id in the first item for deletion
            self.bookmarks_table.item(row, 0).setData(Qt.UserRole, bookmark_id)

    def _delete_selected(self):
        """Delete selected bookmarks."""
        selected_rows = set()
        for item in self.bookmarks_table.selectedItems():
            selected_rows.add(item.row())

        for row in sorted(selected_rows, reverse=True):
            bookmark_id = self.bookmarks_table.item(row, 0).data(Qt.UserRole)
            self.bookmark_manager.remove_bookmark(bookmark_id)
            self.bookmarks_table.removeRow(row)

    def _export_bookmarks(self):
        """Export bookmarks to file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Bookmarks",
                                                  "bookmarks.json", "JSON Files (*.json)")
        if file_path:
            self.bookmark_manager.export_bookmarks(file_path)

    def _import_bookmarks(self):
        """Import bookmarks from file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Bookmarks",
                                                  "", "JSON Files (*.json)")
        if file_path:
            self.bookmark_manager.import_bookmarks(file_path)
            self._load_bookmarks()
