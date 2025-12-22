import os
import json
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = "config.json"

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY")
    GOOGLE_GENAI_BASE_URL = os.getenv("GOOGLE_GENAI_BASE_URL")
    
    # Defaults
    _config_data = {
        "current_model": "veo-3.1-generate-preview",
        "models": []
    }

    @classmethod
    def load_config(cls):
        """Load configuration from JSON file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cls._config_data = json.load(f)
            except Exception as e:
                print(f"Error loading config.json: {e}")

    @classmethod
    def save_config(cls):
        """Save current configuration to JSON file."""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cls._config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    @classmethod
    def get_models(cls):
        """Return list of available models."""
        cls.load_config()
        return cls._config_data.get("models", [])

    @classmethod
    def get_current_model(cls):
        """Return the ID of the currently selected model."""
        cls.load_config()
        return cls._config_data.get("current_model", "veo-3.1-generate-preview")

    @classmethod
    def set_current_model(cls, model_id):
        """Set the current model and save to file."""
        cls._config_data["current_model"] = model_id
        cls.save_config()

    @classmethod
    def validate(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        if cls.GOOGLE_API_KEY == "your_api_key_here":
            raise ValueError("Please replace placeholder API key in .env with your actual key")
        if cls.GOOGLE_GENAI_BASE_URL:
            base_url = cls.GOOGLE_GENAI_BASE_URL.strip()
            if not (base_url.startswith("http://") or base_url.startswith("https://")):
                raise ValueError("GOOGLE_GENAI_BASE_URL must start with http:// or https://")
