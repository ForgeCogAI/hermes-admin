import json
import os
import subprocess

HERMES_IMAGE = os.environ.get("HERMES_IMAGE", "hermes-agent")

COMPOSE_TEMPLATE = """\
services:
  gateway:
    image: {image}
    restart: unless-stopped
    volumes:
      - {data_dir}:/opt/data
    networks:
      - hermes-net
    command: ["gateway", "run"]

  dashboard:
    image: {image}
    restart: unless-stopped
    depends_on:
      - gateway
    volumes:
      - {data_dir}:/opt/data
    ports:
      - "{port}:9119"
    networks:
      - hermes-net
    command: ["dashboard", "--host", "0.0.0.0", "--no-open", "--insecure", "--tui"]

networks:
  hermes-net:
    driver: bridge
"""


def _compose_path(data_dir: str) -> str:
    return os.path.join(data_dir, "docker-compose.yml")


def _project_name(username: str) -> str:
    return f"hermes-{username}"


def generate_compose_file(data_dir: str, port: int) -> None:
    content = COMPOSE_TEMPLATE.format(
        image=HERMES_IMAGE,
        data_dir=data_dir,
        port=port,
    )
    with open(_compose_path(data_dir), "w") as f:
        f.write(content)


class DockerNotInstalledError(RuntimeError):
    """Raised when the `docker` CLI is not available on PATH."""


def check_image_exists(image: str = HERMES_IMAGE) -> bool:
    """Return True if the image exists locally."""
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _run_compose(data_dir: str, username: str, *args, timeout: int = 60) -> tuple[int, str, str]:
    cmd = [
        "docker", "compose",
        "-f", _compose_path(data_dir),
        "-p", _project_name(username),
    ] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as e:
        raise DockerNotInstalledError(
            "docker 命令未找到，请先安装 Docker 并确保 docker 在 PATH 中"
        ) from e
    except subprocess.TimeoutExpired as e:
        return 1, "", f"命令超时: {e}"
    return result.returncode, result.stdout, result.stderr


def start_container(data_dir: str, username: str) -> dict:
    if not check_image_exists():
        return {
            "success": False,
            "stdout": "",
            "stderr": (
                f"本地不存在镜像 `{HERMES_IMAGE}`。\n"
                "请先克隆并构建 hermes-agent：\n"
                "  git clone https://github.com/NousResearch/hermes-agent.git\n"
                "  cd hermes-agent && docker build -t hermes-agent ."
            ),
        }
    try:
        code, stdout, stderr = _run_compose(data_dir, username, "up", "-d", timeout=120)
    except DockerNotInstalledError as e:
        return {"success": False, "stdout": "", "stderr": str(e)}
    return {"success": code == 0, "stdout": stdout, "stderr": stderr}


def stop_container(data_dir: str, username: str) -> dict:
    try:
        code, stdout, stderr = _run_compose(data_dir, username, "down", timeout=60)
    except DockerNotInstalledError as e:
        return {"success": False, "stdout": "", "stderr": str(e)}
    return {"success": code == 0, "stdout": stdout, "stderr": stderr}


def restart_container(data_dir: str, username: str) -> dict:
    try:
        code, stdout, stderr = _run_compose(data_dir, username, "restart", timeout=60)
    except DockerNotInstalledError as e:
        return {"success": False, "stdout": "", "stderr": str(e)}
    return {"success": code == 0, "stdout": stdout, "stderr": stderr}


def get_container_status(data_dir: str, username: str) -> str:
    """Returns: running | partial | stopped | not_found | docker_unavailable"""
    compose_file = _compose_path(data_dir)
    if not os.path.exists(compose_file):
        return "not_found"

    try:
        code, stdout, _ = _run_compose(data_dir, username, "ps", "--format", "json")
    except DockerNotInstalledError:
        return "docker_unavailable"

    if code != 0 or not stdout.strip():
        return "stopped"

    try:
        lines = [line for line in stdout.strip().splitlines() if line.strip()]
        services = [json.loads(line) for line in lines]
        running = sum(1 for s in services if s.get("State") == "running")
        if running == len(services) and running > 0:
            return "running"
        if running > 0:
            return "partial"
        return "stopped"
    except Exception:
        return "stopped"


def get_container_logs(data_dir: str, username: str, lines: int = 100) -> str:
    try:
        _, stdout, stderr = _run_compose(
            data_dir, username, "logs", "--tail", str(lines)
        )
    except DockerNotInstalledError as e:
        return str(e)
    return stdout or stderr
