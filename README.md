# Google Veo Studio

[简体中文文档](README_zh-CN.md)

A modern desktop GUI application for generating videos using Google's Veo 3.1 model via the Gemini API. Built with Python and PySide6.

## Features

- **GUI Interface**: User-friendly desktop interface, no command line required.
- **Veo 3.1 Support**: Utilizes Google's latest video generation model.
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
- A Google Cloud API Key

## Installation

### Method 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. This project is configured to use Tsinghua University mirror for faster downloads in China.

1.  **Install uv** (if not already installed):
    ```bash
    # On Windows (PowerShell)
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # On macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the repository** (or download the source code):
    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

3.  **Create virtual environment and install dependencies**:
    ```bash
    # uv will automatically create a virtual environment and install dependencies
    uv sync
    ```

4.  **Activate the virtual environment**:
    ```bash
    # On Windows
    .venv\Scripts\activate
    
    # On macOS/Linux
    source .venv/bin/activate
    ```

### Method 2: Using pip (Traditional)

1.  **Clone the repository** (or download the source code):
    ```bash
    git clone https://github.com/sihuangtech/veo-studio.git
    cd veo-studio
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the example configuration file:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and replace `your_api_key_here` with your actual Google Cloud API Key.

    *Note: The application will verify this file and alert you if it's missing or configured with placeholders.*

3.  **Network Proxy Settings (Optional)**:
    If you are in a region where Google services are restricted (e.g., Chinese Mainland), you can configure a proxy by uncommenting and setting `HTTPS_PROXY` in your `.env` file:
    ```bash
    HTTPS_PROXY=http://127.0.0.1:7890
    ```

4.  **Custom API Endpoint (Optional)**:
    If you are using an API gateway / reverse proxy to access the Google GenAI API, you can override the SDK base URL in your `.env` file:
    ```bash
    GOOGLE_GENAI_BASE_URL=https://your-proxy.example.com
    ```

## Video Model Selection

Google provides multiple Veo video generation models. **You can now switch between them directly in the GUI.**

1.  Locate the **Model Selection** dropdown in the left panel.
2.  Select your desired model.
3.  The selection is automatically saved to `config.json`.

| Model Name | Version | Description |
| :--- | :--- | :--- |
| `veo-3.1-generate-preview` | Veo 3 | Released on Oct 15, 2025. Generates 720p or 1080p video at 24 or 30 fps. |
| `veo-3.1-fast-generate-preview` | Veo 3 | Released on Oct 15, 2025. Generates 720p or 1080p video at 24 or 30 fps. Optimized for speed and rapid iteration. |
| `veo-3.0-generate-001` | Veo 3 | Released in May 2025. Shut down in Nov 2025, replaced by Veo 3.1. |
| `veo-3.0-fast-generate-001` | Veo 3 | Released in May 2025. Shut down in Nov 2025, replaced by Veo 3.1. |
| `veo-2.0-generate-001` | Veo 2 | Released in Dec 2024. Generates 1080p video at 24 or 30 fps. |

*Notes:*
- *All models generate 8-second videos (API returns integer duration).*
- *Veo 3 series models support native audio generation and higher realism.*
- *Ensure your Google Cloud account is allowlisted for the corresponding preview models.*
- *For more official documentation and model details, please refer to: [Google Gemini API Video Docs](https://ai.google.dev/gemini-api/docs/video)*

## Usage

Run the graphical user interface:

```bash
python3 gui.py
```

### Standard Video Generation

1.  Select the desired model from the **Model Selection** dropdown.
2.  Enter your video description in the **Prompt** box.
3.  (Optional) Enter a **Negative Prompt** to specify what to avoid.
4.  Adjust **Aspect Ratio** and **Person Generation** settings as needed.
5.  (Optional) Check **Use Seed** and set a number for reproducible generation.
6.  Click **Generate Video**.
7.  Wait for the process to complete. The log panel on the right will show status updates.
8.  Once finished, the video location will be displayed, and a success message will appear.
9.  Generated videos are saved in the `output` directory within the project folder.

### Reference Video Analysis (Optional)

If you have an existing video and want to generate a similar video:

1.  Click **Browse** in the **Reference Video** section and select your video file (mp4/mov).
2.  (Optional) Enter a brief description in the **Prompt** box to guide the analysis.
3.  Click **Analyze Video** to analyze the reference video and generate an optimized prompt.
4.  The analysis result will be displayed in the log panel.
5.  Adjust other settings (aspect ratio, seed, etc.) as needed.
6.  Click **Generate Video** to create a video based on the reference.

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

- **API Key Errors**: Ensure your API key is valid and has access to the Veo model in Google Cloud Console.
- **Quota Limits**: Video generation models often have strict quota limits. Check your Google Cloud quota if generation fails repeatedly.
- **Logs**: Check the "Console Output" panel in the application for detailed error messages.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Maintained by **SK Studio**.

- **Website**: [www.skstudio.cn](https://www.skstudio.cn)
- **Email**: [contact@skstudio.cn](mailto:contact@skstudio.cn)
- **QQ Group**: [Join Chat](https://qm.qq.com/q/KUCcyyYtyi)
