# Google Veo Studio

[English](README.md)

一个基于 Google Veo / Gemini API 的现代化视频生成应用，提供命令行、PySide6 桌面 GUI 和 Gradio 网页 UI。

## 功能特性

- **多种界面**: 支持命令行、桌面 GUI 和本地网页 UI。
- **支持多种 Veo 模型**: 内置当前可用的 Veo 视频生成模型，明确弃用的模型不会放入默认列表。
- **网页端认证输入**: Web UI 可以选择 AI Studio API Key 或 Enterprise Service Account，不必手动修改 `.env`。
- **参考视频分析**: 分析现有视频，生成优化的提示词用于生成类似视频。
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
- Google AI Studio API Key，或 Google Cloud Service Account

## 安装指南

### 方法一：使用 uv（推荐）

[uv](https://github.com/astral-sh/uv) 是一个快速的 Python 包安装器和解析器。本项目已配置使用清华大学镜像源，在中国大陆可以获得更快的下载速度。

1. **安装 uv**（如果尚未安装）:

    ```bash
    # Windows (PowerShell)
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **克隆仓库**（或下载源代码）:

    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

3. **创建虚拟环境并安装依赖**:

    ```bash
    # uv 会自动创建虚拟环境并安装依赖
    uv sync
    ```

4. **激活虚拟环境**:

    ```bash
    # Windows
    .venv\Scripts\activate
    
    # macOS/Linux
    source .venv/bin/activate
    ```

### 方法二：使用 pip（传统方式）

1. **克隆仓库**（或下载源代码）:

    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

2. **创建并激活虚拟环境**:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Windows 用户: .venv\Scripts\activate
    ```

3. **安装依赖**:

    ```bash
    pip install -r requirements.txt
    ```

## 配置说明

1. 复制示例配置文件:

    ```bash
    cp .env.example .env
    ```

2. 选择认证方式。

    **Google AI Studio API Key（个人开发最常用）**

    ```bash
    GOOGLE_AUTH_MODE=ai_studio
    GOOGLE_API_KEY=your_api_key_here
    ```

    **Gemini Enterprise / Google Cloud Service Account（企业级）**

    ```bash
    GOOGLE_AUTH_MODE=enterprise
    GOOGLE_CLOUD_PROJECT=your-gcp-project-id
    GOOGLE_CLOUD_LOCATION=us-central1
    GOOGLE_SERVICE_ACCOUNT_FILE=C:\path\to\service-account.json
    ```

    `GOOGLE_SERVICE_ACCOUNT_FILE` 可以省略；如果你的环境已经配置了 Google Application Default Credentials，SDK 会尝试使用默认凭据。Web UI 也支持在页面里选择认证方式并上传 Service Account JSON。

    *注意: 程序启动时会检查对应认证配置，如果缺失或配置了占位符，会发出警告。*

3. **设置网络代理 (中国大陆用户推荐)**:
    如果你在中国大陆无法访问 Google 服务，请在 `.env` 文件中取消 `HTTPS_PROXY` 的注释并设置你的代理地址：

    ```bash
    HTTPS_PROXY=http://127.0.0.1:7890
    ```

4. **自定义 API 端点 (可选)**:
    如果你使用了 API 网关 / 反向代理来访问 Google GenAI API，可以在 `.env` 文件中覆盖 SDK 的 base URL：

    ```bash
    GOOGLE_GENAI_BASE_URL=https://your-proxy.example.com
    ```

## 模型选择

Google 提供了多种 Veo 视频生成模型。你可以在桌面 GUI 或 Web UI 中直接切换模型。默认列表只放当前可用模型；如果官方明确标记某个模型已弃用或停用，就不要再写入配置文件。

1. 在左侧面板找到 **Model Selection** (模型选择) 下拉框。
2. 选择你想要使用的模型。
3. 选择会自动保存到 `config.json` 文件中。

### Veo 视频模型

| 模型名称 | 类型 | 描述 |
| :--- | :--- | :--- |
| `veo-3.1-generate-preview` | Veo 3.1 | 高质量视频生成，支持原生音频和更强控制能力。 |
| `veo-3.1-fast-generate-preview` | Veo 3.1 | Veo 3.1 快速版本，适合更快迭代。 |
| `veo-3.1-lite-generate-preview` | Veo 3.1 | 更低成本的 Veo 3.1 版本，适合高频生成。 |
| `veo-3.0-generate-001` | Veo 3.0 | 通用 Veo 3 视频生成模型，支持音频。 |
| `veo-3.0-fast-generate-001` | Veo 3.0 | 更快的 Veo 3 视频生成模型，支持音频。 |
| `veo-2.0-generate-001` | Veo 2.0 | 早期 Veo 视频生成模型，不支持原生音频。 |

### Gemini 参考视频分析模型

这些模型只用于“参考视频分析、提示词改写和文案生成”，不用于直接生成视频。

| 模型名称 | 描述 |
| :--- | :--- |
| `gemini-3.5-flash` | 稳定、快速的文本/多模态分析模型。 |
| `gemini-3.1-pro-preview` | 预览版高级推理和复杂多模态分析模型。 |
| `gemini-3-flash-preview` | 默认参考视频分析模型。 |
| `gemini-3.1-flash-lite` | 低延迟、低成本的轻量分析模型。 |
| `gemini-3.1-flash-lite-preview` | 预览版轻量分析模型。 |
| `gemini-2.5-pro` | 稳定复杂分析和推理模型。 |
| `gemini-2.5-flash` | 稳定低延迟多模态分析模型。 |
| `gemini-2.5-flash-lite` | 稳定低成本轻量模型。 |

*注意：*

- *不同模型支持的分辨率、时长、音频和价格可能不同，请以官方文档和你的账号权限为准。*
- *Veo 3 系列支持原生音频生成，Veo 2 不支持原生音频。*
- *请确保你的 Google Cloud 账号已获准访问对应的预览版模型。*
- *更多官方文档与模型详情，请参考：[Google Gemini API Video Docs](https://ai.google.dev/gemini-api/docs/video)*

## 使用方法

运行图形用户界面:

```bash
python3 gui.py
```

运行网页用户界面:

```bash
python3 web.py
```

启动后打开 `http://127.0.0.1:7860`。网页版本支持在页面中选择认证方式、填写 Google AI Studio API Key 或上传 Service Account JSON，并选择 Veo 视频模型和 Gemini 参考视频分析模型；页面中填写的认证信息只用于本次请求，不会写入 `.env`。

网页 UI 使用 Gradio 构建。如果使用 uv 安装依赖，运行：

```bash
uv sync
```

### 标准视频生成

1. 从 **Model Selection** (模型选择) 下拉框中选择想要使用的模型。
2. 在 **Prompt** (提示词) 输入框中输入你的视频描述。
3. (可选) 输入 **Negative Prompt** (负向提示词) 以指定想要避免的内容。
4. 根据需要调整 **Aspect Ratio** (宽高比) 和 **Person Generation** (人物生成) 设置。
5. (可选) 勾选 **Use Seed** (使用种子) 并设置一个数字以生成可复现的结果。
6. 点击 **Generate Video** (生成视频)。
7. 等待处理完成。右侧的日志面板会显示状态更新。
8. 完成后，界面会显示视频保存位置，并弹出成功提示。
9. 生成的视频将保存在项目文件夹下的 `output` 目录中。

### 参考视频分析（可选）

如果你有一个现有视频，想要生成类似的视频：

1. 在 **Reference Video** (参考视频) 部分点击 **Browse** (浏览) 并选择你的视频文件（mp4/mov）。
2. (可选) 在 **Prompt** (提示词) 输入框中输入简短描述以引导分析。
3. 点击 **Analyze Video** (分析视频) 来分析参考视频并生成优化的提示词。
4. 分析结果将显示在日志面板中。
5. 根据需要调整其他设置（宽高比、种子等）。
6. 点击 **Generate Video** (生成视频) 基于参考视频创建新视频。

## 项目结构

- `gui.py`: GUI 应用程序启动脚本。
- `main.py`: 命令行接口入口。
- `app/`: 源代码目录。
  - `gui.py`: GUI 主窗口实现。
  - `veo_client.py`: 与 Google GenAI API 交互的核心逻辑。
  - `config.py`: 配置管理。
  - `utils.py`: 通用工具函数。
  - `prompts/`: 视频分析提示词模板。
- `config.json`: 存储用户首选项 (例如选中的模型)。
- `.env`: API 密钥配置文件。
- `pyproject.toml`: 项目元数据和依赖配置 (用于 uv)。
- `uv.toml`: UV 配置文件，包含清华镜像源设置。

## 故障排除

- **认证错误**: 如果使用 AI Studio，确保 API Key 有效并有权访问 Veo 模型；如果使用 Enterprise / Service Account，确保项目 ID、区域、服务账号权限和凭据文件正确。
- **配额限制**: 视频生成模型通常有严格的配额限制。如果生成反复失败，请检查你的 Google Cloud 配额。
- **日志**: 查看应用程序中的 "Console Output" (控制台输出) 面板以获取详细的错误信息。

## 开源协议

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

本项目由 **彩旗工作室 (SK Studio)** 维护。

- **官网**: [www.skstudio.cn](https://www.skstudio.cn)
- **邮箱**: [contact@skstudio.cn](mailto:contact@skstudio.cn)
- **彩旗开源交流群**: [点击加入群聊](https://qm.qq.com/q/KUCcyyYtyi)

## 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=sihuangtech/veo-studio&type=Date)](https://star-history.com/#sihuangtech/veo-studio&Date)
