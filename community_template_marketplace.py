"""
Community Template Marketplace for the Moveworks YAML Assistant.

This module provides a platform for sharing, discovering, and managing
community-contributed workflow templates, fostering collaboration and
knowledge sharing among users.
"""

import json
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QTextEdit, QLineEdit, QComboBox, QSpinBox, QDialog,
    QFormLayout, QDialogButtonBox, QTabWidget, QGroupBox, QScrollArea,
    QFrame, QProgressBar, QMessageBox, QSplitter, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QSlider, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QDate
from PySide6.QtGui import QFont, QIcon, QPalette, QPixmap

from core_structures import Workflow
from template_library import WorkflowTemplate
from yaml_generator import generate_yaml_string


@dataclass
class CommunityTemplate:
    """Represents a community-contributed template."""
    id: str
    name: str
    description: str
    author: str
    author_email: str
    category: str
    tags: List[str]
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    workflow_yaml: str
    version: str = "1.0.0"
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    license: str = "MIT"
    dependencies: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    documentation: str = ""
    verified: bool = False


@dataclass
class TemplateRating:
    """Represents a user rating for a template."""
    template_id: str
    user_id: str
    rating: int  # 1-5 stars
    review: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TemplateComment:
    """Represents a user comment on a template."""
    template_id: str
    user_id: str
    username: str
    comment: str
    parent_comment_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class TemplateRepository:
    """Manages the local template repository and remote synchronization."""
    
    def __init__(self, local_path: str = "templates/community"):
        self.local_path = Path(local_path)
        self.local_path.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, CommunityTemplate] = {}
        self.ratings: Dict[str, List[TemplateRating]] = {}
        self.comments: Dict[str, List[TemplateComment]] = {}
        
        # Mock remote API endpoints (would be real in production)
        self.api_base_url = "https://api.moveworks-templates.com/v1"
        
        self._load_local_templates()
    
    def _load_local_templates(self):
        """Load templates from local storage."""
        templates_file = self.local_path / "templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r') as f:
                    data = json.load(f)
                    for template_data in data.get('templates', []):
                        template = CommunityTemplate(**template_data)
                        self.templates[template.id] = template
            except Exception as e:
                print(f"Error loading local templates: {e}")
    
    def _save_local_templates(self):
        """Save templates to local storage."""
        templates_file = self.local_path / "templates.json"
        try:
            data = {
                'templates': [asdict(template) for template in self.templates.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(templates_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving local templates: {e}")
    
    def search_templates(self, query: str = "", category: str = "", 
                        difficulty: str = "", tags: List[str] = None) -> List[CommunityTemplate]:
        """Search templates based on criteria."""
        results = []
        
        for template in self.templates.values():
            # Text search
            if query and query.lower() not in template.name.lower() and \
               query.lower() not in template.description.lower():
                continue
            
            # Category filter
            if category and template.category != category:
                continue
            
            # Difficulty filter
            if difficulty and template.difficulty != difficulty:
                continue
            
            # Tags filter
            if tags and not any(tag in template.tags for tag in tags):
                continue
            
            results.append(template)
        
        # Sort by rating and downloads
        return sorted(results, key=lambda t: (t.rating, t.downloads), reverse=True)
    
    def get_template(self, template_id: str) -> Optional[CommunityTemplate]:
        """Get a specific template by ID."""
        return self.templates.get(template_id)
    
    def download_template(self, template_id: str) -> bool:
        """Download and install a template."""
        template = self.get_template(template_id)
        if not template:
            return False
        
        # Increment download count
        template.downloads += 1
        self._save_local_templates()
        
        # Save template file locally
        template_file = self.local_path / f"{template_id}.yaml"
        try:
            with open(template_file, 'w') as f:
                f.write(template.workflow_yaml)
            return True
        except Exception as e:
            print(f"Error downloading template: {e}")
            return False
    
    def submit_template(self, template: CommunityTemplate) -> bool:
        """Submit a new template to the community."""
        # Generate unique ID
        template.id = hashlib.md5(
            f"{template.name}{template.author}{datetime.now()}".encode()
        ).hexdigest()[:12]
        
        # Add to local repository
        self.templates[template.id] = template
        self._save_local_templates()
        
        # In a real implementation, this would upload to the remote server
        return True
    
    def rate_template(self, template_id: str, rating: int, review: str, user_id: str) -> bool:
        """Rate a template."""
        if template_id not in self.templates:
            return False
        
        # Create rating
        template_rating = TemplateRating(
            template_id=template_id,
            user_id=user_id,
            rating=rating,
            review=review
        )
        
        # Add to ratings
        if template_id not in self.ratings:
            self.ratings[template_id] = []
        self.ratings[template_id].append(template_rating)
        
        # Update template rating
        template = self.templates[template_id]
        all_ratings = [r.rating for r in self.ratings[template_id]]
        template.rating = sum(all_ratings) / len(all_ratings)
        template.rating_count = len(all_ratings)
        
        self._save_local_templates()
        return True
    
    def get_popular_templates(self, limit: int = 10) -> List[CommunityTemplate]:
        """Get the most popular templates."""
        return sorted(
            self.templates.values(),
            key=lambda t: (t.downloads, t.rating),
            reverse=True
        )[:limit]
    
    def get_recent_templates(self, days: int = 7) -> List[CommunityTemplate]:
        """Get recently added templates."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = [t for t in self.templates.values() if t.created_at >= cutoff_date]
        return sorted(recent, key=lambda t: t.created_at, reverse=True)


class TemplateSubmissionDialog(QDialog):
    """Dialog for submitting new templates to the community."""
    
    def __init__(self, workflow: Workflow, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.setWindowTitle("Submit Template to Community")
        self.setModal(True)
        self.resize(600, 500)
        self.setupUI()
    
    def setupUI(self):
        """Set up the submission dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form for template metadata
        form_group = QGroupBox("Template Information")
        form_layout = QFormLayout(form_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a descriptive name for your template")
        form_layout.addRow("Template Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Describe what this template does and when to use it")
        form_layout.addRow("Description:", self.description_edit)
        
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Your name")
        form_layout.addRow("Author:", self.author_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("your.email@example.com")
        form_layout.addRow("Email:", self.email_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "User Management", "Communication", "Approvals", "IT Service Management",
            "Data Processing", "Integration", "Automation", "Other"
        ])
        form_layout.addRow("Category:", self.category_combo)
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["beginner", "intermediate", "advanced"])
        form_layout.addRow("Difficulty:", self.difficulty_combo)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("user, notification, approval (comma-separated)")
        form_layout.addRow("Tags:", self.tags_edit)
        
        self.license_combo = QComboBox()
        self.license_combo.addItems(["MIT", "Apache 2.0", "GPL v3", "BSD", "Creative Commons"])
        form_layout.addRow("License:", self.license_combo)
        
        layout.addWidget(form_group)
        
        # Documentation section
        doc_group = QGroupBox("Documentation (Optional)")
        doc_layout = QVBoxLayout(doc_group)
        
        self.documentation_edit = QTextEdit()
        self.documentation_edit.setMaximumHeight(150)
        self.documentation_edit.setPlaceholderText(
            "Provide additional documentation, usage examples, or setup instructions"
        )
        doc_layout.addWidget(self.documentation_edit)
        
        layout.addWidget(doc_group)
        
        # Preview section
        preview_group = QGroupBox("YAML Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.yaml_preview = QTextEdit()
        self.yaml_preview.setReadOnly(True)
        self.yaml_preview.setMaximumHeight(200)
        self.yaml_preview.setFont(QFont("Consolas", 10))
        
        # Generate YAML preview
        yaml_content = generate_yaml_string(self.workflow, "community_template")
        self.yaml_preview.setPlainText(yaml_content)
        
        preview_layout.addWidget(self.yaml_preview)
        layout.addWidget(preview_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_template(self) -> CommunityTemplate:
        """Get the template object from the form data."""
        tags = [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()]
        
        return CommunityTemplate(
            id="",  # Will be generated by repository
            name=self.name_edit.text(),
            description=self.description_edit.toPlainText(),
            author=self.author_edit.text(),
            author_email=self.email_edit.text(),
            category=self.category_combo.currentText(),
            tags=tags,
            difficulty=self.difficulty_combo.currentText(),
            workflow_yaml=self.yaml_preview.toPlainText(),
            license=self.license_combo.currentText(),
            documentation=self.documentation_edit.toPlainText()
        )


class TemplateRatingDialog(QDialog):
    """Dialog for rating and reviewing templates."""
    
    def __init__(self, template: CommunityTemplate, parent=None):
        super().__init__(parent)
        self.template = template
        self.setWindowTitle(f"Rate Template: {template.name}")
        self.setModal(True)
        self.resize(400, 300)
        self.setupUI()
    
    def setupUI(self):
        """Set up the rating dialog UI."""
        layout = QVBoxLayout(self)
        
        # Template info
        info_label = QLabel(f"<b>{self.template.name}</b><br>{self.template.description}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Rating
        rating_group = QGroupBox("Your Rating")
        rating_layout = QVBoxLayout(rating_group)
        
        self.rating_slider = QSlider(Qt.Horizontal)
        self.rating_slider.setRange(1, 5)
        self.rating_slider.setValue(5)
        self.rating_slider.setTickPosition(QSlider.TicksBelow)
        self.rating_slider.setTickInterval(1)
        
        self.rating_label = QLabel("5 stars")
        self.rating_slider.valueChanged.connect(
            lambda v: self.rating_label.setText(f"{v} star{'s' if v != 1 else ''}")
        )
        
        rating_layout.addWidget(self.rating_slider)
        rating_layout.addWidget(self.rating_label)
        layout.addWidget(rating_group)
        
        # Review
        review_group = QGroupBox("Review (Optional)")
        review_layout = QVBoxLayout(review_group)
        
        self.review_edit = QTextEdit()
        self.review_edit.setPlaceholderText("Share your experience with this template...")
        self.review_edit.setMaximumHeight(150)
        review_layout.addWidget(self.review_edit)
        
        layout.addWidget(review_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_rating(self) -> Tuple[int, str]:
        """Get the rating and review."""
        return self.rating_slider.value(), self.review_edit.toPlainText()


class CommunityTemplateMarketplace(QWidget):
    """Main widget for the community template marketplace."""
    
    template_downloaded = Signal(str)  # Emits template ID when downloaded
    template_applied = Signal(object)  # Emits CommunityTemplate when applied
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repository = TemplateRepository()
        self.current_user_id = "user123"  # Would be from authentication
        self.initUI()
        self._populate_sample_templates()
    
    def initUI(self):
        """Initialize the marketplace UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Apply modern styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            }
            QGroupBox {
                font-weight: 600;
                color: #2c3e50;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #e1e8ed;
                background-color: #ffffff;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e1e8ed;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #4a86e8;
            }
        """)
        
        # Header
        header_label = QLabel("🌐 Community Template Marketplace")
        header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 12px;
            background-color: #e3f2fd;
            border-radius: 8px;
            border: 2px solid #4a86e8;
        """)
        layout.addWidget(header_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Browse tab
        self.browse_tab = self._create_browse_tab()
        self.tab_widget.addTab(self.browse_tab, "🔍 Browse")
        
        # Popular tab
        self.popular_tab = self._create_popular_tab()
        self.tab_widget.addTab(self.popular_tab, "🔥 Popular")
        
        # My Templates tab
        self.my_templates_tab = self._create_my_templates_tab()
        self.tab_widget.addTab(self.my_templates_tab, "📁 My Templates")
        
        # Submit tab
        self.submit_tab = self._create_submit_tab()
        self.tab_widget.addTab(self.submit_tab, "📤 Submit")
        
        layout.addWidget(self.tab_widget)
    
    def _create_browse_tab(self) -> QWidget:
        """Create the browse templates tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search and filters
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search templates...")
        self.search_edit.textChanged.connect(self._search_templates)
        search_layout.addWidget(self.search_edit)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "User Management", "Communication", 
                                     "Approvals", "IT Service Management", "Data Processing"])
        self.category_filter.currentTextChanged.connect(self._search_templates)
        search_layout.addWidget(self.category_filter)
        
        self.difficulty_filter = QComboBox()
        self.difficulty_filter.addItems(["All Levels", "beginner", "intermediate", "advanced"])
        self.difficulty_filter.currentTextChanged.connect(self._search_templates)
        search_layout.addWidget(self.difficulty_filter)
        
        layout.addLayout(search_layout)
        
        # Results list
        self.templates_list = QListWidget()
        self.templates_list.itemDoubleClicked.connect(self._on_template_selected)
        layout.addWidget(self.templates_list)
        
        # Template details
        self.template_details = QTextEdit()
        self.template_details.setReadOnly(True)
        self.template_details.setMaximumHeight(150)
        layout.addWidget(self.template_details)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("📥 Download")
        self.download_btn.clicked.connect(self._download_template)
        self.download_btn.setEnabled(False)
        button_layout.addWidget(self.download_btn)
        
        self.apply_btn = QPushButton("✅ Apply Template")
        self.apply_btn.clicked.connect(self._apply_template)
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)
        
        self.rate_btn = QPushButton("⭐ Rate")
        self.rate_btn.clicked.connect(self._rate_template)
        self.rate_btn.setEnabled(False)
        button_layout.addWidget(self.rate_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_popular_tab(self) -> QWidget:
        """Create the popular templates tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Popular templates list
        self.popular_list = QListWidget()
        layout.addWidget(self.popular_list)
        
        return widget
    
    def _create_my_templates_tab(self) -> QWidget:
        """Create the my templates tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # My templates list
        self.my_templates_list = QListWidget()
        layout.addWidget(self.my_templates_list)
        
        return widget
    
    def _create_submit_tab(self) -> QWidget:
        """Create the submit template tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel("""
        <h3>Share Your Template with the Community</h3>
        <p>Help other users by sharing your workflow templates. Your contributions make the community stronger!</p>
        
        <p><b>Guidelines:</b></p>
        <ul>
        <li>Ensure your template follows Moveworks best practices</li>
        <li>Provide clear descriptions and documentation</li>
        <li>Test your template thoroughly before submitting</li>
        <li>Use appropriate tags and categories</li>
        </ul>
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 16px; background-color: #f0f8ff; border-radius: 8px;")
        layout.addWidget(instructions)
        
        # Submit button
        submit_btn = QPushButton("📤 Submit Current Workflow as Template")
        submit_btn.clicked.connect(self._submit_template)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(submit_btn)
        
        layout.addStretch()
        return widget
    
    def _populate_sample_templates(self):
        """Populate with sample templates for demonstration."""
        sample_templates = [
            CommunityTemplate(
                id="sample1",
                name="User Onboarding Workflow",
                description="Complete user onboarding process with notifications and approvals",
                author="John Doe",
                author_email="john@example.com",
                category="User Management",
                tags=["onboarding", "user", "approval", "notification"],
                difficulty="intermediate",
                workflow_yaml="action_name: user_onboarding\nsteps:\n  - action:\n      action_name: mw.create_user",
                downloads=156,
                rating=4.5,
                rating_count=23
            ),
            CommunityTemplate(
                id="sample2",
                name="IT Ticket Creation",
                description="Automated IT ticket creation with priority assignment",
                author="Jane Smith",
                author_email="jane@example.com",
                category="IT Service Management",
                tags=["ticket", "it", "automation"],
                difficulty="beginner",
                workflow_yaml="action_name: create_ticket\nsteps:\n  - action:\n      action_name: servicenow.create_incident",
                downloads=89,
                rating=4.2,
                rating_count=15
            )
        ]
        
        for template in sample_templates:
            self.repository.templates[template.id] = template
        
        self._refresh_all_lists()
    
    def _search_templates(self):
        """Search and filter templates."""
        query = self.search_edit.text()
        category = self.category_filter.currentText()
        difficulty = self.difficulty_filter.currentText()
        
        # Apply filters
        category_filter = None if category == "All Categories" else category
        difficulty_filter = None if difficulty == "All Levels" else difficulty
        
        results = self.repository.search_templates(
            query=query,
            category=category_filter,
            difficulty=difficulty_filter
        )
        
        # Update list
        self.templates_list.clear()
        for template in results:
            item = QListWidgetItem()
            item_text = f"{template.name}\n{template.description[:100]}...\n"
            item_text += f"⭐ {template.rating:.1f} ({template.rating_count}) | "
            item_text += f"📥 {template.downloads} | {template.difficulty}"
            item.setText(item_text)
            item.setData(Qt.UserRole, template)
            self.templates_list.addItem(item)
    
    def _refresh_all_lists(self):
        """Refresh all template lists."""
        self._search_templates()
        
        # Update popular list
        self.popular_list.clear()
        popular = self.repository.get_popular_templates(10)
        for template in popular:
            item = QListWidgetItem(f"{template.name} (⭐ {template.rating:.1f}, 📥 {template.downloads})")
            item.setData(Qt.UserRole, template)
            self.popular_list.addItem(item)
    
    def _on_template_selected(self, item):
        """Handle template selection."""
        template = item.data(Qt.UserRole)
        if template:
            # Show template details
            details = f"""
<h3>{template.name}</h3>
<p><b>Author:</b> {template.author}</p>
<p><b>Category:</b> {template.category}</p>
<p><b>Difficulty:</b> {template.difficulty}</p>
<p><b>Tags:</b> {', '.join(template.tags)}</p>
<p><b>Rating:</b> ⭐ {template.rating:.1f} ({template.rating_count} reviews)</p>
<p><b>Downloads:</b> {template.downloads}</p>
<p><b>Description:</b></p>
<p>{template.description}</p>
            """.strip()
            
            self.template_details.setHtml(details)
            
            # Enable action buttons
            self.download_btn.setEnabled(True)
            self.apply_btn.setEnabled(True)
            self.rate_btn.setEnabled(True)
            
            # Store current selection
            self.current_template = template
    
    def _download_template(self):
        """Download the selected template."""
        if hasattr(self, 'current_template'):
            success = self.repository.download_template(self.current_template.id)
            if success:
                QMessageBox.information(self, "Success", "Template downloaded successfully!")
                self.template_downloaded.emit(self.current_template.id)
                self._refresh_all_lists()
            else:
                QMessageBox.warning(self, "Error", "Failed to download template.")
    
    def _apply_template(self):
        """Apply the selected template."""
        if hasattr(self, 'current_template'):
            self.template_applied.emit(self.current_template)
    
    def _rate_template(self):
        """Rate the selected template."""
        if hasattr(self, 'current_template'):
            dialog = TemplateRatingDialog(self.current_template, self)
            if dialog.exec() == QDialog.Accepted:
                rating, review = dialog.get_rating()
                success = self.repository.rate_template(
                    self.current_template.id, rating, review, self.current_user_id
                )
                if success:
                    QMessageBox.information(self, "Success", "Thank you for your rating!")
                    self._refresh_all_lists()
    
    def _submit_template(self):
        """Submit a new template."""
        # This would get the current workflow from the main application
        # For now, create a dummy workflow
        from core_structures import Workflow
        workflow = Workflow()
        
        dialog = TemplateSubmissionDialog(workflow, self)
        if dialog.exec() == QDialog.Accepted:
            template = dialog.get_template()
            success = self.repository.submit_template(template)
            if success:
                QMessageBox.information(self, "Success", 
                                      "Template submitted successfully! It will be reviewed before publication.")
                self._refresh_all_lists()
            else:
                QMessageBox.warning(self, "Error", "Failed to submit template.")
