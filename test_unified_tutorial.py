#!/usr/bin/env python3
"""
Test script for the unified tutorial system.

This script tests the unified tutorial system that combines the best features
from all existing tutorial systems.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

def test_unified_tutorial_system():
    """Test the unified tutorial system components."""
    print("Testing Unified Tutorial System...")

    try:
        from unified_tutorial_system import (
            UnifiedTutorialManager, 
            UnifiedTutorialSelectionDialog,
            UnifiedTutorialOverlay,
            UnifiedTutorial,
            UnifiedTutorialStep,
            TutorialCategory,
            TutorialDifficulty
        )

        # Test tutorial step creation
        step = UnifiedTutorialStep(
            title="Test Step",
            description="This is a test tutorial step",
            instruction="This tests the unified tutorial step creation",
            target_element="test_element",
            action_type="copy_paste",
            copy_paste_data="test_data"
        )
        print("✓ UnifiedTutorialStep created successfully")

        # Test tutorial creation
        tutorial = UnifiedTutorial(
            id="test_tutorial",
            title="Test Tutorial",
            description="A test tutorial for the unified system",
            category=TutorialCategory.GETTING_STARTED,
            difficulty=TutorialDifficulty.BEGINNER,
            estimated_time="5 minutes",
            learning_objectives=["Test objective 1", "Test objective 2"],
            steps=[step]
        )
        print("✓ UnifiedTutorial created successfully")

        print("✓ Unified tutorial system components imported and tested successfully")
        return True

    except ImportError as e:
        print(f"✗ Unified tutorial system import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unified tutorial system error: {e}")
        return False


class TestMainWindow(QMainWindow):
    """Test main window for unified tutorial system."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified Tutorial System Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add test elements with object names for tutorial targeting
        title_label = QLabel("🎓 Unified Tutorial System Test")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # Test button for tutorial targeting
        self.test_button = QPushButton("Test Button (Tutorial Target)")
        self.test_button.setObjectName("test_target_button")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout.addWidget(self.test_button)
        
        # Tutorial system test button
        tutorial_test_btn = QPushButton("🚀 Test Tutorial Selection Dialog")
        tutorial_test_btn.clicked.connect(self.test_tutorial_dialog)
        tutorial_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(tutorial_test_btn)
        
        # Tutorial overlay test button
        overlay_test_btn = QPushButton("🎯 Test Tutorial Overlay")
        overlay_test_btn.clicked.connect(self.test_tutorial_overlay)
        overlay_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        layout.addWidget(overlay_test_btn)
        
        # Manager test button
        manager_test_btn = QPushButton("📚 Test Tutorial Manager")
        manager_test_btn.clicked.connect(self.test_tutorial_manager)
        manager_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        layout.addWidget(manager_test_btn)
        
        # Status label
        self.status_label = QLabel("Ready to test unified tutorial system")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #6c757d; margin: 20px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Initialize tutorial manager
        try:
            from unified_tutorial_system import UnifiedTutorialManager
            self.tutorial_manager = UnifiedTutorialManager(self)
            self.status_label.setText("✓ Unified tutorial manager initialized successfully")
            self.status_label.setStyleSheet("color: #28a745; margin: 20px;")
        except Exception as e:
            self.status_label.setText(f"✗ Failed to initialize tutorial manager: {e}")
            self.status_label.setStyleSheet("color: #dc3545; margin: 20px;")
    
    def test_tutorial_dialog(self):
        """Test the tutorial selection dialog."""
        try:
            self.status_label.setText("Opening tutorial selection dialog...")
            self.tutorial_manager.show_tutorial_selection()
            self.status_label.setText("✓ Tutorial selection dialog opened successfully")
            self.status_label.setStyleSheet("color: #28a745; margin: 20px;")
        except Exception as e:
            self.status_label.setText(f"✗ Tutorial dialog error: {e}")
            self.status_label.setStyleSheet("color: #dc3545; margin: 20px;")
    
    def test_tutorial_overlay(self):
        """Test the tutorial overlay directly."""
        try:
            from unified_tutorial_system import UnifiedTutorialOverlay, UnifiedTutorialStep
            
            self.status_label.setText("Creating tutorial overlay...")
            
            # Create test overlay
            overlay = UnifiedTutorialOverlay(self)
            
            # Create test step
            test_step = UnifiedTutorialStep(
                title="Test Overlay Step",
                description="This tests the unified tutorial overlay system",
                instruction="This overlay should appear with copy-paste functionality and visual highlighting. Try dragging the panel around!",
                target_element="test_target_button",
                action_type="copy_paste",
                copy_paste_data="Hello from unified tutorial system!"
            )
            
            # Show the step
            overlay.show_step(test_step, self.test_button, 1, 1)
            
            self.status_label.setText("✓ Tutorial overlay created and displayed")
            self.status_label.setStyleSheet("color: #28a745; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"✗ Tutorial overlay error: {e}")
            self.status_label.setStyleSheet("color: #dc3545; margin: 20px;")
    
    def test_tutorial_manager(self):
        """Test the tutorial manager functionality."""
        try:
            self.status_label.setText("Testing tutorial manager...")
            
            # Test manager methods
            is_active = self.tutorial_manager.is_tutorial_active()
            info = self.tutorial_manager.get_current_tutorial_info()
            
            self.status_label.setText(f"✓ Manager test: Active={is_active}, Info={info is not None}")
            self.status_label.setStyleSheet("color: #28a745; margin: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"✗ Tutorial manager error: {e}")
            self.status_label.setStyleSheet("color: #dc3545; margin: 20px;")


def main():
    """Run the unified tutorial system test."""
    print("=" * 60)
    print("UNIFIED TUTORIAL SYSTEM TEST")
    print("=" * 60)
    
    # Test components first
    if not test_unified_tutorial_system():
        print("Component test failed. Exiting.")
        return 1
    
    # Create and run GUI test
    app = QApplication(sys.argv)
    
    window = TestMainWindow()
    window.show()
    
    print("\n" + "=" * 60)
    print("GUI Test Window Opened")
    print("Use the buttons to test different tutorial system features:")
    print("- Tutorial Selection Dialog")
    print("- Tutorial Overlay with highlighting")
    print("- Tutorial Manager functionality")
    print("=" * 60)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
