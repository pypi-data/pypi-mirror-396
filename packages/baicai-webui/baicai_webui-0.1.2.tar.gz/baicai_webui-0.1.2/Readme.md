# Baicai WebUI

Baicai WebUI：面向教学的白菜人工智能平台Web界面。

## 概述

Baicai WebUI 为交互式教材打造一个示例，它提供了学情调研、个性化教材生成、个性化问答、人工智能实验智能体、智能体工作流的可视化功能、与 AI 智能体的实时交互，以及用于管理和监控智能体活动的用户友好环境。

## 功能特性

- 🎨 基于 Streamlit 构建的现代化、响应式 Web 界面
- 📊 使用 Mermaid 图表的交互式工作流可视化
- 🔄 实时智能体交互和监控
- 📈 基于流程的智能体工作流可视化

## 系统要求

- Python 3.10 或更高版本（但低于 3.12）
- Poetry 用于依赖管理
- **Windows 用户**：需要提前安装 Microsoft Visual C++ Redistributable（Microsoft Visual C++ 可再发行组件包）。请根据您的系统架构下载并安装 [Microsoft Visual C++ 2015-2022 Redistributable](https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist)（x64 版本适用于大多数现代 Windows 系统）

## 安装

如果不想安装，直接进入百度网盘：https://pan.baidu.com/s/1T8p-WZ48q46k-DHccah6GQ?pwd=3edj 提取码:3edj，下载相关文件，具体见[运行应用](#运行应用)

### 方法1: 使用 pip 安装（推荐）

这是最简单的安装方式，适用于大多数用户。

```bash
pip install baicai-webui
```

安装完成后，可以通过以下命令启动应用：

```bash
baicai-webui
```

### 方法2: 使用 Poetry 安装（开发环境）

1. 安装 Baicai WebUI 及其依赖:

```bash
cd baicai_webui
poetry install
```


### 方法3: 构建自包含包（生产环境）

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
   - **Linux/Mac**: 在终端运行 `./启动应用.sh`(无法使用，勿用)

#### 自包含包特点

✅ 完全自包含，无需安装 Python
✅ 无需安装任何依赖包
✅ 环境完全隔离，不会影响系统
✅ 即解压即用
✅ 跨平台兼容

## 运行应用

### 前期准备

如果需要使用教材功能，需要做如下设置：

1. **下载资源文件**

   打开百度网盘：https://pan.baidu.com/s/1T8p-WZ48q46k-DHccah6GQ?pwd=3edj 提取码:3edj

2. **必需文件**（必须下载）：
   - `.baicai.zip`：软件运行环境（可自动生成）和示例数据
   - `数据和工作流.zip`：教材配套实验资源

3. **可选文件**（仅在网络环境受限时下载）：
   - `.cache.zip`：缓存数据
   - `.fastai.zip`：FastAI 相关数据

4. **解压和配置**：

   解压下载的 zip 文件，并按以下规则放置：

   - **必需文件夹**（解压 `.baicai.zip` 后）：
     - 将 `.baicai` 文件夹放入用户主目录
       - Windows: `C:\Users\你的用户名\`
       - Linux/Mac: `~/` 或 `/home/你的用户名/`

   - **可选文件夹**（仅在下载了对应 zip 文件时）：
     - 将 `.cache` 文件夹放入用户主目录
     - 将 `.fastai` 文件夹放入用户主目录

### pip 安装方式运行

如果使用 pip 安装，直接运行：

```bash
baicai-webui
```

### Poetry 安装方式运行


1. 启动 Web 界面:

```bash
baicai-webui
```

2. 或者直接运行:

```bash
streamlit run baicai_webui/app.py
```


### 项目结构

```
baicai_webui/
├── baicai_webui/           # 主包目录
│   ├── app.py              # 主 Streamlit 应用
│   ├── components/         # UI 组件
│   └── utils/              # 工具函数
├── docs/                   # 文档
├── tests/                  # 测试文件
├── build_self_contained.py # 自包含包构建脚本
├── pyproject.toml          # 项目配置
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

## 贡献

1. Fork 本仓库
2. 创建功能分支
3. 进行您的更改
4. 运行测试并确保通过
5. 提交 Pull Request

## 许可证

本项目采用 [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) 许可证。
