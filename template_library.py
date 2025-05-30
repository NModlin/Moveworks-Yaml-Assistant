"""
Template Library System for the Moveworks YAML Assistant.

This module provides workflow templates to help users get started quickly.
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QTextEdit, QWidget, QSplitter, QGroupBox, QLineEdit,
    QComboBox, QFileDialog, QMessageBox, QTabWidget, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, SwitchCase, DefaultCase,
    ForLoopStep, ParallelStep, ParallelBranch, ParallelForLoop, ReturnStep,
    RaiseStep, TryCatchStep, CatchBlock
)


@dataclass
class WorkflowTemplate:
    """Represents a workflow template with metadata."""
    name: str
    description: str
    category: str
    difficulty: str  # Beginner, Intermediate, Advanced
    tags: List[str]
    workflow: Workflow
    author: str = "System"
    version: str = "1.0"
    created_date: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "author": self.author,
            "version": self.version,
            "created_date": self.created_date,
            "workflow": {
                "steps": [asdict(step) for step in self.workflow.steps]
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowTemplate':
        """Create template from dictionary."""
        # Reconstruct workflow steps
        steps = []
        for step_data in data.get("workflow", {}).get("steps", []):
            # Determine step type and create appropriate instance
            if "action_name" in step_data:
                steps.append(ActionStep(**step_data))
            elif "code" in step_data:
                steps.append(ScriptStep(**step_data))
            # Note: For complex step types (switch, for, parallel, etc.),
            # we would need more sophisticated reconstruction logic.
            # For now, we'll handle the basic types that are most commonly saved.

        workflow = Workflow(steps=steps)

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", "General"),
            difficulty=data.get("difficulty", "Beginner"),
            tags=data.get("tags", []),
            author=data.get("author", "System"),
            version=data.get("version", "1.0"),
            created_date=data.get("created_date", ""),
            workflow=workflow
        )


class TemplateLibrary:
    """Manages workflow templates."""

    def __init__(self):
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.templates_dir = "templates"
        self._ensure_templates_dir()
        self._load_builtin_templates()
        self._load_user_templates()

    def _ensure_templates_dir(self):
        """Ensure templates directory exists."""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)

    def _load_builtin_templates(self):
        """Load built-in workflow templates."""
        # User Lookup Template
        user_lookup_workflow = Workflow(steps=[
            ActionStep(
                action_name="mw.get_user_by_email",
                output_key="user_info",
                description="Look up user information by email address",
                input_args={"email": "data.input_email"},
                user_provided_json_output='{"user": {"id": "12345", "name": "John Doe", "email": "john.doe@company.com", "department": "Engineering"}}'
            ),
            ScriptStep(
                code="""
# Process user information
user = data.user_info.user
result = {
    "user_found": True,
    "display_name": user.name,
    "department": user.department,
    "user_id": user.id
}
return result
                """.strip(),
                output_key="processed_user",
                description="Process and format user information",
                user_provided_json_output='{"user_found": true, "display_name": "John Doe", "department": "Engineering", "user_id": "12345"}'
            )
        ])

        user_lookup_template = WorkflowTemplate(
            name="User Lookup",
            description="Look up and process user information by email address. Perfect for user verification workflows.",
            category="User Management",
            difficulty="Beginner",
            tags=["user", "lookup", "email", "basic"],
            workflow=user_lookup_workflow
        )

        # Ticket Creation Template
        ticket_creation_workflow = Workflow(steps=[
            ActionStep(
                action_name="mw.get_user_by_email",
                output_key="requestor_info",
                description="Get requestor information",
                input_args={"email": "data.requestor_email"},
                user_provided_json_output='{"user": {"id": "12345", "name": "John Doe", "email": "john.doe@company.com"}}'
            ),
            ActionStep(
                action_name="servicenow.create_incident",
                output_key="ticket_result",
                description="Create ServiceNow incident ticket",
                input_args={
                    "short_description": "data.issue_summary",
                    "description": "data.issue_details",
                    "caller_id": "data.requestor_info.user.id",
                    "urgency": "3",
                    "impact": "3"
                },
                user_provided_json_output='{"ticket": {"number": "INC0012345", "sys_id": "abc123", "state": "New"}}'
            ),
            ScriptStep(
                code="""
# Format ticket response
ticket = data.ticket_result.ticket
requestor = data.requestor_info.user

response = {
    "success": True,
    "ticket_number": ticket.number,
    "message": f"Ticket {ticket.number} created successfully for {requestor.name}",
    "ticket_url": f"https://company.service-now.com/nav_to.do?uri=incident.do?sys_id={ticket.sys_id}"
}
return response
                """.strip(),
                output_key="final_response",
                description="Format the ticket creation response",
                user_provided_json_output='{"success": true, "ticket_number": "INC0012345", "message": "Ticket INC0012345 created successfully for John Doe", "ticket_url": "https://company.service-now.com/nav_to.do?uri=incident.do?sys_id=abc123"}'
            )
        ])

        ticket_creation_template = WorkflowTemplate(
            name="Ticket Creation",
            description="Create a ServiceNow incident ticket with user lookup and response formatting.",
            category="IT Service Management",
            difficulty="Intermediate",
            tags=["ticket", "servicenow", "incident", "itsm"],
            workflow=ticket_creation_workflow
        )

        # Error Handling Template
        error_handling_workflow = Workflow(steps=[
            ActionStep(
                action_name="mw.get_user_by_email",
                output_key="user_lookup",
                description="Attempt to look up user",
                input_args={"email": "data.user_email"},
                user_provided_json_output='{"user": {"id": "12345", "name": "John Doe"}, "error": null}'
            ),
            ScriptStep(
                code="""
# Check if user lookup was successful
if hasattr(data.user_lookup, 'error') and data.user_lookup.error:
    return {
        "success": False,
        "error_type": "user_not_found",
        "message": "User not found with the provided email address",
        "suggested_action": "Please verify the email address and try again"
    }
elif hasattr(data.user_lookup, 'user') and data.user_lookup.user:
    return {
        "success": True,
        "user_id": data.user_lookup.user.id,
        "user_name": data.user_lookup.user.name,
        "message": "User found successfully"
    }
else:
    return {
        "success": False,
        "error_type": "unexpected_response",
        "message": "Unexpected response format from user lookup",
        "suggested_action": "Please contact support"
    }
                """.strip(),
                output_key="validation_result",
                description="Validate user lookup result and handle errors",
                user_provided_json_output='{"success": true, "user_id": "12345", "user_name": "John Doe", "message": "User found successfully"}'
            )
        ])

        error_handling_template = WorkflowTemplate(
            name="Error Handling Pattern",
            description="Demonstrates proper error handling and validation patterns in workflows.",
            category="Best Practices",
            difficulty="Advanced",
            tags=["error", "validation", "patterns", "best-practices"],
            workflow=error_handling_workflow
        )

        # Switch Statement Template
        switch_workflow = Workflow(steps=[
            ActionStep(
                action_name="mw.get_user_by_email",
                output_key="user_info",
                description="Get user information",
                input_args={"email": "data.user_email"},
                user_provided_json_output='{"user": {"id": "12345", "access_level": "admin", "status": "active"}}'
            ),
            SwitchStep(
                description="Handle user based on access level",
                cases=[
                    SwitchCase(
                        condition="data.user_info.user.access_level == 'admin'",
                        steps=[
                            ActionStep(
                                action_name="send_admin_welcome",
                                output_key="admin_welcome_notification",
                                input_args={
                                    "user_id": "data.user_info.user.id",
                                    "message": "Welcome, Admin! You have full access to the admin dashboard."
                                }
                            )
                        ]
                    ),
                    SwitchCase(
                        condition="data.user_info.user.access_level == 'member'",
                        steps=[
                            ActionStep(
                                action_name="send_member_welcome",
                                output_key="member_welcome_notification",
                                input_args={
                                    "user_id": "data.user_info.user.id",
                                    "message": "Welcome, Member! Explore your member benefits in your profile."
                                }
                            )
                        ]
                    )
                ],
                default_case=DefaultCase(
                    steps=[
                        ActionStep(
                            action_name="send_generic_access_notification",
                            output_key="generic_access_notification",
                            input_args={
                                "user_id": "data.user_info.user.id",
                                "message": "You're set! Start exploring your new account."
                            }
                        )
                    ]
                )
            )
        ])

        switch_template = WorkflowTemplate(
            name="Switch Statement Pattern",
            description="Demonstrates conditional logic using switch statements with multiple cases and default handling.",
            category="Control Flow",
            difficulty="Intermediate",
            tags=["switch", "conditional", "control-flow", "user-management"],
            workflow=switch_workflow
        )

        # For Loop Template
        for_loop_workflow = Workflow(steps=[
            ActionStep(
                action_name="get_user_list",
                output_key="users",
                description="Get list of users to process",
                input_args={"department": "data.department"},
                user_provided_json_output='[{"id": "user1", "age": 35}, {"id": "user2", "age": 42}, {"id": "user3", "age": 29}]'
            ),
            ForLoopStep(
                description="Process each user and adjust their age",
                each="user",
                index="user_index",
                in_source="data.users",
                output_key="adjusted_ages_notifications",
                steps=[
                    ScriptStep(
                        code="user['age'] - 10",
                        input_args={"user": "user"},
                        output_key="adjusted_age",
                        description="Calculate adjusted age"
                    ),
                    ActionStep(
                        action_name="send_age_adjustment_notification",
                        output_key="age_notification",
                        input_args={
                            "user_id": "user.id",
                            "message": "Your adjusted age is {adjusted_age}"
                        },
                        description="Send notification with adjusted age"
                    )
                ]
            )
        ])

        for_loop_template = WorkflowTemplate(
            name="For Loop Processing",
            description="Demonstrates iterating over collections with for loops, processing each item with multiple steps.",
            category="Control Flow",
            difficulty="Intermediate",
            tags=["for-loop", "iteration", "data-processing", "bulk-operations"],
            workflow=for_loop_workflow
        )

        # Parallel Processing Template
        parallel_workflow = Workflow(steps=[
            ParallelStep(
                description="Run multiple independent actions in parallel",
                branches=[
                    ParallelBranch(
                        name="logging_branch",
                        steps=[
                            ActionStep(
                                action_name="log_event",
                                output_key="log_result",
                                input_args={"event_name": "user_login"}
                            )
                        ]
                    ),
                    ParallelBranch(
                        name="notification_branch",
                        steps=[
                            ActionStep(
                                action_name="send_email",
                                output_key="email_result",
                                input_args={
                                    "email": "data.requestor_email",
                                    "subject": "Login Notification",
                                    "body": "You have logged in successfully."
                                }
                            )
                        ]
                    )
                ]
            )
        ])

        parallel_template = WorkflowTemplate(
            name="Parallel Processing",
            description="Demonstrates running multiple independent actions concurrently for improved performance.",
            category="Control Flow",
            difficulty="Advanced",
            tags=["parallel", "concurrent", "performance", "branches"],
            workflow=parallel_workflow
        )

        # Try-Catch Error Handling Template
        try_catch_workflow = Workflow(steps=[
            TryCatchStep(
                description="Handle potential action failure with error recovery",
                try_steps=[
                    ActionStep(
                        action_name="may_fail_action",
                        output_key="action_result",
                        description="Action that might fail"
                    )
                ],
                catch_block=CatchBlock(
                    on_status_code=["E400"],
                    steps=[
                        ActionStep(
                            action_name="notify_admin",
                            output_key="notify_admin_output",
                            input_args={
                                "message": "That flakey action is failing again",
                                "error": "error_data.action_result"
                            }
                        ),
                        RaiseStep(
                            output_key="raised_error",
                            message="The action has failed. The IT team is aware this is failing for some cases, please be patient."
                        )
                    ]
                )
            )
        ])

        try_catch_template = WorkflowTemplate(
            name="Try-Catch Error Handling",
            description="Demonstrates robust error handling with try-catch blocks and specific error code handling.",
            category="Error Handling",
            difficulty="Advanced",
            tags=["try-catch", "error-handling", "resilience", "recovery"],
            workflow=try_catch_workflow
        )

        # Return Statement Template
        return_workflow = Workflow(steps=[
            ActionStep(
                action_name="get_user_list",
                output_key="users",
                description="Get list of users",
                user_provided_json_output='[{"id": "user1", "name": "alice", "age": 30}, {"id": "user2", "name": "bob", "age": 25}]'
            ),
            ReturnStep(
                description="Return formatted user data",
                output_mapper={
                    "MAP()": {
                        "converter": {
                            "id": "item.id",
                            "name": "item.name.$TITLECASE()"
                        },
                        "items": "data.users"
                    }
                }
            )
        ])

        return_template = WorkflowTemplate(
            name="Return Statement with Data Mapping",
            description="Demonstrates returning structured data with advanced mapping and transformation functions.",
            category="Data Processing",
            difficulty="Intermediate",
            tags=["return", "data-mapping", "transformation", "output"],
            workflow=return_workflow
        )

        # Add templates to library
        self.templates["user_lookup"] = user_lookup_template
        self.templates["ticket_creation"] = ticket_creation_template
        self.templates["error_handling"] = error_handling_template
        self.templates["switch_statement"] = switch_template
        self.templates["for_loop_processing"] = for_loop_template
        self.templates["parallel_processing"] = parallel_template
        self.templates["try_catch_handling"] = try_catch_template
        self.templates["return_data_mapping"] = return_template

    def _load_user_templates(self):
        """Load user-created templates from files."""
        if not os.path.exists(self.templates_dir):
            return

        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.templates_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    template = WorkflowTemplate.from_dict(data)
                    template_id = filename[:-5]  # Remove .json extension
                    self.templates[template_id] = template
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")

    def save_template(self, template_id: str, template: WorkflowTemplate) -> bool:
        """Save a template to file."""
        try:
            filepath = os.path.join(self.templates_dir, f"{template_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2)

            self.templates[template_id] = template
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        try:
            filepath = os.path.join(self.templates_dir, f"{template_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)

            if template_id in self.templates:
                del self.templates[template_id]
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False

    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def get_templates_by_category(self, category: str) -> List[WorkflowTemplate]:
        """Get all templates in a category."""
        return [t for t in self.templates.values() if t.category == category]

    def get_all_categories(self) -> List[str]:
        """Get all template categories."""
        categories = set(t.category for t in self.templates.values())
        return sorted(list(categories))

    def search_templates(self, query: str) -> List[WorkflowTemplate]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []

        for template in self.templates.values():
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)

        return results

    def export_template(self, template_id: str, filepath: str) -> bool:
        """Export a template to a file."""
        template = self.get_template(template_id)
        if not template:
            return False

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting template: {e}")
            return False

    def import_template(self, filepath: str) -> Optional[str]:
        """Import a template from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            template = WorkflowTemplate.from_dict(data)

            # Generate unique ID
            base_id = template.name.lower().replace(' ', '_')
            template_id = base_id
            counter = 1
            while template_id in self.templates:
                template_id = f"{base_id}_{counter}"
                counter += 1

            self.save_template(template_id, template)
            return template_id
        except Exception as e:
            print(f"Error importing template: {e}")
            return None


class TemplateBrowserDialog(QDialog):
    """Dialog for browsing and selecting workflow templates."""

    template_selected = Signal(str)  # Emits template ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Library")
        self.setModal(True)
        self.resize(800, 600)

        self.library = template_library
        self._setup_ui()
        self._load_templates()

    def _setup_ui(self):
        """Setup the template browser UI."""
        layout = QVBoxLayout(self)

        # Header with search
        header_layout = QHBoxLayout()

        header_label = QLabel("Workflow Templates")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search templates...")
        self.search_edit.textChanged.connect(self._filter_templates)
        header_layout.addWidget(self.search_edit)

        layout.addLayout(header_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel: Categories and templates
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))

        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.currentTextChanged.connect(self._filter_templates)
        category_layout.addWidget(self.category_combo)

        left_layout.addLayout(category_layout)

        # Template list
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self._on_template_selection_changed)
        left_layout.addWidget(self.template_list)

        splitter.addWidget(left_panel)

        # Right panel: Template details and preview
        right_panel = QTabWidget()

        # Details tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        self.template_title = QLabel()
        self.template_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        details_layout.addWidget(self.template_title)

        self.template_description = QTextEdit()
        self.template_description.setReadOnly(True)
        self.template_description.setMaximumHeight(100)
        details_layout.addWidget(self.template_description)

        # Metadata
        metadata_group = QGroupBox("Template Information")
        metadata_layout = QVBoxLayout(metadata_group)

        self.metadata_labels = {}
        for field in ["Category", "Difficulty", "Author", "Tags"]:
            label = QLabel()
            self.metadata_labels[field] = label
            metadata_layout.addWidget(label)

        details_layout.addWidget(metadata_group)
        details_layout.addStretch()

        right_panel.addTab(details_widget, "Details")

        # Preview tab
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        self.workflow_preview = QTreeWidget()
        self.workflow_preview.setHeaderLabels(["Step", "Type", "Details"])
        preview_layout.addWidget(self.workflow_preview)

        right_panel.addTab(preview_widget, "Workflow Preview")

        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])

        # Buttons
        button_layout = QHBoxLayout()

        self.use_template_btn = QPushButton("Use Template")
        self.use_template_btn.clicked.connect(self._use_selected_template)
        self.use_template_btn.setEnabled(False)
        button_layout.addWidget(self.use_template_btn)

        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_template)
        button_layout.addWidget(export_btn)

        import_btn = QPushButton("Import...")
        import_btn.clicked.connect(self._import_template)
        button_layout.addWidget(import_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _load_templates(self):
        """Load templates into the UI."""
        # Load categories
        categories = self.library.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category)

        # Load all templates
        self._filter_templates()

    def _filter_templates(self):
        """Filter templates based on search and category."""
        self.template_list.clear()

        search_text = self.search_edit.text().strip()
        selected_category = self.category_combo.currentText()

        # Get templates to show
        if search_text:
            templates = self.library.search_templates(search_text)
        else:
            templates = list(self.library.templates.values())

        # Filter by category
        if selected_category != "All Categories":
            templates = [t for t in templates if t.category == selected_category]

        # Add to list
        for template in templates:
            item = QListWidgetItem(f"{template.name} ({template.difficulty})")
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)

    def _on_template_selection_changed(self, current, previous):
        """Handle template selection change."""
        if current:
            template = current.data(Qt.UserRole)
            self._show_template_details(template)
            self.use_template_btn.setEnabled(True)
        else:
            self.use_template_btn.setEnabled(False)

    def _show_template_details(self, template: WorkflowTemplate):
        """Show details for the selected template."""
        self.template_title.setText(template.name)
        self.template_description.setPlainText(template.description)

        # Update metadata
        self.metadata_labels["Category"].setText(f"Category: {template.category}")
        self.metadata_labels["Difficulty"].setText(f"Difficulty: {template.difficulty}")
        self.metadata_labels["Author"].setText(f"Author: {template.author}")
        self.metadata_labels["Tags"].setText(f"Tags: {', '.join(template.tags)}")

        # Update workflow preview
        self.workflow_preview.clear()
        for i, step in enumerate(template.workflow.steps):
            item = QTreeWidgetItem([
                f"Step {i+1}",
                type(step).__name__,
                getattr(step, 'description', '') or getattr(step, 'action_name', '') or 'Script Step'
            ])
            self.workflow_preview.addTopLevelItem(item)

    def _use_selected_template(self):
        """Use the selected template."""
        current_item = self.template_list.currentItem()
        if current_item:
            template = current_item.data(Qt.UserRole)
            # Find template ID
            for template_id, t in self.library.templates.items():
                if t == template:
                    self.template_selected.emit(template_id)
                    self.accept()
                    break

    def _export_template(self):
        """Export the selected template."""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template to export.")
            return

        template = current_item.data(Qt.UserRole)
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Template", f"{template.name}.json", "JSON Files (*.json)"
        )

        if filename:
            # Find template ID
            for template_id, t in self.library.templates.items():
                if t == template:
                    if self.library.export_template(template_id, filename):
                        QMessageBox.information(self, "Success", "Template exported successfully!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to export template.")
                    break

    def _import_template(self):
        """Import a template from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Template", "", "JSON Files (*.json)"
        )

        if filename:
            template_id = self.library.import_template(filename)
            if template_id:
                QMessageBox.information(self, "Success", "Template imported successfully!")
                self._load_templates()
            else:
                QMessageBox.critical(self, "Error", "Failed to import template.")


# Global template library instance
template_library = TemplateLibrary()
