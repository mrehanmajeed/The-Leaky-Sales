from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Lead

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    
    email_sent_count = 0
    follow_up_sent_count = 0
    replied_count = 0
    closed_count = 0
    failed_count = 0
    
    for lead in leads:
        if lead.status in ["email_sent", "follow_up_sent"]:
            email_sent_count += 1
        if lead.status == "follow_up_sent":
            follow_up_sent_count += 1
        if lead.status == "replied":
            replied_count += 1
        if lead.status == "closed":
            closed_count += 1
        if lead.status == "email_failed":
            failed_count += 1
            
    stats = {
        "total": len(leads),
        "email_sent": email_sent_count,
        "follow_up_sent": follow_up_sent_count,
        "replied": replied_count,
        "closed": closed_count,
        "failed": failed_count
    }
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "leads": leads, "stats": stats}
    )

@router.get("/lead/{lead_id}", response_class=HTMLResponse)
def get_lead_detail(request: Request, lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    return templates.TemplateResponse(
        "lead_detail.html",
        {"request": request, "lead": lead}
    )
