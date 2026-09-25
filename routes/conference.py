import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.conference import Conference
from models.user import User
from typing import Optional

from pydantic import BaseModel, constr

router = APIRouter()

class GuidelinesRequest(BaseModel):
    user_id: int
    conference_id: str
    text: str


class ConferenceCreate(BaseModel):
    name: constr(min_length=2, max_length=200)
    guidelines: Optional[str] = None



@router.get("/get-list")
def get_conference_names(db: Session = Depends(get_db)):
    """Fetch all conference names and their IDs.

    Returns an empty list when there are none. An empty collection is not a
    404: 404 means the endpoint does not exist, and clients that treat any
    non-2xx as an error (axios does) end up in their error branch and render
    nothing instead of an empty state.
    """
    conferences = db.query(Conference.id, Conference.name).order_by(Conference.name).all()
    return [{"value": c.id, "label": c.name} for c in conferences]


def _require_admin(x_admin_token: Optional[str] = Header(default=None)):
    """Gate writes behind ADMIN_TOKEN when one is configured.

    Left open when the variable is unset so a fresh deployment can create its
    first conference. Set ADMIN_TOKEN in the environment to close it.
    """
    expected = os.getenv("ADMIN_TOKEN")
    if expected and x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Admin-Token")


@router.post("/create", status_code=201, dependencies=[Depends(_require_admin)])
def create_conference(payload: ConferenceCreate, db: Session = Depends(get_db)):
    """Create a conference.

    Without this the application cannot bootstrap: reviewer signup requires
    choosing a conference, so an empty table leaves no way in except raw SQL.
    """
    name = payload.name.strip()
    existing = db.query(Conference).filter(Conference.name == name).first()
    if existing:
        raise HTTPException(status_code=409, detail="A conference with that name already exists")

    conference = Conference(name=name, guidelines=payload.guidelines)
    db.add(conference)
    db.commit()
    db.refresh(conference)
    return {"value": conference.id, "label": conference.name}


@router.post("/upload_guidelines")
def upload_guidelines(payload: GuidelinesRequest, db: Session = Depends(get_db)):
    """Upload or update conference guidelines as text."""
    reviewer = db.query(User).filter(User.id == payload.user_id, User.role == "reviewer").first()
    if not reviewer:
        raise HTTPException(status_code=403, detail="User not authorized")
    
    conference = db.query(Conference).filter(Conference.id == payload.conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    conference.guidelines = payload.text  # Directly save input text
    db.commit()
    
    return {"message": "Guidelines uploaded successfully"}

# @router.get("/conference/{conference_id}")
# def get_conference_details(conference_id: int, db: Session = Depends(get_db)):
#     """Fetch a conference's details including its slug from the database."""
#     conference = db.query(Conference).filter(Conference.id == conference_id).first()
    
#     if not conference:
#         raise HTTPException(status_code=404, detail="Conference not found")
    
#     return {"id": conference.id, "name": conference.name, "guidelines": conference.guidelines}