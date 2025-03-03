#!/usr/bin/env python3
"""
SpaceWar - A space combat game
Main entry point
"""
import os
import sys
import importlib.util

def main():
    """
    Main entry point for the game
    """
    # Make sure we're in the correct directory for relative paths to work
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import the original spacewar.py as a module
    spec = importlib.util.spec_from_file_location("spacewar_original", "spacewar.py")
    spacewar_original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(spacewar_original)
    
    # Restore the original directory
    os.chdir(original_dir)

if __name__ == "__main__":
    main() 