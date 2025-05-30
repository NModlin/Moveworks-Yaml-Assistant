#!/usr/bin/env python3
"""
Test script for the new Tabbed JSON Path Selector interface.

This script demonstrates the clean, organized tabbed interface with
collapsible sections that reduces clutter and improves usability.
"""

import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import our components
from tabbed_json_selector import TabbedJsonPathSelector
from enhanced_json_selector import VisualDesignConstants
from core_structures import Workflow, ActionStep, ScriptStep


class TabbedInterfaceTestWindow(QMainWindow):
    """Test window showcasing the new tabbed interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Path Selector - Clean Tabbed Interface")
        self.setGeometry(100, 100, 1000, 800)
        
        # Apply clean background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {VisualDesignConstants.LIGHT_BACKGROUND};
            }}
        """)
        
        self._setup_ui()
        self._create_test_workflow()
        
    def _setup_ui(self):
        """Setup the test UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header with clean design
        header = QLabel("🎯 Clean Tabbed Interface - No More Clutter!")
        header.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: bold;
                color: white;
                background-color: {VisualDesignConstants.ACCENT_COLOR};
                border: none;
                border-radius: 8px;
                padding: 16px;
                text-align: center;
            }}
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Benefits description
        benefits = QLabel(
            "✨ NEW FEATURES:\n"
            "• 📑 Tabbed interface for better organization\n"
            "• 📁 Collapsible sections to reduce clutter\n"
            "• 🎯 Essential features in Main tab\n"
            "• 🚀 Advanced features in separate tab\n"
            "• ❓ Built-in help and documentation\n"
            "• 🎨 Clean, modern design"
        )
        benefits.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: #333;
                padding: 16px;
                background-color: white;
                border: 2px solid {VisualDesignConstants.SUCCESS_COLOR};
                border-radius: 8px;
                margin-bottom: 16px;
            }}
        """)
        benefits.setWordWrap(True)
        layout.addWidget(benefits)
        
        # Load test data button
        load_btn = QPushButton("📊 Load Test Data & Explore Tabs")
        load_btn.clicked.connect(self._load_test_data)
        load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VisualDesignConstants.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: #388e3c;
                transform: translateY(-2px);
            }}
        """)
        layout.addWidget(load_btn)
        
        # Tabbed JSON Path Selector
        self.json_selector = TabbedJsonPathSelector()
        layout.addWidget(self.json_selector)
        
        # Status display
        self.status_label = QLabel("Ready - Click the button above to load test data and explore the clean interface")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-size: 13px;
                font-style: italic;
                padding: 12px;
                background-color: white;
                border-radius: 6px;
                margin-top: 8px;
                border: 1px solid {VisualDesignConstants.SUBTLE_BORDER};
            }}
        """)
        layout.addWidget(self.status_label)
        
    def _create_test_workflow(self):
        """Create a comprehensive test workflow."""
        self.workflow = Workflow()
        
        # User profile step
        user_step = ActionStep(
            name="get_user_profile",
            action_name="user_profile_lookup",
            description="Retrieve detailed user profile information",
            output_key="user_profile"
        )
        user_step.parsed_json_output = {
            "user_info": {
                "basic": {
                    "user_id": "USR-12345",
                    "first_name": "Sarah",
                    "last_name": "Connor",
                    "email": "sarah.connor@company.com",
                    "phone": "+1-555-0199",
                    "employee_id": "EMP-98765"
                },
                "work": {
                    "department": "Cybersecurity",
                    "title": "Senior Security Analyst",
                    "level": "L5",
                    "hire_date": "2020-03-15",
                    "location": {
                        "office": "Los Angeles HQ",
                        "building": "Skynet Tower",
                        "floor": 42,
                        "desk": "42A-108"
                    },
                    "manager": {
                        "name": "Kyle Reese",
                        "email": "kyle.reese@company.com",
                        "user_id": "USR-67890",
                        "title": "Security Team Lead"
                    }
                },
                "access": {
                    "permissions": ["read", "write", "admin", "security_admin"],
                    "groups": ["security_team", "senior_staff", "incident_response"],
                    "clearance_level": "TOP_SECRET",
                    "last_login": "2024-01-15T16:45:00Z",
                    "login_count": 2847,
                    "failed_attempts": 0
                }
            },
            "preferences": {
                "ui": {
                    "theme": "dark",
                    "language": "en-US",
                    "timezone": "America/Los_Angeles",
                    "date_format": "MM/DD/YYYY"
                },
                "notifications": {
                    "email": True,
                    "slack": True,
                    "mobile": True,
                    "desktop": True,
                    "security_alerts": True
                },
                "dashboard": {
                    "widgets": ["security_alerts", "system_status", "recent_incidents"],
                    "refresh_interval": 30,
                    "auto_refresh": True
                }
            }
        }
        self.workflow.add_step(user_step)
        
        # Security incidents step
        incidents_step = ScriptStep(
            name="get_security_incidents",
            description="Retrieve security incidents and threat data",
            output_key="security_data"
        )
        incidents_step.parsed_json_output = {
            "incidents": [
                {
                    "incident_id": "INC-2024-001",
                    "title": "Suspicious Login Attempt",
                    "severity": "HIGH",
                    "status": "INVESTIGATING",
                    "created_date": "2024-01-15T14:30:00Z",
                    "affected_systems": ["auth_server", "user_portal"],
                    "threat_indicators": {
                        "ip_addresses": ["192.168.1.100", "10.0.0.50"],
                        "user_agents": ["Mozilla/5.0 (Suspicious Bot)"],
                        "attack_patterns": ["brute_force", "credential_stuffing"]
                    },
                    "response_team": {
                        "lead": "Sarah Connor",
                        "members": ["Kyle Reese", "John Connor", "T-800"],
                        "escalation_level": 2
                    }
                },
                {
                    "incident_id": "INC-2024-002",
                    "title": "Malware Detection",
                    "severity": "CRITICAL",
                    "status": "CONTAINED",
                    "created_date": "2024-01-14T09:15:00Z",
                    "affected_systems": ["workstation_42", "file_server_03"],
                    "threat_indicators": {
                        "file_hashes": ["a1b2c3d4e5f6", "f6e5d4c3b2a1"],
                        "malware_family": "Skynet.Trojan",
                        "attack_vectors": ["email_attachment", "usb_drive"]
                    },
                    "response_team": {
                        "lead": "Kyle Reese",
                        "members": ["Sarah Connor", "T-800"],
                        "escalation_level": 3
                    }
                }
            ],
            "summary": {
                "total_incidents": 2,
                "by_severity": {
                    "critical": 1,
                    "high": 1,
                    "medium": 0,
                    "low": 0
                },
                "by_status": {
                    "investigating": 1,
                    "contained": 1,
                    "resolved": 0
                },
                "threat_score": 8.5,
                "last_updated": "2024-01-15T16:45:00Z"
            }
        }
        self.workflow.add_step(incidents_step)
        
        # System metrics step
        metrics_step = ActionStep(
            name="get_system_metrics",
            action_name="system_monitoring",
            description="Retrieve system performance and health metrics",
            output_key="system_metrics"
        )
        metrics_step.parsed_json_output = {
            "performance": {
                "cpu": {
                    "usage_percent": 45.2,
                    "cores": 16,
                    "temperature": 68.5,
                    "load_average": [1.2, 1.5, 1.8]
                },
                "memory": {
                    "total_gb": 64,
                    "used_gb": 28.7,
                    "available_gb": 35.3,
                    "usage_percent": 44.8
                },
                "disk": {
                    "total_tb": 2.0,
                    "used_tb": 1.2,
                    "available_tb": 0.8,
                    "usage_percent": 60.0
                },
                "network": {
                    "interfaces": ["eth0", "eth1", "lo"],
                    "bandwidth_mbps": 1000,
                    "current_usage_mbps": 156.7,
                    "packets_per_second": 2847
                }
            },
            "health": {
                "overall_status": "HEALTHY",
                "uptime_hours": 720,
                "last_reboot": "2024-01-01T00:00:00Z",
                "services": {
                    "running": 42,
                    "stopped": 3,
                    "failed": 0
                },
                "alerts": {
                    "critical": 0,
                    "warning": 2,
                    "info": 5
                }
            }
        }
        self.workflow.add_step(metrics_step)
        
    def _load_test_data(self):
        """Load test data into the tabbed selector."""
        self.json_selector.set_workflow(self.workflow, current_step_index=0)
        self.status_label.setText(
            "✅ Test data loaded! Explore the tabs:\n"
            "• 🎯 Main tab: Essential features with collapsible sections\n"
            "• 🚀 Advanced tab: Bookmarks, templates, and history\n"
            "• ❓ Help tab: Documentation and usage tips"
        )


def main():
    """Run the tabbed interface test."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("JSON Path Selector - Tabbed Interface")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("Moveworks")
    
    # Create and show test window
    test_window = TabbedInterfaceTestWindow()
    test_window.show()
    
    print("🎯 Clean Tabbed Interface Test")
    print("=" * 50)
    print("PROBLEM SOLVED:")
    print("• No more cluttered interface!")
    print("• Clean tabbed organization")
    print("• Collapsible sections reduce visual noise")
    print("• Essential features prominently displayed")
    print("• Advanced features neatly organized")
    print("• Built-in help and documentation")
    print("=" * 50)
    print("Click 'Load Test Data' to explore the new interface!")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
