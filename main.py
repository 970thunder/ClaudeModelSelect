#!/usr/bin/env python3
"""
Claude Code Model Manager
A visual tool for managing and switching Claude Code models
"""

import sys
import os

def main():
    """Main entry point with GUI selection"""
    # Set UTF-8 encoding for Windows
    if sys.platform == "win32":
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass

    # Check for command line arguments
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        if choice in ["1", "2", "3"]:
            print(f"🎯 Claude Code 模型管理器 - 使用界面类型: {choice}")
        else:
            print(f"❌ 无效的命令行参数: {choice}")
            choice = "1"
    else:
        print("🎯 Claude Code 模型管理器")
        print("="*40)
        print("请选择界面类型:")
        print("1. PyQt 现代化界面 (推荐)")
        print("2. Tkinter 增强界面")
        print("3. Tkinter 经典界面")
        print("="*40)

        while True:
            try:
                choice = input("请输入选择 (1-3, 默认为1): ").strip()
                if not choice:
                    choice = "1"
                    break
                elif choice in ["1", "2", "3"]:
                    break
                else:
                    print("无效选择，请输入 1, 2 或 3")
            except (EOFError, KeyboardInterrupt):
                print("\n使用默认选择: 1")
                choice = "1"
                break

    try:
        if choice == "1":
            # Try PyQt first with detailed error handling
            try:
                print("🚀 启动PyQt现代化界面...")

                # Import PyQt modules
                try:
                    from PyQt5.QtWidgets import QApplication
                except ImportError as e:
                    print(f"❌ PyQt核心模块导入失败: {e}")
                    raise

                try:
                    from claude_model_manager.pyqt_gui import ModernPyQtGUI
                except ImportError as e:
                    print(f"❌ PyQt GUI类导入失败: {e}")
                    raise

                # Create application and window
                app = QApplication(sys.argv)
                window = ModernPyQtGUI()
                window.show()

                print("✅ PyQt界面启动成功！")
                sys.exit(app.exec())

            except ImportError as e:
                print(f"⚠️ PyQt导入失败: {e}")
                print("⚠️ PyQt不可用，正在尝试增强Tkinter界面...")
                choice = "2"

        if choice == "2":
            # Enhanced Tkinter GUI
            try:
                from claude_model_manager.modern_gui import ModernModelManagerGUI
                print("🎨 启动增强Tkinter界面...")
                app = ModernModelManagerGUI()
                app.run()
                return
            except ImportError:
                print("⚠️ 增强界面不可用，使用经典界面...")
                choice = "3"

        if choice == "3":
            # Original Tkinter GUI
            from claude_model_manager.gui import ModelManagerGUI
            print("📋 启动经典Tkinter界面...")
            app = ModelManagerGUI()
            app.run()

    except Exception as e:
        print(f"❌ 界面启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()