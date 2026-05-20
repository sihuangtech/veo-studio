import json
import os
from copy import deepcopy
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DEFAULT_GEMINI_TEXT_MODEL = "gemini-3-flash-preview"

DEFAULT_VEO_MODELS = [
    {
        "id": "veo-3.1-generate-preview",
        "name": "Veo 3.1 (Preview)",
        "description": "High-fidelity video generation with native audio and advanced controls.",
    },
    {
        "id": "veo-3.1-fast-generate-preview",
        "name": "Veo 3.1 Fast (Preview)",
        "description": "Veo 3.1 variant optimized for faster iteration.",
    },
    {
        "id": "veo-3.1-lite-generate-preview",
        "name": "Veo 3.1 Lite (Preview)",
        "description": "Lower-cost Veo 3.1 variant for high-volume video workflows.",
    },
    {
        "id": "veo-3.0-generate-001",
        "name": "Veo 3.0",
        "description": "General Veo 3 model for text/image to video generation with audio.",
    },
    {
        "id": "veo-3.0-fast-generate-001",
        "name": "Veo 3.0 Fast",
        "description": "Faster Veo 3 variant for lower-latency video generation with audio.",
    },
    {
        "id": "veo-2.0-generate-001",
        "name": "Veo 2.0",
        "description": "Earlier Veo model for video generation without native audio.",
    },
]

DEFAULT_GEMINI_TEXT_MODELS = [
    {
        "id": "gemini-3.5-flash",
        "name": "Gemini 3.5 Flash",
        "description": "Stable text model for fast, high-quality analysis and prompt rewriting.",
    },
    {
        "id": "gemini-3.1-pro-preview",
        "name": "Gemini 3.1 Pro Preview",
        "description": "Preview model for advanced reasoning and complex multimodal analysis.",
    },
    {
        "id": "gemini-3-flash-preview",
        "name": "Gemini 3 Flash Preview",
        "description": "Preview multimodal text model; default for reference video analysis.",
    },
    {
        "id": "gemini-3.1-flash-lite",
        "name": "Gemini 3.1 Flash-Lite",
        "description": "Stable low-latency, lower-cost model for simple analysis tasks.",
    },
    {
        "id": "gemini-3.1-flash-lite-preview",
        "name": "Gemini 3.1 Flash-Lite Preview",
        "description": "Preview low-cost model for lightweight, high-frequency tasks.",
    },
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "Stable 2.5 Pro model for complex analysis and reasoning.",
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "description": "Stable 2.5 Flash model for low-latency multimodal analysis.",
    },
    {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash-Lite",
        "description": "Stable cost-efficient 2.5 model for lightweight tasks.",
    },
]

DEFAULT_CONFIG = {
    "current_model": "veo-3.1-generate-preview",
    "models": DEFAULT_VEO_MODELS,
    "current_text_model": DEFAULT_GEMINI_TEXT_MODEL,
    "text_models": DEFAULT_GEMINI_TEXT_MODELS,
}


def _merge_model_lists(config_models, default_models):
    """保留用户自定义模型，同时补齐官方默认模型。"""
    if not isinstance(config_models, list):
        config_models = []

    merged = []
    seen = set()
    for model in config_models + default_models:
        if not isinstance(model, dict):
            continue
        model_id = model.get("id")
        if not isinstance(model_id, str) or not model_id.strip() or model_id in seen:
            continue
        merged.append(model)
        seen.add(model_id)
    return merged


class Config:
    BASE_DIR = BASE_DIR
    CONFIG_FILE = CONFIG_FILE
    GOOGLE_AUTH_MODE = os.getenv("GOOGLE_AUTH_MODE", "ai_studio")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    VEO_MODEL_NAME = os.getenv("VEO_MODEL_NAME")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY")
    GOOGLE_GENAI_BASE_URL = os.getenv("GOOGLE_GENAI_BASE_URL")
    GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL")
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    _config_data = deepcopy(DEFAULT_CONFIG)

    @classmethod
    def _merge_with_defaults(cls, config_data):
        data = deepcopy(DEFAULT_CONFIG)
        if not isinstance(config_data, dict):
            return data

        current_model = config_data.get("current_model")
        if isinstance(current_model, str) and current_model.strip():
            data["current_model"] = current_model.strip()

        data["models"] = _merge_model_lists(config_data.get("models"), DEFAULT_VEO_MODELS)

        current_text_model = config_data.get("current_text_model")
        if isinstance(current_text_model, str) and current_text_model.strip():
            data["current_text_model"] = current_text_model.strip()

        data["text_models"] = _merge_model_lists(
            config_data.get("text_models"),
            DEFAULT_GEMINI_TEXT_MODELS,
        )

        return data

    @classmethod
    def load_config(cls):
        """Load configuration from JSON file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cls._config_data = cls._merge_with_defaults(json.load(f))
            except Exception as e:
                print(f"Error loading config.json: {e}")
                cls._config_data = deepcopy(DEFAULT_CONFIG)
        else:
            cls._config_data = deepcopy(DEFAULT_CONFIG)

    @classmethod
    def save_config(cls):
        """Save current configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cls._config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    @classmethod
    def get_models(cls):
        """Return list of available Veo video models."""
        cls.load_config()
        return cls._config_data.get("models", [])

    @classmethod
    def get_text_models(cls):
        """Return list of available Gemini text models."""
        cls.load_config()
        return cls._config_data.get("text_models", [])

    @classmethod
    def get_current_model(cls):
        """Return the ID of the currently selected model."""
        cls.load_config()
        if cls.VEO_MODEL_NAME:
            return cls.VEO_MODEL_NAME.strip()
        return cls._config_data.get("current_model", "veo-3.1-generate-preview")

    @classmethod
    def get_current_text_model(cls):
        """Return the model used for reference video analysis."""
        cls.load_config()
        if cls.GEMINI_TEXT_MODEL:
            return cls.GEMINI_TEXT_MODEL.strip()
        return cls._config_data.get("current_text_model", DEFAULT_GEMINI_TEXT_MODEL)

    @classmethod
    def set_current_model(cls, model_id):
        """Set the current model and save to file."""
        cls.load_config()
        cls._config_data["current_model"] = model_id
        cls.save_config()

    @classmethod
    def get_auth_mode(cls):
        auth_mode = (cls.GOOGLE_AUTH_MODE or "ai_studio").strip().lower().replace("-", "_")
        if auth_mode in ("google_ai_studio", "aistudio", "api_key"):
            return "ai_studio"
        if auth_mode in ("enterprise", "vertex", "vertexai", "service_account"):
            return "enterprise"
        return auth_mode

    @classmethod
    def validate(cls):
        auth_mode = cls.get_auth_mode()
        if auth_mode not in ("ai_studio", "enterprise"):
            raise ValueError("GOOGLE_AUTH_MODE must be ai_studio or enterprise")
        if auth_mode == "ai_studio":
            if not cls.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found in .env file")
            if cls.GOOGLE_API_KEY == "your_api_key_here":
                raise ValueError("Please replace placeholder API key in .env with your actual key")
        if auth_mode == "enterprise":
            if not cls.GOOGLE_CLOUD_PROJECT:
                raise ValueError("GOOGLE_CLOUD_PROJECT is required for enterprise authentication")
            if not cls.GOOGLE_CLOUD_LOCATION:
                raise ValueError("GOOGLE_CLOUD_LOCATION is required for enterprise authentication")
            if cls.GOOGLE_SERVICE_ACCOUNT_FILE and not os.path.exists(cls.GOOGLE_SERVICE_ACCOUNT_FILE):
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE does not exist")
        if cls.VEO_MODEL_NAME and not cls.VEO_MODEL_NAME.strip():
            raise ValueError("VEO_MODEL_NAME cannot be empty")
        if cls.GEMINI_TEXT_MODEL is not None and not cls.GEMINI_TEXT_MODEL.strip():
            raise ValueError("GEMINI_TEXT_MODEL cannot be empty")
        if cls.GOOGLE_GENAI_BASE_URL:
            base_url = cls.GOOGLE_GENAI_BASE_URL.strip()
            if not (base_url.startswith("http://") or base_url.startswith("https://")):
                raise ValueError("GOOGLE_GENAI_BASE_URL must start with http:// or https://")
