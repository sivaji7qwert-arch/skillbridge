"""
Adds the scripts/ directory to sys.path so test files can import the
pipeline modules directly (e.g. `from extract_skills import ...`)
without installing the project as a package.
"""
import os
import sys

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS_DIR))
