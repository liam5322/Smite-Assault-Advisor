#!/usr/bin/env python3
"""
Quick launcher for SMITE 2 Assault Brain
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from main import main

if __name__ == "__main__":
    main()