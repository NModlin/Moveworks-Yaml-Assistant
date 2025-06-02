"""
Visual Workflow Builder for the Moveworks YAML Assistant.

This module provides a drag-and-drop visual interface for building workflows,
making it easier for users to understand workflow structure and create
complex workflows through visual manipulation.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QFrame, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsProxyWidget,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QMenu, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QDialogButtonBox, QSplitter,
    QToolBox, QListWidget, QListWidgetItem, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QMimeData, QTimer
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QDrag, QPalette, QPixmap,
    QLinearGradient, QPolygonF
)

from core_structures import (
    Workflow, ActionStep, ScriptStep, SwitchStep, ForLoopStep, ParallelStep,
    ReturnStep, RaiseStep, TryCatchStep, InputVariable
)
from expression_factory import ExpressionFactory


@dataclass
class NodePosition:
    """Represents the position of a node in the visual builder."""
    x: float
    y: float
    width: float = 150
    height: float = 80


class WorkflowNode(QGraphicsRectItem):
    """Visual representation of a workflow step."""
    
    def __init__(self, step, node_id: str, position: NodePosition):
        super().__init__(0, 0, position.width, position.height)
        self.step = step
        self.node_id = node_id
        self.position = position
        self.connections = []  # List of connected nodes
        
        # Set up appearance
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Set position
        self.setPos(position.x, position.y)
        
        # Style based on step type
        self._setup_appearance()
        
        # Add text label
        self.text_item = QGraphicsTextItem(self._get_display_text(), self)
        self.text_item.setPos(5, 5)
        self.text_item.setTextWidth(position.width - 10)
        
        # Add connection points
        self._setup_connection_points()
    
    def _setup_appearance(self):
        """Set up node appearance based on step type."""
        step_type = self.step.__class__.__name__
        
        # Color scheme for different step types
        colors = {
            'ActionStep': QColor(52, 152, 219),      # Blue
            'ScriptStep': QColor(46, 204, 113),      # Green
            'SwitchStep': QColor(241, 196, 15),      # Yellow
            'ForLoopStep': QColor(155, 89, 182),     # Purple
            'ParallelStep': QColor(230, 126, 34),    # Orange
            'ReturnStep': QColor(231, 76, 60),       # Red
            'RaiseStep': QColor(192, 57, 43),        # Dark Red
            'TryCatchStep': QColor(149, 165, 166)    # Gray
        }
        
        color = colors.get(step_type, QColor(127, 140, 141))
        
        # Create gradient
        gradient = QLinearGradient(0, 0, 0, self.position.height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(110))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(color.darker(150), 2))
        
        # Add rounded corners
        self.setRect(0, 0, self.position.width, self.position.height)
    
    def _get_display_text(self) -> str:
        """Get display text for the node."""
        step_type = self.step.__class__.__name__.replace('Step', '')
        
        if hasattr(self.step, 'action_name') and self.step.action_name:
            return f"{step_type}\n{self.step.action_name}"
        elif hasattr(self.step, 'description') and self.step.description:
            desc = self.step.description[:30] + "..." if len(self.step.description) > 30 else self.step.description
            return f"{step_type}\n{desc}"
        else:
            return step_type
    
    def _setup_connection_points(self):
        """Set up connection points for the node."""
        # Input connection point (top)
        self.input_point = QRectF(
            self.position.width / 2 - 5, -5, 10, 10
        )
        
        # Output connection point (bottom)
        self.output_point = QRectF(
            self.position.width / 2 - 5, self.position.height - 5, 10, 10
        )
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.RightButton:
            self._show_context_menu(event.screenPos())
        else:
            super().mousePressEvent(event)
    
    def _show_context_menu(self, position):
        """Show context menu for the node."""
        menu = QMenu()
        
        edit_action = menu.addAction("Edit Step")
        edit_action.triggered.connect(self._edit_step)
        
        delete_action = menu.addAction("Delete Step")
        delete_action.triggered.connect(self._delete_step)
        
        menu.addSeparator()
        
        duplicate_action = menu.addAction("Duplicate Step")
        duplicate_action.triggered.connect(self._duplicate_step)
        
        menu.exec_(position)
    
    def _edit_step(self):
        """Edit the step properties."""
        dialog = StepEditDialog(self.step)
        if dialog.exec() == QDialog.Accepted:
            self.step = dialog.get_step()
            self.text_item.setPlainText(self._get_display_text())
    
    def _delete_step(self):
        """Delete this step."""
        if self.scene():
            self.scene().removeItem(self)
    
    def _duplicate_step(self):
        """Duplicate this step."""
        # This would be handled by the parent scene
        pass
    
    def itemChange(self, change, value):
        """Handle item changes (like position changes)."""
        if change == QGraphicsItem.ItemPositionChange:
            # Update connections when position changes
            self._update_connections()
        return super().itemChange(change, value)
    
    def _update_connections(self):
        """Update connection lines when node moves."""
        # This would update any connection lines
        pass


class ConnectionLine(QGraphicsLineItem):
    """Visual representation of a connection between workflow steps."""
    
    def __init__(self, start_node: WorkflowNode, end_node: WorkflowNode):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        
        # Set up appearance
        pen = QPen(QColor(52, 73, 94), 2)
        pen.setStyle(Qt.SolidLine)
        self.setPen(pen)
        
        # Add arrow head
        self.arrow_head = QPolygonF([
            QPointF(0, 0),
            QPointF(-10, -5),
            QPointF(-10, 5)
        ])
        
        self.update_line()
    
    def update_line(self):
        """Update the line position based on connected nodes."""
        start_pos = self.start_node.pos() + QPointF(
            self.start_node.position.width / 2,
            self.start_node.position.height
        )
        end_pos = self.end_node.pos() + QPointF(
            self.end_node.position.width / 2,
            0
        )
        
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())


class StepEditDialog(QDialog):
    """Dialog for editing step properties."""
    
    def __init__(self, step, parent=None):
        super().__init__(parent)
        self.step = step
        self.setWindowTitle("Edit Step")
        self.setModal(True)
        self.resize(400, 300)
        self.setupUI()
    
    def setupUI(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout for step properties
        form_layout = QFormLayout()
        
        # Step type (read-only)
        step_type_label = QLabel(self.step.__class__.__name__)
        form_layout.addRow("Step Type:", step_type_label)
        
        # Common fields
        if hasattr(self.step, 'description'):
            self.description_edit = QLineEdit(self.step.description or "")
            form_layout.addRow("Description:", self.description_edit)
        
        if hasattr(self.step, 'output_key'):
            self.output_key_edit = QLineEdit(self.step.output_key or "")
            form_layout.addRow("Output Key:", self.output_key_edit)
        
        # Step-specific fields
        if hasattr(self.step, 'action_name'):
            self.action_name_edit = QLineEdit(self.step.action_name or "")
            form_layout.addRow("Action Name:", self.action_name_edit)
        
        if hasattr(self.step, 'code'):
            self.code_edit = QTextEdit(self.step.code or "")
            self.code_edit.setMaximumHeight(150)
            form_layout.addRow("Code:", self.code_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_step(self):
        """Get the updated step object."""
        # Update step properties from form
        if hasattr(self.step, 'description') and hasattr(self, 'description_edit'):
            self.step.description = self.description_edit.text()
        
        if hasattr(self.step, 'output_key') and hasattr(self, 'output_key_edit'):
            self.step.output_key = self.output_key_edit.text()
        
        if hasattr(self.step, 'action_name') and hasattr(self, 'action_name_edit'):
            self.step.action_name = self.action_name_edit.text()
        
        if hasattr(self.step, 'code') and hasattr(self, 'code_edit'):
            self.step.code = self.code_edit.toPlainText()
        
        return self.step


class StepPalette(QWidget):
    """Palette of available workflow steps for dragging."""
    
    step_dragged = Signal(str)  # Emits step type when dragged
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        """Initialize the palette UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title_label = QLabel("🧩 Step Palette")
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px;
            background-color: #ecf0f1;
            border-radius: 6px;
        """)
        layout.addWidget(title_label)
        
        # Step categories
        self.toolbox = QToolBox()
        
        # Basic steps
        basic_steps = QWidget()
        basic_layout = QVBoxLayout(basic_steps)
        
        self._add_step_button(basic_layout, "Action", "Execute a Moveworks action", "ActionStep")
        self._add_step_button(basic_layout, "Script", "Run custom APIthon code", "ScriptStep")
        self._add_step_button(basic_layout, "Return", "Return workflow result", "ReturnStep")
        
        basic_layout.addStretch()
        self.toolbox.addItem(basic_steps, "Basic Steps")
        
        # Control flow steps
        control_steps = QWidget()
        control_layout = QVBoxLayout(control_steps)
        
        self._add_step_button(control_layout, "Switch", "Conditional logic", "SwitchStep")
        self._add_step_button(control_layout, "For Loop", "Iterate over items", "ForLoopStep")
        self._add_step_button(control_layout, "Parallel", "Run steps in parallel", "ParallelStep")
        
        control_layout.addStretch()
        self.toolbox.addItem(control_steps, "Control Flow")
        
        # Error handling steps
        error_steps = QWidget()
        error_layout = QVBoxLayout(error_steps)
        
        self._add_step_button(error_layout, "Try-Catch", "Handle errors gracefully", "TryCatchStep")
        self._add_step_button(error_layout, "Raise", "Raise an error", "RaiseStep")
        
        error_layout.addStretch()
        self.toolbox.addItem(error_steps, "Error Handling")
        
        layout.addWidget(self.toolbox)
    
    def _add_step_button(self, layout, title, description, step_type):
        """Add a step button to the palette."""
        button = QPushButton(f"{title}\n{description}")
        button.setMinimumHeight(60)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                text-align: left;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        # Enable dragging
        button.setProperty("step_type", step_type)
        button.mousePressEvent = lambda event, st=step_type: self._start_drag(event, st)
        
        layout.addWidget(button)
    
    def _start_drag(self, event, step_type):
        """Start drag operation for a step type."""
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(step_type)
            mime_data.setData("application/x-step-type", step_type.encode())
            
            # Create drag pixmap
            pixmap = QPixmap(100, 40)
            pixmap.fill(QColor(52, 152, 219, 180))
            
            drag.setPixmap(pixmap)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)


class VisualWorkflowScene(QGraphicsScene):
    """Graphics scene for the visual workflow builder."""
    
    workflow_changed = Signal()  # Emitted when workflow structure changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = {}  # Dict of node_id -> WorkflowNode
        self.connections = []  # List of ConnectionLine objects
        self.workflow = Workflow()
        self.node_counter = 0
        
        # Set up scene
        self.setSceneRect(0, 0, 2000, 1500)
        self.setBackgroundBrush(QBrush(QColor(248, 249, 250)))
        
        # Enable drop events
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasFormat("application/x-step-type"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if event.mimeData().hasFormat("application/x-step-type"):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop events to create new nodes."""
        if event.mimeData().hasFormat("application/x-step-type"):
            step_type = event.mimeData().data("application/x-step-type").data().decode()
            position = event.scenePos()
            
            self._create_node_at_position(step_type, position)
            event.acceptProposedAction()
    
    def _create_node_at_position(self, step_type: str, position: QPointF):
        """Create a new node at the specified position."""
        # Create step instance
        step = self._create_step_instance(step_type)
        
        # Create node
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        
        node_position = NodePosition(position.x(), position.y())
        node = WorkflowNode(step, node_id, node_position)
        
        # Add to scene and tracking
        self.addItem(node)
        self.nodes[node_id] = node
        
        # Update workflow
        self._update_workflow()
        self.workflow_changed.emit()
    
    def _create_step_instance(self, step_type: str):
        """Create a step instance based on type."""
        if step_type == "ActionStep":
            return ExpressionFactory.create_action()
        elif step_type == "ScriptStep":
            return ExpressionFactory.create_script()
        elif step_type == "SwitchStep":
            return ExpressionFactory.create_switch()
        elif step_type == "ForLoopStep":
            return ExpressionFactory.create_for_loop()
        elif step_type == "ParallelStep":
            return ExpressionFactory.create_parallel()
        elif step_type == "ReturnStep":
            return ExpressionFactory.create_return()
        elif step_type == "RaiseStep":
            return ExpressionFactory.create_raise()
        elif step_type == "TryCatchStep":
            return ExpressionFactory.create_try_catch()
        else:
            return ExpressionFactory.create_action()
    
    def _update_workflow(self):
        """Update the workflow object from the visual representation."""
        # Sort nodes by Y position to determine execution order
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda node: node.pos().y()
        )
        
        # Update workflow steps
        self.workflow.steps = [node.step for node in sorted_nodes]
    
    def load_workflow(self, workflow: Workflow):
        """Load a workflow into the visual builder."""
        # Clear existing nodes
        self.clear()
        self.nodes.clear()
        self.connections.clear()
        self.node_counter = 0
        
        # Create nodes for each step
        y_position = 50
        for i, step in enumerate(workflow.steps):
            node_id = f"node_{i}"
            position = NodePosition(100, y_position)
            node = WorkflowNode(step, node_id, position)
            
            self.addItem(node)
            self.nodes[node_id] = node
            
            y_position += 120  # Space between nodes
        
        # Create connections between sequential nodes
        node_list = list(self.nodes.values())
        for i in range(len(node_list) - 1):
            connection = ConnectionLine(node_list[i], node_list[i + 1])
            self.addItem(connection)
            self.connections.append(connection)
        
        self.workflow = workflow
    
    def get_workflow(self) -> Workflow:
        """Get the current workflow from the visual representation."""
        self._update_workflow()
        return self.workflow


class VisualWorkflowBuilder(QWidget):
    """Main visual workflow builder widget."""
    
    workflow_changed = Signal(object)  # Emits the updated workflow
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        """Initialize the visual builder UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Step palette
        self.step_palette = StepPalette()
        self.step_palette.setMaximumWidth(250)
        splitter.addWidget(self.step_palette)
        
        # Right panel - Visual canvas
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self._clear_canvas)
        toolbar_layout.addWidget(clear_btn)
        
        auto_layout_btn = QPushButton("📐 Auto Layout")
        auto_layout_btn.clicked.connect(self._auto_layout)
        toolbar_layout.addWidget(auto_layout_btn)
        
        zoom_in_btn = QPushButton("🔍 Zoom In")
        zoom_in_btn.clicked.connect(self._zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("🔍 Zoom Out")
        zoom_out_btn.clicked.connect(self._zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)
        
        toolbar_layout.addStretch()
        canvas_layout.addLayout(toolbar_layout)
        
        # Graphics view
        self.scene = VisualWorkflowScene()
        self.scene.workflow_changed.connect(self._on_workflow_changed)
        
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        canvas_layout.addWidget(self.view)
        
        splitter.addWidget(canvas_widget)
        splitter.setSizes([250, 800])
        
        layout.addWidget(splitter)
    
    def _clear_canvas(self):
        """Clear the visual canvas."""
        self.scene.clear()
        self.scene.nodes.clear()
        self.scene.connections.clear()
        self.scene.workflow = Workflow()
        self._on_workflow_changed()
    
    def _auto_layout(self):
        """Automatically arrange nodes in a clean layout."""
        nodes = list(self.scene.nodes.values())
        if not nodes:
            return
        
        # Arrange nodes vertically with consistent spacing
        y_position = 50
        for node in nodes:
            node.setPos(100, y_position)
            y_position += 120
        
        # Update connections
        for connection in self.scene.connections:
            connection.update_line()
    
    def _zoom_in(self):
        """Zoom in on the canvas."""
        self.view.scale(1.2, 1.2)
    
    def _zoom_out(self):
        """Zoom out on the canvas."""
        self.view.scale(0.8, 0.8)
    
    def _on_workflow_changed(self):
        """Handle workflow changes."""
        workflow = self.scene.get_workflow()
        self.workflow_changed.emit(workflow)
    
    def load_workflow(self, workflow: Workflow):
        """Load a workflow into the visual builder."""
        self.scene.load_workflow(workflow)
    
    def get_workflow(self) -> Workflow:
        """Get the current workflow."""
        return self.scene.get_workflow()
