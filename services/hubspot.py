import requests
import logging
from config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"Bearer {settings.HUBSPOT_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}
BASE_URL = "https://api.hubapi.com"

def create_contact(lead) -> str | None:
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    
    parts = lead.name.split(" ", 1)
    firstname = parts[0]
    lastname = parts[1] if len(parts) > 1 else ""

    payload = {
        "properties": {
            "firstname": firstname,
            "lastname": lastname,
            "email": lead.email,
            "phone": lead.phone or "",
            "hs_lead_status": "NEW",
            "leadsource": "WEBSITE"
        }
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        
        if response.status_code == 201:
            return response.json().get("id")
        
        if response.status_code == 409:
            # Contact already exists, search by email
            search_url = f"{BASE_URL}/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": lead.email
                            }
                        ]
                    }
                ]
            }
            search_res = requests.post(search_url, headers=HEADERS, json=search_payload, timeout=10)
            if search_res.status_code == 200:
                results = search_res.json().get("results", [])
                if results:
                    return results[0].get("id")
            
        logger.error(f"Failed to create/find HubSpot contact: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error in HubSpot create_contact: {e}")
        return None

def create_deal(lead, contact_id: str) -> str | None:
    if not contact_id:
        return None
        
    url = f"{BASE_URL}/crm/v3/objects/deals"
    
    # Clean budget string
    amount = lead.budget or "0"
    amount = amount.replace("$", "").replace(",", "").strip()
    if not amount.isdigit():
        amount = "0"
        
    payload = {
        "properties": {
            "dealname": f"Quote — {lead.product} — {lead.name}",
            "pipeline": "default",
            "dealstage": "appointmentscheduled",
            "amount": amount
        }
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        
        if response.status_code == 201:
            deal_id = response.json().get("id")
            
            # Associate deal with contact
            assoc_url = f"{BASE_URL}/crm/v4/associations/deals/contacts/batch/create"
            assoc_payload = {
                "inputs": [
                    {
                        "from": {"id": deal_id},
                        "to": {"id": contact_id},
                        "type": "deal_to_contact"
                    }
                ]
            }
            assoc_res = requests.post(assoc_url, headers=HEADERS, json=assoc_payload, timeout=10)
            if assoc_res.status_code != 201:
                logger.error(f"Failed to associate deal with contact: {assoc_res.text}")
            
            return deal_id
            
        logger.error(f"Failed to create HubSpot deal: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error in HubSpot create_deal: {e}")
        return None
