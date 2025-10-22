"""
PyQt-based modern GUI interface for Claude Code Model Manager
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, List

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QTabWidget, QTextEdit, QMessageBox, QInputDialog, QFileDialog,
                            QHeaderView, QSplitter, QFrame, QProgressBar, QComboBox,
                            QDialog, QLineEdit, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

from .config import ConfigManager, ModelConfig
from .model_manager import ModelManager


class WorkerThread(QThread):
    """Worker thread for connection testing"""
    finished = pyqtSignal(dict)

    def __init__(self, model_manager, model_name):
        super().__init__()
        self.model_manager = model_manager
        self.model_name = model_name

    def run(self):
        try:
            result = self.model_manager.test_model_connection(self.model_name)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})


class SwitchModelThread(QThread):
    """Worker thread for model switching with progress indication"""
    finished = pyqtSignal(dict)
    progress_update = pyqtSignal(str)

    def __init__(self, model_manager, model_name):
        super().__init__()
        self.model_manager = model_manager
        self.model_name = model_name

    def run(self):
        try:
            self.progress_update.emit("正在切换模型...")
            result = self.model_manager.switch_model(self.model_name)
            self.progress_update.emit("模型切换完成")
            self.finished.emit(result)
        except Exception as e:
            error_result = {"success": False, "message": f"切换过程中发生异常: {str(e)}"}
            self.finished.emit(error_result)


class AddModelDialog(QDialog):
    """Dialog for adding/editing a model with a single form"""

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = model
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("添加模型" if self.model is None else "编辑模型")
        self.setModal(True)
        self.resize(500, 350)

        layout = QVBoxLayout(self)

        # Create form layout
        form_layout = QFormLayout()

        # Model name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入模型名称，如: Claude-3.5-Sonnet")
        if self.model:
            self.name_edit.setText(self.model.name)
        form_layout.addRow("模型名称 *:", self.name_edit)

        # Base URL
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("输入基础URL，如: https://api.anthropic.com")
        if self.model:
            self.url_edit.setText(self.model.base_url)
        form_layout.addRow("基础URL *:", self.url_edit)

        # Model ID
        self.model_id_edit = QLineEdit()
        self.model_id_edit.setPlaceholderText("输入模型ID，如: claude-3-5-sonnet-20241022")
        if self.model:
            self.model_id_edit.setText(self.model.model)
        form_layout.addRow("模型ID *:", self.model_id_edit)

        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入API密钥 (可选)")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        if self.model:
            self.api_key_edit.setText(self.model.api_key)
        form_layout.addRow("API密钥:", self.api_key_edit)

        layout.addLayout(form_layout)

        # Add description
        desc_label = QLabel("标注 * 的字段为必填项")
        desc_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(desc_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_model_data(self):
        """Get the model data from the form"""
        return {
            'name': self.name_edit.text().strip(),
            'base_url': self.url_edit.text().strip(),
            'model': self.model_id_edit.text().strip(),
            'api_key': self.api_key_edit.text().strip()
        }

    def validate_form(self):
        """Validate the form data"""
        data = self.get_model_data()

        if not data['name']:
            return False, "模型名称不能为空"
        if not data['base_url']:
            return False, "基础URL不能为空"
        if not data['model']:
            return False, "模型ID不能为空"

        return True, ""

    def accept(self):
        """Handle accept with validation"""
        is_valid, message = self.validate_form()
        if not is_valid:
            QMessageBox.warning(self, "输入错误", message)
            return
        super().accept()


class ModernPyQtGUI(QMainWindow):
    """Modern PyQt GUI for model management"""

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager(self.config_manager)

        # Setup UI
        self.setup_ui()
        self.setup_styles()
        self.load_initial_data()

        # File import/export
        self.import_file = None
        self.export_file = None

    def setup_ui(self):
        """Setup the main UI components"""
        self.setWindowTitle("Claude Code 模型管理器 (PyQt)")
        self.setGeometry(100, 100, 1200, 800)

        # Use default window frame with custom styling
        self.setWindowFlags(Qt.Window)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with custom margins
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()

        # Models tab
        models_tab = self.create_models_tab()
        self.tabs.addTab(models_tab, "📋 模型管理")

        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "⚙️ 设置")

        main_layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("就绪")

    def setup_styles(self):
        """Setup modern styling"""
        # Set default dark theme
        self.current_theme = "dark"
        self.apply_dark_theme()

    def apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            /* Main window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            /* Custom title bar for Windows */
            QMainWindow QWidget#widget_titlebar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #444;
            }
            /* Title bar buttons */
            QPushButton#btn_minimize, QPushButton#btn_maximize, QPushButton#btn_close {
                background-color: transparent;
                color: #cccccc;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton#btn_minimize:hover, QPushButton#btn_maximize:hover {
                background-color: #404040;
                color: #ffffff;
            }
            QPushButton#btn_close:hover {
                background-color: #e81123;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #333;
                color: #fff;
                padding: 8px 16px;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTableWidget {
                background-color: #252526;
                color: #cccccc;
                gridline-color: #444;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #333;
                color: #fff;
                padding: 8px;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton.danger {
                background-color: #d13438;
            }
            QPushButton.danger:hover {
                background-color: #b0262a;
            }
            QPushButton.success {
                background-color: #107c10;
            }
            QPushButton.success:hover {
                background-color: #0e6b0e;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QLabel {
                color: #cccccc;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 1px solid #444;
                width: 20px;
            }
            /* Dialog styling for better looking input dialogs */
            QDialog {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QDialog QLabel {
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            QDialog QLineEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                margin: 8px;
                min-height: 20px;
            }
            QDialog QLineEdit:focus {
                border-color: #007acc;
                background-color: #252526;
                outline: none;
            }
            QDialog QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                margin: 8px;
                font-weight: bold;
                min-width: 80px;
            }
            QDialog QPushButton:hover {
                background-color: #005a9e;
            }
            QDialog QPushButton:pressed {
                background-color: #004578;
            }
            QDialog QPushButton:default {
                background-color: #4ec9b0;
            }
            QDialog QPushButton:default:hover {
                background-color: #3db392;
            }
            /* File dialog styling */
            QFileDialog QWidget {
                background-color: #2d2d2d;
                color: #cccccc;
            }
            QFileDialog QLineEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 10px;
            }
            /* Table row headers for line numbers */
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #444;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #333;
                border: 1px solid #444;
            }
            /* Row number styling */
            QTableWidget QTableWidget::item {
                background-color: transparent;
            }
            QTableWidget::item {
                border-bottom: 1px solid #444;
            }
            /* Vertical header for row numbers */
            QTableWidget QHeaderView::section:vertical {
                background-color: #333;
                color: #cccccc;
                border: 1px solid #444;
                padding: 6px 8px;
            }
        """)

    def apply_light_theme(self):
        """Apply light theme styling"""
        self.setStyleSheet("""
            /* Main window */
            QMainWindow {
                background-color: #ffffff;
                color: #000000;
            }
            /* Custom title bar for Windows */
            QMainWindow QWidget#widget_titlebar {
                background-color: #f0f0f0;
                color: #000000;
                border-bottom: 1px solid #ddd;
            }
            /* Title bar buttons */
            QPushButton#btn_minimize, QPushButton#btn_maximize, QPushButton#btn_close {
                background-color: transparent;
                color: #666666;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton#btn_minimize:hover, QPushButton#btn_maximize:hover {
                background-color: #e0e0e0;
                color: #000000;
            }
            QPushButton#btn_close:hover {
                background-color: #e81123;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: #f8f8f8;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 16px;
                border: 1px solid #ddd;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #333333;
                gridline-color: #ddd;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333333;
                padding: 8px;
                border: 1px solid #ddd;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton.danger {
                background-color: #d13438;
            }
            QPushButton.danger:hover {
                background-color: #b0262a;
            }
            QPushButton.success {
                background-color: #107c10;
            }
            QPushButton.success:hover {
                background-color: #0e6b0e;
            }
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QLabel {
                color: #333333;
            }
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 1px solid #ddd;
                width: 20px;
            }
            /* Dialog styling for better looking input dialogs */
            QDialog {
                background-color: #f8f8f8;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QDialog QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            QDialog QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                margin: 8px;
                min-height: 20px;
            }
            QDialog QLineEdit:focus {
                border-color: #007acc;
                background-color: #f5f5f5;
                outline: none;
            }
            QDialog QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                margin: 8px;
                font-weight: bold;
                min-width: 80px;
            }
            QDialog QPushButton:hover {
                background-color: #005a9e;
            }
            QDialog QPushButton:pressed {
                background-color: #004578;
            }
            QDialog QPushButton:default {
                background-color: #107c10;
            }
            QDialog QPushButton:default:hover {
                background-color: #0e6b0e;
            }
            /* File dialog styling */
            QFileDialog QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QFileDialog QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 10px;
            }
            /* Table row headers for line numbers */
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #ddd;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
            }
            /* Row number styling */
            QTableWidget QTableWidget::item {
                background-color: transparent;
            }
            QTableWidget::item {
                border-bottom: 1px solid #ddd;
            }
            /* Vertical header for row numbers */
            QTableWidget QHeaderView::section:vertical {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #ddd;
                padding: 6px 8px;
            }
        """)

    def toggle_maximize(self):
        """Toggle between maximize and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def create_header(self):
        """Create header layout"""
        header_layout = QHBoxLayout()

        # Title
        title = QLabel("🎯 Claude Code 模型管理器")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Current model info
        self.current_model_label = QLabel("当前模型: 未选择")
        self.current_model_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        header_layout.addWidget(self.current_model_label)

        return header_layout

    def create_models_tab(self):
        """Create models management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        # Model actions
        self.add_btn = QPushButton("➕ 添加模型")
        self.add_btn.clicked.connect(self.add_model)
        toolbar_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ 编辑模型")
        self.edit_btn.clicked.connect(self.edit_model)
        toolbar_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ 删除模型")
        self.delete_btn.clicked.connect(self.delete_model)
        self.delete_btn.setProperty("class", "danger")
        self.delete_btn.setStyleSheet("color: white;")
        toolbar_layout.addWidget(self.delete_btn)

        toolbar_layout.addStretch()

        # Import/Export
        self.import_btn = QPushButton("📥 导入配置文件")
        self.import_btn.clicked.connect(self.import_config)
        toolbar_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("📤 导出配置文件")
        self.export_btn.clicked.connect(self.export_config)
        toolbar_layout.addWidget(self.export_btn)

        layout.addLayout(toolbar_layout)

        # Model table
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(5)
        self.model_table.setHorizontalHeaderLabels(["模型名称", "基础URL", "模型ID", "API密钥", "状态"])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.model_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.model_table.doubleClicked.connect(self.on_model_double_click)

        layout.addWidget(self.model_table)

        # Quick actions
        actions_layout = QHBoxLayout()

        self.switch_btn = QPushButton("🚀 切换到模型")
        self.switch_btn.clicked.connect(self.switch_to_model)
        self.switch_btn.setProperty("class", "success")
        self.switch_btn.setStyleSheet("color: white;")
        actions_layout.addWidget(self.switch_btn)

        self.test_btn = QPushButton("🔗 测试连接")
        self.test_btn.clicked.connect(self.test_model_connection)
        actions_layout.addWidget(self.test_btn)

        self.auto_env_btn = QPushButton("⚡ 自动设置环境变量")
        self.auto_env_btn.clicked.connect(self.auto_set_environment)
        actions_layout.addWidget(self.auto_env_btn)

        self.system_env_btn = QPushButton("🔧 设置系统环境变量")
        self.system_env_btn.clicked.connect(self.set_system_environment)
        actions_layout.addWidget(self.system_env_btn)

        layout.addLayout(actions_layout)

        # Environment variables
        layout.addWidget(QLabel("环境变量命令:"))
        self.env_text = QTextEdit()
        self.env_text.setMaximumHeight(120)
        self.env_text.setReadOnly(True)
        layout.addWidget(self.env_text)

        return tab

    def create_settings_tab(self):
        """Create settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Theme settings card
        theme_frame = QFrame()
        theme_frame.setFrameShape(QFrame.StyledPanel)
        theme_layout = QVBoxLayout(theme_frame)

        theme_title = QLabel("🎨 主题设置")
        theme_title.setFont(QFont("Arial", 14, QFont.Bold))
        theme_layout.addWidget(theme_title)

        theme_combo_layout = QHBoxLayout()
        theme_combo_layout.addWidget(QLabel("选择主题:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["深色主题", "浅色主题"])
        theme_combo.setCurrentText("深色主题")
        theme_combo.currentTextChanged.connect(self.change_theme)
        theme_combo_layout.addWidget(theme_combo)
        theme_combo_layout.addStretch()
        theme_layout.addLayout(theme_combo_layout)

        theme_desc = QLabel("深色主题适合在弱光环境下使用，浅色主题适合明亮环境")
        theme_desc.setStyleSheet("color: #888; font-style: italic;")
        theme_layout.addWidget(theme_desc)

        layout.addWidget(theme_frame)

        layout.addStretch()

        # Information
        info_label = QLabel("使用说明:")
        info_label.setStyleSheet("font-weight: bold; color: #4ec9b0;")
        layout.addWidget(info_label)

        info_text = """
1. 点击'添加模型'创建新的模型配置
2. 双击模型名称或点击'切换到模型'来切换模型
3. 使用'导入/导出配置文件'来备份或分享配置
4. '自动设置环境变量'为当前进程设置环境变量
5. 如果需要永久设置，使用'设置系统环境变量'
        """
        info_widget = QTextEdit(info_text)
        info_widget.setReadOnly(True)
        info_widget.setMaximumHeight(150)
        layout.addWidget(info_widget)

        return tab

    def load_initial_data(self):
        """Load initial data into the UI"""
        self.refresh_model_list()

    def refresh_model_list(self):
        """Refresh the model list"""
        self.model_table.setRowCount(0)

        models = self.model_manager.list_available_models()
        current_model = self.model_manager.get_current_model_info()

        for i, model in enumerate(models):
            self.model_table.insertRow(i)

            # Model name
            name_item = QTableWidgetItem(model['name'])
            self.model_table.setItem(i, 0, name_item)

            # Base URL
            url_item = QTableWidgetItem(model['base_url'])
            self.model_table.setItem(i, 1, url_item)

            # Model ID
            model_id_item = QTableWidgetItem(model['model'])
            self.model_table.setItem(i, 2, model_id_item)

            # API Key status
            api_status = "🔑 已设置" if model['api_key_set'] else "❌ 未设置"
            api_item = QTableWidgetItem(api_status)
            self.model_table.setItem(i, 3, api_item)

            # Current status
            status = "✅ 当前" if model['is_current'] else ""
            status_item = QTableWidgetItem(status)
            self.model_table.setItem(i, 4, status_item)

            # Highlight current model
            if model['is_current']:
                for col in range(5):
                    item = self.model_table.item(i, col)
                    if item:
                        item.setBackground(QColor('#2d2d2d'))

        # Update current model label
        if current_model:
            self.current_model_label.setText(f"当前模型: {current_model['name']}")
        else:
            self.current_model_label.setText("当前模型: 未选择")

        # Update environment commands
        self.update_environment_commands()

    def update_environment_commands(self):
        """Update environment commands display"""
        commands = self.model_manager.get_environment_commands()
        if commands:
            self.env_text.setPlainText('\n'.join(commands))
        else:
            self.env_text.setPlainText("未选择模型。请选择模型以查看环境变量命令。")

    def get_selected_model(self):
        """Get the selected model name"""
        selection = self.model_table.selectedItems()
        if not selection:
            return None
        return self.model_table.item(selection[0].row(), 0).text()

    def add_model(self):
        """Add a new model using a single form dialog"""
        dialog = AddModelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_model_data()
            name = data['name']
            base_url = data['base_url']
            model_id = data['model']
            api_key = data['api_key']

            if self.model_manager.add_model(name, base_url, model_id, api_key):
                self.refresh_model_list()
                self.statusBar().showMessage(f"模型 '{name}' 添加成功")
            else:
                QMessageBox.warning(self, "错误", f"模型 '{name}' 已存在")

    def edit_model(self):
        """Edit selected model using a single form dialog"""
        model_name = self.get_selected_model()
        if not model_name:
            QMessageBox.warning(self, "警告", "请选择要编辑的模型")
            return

        model = self.config_manager.get_model(model_name)
        if not model:
            QMessageBox.critical(self, "错误", "选择的模型未找到")
            return

        dialog = AddModelDialog(self, model)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_model_data()
            new_name = data['name']
            base_url = data['base_url']
            model_id = data['model']
            api_key = data['api_key']

            if self.model_manager.update_model(model.name, new_name, base_url, model_id, api_key):
                self.refresh_model_list()
                self.statusBar().showMessage(f"模型 '{new_name}' 更新成功")
            else:
                QMessageBox.critical(self, "错误", "更新模型失败")

    def delete_model(self):
        """Delete selected model"""
        model_name = self.get_selected_model()
        if not model_name:
            QMessageBox.warning(self, "警告", "请选择要删除的模型")
            return

        reply = QMessageBox.question(self, "确认删除", f"确定要删除模型 '{model_name}' 吗？",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.model_manager.delete_model(model_name):
                self.refresh_model_list()
                self.statusBar().showMessage(f"模型 '{model_name}' 删除成功")
            else:
                QMessageBox.critical(self, "错误", "删除模型失败")

    def on_model_double_click(self, index):
        """Handle double click on model"""
        self.switch_to_model()

    def switch_to_model(self):
        """Switch to selected model with progress indication"""
        model_name = self.get_selected_model()
        if not model_name:
            QMessageBox.warning(self, "警告", "请选择要切换到的模型")
            return

        # Create progress dialog
        self.progress_dialog = QMessageBox(self)
        self.progress_dialog.setWindowTitle("切换模型")
        self.progress_dialog.setText(f"正在切换到模型 '{model_name}'...")
        self.progress_dialog.setStandardButtons(QMessageBox.Cancel)

        # Add custom styles to the progress dialog
        self.progress_dialog.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QMessageBox QLabel {
                color: #cccccc;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
            }
            QMessageBox QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 8px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #005a9e;
            }
        """) if self.current_theme == "dark" else self.progress_dialog.setStyleSheet("""
            QMessageBox {
                background-color: #f8f8f8;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
            }
            QMessageBox QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 8px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #005a9e;
            }
        """)

        # Disable the switch button while processing
        self.switch_btn.setEnabled(False)
        self.switch_btn.setText("🔄 切换中...")

        # Create worker thread
        self.switch_worker = SwitchModelThread(self.model_manager, model_name)
        self.switch_worker.finished.connect(self.on_switch_finished)
        self.switch_worker.progress_update.connect(self.on_switch_progress_update)
        self.switch_worker.start()

        # Start the dialog
        self.progress_dialog.exec()

    def on_switch_progress_update(self, message):
        """Handle progress updates during model switching"""
        if self.progress_dialog:
            self.progress_dialog.setText(message)

    def on_switch_finished(self, result):
        """Handle model switch completion"""
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.done(0)

        # Re-enable the switch button
        self.switch_btn.setEnabled(True)
        self.switch_btn.setText("🚀 切换到模型")

        model_name = self.get_selected_model()

        if result["success"]:
            self.statusBar().showMessage(f"已切换到模型 '{model_name}'")

            env_result = result.get("environment_result", {})
            system_result = result.get("system_result", {})

            message = f"✅ 已切换到模型 '{model_name}'\n"
            message += f"环境变量: {env_result.get('message', '设置完成')}\n"

            if system_result.get("success"):
                message += "🔧 系统环境变量已永久设置"
                QMessageBox.information(self, "成功", message)
            else:
                message += "⚠️ 当前进程环境变量已设置 (重启后需重新设置)"
                QMessageBox.information(self, "成功", message)

            self.refresh_model_list()
        else:
            QMessageBox.critical(self, "错误", result.get("message", "切换模型失败"))

    def auto_set_environment(self):
        """Auto-set environment variables"""
        model_name = self.get_selected_model()
        if not model_name:
            QMessageBox.warning(self, "警告", "请选择要设置环境变量的模型")
            return

        # Switch model with auto_set_environment=False
        result = self.model_manager.switch_model(model_name, auto_set_environment=False)

        if result["success"]:
            env_result = self.model_manager.execute_environment_commands()

            if env_result["success"]:
                QMessageBox.information(self, "成功",
                    f"已切换到模型 '{model_name}'\n\n"
                    f"{env_result['message']}\n\n"
                    "⚠️ 环境变量仅在当前进程生效")
            else:
                QMessageBox.warning(self, "部分成功",
                    f"已切换到模型 '{model_name}'\n\n"
                    f"环境变量设置失败: {env_result['message']}")

            self.refresh_model_list()
        else:
            QMessageBox.critical(self, "错误", result.get("message", "切换模型失败"))

    def set_system_environment(self):
        """Set system environment variables"""
        model_name = self.get_selected_model()
        if not model_name:
            QMessageBox.warning(self, "警告", "请选择要设置系统环境变量的模型")
            return

        # Switch model first
        result = self.model_manager.switch_model(model_name, auto_set_environment=False)

        if not result["success"]:
            QMessageBox.critical(self, "错误", result.get("message", "切换模型失败"))
            return

        if self.model_manager.is_admin():
            sys_result = self.model_manager.set_system_environment_vars()

            if sys_result["success"]:
                QMessageBox.information(self, "成功",
                    f"已切换到模型 '{model_name}'\n\n"
                    f"{sys_result['message']}\n\n"
                    "✅ 系统环境变量已永久设置")
            else:
                QMessageBox.critical(self, "错误",
                    f"已切换到模型 '{model_name}'\n\n"
                    f"系统环境变量设置失败: {sys_result['message']}")
        else:
            reply = QMessageBox.question(self, "需要管理员权限",
                "设置系统环境变量需要管理员权限。\n\n"
                "是否重新启动程序以管理员身份运行？",
                QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                if self.model_manager.restart_with_admin():
                    QMessageBox.information(self, "信息", "程序将以管理员身份重新启动")
                    self.close()
                else:
                    QMessageBox.critical(self, "错误", "无法以管理员身份重新启动程序")

    def test_model_connection(self):
        """Test model connection"""
        model_name = self.get_selected_model()
        if not model_name:
            QMessageBox.warning(self, "警告", "请选择要测试连接的模型")
            return

        # Create progress dialog
        progress = QMessageBox(self)
        progress.setWindowTitle("测试连接")
        progress.setText(f"正在测试模型 '{model_name}'...")
        progress.setStandardButtons(QMessageBox.Cancel)

        # Create worker thread
        self.worker = WorkerThread(self.model_manager, model_name)
        self.worker.finished.connect(lambda result: self.on_test_finished(result, progress))
        self.worker.start()

        progress.exec()

    def on_test_finished(self, result, progress):
        """Handle test completion"""
        progress.done(0)

        if result["success"]:
            message = f"✅ {result['message']}\n"
            if "response_time" in result:
                message += f"⏱️ 响应时间: {result['response_time']:.2f}秒\n"
            if "status_code" in result:
                message += f"🔢 状态码: {result['status_code']}"
            QMessageBox.information(self, "测试成功", message)
        else:
            message = f"❌ {result['error']}\n"
            if "status_code" in result:
                message += f"🔢 状态码: {result['status_code']}"
            QMessageBox.critical(self, "测试失败", message)

    def import_config(self):
        """Import configuration from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", "", "JSON文件 (*.json)")

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Import models
                imported_count = 0
                for model_data in config_data.get("models", []):
                    name = model_data.get("name", "")
                    base_url = model_data.get("base_url", "")
                    model_id = model_data.get("model", "")
                    api_key = model_data.get("api_key", "")

                    if name and base_url and model_id:
                        if self.model_manager.add_model(name, base_url, model_id, api_key):
                            imported_count += 1

                # Import current model if exists
                current_model = config_data.get("current_model")
                if current_model:
                    self.model_manager.switch_model(current_model)

                self.refresh_model_list()
                self.statusBar().showMessage(f"成功导入 {imported_count} 个模型配置")

            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入配置文件失败: {str(e)}")

    def export_config(self):
        """Export configuration to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "claude_models.json", "JSON文件 (*.json)")

        if file_path:
            try:
                config_data = {
                    "models": [],
                    "current_model": self.config_manager.current_model,
                    "export_time": "2024-10-21",
                    "version": "1.0"
                }

                for name, model in self.config_manager.models.items():
                    config_data["models"].append({
                        "name": model.name,
                        "base_url": model.base_url,
                        "model": model.model,
                        "api_key": model.api_key
                    })

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)

                self.statusBar().showMessage(f"配置已导出到: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出配置文件失败: {str(e)}")

    def change_theme(self, theme_name):
        """Change application theme"""
        if theme_name == "浅色主题":
            self.current_theme = "light"
            self.apply_light_theme()
        else:
            self.current_theme = "dark"
            self.apply_dark_theme()

    def closeEvent(self, event):
        """Handle application close"""
        reply = QMessageBox.question(self, "确认退出", "确定要退出程序吗？",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Main entry point for PyQt application"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Claude Code Model Manager")
    app.setApplicationVersion("1.0")

    # Create and show main window
    window = ModernPyQtGUI()
    window.show()

    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()