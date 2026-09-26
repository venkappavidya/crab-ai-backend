from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database.db import get_db
from models.conference import Conference 
from models.conference_paper import ConferencePaper
from models.user import User
from datetime import datetime
import shutil
import os
import json
from pydantic import BaseModel

class ReviewRequest(BaseModel):
    paper_id: int
    review_text: str
    status: str


router = APIRouter()


def _available_reviews(paper):
    """Return only the models that actually produced a review.

    The client reads review['reviews'][0]['numerical_ratings'] for every entry
    in this list. Sending a model with review=None makes that dereference a
    null and the dashboard renders a blank page. Only Gemini is wired up, so
    the other slots are empty until a model is connected.
    """
    candidates = [
        ("Gemini", paper.review_gemini),
        ("Claude", paper.review_claude),
        ("OpenAI", paper.review_openai),
        ("Perplexity", paper.review_perplexity),
        ("Deepseek", paper.review_deepseek),
    ]
    return [{"model": name, "review": review} for name, review in candidates if review]


UPLOAD_FOLDER = "uploads/guidelines"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@router.get("/paper/conference/{conference_id}/user/{user_id}")
def get_conference_papers(user_id: int, conference_id: int, db: Session = Depends(get_db)):
    """Fetch all papers for the specified conference and year where the reviewer is assigned."""
    print("Inside this:")
    reviewer = db.query(User).filter(User.id == user_id, User.role == "reviewer").first()
   
    if not reviewer:
        raise HTTPException(status_code=403, detail="User not authorized")
    
    current_year = datetime.utcnow().year

    conference = db.query(Conference).filter(Conference.id == conference_id).first()
 
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    papers = db.query(ConferencePaper).filter(ConferencePaper.conference_id == conference.id, ConferencePaper.year == current_year).all()
    if not papers:
        # No submissions yet is an empty queue, not a missing resource.
        return []
   
    response = []
    
    for paper in papers:
        print(paper.status)
        if paper.status =="Accepted" or paper.status =="Rejected":

            response.append({
                'id':paper.id,
                'title':paper.title,
                'conference': conference.name,
                'uploadDate':  datetime.utcnow(),
                'status':paper.status,
                'score':'',
                'pdfUrl': paper.path,
                'reviews': _available_reviews(paper),
                'summary':paper.summary,
                'finalDecision':{
                    'reviewer':paper.reviewer_name,
                    'comments': paper.human_review,
                    'decision':paper.status,
                    'date': paper.date_of_review
                }
                
            })
        else:
            response.append({
                'id':paper.id,
                'title':paper.title,
                'conference': conference.name,
                'uploadDate':  datetime.utcnow(),
                'status':paper.status,
                'score':'',
                'pdfUrl': paper.path,
                'reviews': _available_reviews(paper),
                'summary':paper.summary
                
            })

    
    return response

@router.post("/paper/conference/{conference_id}/user/{user_id}")
def submit_review(conference_id:int, user_id:int,request: ReviewRequest, db: Session = Depends(get_db)):
    """Submit a human review and update the paper status for a specific conference and year."""
    print("inside")
    paper_id = request.paper_id
    review_text = request.review_text
    status = request.status



    reviewer = db.query(User).filter(User.id == user_id, User.role == "reviewer").first()
    if not reviewer:
        raise HTTPException(status_code=403, detail="User not authorized")
    print("about to get reviewer info")
    current_year = datetime.utcnow().year
    conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found for the current year")
    print("about to get conferences")
    paper = db.query(ConferencePaper).filter(ConferencePaper.id == paper_id, ConferencePaper.conference_id == conference.id, ConferencePaper.year == current_year).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    print("about to get paper")

    paper.human_review = review_text
    paper.status = status
    paper.reviewer_id = reviewer.id
    paper.reviewer_name = reviewer.name
    paper.date_of_review = datetime.utcnow()
    db.commit()

    print("committed to the db successfully")


    papers = db.query(ConferencePaper).filter(ConferencePaper.conference_id == conference.id, ConferencePaper.year == current_year).all()
    
    print("not error so far")
    response = []
    for paper in papers:
        if paper.status != "Reviewed":

            response.append({
                'id':paper.id,
                'title':paper.title,
                'conference': conference.name,
                'uploadDate':  datetime.utcnow(),
                'status':paper.status,
                'score':'',
                'pdfUrl': paper.path,
                'reviews': _available_reviews(paper),
                'summary':paper.summary,
                'finalDecision':{
                    'reviewer':paper.reviewer_name,
                    'comments': paper.human_review,
                    'decision':paper.status,
                    'date': paper.date_of_review
                }
                
            })
        else:
            response.append({
                'id':paper.id,
                'title':paper.title,
                'conference': conference.name,
                'uploadDate':  datetime.utcnow(),
                'status':paper.status,
                'score':'',
                'pdfUrl': paper.path,
                'reviews': _available_reviews(paper),
                'summary':paper.summary
                
            })

       
    

    # print(response)
    
    return response
    # return {"message": "Review submitted successfully", "paper_id": paper.id}
