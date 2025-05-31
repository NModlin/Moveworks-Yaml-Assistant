"""
Bender Function Builder Widget for the Moveworks YAML Assistant.

This module provides UI components for building Bender function expressions
with guided input and validation.

Supported Bender Functions:
- MAP(): Transform array items
- FILTER(): Filter array items by condition  
- CONDITIONAL(): IF...THEN...ELSE logic
- LOOKUP(): Lookup value in mapping object
- CONCAT(): Concatenate strings
"""

import json
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QTabWidget,
    QScrollArea, QFrame, QSplitter, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette

from dsl_validator import dsl_validator, DSLValidationResult


class BenderFunctionBuilder(QWidget):
    """Widget for building Bender function expressions with guided input."""
    
    function_built = Signal(str)  # Emitted when a function is built
    
    def __init__(self):
        super().__init__()
        self.current_function = None
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_current_expression)
        
        self._setup_ui()
        self._setup_styling()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_label = QLabel("Bender Function Builder")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; margin-bottom: 8px;")
        layout.addWidget(header_label)
        
        # Function selector
        selector_group = QGroupBox("Select Function Type")
        selector_layout = QVBoxLayout(selector_group)
        
        self.function_combo = QComboBox()
        self.function_combo.addItems([
            "Select a function...",
            "MAP - Transform array items",
            "FILTER - Filter array items by condition", 
            "CONDITIONAL - IF...THEN...ELSE logic",
            "LOOKUP - Lookup value in mapping object",
            "CONCAT - Concatenate strings"
        ])
        self.function_combo.currentTextChanged.connect(self._on_function_selected)
        selector_layout.addWidget(self.function_combo)
        
        layout.addWidget(selector_group)
        
        # Function configuration area
        self.config_area = QTabWidget()
        self.config_area.setVisible(False)
        layout.addWidget(self.config_area)
        
        # Preview and validation area
        preview_group = QGroupBox("Generated Expression")
        preview_layout = QVBoxLayout(preview_group)
        
        self.expression_preview = QTextEdit()
        self.expression_preview.setMaximumHeight(80)
        self.expression_preview.setReadOnly(True)
        self.expression_preview.setPlaceholderText("Generated Bender expression will appear here...")
        preview_layout.addWidget(self.expression_preview)
        
        # Validation status
        self.validation_status = QLabel("Select a function to begin")
        self.validation_status.setStyleSheet("color: #666; font-style: italic;")
        preview_layout.addWidget(self.validation_status)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.use_expression_btn = QPushButton("Use This Expression")
        self.use_expression_btn.clicked.connect(self._use_expression)
        self.use_expression_btn.setEnabled(False)
        self.use_expression_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_form)
        
        button_layout.addWidget(self.use_expression_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        preview_layout.addLayout(button_layout)
        layout.addWidget(preview_group)
    
    def _setup_styling(self):
        """Apply consistent styling."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #333;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2196f3;
            }
        """)
    
    def _on_function_selected(self, text: str):
        """Handle function selection."""
        if text.startswith("Select"):
            self.config_area.setVisible(False)
            self.current_function = None
            return
        
        function_name = text.split(" - ")[0]
        self.current_function = function_name
        self.config_area.setVisible(True)
        
        # Clear existing tabs
        self.config_area.clear()
        
        # Create configuration widget for selected function
        if function_name == "MAP":
            self._create_map_config()
        elif function_name == "FILTER":
            self._create_filter_config()
        elif function_name == "CONDITIONAL":
            self._create_conditional_config()
        elif function_name == "LOOKUP":
            self._create_lookup_config()
        elif function_name == "CONCAT":
            self._create_concat_config()
        
        self._update_preview()
    
    def _create_map_config(self):
        """Create configuration widget for MAP function."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Items parameter (JSON path to array)
        self.map_items = QLineEdit()
        self.map_items.setPlaceholderText("data.users")
        self.map_items.textChanged.connect(self._on_config_changed)
        layout.addRow("Items (array path):", self.map_items)
        
        # Converter parameter (transformation expression)
        self.map_converter = QTextEdit()
        self.map_converter.setMaximumHeight(60)
        self.map_converter.setPlaceholderText('{"id": "item.id", "name": "item.name"}')
        self.map_converter.textChanged.connect(self._on_config_changed)
        layout.addRow("Converter (transform):", self.map_converter)
        
        # Optional context parameter
        self.map_context = QLineEdit()
        self.map_context.setPlaceholderText("Optional context (leave empty if not needed)")
        self.map_context.textChanged.connect(self._on_config_changed)
        layout.addRow("Context (optional):", self.map_context)
        
        self.config_area.addTab(widget, "MAP Configuration")
    
    def _create_filter_config(self):
        """Create configuration widget for FILTER function."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Items parameter (JSON path to array)
        self.filter_items = QLineEdit()
        self.filter_items.setPlaceholderText("data.users")
        self.filter_items.textChanged.connect(self._on_config_changed)
        layout.addRow("Items (array path):", self.filter_items)
        
        # Condition parameter (boolean expression)
        self.filter_condition = QLineEdit()
        self.filter_condition.setPlaceholderText("item.status == 'active'")
        self.filter_condition.textChanged.connect(self._on_config_changed)
        layout.addRow("Condition:", self.filter_condition)
        
        self.config_area.addTab(widget, "FILTER Configuration")
    
    def _create_conditional_config(self):
        """Create configuration widget for CONDITIONAL function."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Condition parameter
        self.conditional_condition = QLineEdit()
        self.conditional_condition.setPlaceholderText("data.age >= 18")
        self.conditional_condition.textChanged.connect(self._on_config_changed)
        layout.addRow("Condition:", self.conditional_condition)
        
        # On pass parameter
        self.conditional_on_pass = QLineEdit()
        self.conditional_on_pass.setPlaceholderText("'Adult'")
        self.conditional_on_pass.textChanged.connect(self._on_config_changed)
        layout.addRow("If true (on_pass):", self.conditional_on_pass)
        
        # On fail parameter
        self.conditional_on_fail = QLineEdit()
        self.conditional_on_fail.setPlaceholderText("'Minor'")
        self.conditional_on_fail.textChanged.connect(self._on_config_changed)
        layout.addRow("If false (on_fail):", self.conditional_on_fail)
        
        self.config_area.addTab(widget, "CONDITIONAL Configuration")
    
    def _create_lookup_config(self):
        """Create configuration widget for LOOKUP function."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Mapping parameter (JSON path to object)
        self.lookup_mapping = QLineEdit()
        self.lookup_mapping.setPlaceholderText("data.user_roles")
        self.lookup_mapping.textChanged.connect(self._on_config_changed)
        layout.addRow("Mapping (object path):", self.lookup_mapping)
        
        # Key parameter
        self.lookup_key = QLineEdit()
        self.lookup_key.setPlaceholderText("data.user_id")
        self.lookup_key.textChanged.connect(self._on_config_changed)
        layout.addRow("Key:", self.lookup_key)
        
        # Optional default parameter
        self.lookup_default = QLineEdit()
        self.lookup_default.setPlaceholderText("'default_role'")
        self.lookup_default.textChanged.connect(self._on_config_changed)
        layout.addRow("Default (optional):", self.lookup_default)
        
        self.config_area.addTab(widget, "LOOKUP Configuration")
    
    def _create_concat_config(self):
        """Create configuration widget for CONCAT function."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Strings parameter (array of strings)
        self.concat_strings = QTextEdit()
        self.concat_strings.setMaximumHeight(60)
        self.concat_strings.setPlaceholderText('[data.first_name, " ", data.last_name]')
        self.concat_strings.textChanged.connect(self._on_config_changed)
        layout.addRow("Strings (array):", self.concat_strings)
        
        # Optional separator parameter
        self.concat_separator = QLineEdit()
        self.concat_separator.setPlaceholderText("Optional separator (leave empty for default)")
        self.concat_separator.textChanged.connect(self._on_config_changed)
        layout.addRow("Separator (optional):", self.concat_separator)
        
        self.config_area.addTab(widget, "CONCAT Configuration")
    
    def _on_config_changed(self):
        """Handle configuration changes."""
        # Debounce validation
        self.validation_timer.start(300)
        self._update_preview()
    
    def _update_preview(self):
        """Update the expression preview."""
        if not self.current_function:
            self.expression_preview.clear()
            return
        
        expression = self._build_expression()
        self.expression_preview.setPlainText(expression)
        
        # Enable/disable use button based on expression validity
        self.use_expression_btn.setEnabled(bool(expression.strip()))
    
    def _build_expression(self) -> str:
        """Build the Bender expression from current configuration."""
        if not self.current_function:
            return ""
        
        try:
            if self.current_function == "MAP":
                items = self.map_items.text().strip()
                converter = self.map_converter.toPlainText().strip()
                context = self.map_context.text().strip()
                
                if not items or not converter:
                    return ""
                
                if context:
                    return f"$MAP({items}, {converter}, {context})"
                else:
                    return f"$MAP({items}, {converter})"
            
            elif self.current_function == "FILTER":
                items = self.filter_items.text().strip()
                condition = self.filter_condition.text().strip()
                
                if not items or not condition:
                    return ""
                
                return f"$FILTER({items}, {condition})"
            
            elif self.current_function == "CONDITIONAL":
                condition = self.conditional_condition.text().strip()
                on_pass = self.conditional_on_pass.text().strip()
                on_fail = self.conditional_on_fail.text().strip()
                
                if not condition or not on_pass or not on_fail:
                    return ""
                
                return f"$CONDITIONAL({condition}, {on_pass}, {on_fail})"
            
            elif self.current_function == "LOOKUP":
                mapping = self.lookup_mapping.text().strip()
                key = self.lookup_key.text().strip()
                default = self.lookup_default.text().strip()
                
                if not mapping or not key:
                    return ""
                
                if default:
                    return f"$LOOKUP({mapping}, {key}, {default})"
                else:
                    return f"$LOOKUP({mapping}, {key})"
            
            elif self.current_function == "CONCAT":
                strings = self.concat_strings.toPlainText().strip()
                separator = self.concat_separator.text().strip()
                
                if not strings:
                    return ""
                
                if separator:
                    return f"$CONCAT({strings}, {separator})"
                else:
                    return f"$CONCAT({strings})"
        
        except Exception:
            return ""
        
        return ""
    
    def _validate_current_expression(self):
        """Validate the current expression."""
        expression = self._build_expression()
        
        if not expression:
            self.validation_status.setText("Complete the required fields to generate expression")
            self.validation_status.setStyleSheet("color: #666; font-style: italic;")
            return
        
        # Validate using DSL validator
        result = dsl_validator.validate_expression(expression)
        
        if result.is_valid:
            self.validation_status.setText("✓ Expression is valid")
            self.validation_status.setStyleSheet("color: #4caf50; font-weight: bold;")
        else:
            error_msg = "; ".join(result.errors[:2])  # Show first 2 errors
            self.validation_status.setText(f"⚠ Issues: {error_msg}")
            self.validation_status.setStyleSheet("color: #f44336;")
    
    def _use_expression(self):
        """Emit the built expression."""
        expression = self._build_expression()
        if expression:
            self.function_built.emit(expression)
    
    def _clear_form(self):
        """Clear the form."""
        self.function_combo.setCurrentIndex(0)
        self.config_area.setVisible(False)
        self.expression_preview.clear()
        self.validation_status.setText("Select a function to begin")
        self.validation_status.setStyleSheet("color: #666; font-style: italic;")
        self.use_expression_btn.setEnabled(False)
