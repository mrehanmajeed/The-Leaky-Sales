# ShopRocket Lead Pipeline

This is a production-grade automated lead pipeline system. It polls a Google Sheet for new leads, handles a POST webhook for direct submissions, creates a Contact and Deal in HubSpot CRM, generates a personalized email using Gemini AI, and sends it via Gmail SMTP.

## HOW TO RUN

```bash

# 1. Add service_account.json (Google Cloud Service Account with Sheets + Drive API)
# Place it in the root directory.

# 2. Install deps
pip install -r requirements.txt

# 3. Run
uvicorn main:app --reload --port 8000

# Dashboard: http://localhost:8000
# API docs:  http://localhost:8000/docs
```
