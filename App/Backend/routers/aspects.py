from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from schemas.aspect import AspectCreate, AspectUpdate, AspectResponse
from services.aspect_service import (
    list_aspects,
    list_active_aspects,
    create_single_aspect,
    delete_single_aspect,
    modify_single_aspect,
)

AspectRouter = APIRouter(
    prefix="/aspects",
    tags=["Aspects"],
)


@AspectRouter.get("/", response_model=List[AspectResponse])
def get_aspects(db: Session = Depends(get_db)):
    return list_aspects(db)


@AspectRouter.get("/active", response_model=List[AspectResponse])
def get_active_aspects(db: Session = Depends(get_db)):
    return list_active_aspects(db)


@AspectRouter.post("/", response_model=AspectResponse)
def add_aspect(body: AspectCreate, db: Session = Depends(get_db)):
    return create_single_aspect(db, body.name)


@AspectRouter.patch("/{aspect_id}")
def toggle_aspect(
    body: AspectUpdate,
    aspect_id: int = Path(gt=0, description="ID of the aspect to update"),
    db: Session = Depends(get_db),
):
    return modify_single_aspect(db, aspect_id, body.is_active)


@AspectRouter.delete("/{aspect_id}")
def remove_aspect(
    aspect_id: int = Path(gt=0, description="ID of the aspect to delete"),
    db: Session = Depends(get_db),
):
    return delete_single_aspect(db, aspect_id)
