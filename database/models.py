from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database.connection import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    product = Column(String(255), nullable=True)
    budget = Column(String(100), nullable=True)
    message = Column(Text, nullable=True)
    hubspot_contact_id = Column(String(100), nullable=True)
    hubspot_deal_id = Column(String(100), nullable=True)
    first_email_body = Column(Text, nullable=True)
    followup_email_body = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    status = Column(String(50), default="new")
    first_email_sent_at = Column(DateTime(timezone=True), nullable=True)
    followup_sent_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
