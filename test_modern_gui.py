#!/usr/bin/env python3
"""
测试现代化GUI界面
"""

import tkinter as tk
from claude_model_manager.modern_gui import ModernModelManagerGUI

def test_modern_gui():
    """测试现代化GUI界面"""
    print("=== 现代化GUI界面测试 ===")

    try:
        # 创建主窗口但不运行主循环
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        # 测试对话框
        from claude_model_manager.modern_gui import ModernModelDialog

        print("1. 测试添加模型对话框...")
        dialog = None
        try:
            dialog = ModernModelDialog(root, "测试对话框")
            print("   ✅ 模型对话框创建成功")
            if dialog.dialog:
                dialog.dialog.destroy()
        except Exception as e:
            print(f"   ❌ 模型对话框错误: {e}")

        print("2. 测试GUI主类创建...")
        try:
            app = ModernModelManagerGUI()
            print("   ✅ GUI主类创建成功")

            # 测试界面组件
            print("3. 测试界面组件...")
            if hasattr(app, 'model_tree'):
                print("   ✅ 模型树组件存在")
            if hasattr(app, 'current_model_info'):
                print("   ✅ 当前模型信息组件存在")
            if hasattr(app, 'refresh_model_list'):
                print("   ✅ 刷新方法存在")

            # 测试状态更新
            print("4. 测试状态更新...")
            app.refresh_model_list()
            print("   ✅ 状态更新成功")

            app.root.quit()
            app.root.destroy()

        except Exception as e:
            print(f"   ❌ GUI创建错误: {e}")

        root.destroy()

    except Exception as e:
        print(f"测试失败: {e}")

    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_modern_gui()