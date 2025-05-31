"""
DSL Builder Widget for creating Moveworks DSL expressions interactively.

This widget provides a user-friendly interface for building complex DSL expressions
with templates, validation, and real-time preview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QGroupBox, QFormLayout, QListWidget, QListWidgetItem,
    QTabWidget, QScrollArea, QFrame, QSplitter, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from typing import Dict, List, Optional
import re

from dsl_validator import dsl_validator, DSLValidationResult


class DSLSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for DSL expressions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_highlighting_rules()
    
    def _setup_highlighting_rules(self):
        """Set up syntax highlighting rules for DSL."""
        self.highlighting_rules = []
        
        # DSL functions ($CONCAT, $IF, etc.)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#0066cc"))
        function_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\$[A-Z_]+', function_format))
        
        # Data references (data.*, meta_info.*)
        data_format = QTextCharFormat()
        data_format.setForeground(QColor("#cc6600"))
        self.highlighting_rules.append((r'\b(data|meta_info)\.[a-zA-Z_][a-zA-Z0-9_.]*', data_format))
        
        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#cc0066"))
        operator_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'(==|!=|>=|<=|>|<|&&|\|\|)', operator_format))
        
        # String literals
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#009900"))
        self.highlighting_rules.append((r'"[^"]*"', string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#0099cc"))
        self.highlighting_rules.append((r'\b\d+(\.\d+)?\b', number_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format in self.highlighting_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class DSLTemplateWidget(QWidget):
    """Widget for selecting and using DSL templates."""
    
    template_selected = Signal(str)  # Emitted when a template is selected
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_templates()
    
    def _setup_ui(self):
        """Set up the template widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_label = QLabel("DSL Templates")
        header_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        layout.addWidget(header_label)
        
        # Template categories
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All Templates",
            "Data References",
            "String Operations", 
            "Conditional Logic",
            "Comparisons",
            "User Context"
        ])
        self.category_combo.currentTextChanged.connect(self._filter_templates)
        layout.addWidget(self.category_combo)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_clicked)
        layout.addWidget(self.template_list)
        
        # Template preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("background-color: #f8f8f8; font-family: monospace;")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Use template button
        self.use_template_btn = QPushButton("Use Template")
        self.use_template_btn.clicked.connect(self._use_selected_template)
        self.use_template_btn.setEnabled(False)
        layout.addWidget(self.use_template_btn)
    
    def _load_templates(self):
        """Load DSL templates."""
        self.templates = {
            "Data References": [
                ("Simple field access", "data.field_name", "Access a field from step output"),
                ("Nested field access", "data.user_info.email", "Access nested object properties"),
                ("Array element", "data.items[0]", "Access first element of an array"),
                ("User email", "meta_info.user.email", "Current user's email address"),
                ("User name", "meta_info.user.name", "Current user's display name"),
            ],
            "String Operations": [
                ("Concatenate strings", "$CONCAT([data.first_name, ' ', data.last_name])", "Join multiple strings together"),
                ("Split string", "$SPLIT(data.full_name, ' ')[0]", "Split string and get first part"),
                ("Convert to text", "$TEXT(data.user_id)", "Convert number to string"),
                ("Uppercase", "$UPPER(data.name)", "Convert string to uppercase"),
                ("Lowercase", "$LOWER(data.email)", "Convert string to lowercase"),
            ],
            "Conditional Logic": [
                ("Simple condition", "$IF(data.is_active, 'Active', 'Inactive')", "Basic if-then-else logic"),
                ("Null check", "$IF(data.phone != null, data.phone, 'No phone')", "Handle null values safely"),
                ("Complex condition", "$IF(data.age >= 18 && data.status == 'verified', 'Approved', 'Pending')", "Multiple conditions"),
            ],
            "Comparisons": [
                ("Equal to", "data.status == 'active'", "Check if values are equal"),
                ("Not equal", "data.type != 'guest'", "Check if values are different"),
                ("Greater than", "data.age >= 18", "Numeric comparison"),
                ("Contains text", "data.email.contains('@')", "Check if string contains substring"),
                ("Is null", "data.optional_field == null", "Check for null values"),
            ],
            "User Context": [
                ("Current user email", "meta_info.user.email", "Email of the current user"),
                ("Current user ID", "meta_info.user.id", "Unique ID of current user"),
                ("User department", "meta_info.user.department", "User's department"),
                ("User role", "meta_info.user.role", "User's role or title"),
            ]
        }
        
        self._filter_templates()
    
    def _filter_templates(self):
        """Filter templates based on selected category."""
        self.template_list.clear()
        category = self.category_combo.currentText()
        
        if category == "All Templates":
            # Show all templates
            for cat, templates in self.templates.items():
                for name, expression, description in templates:
                    item = QListWidgetItem(f"[{cat}] {name}")
                    item.setData(Qt.UserRole, (expression, description))
                    self.template_list.addItem(item)
        else:
            # Show templates for specific category
            if category in self.templates:
                for name, expression, description in self.templates[category]:
                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, (expression, description))
                    self.template_list.addItem(item)
    
    def _on_template_clicked(self, item):
        """Handle template selection."""
        expression, description = item.data(Qt.UserRole)
        self.preview_text.setPlainText(f"Expression: {expression}\n\nDescription: {description}")
        self.use_template_btn.setEnabled(True)
        self.selected_expression = expression
    
    def _use_selected_template(self):
        """Emit the selected template."""
        if hasattr(self, 'selected_expression'):
            self.template_selected.emit(self.selected_expression)


class DSLBuilderWidget(QWidget):
    """
    Interactive DSL expression builder widget.
    
    Provides templates, validation, and real-time preview for creating DSL expressions.
    """
    
    expression_built = Signal(str)  # Emitted when expression is ready
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the DSL builder UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_label = QLabel("DSL Expression Builder")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(header_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Templates
        self.template_widget = DSLTemplateWidget()
        splitter.addWidget(self.template_widget)
        
        # Right panel: Expression editor and validation
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Expression editor
        editor_group = QGroupBox("DSL Expression")
        editor_layout = QVBoxLayout(editor_group)
        
        self.expression_edit = QTextEdit()
        self.expression_edit.setMaximumHeight(100)
        self.expression_edit.setPlaceholderText("Enter your DSL expression here or select a template...")
        
        # Add syntax highlighting
        self.highlighter = DSLSyntaxHighlighter(self.expression_edit.document())
        
        editor_layout.addWidget(self.expression_edit)
        right_layout.addWidget(editor_group)
        
        # Validation results
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validation_text = QTextEdit()
        self.validation_text.setMaximumHeight(150)
        self.validation_text.setReadOnly(True)
        validation_layout.addWidget(self.validation_text)
        
        right_layout.addWidget(validation_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.validate_btn = QPushButton("Validate Expression")
        self.validate_btn.clicked.connect(self._validate_expression)
        button_layout.addWidget(self.validate_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_expression)
        button_layout.addWidget(self.clear_btn)
        
        self.use_expression_btn = QPushButton("Use Expression")
        self.use_expression_btn.clicked.connect(self._use_expression)
        self.use_expression_btn.setEnabled(False)
        button_layout.addWidget(self.use_expression_btn)
        
        right_layout.addLayout(button_layout)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 400])
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.template_widget.template_selected.connect(self._insert_template)
        self.expression_edit.textChanged.connect(self._on_expression_changed)
    
    def _insert_template(self, template_expression: str):
        """Insert a template into the expression editor."""
        current_text = self.expression_edit.toPlainText()
        if current_text.strip():
            # Ask user if they want to replace or append
            reply = QMessageBox.question(
                self, "Insert Template",
                "Do you want to replace the current expression or append to it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.expression_edit.setPlainText(template_expression)
            elif reply == QMessageBox.StandardButton.No:
                self.expression_edit.setPlainText(current_text + " " + template_expression)
        else:
            self.expression_edit.setPlainText(template_expression)
        
        # Validate the new expression
        self._validate_expression()
    
    def _on_expression_changed(self):
        """Handle expression text changes."""
        # Enable/disable use button based on content
        has_content = bool(self.expression_edit.toPlainText().strip())
        self.use_expression_btn.setEnabled(has_content)
        
        # Auto-validate if there's content
        if has_content:
            self._validate_expression()
    
    def _validate_expression(self):
        """Validate the current DSL expression."""
        expression = self.expression_edit.toPlainText().strip()
        
        if not expression:
            self.validation_text.setPlainText("Enter an expression to validate...")
            return
        
        # Validate using DSL validator
        result = dsl_validator.validate_dsl_expression(expression)
        
        # Format validation results
        validation_output = []
        
        if result.is_valid:
            validation_output.append("✅ Expression is valid!")
        else:
            validation_output.append("❌ Expression has errors:")
            for error in result.errors:
                validation_output.append(f"  • {error}")
        
        if result.warnings:
            validation_output.append("\n⚠️ Warnings:")
            for warning in result.warnings:
                validation_output.append(f"  • {warning}")
        
        if result.suggestions:
            validation_output.append("\n💡 Suggestions:")
            for suggestion in result.suggestions:
                validation_output.append(f"  • {suggestion}")
        
        if result.detected_patterns:
            validation_output.append(f"\n🔍 Detected patterns: {', '.join(result.detected_patterns)}")
        
        if result.data_references:
            validation_output.append(f"\n📊 Data references: {', '.join(result.data_references)}")
        
        if result.function_calls:
            validation_output.append(f"\n🔧 Function calls: {', '.join(result.function_calls)}")
        
        self.validation_text.setPlainText("\n".join(validation_output))
    
    def _clear_expression(self):
        """Clear the expression editor."""
        self.expression_edit.clear()
        self.validation_text.setPlainText("Enter an expression to validate...")
        self.use_expression_btn.setEnabled(False)
    
    def _use_expression(self):
        """Emit the current expression for use."""
        expression = self.expression_edit.toPlainText().strip()
        if expression:
            self.expression_built.emit(expression)
    
    def set_expression(self, expression: str):
        """Set the expression in the editor."""
        self.expression_edit.setPlainText(expression)
        self._validate_expression()
    
    def get_expression(self) -> str:
        """Get the current expression."""
        return self.expression_edit.toPlainText().strip()
