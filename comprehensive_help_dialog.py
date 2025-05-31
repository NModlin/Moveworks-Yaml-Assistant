"""
Comprehensive Help Dialog for the Enhanced Moveworks YAML Assistant.

This module provides a modern, searchable help interface with support for
all features, tutorials, and documentation.
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QGroupBox, QScrollArea, QFrame,
    QComboBox, QCheckBox, QProgressBar, QToolButton, QMenu
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, pyqtSignal
from PySide6.QtGui import QFont, QIcon, QPixmap, QTextDocument, QAction

from help_system import help_system, HelpTopic, HelpSection


class HelpSearchThread(QThread):
    """Background thread for searching help content."""

    search_completed = pyqtSignal(list)  # List of HelpTopic results

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        """Perform search in background."""
        if len(self.query) >= 2:  # Minimum search length
            results = help_system.search_topics(self.query)
            self.search_completed.emit(results)
        else:
            self.search_completed.emit([])


class HelpTopicViewer(QTextEdit):
    """Enhanced text viewer for help topics with rich formatting."""

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)

        # Configure rich text display
        self.document().setDefaultStyleSheet("""
            h1 { color: #2c3e50; font-size: 24px; margin-bottom: 16px; }
            h2 { color: #34495e; font-size: 20px; margin-bottom: 12px; margin-top: 20px; }
            h3 { color: #7f8c8d; font-size: 16px; margin-bottom: 8px; margin-top: 16px; }
            p { margin-bottom: 12px; line-height: 1.6; }
            code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }
            pre { background-color: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #3498db; margin: 12px 0; }
            ul { margin-bottom: 12px; }
            li { margin-bottom: 4px; }
            .tip { background-color: #e8f5e8; padding: 12px; border-radius: 6px; border-left: 4px solid #27ae60; margin: 12px 0; }
            .warning { background-color: #fff3cd; padding: 12px; border-radius: 6px; border-left: 4px solid #ffc107; margin: 12px 0; }
            .error { background-color: #f8d7da; padding: 12px; border-radius: 6px; border-left: 4px solid #dc3545; margin: 12px 0; }
        """)

    def display_topic(self, topic: HelpTopic):
        """Display a help topic with rich formatting."""
        if not topic:
            self.clear()
            return

        # Convert markdown-like content to HTML
        html_content = self._convert_to_html(topic)
        self.setHtml(html_content)

    def _convert_to_html(self, topic: HelpTopic) -> str:
        """Convert topic content to HTML with rich formatting."""
        content = topic.content

        # Basic markdown-like conversions
        content = content.replace('\n# ', '\n<h1>')
        content = content.replace('\n## ', '\n<h2>')
        content = content.replace('\n### ', '\n<h3>')
        content = content.replace('\n\n', '</p><p>')

        # Code blocks
        content = content.replace('```yaml\n', '<pre><code class="yaml">')
        content = content.replace('```python\n', '<pre><code class="python">')
        content = content.replace('```json\n', '<pre><code class="json">')
        content = content.replace('```\n', '</code></pre>')

        # Inline code
        import re
        content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)

        # Bold and italic
        content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)

        # Lists
        content = re.sub(r'\n- ', '\n<li>', content)
        content = re.sub(r'(<li>.*?)(?=\n[^<])', r'<ul>\1</ul>', content, flags=re.DOTALL)

        # Add topic metadata
        metadata = f"""
        <div style="background-color: #ecf0f1; padding: 12px; border-radius: 6px; margin-bottom: 20px;">
            <h1>{topic.title}</h1>
            <p><strong>Category:</strong> {topic.category}</p>
            <p><strong>Difficulty:</strong> {topic.difficulty}</p>
            <p><strong>Estimated Time:</strong> {topic.estimated_time}</p>
            {f'<p><strong>Prerequisites:</strong> {", ".join(topic.prerequisites)}</p>' if topic.prerequisites else ''}
        </div>
        """

        return f"{metadata}<div>{content}</div>"


class ComprehensiveHelpDialog(QDialog):
    """
    Modern, comprehensive help dialog with advanced features.

    Features:
    - Searchable help content
    - Categorized topics
    - Rich text display
    - Related topics
    - Bookmarks
    - Print support
    - Tutorial integration
    """

    tutorial_requested = Signal(str)  # Emits tutorial ID to start

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enhanced Moveworks YAML Assistant - Help & Documentation")
        self.setGeometry(200, 200, 1200, 800)

        # Search state
        self.search_thread = None
        self.current_topic = None
        self.bookmarks = []

        self._setup_ui()
        self._connect_signals()
        self._load_initial_content()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Apply comprehensive dialog styling with high contrast
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 13px;
                font-weight: 500;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
            }
            QGroupBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #2c3e50;
                background-color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QTextEdit, QLineEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
            QListWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }
            QListWidget::item {
                color: #2c3e50;
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #ebf3fd;
            }
            QTreeWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }
            QTreeWidget::item {
                color: #2c3e50;
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
            QToolButton {
                background-color: #95a5a6;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QToolButton:hover {
                background-color: #7f8c8d;
            }
        """)

        # Header with search and tools
        header_layout = self._create_header()
        layout.addLayout(header_layout)

        # Main content splitter
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Left panel: Navigation
        left_panel = self._create_navigation_panel()
        main_splitter.addWidget(left_panel)

        # Right panel: Content display
        right_panel = self._create_content_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([350, 850])

        # Footer with status and actions
        footer_layout = self._create_footer()
        layout.addLayout(footer_layout)

    def _create_header(self) -> QHBoxLayout:
        """Create the header with search and tools."""
        layout = QHBoxLayout()

        # Search section
        search_label = QLabel("🔍 Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search help topics, features, tutorials...")
        self.search_edit.setMinimumWidth(300)

        # Search options
        self.search_options_btn = QToolButton()
        self.search_options_btn.setText("⚙️")
        self.search_options_btn.setToolTip("Search Options")

        # Quick access buttons
        self.tutorials_btn = QPushButton("📚 Tutorials")
        self.templates_btn = QPushButton("📋 Templates")
        self.examples_btn = QPushButton("💡 Examples")

        layout.addWidget(search_label)
        layout.addWidget(self.search_edit)
        layout.addWidget(self.search_options_btn)
        layout.addStretch()
        layout.addWidget(self.tutorials_btn)
        layout.addWidget(self.templates_btn)
        layout.addWidget(self.examples_btn)

        return layout

    def _create_navigation_panel(self) -> QWidget:
        """Create the left navigation panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Navigation tabs
        nav_tabs = QTabWidget()

        # Sections tab
        sections_tab = self._create_sections_tab()
        nav_tabs.addTab(sections_tab, "📖 Sections")

        # Search results tab
        search_tab = self._create_search_tab()
        nav_tabs.addTab(search_tab, "🔍 Search")

        # Bookmarks tab
        bookmarks_tab = self._create_bookmarks_tab()
        nav_tabs.addTab(bookmarks_tab, "⭐ Bookmarks")

        layout.addWidget(nav_tabs)
        return panel

    def _create_sections_tab(self) -> QWidget:
        """Create the sections navigation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Sections tree
        self.sections_tree = QTreeWidget()
        self.sections_tree.setHeaderLabel("Help Sections")
        self.sections_tree.setRootIsDecorated(True)

        layout.addWidget(self.sections_tree)
        return widget

    def _create_search_tab(self) -> QWidget:
        """Create the search results tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search results list
        self.search_results = QListWidget()
        self.search_results.setAlternatingRowColors(True)

        # Search status
        self.search_status = QLabel("Enter search terms to find help topics")
        self.search_status.setStyleSheet("color: #7f8c8d; font-style: italic;")

        layout.addWidget(self.search_status)
        layout.addWidget(self.search_results)
        return widget

    def _create_bookmarks_tab(self) -> QWidget:
        """Create the bookmarks tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Bookmarks list
        self.bookmarks_list = QListWidget()

        # Bookmark controls
        bookmark_controls = QHBoxLayout()
        self.add_bookmark_btn = QPushButton("Add")
        self.remove_bookmark_btn = QPushButton("Remove")

        bookmark_controls.addWidget(self.add_bookmark_btn)
        bookmark_controls.addWidget(self.remove_bookmark_btn)
        bookmark_controls.addStretch()

        layout.addLayout(bookmark_controls)
        layout.addWidget(self.bookmarks_list)
        return widget

    def _create_content_panel(self) -> QWidget:
        """Create the right content panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Content tabs
        content_tabs = QTabWidget()

        # Main content tab
        main_tab = self._create_main_content_tab()
        content_tabs.addTab(main_tab, "📄 Content")

        # Related topics tab
        related_tab = self._create_related_topics_tab()
        content_tabs.addTab(related_tab, "🔗 Related")

        layout.addWidget(content_tabs)
        return panel

    def _create_main_content_tab(self) -> QWidget:
        """Create the main content display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Topic header
        self.topic_header = QLabel()
        self.topic_header.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.topic_header.hide()

        # Content viewer
        self.content_viewer = HelpTopicViewer()

        # Content controls
        controls_layout = QHBoxLayout()
        self.bookmark_btn = QPushButton("⭐ Bookmark")
        self.print_btn = QPushButton("🖨️ Print")
        self.copy_btn = QPushButton("📋 Copy")

        controls_layout.addWidget(self.bookmark_btn)
        controls_layout.addWidget(self.print_btn)
        controls_layout.addWidget(self.copy_btn)
        controls_layout.addStretch()

        layout.addWidget(self.topic_header)
        layout.addWidget(self.content_viewer)
        layout.addLayout(controls_layout)
        return widget

    def _create_related_topics_tab(self) -> QWidget:
        """Create the related topics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Related topics list
        self.related_topics_list = QListWidget()

        layout.addWidget(QLabel("Related Topics:"))
        layout.addWidget(self.related_topics_list)
        return widget

    def _create_footer(self) -> QHBoxLayout:
        """Create the footer with status and actions."""
        layout = QHBoxLayout()

        # Status information
        self.status_label = QLabel("Ready")

        # Action buttons
        self.close_btn = QPushButton("Close")

        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.close_btn)

        return layout

    def _connect_signals(self):
        """Connect UI signals to handlers."""
        # Search
        self.search_edit.textChanged.connect(self._on_search_changed)

        # Navigation
        self.sections_tree.itemClicked.connect(self._on_section_item_clicked)
        self.search_results.itemClicked.connect(self._on_search_result_clicked)
        self.related_topics_list.itemClicked.connect(self._on_related_topic_clicked)

        # Controls
        self.bookmark_btn.clicked.connect(self._add_bookmark)
        self.close_btn.clicked.connect(self.close)

        # Quick access
        self.tutorials_btn.clicked.connect(lambda: self._show_section("Tutorials"))
        self.templates_btn.clicked.connect(lambda: self._show_section("Templates & Examples"))
        self.examples_btn.clicked.connect(lambda: self._show_section("Examples"))

    def _load_initial_content(self):
        """Load initial help content."""
        self._populate_sections_tree()
        self._show_welcome_content()

    def _populate_sections_tree(self):
        """Populate the sections tree with help content."""
        self.sections_tree.clear()

        sections = help_system.get_sections()
        for section in sections:
            section_item = QTreeWidgetItem([f"{section.icon} {section.title}"])
            section_item.setData(0, Qt.UserRole, section)

            # Add topics to section
            topics = help_system.get_section_topics(section.title)
            for topic in topics:
                topic_item = QTreeWidgetItem([topic.title])
                topic_item.setData(0, Qt.UserRole, topic)
                section_item.addChild(topic_item)

            self.sections_tree.addTopLevelItem(section_item)

        # Expand first section
        if self.sections_tree.topLevelItemCount() > 0:
            self.sections_tree.topLevelItem(0).setExpanded(True)

    def _show_welcome_content(self):
        """Show welcome content with enhanced features."""
        # Try to show the enhanced compound action topic first
        compound_action_topic = help_system.get_topic("Compound Action Name")
        if compound_action_topic:
            self.show_topic(compound_action_topic)
        else:
            # Fallback to application overview
            welcome_topic = help_system.get_topic("Application Overview")
            if welcome_topic:
                self.show_topic(welcome_topic)

    def show_topic(self, topic: HelpTopic):
        """Display a specific help topic."""
        if not topic:
            return

        self.current_topic = topic
        self.topic_header.setText(f"{topic.category} → {topic.title}")
        self.topic_header.show()

        # Display content
        self.content_viewer.display_topic(topic)

        # Update related topics
        self._update_related_topics(topic)

        # Update status
        self.status_label.setText(f"Viewing: {topic.title}")

    def _update_related_topics(self, topic: HelpTopic):
        """Update the related topics list."""
        self.related_topics_list.clear()

        related_topics = help_system.get_related_topics(topic.title)
        for related_topic in related_topics:
            item = QListWidgetItem(related_topic.title)
            item.setData(Qt.UserRole, related_topic)
            self.related_topics_list.addItem(item)

    def _on_search_changed(self, text: str):
        """Handle search text changes."""
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()

        if len(text) >= 2:
            self.search_thread = HelpSearchThread(text)
            self.search_thread.search_completed.connect(self._on_search_completed)
            self.search_thread.start()
            self.search_status.setText("Searching...")
        else:
            self.search_results.clear()
            self.search_status.setText("Enter search terms to find help topics")

    def _on_search_completed(self, results: List[HelpTopic]):
        """Handle search completion."""
        self.search_results.clear()

        if results:
            for topic in results:
                item = QListWidgetItem(f"{topic.category} → {topic.title}")
                item.setData(Qt.UserRole, topic)
                item.setToolTip(topic.content[:200] + "..." if len(topic.content) > 200 else topic.content)
                self.search_results.addItem(item)

            self.search_status.setText(f"Found {len(results)} topics")
        else:
            self.search_status.setText("No topics found")

    def _on_section_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle section tree item clicks."""
        data = item.data(0, Qt.UserRole)
        if isinstance(data, HelpTopic):
            self.show_topic(data)

    def _on_search_result_clicked(self, item: QListWidgetItem):
        """Handle search result clicks."""
        topic = item.data(Qt.UserRole)
        if topic:
            self.show_topic(topic)

    def _on_related_topic_clicked(self, item: QListWidgetItem):
        """Handle related topic clicks."""
        topic = item.data(Qt.UserRole)
        if topic:
            self.show_topic(topic)

    def _add_bookmark(self):
        """Add current topic to bookmarks."""
        if self.current_topic and self.current_topic not in self.bookmarks:
            self.bookmarks.append(self.current_topic)
            self._update_bookmarks_list()

    def _update_bookmarks_list(self):
        """Update the bookmarks list display."""
        self.bookmarks_list.clear()
        for topic in self.bookmarks:
            item = QListWidgetItem(topic.title)
            item.setData(Qt.UserRole, topic)
            self.bookmarks_list.addItem(item)

    def _show_section(self, section_name: str):
        """Show a specific help section."""
        # Find and expand the section in the tree
        for i in range(self.sections_tree.topLevelItemCount()):
            item = self.sections_tree.topLevelItem(i)
            section = item.data(0, Qt.UserRole)
            if isinstance(section, HelpSection) and section.title == section_name:
                item.setExpanded(True)
                self.sections_tree.setCurrentItem(item)
                break

    def show_topic_by_title(self, title: str):
        """Show a topic by its title."""
        topic = help_system.get_topic(title)
        if topic:
            self.show_topic(topic)
            self.show()
            self.raise_()
            self.activateWindow()
