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


def _deep_merge(base: dict, override: dict) -> dict:
    """递归合并 override 到 base。override 中的 dict 与 base 同 key 时继续递归；
    其他值（含 list/str/None）直接覆盖。base 会被原地修改并返回。"""
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def write_hermes_config(data_dir: str, config: dict) -> None:
    """将 admin 模板/用户覆盖配置写入 hermes 容器内 ~/.hermes/config.yaml
    对应宿主路径 = data_dir/config.yaml（容器内 HERMES_HOME=/opt/data）。

    Hermes 的 schema 关键字段：
      model.default / model.provider / model.base_url / model.api_key
      agent.max_turns / agent.reasoning_effort
      display.language

    为避免覆盖 hermes 启动时自动生成的注释与默认值，采用 deep-merge 策略：
    读取现有 config.yaml → 合并我们管理的字段 → 写回。
    """
    model = (config.get("model") or "").strip()
    api_key = (config.get("api_key") or "").strip()
    base_url = (config.get("base_url") or "").strip()
    reasoning_effort = (config.get("reasoning_effort") or "").strip()
    max_turns = config.get("max_turns")
    language = (config.get("language") or "").strip()

    overrides: dict = {}

    model_section: dict = {}
    if model:
        model_section["default"] = model
    if base_url:
        # 走自定义 OpenAI 兼容端点（OpenRouter、DashScope、Ollama 等）
        model_section["provider"] = "custom"
        model_section["base_url"] = base_url
    if api_key:
        model_section["api_key"] = api_key
    if model_section:
        overrides["model"] = model_section

    agent_section: dict = {}
    if max_turns is not None:
        agent_section["max_turns"] = int(max_turns)
    if reasoning_effort:
        agent_section["reasoning_effort"] = reasoning_effort
    if agent_section:
        overrides["agent"] = agent_section

    if language:
        overrides["display"] = {"language": language}

    config_path = os.path.join(data_dir, "config.yaml")
    existing: dict = {}
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    existing = loaded
        except yaml.YAMLError:
            existing = {}

    merged = _deep_merge(existing, overrides)

    yaml_content = yaml.dump(merged, default_flow_style=False, allow_unicode=True, sort_keys=False)

    extra = (config.get("extra_yaml") or "").strip()
    if extra:
        yaml_content += "\n" + extra + "\n"

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
