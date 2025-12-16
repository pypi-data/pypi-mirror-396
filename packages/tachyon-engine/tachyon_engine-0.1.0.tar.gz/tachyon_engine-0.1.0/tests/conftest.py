"""
Pytest configuration for tachyon_engine tests
"""

import pytest
import sys
import os

# Add parent directory to path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

