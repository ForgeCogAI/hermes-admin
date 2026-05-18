import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AdminTemplate, User
from schemas import ConfigUpdate, UserCreate, UserResponse
from services import config_service, docker_service

router = APIRouter()


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).order_by(User.created_at).all()
    result = []
    for u in users:
        status = docker_service.get_container_status(u.data_dir, u.username)
        resp = UserResponse.model_validate(u)
        resp.container_status = status
        result.append(resp)
    return result


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    used_ports = [u.assigned_port for u in db.query(User).all()]
    port = config_service.get_next_port(used_ports)
    data_dir = config_service.ensure_user_dir(user_in.username)

    template = db.query(AdminTemplate).filter(AdminTemplate.id == 1).first()
    template_json = template.config_json if template else json.dumps(config_service.DEFAULT_CONFIG)

    user = User(
        username=user_in.username,
        display_name=user_in.display_name or user_in.username,
        email=user_in.email,
        assigned_port=port,
        data_dir=data_dir,
        config_json="{}",  # user starts with no overrides
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize files on disk
    docker_service.generate_compose_file(data_dir, port)
    merged = config_service.merge_config(template_json, "{}")
    config_service.write_hermes_config(data_dir, merged)

    resp = UserResponse.model_validate(user)
    resp.container_status = "stopped"
    return resp


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)
    docker_service.stop_container(user.data_dir, user.username)
    user.is_active = False
    db.commit()
    return {"message": "User deleted"}


@router.post("/{user_id}/start")
def start_container(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)

    # Re-generate compose in case config changed
    docker_service.generate_compose_file(user.data_dir, user.assigned_port)

    # Write merged config before starting
    template = db.query(AdminTemplate).filter(AdminTemplate.id == 1).first()
    template_json = template.config_json if template else json.dumps(config_service.DEFAULT_CONFIG)
    merged = config_service.merge_config(template_json, user.config_json)
    config_service.write_hermes_config(user.data_dir, merged)

    result = docker_service.start_container(user.data_dir, user.username)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"] or "Failed to start container")
    return {"status": "starting", "port": user.assigned_port}


@router.post("/{user_id}/stop")
def stop_container(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)
    docker_service.stop_container(user.data_dir, user.username)
    return {"status": "stopped"}


@router.post("/{user_id}/restart")
def restart_container(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)
    result = docker_service.restart_container(user.data_dir, user.username)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    return {"status": "restarting"}


@router.get("/{user_id}/status")
def get_status(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)
    status = docker_service.get_container_status(user.data_dir, user.username)
    return {"status": status, "port": user.assigned_port}


@router.get("/{user_id}/logs")
def get_logs(user_id: int, lines: int = 100, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)
    logs = docker_service.get_container_logs(user.data_dir, user.username, lines)
    return {"logs": logs}


@router.get("/{user_id}/config")
def get_config(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)
    return {"config_json": user.config_json}


@router.put("/{user_id}/config")
def update_config(user_id: int, body: ConfigUpdate, db: Session = Depends(get_db)):
    user = _get_user_or_404(user_id, db)

    # Validate JSON
    try:
        json.loads(body.config_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    user.config_json = body.config_json
    db.commit()

    # Re-write hermes config
    template = db.query(AdminTemplate).filter(AdminTemplate.id == 1).first()
    template_json = template.config_json if template else json.dumps(config_service.DEFAULT_CONFIG)
    merged = config_service.merge_config(template_json, user.config_json)
    config_service.write_hermes_config(user.data_dir, merged)

    return {"message": "Config updated"}
