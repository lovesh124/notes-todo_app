"""Pytest configuration and shared fixtures."""
import sys
import os

# Add parent directory to Python path so tests can import app and db modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
