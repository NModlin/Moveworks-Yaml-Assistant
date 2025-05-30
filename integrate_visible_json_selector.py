#!/usr/bin/env python3
"""
Integration script for the more visible JSON Path Selector Dialog.

This script demonstrates how to integrate the enhanced, easily visible
JSON Path Selector dialog into the main Moveworks YAML Assistant application.
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PySide6.QtCore import Qt

# Import our components
from json_path_selector_dialog import JsonPathSelectorDialog
from enhanced_json_selector import VisualDesignConstants
from core_structures import Workflow, ActionStep, ScriptStep

logger = logging.getLogger(__name__)


class MainApplicationDemo(QMainWindow):
    """
    Demo of how to integrate the visible JSON Path Selector dialog
    into the main application workflow.
    """
    
    def __init__(self):
        super().__init__()
        self.workflow = None
        self.selected_paths = []
        
        self.setWindowTitle("Moveworks YAML Assistant - Enhanced JSON Path Selection")
        self.setGeometry(100, 100, 800, 600)
        
        self._setup_ui()
        self._create_sample_workflow()
    
    def _setup_ui(self):
        """Setup the main application UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Apply consistent styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
            }}
        """)
        
        # Header
        header = QLabel("🎯 Enhanced JSON Path Selection Integration")
        header.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {VisualDesignConstants.ACCENT_COLOR};
                background-color: white;
                border: 2px solid {VisualDesignConstants.ACCENT_COLOR};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                text-align: center;
            }}
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel(
            "This demo shows how the enhanced JSON Path Selector dialog integrates "
            "into the main application. Click the button below to open the large, "
            "easily visible JSON Path Selector dialog."
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                color: #666;
                padding: 15px;
                background-color: #f0f8ff;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Open dialog button
        self.open_dialog_btn = QPushButton("🔍 Open JSON Path Selector Dialog")
        self.open_dialog_btn.clicked.connect(self._open_json_path_dialog)
        self.open_dialog_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: #1976d2;
            }}
            QPushButton:pressed {{
                background-color: #0d47a1;
            }}
        """)
        layout.addWidget(self.open_dialog_btn)
        
        # Selected paths display
        paths_group = QLabel("📋 Selected Paths")
        paths_group.setStyleSheet(f"""
            QLabel {{
                font-size: {VisualDesignConstants.HEADER_FONT_SIZE};
                font-weight: bold;
                color: #333;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(paths_group)
        
        self.paths_display = QTextEdit()
        self.paths_display.setReadOnly(True)
        self.paths_display.setPlaceholderText("Selected JSON paths will appear here...")
        self.paths_display.setStyleSheet(f"""
            QTextEdit {{
                font-family: {VisualDesignConstants.MONOSPACE_FONT};
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                background-color: white;
                border: 2px solid {VisualDesignConstants.SUBTLE_BORDER};
                border-radius: 6px;
                padding: 15px;
                min-height: 200px;
            }}
        """)
        layout.addWidget(self.paths_display)
        
        # Status display
        self.status_label = QLabel("Ready - Click the button above to select JSON paths")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {VisualDesignConstants.ACCENT_COLOR};
                font-style: italic;
                padding: 10px;
                background-color: {VisualDesignConstants.HOVER_BACKGROUND};
                border-radius: 4px;
                margin-top: 10px;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear Selected Paths")
        clear_btn.clicked.connect(self._clear_paths)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.WARNING_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: {VisualDesignConstants.BODY_FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #f57c00;
            }}
        """)
        layout.addWidget(clear_btn)
    
    def _create_sample_workflow(self):
        """Create a sample workflow with JSON data."""
        self.workflow = Workflow()
        
        # User lookup step
        user_step = ActionStep(
            name="lookup_user",
            action_name="user_lookup",
            description="Look up user information",
            output_key="user_data"
        )
        user_step.parsed_json_output = {
            "user": {
                "id": "12345",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "manager": {
                    "name": "Jane Smith",
                    "email": "jane.smith@company.com",
                    "id": "67890"
                },
                "location": "San Francisco",
                "permissions": ["read", "write", "admin"],
                "last_login": "2024-01-15T10:30:00Z"
            },
            "metadata": {
                "query_time": "2024-01-15T11:00:00Z",
                "source": "active_directory",
                "confidence": 0.95
            }
        }
        self.workflow.add_step(user_step)
        
        # Ticket processing step
        ticket_step = ScriptStep(
            name="process_tickets",
            description="Process user tickets",
            output_key="ticket_data"
        )
        ticket_step.parsed_json_output = {
            "tickets": [
                {
                    "id": "TKT-001",
                    "title": "Password Reset Request",
                    "status": "open",
                    "priority": "high",
                    "assignee": {
                        "name": "Support Team",
                        "email": "support@company.com",
                        "team": "IT Support"
                    },
                    "created_date": "2024-01-15T09:00:00Z",
                    "tags": ["password", "urgent", "security"]
                },
                {
                    "id": "TKT-002",
                    "title": "Access Request",
                    "status": "closed",
                    "priority": "medium",
                    "assignee": {
                        "name": "IT Admin",
                        "email": "itadmin@company.com",
                        "team": "IT Administration"
                    },
                    "created_date": "2024-01-14T14:30:00Z",
                    "tags": ["access", "permissions"]
                }
            ],
            "summary": {
                "total_count": 2,
                "status_breakdown": {
                    "open": 1,
                    "closed": 1,
                    "in_progress": 0
                },
                "priority_breakdown": {
                    "high": 1,
                    "medium": 1,
                    "low": 0
                }
            }
        }
        self.workflow.add_step(ticket_step)
    
    def _open_json_path_dialog(self):
        """Open the JSON Path Selector dialog."""
        dialog = JsonPathSelectorDialog(self, self.workflow)
        dialog.path_selected.connect(self._on_path_selected)
        
        # Show the dialog
        result = dialog.exec()
        
        if result == JsonPathSelectorDialog.Accepted:
            selected_path = dialog.get_selected_path()
            if selected_path:
                self._add_selected_path(selected_path)
                self.status_label.setText(f"✅ Added path: {selected_path}")
            else:
                self.status_label.setText("⚠️ No path was selected")
        else:
            self.status_label.setText("❌ Dialog was cancelled")
    
    def _on_path_selected(self, path):
        """Handle path selection from dialog."""
        logger.debug(f"Path selected in dialog: {path}")
    
    def _add_selected_path(self, path):
        """Add a selected path to the display."""
        if path not in self.selected_paths:
            self.selected_paths.append(path)
            self._update_paths_display()
    
    def _update_paths_display(self):
        """Update the paths display."""
        if self.selected_paths:
            paths_text = "\n".join([f"• {path}" for path in self.selected_paths])
            self.paths_display.setPlainText(paths_text)
        else:
            self.paths_display.clear()
    
    def _clear_paths(self):
        """Clear all selected paths."""
        self.selected_paths.clear()
        self.paths_display.clear()
        self.status_label.setText("🗑️ Cleared all selected paths")


def main():
    """Run the integration demo."""
    app = QApplication(sys.argv)
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create and show the demo
    demo = MainApplicationDemo()
    demo.show()
    
    print("🎯 Enhanced JSON Path Selection Integration Demo")
    print("=" * 55)
    print("Features demonstrated:")
    print("• Large, easily visible JSON Path Selector dialog")
    print("• Enhanced visual design with clear hierarchy")
    print("• Auto-population from workflow steps")
    print("• Real-time search and filtering capabilities")
    print("• One-click path selection and preview")
    print("• Integration with main application workflow")
    print("=" * 55)
    print("Click 'Open JSON Path Selector Dialog' to begin!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
