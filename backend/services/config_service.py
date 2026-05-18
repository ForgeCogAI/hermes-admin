import json
import os

import yaml

DATA_BASE_DIR = os.environ.get("ADMIN_DATA_DIR", os.path.expanduser("~/.hermes-admin"))
USERS_DIR = os.path.join(DATA_BASE_DIR, "users")

DEFAULT_CONFIG = {
    "model": "anthropic/claude-opus-4-5",
    "api_key": "",
    "base_url": "",
    "reasoning_effort": "high",
    "max_turns": 60,
    "language": "zh",  # UI 语言 (zh/en/ja/de/es/fr/tr/uk)
    "extra_yaml": "",
}

PORT_RANGE_START = 9200
PORT_RANGE_END = 9400


def get_user_data_dir(username: str) -> str:
    return os.path.join(USERS_DIR, username)


def ensure_user_dir(username: str) -> str:
    data_dir = get_user_data_dir(username)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_next_port(used_ports: list[int]) -> int:
    for port in range(PORT_RANGE_START, PORT_RANGE_END):
        if port not in used_ports:
            return port
    raise ValueError("No available ports in range")


def write_hermes_config(data_dir: str, config: dict) -> None:
    """Generate cli-config.yaml from our config dict."""
    hermes_cfg: dict = {}

    model = config.get("model", "").strip()
    api_key = config.get("api_key", "").strip()
    base_url = config.get("base_url", "").strip()
    reasoning_effort = config.get("reasoning_effort", "").strip()
    max_turns = config.get("max_turns")
    language = config.get("language", "").strip()

    if model:
        hermes_cfg.setdefault("llm", {})["model"] = model
    if api_key:
        hermes_cfg.setdefault("llm", {})["api_key"] = api_key
    if base_url:
        hermes_cfg.setdefault("llm", {})["base_url"] = base_url
    if reasoning_effort:
        hermes_cfg.setdefault("llm", {})["reasoning_effort"] = reasoning_effort
    if max_turns is not None:
        hermes_cfg.setdefault("agent", {})["max_turns"] = int(max_turns)
    if language:
        hermes_cfg.setdefault("display", {})["language"] = language

    yaml_content = yaml.dump(hermes_cfg, default_flow_style=False, allow_unicode=True)

    extra = config.get("extra_yaml", "").strip()
    if extra:
        yaml_content += "\n" + extra + "\n"

    config_path = os.path.join(data_dir, "cli-config.yaml")
    with open(config_path, "w") as f:
        f.write(yaml_content)


def merge_config(template_json: str, user_json: str) -> dict:
    """Merge template config with user overrides (user wins on non-empty values)."""
    base = json.loads(template_json) if template_json else {}
    overrides = json.loads(user_json) if user_json else {}
    merged = {**base}
    for k, v in overrides.items():
        if v not in (None, "", {}):
            merged[k] = v
    return merged
