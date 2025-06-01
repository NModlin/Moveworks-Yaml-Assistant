"""
Moveworks YAML Assistant Test Suite

This package contains comprehensive tests for the Moveworks YAML Assistant,
organized by test type and functionality.
"""

import sys
from pathlib import Path

# Add project root to Python path for test imports
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
