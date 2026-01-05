#!/usr/bin/env python3
"""
PyQt-based Claude Code Model Manager
Main entry point for the PyQt application
"""

import sys
import os
import traceback
import subprocess

def show_error(title, message):
    """Show error message using platform specific method"""
    try:
        if sys.platform == 'darwin':
            # Use AppleScript on macOS
            subprocess.call(['osascript', '-e', f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" icon stop'])
        else:
            # Fallback to tkinter
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(title, message)
            root.destroy()
    except:
        # If all else fails, print to stderr (might be visible in console logs)
        sys.stderr.write(f"{title}: {message}\n")

def main():
    """Main entry point for PyQt application"""
    try:
        # Handle path for PyInstaller
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # One-file mode
                application_path = sys._MEIPASS
            else:
                # One-dir mode
                application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # Add application path to sys.path if not already there
        if application_path not in sys.path:
            sys.path.insert(0, application_path)

        # Try to import PyQt modules
        try:
            from PyQt5.QtWidgets import QApplication
            from claude_model_manager.pyqt_gui import ModernPyQtGUI
        except ImportError as e:
            show_error("启动错误", f"PyQt5 模块导入失败。\n\n错误详情: {e}\n\n请确保已安装 PyQt5。")
            return

        # Create QApplication
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("Claude Code Model Manager")
        app.setApplicationVersion("1.0")

        # Create and show main window
        try:
            window = ModernPyQtGUI()
            window.show()
        except Exception as e:
            error_msg = f"界面初始化失败: {str(e)}\n\n{traceback.format_exc()}"
            show_error("运行时错误", error_msg)
            return 1

        # Execute application
        return app.exec()

    except Exception as e:
        error_msg = f"应用程序发生未捕获异常: {str(e)}\n\n{traceback.format_exc()}"
        show_error("致命错误", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())