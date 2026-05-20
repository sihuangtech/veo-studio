import app.config as config


def test_missing_config_uses_default_models(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "CONFIG_FILE", str(tmp_path / "missing-config.json"))
    monkeypatch.setattr(config.Config, "VEO_MODEL_NAME", None)

    config.Config.load_config()

    models = config.Config.get_models()
    assert models
    assert config.Config.get_current_model() == "veo-3.1-generate-preview"


def test_empty_models_are_replaced_with_defaults():
    merged = config.Config._merge_with_defaults(
        {
            "current_model": "custom-veo-model",
            "models": [],
            "text_models": [],
        }
    )

    assert merged["current_model"] == "custom-veo-model"
    assert merged["models"]
    assert merged["text_models"]


def test_veo_model_name_env_overrides_config(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "CONFIG_FILE", str(tmp_path / "missing-config.json"))
    monkeypatch.setattr(config.Config, "VEO_MODEL_NAME", "veo-custom-from-env")

    assert config.Config.get_current_model() == "veo-custom-from-env"


def test_auth_mode_aliases_are_normalized(monkeypatch):
    monkeypatch.setattr(config.Config, "GOOGLE_AUTH_MODE", "service-account")
    assert config.Config.get_auth_mode() == "enterprise"

    monkeypatch.setattr(config.Config, "GOOGLE_AUTH_MODE", "api_key")
    assert config.Config.get_auth_mode() == "ai_studio"


def test_config_model_lists_keep_custom_and_add_defaults():
    merged = config.Config._merge_with_defaults(
        {
            "models": [
                {
                    "id": "veo-custom",
                    "name": "Custom Veo",
                    "description": "Custom gateway model",
                }
            ],
            "text_models": [
                {
                    "id": "gemini-custom",
                    "name": "Custom Gemini",
                    "description": "Custom gateway model",
                }
            ],
        }
    )

    veo_ids = [model["id"] for model in merged["models"]]
    text_ids = [model["id"] for model in merged["text_models"]]

    assert "veo-custom" in veo_ids
    assert "veo-3.1-lite-generate-preview" in veo_ids
    assert "gemini-custom" in text_ids
    assert "gemini-3.5-flash" in text_ids
