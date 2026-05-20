from sqlalchemy.orm import Session
from typing import List

from models.aspect import AspectDB


def create_first_aspects(db: Session, user_id: int, aspects: List[str]):
    for aspect in aspects:
        new_aspect = AspectDB(
            user_id=user_id,
            name=aspect,
            is_active=True,
        )
        db.add(new_aspect)
    db.commit()


def get_all_aspects(db: Session, user_id: int):
    return db.query(AspectDB).filter(
        AspectDB.user_id == user_id
    ).order_by(AspectDB.created_at.desc()).all()


def get_all_active_aspects(db: Session, user_id: int):
    return db.query(AspectDB).filter(
        AspectDB.user_id == user_id,
        AspectDB.is_active == True
    ).order_by(AspectDB.created_at.desc()).all()


def create_aspect(db: Session, aspect: str, user_id: int) -> AspectDB:
    new_aspect = AspectDB(
        user_id=user_id,
        name=aspect,
        is_active=True,
    )
    db.add(new_aspect)
    db.commit()
    db.refresh(new_aspect)
    return new_aspect


def get_aspect(db: Session, aspect_id: int, user_id: int) -> AspectDB | None:
    return db.query(AspectDB).filter(
        AspectDB.aspect_id == aspect_id,
        AspectDB.user_id == user_id,
    ).first()


def delete_aspect(db: Session, aspect_id: int, user_id: int) -> bool:
    aspect = get_aspect(db, aspect_id, user_id)
    if not aspect:
        return False
    db.delete(aspect)
    db.commit()
    return True


def modify_aspect_status(db: Session, aspect_id: int, user_id: int, is_active: bool) -> bool:
    aspect = get_aspect(db, aspect_id, user_id)
    if not aspect:
        return False
    aspect.is_active = is_active
    db.commit()
    return True
