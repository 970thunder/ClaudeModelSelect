# Claude Code Model Manager

A Python-based visual tool for managing and switching Claude Code models. This tool provides a user-friendly interface to configure different AI models and easily switch between them for use with Claude Code.

## Features

### Interface Features
- **Modern UI**: Supports a modernized PyQt interface with a professional look and feel.
- **Multiple Interface Options**: PyQt Modern Interface / Tkinter Enhanced Interface / Tkinter Classic Interface.
- **Dark Theme**: Eye-protection dark theme for comfortable visual experience.
- **Responsive Layout**: Adapts to different screen sizes and supports window scaling.

![image-20251023110041252](C:\Users\Hyper\AppData\Roaming\Typora\typora-user-images\image-20251023110041252.png)

### Core Functionality
- **Visual Model Management**: GUI interface for adding, editing, and deleting model configurations.
- **Smart Model Switching**: One-click integration of environment variables and system variable settings.
- **Configuration Management**: Import/export JSON configuration files for easy backup and sharing.
- **Environment Variable Management**: Automatically generates and sets environment variable commands.
- **Secure API Key Storage**: Encrypted storage for API keys.
- **Cross-Platform Support**: Supports Windows, macOS, and Linux.
- **Intelligent Permission Management**: Automatically detects administrator privileges with friendly prompts.

![image-20251023110055433](https://yhyper.dpdns.org/photostore/2025/10/image-20251023110055433.png)

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

## Usage

### Install Dependencies

```bash
# Using conda (Recommended)
conda env create -f environment.yml
conda activate Claude

# Using pip
pip install -r requirements.txt
```

### Run Application

```bash
# Main program (supports multiple interface selection)
python main.py

# PyQt specific launch (if you only want the PyQt interface)
python main_pyqt.py

# Classic Tkinter interface
python -c "from claude_model_manager.gui import ModelManagerGUI; app = ModelManagerGUI(); app.run()"

# Enhanced Tkinter interface
python -c "from claude_model_manager.modern_gui import ModernModelManagerGUI; app = ModernModelManagerGUI(); app.run()"
```

When running via code, an interface selection menu will be displayed (EXE runs default to PyQt):
```
🎯 Claude Code Model Manager
========================================
Please select interface type:
1. PyQt Modern Interface (Recommended)
2. Tkinter Enhanced Interface
3. Tkinter Classic Interface
========================================
Please enter selection (1-3, default 1):
```

### Adding Models

1. Click the "Add Model" button.
2. Fill in the model details:
   - **Model Name**: A descriptive name for the model.
   - **Base URL**: The API endpoint URL (e.g., `https://api.siliconflow.cn/`).
   - **Model**: The model identifier (e.g., `moonshotai/Kimi-K2-Instruct-0905`).
   - **API Key**: Your API key (optional, can be set later).

### Switching Models

1. Select a model from the list.
2. Click "Switch to Model" or double-click the model.
3. The tool will generate the necessary environment variable commands.

### Importing/Exporting Configurations

#### Import Configuration
1. Click the "Import Configuration" button.
2. Select a JSON configuration file.
3. The system will automatically import all model configurations and current model settings.

#### Export Configuration
1. Click the "Export Configuration" button.
2. Select the save location and filename.
3. The system will export all current model configurations and statuses.

#### Configuration Format Example
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

### Exporting Environment Variables

After switching to a model, you can:
- Copy the environment commands from the "Environment Variable Commands" section.
- Run these commands in your terminal to set the environment variables.
- Use the "Export Commands" button for a formatted view.

## Example Model Configurations

### Silicon Cloud Example
```
Model Name: Silicon Cloud Kimi
Base URL: https://api.siliconflow.cn/
Model: moonshotai/Kimi-K2-Instruct-0905
API Key: your_silicon_cloud_api_key
```

### Anthropic Example
```
Model Name: Anthropic Claude
Base URL: https://api.anthropic.com/
Model: claude-3-sonnet-20240229
API Key: your_anthropic_api_key
```

## Interface Features

### Modern Interface Design
- **🎨 Dark Theme**: Eye-protecting dark background to reduce visual fatigue.
- **🚀 Intuitive Layout**: Clear card-based design with rational partitioning.
- **✨ Beautiful Icons**: Rich visual elements to enhance user experience.
- **📊 Status Indicators**: Real-time status display with clear operational feedback.
- **🔧 Smart Help**: Friendly prompt messages and error handling.

### Interface Functional Areas
1. **🎯 Top Status Bar** - Displays current status and program information.
2. **📊 Current Model Card** - Clearly shows the currently active model.
3. **📋 Model List Area** - Modern tree-table displaying all models.
4. **⚡ Quick Action Bar** - One-click access to common functions.
5. **🔧 Environment Variable Area** - Displays and allows copying of environment variable commands.

## Project Structure

```
ClaudeModelSelect/
├── main.py                 # Main program entry (supports multiple interface selection)
├── main_pyqt.py            # PyQt specific launch script
├── requirements.txt        # Python dependencies
├── README.md              # This document
├── test_new_features.py   # Feature testing
├── test_modern_gui.py     # Modern GUI testing
└── claude_model_manager/  # Main package
    ├── __init__.py        # Package initialization
    ├── config.py          # Configuration management
    ├── model_manager.py   # Core model operations
    ├── gui.py             # Original Tkinter GUI
    ├── modern_gui.py      # Enhanced Tkinter modern GUI
    └── pyqt_gui.py        # PyQt modern GUI (supports import/export)
```

## Packaging Guide

The project is configured with automated build scripts, supporting one-click cross-platform packaging.

### Automated Packaging (Recommended)

Run the build script in the project root directory; the system will automatically identify the current OS and execute the corresponding packaging process:

```bash
python build.py
```

### Platform Specific Notes

#### Windows
- **Output**: `dist/ClaudeModelManager.exe` (Single-file executable)
- **Config**: Uses `build_windows.spec`

#### macOS
- **Output**: `dist/ClaudeModelManager.app` (macOS Application Bundle)
- **Config**: Uses `build_macos.spec`
- **DMG Image**: If `create-dmg` is installed (recommended `brew install create-dmg`), the script will automatically generate a `ClaudeModelManager.dmg` installation image.

### Manual Packaging (Advanced)

If you need manual control over packaging parameters, use the following commands:

**Windows:**
```bash
pyinstaller build_windows.spec
```

**macOS:**
```bash
pyinstaller build_macos.spec
```

### Interface Comparison

| Interface Type | Visuals | Performance | Completeness | Recommended Use Case |
|----------------|---------|-------------|--------------|----------------------|
| **PyQt Interface** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Production, needs professional look |
| **Enhanced Tkinter** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Balance of performance and functionality |
| **Classic Tkinter** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | High compatibility requirements |

## Configuration Storage

Model configurations are stored in:
- **Windows**: `%USERPROFILE%\.claude_model_manager\config.json`
- **Linux/macOS**: `~/.claude_model_manager/config.json`

## Security Notes

- API keys are stored in plain text in the configuration file.
- Consider using environment variables for API keys in production.
- The configuration file is stored in your user directory.

## Troubleshooting

### Common Issues

1. **GUI fails to open**: Ensure tkinter is installed (usually included with Python).
2. **Environment variables not working**: Ensure you run the export commands in your terminal.
3. **Model fails to switch**: Check if the model configuration is valid.

### Getting Help

If you encounter problems:
1. Check if all required fields are filled.
2. Verify that your API key is correct.
3. Ensure the Base URL is accessible.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=970thunder/ClaudeModelSelect&type=date&legend=top-left)](https://www.star-history.com/#970thunder/ClaudeModelSelect&type=date&legend=top-left)
