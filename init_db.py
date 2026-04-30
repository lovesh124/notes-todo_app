#!/usr/bin/env python3
"""Initialize MongoDB for the notes-todo application."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db

if __name__ == "__main__":
    print("Initializing MongoDB for Notes & Todo App...")
    
    success = init_db()

    if success:
        print("\nMongoDB initialization successful!")
        sys.exit(0)
    else:
        print("\nMongoDB initialization failed!")
        sys.exit(1)
