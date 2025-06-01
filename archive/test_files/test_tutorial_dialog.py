#!/usr/bin/env python3
"""
Test script to verify tutorial dialog display and functionality.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from tutorials import UnifiedTutorialSelectionDialog as TutorialDialog

class TestMainWindow(QMainWindow):
    """Simple test window to launch tutorial dialog."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutorial Dialog Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Test button
        test_button = QPushButton("Open Tutorial Dialog")
        test_button.clicked.connect(self.open_tutorial_dialog)
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(test_button)
    
    def open_tutorial_dialog(self):
        """Open the tutorial dialog for testing."""
        dialog = TutorialDialog(self)
        dialog.tutorial_selected.connect(self.on_tutorial_selected)
        result = dialog.exec()
        print(f"Dialog result: {result}")
    
    def on_tutorial_selected(self, tutorial_id):
        """Handle tutorial selection."""
        print(f"Tutorial selected: {tutorial_id}")

def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    window = TestMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
