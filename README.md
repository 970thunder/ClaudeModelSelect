# Claude Code 模型管理器

一个基于Python的可视化工具，用于管理和切换Claude Code模型。该工具提供用户友好的界面来配置不同的AI模型，并轻松在它们之间切换以供Claude Code使用。

## 特性

- **可视化模型管理**: 中文GUI界面，用于添加、编辑和删除模型配置
- **轻松模型切换**: 一键在不同模型之间切换
- **环境变量管理**: 自动生成环境变量命令
- **安全的API密钥存储**: 加密存储API密钥
- **跨平台支持**: 支持Windows、macOS和Linux

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

### 运行应用程序

```bash
python main.py
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

## Project Structure

```
ClaudeModelSelect/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── claude_model_manager/  # Main package
    ├── __init__.py        # Package initialization
    ├── config.py          # Configuration management
    ├── model_manager.py   # Core model operations
    └── gui.py            # GUI interface
```

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