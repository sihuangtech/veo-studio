# Google Veo Studio

[English](README.md)

一个基于 Google Veo 3.1 模型（通过 Gemini API）的现代化桌面视频生成应用。使用 Python 和 PySide6 构建。

## 功能特性

- **GUI 图形界面**: 友好的桌面操作界面，无需使用命令行。
- **支持 Veo 3.1**: 使用 Google 最新的视频生成模型。
- **可自定义参数**:
    - 提示词 (Prompt) & 负向提示词 (Negative Prompt)
    - 宽高比 (16:9, 9:16)
    - 人物生成安全设置
    - 随机种子控制 (Seed) 以获得可复现的结果
- **实时日志**: GUI 界面内集成控制台输出，实时监控进度和错误。
- **模块化设计**: 代码结构清晰，分离了界面、逻辑和配置。

## 环境要求

- Python 3.10 或更高版本
- 启用了 Vertex AI / Gemini API 的 Google Cloud 项目
- Google Cloud API Key

## 安装指南

### 方法一：使用 uv（推荐）

[uv](https://github.com/astral-sh/uv) 是一个快速的 Python 包安装器和解析器。本项目已配置使用清华大学镜像源，在中国大陆可以获得更快的下载速度。

1.  **安装 uv**（如果尚未安装）:
    ```bash
    # Windows (PowerShell)
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **克隆仓库**（或下载源代码）:
    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

3.  **创建虚拟环境并安装依赖**:
    ```bash
    # uv 会自动创建虚拟环境并安装依赖
    uv sync
    ```

4.  **激活虚拟环境**:
    ```bash
    # Windows
    .venv\Scripts\activate
    
    # macOS/Linux
    source .venv/bin/activate
    ```

### 方法二：使用 pip（传统方式）

1.  **克隆仓库**（或下载源代码）:
    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

2.  **创建并激活虚拟环境**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Windows 用户: .venv\Scripts\activate
    ```

3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

## 配置说明

1.  复制示例配置文件:
    ```bash
    cp .env.example .env
    ```
2.  打开 `.env` 文件，将 `your_api_key_here` 替换为你真实的 Google Cloud API Key。

    *注意: 程序启动时会检查此文件，如果文件缺失或配置了占位符，会发出警告。*

3.  **设置网络代理 (中国大陆用户推荐)**:
    如果你在中国大陆无法访问 Google 服务，请在 `.env` 文件中取消 `HTTPS_PROXY` 的注释并设置你的代理地址：
    ```bash
    HTTPS_PROXY=http://127.0.0.1:7890
    ```

## 视频模型选择

Google 提供了多种 Veo 视频生成模型，你可以在 `.env` 文件中通过修改 `VEO_MODEL_NAME` 来切换：

| 模型名称 | 版本 | 描述 |
| :--- | :--- | :--- |
| `veo-3.1-generate-preview` | Veo 3 | 2025年10月15日发布，生成 720p 或 1080p 分辨率视频，支持 24 或 30 fps。 |
| `veo-3.1-fast-generate-preview` | Veo 3 | 2025年10月15日发布，生成 720p 或 1080p 分辨率视频，支持 24 或 30 fps。优化了生成速度，适用于快速迭代。 |
| `veo-3.0-generate-001` | Veo 3 | 2025年5月发布。已于2025年11月停用，被 Veo 3.1 取代。 |
| `veo-3.0-fast-generate-001` | Veo 3 | 2025年5月发布。已于2025年11月停用，被 Veo 3.1 取代。 |
| `veo-2.0-generate-001` | Veo 2 | 2024年12月发布，生成 1080p 分辨率视频，支持 24 或 30 fps。 |

*注意：*
- *所有模型生成的视频长度为 8 秒（部分早期 Veo 2 变体可能为 6 秒，但 API 统一返回整数时长）。*
- *Veo 3 系列模型支持原生音频生成和更高的真实感。*
- *请确保你的 Google Cloud 账号已获准访问对应的预览版模型。*
- *更多官方文档与模型详情，请参考：[Google Gemini API Video Docs](https://ai.google.dev/gemini-api/docs/video)*

## 使用方法

运行图形用户界面:

```bash
python3 run_gui.py
```

1.  在 **Prompt** (提示词) 输入框中输入你的视频描述。
2.  (可选) 输入 **Negative Prompt** (负向提示词) 以指定想要避免的内容。
3.  根据需要调整 **Aspect Ratio** (宽高比) 和 **Person Generation** (人物生成) 设置。
4.  (可选) 勾选 **Use Seed** (使用种子) 并设置一个数字以生成可复现的结果。
5.  点击 **Generate Video** (生成视频)。
6.  等待处理完成。右侧的日志面板会显示状态更新。
7.  完成后，界面会显示视频保存位置，并弹出成功提示。
8.  生成的视频将保存在项目文件夹下的 `output` 目录中。

## 项目结构

- `run_gui.py`: GUI 应用程序启动脚本。
- `main.py`: 命令行接口入口。
- `app/`: 源代码目录。
    - `gui.py`: GUI 主窗口实现。
    - `veo_client.py`: 与 Google GenAI API 交互的核心逻辑。
    - `config.py`: 配置管理。
    - `utils.py`: 通用工具函数。
- `.env`: API 密钥配置文件。
- `pyproject.toml`: 项目元数据和依赖配置 (用于 uv)。
- `uv.toml`: UV 配置文件，包含清华镜像源设置。

## 故障排除

- **API Key 错误**: 确保你的 API Key 有效，并且在 Google Cloud Console 中有权访问 Veo 模型。
- **配额限制**: 视频生成模型通常有严格的配额限制。如果生成反复失败，请检查你的 Google Cloud 配额。
- **日志**: 查看应用程序中的 "Console Output" (控制台输出) 面板以获取详细的错误信息。

## 开源协议

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

本项目由 **彩旗工作室 (SK Studio)** 维护。

- **官网**: [www.skstudio.cn](https://www.skstudio.cn)
- **邮箱**: [contact@skstudio.cn](mailto:contact@skstudio.cn)
- **彩旗开源交流群**: [点击加入群聊](https://qm.qq.com/q/KUCcyyYtyi)
