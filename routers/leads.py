from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import logging

from database.connection import get_db
from database.models import Lead
from services.hubspot import create_contact, create_deal
from services.ai import generate_first_email
from services.mailer import send_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leads", tags=["Leads"])

class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    product: str = ""
    budget: str = ""
    message: str = ""

@router.post("/", status_code=201)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    existing_lead = db.query(Lead).filter(Lead.email == data.email).first()
    if existing_lead:
        raise HTTPException(status_code=409, detail="Lead with this email already exists")

    lead = Lead(
        name=data.name.strip(),
        email=data.email.strip(),
        phone=data.phone.strip(),
        product=data.product.strip(),
        budget=data.budget.strip(),
        message=data.message.strip()
    )
    db.add(lead)
    db.flush()

    contact_id = create_contact(lead)
    if contact_id:
        lead.hubspot_contact_id = contact_id
        deal_id = create_deal(lead, contact_id)
        if deal_id:
            lead.hubspot_deal_id = deal_id

    email_body = generate_first_email(lead.name, lead.product, lead.budget, lead.message)
    lead.first_email_body = email_body

    subject = f"Your ShopRocket Quote for {lead.product} — Let's Talk"
    success = send_email(to_email=lead.email, subject=subject, plain_body=email_body)

    if success:
        lead.first_email_sent_at = datetime.now(timezone.utc)
        lead.status = "email_sent"
    else:
        lead.status = "email_failed"
        lead.error_log = "SMTP failure on first email"

    db.commit()
    db.refresh(lead)

    return {"id": lead.id, "status": lead.status, "message": "Lead processed"}

@router.patch("/{lead_id}/replied")
def mark_replied(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.status = "replied"
    lead.replied_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Marked as replied"}

@router.patch("/{lead_id}/close")
def close_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.status = "closed"
    db.commit()
    return {"message": "Lead closed"}

@router.get("/")
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return leads
