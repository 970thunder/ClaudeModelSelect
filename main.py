#!/usr/bin/env python3
"""
Claude Code Model Manager
A visual tool for managing and switching Claude Code models
"""

import sys
import os
from claude_model_manager.gui import ModelManagerGUI

def main():
    """Main entry point for the application"""
    app = ModelManagerGUI()
    app.run()

if __name__ == "__main__":
    main()