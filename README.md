# Google Veo Studio

[简体中文文档](README_zh-CN.md)

A modern video generation app powered by Google Veo / Gemini API, with command-line, PySide6 desktop GUI, and Gradio web UI options.

## Features

- **Multiple Interfaces**: Command-line, desktop GUI, and local web UI.
- **Multiple Veo Models**: Built-in model catalog for currently usable Veo video models; explicitly deprecated models are not included by default.
- **Web Authentication Input**: The web UI supports AI Studio API Key and Enterprise Service Account auth without manually editing `.env`.
- **Reference Video Analysis**: Analyze existing videos to generate optimized prompts for similar video generation.
- **Customizable Parameters**:
  - Prompt & Negative Prompt
  - Aspect Ratio (16:9, 9:16)
  - Person Generation Safety Settings
  - Seed Control for reproducible results
- **Real-time Logging**: Integrated console output within the GUI for monitoring progress and errors.
- **Modular Design**: Clean code structure separating GUI, logic, and configuration.

## Prerequisites

- Python 3.10 or higher
- A Google Cloud Project with Vertex AI / Gemini API enabled
- A Google AI Studio API Key, or a Google Cloud Service Account

## Installation

### Method 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. This project is configured to use Tsinghua University mirror for faster downloads in China.

1. **Install uv** (if not already installed):

    ```bash
    # On Windows (PowerShell)
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # On macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **Clone the repository** (or download the source code):

    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

3. **Create virtual environment and install dependencies**:

    ```bash
    # uv will automatically create a virtual environment and install dependencies
    uv sync
    ```

4. **Activate the virtual environment**:

    ```bash
    # On Windows
    .venv\Scripts\activate
    
    # On macOS/Linux
    source .venv/bin/activate
    ```

### Method 2: Using pip (Traditional)

1. **Clone the repository** (or download the source code):

    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

2. **Create and activate a virtual environment**:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Copy the example configuration file:

    ```bash
    cp .env.example .env
    ```

2. Choose an authentication mode.

    **Google AI Studio API Key (most common for individual developers)**

    ```bash
    GOOGLE_AUTH_MODE=ai_studio
    GOOGLE_API_KEY=your_api_key_here
    ```

    **Gemini Enterprise / Google Cloud Service Account (enterprise use)**

    ```bash
    GOOGLE_AUTH_MODE=enterprise
    GOOGLE_CLOUD_PROJECT=your-gcp-project-id
    GOOGLE_CLOUD_LOCATION=us-central1
    GOOGLE_SERVICE_ACCOUNT_FILE=C:\path\to\service-account.json
    ```

    `GOOGLE_SERVICE_ACCOUNT_FILE` can be omitted if your environment already has Google Application Default Credentials configured. The web UI also lets users choose the auth mode and upload a Service Account JSON file on the page.

    *Note: The application validates the selected authentication configuration and alerts you if required values are missing or placeholders are still present.*

3. **Network Proxy Settings (Optional)**:
    If you are in a region where Google services are restricted (e.g., Chinese Mainland), you can configure a proxy by uncommenting and setting `HTTPS_PROXY` in your `.env` file:

    ```bash
    HTTPS_PROXY=http://127.0.0.1:7890
    ```

4. **Custom API Endpoint (Optional)**:
    If you are using an API gateway / reverse proxy to access the Google GenAI API, you can override the SDK base URL in your `.env` file:

    ```bash
    GOOGLE_GENAI_BASE_URL=https://your-proxy.example.com
    ```

## Model Selection

Google provides multiple Veo video generation models. You can switch between them in the desktop GUI or the web UI. The default catalog includes currently usable models; if a model is explicitly deprecated or shut down by Google, do not keep it in the config files.

1. Locate the **Model Selection** dropdown in the left panel.
2. Select your desired model.
3. The selection is automatically saved to `config.json`.

### Veo Video Models

| Model Name | Type | Description |
| :--- | :--- | :--- |
| `veo-3.1-generate-preview` | Veo 3.1 | High-fidelity video generation with native audio and advanced controls. |
| `veo-3.1-fast-generate-preview` | Veo 3.1 | Faster Veo 3.1 variant for rapid iteration. |
| `veo-3.1-lite-generate-preview` | Veo 3.1 | Lower-cost Veo 3.1 variant for high-volume workflows. |
| `veo-3.0-generate-001` | Veo 3.0 | General Veo 3 video generation model with audio support. |
| `veo-3.0-fast-generate-001` | Veo 3.0 | Faster Veo 3 video generation model with audio support. |
| `veo-2.0-generate-001` | Veo 2.0 | Earlier Veo video generation model without native audio. |

### Gemini Reference Analysis Models

These models are used only for reference video analysis, prompt rewriting, and copywriting. They do not generate videos directly.

| Model Name | Description |
| :--- | :--- |
| `gemini-3.5-flash` | Stable, fast text/multimodal analysis model. |
| `gemini-3.1-pro-preview` | Preview model for advanced reasoning and complex multimodal analysis. |
| `gemini-3-flash-preview` | Default model for reference video analysis. |
| `gemini-3.1-flash-lite` | Low-latency, low-cost lightweight analysis model. |
| `gemini-3.1-flash-lite-preview` | Preview lightweight analysis model. |
| `gemini-2.5-pro` | Stable model for complex analysis and reasoning. |
| `gemini-2.5-flash` | Stable low-latency multimodal analysis model. |
| `gemini-2.5-flash-lite` | Stable cost-efficient lightweight model. |

*Notes:*

- *Supported resolution, duration, audio, and pricing vary by model; check the official docs and your account access.*
- *Veo 3 series models support native audio generation; Veo 2 does not support native audio.*
- *Ensure your Google Cloud account is allowlisted for the corresponding preview models.*
- *For more official documentation and model details, please refer to: [Google Gemini API Video Docs](https://ai.google.dev/gemini-api/docs/video)*

## Usage

Run the graphical user interface:

```bash
python3 gui.py
```

Run the web user interface:

```bash
python3 web.py
```

Then open `http://127.0.0.1:7860`. The web UI lets users choose the authentication mode, enter a Google AI Studio API key or upload a Service Account JSON file, and choose both the Veo video model and the Gemini model used for reference video analysis without editing `.env`.

The web UI is built with Gradio. If you use uv, install/sync dependencies with:

```bash
uv sync
```

### Standard Video Generation

1. Select the desired model from the **Model Selection** dropdown.
2. Enter your video description in the **Prompt** box.
3. (Optional) Enter a **Negative Prompt** to specify what to avoid.
4. Adjust **Aspect Ratio** and **Person Generation** settings as needed.
5. (Optional) Check **Use Seed** and set a number for reproducible generation.
6. Click **Generate Video**.
7. Wait for the process to complete. The log panel on the right will show status updates.
8. Once finished, the video location will be displayed, and a success message will appear.
9. Generated videos are saved in the `output` directory within the project folder.

### Reference Video Analysis (Optional)

If you have an existing video and want to generate a similar video:

1. Click **Browse** in the **Reference Video** section and select your video file (mp4/mov).
2. (Optional) Enter a brief description in the **Prompt** box to guide the analysis.
3. Click **Analyze Video** to analyze the reference video and generate an optimized prompt.
4. The analysis result will be displayed in the log panel.
5. Adjust other settings (aspect ratio, seed, etc.) as needed.
6. Click **Generate Video** to create a video based on the reference.

## Project Structure

- `gui.py`: Launch script for the GUI application.
- `main.py`: Command-line interface entry point.
- `app/`: Source code directory.
  - `gui.py`: Main GUI window implementation.
  - `veo_client.py`: Core logic for interacting with the Google GenAI API.
  - `config.py`: Configuration management.
  - `utils.py`: Utility functions.
  - `prompts/`: Prompt templates for video analysis.
- `config.json`: Stores user preferences (e.g., selected model).
- `.env`: Configuration file for API keys.
- `pyproject.toml`: Project metadata and dependencies (for uv).
- `uv.toml`: UV configuration with Tsinghua mirror settings.

## Troubleshooting

- **Authentication Errors**: For AI Studio, ensure the API key is valid and has Veo access. For Enterprise / Service Account, ensure the project ID, location, service account permissions, and credentials file are correct.
- **Quota Limits**: Video generation models often have strict quota limits. Check your Google Cloud quota if generation fails repeatedly.
- **Logs**: Check the "Console Output" panel in the application for detailed error messages.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Maintained by **SK Studio**.

- **Website**: [www.skstudio.cn](https://www.skstudio.cn)
- **Email**: [contact@skstudio.cn](mailto:contact@skstudio.cn)
- **QQ Group**: [Join Chat](https://qm.qq.com/q/KUCcyyYtyi)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sihuangtech/veo-studio&type=Date)](https://star-history.com/#sihuangtech/veo-studio&Date)
