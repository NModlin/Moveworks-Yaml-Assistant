"""
Simple Visual Workflow Builder for the Moveworks YAML Assistant.

This module provides a simplified drag-and-drop interface for building workflows visually.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGraphicsView, QGraphicsScene, 
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsProxyWidget, QMenu, QDialog, QFormLayout, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from typing import List, Optional, Dict
from core_structures import Workflow, ActionStep, ScriptStep


class WorkflowNodeItem(QGraphicsRectItem):
    """A visual node representing a workflow step."""
    
    def __init__(self, step, node_id: str, parent=None):
        super().__init__(parent)
        self.step = step
        self.node_id = node_id
        self.setRect(0, 0, 200, 80)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Set appearance based on step type
        self._setup_appearance()
        
        # Add text
        self.text_item = QGraphicsTextItem(self)
        self._update_text()
        
    def _setup_appearance(self):
        """Set up the visual appearance based on step type."""
        if isinstance(self.step, ActionStep):
            color = QColor("#3498db")  # Blue for actions
            self.setBrush(QBrush(color.lighter(180)))
            self.setPen(QPen(color, 2))
        elif isinstance(self.step, ScriptStep):
            color = QColor("#27ae60")  # Green for scripts
            self.setBrush(QBrush(color.lighter(180)))
            self.setPen(QPen(color, 2))
        else:
            color = QColor("#95a5a6")  # Gray for other types
            self.setBrush(QBrush(color.lighter(180)))
            self.setPen(QPen(color, 2))
            
    def _update_text(self):
        """Update the text displayed on the node."""
        if isinstance(self.step, ActionStep):
            title = f"Action: {self.step.action_name or 'Unnamed'}"
            subtitle = f"Output: {self.step.output_key or 'None'}"
        elif isinstance(self.step, ScriptStep):
            title = "Script Step"
            subtitle = f"Output: {self.step.output_key or 'None'}"
        else:
            title = f"{type(self.step).__name__}"
            subtitle = getattr(self.step, 'description', '') or "No description"
            
        text = f"{title}\n{subtitle}"
        self.text_item.setPlainText(text)
        self.text_item.setPos(10, 10)
        
        # Style the text
        font = QFont("Arial", 10)
        self.text_item.setFont(font)
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.RightButton:
            self._show_context_menu(event.screenPos())
        else:
            super().mousePressEvent(event)
            
    def _show_context_menu(self, pos):
        """Show context menu for the node."""
        menu = QMenu()
        
        edit_action = menu.addAction("Edit Step")
        delete_action = menu.addAction("Delete Step")
        
        action = menu.exec(pos.toPoint())
        
        if action == edit_action:
            self._edit_step()
        elif action == delete_action:
            self._delete_step()
            
    def _edit_step(self):
        """Open edit dialog for the step."""
        dialog = StepEditDialog(self.step)
        if dialog.exec() == QDialog.Accepted:
            self._update_text()
            
    def _delete_step(self):
        """Delete this step from the scene."""
        scene = self.scene()
        if scene and hasattr(scene, 'remove_node'):
            scene.remove_node(self.node_id)


class StepEditDialog(QDialog):
    """Dialog for editing step properties."""
    
    def __init__(self, step, parent=None):
        super().__init__(parent)
        self.step = step
        self.setWindowTitle("Edit Step")
        self.setModal(True)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QFormLayout(self)
        
        if isinstance(self.step, ActionStep):
            self.action_name_edit = QLineEdit(self.step.action_name or "")
            layout.addRow("Action Name:", self.action_name_edit)
            
            self.output_key_edit = QLineEdit(self.step.output_key or "")
            layout.addRow("Output Key:", self.output_key_edit)
            
        elif isinstance(self.step, ScriptStep):
            self.output_key_edit = QLineEdit(self.step.output_key or "")
            layout.addRow("Output Key:", self.output_key_edit)
            
        # Common fields
        self.description_edit = QLineEdit(getattr(self.step, 'description', '') or "")
        layout.addRow("Description:", self.description_edit)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
    def accept(self):
        """Apply changes and close dialog."""
        if isinstance(self.step, ActionStep):
            self.step.action_name = self.action_name_edit.text()
            self.step.output_key = self.output_key_edit.text()
        elif isinstance(self.step, ScriptStep):
            self.step.output_key = self.output_key_edit.text()
            
        self.step.description = self.description_edit.text()
        super().accept()


class VisualWorkflowScene(QGraphicsScene):
    """Graphics scene for the visual workflow builder."""
    
    workflow_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow = Workflow()
        self.nodes: Dict[str, WorkflowNodeItem] = {}
        self.node_counter = 0
        
        # Set scene size
        self.setSceneRect(0, 0, 1000, 800)
        
    def add_step(self, step, position: QPointF = None):
        """Add a step to the visual workflow."""
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        
        # Create visual node
        node = WorkflowNodeItem(step, node_id)
        
        # Position the node
        if position:
            node.setPos(position)
        else:
            # Auto-position based on existing nodes
            y_pos = len(self.nodes) * 100 + 50
            node.setPos(50, y_pos)
            
        # Add to scene and tracking
        self.addItem(node)
        self.nodes[node_id] = node
        
        # Add to workflow
        self.workflow.steps.append(step)
        
        self.workflow_changed.emit()
        
    def remove_node(self, node_id: str):
        """Remove a node from the scene."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # Remove from workflow
            if node.step in self.workflow.steps:
                self.workflow.steps.remove(node.step)
                
            # Remove from scene
            self.removeItem(node)
            del self.nodes[node_id]
            
            self.workflow_changed.emit()
            
    def clear_workflow(self):
        """Clear all nodes from the scene."""
        for node_id in list(self.nodes.keys()):
            self.remove_node(node_id)
            
    def load_workflow(self, workflow: Workflow):
        """Load a workflow into the visual builder."""
        self.clear_workflow()
        self.workflow = workflow
        
        # Create nodes for each step
        for i, step in enumerate(workflow.steps):
            position = QPointF(50, i * 100 + 50)
            self.add_step(step, position)


class SimpleVisualBuilder(QWidget):
    """Simple visual workflow builder widget."""
    
    workflow_changed = Signal(Workflow)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the visual builder UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_label = QLabel("🎨 Visual Workflow Builder")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border-radius: 6px;
            }
        """)
        layout.addWidget(header_label)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        add_action_btn = QPushButton("➕ Add Action")
        add_action_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_action_btn.clicked.connect(self._add_action_step)
        toolbar_layout.addWidget(add_action_btn)
        
        add_script_btn = QPushButton("📝 Add Script")
        add_script_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_script_btn.clicked.connect(self._add_script_step)
        toolbar_layout.addWidget(add_script_btn)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self._clear_workflow)
        toolbar_layout.addWidget(clear_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Graphics view
        self.scene = VisualWorkflowScene()
        self.scene.workflow_changed.connect(self._on_workflow_changed)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        layout.addWidget(self.view)
        
    def _add_action_step(self):
        """Add a new action step."""
        step = ActionStep(
            action_name="new_action",
            output_key="action_result",
            description="New action step"
        )
        self.scene.add_step(step)
        
    def _add_script_step(self):
        """Add a new script step."""
        step = ScriptStep(
            code="# Your APIthon code here\nresult = 'Hello, World!'",
            output_key="script_result",
            description="New script step"
        )
        self.scene.add_step(step)
        
    def _clear_workflow(self):
        """Clear the entire workflow."""
        self.scene.clear_workflow()
        
    def _on_workflow_changed(self):
        """Handle workflow changes."""
        self.workflow_changed.emit(self.scene.workflow)
        
    def set_workflow(self, workflow: Workflow):
        """Set the current workflow."""
        self.scene.load_workflow(workflow)
        
    def get_workflow(self) -> Workflow:
        """Get the current workflow."""
        return self.scene.workflow
