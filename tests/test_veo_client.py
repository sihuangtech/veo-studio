import os

from app.config import Config
from app.veo_client import VeoClient


def test_extract_json_from_fenced_response():
    client = VeoClient.__new__(VeoClient)

    data = client._extract_json('Here is the result:\n```json\n{"veo_prompt": "hello"}\n```')

    assert data == {"veo_prompt": "hello"}


def test_output_filename_is_inside_project_output_dir(monkeypatch, tmp_path):
    client = VeoClient.__new__(VeoClient)
    monkeypatch.setattr(Config, "BASE_DIR", str(tmp_path))

    filename = client._build_output_filename()

    assert os.path.isabs(filename)
    assert os.path.dirname(filename) == str(tmp_path / "output")
    assert os.path.exists(tmp_path / "output")


def test_build_client_kwargs_for_ai_studio():
    client = VeoClient.__new__(VeoClient)

    kwargs = client._build_client_kwargs(auth_mode="ai_studio", api_key="test-key")

    assert kwargs == {"api_key": "test-key"}


def test_build_client_kwargs_for_enterprise_without_service_account_file():
    client = VeoClient.__new__(VeoClient)

    kwargs = client._build_client_kwargs(
        auth_mode="enterprise",
        project="demo-project",
        location="us-central1",
    )

    assert kwargs["enterprise"] is True
    assert kwargs["project"] == "demo-project"
    assert kwargs["location"] == "us-central1"
    assert "credentials" not in kwargs
