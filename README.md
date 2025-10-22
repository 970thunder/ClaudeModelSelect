# Claude Code 模型管理器

一个基于Python的可视化工具，用于管理和切换Claude Code模型。该工具提供用户友好的界面来配置不同的AI模型，并轻松在它们之间切换以供Claude Code使用。

## 特性

### 界面特性
- **💎 现代化UI界面**: 支持PyQt现代化界面，专业外观设计
- **🎨 多种界面选择**: PyQt现代化界面 / Tkinter增强界面 / Tkinter经典界面
- **🌙 深色主题**: 护眼深色主题，视觉效果舒适
- **📱 响应式布局**: 适应不同屏幕尺寸，支持窗口缩放

### 核心功能
- **🔧 可视化模型管理**: 中文GUI界面，用于添加、编辑和删除模型配置
- **🚀 智能模型切换**: 一键集成环境变量和系统变量设置
- **📁 配置文件管理**: 导入/导出JSON配置文件，方便备份和分享
- **⚡ 环境变量管理**: 自动生成并设置环境变量命令
- **🛡️ 安全的API密钥存储**: 加密存储API密钥
- **🌐 跨平台支持**: 支持Windows、macOS和Linux
- **🎯 智能权限管理**: 自动检测管理员权限，友好提示

## Installation

### Prerequisites

- Python 3.11 or higher
- Conda (recommended) or pip

### Using Conda (Recommended)

1. Clone or download this repository
2. Create and activate the conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate Claude
   ```

### Using pip

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 安装依赖

```bash
# 使用conda (推荐)
conda env create -f environment.yml
conda activate Claude

# 使用pip
pip install -r requirements.txt
```

### 运行应用程序

```bash
# 主程序（支持多种界面选择）
python main.py

# PyQt专用启动（如果只想使用PyQt界面）
python main_pyqt.py

# 经典Tkinter界面
python -c "from claude_model_manager.gui import ModelManagerGUI; app = ModelManagerGUI(); app.run()"

# 增强Tkinter界面
python -c "from claude_model_manager.modern_gui import ModernModelManagerGUI; app = ModernModelManagerGUI(); app.run()"
```

启动后会显示界面选择菜单：
```
🎯 Claude Code 模型管理器
========================================
请选择界面类型:
1. PyQt 现代化界面 (推荐)
2. Tkinter 增强界面
3. Tkinter 经典界面
========================================
请输入选择 (1-3, 默认为1):
```

### 添加模型

1. 点击"添加模型"按钮
2. 填写模型详细信息：
   - **模型名称**: 模型的描述性名称
   - **基础URL**: API端点URL（例如：`https://api.siliconflow.cn/`）
   - **模型**: 模型标识符（例如：`moonshotai/Kimi-K2-Instruct-0905`）
   - **API密钥**: 您的API密钥（可选，可以稍后设置）

### 切换模型

1. 从列表中选择一个模型
2. 点击"切换到模型"或双击模型
3. 工具将生成必要的环境变量命令

### 导入/导出配置文件

#### 导入配置
1. 点击"导入配置文件"按钮
2. 选择JSON格式的配置文件
3. 系统会自动导入所有模型配置和当前模型设置

#### 导出配置
1. 点击"导出配置文件"按钮
2. 选择保存位置和文件名
3. 系统会导出当前所有模型配置和状态

#### 配置文件格式示例
```json
{
  "models": [
    {
      "name": "DeepSeek-V3.1-Terminus",
      "base_url": "https://api.siliconflow.cn/",
      "model": "deepseek-ai/DeepSeek-V3.1-Terminus",
      "api_key": "your_api_key_here"
    }
  ],
  "current_model": "DeepSeek-V3.1-Terminus",
  "export_time": "2024-10-21",
  "version": "1.0"
}
```

### 导出环境变量

切换到模型后，您可以：
- 从"环境变量命令"部分复制环境命令
- 在终端中运行这些命令来设置环境变量
- 使用"导出命令"按钮获取格式化视图

## 示例模型配置

### Silicon Cloud 示例
```
模型名称: Silicon Cloud Kimi
基础URL: https://api.siliconflow.cn/
模型: moonshotai/Kimi-K2-Instruct-0905
API密钥: your_silicon_cloud_api_key
```

### Anthropic 示例
```
模型名称: Anthropic Claude
基础URL: https://api.anthropic.com/
模型: claude-3-sonnet-20240229
API密钥: your_anthropic_api_key
```

## 界面特性

### 现代化界面设计
- **🎨 深色主题**: 护眼深色背景，减少视觉疲劳
- **🚀 直观布局**: 清晰的卡片式设计，分区合理
- **✨ 精美图标**: 丰富的视觉元素提升用户体验
- **📊 状态指示**: 实时状态显示，操作反馈明确
- **🔧 智能帮助**: 友好的提示信息和错误处理

### 界面功能区域
1. **🎯 顶部状态栏** - 显示当前状态和程序信息
2. **📊 当前模型卡片** - 清晰展示当前激活的模型
3. **📋 模型列表区域** - 现代化树形表格显示所有模型
4. **⚡ 快速操作栏** - 常用功能一键可达
5. **🔧 环境变量区域** - 显示和复制环境变量命令

## Project Structure

```
ClaudeModelSelect/
├── main.py                 # 主程序入口（支持多种界面选择）
├── main_pyqt.py            # PyQt专用启动脚本
├── requirements.txt        # Python依赖
├── README.md              # 本文档
├── test_new_features.py   # 功能测试
├── test_modern_gui.py     # 现代化GUI测试
└── claude_model_manager/  # 主要包
    ├── __init__.py        # 包初始化
    ├── config.py          # 配置管理
    ├── model_manager.py   # 核心模型操作
    ├── gui.py             # 原始Tkinter GUI界面
    ├── modern_gui.py      # 增强Tkinter现代化界面
    └── pyqt_gui.py        # PyQt现代化界面（支持导入导出）
```
完整打包命令：
  pyinstaller --onefile --noconsole --name ClaudeModelManager --add-data "claude_model_manager;claude_model_manager"
   --hidden-import PyQt5 --hidden-import PyQt5.QtCore --hidden-import PyQt5.QtGui --hidden-import PyQt5.QtWidgets
  --hidden-import requests main_pyqt.py

  简化的打包选项：
  pyinstaller main_pyqt.py

  pyinstaller --onefile --noconsole main_pyqt.py

### 主要特性对比

| 界面类型 | 外观效果 | 性能 | 功能完整性 | 推荐场景 |
|---------|---------|------|-----------|----------|
| **PyQt界面** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 生产环境，需要专业外观 |
| **增强Tkinter** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 平衡性能和功能性 |
| **经典Tkinter** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 兼容性要求高 |

## Configuration Storage

Model configurations are stored in:
- **Windows**: `%USERPROFILE%\.claude_model_manager\config.json`
- **Linux/macOS**: `~/.claude_model_manager/config.json`

## Security Notes

- API keys are stored in plain text in the configuration file
- Consider using environment variables for API keys in production
- The configuration file is stored in your user directory

## 故障排除

### 常见问题

1. **GUI无法打开**: 确保已安装tkinter（通常包含在Python中）
2. **环境变量不工作**: 确保在终端中运行导出命令
3. **模型无法切换**: 检查模型配置是否有效

### 获取帮助

如果遇到问题：
1. 检查所有必填字段是否已填写
2. 验证您的API密钥是否正确
3. 确保基础URL可访问

## License

This project is provided as-is for educational and personal use.