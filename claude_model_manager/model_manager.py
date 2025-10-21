"""
Core model management functionality
"""

import os
import subprocess
import sys
import requests
import json
import platform
import ctypes
import winreg
from typing import Dict, List, Optional
from .config import ConfigManager, ModelConfig


class ModelManager:
    """Core model management operations"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def switch_model(self, model_name: str, auto_set_environment: bool = True) -> Dict[str, str]:
        """Switch to a different model with optional environment variable setup"""
        if not self.config_manager.set_current_model(model_name):
            return {"success": False, "message": "切换模型失败"}

        # Export environment variables with smart authentication
        env_vars = self.config_manager.export_environment_vars()

        # Clean up conflicting environment variables
        conflict_vars = ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"]
        for var in conflict_vars:
            if var not in env_vars:
                os.environ.pop(var, None)

        # Set new environment variables in current process
        for key, value in env_vars.items():
            os.environ[key] = value

        # Auto-set environment variables (current process and user environment)
        env_result = {"success": True, "message": "环境变量已在当前进程中设置"}
        if auto_set_environment:
            env_result = self.execute_environment_commands()

        # Try to set system environment variables if running as admin
        system_result = {"success": False, "message": "未尝试设置系统环境变量"}
        if auto_set_environment and self.is_admin() and env_result["success"]:
            # Only set system environment if current process setting was successful
            system_result = self.set_system_environment_vars()

        # Combine results
        combined_message = f"已切换到模型 '{model_name}'"
        combined_message += f"\n- {env_result['message']}"
        if system_result["success"]:
            combined_message += f"\n- {system_result['message']}"
        elif system_result["message"] != "未尝试设置系统环境变量":
            combined_message += f"\n- 系统环境变量: {system_result['message']}"

        return {
            "success": True,
            "message": combined_message.strip(),
            "environment_result": env_result,
            "system_result": system_result
        }

    def get_current_model_info(self) -> Optional[Dict]:
        """Get information about the current model"""
        current = self.config_manager.get_current_model()
        if not current:
            return None

        return {
            "name": current.name,
            "base_url": current.base_url,
            "model": current.model,
            "api_key_set": bool(current.api_key)
        }

    def list_available_models(self) -> List[Dict]:
        """Get list of all available models with current status"""
        models = []
        current_model = self.config_manager.get_current_model()

        for name, config in self.config_manager.models.items():
            models.append({
                "name": name,
                "base_url": config.base_url,
                "model": config.model,
                "api_key_set": bool(config.api_key),
                "is_current": current_model and current_model.name == name
            })

        return models

    def add_model(self, name: str, base_url: str, model: str, api_key: str = "") -> bool:
        """Add a new model configuration"""
        new_model = ModelConfig(name, base_url, model, api_key)
        return self.config_manager.add_model(new_model)

    def update_model(self, old_name: str, name: str, base_url: str, model: str, api_key: str = "") -> bool:
        """Update an existing model configuration"""
        updated_model = ModelConfig(name, base_url, model, api_key)
        return self.config_manager.update_model(old_name, updated_model)

    def delete_model(self, name: str) -> bool:
        """Delete a model configuration"""
        return self.config_manager.delete_model(name)

    def get_environment_commands(self) -> List[str]:
        """Get shell commands to set environment variables"""
        env_vars = self.config_manager.export_environment_vars()
        if not env_vars:
            return []

        commands = []
        for key, value in env_vars.items():
            if sys.platform == "win32":
                commands.append(f'set {key}="{value}"')
            else:
                commands.append(f'export {key}="{value}"')

        return commands

    def execute_environment_commands(self) -> Dict[str, str]:
        """Execute environment variable commands in current process and system"""
        env_vars = self.config_manager.export_environment_vars()
        if not env_vars:
            return {"success": False, "message": "没有可用的环境变量配置"}

        try:
            # 清理可能冲突的环境变量
            conflict_vars = ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"]
            for var in conflict_vars:
                if var not in env_vars:
                    # 如果不在新配置中，就清理掉
                    os.environ.pop(var, None)
                    if sys.platform == "win32":
                        subprocess.run(f'setx {var} ""', shell=True, capture_output=True)

            # Set in current process
            for key, value in env_vars.items():
                os.environ[key] = value

            # Also try to set in user environment (Windows)
            if sys.platform == "win32":
                for key, value in env_vars.items():
                    subprocess.run(f'setx {key} "{value}"', shell=True, capture_output=True)

            return {
                "success": True,
                "message": f"已成功设置 {len(env_vars)} 个环境变量（当前进程和用户环境）"
            }
        except Exception as e:
            return {"success": False, "message": f"设置环境变量失败: {str(e)}"}

    def is_admin(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            if sys.platform == "win32":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False

    def set_system_environment_vars(self) -> Dict[str, str]:
        """Set environment variables in Windows system registry"""
        if sys.platform != "win32":
            return {"success": False, "message": "系统环境变量设置仅支持Windows系统"}

        if not self.is_admin():
            return {"success": False, "message": "需要管理员权限来修改系统环境变量"}

        env_vars = self.config_manager.export_environment_vars()
        if not env_vars:
            return {"success": False, "message": "没有可用的环境变量配置"}

        try:
            # Open registry key for system environment variables
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                0, winreg.KEY_SET_VALUE
            )

            for var_name, var_value in env_vars.items():
                winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, var_value)

            winreg.CloseKey(key)

            # Notify system about environment changes
            ctypes.windll.user32.SendMessageTimeoutW(
                0xFFFF, 0x1A, 0, "Environment", 0, 1000, None
            )

            return {
                "success": True,
                "message": f"已成功设置 {len(env_vars)} 个系统环境变量，重启后生效"
            }

        except Exception as e:
            return {"success": False, "message": f"设置系统环境变量失败: {str(e)}"}

    def restart_with_admin(self) -> bool:
        """Restart the application with administrator privileges"""
        if sys.platform != "win32":
            return False

        try:
            # Get current script path
            script = sys.argv[0]

            # Request UAC elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, script, None, 1
            )
            return True
        except Exception as e:
            print(f"请求管理员权限失败: {e}")
            return False

    def test_model_connection(self, model_name: str) -> Dict:
        """Test connection to a model with actual API call"""
        model = self.config_manager.get_model(model_name)
        if not model:
            return {"success": False, "error": "模型未找到"}

        # Basic validation
        if not model.base_url:
            return {"success": False, "error": "基础URL是必需的"}
        if not model.model:
            return {"success": False, "error": "模型名称是必需的"}

        # Test API connection
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Claude-Code-Model-Manager/1.0.0"
            }

            # Add API key if available
            if model.api_key:
                if "anthropic" in model.base_url.lower():
                    headers["x-api-key"] = model.api_key
                    headers["anthropic-version"] = "2023-06-01"
                else:
                    headers["Authorization"] = f"Bearer {model.api_key}"

            # Prepare test message
            test_message = {
                "model": model.model,
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a connection test. Please respond with 'OK'."
                    }
                ]
            }

            # Determine the endpoint based on the base URL
            if "anthropic" in model.base_url.lower():
                endpoint = f"{model.base_url.rstrip('/')}/v1/messages"
                # Adjust payload for Anthropic API
                test_message = {
                    "model": model.model,
                    "max_tokens": 10,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello, this is a connection test. Please respond with 'OK'."
                        }
                    ]
                }
            elif "siliconflow" in model.base_url.lower():
                endpoint = f"{model.base_url.rstrip('/')}/v1/chat/completions"
            else:
                # Assume OpenAI-compatible API
                endpoint = f"{model.base_url.rstrip('/')}/v1/chat/completions"

            # Make the API call
            response = requests.post(
                endpoint,
                headers=headers,
                json=test_message,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "连接测试成功！模型配置正确。",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": f"认证失败 (HTTP {response.status_code})。请检查API密钥是否正确。",
                    "status_code": response.status_code
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": f"模型未找到 (HTTP {response.status_code})。请检查模型名称是否正确。",
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"API请求失败 (HTTP {response.status_code}): {response.text}",
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "连接超时。请检查网络连接和基础URL。"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "无法连接到服务器。请检查基础URL是否正确。"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"请求异常: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }