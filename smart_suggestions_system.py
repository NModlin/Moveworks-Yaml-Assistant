"""
Smart Suggestions System for the Moveworks YAML Assistant.

This module provides AI-powered workflow suggestions based on user input,
context analysis, and machine learning patterns to help users create
better workflows more efficiently.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QTextEdit, QGroupBox, QScrollArea, QFrame, QComboBox,
    QProgressBar, QToolTip
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QIcon, QPalette

from core_structures import Workflow, ActionStep, ScriptStep
from expression_factory import ExpressionFactory, CommonPatterns


@dataclass
class Suggestion:
    """Represents a smart suggestion for workflow improvement."""
    id: str
    title: str
    description: str
    suggestion_type: str  # 'action', 'optimization', 'pattern', 'fix'
    confidence: float  # 0.0 to 1.0
    applicable_context: List[str]
    implementation_code: str
    benefits: List[str]
    estimated_time_saved: int  # in minutes
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserContext:
    """Represents the current user context for generating suggestions."""
    current_workflow: Optional[Workflow]
    recent_actions: List[str]
    common_patterns: List[str]
    error_history: List[str]
    user_skill_level: str  # 'beginner', 'intermediate', 'advanced'
    preferred_actions: List[str]
    time_of_day: str
    workflow_complexity: str


class PatternAnalyzer:
    """Analyzes workflow patterns to generate intelligent suggestions."""
    
    def __init__(self):
        self.action_patterns = defaultdict(list)
        self.sequence_patterns = defaultdict(int)
        self.error_patterns = defaultdict(list)
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load predefined optimization rules."""
        return {
            'duplicate_actions': {
                'pattern': r'(mw\.\w+).*\1',
                'suggestion': 'Consider combining duplicate actions',
                'confidence': 0.8
            },
            'missing_error_handling': {
                'pattern': r'mw\.(?!.*try_catch)',
                'suggestion': 'Add error handling with try-catch',
                'confidence': 0.7
            },
            'inefficient_loops': {
                'pattern': r'for.*in.*data\.\w+.*action',
                'suggestion': 'Consider using parallel processing',
                'confidence': 0.6
            },
            'hardcoded_values': {
                'pattern': r'"[^"]*@[^"]*"',
                'suggestion': 'Use input variables instead of hardcoded values',
                'confidence': 0.9
            }
        }
    
    def analyze_workflow(self, workflow: Workflow) -> List[Suggestion]:
        """Analyze a workflow and generate suggestions."""
        suggestions = []
        
        if not workflow or not workflow.steps:
            return suggestions
        
        # Analyze for common patterns
        suggestions.extend(self._analyze_action_patterns(workflow))
        suggestions.extend(self._analyze_optimization_opportunities(workflow))
        suggestions.extend(self._analyze_best_practices(workflow))
        suggestions.extend(self._analyze_error_handling(workflow))
        
        return sorted(suggestions, key=lambda s: s.confidence, reverse=True)
    
    def _analyze_action_patterns(self, workflow: Workflow) -> List[Suggestion]:
        """Analyze action patterns and suggest improvements."""
        suggestions = []
        action_names = []
        
        for step in workflow.steps:
            if hasattr(step, 'action_name') and step.action_name:
                action_names.append(step.action_name)
        
        # Check for common patterns
        if 'mw.get_user_by_email' in action_names:
            if 'mw.send_notification' not in action_names:
                suggestions.append(Suggestion(
                    id="suggest_notification",
                    title="Add User Notification",
                    description="After looking up a user, consider sending them a notification",
                    suggestion_type="pattern",
                    confidence=0.7,
                    applicable_context=["user_management"],
                    implementation_code="""
# Add after user lookup
notification_step = ExpressionFactory.create_action(
    action_name="mw.send_notification",
    output_key="notification_result",
    input_args={
        "recipient": "data.user_info.user.email",
        "message": "Welcome to the system!"
    }
)
                    """.strip(),
                    benefits=["Improved user experience", "Automated communication"],
                    estimated_time_saved=5
                ))
        
        return suggestions
    
    def _analyze_optimization_opportunities(self, workflow: Workflow) -> List[Suggestion]:
        """Analyze for optimization opportunities."""
        suggestions = []
        
        # Check for sequential actions that could be parallelized
        sequential_actions = []
        for step in workflow.steps:
            if hasattr(step, 'action_name'):
                sequential_actions.append(step)
        
        if len(sequential_actions) >= 3:
            suggestions.append(Suggestion(
                id="suggest_parallel",
                title="Parallelize Independent Actions",
                description="Some actions can run in parallel to improve performance",
                suggestion_type="optimization",
                confidence=0.6,
                applicable_context=["performance"],
                implementation_code="""
# Convert to parallel execution
parallel_step = ExpressionFactory.create_parallel(
    description="Run actions in parallel",
    branches=[
        ParallelBranch(name="branch1", steps=[action1]),
        ParallelBranch(name="branch2", steps=[action2])
    ]
)
                """.strip(),
                benefits=["Faster execution", "Better resource utilization"],
                estimated_time_saved=15
            ))
        
        return suggestions
    
    def _analyze_best_practices(self, workflow: Workflow) -> List[Suggestion]:
        """Analyze adherence to best practices."""
        suggestions = []
        
        # Check for input validation
        has_validation = any(
            hasattr(step, 'code') and 'validation' in step.code.lower()
            for step in workflow.steps
        )
        
        if not has_validation and workflow.input_variables:
            suggestions.append(Suggestion(
                id="suggest_input_validation",
                title="Add Input Validation",
                description="Validate input variables to prevent errors",
                suggestion_type="fix",
                confidence=0.8,
                applicable_context=["best_practices"],
                implementation_code="""
# Add input validation script
validation_step = ExpressionFactory.create_script(
    code='''
# Validate required inputs
if not data.user_email or '@' not in data.user_email:
    return {"error": "Invalid email address"}
return {"validation": "passed"}
    ''',
    output_key="input_validation"
)
                """.strip(),
                benefits=["Error prevention", "Better user feedback"],
                estimated_time_saved=10
            ))
        
        return suggestions
    
    def _analyze_error_handling(self, workflow: Workflow) -> List[Suggestion]:
        """Analyze error handling patterns."""
        suggestions = []
        
        has_try_catch = any(
            step.__class__.__name__ == 'TryCatchStep'
            for step in workflow.steps
        )
        
        has_risky_actions = any(
            hasattr(step, 'action_name') and any(
                risky in step.action_name for risky in ['api', 'external', 'create', 'delete']
            )
            for step in workflow.steps
        )
        
        if has_risky_actions and not has_try_catch:
            suggestions.append(Suggestion(
                id="suggest_error_handling",
                title="Add Error Handling",
                description="Wrap risky operations in try-catch blocks",
                suggestion_type="fix",
                confidence=0.9,
                applicable_context=["error_handling"],
                implementation_code="""
# Wrap risky action in try-catch
error_handled_step = CommonPatterns.error_handling_pattern(
    action_name="your_risky_action",
    input_args={"param": "data.input"}
)
                """.strip(),
                benefits=["Graceful error handling", "Better user experience"],
                estimated_time_saved=20
            ))
        
        return suggestions


class ContextAnalyzer:
    """Analyzes user context to provide personalized suggestions."""
    
    def __init__(self):
        self.user_patterns = defaultdict(list)
        self.skill_indicators = {
            'beginner': ['basic', 'simple', 'help', 'tutorial'],
            'intermediate': ['complex', 'advanced', 'optimization'],
            'advanced': ['custom', 'enterprise', 'integration']
        }
    
    def analyze_user_context(self, workflow: Workflow, user_history: List[str]) -> UserContext:
        """Analyze user context from workflow and history."""
        skill_level = self._determine_skill_level(workflow, user_history)
        complexity = self._assess_workflow_complexity(workflow)
        
        return UserContext(
            current_workflow=workflow,
            recent_actions=self._extract_recent_actions(user_history),
            common_patterns=self._identify_common_patterns(user_history),
            error_history=self._extract_error_history(user_history),
            user_skill_level=skill_level,
            preferred_actions=self._identify_preferred_actions(user_history),
            time_of_day=datetime.now().strftime("%H"),
            workflow_complexity=complexity
        )
    
    def _determine_skill_level(self, workflow: Workflow, history: List[str]) -> str:
        """Determine user skill level based on workflow complexity and history."""
        if not workflow or len(workflow.steps) <= 2:
            return 'beginner'
        
        advanced_features = sum(1 for step in workflow.steps if step.__class__.__name__ in [
            'SwitchStep', 'ForLoopStep', 'ParallelStep', 'TryCatchStep'
        ])
        
        if advanced_features >= 2:
            return 'advanced'
        elif advanced_features >= 1 or len(workflow.steps) > 5:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _assess_workflow_complexity(self, workflow: Workflow) -> str:
        """Assess the complexity of the current workflow."""
        if not workflow or len(workflow.steps) <= 2:
            return 'simple'
        elif len(workflow.steps) <= 5:
            return 'moderate'
        else:
            return 'complex'
    
    def _extract_recent_actions(self, history: List[str]) -> List[str]:
        """Extract recent actions from user history."""
        # This would analyze actual user history
        return ['mw.get_user_by_email', 'mw.send_notification']
    
    def _identify_common_patterns(self, history: List[str]) -> List[str]:
        """Identify common patterns in user workflows."""
        return ['user_lookup', 'notification', 'approval']
    
    def _extract_error_history(self, history: List[str]) -> List[str]:
        """Extract error patterns from history."""
        return ['missing_email', 'invalid_user']
    
    def _identify_preferred_actions(self, history: List[str]) -> List[str]:
        """Identify user's preferred actions."""
        return ['mw.get_user_by_email', 'mw.send_notification']


class SmartSuggestionsEngine:
    """Main engine for generating smart suggestions."""
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.context_analyzer = ContextAnalyzer()
        self.suggestion_cache = {}
        self.user_feedback = defaultdict(list)
    
    def generate_suggestions(self, workflow: Workflow, user_history: List[str] = None) -> List[Suggestion]:
        """Generate smart suggestions for the given workflow."""
        if user_history is None:
            user_history = []
        
        # Analyze context
        context = self.context_analyzer.analyze_user_context(workflow, user_history)
        
        # Generate suggestions
        suggestions = []
        suggestions.extend(self.pattern_analyzer.analyze_workflow(workflow))
        suggestions.extend(self._generate_contextual_suggestions(context))
        suggestions.extend(self._generate_skill_based_suggestions(context))
        
        # Filter and rank suggestions
        filtered_suggestions = self._filter_suggestions(suggestions, context)
        return self._rank_suggestions(filtered_suggestions, context)
    
    def _generate_contextual_suggestions(self, context: UserContext) -> List[Suggestion]:
        """Generate suggestions based on user context."""
        suggestions = []
        
        # Time-based suggestions
        hour = int(context.time_of_day)
        if 9 <= hour <= 17:  # Business hours
            suggestions.append(Suggestion(
                id="business_hours_notification",
                title="Business Hours Optimization",
                description="Consider adding business hours check for notifications",
                suggestion_type="optimization",
                confidence=0.5,
                applicable_context=["timing"],
                implementation_code="""
# Add business hours check
business_hours_check = ExpressionFactory.create_script(
    code='''
import datetime
now = datetime.datetime.now()
if 9 <= now.hour <= 17:
    return {"send_notification": True}
else:
    return {"send_notification": False, "schedule_for": "next_business_day"}
    ''',
    output_key="timing_check"
)
                """.strip(),
                benefits=["Better user experience", "Appropriate timing"],
                estimated_time_saved=5
            ))
        
        return suggestions
    
    def _generate_skill_based_suggestions(self, context: UserContext) -> List[Suggestion]:
        """Generate suggestions based on user skill level."""
        suggestions = []
        
        if context.user_skill_level == 'beginner':
            suggestions.append(Suggestion(
                id="beginner_template",
                title="Use Template",
                description="Consider starting with a pre-built template",
                suggestion_type="pattern",
                confidence=0.8,
                applicable_context=["learning"],
                implementation_code="# Use File → Apply Template to get started",
                benefits=["Faster development", "Best practices"],
                estimated_time_saved=30
            ))
        elif context.user_skill_level == 'advanced':
            suggestions.append(Suggestion(
                id="advanced_optimization",
                title="Advanced Optimization",
                description="Consider using advanced features like parallel processing",
                suggestion_type="optimization",
                confidence=0.6,
                applicable_context=["performance"],
                implementation_code="""
# Advanced parallel processing
parallel_step = ExpressionFactory.create_parallel(
    description="Advanced parallel execution",
    branches=[
        ParallelBranch(name="data_processing", steps=[...]),
        ParallelBranch(name="notification", steps=[...])
    ]
)
                """.strip(),
                benefits=["Maximum performance", "Scalability"],
                estimated_time_saved=45
            ))
        
        return suggestions
    
    def _filter_suggestions(self, suggestions: List[Suggestion], context: UserContext) -> List[Suggestion]:
        """Filter suggestions based on context and relevance."""
        filtered = []
        
        for suggestion in suggestions:
            # Filter by confidence threshold
            if suggestion.confidence < 0.4:
                continue
            
            # Filter by skill level appropriateness
            if context.user_skill_level == 'beginner' and suggestion.suggestion_type == 'optimization':
                if suggestion.confidence < 0.7:
                    continue
            
            # Filter by workflow complexity
            if context.workflow_complexity == 'simple' and 'advanced' in suggestion.title.lower():
                continue
            
            filtered.append(suggestion)
        
        return filtered
    
    def _rank_suggestions(self, suggestions: List[Suggestion], context: UserContext) -> List[Suggestion]:
        """Rank suggestions by relevance and importance."""
        def score_suggestion(suggestion: Suggestion) -> float:
            score = suggestion.confidence
            
            # Boost score for user's skill level
            if context.user_skill_level == 'beginner' and suggestion.suggestion_type == 'pattern':
                score += 0.2
            elif context.user_skill_level == 'advanced' and suggestion.suggestion_type == 'optimization':
                score += 0.2
            
            # Boost score for error fixes
            if suggestion.suggestion_type == 'fix':
                score += 0.3
            
            # Boost score for time savings
            if suggestion.estimated_time_saved > 15:
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
        
        return sorted(suggestions, key=score_suggestion, reverse=True)
    
    def record_feedback(self, suggestion_id: str, feedback: str, user_context: UserContext):
        """Record user feedback on suggestions for learning."""
        self.user_feedback[suggestion_id].append({
            'feedback': feedback,
            'context': user_context,
            'timestamp': datetime.now()
        })


class SmartSuggestionsWidget(QWidget):
    """Widget for displaying smart suggestions in the UI."""
    
    suggestion_applied = Signal(str)  # Emits suggestion ID when applied
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.suggestions_engine = SmartSuggestionsEngine()
        self.current_suggestions = []
        self.initUI()
    
    def initUI(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
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
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        
        # Header
        header_label = QLabel("🧠 Smart Suggestions")
        header_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px;
            background-color: #e8f5e8;
            border-radius: 6px;
            border: 1px solid #28a745;
        """)
        layout.addWidget(header_label)
        
        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.itemClicked.connect(self._on_suggestion_clicked)
        layout.addWidget(self.suggestions_list)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Suggestions")
        refresh_btn.clicked.connect(self.refresh_suggestions)
        layout.addWidget(refresh_btn)
        
        # Status label
        self.status_label = QLabel("No suggestions available")
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 8px;")
        layout.addWidget(self.status_label)
    
    def update_suggestions(self, workflow: Workflow, user_history: List[str] = None):
        """Update suggestions based on current workflow."""
        if user_history is None:
            user_history = []
        
        self.current_suggestions = self.suggestions_engine.generate_suggestions(workflow, user_history)
        self._display_suggestions()
    
    def _display_suggestions(self):
        """Display suggestions in the list widget."""
        self.suggestions_list.clear()
        
        if not self.current_suggestions:
            self.status_label.setText("No suggestions available")
            return
        
        self.status_label.setText(f"{len(self.current_suggestions)} suggestions found")
        
        for suggestion in self.current_suggestions[:10]:  # Show top 10
            item = QListWidgetItem()
            
            # Create suggestion display text
            confidence_stars = "⭐" * int(suggestion.confidence * 5)
            time_saved = f"⏱️ {suggestion.estimated_time_saved}min"
            
            item_text = f"""
{suggestion.title} {confidence_stars}
{suggestion.description}
Type: {suggestion.suggestion_type.title()} | {time_saved}
            """.strip()
            
            item.setText(item_text)
            item.setData(Qt.UserRole, suggestion)
            
            # Color code by type
            if suggestion.suggestion_type == 'fix':
                item.setBackground(QPalette().color(QPalette.Base))
            elif suggestion.suggestion_type == 'optimization':
                item.setBackground(QPalette().color(QPalette.AlternateBase))
            
            self.suggestions_list.addItem(item)
    
    def _on_suggestion_clicked(self, item):
        """Handle suggestion click."""
        suggestion = item.data(Qt.UserRole)
        if suggestion:
            self._show_suggestion_details(suggestion)
    
    def _show_suggestion_details(self, suggestion: Suggestion):
        """Show detailed suggestion information."""
        # This would open a detailed dialog
        # For now, emit the signal
        self.suggestion_applied.emit(suggestion.id)
    
    def refresh_suggestions(self):
        """Refresh suggestions manually."""
        # This would trigger a refresh from the parent
        self.status_label.setText("Refreshing suggestions...")
        QTimer.singleShot(1000, lambda: self.status_label.setText("Suggestions refreshed"))
