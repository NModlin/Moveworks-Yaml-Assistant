"""
Unified Tutorial System for Moveworks YAML Assistant.

This package provides a comprehensive, plugin-based tutorial system that replaces
all legacy tutorial implementations with a unified, maintainable architecture.
"""

from .unified_tutorial_system import (
    UnifiedTutorialManager,
    UnifiedTutorialOverlay,
    UnifiedTutorialSelectionDialog,
    UnifiedTutorial,
    UnifiedTutorialStep,
    TutorialPlugin,
    PluginManager,
    TutorialCategory,
    TutorialDifficulty
)

# Legacy compatibility aliases
TutorialDialog = UnifiedTutorialSelectionDialog

__version__ = "2.0.0"
__all__ = [
    "UnifiedTutorialManager",
    "UnifiedTutorialOverlay",
    "UnifiedTutorialSelectionDialog",
    "UnifiedTutorial",
    "UnifiedTutorialStep",
    "TutorialPlugin",
    "PluginManager",
    "TutorialCategory",
    "TutorialDifficulty",
    "TutorialDialog"  # Legacy compatibility
]
