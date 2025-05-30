"""
Enhanced error display widgets for the Moveworks YAML Assistant.

This module provides improved error visualization and user feedback.
"""

from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QScrollArea, QFrame, QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
    QSplitter, QGroupBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPalette, QPixmap, QPainter


class ErrorSeverity:
    """Error severity levels with associated colors and icons."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

    COLORS = {
        ERROR: "#ffebee",
        WARNING: "#fff3e0",
        INFO: "#e3f2fd",
        SUCCESS: "#e8f5e8"
    }

    BORDER_COLORS = {
        ERROR: "#f44336",
        WARNING: "#ff9800",
        INFO: "#2196f3",
        SUCCESS: "#4caf50"
    }

    TEXT_COLORS = {
        ERROR: "#c62828",
        WARNING: "#ef6c00",
        INFO: "#1565c0",
        SUCCESS: "#2e7d32"
    }


class ErrorItem(QFrame):
    """Individual error item widget with severity styling."""

    def __init__(self, message: str, severity: str = ErrorSeverity.ERROR, step_number: Optional[int] = None):
        super().__init__()
        self.message = message
        self.severity = severity
        self.step_number = step_number

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Set up the error item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        # Severity indicator
        severity_label = QLabel("●")
        severity_label.setFixedSize(16, 16)
        severity_label.setAlignment(Qt.AlignCenter)
        severity_label.setStyleSheet(f"color: {ErrorSeverity.BORDER_COLORS[self.severity]}; font-size: 12px; font-weight: bold;")
        layout.addWidget(severity_label)

        # Step number (if provided)
        if self.step_number is not None:
            step_label = QLabel(f"Step {self.step_number}:")
            step_label.setStyleSheet("font-weight: bold; color: #666;")
            layout.addWidget(step_label)

        # Error message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {ErrorSeverity.TEXT_COLORS[self.severity]};")
        layout.addWidget(message_label, 1)

    def _apply_styling(self):
        """Apply severity-based styling to the frame."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            ErrorItem {{
                background-color: {ErrorSeverity.COLORS[self.severity]};
                border: 1px solid {ErrorSeverity.BORDER_COLORS[self.severity]};
                border-radius: 4px;
                margin: 2px;
            }}
        """)


class ErrorListWidget(QWidget):
    """Widget for displaying a list of errors with filtering and grouping."""

    error_selected = Signal(str, int)  # message, step_number

    def __init__(self):
        super().__init__()
        self.errors = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the error list UI."""
        layout = QVBoxLayout(self)

        # Header with controls
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Validation Results")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_errors)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Scroll area for errors
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.error_container = QWidget()
        self.error_layout = QVBoxLayout(self.error_container)
        self.error_layout.addStretch()

        scroll_area.setWidget(self.error_container)
        layout.addWidget(scroll_area)

        # Summary label
        self.summary_label = QLabel("No errors")
        self.summary_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.summary_label)

    def set_errors(self, errors: List[str]):
        """Set the list of errors to display."""
        self.clear_errors()
        self.errors = errors

        if not errors:
            self.summary_label.setText("✓ No errors found")
            self.summary_label.setStyleSheet("color: #4caf50; font-style: italic;")
            return

        # Group errors by step number
        step_errors = {}
        general_errors = []

        for error in errors:
            if error.startswith("Step "):
                try:
                    # Extract step number
                    step_part = error.split(":")[0]
                    step_num = int(step_part.split()[1])
                    message = error[len(step_part) + 2:]  # Remove "Step X: "

                    if step_num not in step_errors:
                        step_errors[step_num] = []
                    step_errors[step_num].append(message)
                except (ValueError, IndexError):
                    general_errors.append(error)
            else:
                general_errors.append(error)

        # Add general errors first
        for error in general_errors:
            error_item = ErrorItem(error, ErrorSeverity.ERROR)
            self.error_layout.insertWidget(self.error_layout.count() - 1, error_item)

        # Add step-specific errors
        for step_num in sorted(step_errors.keys()):
            for error in step_errors[step_num]:
                error_item = ErrorItem(error, ErrorSeverity.ERROR, step_num)
                self.error_layout.insertWidget(self.error_layout.count() - 1, error_item)

        # Update summary
        error_count = len(errors)
        step_count = len(step_errors)
        if step_count > 0:
            self.summary_label.setText(f"{error_count} error(s) found in {step_count} step(s)")
        else:
            self.summary_label.setText(f"{error_count} error(s) found")
        self.summary_label.setStyleSheet("color: #f44336; font-style: italic;")

    def add_error(self, message: str, severity: str = ErrorSeverity.ERROR, step_number: Optional[int] = None):
        """Add a single error to the display."""
        error_item = ErrorItem(message, severity, step_number)
        self.error_layout.insertWidget(self.error_layout.count() - 1, error_item)
        self.errors.append(message)

    def clear_errors(self):
        """Clear all displayed errors."""
        # Remove all error items except the stretch
        while self.error_layout.count() > 1:
            child = self.error_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.errors.clear()
        self.summary_label.setText("No errors")
        self.summary_label.setStyleSheet("color: #666; font-style: italic;")


class ValidationDialog(QDialog):
    """Dialog for displaying detailed validation results."""

    def __init__(self, errors: List[str], parent=None):
        super().__init__(parent)
        self.errors = errors
        self.setWindowTitle("Validation Results")
        self.setModal(True)
        self.resize(600, 400)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the validation dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        if self.errors:
            header_label = QLabel(f"Found {len(self.errors)} validation error(s):")
            header_label.setStyleSheet("font-weight: bold; color: #f44336; font-size: 14px;")
        else:
            header_label = QLabel("✓ Validation passed successfully!")
            header_label.setStyleSheet("font-weight: bold; color: #4caf50; font-size: 14px;")

        layout.addWidget(header_label)

        if self.errors:
            # Error list
            error_list = ErrorListWidget()
            error_list.set_errors(self.errors)
            layout.addWidget(error_list)

            # Export errors button
            export_btn = QPushButton("Copy Errors to Clipboard")
            export_btn.clicked.connect(self._copy_errors_to_clipboard)
            layout.addWidget(export_btn)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _copy_errors_to_clipboard(self):
        """Copy all errors to clipboard."""
        from PySide6.QtWidgets import QApplication
        error_text = "\n".join(self.errors)
        QApplication.clipboard().setText(error_text)


class StatusIndicator(QLabel):
    """Status indicator widget with color coding and tooltips."""

    def __init__(self, text: str = "Ready"):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(30)
        self.set_status("ready")

    def set_status(self, status: str, message: str = None):
        """Set the status with appropriate styling."""
        status_config = {
            "ready": {"color": "#4caf50", "bg": "#e8f5e8", "text": "Ready"},
            "error": {"color": "#f44336", "bg": "#ffebee", "text": "Errors Found"},
            "warning": {"color": "#ff9800", "bg": "#fff3e0", "text": "Warnings"},
            "working": {"color": "#2196f3", "bg": "#e3f2fd", "text": "Processing..."},
            "success": {"color": "#4caf50", "bg": "#e8f5e8", "text": "Success"}
        }

        config = status_config.get(status, status_config["ready"])

        display_text = message or config["text"]
        self.setText(display_text)

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {config["bg"]};
                color: {config["color"]};
                border: 1px solid {config["color"]};
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }}
        """)

    def set_error_count(self, count: int):
        """Set status based on error count."""
        if count == 0:
            self.set_status("success", "✓ No Errors")
        else:
            self.set_status("error", f"✗ {count} Error(s)")


class HelpDialog(QDialog):
    """Dialog for displaying help content with search and navigation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Moveworks YAML Assistant - Help")
        self.setModal(False)
        self.resize(800, 600)
        self._setup_ui()
        self._load_help_content()

    def _setup_ui(self):
        """Set up the help dialog UI."""
        layout = QVBoxLayout(self)

        # Create splitter for navigation and content
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel: Navigation
        nav_panel = self._create_navigation_panel()
        splitter.addWidget(nav_panel)

        # Right panel: Content
        content_panel = self._create_content_panel()
        splitter.addWidget(content_panel)

        # Set splitter proportions
        splitter.setSizes([250, 550])

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

    def _create_navigation_panel(self):
        """Create the navigation panel with topics list."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Search box
        from PySide6.QtWidgets import QLineEdit
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search help topics...")
        self.search_box.textChanged.connect(self._filter_topics)
        layout.addWidget(self.search_box)

        # Topics list
        self.topics_list = QListWidget()
        self.topics_list.itemClicked.connect(self._on_topic_selected)
        layout.addWidget(self.topics_list)

        return panel

    def _create_content_panel(self):
        """Create the content panel for displaying help text."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        self.content_title = QLabel("Select a topic")
        self.content_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.content_title)

        # Content
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        layout.addWidget(self.content_text)

        # Related topics
        self.related_label = QLabel("Related Topics:")
        self.related_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.related_label.hide()
        layout.addWidget(self.related_label)

        self.related_list = QListWidget()
        self.related_list.setMaximumHeight(100)
        self.related_list.itemClicked.connect(self._on_related_topic_clicked)
        self.related_list.hide()
        layout.addWidget(self.related_list)

        return panel

    def _load_help_content(self):
        """Load help content into the topics list."""
        from help_system import help_system

        # Group topics by category
        categories = help_system.get_all_categories()

        for category in categories:
            # Add category header
            category_item = QListWidgetItem(f"📁 {category}")
            category_item.setData(Qt.UserRole, {"type": "category", "name": category})
            font = category_item.font()
            font.setBold(True)
            category_item.setFont(font)
            self.topics_list.addItem(category_item)

            # Add topics in category
            topics = help_system.get_topics_by_category(category)
            for topic in topics:
                topic_item = QListWidgetItem(f"  📄 {topic.title}")
                topic_item.setData(Qt.UserRole, {"type": "topic", "topic": topic})
                self.topics_list.addItem(topic_item)

    def _filter_topics(self, query: str):
        """Filter topics based on search query."""
        if not query.strip():
            # Show all topics
            for i in range(self.topics_list.count()):
                self.topics_list.item(i).setHidden(False)
            return

        from help_system import help_system
        matching_topics = help_system.search_topics(query)
        matching_titles = {topic.title for topic in matching_topics}

        # Hide non-matching topics
        for i in range(self.topics_list.count()):
            item = self.topics_list.item(i)
            item_data = item.data(Qt.UserRole)

            if item_data["type"] == "category":
                # Show category if any topics in it match
                category_topics = help_system.get_topics_by_category(item_data["name"])
                has_matching = any(topic.title in matching_titles for topic in category_topics)
                item.setHidden(not has_matching)
            else:
                # Show topic if it matches
                topic_title = item_data["topic"].title
                item.setHidden(topic_title not in matching_titles)

    def _on_topic_selected(self, item):
        """Handle topic selection."""
        item_data = item.data(Qt.UserRole)

        if item_data["type"] == "topic":
            topic = item_data["topic"]
            self._display_topic(topic)

    def _on_related_topic_clicked(self, item):
        """Handle related topic click."""
        topic_title = item.text()
        from help_system import help_system
        topic = help_system.get_topic(topic_title)
        if topic:
            self._display_topic(topic)

    def _display_topic(self, topic):
        """Display a help topic in the content panel."""
        self.content_title.setText(topic.title)
        self.content_text.setPlainText(topic.content)

        # Show related topics
        from help_system import help_system
        related_topics = help_system.get_related_topics(topic.title)

        if related_topics:
            self.related_label.show()
            self.related_list.show()
            self.related_list.clear()

            for related_topic in related_topics:
                item = QListWidgetItem(related_topic.title)
                self.related_list.addItem(item)
        else:
            self.related_label.hide()
            self.related_list.hide()

    def show_topic(self, topic_title: str):
        """Show the dialog and navigate to a specific topic."""
        from help_system import help_system
        topic = help_system.get_topic(topic_title)
        if topic:
            self._display_topic(topic)
        self.show()
        self.raise_()
        self.activateWindow()
