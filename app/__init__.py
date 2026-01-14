"""
eviStream app package
This module ensures the project root is in sys.path
"""

import sys
from pathlib import Path

# Add project root to Python path
# This allows all modules in app/ to import from core/ and utils/
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))



