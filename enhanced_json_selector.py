"""
Enhanced JSON Path Selector for the Moveworks YAML Assistant.

This module provides an improved JSON path selection widget with tree visualization,
search functionality, and preview capabilities.
"""

import json
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter, QGroupBox,
    QComboBox, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon


class JsonTreeWidget(QTreeWidget):
    """Enhanced tree widget for JSON structure visualization."""
    
    path_selected = Signal(str)  # Emits the selected JSON path
    
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Key", "Type", "Value"])
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self._on_item_clicked)
        
        # Enable multi-selection for complex paths
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        
        # Store path information in items
        self.path_map = {}  # item -> full_path
    
    def populate_from_json(self, data: Dict[str, Any], root_path: str = "data"):
        """Populate tree from JSON data."""
        self.clear()
        self.path_map.clear()
        
        if not data:
            return
        
        # Create root item
        root_item = QTreeWidgetItem([root_path, "object", ""])
        self.addTopLevelItem(root_item)
        self.path_map[root_item] = root_path
        
        # Recursively add items
        self._add_json_items(root_item, data, root_path)
        
        # Expand first level
        root_item.setExpanded(True)
    
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
        """Handle item click."""
        if item in self.path_map:
            path = self.path_map[item]
            self.path_selected.emit(path)
    
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
        """Setup the preview UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Path Preview")
        header_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header_label)
        
        # Current path display
        self.path_label = QLabel("No path selected")
        self.path_label.setStyleSheet("color: #666; font-family: monospace;")
        layout.addWidget(self.path_label)
        
        # Value preview
        self.value_text = QTextEdit()
        self.value_text.setReadOnly(True)
        self.value_text.setMaximumHeight(150)
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.Monospace)
        self.value_text.setFont(font)
        layout.addWidget(self.value_text)
        
        # Copy button
        copy_btn = QPushButton("Copy Path")
        copy_btn.clicked.connect(self._copy_path)
        layout.addWidget(copy_btn)
    
    def set_path_and_data(self, path: str, data: Dict[str, Any]):
        """Set the current path and data for preview."""
        self.current_path = path
        self.current_data = data
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview display."""
        if not self.current_path:
            self.path_label.setText("No path selected")
            self.value_text.clear()
            return
        
        self.path_label.setText(self.current_path)
        
        # Extract value from data using path
        try:
            value = self._extract_value_by_path(self.current_data, self.current_path)
            
            if isinstance(value, (dict, list)):
                # Pretty print JSON
                formatted_value = json.dumps(value, indent=2)
            else:
                formatted_value = str(value)
            
            self.value_text.setPlainText(formatted_value)
        except Exception as e:
            self.value_text.setPlainText(f"Error extracting value: {str(e)}")
    
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
        """Copy the current path to clipboard."""
        if self.current_path:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.current_path)


class EnhancedJsonPathSelector(QWidget):
    """Enhanced JSON path selector with tree view, search, and preview."""
    
    path_selected = Signal(str)  # Emits the selected path
    
    def __init__(self):
        super().__init__()
        self.workflow = None
        self.current_step_index = -1
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the enhanced JSON path selector UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Enhanced JSON Path Selector")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header_label)
        
        # Step selection
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Step:"))
        
        self.step_combo = QComboBox()
        self.step_combo.currentIndexChanged.connect(self._on_step_changed)
        step_layout.addWidget(self.step_combo)
        
        layout.addLayout(step_layout)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search paths, keys, or values...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # JSON tree
        tree_group = QGroupBox("JSON Structure")
        tree_layout = QVBoxLayout(tree_group)
        
        self.json_tree = JsonTreeWidget()
        self.json_tree.path_selected.connect(self._on_path_selected)
        tree_layout.addWidget(self.json_tree)
        
        splitter.addWidget(tree_group)
        
        # Preview panel
        self.preview_widget = JsonPathPreviewWidget()
        splitter.addWidget(self.preview_widget)
        
        splitter.setSizes([300, 150])
    
    def set_workflow(self, workflow, current_step_index: int = -1):
        """Set the workflow and update available steps."""
        self.workflow = workflow
        self.current_step_index = current_step_index
        self._update_step_combo()
    
    def _update_step_combo(self):
        """Update the step selection combo box."""
        self.step_combo.clear()
        
        if not self.workflow:
            return
        
        # Add steps that have JSON output
        for i, step in enumerate(self.workflow.steps):
            if i >= self.current_step_index:
                continue  # Don't show current or future steps
            
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                step_name = f"Step {i+1}: {getattr(step, 'output_key', 'unknown')}"
                self.step_combo.addItem(step_name, i)
        
        # Add initial inputs if available
        self.step_combo.addItem("Initial Inputs", -1)
    
    def _on_step_changed(self, index):
        """Handle step selection change."""
        if index < 0:
            return
        
        step_index = self.step_combo.itemData(index)
        
        if step_index == -1:
            # Initial inputs selected
            # You could add initial input data here
            self.json_tree.populate_from_json({}, "data")
        else:
            # Step output selected
            step = self.workflow.steps[step_index]
            if hasattr(step, 'parsed_json_output') and step.parsed_json_output:
                output_key = getattr(step, 'output_key', 'unknown')
                data = {output_key: step.parsed_json_output}
                self.json_tree.populate_from_json(data, "data")
    
    def _on_search_changed(self, query):
        """Handle search query change."""
        if not query.strip():
            return
        
        # Find matching paths
        matching_paths = self.json_tree.search_paths(query)
        
        # Highlight first match
        if matching_paths:
            self.json_tree.highlight_path(matching_paths[0])
    
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
        
        # Emit signal
        self.path_selected.emit(path)
