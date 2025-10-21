#!/usr/bin/env python3
"""
测试新功能的脚本
"""

from claude_model_manager.model_manager import ModelManager
from claude_model_manager.config import ConfigManager

def test_all_features():
    print("=== Claude Code 模型管理器新功能测试 ===\n")

    cm = ConfigManager()
    mm = ModelManager(cm)

    # 1. 测试管理员权限检测
    print("1. 管理员权限检测:")
    is_admin = mm.is_admin()
    print(f"   当前是否以管理员身份运行: {is_admin}")

    # 2. 测试当前模型信息
    print("\n2. 当前模型信息:")
    current_model = mm.get_current_model_info()
    if current_model:
        print(f"   名称: {current_model['name']}")
        print(f"   Base URL: {current_model['base_url']}")
        print(f"   模型: {current_model['model']}")
        print(f"   API密钥: {'已设置' if current_model['api_key_set'] else '未设置'}")
    else:
        print("   未选择当前模型")

    # 3. 测试环境变量命令生成
    print("\n3. 环境变量命令:")
    commands = mm.get_environment_commands()
    if commands:
        for cmd in commands:
            print(f"   {cmd}")
    else:
        print("   没有可用的环境变量命令")

    # 4. 测试自动环境变量设置
    print("\n4. 自动设置环境变量:")
    result = mm.execute_environment_commands()
    print(f"   执行结果: {result['success']}")
    print(f"   消息: {result['message']}")

    # 5. 测试系统环境变量设置（仅在有管理员权限时）
    print("\n5. 系统环境变量设置:")
    if is_admin:
        result = mm.set_system_environment_vars()
        print(f"   执行结果: {result['success']}")
        print(f"   消息: {result['message']}")
    else:
        print("   需要管理员权限才能测试此功能")

    # 6. 测试所有可用模型
    print("\n6. 所有可用模型:")
    models = mm.list_available_models()
    for model in models:
        status = "[当前]" if model["is_current"] else ""
        print(f"   {model['name']} {status}")
        print(f"     基础URL: {model['base_url']}")
        print(f"     模型: {model['model']}")
        print(f"     API密钥: {'已设置' if model['api_key_set'] else '未设置'}")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_all_features()