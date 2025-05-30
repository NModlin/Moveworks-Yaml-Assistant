#!/usr/bin/env python3
"""
Comprehensive test script to verify all font readability improvements throughout the application.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_font_readability():
    """Test font readability across all UI components."""
    print("🧪 Testing Comprehensive Font Readability")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
        from PySide6.QtWidgets import QTabWidget, QGroupBox, QLabel, QListWidget, QTreeWidget
        from PySide6.QtWidgets import QComboBox, QTableWidget, QLineEdit, QTextEdit, QPushButton
        from PySide6.QtCore import Qt
        
        # Create minimal app for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create test window with comprehensive styling
        window = QMainWindow()
        window.setWindowTitle("Font Readability Test - All UI Components")
        window.setGeometry(100, 100, 1000, 700)
        
        # Apply the same styling as main application
        window.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #f5f5f5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 13px;
                color: #2c3e50;
            }
            
            /* Tab Widgets - High Contrast */
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
                border-bottom-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
                color: #2c3e50;
            }
            
            /* Group Boxes - High Contrast */
            QGroupBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 600;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #2c3e50;
                background-color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 14px;
            }
            
            /* Labels - High Contrast */
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
            }
            
            /* List Widgets - High Contrast */
            QListWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                color: #2c3e50;
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 13px;
                font-weight: 500;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            
            /* Tree Widgets - High Contrast */
            QTreeWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
            }
            QTreeWidget::item {
                color: #2c3e50;
                padding: 4px;
                font-size: 13px;
                font-weight: 500;
            }
            
            /* Combo Boxes - High Contrast */
            QComboBox {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 20px;
                font-weight: 500;
            }
            
            /* Table Widgets - High Contrast */
            QTableWidget {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                color: #2c3e50;
                padding: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            
            /* Text Inputs - High Contrast */
            QLineEdit, QTextEdit {
                color: #2c3e50;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
            
            /* Buttons - High Contrast */
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
        """)
        
        # Create central widget with comprehensive UI components
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🔍 Font Readability Test - All UI Components")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Create tab widget to test tab readability
        tab_widget = QTabWidget()
        
        # Tab 1: Basic Components
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        # Group box with labels
        group1 = QGroupBox("📝 Text Elements Test")
        group1_layout = QVBoxLayout(group1)
        
        group1_layout.addWidget(QLabel("Regular Label - Should be dark text (#2c3e50)"))
        group1_layout.addWidget(QLabel("Another Label - Testing readability"))
        
        line_edit = QLineEdit("Sample text input - dark text on white background")
        group1_layout.addWidget(line_edit)
        
        text_edit = QTextEdit()
        text_edit.setPlainText("Sample text area content\nMultiple lines\nDark text (#2c3e50) on white background")
        text_edit.setMaximumHeight(80)
        group1_layout.addWidget(text_edit)
        
        tab1_layout.addWidget(group1)
        
        # Group box with list and combo
        group2 = QGroupBox("📋 Selection Elements Test")
        group2_layout = QVBoxLayout(group2)
        
        list_widget = QListWidget()
        list_widget.addItems(["List Item 1 - Dark Text", "List Item 2 - Dark Text", "List Item 3 - Dark Text"])
        list_widget.setMaximumHeight(100)
        group2_layout.addWidget(list_widget)
        
        combo_box = QComboBox()
        combo_box.addItems(["Combo Option 1", "Combo Option 2", "Combo Option 3"])
        group2_layout.addWidget(combo_box)
        
        tab1_layout.addWidget(group2)
        
        tab_widget.addTab(tab1, "📝 Basic Components")
        
        # Tab 2: Advanced Components
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        
        # Tree widget
        tree_widget = QTreeWidget()
        tree_widget.setHeaderLabels(["Tree Column 1", "Tree Column 2"])
        tree_widget.setMaximumHeight(150)
        
        # Add tree items
        from PySide6.QtWidgets import QTreeWidgetItem
        root_item = QTreeWidgetItem(tree_widget, ["Root Item - Dark Text", "Value"])
        child_item = QTreeWidgetItem(root_item, ["Child Item - Dark Text", "Child Value"])
        tree_widget.expandAll()
        
        tab2_layout.addWidget(QLabel("🌳 Tree Widget Test"))
        tab2_layout.addWidget(tree_widget)
        
        # Table widget
        table_widget = QTableWidget(3, 2)
        table_widget.setHorizontalHeaderLabels(["Column 1", "Column 2"])
        table_widget.setMaximumHeight(150)
        
        # Add table items
        from PySide6.QtWidgets import QTableWidgetItem
        for row in range(3):
            for col in range(2):
                item = QTableWidgetItem(f"Cell {row+1},{col+1} - Dark Text")
                table_widget.setItem(row, col, item)
        
        tab2_layout.addWidget(QLabel("📊 Table Widget Test"))
        tab2_layout.addWidget(table_widget)
        
        tab_widget.addTab(tab2, "🔧 Advanced Components")
        
        # Tab 3: Button Test
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        
        tab3_layout.addWidget(QLabel("🔘 Button Test - White text on blue background"))
        
        button1 = QPushButton("Primary Button - White Text")
        tab3_layout.addWidget(button1)
        
        button2 = QPushButton("Secondary Button - White Text")
        button2.setStyleSheet("background-color: #95a5a6; color: #ffffff;")
        tab3_layout.addWidget(button2)
        
        tab_widget.addTab(tab3, "🔘 Buttons")
        
        layout.addWidget(tab_widget)
        
        # Instructions
        instructions = QLabel("""
📋 Manual Testing Instructions:
1. Check that ALL tab text is readable (dark text on light tabs)
2. Verify group box titles are dark and readable
3. Confirm all labels use dark text (#2c3e50)
4. Test list items, tree items, and table cells for readability
5. Ensure combo box text is dark
6. Verify buttons have white text on colored backgrounds
7. Check that no text appears light/white on light backgrounds

✅ Expected Results:
• Tab text: Dark (#2c3e50) on light backgrounds
• Selected tabs: White text on blue/green backgrounds
• All body text: Dark (#2c3e50) for maximum readability
• Buttons: White text on colored backgrounds
• No white-on-white or light-on-light text anywhere
        """)
        instructions.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 6px; font-size: 12px; color: #2c3e50;")
        layout.addWidget(instructions)
        
        window.show()
        
        print("✅ Font readability test window created successfully")
        print("📋 Manual Testing Required:")
        print("   1. Check tab text readability")
        print("   2. Verify group box titles")
        print("   3. Test all text elements")
        print("   4. Confirm no light text on light backgrounds")
        print("\n⏳ Close the test window when done...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Font readability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the comprehensive font readability test."""
    print("🚀 Comprehensive Font Readability Test")
    print("=" * 70)
    
    success = test_font_readability()
    
    print("\n" + "=" * 70)
    if success == 0:  # QApplication.exec() returns 0 on normal exit
        print("✅ Font readability test completed!")
        print("   If all text was readable, the improvements are working!")
    else:
        print("❌ Font readability test failed")
    
    return success == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
