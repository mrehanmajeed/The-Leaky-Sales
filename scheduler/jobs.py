import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="UTC")

def process_new_leads():
    # Import inside to avoid circular imports
    from database.connection import SessionLocal
    from database.models import Lead
    from services.sheets import fetch_all_rows
    from services.hubspot import create_contact, create_deal
    from services.ai import generate_first_email
    from services.mailer import send_email

    logger.info("Running process_new_leads job...")
    db = SessionLocal()
    try:
        rows = fetch_all_rows()
        for row in rows:
            email = row.get("Email", "").strip()
            if not email:
                continue

            existing_lead = db.query(Lead).filter(Lead.email == email).first()
            if existing_lead:
                continue

            # Create lead
            lead = Lead(
                name=row.get("Name", "").strip(),
                email=email,
                phone=str(row.get("Phone", "")).strip(),
                product=row.get("Product", "").strip(),
                budget=str(row.get("Budget", "")).strip(),
                message=row.get("Message", "").strip()
            )
            db.add(lead)
            db.flush()

            # HubSpot
            contact_id = create_contact(lead)
            if contact_id:
                lead.hubspot_contact_id = contact_id
                deal_id = create_deal(lead, contact_id)
                if deal_id:
                    lead.hubspot_deal_id = deal_id

            # AI Email
            email_body = generate_first_email(lead.name, lead.product, lead.budget, lead.message)
            lead.first_email_body = email_body

            # Send Email
            subject = f"Your ShopRocket Quote for {lead.product} — Let's Talk"
            success = send_email(to_email=lead.email, subject=subject, plain_body=email_body)

            if success:
                lead.first_email_sent_at = datetime.now(timezone.utc)
                lead.status = "email_sent"
            else:
                lead.status = "email_failed"
                lead.error_log = "SMTP failure on first email"

            db.commit()
    except Exception as e:
        logger.error(f"Error in process_new_leads: {e}")
        db.rollback()
    finally:
        db.close()

def send_followups():
    from database.connection import SessionLocal
    from database.models import Lead
    from services.ai import generate_followup_email
    from services.mailer import send_email

    logger.info("Running send_followups job...")
    db = SessionLocal()
    try:
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        leads = db.query(Lead).filter(
            Lead.status == "email_sent",
            Lead.first_email_sent_at <= three_days_ago,
            Lead.followup_sent_at == None
        ).all()

        for lead in leads:
            email_body = generate_followup_email(lead.name, lead.product)
            lead.followup_email_body = email_body

            first_name = lead.name.split()[0] if lead.name else "there"
            subject = f"Still thinking about the {lead.product}, {first_name}?"
            
            success = send_email(to_email=lead.email, subject=subject, plain_body=email_body)
            if success:
                lead.followup_sent_at = datetime.now(timezone.utc)
                lead.status = "follow_up_sent"
            else:
                lead.error_log = "SMTP failure on follow-up email"

            db.commit()
    except Exception as e:
        logger.error(f"Error in send_followups: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(
        process_new_leads, 
        trigger=IntervalTrigger(minutes=5), 
        id="process_leads", 
        replace_existing=True
    )
    scheduler.add_job(
        send_followups, 
        trigger=CronTrigger(hour=9, minute=0), 
        id="followups", 
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")
