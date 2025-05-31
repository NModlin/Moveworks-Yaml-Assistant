"""
Enhanced Script Editor Widget for APIthon Scripts.

This module provides a comprehensive script editor with real-time validation,
resource constraint monitoring, and educational feedback for APIthon scripts.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton,
    QProgressBar, QFrame, QScrollArea, QGroupBox, QFormLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QToolTip
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QTextCharFormat, QTextCursor
from typing import Optional, Set
from core_structures import ScriptStep
from enhanced_apiton_validator import enhanced_apiton_validator, APIthonValidationResult


class ValidationIndicator(QFrame):
    """Visual indicator for validation status with detailed feedback."""
    
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setMaximumHeight(100)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the validation indicator UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Status header
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Resource usage bars
        resource_layout = QHBoxLayout()
        
        # Code size indicator
        code_size_layout = QVBoxLayout()
        code_size_layout.addWidget(QLabel("Code Size:"))
        self.code_size_bar = QProgressBar()
        self.code_size_bar.setMaximum(4096)
        self.code_size_bar.setTextVisible(True)
        self.code_size_bar.setFormat("%v / %m bytes")
        code_size_layout.addWidget(self.code_size_bar)
        resource_layout.addLayout(code_size_layout)
        
        layout.addLayout(resource_layout)
        
        # Quick stats
        self.stats_label = QLabel("0 errors, 0 warnings")
        self.stats_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.stats_label)
        
    def update_validation(self, result: APIthonValidationResult):
        """Update the indicator with validation results."""
        # Update status
        if result.is_valid:
            if result.warnings:
                self.status_label.setText("✓ Valid (with warnings)")
                self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
                self.setStyleSheet("QFrame { border: 2px solid #ff9800; background-color: #fff3e0; }")
            else:
                self.status_label.setText("✓ Valid")
                self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
                self.setStyleSheet("QFrame { border: 2px solid #4caf50; background-color: #e8f5e8; }")
        else:
            self.status_label.setText("✗ Invalid")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self.setStyleSheet("QFrame { border: 2px solid #f44336; background-color: #ffebee; }")
            
        # Update resource usage
        if 'code_bytes' in result.resource_usage:
            code_bytes = result.resource_usage['code_bytes']
            self.code_size_bar.setValue(code_bytes)
            
            # Color code the progress bar based on usage
            if code_bytes > 3276:  # 80% of 4096
                self.code_size_bar.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")
            elif code_bytes > 2048:  # 50% of 4096
                self.code_size_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff9800; }")
            else:
                self.code_size_bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; }")
                
        # Update stats
        error_count = len(result.errors)
        warning_count = len(result.warnings)
        self.stats_label.setText(f"{error_count} errors, {warning_count} warnings")


class FeedbackPanel(QScrollArea):
    """Panel for displaying detailed validation feedback and suggestions."""
    
    fix_requested = Signal(str, str)  # fix_type, fix_data
    
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setMaximumHeight(200)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the feedback panel UI."""
        content_widget = QWidget()
        self.setWidget(content_widget)
        
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_label = QLabel("Validation Feedback")
        header_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-bottom: 8px;")
        self.layout.addWidget(header_label)
        
        # Content will be added dynamically
        self.layout.addStretch()
        
    def update_feedback(self, result: APIthonValidationResult):
        """Update the feedback panel with validation results."""
        # Clear existing content (except header and stretch)
        while self.layout.count() > 2:
            child = self.layout.takeAt(1)
            if child.widget():
                child.widget().deleteLater()
                
        # Add errors
        for error in result.errors:
            error_widget = self._create_feedback_item(error, "error")
            self.layout.insertWidget(self.layout.count() - 1, error_widget)
            
        # Add warnings
        for warning in result.warnings:
            warning_widget = self._create_feedback_item(warning, "warning")
            self.layout.insertWidget(self.layout.count() - 1, warning_widget)
            
        # Add suggestions
        for suggestion in result.suggestions:
            suggestion_widget = self._create_feedback_item(suggestion, "suggestion")
            self.layout.insertWidget(self.layout.count() - 1, suggestion_widget)
            
        # Add return analysis feedback
        if result.return_analysis:
            self._add_return_analysis_feedback(result.return_analysis)
            
        # Add citation compliance feedback
        if result.citation_compliance.get('is_reserved'):
            self._add_citation_feedback(result.citation_compliance)
            
    def _create_feedback_item(self, message: str, feedback_type: str) -> QFrame:
        """Create a feedback item widget."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Icon and styling based on type
        if feedback_type == "error":
            icon = "❌"
            frame.setStyleSheet("QFrame { background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; }")
        elif feedback_type == "warning":
            icon = "⚠️"
            frame.setStyleSheet("QFrame { background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; }")
        else:  # suggestion
            icon = "💡"
            frame.setStyleSheet("QFrame { background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; }")
            
        # Message
        message_label = QLabel(f"{icon} {message}")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #2c3e50; font-size: 11px;")
        layout.addWidget(message_label, 1)
        
        return frame
        
    def _add_return_analysis_feedback(self, return_analysis: dict):
        """Add return value analysis feedback."""
        if not return_analysis.get('has_explicit_return') and return_analysis.get('last_statement_type') == 'Assign':
            feedback = self._create_feedback_item(
                "💡 Tip: The last line assigns to a variable but doesn't return it. "
                "The output_key will receive None instead of your variable's value.",
                "suggestion"
            )
            self.layout.insertWidget(self.layout.count() - 1, feedback)
            
    def _add_citation_feedback(self, citation_compliance: dict):
        """Add citation compliance feedback."""
        if citation_compliance.get('compliance_status') == 'non_compliant':
            feedback = self._create_feedback_item(
                f"📋 Citation Format: output_key '{citation_compliance['output_key']}' suggests citation format. "
                f"Consider including fields: {', '.join(citation_compliance['required_fields'])}",
                "suggestion"
            )
            self.layout.insertWidget(self.layout.count() - 1, feedback)


class EnhancedScriptEditor(QWidget):
    """Enhanced script editor with real-time validation and feedback."""
    
    script_changed = Signal()
    validation_updated = Signal(APIthonValidationResult)
    
    def __init__(self):
        super().__init__()
        self.current_step: Optional[ScriptStep] = None
        self.available_data_paths: Set[str] = set()
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._perform_validation)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the enhanced script editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header with title and help
        header_layout = QHBoxLayout()
        title_label = QLabel("APIthon Script Editor")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        help_btn = QPushButton("?")
        help_btn.setMaximumSize(24, 24)
        help_btn.setToolTip("Click for APIthon scripting help and examples")
        help_btn.clicked.connect(self._show_help)
        header_layout.addWidget(help_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Validation indicator
        self.validation_indicator = ValidationIndicator()
        layout.addWidget(self.validation_indicator)
        
        # Script code editor
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText(
            "Enter your APIthon script code here...\n\n"
            "# Example:\n"
            "user_name = data.user_info.name\n"
            "result = {'greeting': f'Hello, {user_name}!'}\n"
            "return result"
        )
        
        # Set monospace font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.code_editor.setFont(font)
        
        # Connect text change signal with debouncing
        self.code_editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.code_editor)
        
        # Feedback panel
        self.feedback_panel = FeedbackPanel()
        self.feedback_panel.fix_requested.connect(self._apply_fix)
        layout.addWidget(self.feedback_panel)
        
    def set_script_step(self, step: ScriptStep, available_data_paths: Set[str] = None):
        """Set the script step to edit."""
        self.current_step = step
        self.available_data_paths = available_data_paths or set()
        
        # Update editor content
        if step and step.code:
            self.code_editor.setPlainText(step.code)
        else:
            self.code_editor.clear()
            
        # Trigger validation
        self._perform_validation()
        
    def _on_text_changed(self):
        """Handle text changes with debounced validation."""
        # Update the step if we have one
        if self.current_step:
            self.current_step.code = self.code_editor.toPlainText()
            
        # Restart the validation timer
        self.validation_timer.start(500)  # 500ms delay
        self.script_changed.emit()
        
    def _perform_validation(self):
        """Perform comprehensive validation on the current script."""
        if not self.current_step:
            return
            
        # Run enhanced validation
        result = enhanced_apiton_validator.comprehensive_validate(
            self.current_step, 
            self.available_data_paths
        )
        
        # Update UI components
        self.validation_indicator.update_validation(result)
        self.feedback_panel.update_feedback(result)
        
        # Emit validation result
        self.validation_updated.emit(result)
        
    def _apply_fix(self, fix_type: str, fix_data: str):
        """Apply an automated fix to the script."""
        # This would implement automated fixes based on suggestions
        # For now, just show a message
        QMessageBox.information(
            self, 
            "Auto-Fix", 
            f"Auto-fix feature coming soon!\nFix type: {fix_type}\nData: {fix_data}"
        )
        
    def _show_help(self):
        """Show APIthon scripting help and examples."""
        help_text = """
        <h3>APIthon Scripting Guide</h3>
        
        <h4>Basic Rules:</h4>
        <ul>
        <li>No import statements allowed</li>
        <li>No class or function definitions</li>
        <li>No private identifiers (starting with _)</li>
        <li>Return statements allowed at module level</li>
        </ul>
        
        <h4>Resource Limits:</h4>
        <ul>
        <li>Maximum script size: 4096 bytes</li>
        <li>Maximum string length: 4096 characters</li>
        <li>Numeric values: 0 to 4,294,967,295</li>
        </ul>
        
        <h4>Data Access:</h4>
        <ul>
        <li>Use <code>data.field_name</code> for workflow data</li>
        <li>Use <code>meta_info.user.email</code> for user context</li>
        </ul>
        
        <h4>Return Values:</h4>
        <ul>
        <li>Last line should be an expression or return statement</li>
        <li>Avoid assignments as the final line</li>
        <li>For output_key "result": return citation dictionary</li>
        <li>For output_key "results": return list of citations</li>
        </ul>
        """
        
        QMessageBox.information(self, "APIthon Help", help_text)
