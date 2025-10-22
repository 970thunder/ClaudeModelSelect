#!/usr/bin/env python3
"""
测试PyQt启动的直接脚本
"""

import sys
import os

def test_pyqt_launch():
    """测试PyQt启动流程"""
    print("🧪 PyQt启动测试")
    print("="*50)

    # 检查PyQt安装
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5.QtWidgets 导入成功")
    except ImportError as e:
        print(f"❌ PyQt5.QtWidgets 导入失败: {e}")
        print("请确保已安装PyQt5: pip install PyQt5")
        return False

    # 检查自定义GUI类
    try:
        from claude_model_manager.pyqt_gui import ModernPyQtGUI
        print("✅ ModernPyQtGUI 类导入成功")
    except ImportError as e:
        print(f"❌ ModernPyQtGUI 类导入失败: {e}")
        return False

    # 尝试创建实例
    try:
        print("尝试创建GUI实例...")
        app = QApplication(sys.argv)
        window = ModernPyQtGUI()
        print("✅ GUI实例创建成功")

        # 显示窗口但不运行主循环
        window.show()
        print("✅ 窗口显示成功")

        # 立即关闭窗口避免阻塞
        window.close()
        print("✅ 窗口关闭成功")

        return True

    except Exception as e:
        print(f"❌ GUI实例创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_pyqt_launch():
        print("\n🎉 PyQt测试完全通过！可以正常使用PyQt界面。")
    else:
        print("\n❌ PyQt测试失败，请检查错误信息。")