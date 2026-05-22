import json
import os

import gradio as gr

from .config import Config
from .web_service import WebGenerationService

SERVICE = WebGenerationService()
APP_CSS = """
.gradio-container,
.gradio-container .contain,
.gradio-container main {
    width: 96vw !important;
    max-width: 1680px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
textarea, input, select { border-radius: 7px !important; }
"""


def _choice_labels(models):
    """中文注释：下拉框显示友好名称，提交时再映射回真实模型 ID。"""
    return [f"{model['name']} ({model['id']})" for model in models]


def _choices_with_current(models, current_model):
    labels = _choice_labels(models)
    if current_model and all(f"({current_model})" not in label for label in labels):
        labels.insert(0, f"Configured Model ({current_model})")
    return labels


def _model_id_from_label(label, models):
    for model in models:
        expected = f"{model['name']} ({model['id']})"
        if label == expected:
            return model["id"]
    return label


def _format_result(result):
    return json.dumps(result, ensure_ascii=False, indent=2)


def _get_uploaded_path(reference_video):
    if reference_video is None:
        return None
    if isinstance(reference_video, str):
        return reference_video
    return getattr(reference_video, "name", None)


def _auth_mode_value(label):
    if label.startswith("Gemini Enterprise"):
        return "enterprise"
    return "ai_studio"


def generate_video(
    auth_mode_label,
    api_key,
    service_account_file,
    project,
    location,
    veo_model_label,
    text_model_label,
    prompt,
    negative_prompt,
    aspect_ratio,
    seed,
    reference_video,
    prompt_language,
    base_url,
    https_proxy,
):
    catalog = SERVICE.get_model_catalog()
    veo_model = _model_id_from_label(veo_model_label, catalog["veo_models"])
    text_model = _model_id_from_label(text_model_label, catalog["text_models"])

    payload = {
        "auth_mode": _auth_mode_value(auth_mode_label),
        "api_key": api_key,
        "service_account_file": _get_uploaded_path(service_account_file),
        "project": project,
        "location": location,
        "veo_model": veo_model,
        "text_model": text_model,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "aspect_ratio": aspect_ratio,
        "seed": seed,
        "reference_video_path": _get_uploaded_path(reference_video),
        "prompt_language": prompt_language,
        "base_url": base_url,
        "https_proxy": https_proxy,
        "person_generation": "allow_adult",
    }

    result = SERVICE.generate(payload)
    video_path = result.get("video_path")
    if video_path and not os.path.exists(video_path):
        video_path = None
    return video_path, _format_result(result)


def build_app():
    catalog = SERVICE.get_model_catalog()
    veo_models = catalog["veo_models"]
    text_models = catalog["text_models"]
    veo_choices = _choices_with_current(veo_models, catalog["current_veo_model"])
    text_choices = _choices_with_current(text_models, catalog["current_text_model"])
    current_veo = _choice_labels([m for m in veo_models if m["id"] == catalog["current_veo_model"]])
    current_text = _choice_labels([m for m in text_models if m["id"] == catalog["current_text_model"]])
    auth_default = (
        "Gemini Enterprise / Service Account"
        if Config.get_auth_mode() == "enterprise"
        else "Google AI Studio / API Key"
    )

    with gr.Blocks(title="Veo Studio Web", fill_width=True) as demo:
        gr.Markdown("# Veo Studio Web\n本地网页版本，认证信息只用于本次生成，不会写入 `.env`；留空则使用 `.env` 中的对应配置。")

        with gr.Row(equal_height=True):
            with gr.Column(scale=3):
                auth_mode = gr.Radio(
                    label="认证方式",
                    choices=["Google AI Studio / API Key", "Gemini Enterprise / Service Account"],
                    value=auth_default,
                )
                api_key = gr.Textbox(label="Google AI Studio API Key", type="password")
                service_account_file = gr.File(
                    label="Service Account JSON（Enterprise 可选）",
                    file_types=[".json"],
                )
                with gr.Row():
                    project = gr.Textbox(label="Google Cloud Project ID")
                    location = gr.Textbox(label="Google Cloud Location")
                prompt = gr.Textbox(label="Prompt", lines=9)
                negative_prompt = gr.Textbox(label="Negative Prompt")
                generate_btn = gr.Button("生成视频", variant="primary")

            with gr.Column(scale=2):
                veo_model = gr.Dropdown(
                    label="Veo 视频模型",
                    choices=veo_choices,
                    value=(current_veo[0] if current_veo else veo_choices[0]),
                )
                text_model = gr.Dropdown(
                    label="Gemini 分析模型",
                    choices=text_choices,
                    value=(current_text[0] if current_text else text_choices[0]),
                )
                aspect_ratio = gr.Radio(label="画幅", choices=["16:9", "9:16"], value="16:9")
                seed = gr.Number(label="Seed（可选）", precision=0)
                reference_video = gr.File(
                    label="参考视频（可选）",
                    file_types=[".mp4", ".mov", ".m4v", ".avi", ".mkv"],
                )
                prompt_language = gr.Radio(label="参考视频分析语言", choices=["zh", "en"], value="zh")
                base_url = gr.Textbox(label="自定义 API Base URL（可选）")
                https_proxy = gr.Textbox(label="HTTPS Proxy（可选）")

        with gr.Row():
            output_video = gr.Video(label="生成视频")
            output_json = gr.Code(label="任务结果", language="json")

        generate_btn.click(
            fn=generate_video,
            inputs=[
                auth_mode,
                api_key,
                service_account_file,
                project,
                location,
                veo_model,
                text_model,
                prompt,
                negative_prompt,
                aspect_ratio,
                seed,
                reference_video,
                prompt_language,
                base_url,
                https_proxy,
            ],
            outputs=[output_video, output_json],
        )

    return demo


def main():
    demo = build_app()
    demo.launch(server_name="127.0.0.1", server_port=7860, css=APP_CSS)


if __name__ == "__main__":
    main()
