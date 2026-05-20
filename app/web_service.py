import os

from .config import Config
from .veo_client import VeoClient


class WebGenerationService:
    """网页端业务服务：只负责参数校验和调用 VeoClient。"""

    @staticmethod
    def get_model_catalog():
        return {
            "veo_models": Config.get_models(),
            "text_models": Config.get_text_models(),
            "current_veo_model": Config.get_current_model(),
            "current_text_model": Config.get_current_text_model(),
        }

    @staticmethod
    def _clean_text(value):
        if not isinstance(value, str):
            return None
        value = value.strip()
        return value or None

    def generate(self, payload):
        auth_mode = self._clean_text(payload.get("auth_mode")) or Config.get_auth_mode()
        api_key = self._clean_text(payload.get("api_key")) or Config.GOOGLE_API_KEY
        service_account_file = self._clean_text(payload.get("service_account_file")) or Config.GOOGLE_SERVICE_ACCOUNT_FILE
        project = self._clean_text(payload.get("project")) or Config.GOOGLE_CLOUD_PROJECT
        location = self._clean_text(payload.get("location")) or Config.GOOGLE_CLOUD_LOCATION
        prompt = self._clean_text(payload.get("prompt"))
        veo_model = self._clean_text(payload.get("veo_model")) or Config.get_current_model()
        text_model = self._clean_text(payload.get("text_model")) or Config.get_current_text_model()
        reference_video_path = self._clean_text(payload.get("reference_video_path"))
        negative_prompt = self._clean_text(payload.get("negative_prompt"))
        base_url = self._clean_text(payload.get("base_url")) or Config.GOOGLE_GENAI_BASE_URL
        https_proxy = self._clean_text(payload.get("https_proxy")) or Config.HTTPS_PROXY

        auth_mode = VeoClient._normalize_auth_mode(auth_mode)
        if auth_mode == "ai_studio" and not api_key:
            raise ValueError("请填写 Google AI Studio API Key，或在 .env 中配置 GOOGLE_API_KEY。")
        if auth_mode == "enterprise":
            if not project:
                raise ValueError("Enterprise / Service Account 认证需要填写 Google Cloud Project ID。")
            if not location:
                raise ValueError("Enterprise / Service Account 认证需要填写 Google Cloud Location。")
            if service_account_file and not os.path.exists(service_account_file):
                raise FileNotFoundError(f"服务账号 JSON 不存在：{service_account_file}")
        if not prompt:
            raise ValueError("请填写视频提示词。")
        if reference_video_path and not os.path.exists(reference_video_path):
            raise FileNotFoundError(f"参考视频不存在：{reference_video_path}")

        seed = payload.get("seed")
        if seed in ("", None):
            seed = None
        else:
            seed = int(seed)

        # 中文注释：网页端传入的密钥只用于本次请求，不写入 .env 或 config.json。
        client = VeoClient(
            auth_mode=auth_mode,
            api_key=api_key,
            service_account_file=service_account_file,
            project=project,
            location=location,
            base_url=base_url,
            https_proxy=https_proxy,
            text_model=text_model,
        )

        common_options = {
            "aspect_ratio": payload.get("aspect_ratio") or "16:9",
            "person_generation": payload.get("person_generation") or "allow_adult",
            "negative_prompt": negative_prompt,
            "seed": seed,
            "model_name": veo_model,
        }

        if reference_video_path:
            return client.generate_video_from_reference(
                reference_video_path=reference_video_path,
                user_prompt=prompt,
                prompt_language=payload.get("prompt_language") or "zh",
                **common_options,
            )

        video_path = client.generate_video(prompt=prompt, **common_options)
        return {
            "video_path": video_path,
            "final_prompt": prompt,
        }
