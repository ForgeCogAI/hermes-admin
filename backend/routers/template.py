import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AdminTemplate
from schemas import ConfigUpdate, TemplateResponse
from services.config_service import DEFAULT_CONFIG

router = APIRouter()


def _get_or_create_template(db: Session) -> AdminTemplate:
    tmpl = db.query(AdminTemplate).filter(AdminTemplate.id == 1).first()
    if not tmpl:
        tmpl = AdminTemplate(id=1, config_json=json.dumps(DEFAULT_CONFIG))
        db.add(tmpl)
        db.commit()
        db.refresh(tmpl)
    return tmpl


@router.get("", response_model=TemplateResponse)
def get_template(db: Session = Depends(get_db)):
    return _get_or_create_template(db)


@router.put("")
def update_template(body: ConfigUpdate, db: Session = Depends(get_db)):
    try:
        json.loads(body.config_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    tmpl = _get_or_create_template(db)
    tmpl.config_json = body.config_json
    db.commit()
    return {"message": "Template updated"}
