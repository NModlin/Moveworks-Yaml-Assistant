"""
Action Name Validator for Moveworks YAML Assistant.

This module provides comprehensive validation for action_name fields including:
- Mandatory field enforcement for ActionStep instances
- Naming convention validation (alphanumeric, dots, underscores)
- Integration with Moveworks Actions Catalog for validation and auto-completion
- Format validation and error reporting with suggestions
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from core_structures import ActionStep


@dataclass
class ActionNameValidationResult:
    """Result of action_name validation with detailed feedback."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    is_known_action: bool = False
    action_category: Optional[str] = None


class ActionNameValidator:
    """Comprehensive validator for action_name fields in Moveworks workflows."""
    
    def __init__(self):
        # Valid action_name pattern: letters, numbers, dots, underscores
        self.action_name_pattern = re.compile(r'^[a-zA-Z0-9_.]+$')
        
        # Minimum length for action names
        self.min_length = 2
        
        # Load MW_ACTIONS_CATALOG if available
        self.mw_actions_catalog = self._load_mw_catalog()
    
    def _load_mw_catalog(self) -> List[Any]:
        """Load Moveworks Actions Catalog if available."""
        try:
            from mw_actions_catalog import MW_ACTIONS_CATALOG
            return MW_ACTIONS_CATALOG
        except ImportError:
            return []
    
    def validate_action_name(self, action_name: str, step_context: Any = None) -> ActionNameValidationResult:
        """
        Validate a single action_name field.
        
        Args:
            action_name: The action_name value to validate
            step_context: Optional ActionStep instance for context-specific validation
            
        Returns:
            ActionNameValidationResult with validation details
        """
        result = ActionNameValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[]
        )
        
        # Check if field is required (always required for ActionStep)
        if not action_name or not action_name.strip():
            result.errors.append("ActionStep requires a non-empty action_name")
            result.is_valid = False
            result.suggestions.append("Add an action name like 'mw.get_user_by_email' or 'custom_action'")
            return result
        
        action_name = action_name.strip()
        
        # Validate naming convention
        if not self._is_valid_action_name_format(action_name):
            result.errors.append(f"action_name '{action_name}' contains invalid characters")
            result.is_valid = False
            result.suggestions.append("Use only letters, numbers, dots, and underscores")
        
        # Check minimum length
        if len(action_name) < self.min_length:
            result.errors.append(f"action_name '{action_name}' is too short (minimum {self.min_length} characters)")
            result.is_valid = False
            result.suggestions.append(f"Use a longer name like 'my_action' or 'mw.get_user'")
        
        # Check for proper mw. prefix format
        if action_name.startswith('mw.'):
            if len(action_name) <= 3:  # Just "mw."
                result.errors.append(f"action_name '{action_name}' is incomplete")
                result.is_valid = False
                result.suggestions.append("Specify the action after 'mw.' (e.g., 'mw.get_user_by_email')")
        
        # Validate against MW_ACTIONS_CATALOG
        catalog_result = self._validate_against_catalog(action_name)
        result.is_known_action = catalog_result['is_known']
        result.action_category = catalog_result.get('category')

        # Add warnings for unknown actions (especially mw. prefixed ones)
        if not catalog_result['is_known']:
            if action_name.startswith('mw.'):
                result.warnings.append(f"action_name '{action_name}' not found in Moveworks catalog")
            if catalog_result['suggestions']:
                result.suggestions.extend(catalog_result['suggestions'])
        
        return result
    
    def _is_valid_action_name_format(self, action_name: str) -> bool:
        """Check if action_name follows valid naming convention."""
        if not action_name:
            return False
        
        # Must match the pattern (letters, numbers, dots, underscores)
        return bool(self.action_name_pattern.match(action_name))
    
    def _validate_against_catalog(self, action_name: str) -> Dict[str, Any]:
        """Validate action_name against Moveworks Actions Catalog."""
        result = {
            'is_known': False,
            'category': None,
            'suggestions': []
        }
        
        if not self.mw_actions_catalog:
            return result
        
        # Check if it's a known action
        for action in self.mw_actions_catalog:
            if action.action_name == action_name:
                result['is_known'] = True
                result['category'] = action.category
                return result
        
        # If not found, look for similar actions
        similar_actions = []
        action_name_lower = action_name.lower()
        
        for action in self.mw_actions_catalog:
            # Check for partial matches
            if action_name_lower in action.action_name.lower():
                similar_actions.append(action.action_name)
            elif action.action_name.lower().startswith(action_name_lower):
                similar_actions.append(action.action_name)
        
        # Limit suggestions to top 3
        result['suggestions'] = [f"Did you mean: {action}" for action in similar_actions[:3]]
        
        return result
    
    def get_action_suggestions(self, partial_name: str = "") -> List[str]:
        """
        Get action name suggestions based on partial input.
        
        Args:
            partial_name: Partial action name to match against
            
        Returns:
            List of suggested action names
        """
        if not self.mw_actions_catalog:
            return []
        
        suggestions = []
        partial_lower = partial_name.lower()
        
        for action in self.mw_actions_catalog:
            if not partial_name or partial_lower in action.action_name.lower():
                suggestions.append(action.action_name)
        
        return sorted(suggestions)
    
    def get_actions_by_category(self, category: str) -> List[str]:
        """
        Get all action names in a specific category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            List of action names in the category
        """
        if not self.mw_actions_catalog:
            return []
        
        return [action.action_name for action in self.mw_actions_catalog 
                if action.category == category]
    
    def get_all_categories(self) -> List[str]:
        """
        Get all available action categories.
        
        Returns:
            List of unique category names
        """
        if not self.mw_actions_catalog:
            return []
        
        categories = set(action.category for action in self.mw_actions_catalog)
        return sorted(list(categories))
    
    def validate_workflow_action_names(self, workflow) -> List[ActionNameValidationResult]:
        """
        Validate all action_name fields in a workflow.
        
        Args:
            workflow: The workflow to validate
            
        Returns:
            List of validation results for each ActionStep
        """
        results = []
        
        for step_index, step in enumerate(workflow.steps):
            if isinstance(step, ActionStep):
                action_name = getattr(step, 'action_name', '')
                result = self.validate_action_name(action_name, step)
                results.append((step_index, result))
        
        return results
    
    def suggest_action_name_fixes(self, action_name: str) -> List[str]:
        """
        Suggest fixes for invalid action names.
        
        Args:
            action_name: The invalid action name
            
        Returns:
            List of suggested fixes
        """
        suggestions = []
        
        if not action_name or not action_name.strip():
            suggestions.extend([
                "mw.get_user_by_email",
                "mw.create_ticket", 
                "custom_action_name"
            ])
            return suggestions
        
        # Clean up the action name
        cleaned = re.sub(r'[^\w\.]', '_', action_name.strip())
        cleaned = re.sub(r'_+', '_', cleaned)  # Remove multiple underscores
        cleaned = cleaned.strip('_')  # Remove leading/trailing underscores
        
        if cleaned and cleaned != action_name:
            suggestions.append(f"Use cleaned version: {cleaned}")
        
        # If it looks like it should be a mw. action
        if action_name.lower().startswith('mw') and not action_name.startswith('mw.'):
            suggestions.append(f"Use proper mw. prefix: mw.{action_name[2:].lstrip('.')}")
        
        # Look for similar actions in catalog
        catalog_suggestions = self._validate_against_catalog(action_name)['suggestions']
        suggestions.extend(catalog_suggestions)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_action_info(self, action_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an action from the catalog.
        
        Args:
            action_name: The action name to look up
            
        Returns:
            Dictionary with action information or None if not found
        """
        if not self.mw_actions_catalog:
            return None
        
        for action in self.mw_actions_catalog:
            if action.action_name == action_name:
                return {
                    'action_name': action.action_name,
                    'display_name': action.display_name,
                    'description': action.description,
                    'category': action.category,
                    'input_args': [arg.name for arg in action.input_args],
                    'required_args': [arg.name for arg in action.input_args if arg.required]
                }
        
        return None


# Global validator instance
action_name_validator = ActionNameValidator()
