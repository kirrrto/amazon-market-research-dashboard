from pathlib import Path
import tomllib


def test_streamlit_upload_limit_matches_project_limit():
    config_path = Path(".streamlit/config.toml")
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    assert config["server"]["maxUploadSize"] == 20
