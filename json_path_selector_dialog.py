#!/usr/bin/env python3
"""
Standalone JSON Path Selector Dialog for the Moveworks YAML Assistant.

This provides a large, easily visible dialog for JSON path selection with
enhanced visual design and user flow improvements.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter, QGroupBox,
    QComboBox, QListWidget, QApplication, QDialogButtonBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Import our enhanced components
from enhanced_json_selector import VisualDesignConstants, JsonTreeWidget, JsonPathPreviewWidget

logger = logging.getLogger(__name__)


class JsonPathSelectorDialog(QDialog):
    """
    Large, standalone dialog for JSON path selection with enhanced visibility.

    Features:
    - Large, easily readable interface
    - Clear visual hierarchy and spacing
    - Enhanced user feedback and status indicators
    - Auto-population from workflow steps
    - Real-time search and filtering
    - One-click path selection and copying
    """

    path_selected = Signal(str)  # Emitted when a path is selected

    def __init__(self, parent=None, workflow=None):
        super().__init__(parent)
        self.workflow = workflow
        self.selected_path = ""

        self.setWindowTitle("JSON Path Selector - Large View (No More Clutter!)")
        self.setModal(True)

        # Make it MUCH larger to solve the clutter problem
        self.setMinimumSize(1600, 1000)
        self.resize(1800, 1200)

        # Center on screen for better visibility
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - 1800) // 2
            y = parent_geo.y() + (parent_geo.height() - 1200) // 2
            self.move(max(0, x), max(0, y))

        # Set window flags for better visibility
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        self._setup_ui()
        self._setup_connections()

        if workflow:
            self.set_workflow(workflow)

    def _setup_ui(self):
        """Setup the dialog UI with enhanced visual design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(VisualDesignConstants.UNIFORM_MARGIN * 2,
                                 VisualDesignConstants.UNIFORM_MARGIN * 2,
                                 VisualDesignConstants.UNIFORM_MARGIN * 2,
                                 VisualDesignConstants.UNIFORM_MARGIN * 2)
        layout.setSpacing(VisualDesignConstants.SECTION_SPACING)

        # Apply comprehensive dialog styling with high contrast
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #ffffff;
                color: #2c3e50;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 13px;
                font-weight: 500;
            }}
            QLabel {{
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
            }}
            QGroupBox {{
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #2c3e50;
                background-color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
            }}
            QPushButton {{
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
                min-height: 25px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #21618c;
            }}
            QTextEdit, QLineEdit {{
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }}
            QTreeWidget {{
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }}
            QTreeWidget::item {{
                color: #2c3e50;
                padding: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: #3498db;
                color: #ffffff;
            }}
        """)

        # Large, prominent header - much bigger for visibility
        header_label = QLabel("🎯 JSON Path Selector - Large View")
        header_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: none;
                border-radius: 12px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 4}px;
                margin-bottom: {VisualDesignConstants.SECTION_SPACING * 2}px;
                text-align: center;
            }}
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Clear, prominent instructions
        instructions = QLabel(
            "📋 INSTRUCTIONS:\n"
            "1. Select a workflow step from the dropdown below\n"
            "2. Browse the JSON structure in the tree view\n"
            "3. Click on any path to select it\n"
            "4. Use the search box to filter paths\n"
            "5. Click OK to use the selected path"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: #333;
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                background-color: #e8f5e8;
                border: 2px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 8px;
                margin-bottom: {VisualDesignConstants.SECTION_SPACING * 2}px;
            }}
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Step selection with much larger, more visible controls
        step_group = QGroupBox("📋 STEP SELECTION")
        step_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: 3px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 10px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 4}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                border-radius: 6px;
            }}
        """)
        step_layout = QHBoxLayout(step_group)
        step_layout.setSpacing(VisualDesignConstants.FORM_SPACING * 3)
        step_layout.setContentsMargins(20, 20, 20, 20)

        step_label = QLabel("Choose Workflow Step:")
        step_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: white;
                min-width: 200px;
            }}
        """)
        step_layout.addWidget(step_label)

        self.step_combo = QComboBox()
        self.step_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                border: 3px solid white;
                border-radius: 8px;
                background-color: white;
                font-size: 16px;
                min-height: 50px;
                font-weight: bold;
            }}
            QComboBox:hover {{
                border-color: {VisualDesignConstants.SUCCESS_COLOR};
                background-color: #f8f8f8;
            }}
            QComboBox:focus {{
                border-color: {VisualDesignConstants.SUCCESS_COLOR};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                width: 12px;
                height: 12px;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
            }}
        """)
        step_layout.addWidget(self.step_combo, 1)

        layout.addWidget(step_group)

        # Search section with much larger, more visible controls
        search_group = QGroupBox("🔍 SEARCH & FILTER")
        search_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                border: 3px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 10px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 4}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                border-radius: 6px;
            }}
        """)
        search_layout = QHBoxLayout(search_group)
        search_layout.setSpacing(VisualDesignConstants.FORM_SPACING * 3)
        search_layout.setContentsMargins(20, 20, 20, 20)

        search_label = QLabel("Search JSON Paths:")
        search_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: white;
                min-width: 200px;
            }}
        """)
        search_layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to search paths, keys, or values...")
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: 16px;
                background-color: white;
                border: 3px solid white;
                border-radius: 8px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                min-height: 50px;
                font-weight: bold;
            }}
            QLineEdit:focus {{
                border-color: {VisualDesignConstants.WARNING_COLOR};
                outline: none;
            }}
            QLineEdit:hover {{
                background-color: #f8f8f8;
            }}
        """)
        search_layout.addWidget(self.search_edit, 1)

        layout.addWidget(search_group)

        # Main content area - MUCH larger and less cluttered
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                width: 8px;
                border-radius: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
            }}
        """)

        # JSON tree with much larger, cleaner styling
        tree_group = QGroupBox("🌳 JSON STRUCTURE EXPLORER")
        tree_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: 3px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 10px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 4}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                border-radius: 6px;
            }}
        """)
        tree_layout = QVBoxLayout(tree_group)
        tree_layout.setContentsMargins(20, 20, 20, 20)
        tree_layout.setSpacing(15)

        # Large, prominent status indicator
        self.status_label = QLabel("📋 Select a workflow step above to explore JSON data")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                margin-bottom: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
            }}
        """)
        tree_layout.addWidget(self.status_label)

        # Much larger, enhanced JSON tree
        self.json_tree = JsonTreeWidget()
        self.json_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: white;
                border: 3px solid white;
                border-radius: 8px;
                font-size: 16px;
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                selection-background-color: {VisualDesignConstants.ACCENT_COLOR};
                selection-color: white;
                min-height: 500px;
                font-weight: bold;
            }}
            QTreeWidget::item {{
                padding: 12px;
                border-bottom: 2px solid #f0f0f0;
                min-height: 30px;
            }}
            QTreeWidget::item:hover {{
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
                border-left: 4px solid {VisualDesignConstants.ACCENT_COLOR};
            }}
            QTreeWidget::item:selected {{
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                color: white;
                font-weight: bold;
                border-left: 4px solid {VisualDesignConstants.SUCCESS_COLOR};
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: none;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                width: 12px;
                height: 12px;
                border-radius: 6px;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: none;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                width: 12px;
                height: 12px;
                border-radius: 6px;
            }}
        """)
        tree_layout.addWidget(self.json_tree)

        content_splitter.addWidget(tree_group)

        # Preview panel with much larger, enhanced styling
        preview_group = QGroupBox("📋 SELECTED PATH PREVIEW")
        preview_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                border: 3px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 10px;
                margin-top: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                padding-top: {VisualDesignConstants.UNIFORM_MARGIN * 4}px;
                padding-left: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-right: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                padding-bottom: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                top: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
                color: white;
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 2}px {VisualDesignConstants.UNIFORM_MARGIN * 3}px;
                border-radius: 6px;
            }}
        """)
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(15)

        self.preview_widget = JsonPathPreviewWidget()
        preview_layout.addWidget(self.preview_widget)

        content_splitter.addWidget(preview_group)
        content_splitter.setSizes([1000, 600])  # Much larger proportions

        layout.addWidget(content_splitter)

        # Much larger dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet(f"""
            QDialogButtonBox {{
                margin-top: {VisualDesignConstants.SECTION_SPACING * 2}px;
            }}
            QPushButton {{
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: {VisualDesignConstants.UNIFORM_MARGIN * 4}px {VisualDesignConstants.UNIFORM_MARGIN * 6}px;
                font-size: 18px;
                font-weight: bold;
                min-width: 150px;
                min-height: 60px;
                margin: {VisualDesignConstants.UNIFORM_MARGIN * 2}px;
            }}
            QPushButton:hover {{
                background-color: #1976d2;
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: #0d47a1;
                transform: translateY(0px);
            }}
            QPushButton[text="Cancel"] {{
                background-color: {VisualDesignConstants.ERROR_COLOR};
            }}
            QPushButton[text="Cancel"]:hover {{
                background-color: #d32f2f;
            }}
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def _setup_connections(self):
        """Setup signal connections."""
        self.step_combo.currentIndexChanged.connect(self._on_step_changed)
        self.search_edit.textChanged.connect(self._on_search_changed)
        self.json_tree.path_selected.connect(self._on_path_selected)

    def set_workflow(self, workflow):
        """Set the workflow and populate step combo."""
        self.workflow = workflow
        self.step_combo.clear()

        if not workflow:
            return

        # Add initial inputs option
        self.step_combo.addItem("Initial Inputs", -1)

        # Add workflow steps
        for i, step in enumerate(workflow.steps):
            step_name = f"Step {i+1}: {getattr(step, 'name', 'Unnamed')}"
            self.step_combo.addItem(step_name, i)

    def _on_step_changed(self, index):
        """Handle step selection change."""
        if index < 0:
            return

        step_index = self.step_combo.itemData(index)

        if step_index == -1:
            # Initial inputs
            self.status_label.setText("📥 Loading initial inputs...")
            initial_data = {}
            if self.workflow and hasattr(self.workflow, 'initial_inputs'):
                initial_data = self.workflow.initial_inputs or {}

            self.json_tree.populate_from_json(initial_data, "data")
            self.status_label.setText(f"✅ Loaded initial inputs ({len(initial_data)} items)")
        else:
            # Step output
            if not self.workflow or step_index >= len(self.workflow.steps):
                self.status_label.setText("❌ Invalid step selection")
                return

            step = self.workflow.steps[step_index]
            step_name = f"Step {step_index + 1}"
            self.status_label.setText(f"📥 Loading {step_name} data...")

            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                output_key = getattr(step, 'output_key', 'unknown')
                data = {output_key: step.parsed_json_output}
                self.json_tree.populate_from_json(data, "data")

                total_items = len(step.parsed_json_output) if isinstance(step.parsed_json_output, (dict, list)) else 1
                self.status_label.setText(f"✅ Loaded {step_name} data ({total_items} items)")
            else:
                self.json_tree.populate_from_json({}, "data")
                self.status_label.setText(f"⚠️ {step_name} has no JSON output")

    def _on_search_changed(self, query):
        """Handle search query change."""
        if not query.strip():
            self.status_label.setText("Ready - Select a step to explore JSON data")
            return

        self.status_label.setText(f"🔍 Searching for '{query}'...")
        # TODO: Implement search functionality

    def _on_path_selected(self, path):
        """Handle path selection."""
        self.selected_path = path
        self.preview_widget.update_preview(path, self.json_tree.current_data)
        self.path_selected.emit(path)

        # Update status
        self.status_label.setText(f"✅ Selected: {path}")

    def get_selected_path(self):
        """Get the currently selected path."""
        return self.selected_path


def main():
    """Test the dialog."""
    app = QApplication(sys.argv)

    dialog = JsonPathSelectorDialog()
    dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
