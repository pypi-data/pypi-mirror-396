# Baicai WebUI

A modern web interface for the Baicai AI agent system, built with Streamlit.

## Overview

Baicai WebUI provides an intuitive and interactive web interface for interacting with the Baicai AI agent system. It offers visualization capabilities for agent workflows, real-time interaction with AI agents, and a user-friendly environment for managing and monitoring agent activities.

## Features

- 🎨 Modern, responsive web interface built with Streamlit
- 📊 Interactive workflow visualization with Mermaid diagrams
- 🔄 Real-time agent interaction and monitoring
- 📈 Flow-based agent workflow visualization
- 🔌 Seamless integration with Baicai Base framework

## Requirements

- Python 3.10 or higher (but less than 3.12)
- Poetry for dependency management
- Baicai Base package installed

## Installation

### 方法1: 使用 Poetry 安装（开发环境）

1. 确保已安装 Baicai Base:

```bash
cd ../baicai_base
poetry install
```

2. 安装 Baicai WebUI:

```bash
cd ../baicai_webui
poetry install
```

3. 设置环境变量:

```bash
cp .env.example .env
# 编辑 .env 文件配置
```

### 方法2: 构建自包含包（生产环境）

自包含包包含了完整的 Python 环境和所有依赖，无需安装任何环境即可运行。

#### 构建自包含包

1. 确保已安装所有依赖:

```bash
cd baicai_webui
poetry install
```

2. 运行构建脚本:

```bash
python build_self_contained.py
```

3. 构建完成后，自包含包位于 `dist/baicai-self-contained/` 目录

#### 使用自包含包

1. 将 `dist/baicai-self-contained/` 目录压缩分发给用户
2. 用户解压后，运行启动脚本即可：
   - **Windows**: 双击 `启动应用.bat`
   - **Linux/Mac**: 在终端运行 `./启动应用.sh`

#### 自包含包特点

✅ 完全自包含，无需安装 Python
✅ 无需安装任何依赖包
✅ 环境完全隔离，不会影响系统
✅ 即解压即用
✅ 跨平台兼容

## Running the Application

### 开发环境运行

1. 激活虚拟环境:

```bash
poetry shell
```

2. 启动 Web 界面:

```bash
baicai-webui
```

或者直接运行:

```bash
streamlit run baicai_webui/app.py
```

### 自包含包运行

1. 解压自包含包到任意位置
2. 进入解压后的目录
3. 运行启动脚本:
   - **Windows**: 双击 `启动应用.bat`
   - **Linux/Mac**: 在终端运行 `./启动应用.sh`
4. 应用会自动在浏览器中打开，地址通常是 http://localhost:8501

## Development

### Setup Development Environment

1. Install development dependencies:

```bash
poetry install --with dev
```

2. Run tests:

```bash
pytest
```

### 构建自包含包

1. 确保所有依赖已安装:

```bash
poetry install
```

2. 运行构建脚本:

```bash
python build_self_contained.py
```

3. 构建完成后，自包含包位于 `dist/baicai-self-contained/` 目录

4. 测试自包含包:

```bash
cd dist/baicai-self-contained
./启动应用.sh  # Linux/Mac
# 或
启动应用.bat   # Windows
```

#### 构建脚本功能

- 复制完整的 Python 环境（包括解释器和标准库）
- 复制所有已安装的依赖包
- 复制项目代码和相关模块
- 创建启动脚本（Windows 和 Linux/Mac）
- 自动配置 Python 路径
- 生成说明文档

### Project Structure

```
baicai_webui/
├── baicai_webui/           # Main package directory
│   ├── app.py              # Main Streamlit application
│   ├── components/         # UI components
│   └── utils/              # Utility functions
├── docs/                   # Documentation
├── tests/                  # Test files
├── build_self_contained.py # 自包含包构建脚本
├── pyproject.toml          # Project configuration
└── dist/                   # 构建输出目录
    └── baicai-self-contained/  # 自包含包
        ├── python/             # Python 环境
        ├── baicai_webui/       # 应用代码
        ├── baicai_base/        # 基础模块
        ├── baicai_dev/         # 开发模块
        ├── baicai_tutor/       # 教程模块
        ├── 启动应用.sh         # Linux/Mac 启动脚本
        ├── 启动应用.bat        # Windows 启动脚本
        └── README.txt          # 使用说明
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) License.
