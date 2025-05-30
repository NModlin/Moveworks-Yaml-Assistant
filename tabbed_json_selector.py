#!/usr/bin/env python3
"""
Tabbed JSON Path Selector with Collapsible Sections.

This module provides a clean, organized JSON Path Selector using tabs
and collapsible sections to reduce clutter and improve usability.
"""

import sys
import json
import logging
from typing import Dict, Any, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter, QTabWidget,
    QComboBox, QApplication, QCompleter, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QFont

# Import our components
from collapsible_widget import CollapsibleContainer, CollapsibleSection
from enhanced_json_selector import (
    VisualDesignConstants, JsonTreeWidget, JsonPathPreviewWidget,
    PathBookmarkManager, IntelligentPathSuggester
)
from core_structures import Workflow

logger = logging.getLogger(__name__)


class TabbedJsonPathSelector(QWidget):
    """
    A clean, tabbed JSON Path Selector with collapsible sections.

    Features:
    - Tabbed interface for better organization
    - Collapsible sections to reduce clutter
    - Essential features prominently displayed
    - Advanced features in separate tabs
    - Clean, modern design
    """

    # Signals
    path_selected = Signal(str)
    step_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workflow = None
        self.current_step_index = 0
        self.selected_path = ""

        # Initialize managers
        self.bookmark_manager = PathBookmarkManager()
        self.path_suggester = IntelligentPathSuggester()

        self._setup_ui()
        self._connect_signals()

        logger.debug("TabbedJsonPathSelector initialized")

    def _setup_ui(self):
        """Setup the tabbed UI structure."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 6px;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-bottom: none;
                border-radius: 6px 6px 0px 0px;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 2px solid white;
                color: {VisualDesignConstants.ACCENT_COLOR};
            }}
            QTabBar::tab:hover {{
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
            }}
        """)

        # Create tabs
        self._create_main_tab()
        self._create_advanced_tab()
        self._create_help_tab()

        layout.addWidget(self.tab_widget)

    def _create_header(self):
        """Create the main header section."""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Title
        title = QLabel("🎯 JSON Path Selector")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {VisualDesignConstants.ACCENT_COLOR};
                background-color: white;
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        # Quick step selection (always visible)
        step_section = self._create_step_selection()
        header_layout.addWidget(step_section)

        return header_widget

    def _create_step_selection(self):
        """Create the step selection section."""
        step_widget = QWidget()
        step_layout = QHBoxLayout(step_widget)
        step_layout.setContentsMargins(12, 8, 12, 8)
        step_layout.setSpacing(12)

        step_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 6px;
            }}
        """)

        # Step label
        step_label = QLabel("📋 Select Step:")
        step_label.setStyleSheet(f"""
            QLabel {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
                color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        step_layout.addWidget(step_label)

        # Step combo box
        self.step_combo = QComboBox()
        self.step_combo.setStyleSheet(f"""
            QComboBox {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                padding: 8px 12px;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                background-color: white;
                min-width: 300px;
            }}
            QComboBox:hover {{
                border-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 1px solid {VisualDesignConstants.ACCENT_COLOR};
                width: 8px;
                height: 8px;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        step_layout.addWidget(self.step_combo)

        # Status indicator
        self.step_status = QLabel("No workflow loaded")
        self.step_status.setStyleSheet(f"""
            QLabel {{
                color: {VisualDesignConstants.WARNING_COLOR};
                font-style: italic;
                font-size: {VisualDesignConstants.SMALL_FONT_SIZE};
            }}
        """)
        step_layout.addWidget(self.step_status)

        step_layout.addStretch()

        return step_widget

    def _create_main_tab(self):
        """Create the main tab with essential features."""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Create collapsible container
        container = CollapsibleContainer()

        # Search section (always expanded)
        search_content = self._create_search_section()
        search_section = container.add_section(
            "🔍 Search & Filter",
            search_content,
            VisualDesignConstants.SUCCESS_COLOR,
            True
        )

        # JSON Explorer section (always expanded)
        explorer_content = self._create_json_explorer()
        explorer_section = container.add_section(
            "🌳 JSON Explorer",
            explorer_content,
            VisualDesignConstants.ACCENT_COLOR,
            True
        )

        # Path Preview section (collapsible)
        preview_content = self._create_path_preview()
        preview_section = container.add_section(
            "📋 Selected Path",
            preview_content,
            VisualDesignConstants.WARNING_COLOR,
            False
        )

        # Add container to scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        main_layout.addWidget(scroll_area)

        self.tab_widget.addTab(main_tab, "🎯 Main")

    def _create_advanced_tab(self):
        """Create the advanced features tab."""
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setContentsMargins(8, 8, 8, 8)
        advanced_layout.setSpacing(8)

        # Create collapsible container
        container = CollapsibleContainer()

        # Bookmarks section
        bookmarks_content = self._create_bookmarks_section()
        container.add_section(
            "📌 Bookmarks & Quick Access",
            bookmarks_content,
            VisualDesignConstants.WARNING_COLOR,
            True
        )

        # Templates section
        templates_content = self._create_templates_section()
        container.add_section(
            "📝 Path Templates",
            templates_content,
            "#9c27b0",
            False
        )

        # History section
        history_content = self._create_history_section()
        container.add_section(
            "📚 Selection History",
            history_content,
            "#607d8b",
            False
        )

        # Add container to scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        advanced_layout.addWidget(scroll_area)

        self.tab_widget.addTab(advanced_tab, "🚀 Advanced")

    def _create_help_tab(self):
        """Create the help and documentation tab."""
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        help_layout.setContentsMargins(16, 16, 16, 16)
        help_layout.setSpacing(16)

        # Help content
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>🎯 JSON Path Selector Help</h2>

        <h3>📋 Getting Started</h3>
        <ol>
            <li><strong>Select a Step:</strong> Choose a workflow step from the dropdown at the top</li>
            <li><strong>Search:</strong> Use the search box to filter JSON paths</li>
            <li><strong>Browse:</strong> Explore the JSON structure in the tree view</li>
            <li><strong>Select:</strong> Click on any path to select it</li>
        </ol>

        <h3>🔍 Search Tips</h3>
        <ul>
            <li>Type partial field names to find matching paths</li>
            <li>Use wildcards (*) for flexible matching</li>
            <li>Search is case-insensitive</li>
        </ul>

        <h3>📌 Bookmarks</h3>
        <ul>
            <li>Save frequently used paths for quick access</li>
            <li>Organize bookmarks by category</li>
            <li>Access bookmarks from the Advanced tab</li>
        </ul>

        <h3>🚀 Advanced Features</h3>
        <ul>
            <li><strong>Templates:</strong> Pre-defined path patterns</li>
            <li><strong>History:</strong> Recently selected paths</li>
            <li><strong>Smart Suggestions:</strong> AI-powered path recommendations</li>
        </ul>
        """)
        help_text.setStyleSheet(f"""
            QTextEdit {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                background-color: white;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 6px;
                padding: 16px;
            }}
        """)

        help_layout.addWidget(help_text)

        self.tab_widget.addTab(help_tab, "❓ Help")

    def _create_search_section(self):
        """Create the search section content."""
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        # Search input
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        search_label = QLabel("🔍")
        search_label.setStyleSheet(f"font-size: {VisualDesignConstants.HEADER_FONT_SIZE};")
        search_row.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search JSON paths...")
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                padding: 8px 12px;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        search_row.addWidget(self.search_edit)

        # Clear button
        clear_btn = QPushButton("✖")
        clear_btn.setFixedSize(32, 32)
        clear_btn.clicked.connect(self.search_edit.clear)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.ERROR_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        """)
        search_row.addWidget(clear_btn)

        search_layout.addLayout(search_row)

        return search_widget

    def _create_json_explorer(self):
        """Create the JSON explorer section content."""
        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout(explorer_widget)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_layout.setSpacing(8)

        # JSON tree
        self.json_tree = JsonTreeWidget()
        self.json_tree.setStyleSheet(f"""
            QTreeWidget {{
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                background-color: white;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                selection-background-color: {VisualDesignConstants.ACCENT_COLOR};
                selection-color: white;
                min-height: 300px;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {VisualDesignConstants.LIGHT_BACKGROUND};
            }}
            QTreeWidget::item:hover {{
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
            }}
        """)
        explorer_layout.addWidget(self.json_tree)

        return explorer_widget

    def _create_path_preview(self):
        """Create the path preview section content."""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)

        # Selected path display
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText("No path selected")
        self.path_display.setStyleSheet(f"""
            QLineEdit {{
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                padding: 8px 12px;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
            }}
        """)
        preview_layout.addWidget(self.path_display)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        # Copy button
        copy_btn = QPushButton("📋 Copy Path")
        copy_btn.clicked.connect(self._copy_selected_path)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #388e3c;
            }}
        """)
        button_row.addWidget(copy_btn)

        # Bookmark button
        bookmark_btn = QPushButton("⭐ Bookmark")
        bookmark_btn.clicked.connect(self._bookmark_selected_path)
        bookmark_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.WARNING_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #f57c00;
            }}
        """)
        button_row.addWidget(bookmark_btn)

        button_row.addStretch()
        preview_layout.addLayout(button_row)

        return preview_widget

    def _create_bookmarks_section(self):
        """Create the bookmarks section content."""
        bookmarks_widget = QWidget()
        bookmarks_layout = QVBoxLayout(bookmarks_widget)
        bookmarks_layout.setContentsMargins(0, 0, 0, 0)
        bookmarks_layout.setSpacing(8)

        # Bookmarks list
        self.bookmarks_list = QTreeWidget()
        self.bookmarks_list.setHeaderLabels(["Path", "Category", "Usage"])
        self.bookmarks_list.setStyleSheet(f"""
            QTreeWidget {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                background-color: white;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                min-height: 200px;
            }}
        """)
        bookmarks_layout.addWidget(self.bookmarks_list)

        # Bookmark management buttons
        bookmark_buttons = QHBoxLayout()
        bookmark_buttons.setSpacing(8)

        add_bookmark_btn = QPushButton("➕ Add")
        add_bookmark_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: {VisualDesignConstants.SMALL_FONT_SIZE};
            }}
        """)
        bookmark_buttons.addWidget(add_bookmark_btn)

        remove_bookmark_btn = QPushButton("🗑️ Remove")
        remove_bookmark_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.ERROR_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: {VisualDesignConstants.SMALL_FONT_SIZE};
            }}
        """)
        bookmark_buttons.addWidget(remove_bookmark_btn)

        bookmark_buttons.addStretch()
        bookmarks_layout.addLayout(bookmark_buttons)

        return bookmarks_widget

    def _create_templates_section(self):
        """Create the templates section content."""
        templates_widget = QWidget()
        templates_layout = QVBoxLayout(templates_widget)
        templates_layout.setContentsMargins(0, 0, 0, 0)
        templates_layout.setSpacing(8)

        # Templates info
        info_label = QLabel("📝 Common path patterns and templates")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-style: italic;
                font-size: {VisualDesignConstants.SMALL_FONT_SIZE};
            }}
        """)
        templates_layout.addWidget(info_label)

        # Template buttons
        template_buttons = QVBoxLayout()
        template_buttons.setSpacing(4)

        templates = [
            ("User Info", "data.user_data.personal_info"),
            ("Email Address", "data.user_data.email"),
            ("Department", "data.user_data.department"),
            ("Manager Info", "data.user_data.manager"),
            ("Permissions", "data.user_data.permissions[0]"),
        ]

        for name, path in templates:
            btn = QPushButton(f"{name}: {path}")
            btn.clicked.connect(lambda checked, p=path: self._select_template_path(p))
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 8px 12px;
                    border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
                    border-radius: 4px;
                    background-color: white;
                    font-size: {VisualDesignConstants.SMALL_FONT_SIZE};
                }}
                QPushButton:hover {{
                    background-color: {VisualDesignConstants.HOVER_BACKGROUND};
                    border-color: {VisualDesignConstants.ACCENT_COLOR};
                }}
            """)
            template_buttons.addWidget(btn)

        templates_layout.addLayout(template_buttons)

        return templates_widget

    def _create_history_section(self):
        """Create the history section content."""
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(8)

        # History list
        self.history_list = QTreeWidget()
        self.history_list.setHeaderLabels(["Recent Paths", "Time"])
        self.history_list.setStyleSheet(f"""
            QTreeWidget {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                background-color: white;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 4px;
                min-height: 150px;
            }}
        """)
        history_layout.addWidget(self.history_list)

        # Clear history button
        clear_history_btn = QPushButton("🗑️ Clear History")
        clear_history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.ERROR_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: {VisualDesignConstants.SMALL_FONT_SIZE};
            }}
        """)
        history_layout.addWidget(clear_history_btn)

        return history_widget

    def _connect_signals(self):
        """Connect widget signals."""
        # Step selection
        self.step_combo.currentIndexChanged.connect(self._on_step_changed)

        # Search
        self.search_edit.textChanged.connect(self._on_search_changed)

        # JSON tree selection - connect to the proper path_selected signal
        self.json_tree.path_selected.connect(self._on_path_selected_from_tree)
        # Also keep the item click for additional handling
        self.json_tree.itemClicked.connect(self._on_tree_item_clicked)

    def _on_step_changed(self, index):
        """Handle step selection change."""
        logger.debug(f"_on_step_changed called with index: {index}")

        if not self.workflow:
            logger.debug("No workflow available for step change")
            return

        if 0 <= index < len(self.workflow.steps):
            logger.debug(f"Setting current step index to: {index}")
            self.current_step_index = index
            self._update_json_tree()
            self.step_changed.emit(index)
        else:
            logger.debug(f"Invalid step index: {index} for workflow with {len(self.workflow.steps)} steps")
            # Clear the tree for invalid selections
            self.json_tree.populate_from_json({}, "data")
            self.step_status.setText("Invalid step selection")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.ERROR_COLOR};")

    def _on_search_changed(self, text):
        """Handle search text change."""
        # Filter JSON tree based on search text
        if hasattr(self.json_tree, 'filter_items'):
            self.json_tree.filter_items(text)

    def _on_tree_item_clicked(self, item, column):
        """Handle JSON tree item click - for additional processing."""
        _ = column  # Unused parameter
        # The actual path selection is handled by _on_path_selected_from_tree
        # This method can be used for additional click handling if needed
        logger.debug(f"Tree item clicked: {item.text(0) if item else 'None'}")

    def _on_path_selected_from_tree(self, path):
        """Handle path selection from the JSON tree."""
        logger.debug(f"Path selected from tree: {path}")
        self.selected_path = path
        self.path_display.setText(self.selected_path)
        self.path_selected.emit(self.selected_path)

    def _copy_selected_path(self):
        """Copy the selected path to clipboard."""
        if self.selected_path:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.selected_path)

    def _bookmark_selected_path(self):
        """Bookmark the selected path."""
        if self.selected_path:
            self.bookmark_manager.add_bookmark(self.selected_path, "User Added")

    def _select_template_path(self, path):
        """Select a template path."""
        self.selected_path = path
        self.path_display.setText(path)
        self.path_selected.emit(path)

    def _update_json_tree(self):
        """Update the JSON tree with current step data."""
        logger.debug(f"_update_json_tree called for step index: {self.current_step_index}")

        if not self.workflow:
            logger.debug("No workflow available")
            self.json_tree.populate_from_json({}, "data")
            self.step_status.setText("No workflow loaded")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.WARNING_COLOR};")
            return

        if self.current_step_index >= len(self.workflow.steps):
            logger.debug(f"Step index {self.current_step_index} out of range for {len(self.workflow.steps)} steps")
            self.json_tree.populate_from_json({}, "data")
            self.step_status.setText("Invalid step selection")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.ERROR_COLOR};")
            return

        step = self.workflow.steps[self.current_step_index]
        step_name = getattr(step, 'description', f'Step {self.current_step_index + 1}')

        if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
            logger.debug(f"Found parsed JSON output for step: {step_name}")
            output_key = getattr(step, 'output_key', f'step_{self.current_step_index}')
            data = {output_key: step.parsed_json_output}
            self.json_tree.populate_from_json(data, "data")

            # Update status with success message
            item_count = len(step.parsed_json_output) if isinstance(step.parsed_json_output, (dict, list)) else 1
            self.step_status.setText(f"✅ Loaded {step_name} ({item_count} items)")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.SUCCESS_COLOR};")
        else:
            logger.debug(f"No parsed JSON output for step: {step_name}")
            self.json_tree.populate_from_json({}, "data")
            self.step_status.setText(f"⚠️ {step_name} has no JSON output")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.WARNING_COLOR};")

    def set_workflow(self, workflow, current_step_index=0):
        """Set the workflow and update the UI."""
        self.workflow = workflow
        self.current_step_index = current_step_index

        # Update step combo
        self.step_combo.clear()
        if workflow:
            for i, step in enumerate(workflow.steps):
                has_json = hasattr(step, 'parsed_json_output') and step.parsed_json_output
                status = "✅" if has_json else "❌"
                step_name = getattr(step, 'description', f'Step {i+1}')
                output_key = getattr(step, 'output_key', 'unknown')
                self.step_combo.addItem(f"{status} {step_name} ({output_key})")

            self.step_status.setText(f"Loaded {len(workflow.steps)} steps")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.SUCCESS_COLOR};")

            # Set current step
            if 0 <= current_step_index < len(workflow.steps):
                self.step_combo.setCurrentIndex(current_step_index)
        else:
            self.step_status.setText("No workflow loaded")
            self.step_status.setStyleSheet(f"color: {VisualDesignConstants.WARNING_COLOR};")

        self._update_json_tree()

    def get_selected_path(self):
        """Get the currently selected path."""
        return self.selected_path
