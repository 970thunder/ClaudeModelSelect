#!/usr/bin/env python3
"""
PyQt-based Claude Code Model Manager
Main entry point for the PyQt application
"""

import sys
import os

def main():
    """Main entry point for PyQt application"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Try to import PyQt modules
        from PyQt5.QtWidgets import QApplication
        from claude_model_manager.pyqt_gui import ModernPyQtGUI

        print("🚀 启动PyQt现代化界面...")

        # Create QApplication
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("Claude Code Model Manager")
        app.setApplicationVersion("1.0")

        # Create and show main window
        window = ModernPyQtGUI()
        window.show()

        # Execute application
        return app.exec()

    except ImportError as e:
        print(f"❌ PyQt模块导入失败: {e}")
        print("💡 请确保已安装PyQt5: pip install PyQt5")
        print("📋 正在启动经典Tkinter界面...")

        # Fallback to original GUI
        try:
            from claude_model_manager.gui import ModelManagerGUI
            original_gui = ModelManagerGUI()
            original_gui.run()
        except Exception as e2:
            print(f"❌ 经典界面启动失败: {e2}")
            input("按回车键退出...")

    except Exception as e:
        print(f"❌ PyQt应用程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    sys.exit(main())