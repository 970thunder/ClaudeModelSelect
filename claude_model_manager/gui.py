"""
GUI interface for Claude Code Model Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from typing import Optional

from .config import ConfigManager, ModelConfig
from .model_manager import ModelManager


class ModelManagerGUI:
    """Main GUI application for model management"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Claude Code 模型管理器")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Initialize managers
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager(self.config_manager)

        # Create GUI
        self.setup_gui()

    def setup_gui(self):
        """Setup the main GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(header_frame, text="Claude Code 模型管理器",
                 font=("Arial", 16, "bold")).grid(row=0, column=0, sticky=tk.W)

        # Current model info
        current_frame = ttk.LabelFrame(main_frame, text="当前模型", padding="10")
        current_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.current_model_label = ttk.Label(current_frame, text="未选择模型",
                                           font=("Arial", 10))
        self.current_model_label.grid(row=0, column=0, sticky=tk.W)

        # Model list
        list_frame = ttk.LabelFrame(main_frame, text="可用模型", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Create treeview for models
        columns = ("名称", "基础URL", "模型", "API密钥", "状态")
        self.model_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        # Configure columns
        self.model_tree.heading("名称", text="名称")
        self.model_tree.heading("基础URL", text="基础URL")
        self.model_tree.heading("模型", text="模型")
        self.model_tree.heading("API密钥", text="API密钥")
        self.model_tree.heading("状态", text="状态")

        self.model_tree.column("名称", width=120)
        self.model_tree.column("基础URL", width=200)
        self.model_tree.column("模型", width=150)
        self.model_tree.column("API密钥", width=80)
        self.model_tree.column("状态", width=80)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.model_tree.yview)
        self.model_tree.configure(yscrollcommand=scrollbar.set)

        self.model_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind double-click event
        self.model_tree.bind("<Double-1>", self.on_model_double_click)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="添加模型",
                  command=self.add_model).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="编辑模型",
                  command=self.edit_model).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="删除模型",
                  command=self.delete_model).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="切换到模型",
                  command=self.switch_to_model).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(button_frame, text="自动设置环境变量",
                  command=self.auto_set_environment).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(button_frame, text="设置系统环境变量",
                  command=self.set_system_environment).grid(row=0, column=5, padx=(0, 5))
        ttk.Button(button_frame, text="测试连接",
                  command=self.test_model_connection).grid(row=0, column=6, padx=(0, 5))
        ttk.Button(button_frame, text="刷新",
                  command=self.refresh_model_list).grid(row=0, column=7, padx=(0, 5))
        ttk.Button(button_frame, text="导出命令",
                  command=self.export_commands).grid(row=0, column=8, padx=(0, 5))

        # Environment commands frame
        self.env_frame = ttk.LabelFrame(main_frame, text="环境变量命令", padding="10")
        self.env_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.env_text = tk.Text(self.env_frame, height=4, width=80)
        self.env_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        env_scrollbar = ttk.Scrollbar(self.env_frame, orient=tk.VERTICAL, command=self.env_text.yview)
        self.env_text.configure(yscrollcommand=env_scrollbar.set)
        env_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.env_frame.columnconfigure(0, weight=1)
        self.env_frame.rowconfigure(0, weight=1)

        # Initial refresh
        self.refresh_model_list()

    def refresh_model_list(self):
        """Refresh the model list display"""
        # Clear existing items
        for item in self.model_tree.get_children():
            self.model_tree.delete(item)

        # Get current model info
        current_model_info = self.model_manager.get_current_model_info()
        if current_model_info:
            current_text = f"当前: {current_model_info['name']} ({current_model_info['model']})"
        else:
            current_text = "未选择模型"
        self.current_model_label.config(text=current_text)

        # Populate model list
        models = self.model_manager.list_available_models()
        for model in models:
            api_key_status = "已设置" if model["api_key_set"] else "未设置"
            status = "当前" if model["is_current"] else ""

            self.model_tree.insert("", "end", values=(
                model["name"],
                model["base_url"],
                model["model"],
                api_key_status,
                status
            ))

        # Update environment commands
        self.update_environment_commands()

    def update_environment_commands(self):
        """Update the environment commands display"""
        commands = self.model_manager.get_environment_commands()
        self.env_text.delete(1.0, tk.END)

        if commands:
            for cmd in commands:
                self.env_text.insert(tk.END, cmd + "\n")
        else:
            self.env_text.insert(tk.END, "未选择模型。请选择模型以查看环境变量命令。")

    def get_selected_model(self) -> Optional[str]:
        """Get the name of the currently selected model"""
        selection = self.model_tree.selection()
        if not selection:
            return None

        item = selection[0]
        values = self.model_tree.item(item, "values")
        return values[0] if values else None

    def add_model(self):
        """Add a new model"""
        dialog = ModelDialog(self.root, "添加模型")
        if dialog.result:
            name, base_url, model, api_key = dialog.result
            if self.model_manager.add_model(name, base_url, model, api_key):
                self.refresh_model_list()
                messagebox.showinfo("成功", f"模型 '{name}' 添加成功！")
            else:
                messagebox.showerror("错误", f"模型 '{name}' 已存在！")

    def edit_model(self):
        """Edit the selected model"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "请选择要编辑的模型。")
            return

        model = self.config_manager.get_model(model_name)
        if not model:
            messagebox.showerror("错误", "选择的模型未找到。")
            return

        dialog = ModelDialog(self.root, "编辑模型", model)
        if dialog.result:
            new_name, base_url, model_name, api_key = dialog.result
            if self.model_manager.update_model(model.name, new_name, base_url, model_name, api_key):
                self.refresh_model_list()
                messagebox.showinfo("成功", "模型更新成功！")
            else:
                messagebox.showerror("错误", "更新模型失败。")

    def delete_model(self):
        """Delete the selected model"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "请选择要删除的模型。")
            return

        if messagebox.askyesno("确认删除",
                             f"确定要删除模型 '{model_name}' 吗？"):
            if self.model_manager.delete_model(model_name):
                self.refresh_model_list()
                messagebox.showinfo("成功", f"模型 '{model_name}' 删除成功！")
            else:
                messagebox.showerror("错误", "删除模型失败。")

    def switch_to_model(self):
        """Switch to the selected model and auto-set environment variables"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "请选择要切换到的模型。")
            return

        if self.model_manager.switch_model(model_name):
            # Auto-set environment variables
            result = self.model_manager.execute_environment_commands()

            if result["success"]:
                messagebox.showinfo("成功",
                    f"已切换到模型 '{model_name}'！\n\n"
                    f"{result['message']}\n\n"
                    "注意：环境变量仅在当前进程生效。重启Claude Code后需要重新设置。"
                )
            else:
                messagebox.showwarning("部分成功",
                    f"已切换到模型 '{model_name}'，但环境变量设置失败：\n"
                    f"{result['message']}"
                )

            self.refresh_model_list()
        else:
            messagebox.showerror("错误", "切换模型失败。")

    def on_model_double_click(self, event):
        """Handle double-click on model"""
        self.switch_to_model()

    def export_commands(self):
        """Show export commands dialog"""
        commands = self.model_manager.get_environment_commands()
        if not commands:
            messagebox.showinfo("信息", "未选择模型。请先选择一个模型。")
            return

        # Create a simple dialog to show commands
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("环境变量命令")
        export_dialog.geometry("600x300")
        export_dialog.transient(self.root)
        export_dialog.grab_set()

        ttk.Label(export_dialog, text="复制并在终端中运行以下命令：",
                 font=("Arial", 10, "bold")).pack(pady=(10, 5))

        text_widget = tk.Text(export_dialog, height=10, width=70)
        text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        for cmd in commands:
            text_widget.insert(tk.END, cmd + "\n")

        text_widget.config(state=tk.DISABLED)

        ttk.Button(export_dialog, text="关闭",
                  command=export_dialog.destroy).pack(pady=10)

    def auto_set_environment(self):
        """Automatically set environment variables in current process"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "请选择要设置环境变量的模型。")
            return

        # First switch to the model
        if not self.model_manager.switch_model(model_name):
            messagebox.showerror("错误", "切换模型失败。")
            return

        # Then execute environment commands
        result = self.model_manager.execute_environment_commands()

        if result["success"]:
            messagebox.showinfo("成功", result["message"])
            self.refresh_model_list()
        else:
            messagebox.showerror("错误", result["message"])

    def set_system_environment(self):
        """Set system environment variables (requires admin)"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "请选择要设置系统环境变量的模型。")
            return

        # First switch to the model
        if not self.model_manager.switch_model(model_name):
            messagebox.showerror("错误", "切换模型失败。")
            return

        # Check if already running as admin
        if self.model_manager.is_admin():
            result = self.model_manager.set_system_environment_vars()
            if result["success"]:
                messagebox.showinfo("成功", result["message"])
            else:
                messagebox.showerror("错误", result["message"])
        else:
            # Ask user if they want to restart with admin privileges
            response = messagebox.askyesno(
                "需要管理员权限",
                "设置系统环境变量需要管理员权限。\n\n"
                "是否重新启动程序以管理员身份运行？\n\n"
                "注意：重启后需要重新选择模型并再次点击此按钮。"
            )

            if response:
                if self.model_manager.restart_with_admin():
                    messagebox.showinfo("信息", "程序将以管理员身份重新启动。")
                    self.root.quit()
                else:
                    messagebox.showerror("错误", "无法以管理员身份重新启动程序。")
                    messagebox.showinfo("提示", "请手动以管理员身份运行此程序。")

    def test_model_connection(self):
        """Test connection to the selected model"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "请选择要测试连接的模型。")
            return

        # Show testing dialog
        test_dialog = tk.Toplevel(self.root)
        test_dialog.title("测试连接")
        test_dialog.geometry("400x200")
        test_dialog.transient(self.root)
        test_dialog.grab_set()

        # Progress label
        progress_label = ttk.Label(test_dialog, text="正在测试连接...",
                                 font=("Arial", 10))
        progress_label.pack(pady=20)

        # Progress bar
        progress_bar = ttk.Progressbar(test_dialog, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()

        # Status text
        status_text = tk.Text(test_dialog, height=4, width=50, wrap=tk.WORD)
        status_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        status_text.insert(tk.END, f"正在测试模型 '{model_name}'...\n")
        status_text.config(state=tk.DISABLED)

        def perform_test():
            """Perform the actual connection test"""
            try:
                result = self.model_manager.test_model_connection(model_name)

                # Update UI in main thread
                test_dialog.after(0, lambda: show_test_result(result))
            except Exception as e:
                result = {"success": False, "error": f"测试过程中发生异常: {str(e)}"}
                test_dialog.after(0, lambda: show_test_result(result))

        def show_test_result(result):
            """Show the test result"""
            progress_bar.stop()
            status_text.config(state=tk.NORMAL)
            status_text.delete(1.0, tk.END)

            if result["success"]:
                progress_label.config(text="连接测试成功！")
                status_text.insert(tk.END, f"✅ {result['message']}\n")
                if "response_time" in result:
                    status_text.insert(tk.END, f"响应时间: {result['response_time']:.2f}秒\n")
                if "status_code" in result:
                    status_text.insert(tk.END, f"状态码: {result['status_code']}\n")
            else:
                progress_label.config(text="连接测试失败！")
                status_text.insert(tk.END, f"❌ {result['error']}\n")
                if "status_code" in result:
                    status_text.insert(tk.END, f"状态码: {result['status_code']}\n")

            status_text.config(state=tk.DISABLED)

            # Add close button
            close_button = ttk.Button(test_dialog, text="关闭",
                                    command=test_dialog.destroy)
            close_button.pack(pady=10)

        # Start the test in a separate thread
        import threading
        test_thread = threading.Thread(target=perform_test)
        test_thread.daemon = True
        test_thread.start()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class ModelDialog:
    """Dialog for adding/editing models"""

    def __init__(self, parent, title: str, model: Optional[ModelConfig] = None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Model name
        ttk.Label(main_frame, text="模型名称：").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=model.name if model else "")
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Base URL
        ttk.Label(main_frame, text="基础URL：").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.base_url_var = tk.StringVar(value=model.base_url if model else "")
        base_url_entry = ttk.Entry(main_frame, textvariable=self.base_url_var, width=40)
        base_url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Model
        ttk.Label(main_frame, text="模型：").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar(value=model.model if model else "")
        model_entry = ttk.Entry(main_frame, textvariable=self.model_var, width=40)
        model_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # API Key
        ttk.Label(main_frame, text="API密钥：").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_var = tk.StringVar(value=model.api_key if model else "")
        api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key_var, width=40, show="*")
        api_key_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Example labels
        example_frame = ttk.LabelFrame(main_frame, text="示例", padding="10")
        example_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        examples = [
            "基础URL: https://api.siliconflow.cn/",
            "模型: moonshotai/Kimi-K2-Instruct-0905",
            "API密钥: 从提供商获取的API密钥"
        ]

        for i, example in enumerate(examples):
            ttk.Label(example_frame, text=example, font=("Arial", 8)).grid(row=i, column=0, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text="确定", command=self.ok).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Focus on name field if new model
        if not model:
            name_entry.focus_set()

        self.dialog.wait_window()

    def ok(self):
        """Handle OK button"""
        name = self.name_var.get().strip()
        base_url = self.base_url_var.get().strip()
        model = self.model_var.get().strip()
        api_key = self.api_key_var.get().strip()

        if not name:
            messagebox.showerror("错误", "模型名称是必需的。")
            return
        if not base_url:
            messagebox.showerror("错误", "基础URL是必需的。")
            return
        if not model:
            messagebox.showerror("错误", "模型是必需的。")
            return

        self.result = (name, base_url, model, api_key)
        self.dialog.destroy()

    def cancel(self):
        """Handle Cancel button"""
        self.dialog.destroy()