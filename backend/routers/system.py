from fastapi import APIRouter
from services.docker_service import HERMES_IMAGE, check_image_exists

router = APIRouter()


@router.get("/status")
def system_status():
    image_ok = check_image_exists()
    return {
        "image": HERMES_IMAGE,
        "image_ready": image_ok,
        "image_hint": (
            None if image_ok else
            f"镜像 `{HERMES_IMAGE}` 不存在，请先执行：\n"
            "git clone https://github.com/NousResearch/hermes-agent.git\n"
            "cd hermes-agent && docker build -t hermes-agent ."
        ),
    }
