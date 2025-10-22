"""
Modern GUI interface for Claude Code Model Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from typing import Optional

from .config import ConfigManager, ModelConfig
from .model_manager import ModelManager


class ModernModelManagerGUI:
    """Modern GUI application for model management with improved styling"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Claude Code 模型管理器")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Set window icon
        self.root.iconbitmap(default=None)  # Will use default tkinter icon

        # Theme configuration
        self.current_theme = "dark"  # Default theme
        self.themes = {
            'dark': {
                'primary': '#2563eb',
                'primary_light': '#3b82f6',
                'secondary': '#64748b',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'background': '#0f172a',
                'surface': '#1e293b',
                'on_surface': '#f1f5f9',
                'border': '#334155'
            },
            'light': {
                'primary': '#1e40af',
                'primary_light': '#3b82f6',
                'secondary': '#6b7280',
                'success': '#047857',
                'warning': '#d97706',
                'error': '#dc2626',
                'background': '#f8fafc',
                'surface': '#ffffff',
                'on_surface': '#1e293b',
                'border': '#e2e8f0'
            }
        }
        self.colors = self.themes[self.current_theme]

        # Add theme selection to UI
        self.setup_theme_ui()

    def setup_theme_ui(self):
        """Add theme selection UI to the main interface"""
        # Add theme selector to header
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_selector = ttk.Combobox(self.root, textvariable=self.theme_var,
                                          values=['dark', 'light'], state='readonly')
        self.theme_selector.set(self.current_theme)
        self.theme_selector.pack(side='right', padx=10)
        self.theme_selector.bind('<<ComboboxSelected>>', self.on_theme_changed)

    def on_theme_changed(self, event):
        """Handle theme selection change"""
        selected_theme = self.theme_var.get()
        self.set_theme(selected_theme)

        # Configure styles
        self.setup_styles()

        # Initialize managers
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager(self.config_manager)

        # Create GUI
        self.setup_gui()

    def set_theme(self, theme_name):
        """Switch between light and dark themes"""
        self.current_theme = theme_name
        self.colors = self.themes[theme_name]
        self.setup_styles()
        self.refresh_all_widgets()

    def refresh_all_widgets(self):
        """Refresh all widgets to apply new theme"""
        # Reconfigure root window
        self.root.configure(bg=self.colors['background'])

        # Update status label and other dynamic elements
        self.refresh_model_list()

    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()

        # Configure themes
        style.theme_use('clam')  # More modern than default

        # Configure colors
        self.root.configure(bg=self.colors['background'])

        # Custom styles for modern look
        style.configure('Modern.TFrame', background=self.colors['background'])
        style.configure('Card.TFrame',
                       background=self.colors['surface'],
                       borderwidth=2,
                       relief='groove')
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0)
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0)

        # Configure treeview
        style.configure('Modern.Treeview',
                       background=self.colors['surface'],
                       foreground=self.colors['on_surface'],
                       fieldbackground=self.colors['surface'],
                       borderwidth=0)
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0)

        # Configure treeview row colors for empty cells
        if self.current_theme == 'dark':
            style.map('Modern.Treeview',
                     background=[('selected', self.colors['primary_light'])])
            # Ensure empty cells have proper background in dark mode
            style.configure('Modern.Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['on_surface'],
                           fieldbackground=self.colors['surface'],
                           borderwidth=0)
            # Configure tag styling for consistent background
            style.configure('model_row.Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['on_surface'])
            style.configure('current_model.Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['on_surface'])
        else:
            style.map('Modern.Treeview',
                     background=[('selected', self.colors['primary'])])
            # Ensure empty cells have proper background in light mode
            style.configure('Modern.Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['on_surface'],
                           fieldbackground=self.colors['surface'],
                           borderwidth=0)
            # Configure tag styling for consistent background
            style.configure('model_row.Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['on_surface'])
            style.configure('current_model.Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['on_surface'])

        # Configure labels
        style.configure('Title.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['on_surface'],
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['on_surface'],
                       font=('Segoe UI', 12, 'normal'))

    def setup_gui(self):
        """Setup the modern GUI components"""
        # Header with branding
        header_frame = ttk.Frame(self.root, style='Modern.TFrame', padding='20 10')
        header_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(header_frame, text="🎯 Claude Code 模型管理器",
                 style='Title.TLabel').pack(side='left')

        # Status indicator
        self.status_label = ttk.Label(header_frame, text="就绪",
                                     style='Subtitle.TLabel', foreground=self.colors['success'])
        self.status_label.pack(side='right')

        # Main content area
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Current model card
        self.current_model_card = ttk.LabelFrame(main_frame, text="📊 当前模型",
                                                padding='15', style='Card.TFrame')
        self.current_model_card.pack(fill='x', pady=(0, 15))

        self.current_model_info = tk.Text(self.current_model_card, height=3, width=80,
                                         bg=self.colors['surface'], fg=self.colors['on_surface'],
                                         borderwidth=0, relief='flat', font=('Segoe UI', 10))
        self.current_model_info.pack(fill='x')
        self.current_model_info.config(state='disabled')

        # Action buttons row
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=(0, 15))

        # Left side buttons
        left_buttons = ttk.Frame(button_frame, style='Modern.TFrame')
        left_buttons.pack(side='left')

        ttk.Button(left_buttons, text="➕ 添加模型",
                  command=self.add_model, style='Primary.TButton').pack(side='left', padx=(0, 5))
        ttk.Button(left_buttons, text="✏️ 编辑模型",
                  command=self.edit_model, style='Primary.TButton').pack(side='left', padx=(0, 5))
        ttk.Button(left_buttons, text="🗑️ 删除模型",
                  command=self.delete_model, style='Primary.TButton').pack(side='left', padx=(0, 5))

        # Right side action buttons
        right_buttons = ttk.Frame(button_frame, style='Modern.TFrame')
        right_buttons.pack(side='right')

        ttk.Button(right_buttons, text="🔄 刷新",
                  command=self.refresh_model_list, style='Primary.TButton').pack(side='left', padx=(0, 5))
        ttk.Button(right_buttons, text="🔄 测试连接",
                  command=self.test_model_connection, style='Primary.TButton').pack(side='left', padx=(0, 5))

        # Model list with modern styling
        list_frame = ttk.LabelFrame(main_frame, text="📋 可用模型",
                                   padding='15', style='Card.TFrame')
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Enhanced treeview with better styling
        columns = ("名称", "基础URL", "模型", "API密钥", "状态")
        self.model_tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                      style='Modern.Treeview', height=8)

        # Configure modern columns
        self.model_tree.heading("名称", text="名称")
        self.model_tree.heading("基础URL", text="基础URL")
        self.model_tree.heading("模型", text="模型")
        self.model_tree.heading("API密钥", text="API密钥")
        self.model_tree.heading("状态", text="状态")

        self.model_tree.column("名称", width=150, anchor='center')
        self.model_tree.column("基础URL", width=250, anchor='center')
        self.model_tree.column("模型", width=180, anchor='center')
        self.model_tree.column("API密钥", width=100, anchor='center')
        self.model_tree.column("状态", width=80, anchor='center')

        # Modern scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.model_tree.yview)
        self.model_tree.configure(yscrollcommand=scrollbar.set)

        self.model_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind double-click and selection events
        self.model_tree.bind("<Double-1>", self.on_model_double_click)
        self.model_tree.bind("<<TreeviewSelect>>", self.on_model_select)

        # Quick actions frame
        actions_frame = ttk.LabelFrame(main_frame, text="⚡ 快速操作",
                                      padding='15', style='Card.TFrame')
        actions_frame.pack(fill='x', pady=(0, 15))

        ttk.Button(actions_frame, text="🚀 切换到模型",
                  command=self.switch_to_model, style='Success.TButton', width=15).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="🔧 自动设置环境变量",
                  command=self.auto_set_environment, style='Primary.TButton', width=18).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="⚙️ 设置系统环境变量",
                  command=self.set_system_environment, style='Warning.TButton', width=18).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="📋 导出命令",
                  command=self.export_commands, style='Primary.TButton', width=12).pack(side='left')

        # Environment commands in modern card
        env_frame = ttk.LabelFrame(main_frame, text="🔧 环境变量命令",
                                  padding='15', style='Card.TFrame')
        env_frame.pack(fill='x')
        env_frame.columnconfigure(0, weight=1)
        env_frame.rowconfigure(0, weight=1)

        self.env_text = tk.Text(env_frame, height=4, bg=self.colors['surface'],
                               fg=self.colors['on_surface'], wrap=tk.WORD,
                               font=('Consolas', 9), borderwidth=1, relief='solid')
        self.env_text.grid(row=0, column=0, sticky='nsew')

        env_scrollbar = ttk.Scrollbar(env_frame, orient='vertical', command=self.env_text.yview)
        self.env_text.configure(yscrollcommand=env_scrollbar.set)
        env_scrollbar.grid(row=0, column=1, sticky='ns')

        # Footer
        footer_frame = ttk.Frame(self.root, style='Modern.TFrame', padding='10')
        footer_frame.pack(fill='x', side='bottom')

        ttk.Label(footer_frame, text="🎯 Claude Code 模型管理器 v1.0",
                 style='Subtitle.TLabel', foreground=self.colors['secondary']).pack(side='left')

        # Initial refresh
        self.refresh_model_list()

    def refresh_model_list(self):
        """Refresh the model list with modern styling"""
        # Clear existing items
        for item in self.model_tree.get_children():
            self.model_tree.delete(item)

        # Update current model info
        current_model_info = self.model_manager.get_current_model_info()
        self.current_model_info.config(state='normal')
        self.current_model_info.delete(1.0, tk.END)

        if current_model_info:
            current_text = f"🔵 当前模型: {current_model_info['name']}\n"
            current_text += f"🌐 基础URL: {current_model_info['base_url']}\n"
            current_text += f"🤖 模型: {current_model_info['model']}"

            self.status_label.config(text=f"已选择: {current_model_info['name']}",
                                   foreground=self.colors['success'])
        else:
            current_text = "🟡 未选择模型 - 请从列表中选择一个模型"
            self.status_label.config(text="未选择模型", foreground=self.colors['warning'])

        self.current_model_info.insert(1.0, current_text)
        self.current_model_info.config(state='disabled',
                                      bg=self.colors['surface'],
                                      fg=self.colors['on_surface'])

        # Populate model list with styled items
        models = self.model_manager.list_available_models()
        for model in models:
            api_key_icon = "🔑" if model["api_key_set"] else "❌"
            status_icon = "✅" if model["is_current"] else ""

            # Insert with proper tag for theme-aware styling
            tag = 'current_model' if model["is_current"] else 'model_row'
            item = self.model_tree.insert("", "end", values=(
                f"{model['name']}" if model['name'] else "",
                model["base_url"] if model["base_url"] else "",
                model["model"] if model["model"] else "",
                api_key_icon,
                status_icon
            ), tags=(tag,))

            # Add styling for current model
            if model["is_current"]:
                self.model_tree.selection_set(item)

        # Update environment commands
        self.update_environment_commands()

    def update_environment_commands(self):
        """Update the environment commands display"""
        commands = self.model_manager.get_environment_commands()
        self.env_text.config(state='normal')
        self.env_text.delete(1.0, tk.END)

        if commands:
            for cmd in commands:
                self.env_text.insert(tk.END, cmd + "\n")
        else:
            self.env_text.insert(tk.END, "未选择模型。请选择模型以查看环境变量命令。")

        self.env_text.config(state='disabled',
                            bg=self.colors['surface'],
                            fg=self.colors['on_surface'])

    def get_selected_model(self) -> Optional[str]:
        """Get the name of the currently selected model"""
        selection = self.model_tree.selection()
        if not selection:
            return None

        item = selection[0]
        values = self.model_tree.item(item, "values")
        return values[0] if values else None

    def on_model_select(self, event):
        """Handle model selection"""
        model_name = self.get_selected_model()
        if model_name:
            self.status_label.config(text=f"已选择: {model_name}",
                                   foreground=self.colors['primary_light'])
            self.update_environment_commands()

    def on_model_double_click(self, event):
        """Handle double-click on model - switch to model"""
        self.switch_to_model()

    # Rest of the methods (add_model, edit_model, delete_model, switch_to_model, etc.)
    # ... will be the same as in the original gui.py but with modern styling

    def add_model(self):
        try:
            dialog = ModernModelDialog(self.root, "➕ 添加模型")
            if dialog.result:
                name, base_url, model, api_key = dialog.result
                if self.model_manager.add_model(name, base_url, model, api_key):
                    self.refresh_model_list()
                    messagebox.showinfo("成功", f"✅ 模型 '{name}' 添加成功！")
                else:
                    messagebox.showerror("错误", f"❌ 模型 '{name}' 已存在！")
        except Exception as e:
            messagebox.showerror("错误", f"添加模型时发生错误: {str(e)}")

    def edit_model(self):
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "⚠️ 请选择要编辑的模型。")
            return

        model = self.config_manager.get_model(model_name)
        if not model:
            messagebox.showerror("错误", "❌ 选择的模型未找到。")
            return

        dialog = ModernModelDialog(self.root, "✏️ 编辑模型", model)
        if dialog.result:
            new_name, base_url, model_name, api_key = dialog.result
            if self.model_manager.update_model(model.name, new_name, base_url, model_name, api_key):
                self.refresh_model_list()
                messagebox.showinfo("成功", "✅ 模型更新成功！")
            else:
                messagebox.showerror("错误", "❌ 更新模型失败。")

    def delete_model(self):
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "⚠️ 请选择要删除的模型。")
            return

        if messagebox.askyesno("确认删除", f"🗑️ 确定要删除模型 '{model_name}' 吗？"):
            if self.model_manager.delete_model(model_name):
                self.refresh_model_list()
                messagebox.showinfo("成功", f"✅ 模型 '{model_name}' 删除成功！")
            else:
                messagebox.showerror("错误", "❌ 删除模型失败。")

    def switch_to_model(self):
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("警告", "⚠️ 请选择要切换到的模型。")
            return

        result = self.model_manager.switch_model(model_name)

        if result["success"]:
            env_success = result.get("environment_result", {}).get("success", False)
            system_success = result.get("system_result", {}).get("success", False)

            message = f"✅ 已切换到模型 '{model_name}'！\n\n"
            message += result["message"] + "\n\n"

            if system_success:
                message += "🎯 系统和当前进程环境变量都已成功设置，重启后仍然有效。"
            elif env_success:
                message += "⚠️ 当前进程环境变量已设置，但系统环境变量设置失败。重启Claude Code后需要重新设置。"
            else:
                message = f"❌ 已切换到模型 '{model_name}'，但环境变量设置失败：\n"
                message += result.get("message", "未知错误")

            if system_success:
                messagebox.showinfo("🚀 切换成功", message)
            elif env_success:
                messagebox.showwarning("⚠️ 部分成功", message)
            else:
                messagebox.showerror("❌ 错误", message)

            self.refresh_model_list()
        else:
            messagebox.showerror("❌ 错误", result.get("message", "切换模型失败。"))

    def auto_set_environment(self):
        """Modern auto-set environment function"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("⚠️ 警告", "请选择要设置环境变量的模型。")
            return

        result = self.model_manager.switch_model(model_name, auto_set_environment=False)

        if result["success"]:
            env_result = self.model_manager.execute_environment_commands()

            if env_result["success"]:
                messagebox.showinfo("✅ 成功",
                    f"已切换到模型 '{model_name}'\n\n"
                    f"{env_result['message']}\n\n"
                    "⚠️ 注意：环境变量仅在当前进程生效。\n"
                    "要设置系统环境变量，请使用'设置系统环境变量'按钮。"
                )
            else:
                messagebox.showwarning("⚠️ 部分成功",
                    f"已切换到模型 '{model_name}'，但环境变量设置失败：\n"
                    f"{env_result['message']}"
                )

            self.refresh_model_list()
        else:
            messagebox.showerror("❌ 错误", result.get("message", "切换模型失败。"))

    def set_system_environment(self):
        """Modern system environment setting"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("⚠️ 警告", "请选择要设置系统环境变量的模型。")
            return

        switch_result = self.model_manager.switch_model(model_name, auto_set_environment=False)

        if not switch_result["success"]:
            messagebox.showerror("❌ 错误", switch_result.get("message", "切换模型失败。"))
            return

        if self.model_manager.is_admin():
            result = self.model_manager.set_system_environment_vars()
            if result["success"]:
                messagebox.showinfo("✅ 成功",
                    f"已切换到模型 '{model_name}'\n\n"
                    f"{result['message']}\n\n"
                    "🎯 系统环境变量已设置，重启后仍然有效。"
                )
            else:
                messagebox.showerror("❌ 错误",
                    f"已切换到模型 '{model_name}'，但系统环境变量设置失败：\n\n"
                    f"{result['message']}"
                )
        else:
            response = messagebox.askyesno(
                "🔐 需要管理员权限",
                "设置系统环境变量需要管理员权限。\n\n"
                "是否重新启动程序以管理员身份运行？\n\n"
                "注意：重启后需要重新选择模型并再次点击此按钮。"
            )
            if response:
                if self.model_manager.restart_with_admin():
                    messagebox.showinfo("🔄 信息", "程序将以管理员身份重新启动。")
                    self.root.quit()
                else:
                    messagebox.showerror("❌ 错误", "无法以管理员身份重新启动程序。")
                    messagebox.showinfo("💡 提示", "请手动以管理员身份运行此程序。")

    def export_commands(self):
        """Modern export commands dialog"""
        commands = self.model_manager.get_environment_commands()
        if not commands:
            messagebox.showinfo("💡 信息", "未选择模型。请先选择一个模型。")
            return

        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("📋 环境变量命令")
        export_dialog.geometry("650x350")
        export_dialog.configure(bg=self.colors['background'])
        export_dialog.transient(self.root)
        export_dialog.grab_set()

        ttk.Label(export_dialog, text="复制并在终端中运行以下命令：",
                 style='Subtitle.TLabel').pack(pady=(20, 10))

        text_frame = ttk.Frame(export_dialog, style='Card.TFrame', padding='10')
        text_frame.pack(fill='both', expand=True, padx=20, pady=5)

        text_widget = tk.Text(text_frame, height=12, width=70, bg=self.colors['surface'],
                             fg=self.colors['on_surface'], font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True)

        for cmd in commands:
            text_widget.insert(tk.END, cmd + "\n")

        text_widget.config(state='disabled')

        ttk.Button(export_dialog, text="✅ 关闭",
                  command=export_dialog.destroy, style='Primary.TButton').pack(pady=10)

    def test_model_connection(self):
        """Modern connection testing with progress indicator"""
        model_name = self.get_selected_model()
        if not model_name:
            messagebox.showwarning("⚠️ 警告", "请选择要测试连接的模型。")
            return

        test_dialog = tk.Toplevel(self.root)
        test_dialog.title("🔗 测试连接")
        test_dialog.geometry("450x300")
        test_dialog.configure(bg=self.colors['background'])
        test_dialog.transient(self.root)
        test_dialog.grab_set()

        # Modern progress indicators
        ttk.Label(test_dialog, text=f"正在测试模型 '{model_name}'...",
                 style='Subtitle.TLabel').pack(pady=20)

        progress_bar = ttk.Progressbar(test_dialog, mode='indeterminate', length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()

        status_frame = ttk.Frame(test_dialog, style='Card.TFrame', padding='15')
        status_frame.pack(fill='both', expand=True, padx=20, pady=10)

        status_text = tk.Text(status_frame, height=6, width=50, wrap=tk.WORD,
                             bg=self.colors['surface'], fg=self.colors['on_surface'])
        status_text.pack(fill='both', expand=True)
        status_text.insert(tk.END, f"正在连接到模型 '{model_name}'...\n")
        status_text.config(state='disabled')

        def perform_test():
            try:
                result = self.model_manager.test_model_connection(model_name)
                test_dialog.after(0, lambda: show_test_result(result))
            except Exception as e:
                result = {"success": False, "error": f"测试过程中发生异常: {str(e)}"}
                test_dialog.after(0, lambda: show_test_result(result))

        def show_test_result(result):
            progress_bar.stop()
            status_text.config(state='normal')
            status_text.delete(1.0, tk.END)

            if result["success"]:
                status_text.insert(tk.END, f"✅ {result['message']}\n")
                if "response_time" in result:
                    status_text.insert(tk.END, f"⏱️ 响应时间: {result['response_time']:.2f}秒\n")
                if "status_code" in result:
                    status_text.insert(tk.END, f"🔢 状态码: {result['status_code']}\n")
                status_text.insert(tk.END, "\n🎯 连接测试成功！")
            else:
                status_text.insert(tk.END, f"❌ {result['error']}\n")
                if "status_code" in result:
                    status_text.insert(tk.END, f"🔢 状态码: {result['status_code']}\n")
                status_text.insert(tk.END, "\n⚠️ 连接测试失败，请检查配置。")

            status_text.config(state='disabled')

            ttk.Button(test_dialog, text="✅ 关闭",
                      command=test_dialog.destroy, style='Primary.TButton').pack(pady=10)

        import threading
        test_thread = threading.Thread(target=perform_test)
        test_thread.daemon = True
        test_thread.start()

    def run(self):
        """Start the modern GUI application"""
        self.root.mainloop()


class ModernModelDialog:
    """Modern dialog for adding/editing models"""

    def __init__(self, parent, title: str, model: Optional[ModelConfig] = None):
        self.result = None
        self.colors = {
            'background': '#0f172a',
            'surface': '#1e293b',
            'on_surface': '#f1f5f9'
        }

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("550x400")
        self.dialog.configure(bg=self.colors['background'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Main frame with modern styling
        main_frame = ttk.Frame(self.dialog, style='Card.TFrame', padding="25")
        main_frame.pack(fill='both', expand=True)

        # Model name
        ttk.Label(main_frame, text="📝 模型名称：",
                 style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 10))
        self.name_var = tk.StringVar(value=model.name if model else "")
        name_entry = tk.Entry(main_frame, textvariable=self.name_var, width=40,
                             bg=self.colors['surface'], fg=self.colors['on_surface'])
        name_entry.grid(row=0, column=1, sticky='ew', pady=(0, 10))

        # Base URL
        ttk.Label(main_frame, text="🌐 基础URL：",
                 style='Subtitle.TLabel').grid(row=1, column=0, sticky='w', pady=(0, 10))
        self.base_url_var = tk.StringVar(value=model.base_url if model else "")
        base_url_entry = tk.Entry(main_frame, textvariable=self.base_url_var, width=40,
                                 bg=self.colors['surface'], fg=self.colors['on_surface'])
        base_url_entry.grid(row=1, column=1, sticky='ew', pady=(0, 10))

        # Model
        ttk.Label(main_frame, text="🤖 模型：",
                 style='Subtitle.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 10))
        self.model_var = tk.StringVar(value=model.model if model else "")
        model_entry = tk.Entry(main_frame, textvariable=self.model_var, width=40,
                              bg=self.colors['surface'], fg=self.colors['on_surface'])
        model_entry.grid(row=2, column=1, sticky='ew', pady=(0, 10))

        # API Key
        ttk.Label(main_frame, text="🔑 API密钥：",
                 style='Subtitle.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 10))
        self.api_key_var = tk.StringVar(value=model.api_key if model else "")
        api_key_entry = tk.Entry(main_frame, textvariable=self.api_key_var, width=40,
                                bg=self.colors['surface'], fg=self.colors['on_surface'], show="*")
        api_key_entry.grid(row=3, column=1, sticky='ew', pady=(0, 10))

        # Example section
        example_frame = ttk.LabelFrame(main_frame, text="💡 示例配置",
                                      style='Card.TFrame', padding="15")
        example_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=15)

        examples = [
            "🌐 基础URL: https://api.siliconflow.cn/",
            "🤖 模型: moonshotai/Kimi-K2-Instruct-0905",
            "🔑 API密钥: 从服务商获取的API密钥"
        ]

        for i, example in enumerate(examples):
            ttk.Label(example_frame, text=example,
                     style='Subtitle.TLabel', font=('Segoe UI', 9)).grid(row=i, column=0, sticky='w')

        # Buttons
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="✅ 确定",
                  command=self.ok, style='Success.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="❌ 取消",
                  command=self.cancel, style='Primary.TButton').pack(side='left')

        main_frame.columnconfigure(1, weight=1)

        if not model:
            name_entry.focus_set()

        self.dialog.wait_window()

    def ok(self):
        name = self.name_var.get().strip()
        base_url = self.base_url_var.get().strip()
        model = self.model_var.get().strip()
        api_key = self.api_key_var.get().strip()

        if not name:
            messagebox.showerror("❌ 错误", "模型名称是必需的。")
            return
        if not base_url:
            messagebox.showerror("❌ 错误", "基础URL是必需的。")
            return
        if not model:
            messagebox.showerror("❌ 错误", "模型是必需的。")
            return

        self.result = (name, base_url, model, api_key)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()