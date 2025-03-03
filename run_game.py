#!/usr/bin/env python3
"""
SpaceWar - A space combat game
Entry point script
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the game
if __name__ == "__main__":
    from spacewar.main import main
    main() 