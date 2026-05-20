from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from repositories.aspect_repository import (
    create_first_aspects,
    create_aspect,
    get_all_aspects,
    get_all_active_aspects,
    delete_aspect,
    modify_aspect_status,
)
import db.seed as seed
from core.constants import DEFAULT_ASPECTS


def seed_default_aspects(db: Session, user_id: int):
    existing = get_all_aspects(db, user_id)
    if not existing:
        create_first_aspects(db, user_id, DEFAULT_ASPECTS)


def get_user_aspects(db: Session) -> list[str]:
    aspects = get_all_active_aspects(db, seed.temp_user_id)
    if not aspects:
        seed_default_aspects(db, seed.temp_user_id)
        aspects = get_all_active_aspects(db, seed.temp_user_id)
    return [a.name for a in aspects]


def list_aspects(db: Session):
    return get_all_aspects(db, seed.temp_user_id)


def list_active_aspects(db: Session):
    return get_all_active_aspects(db, seed.temp_user_id)


def create_single_aspect(db: Session, name: str):
    try:
        return create_aspect(db, name.strip().lower(), seed.temp_user_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Aspect '{name}' already exists")


def delete_single_aspect(db: Session, aspect_id: int):
    deleted = delete_aspect(db, aspect_id, seed.temp_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Aspect not found")
    return {"message": "Aspect deleted successfully"}


def modify_single_aspect(db: Session, aspect_id: int, is_active: bool):
    modified = modify_aspect_status(db, aspect_id, seed.temp_user_id, is_active)
    if not modified:
        raise HTTPException(status_code=404, detail="Aspect not found")
    return {"message": "Aspect modified successfully"}