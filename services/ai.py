import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_first_email(name: str, product: str, budget: str, message: str) -> str:
    prompt = f"""
Act as a ShopRocket sales rep at a premium electronics brand.
Write a personalized first-contact email addressing the lead by their first name ({name}).
Reference the SPECIFIC product they asked about ({product}).
Include one concrete, specific benefit of that product category.
End with exactly ONE CTA: offer a 10-minute call OR ask about delivery timeline.
Tone: friendly, professional, zero pressure.
Length: 100–120 words strictly.
Output ONLY the email body — no subject line, no signature, no markdown.

Additional lead details: Budget: {budget}, Message: {message}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback template
        first_name = name.split()[0] if name else "there"
        fallback = f"Hi {first_name},\n\nThanks for reaching out about the {product}. We pride ourselves on offering premium quality and fantastic support. I'd love to learn more about your setup to see if it's the perfect fit.\n\nAre you available for a brief 10-minute call this week to discuss?\n\nBest,"
        return fallback

def generate_followup_email(name: str, product: str) -> str:
    prompt = f"""
Act as a ShopRocket sales rep.
Write a non-pushy 3-day follow-up for a lead who hasn't replied.
Address the lead by their first name ({name}).
Acknowledge they are busy (one sentence).
Restate one specific value of the product ({product}).
CTA: suggest one specific short time window ("free for 10 mins Thursday?").
Tone: warm, human, not salesy.
Length: 70–85 words strictly.
Output ONLY the email body — no subject line, no signature, no markdown.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        first_name = name.split()[0] if name else "there"
        fallback = f"Hi {first_name},\n\nI know you're likely busy, so I'll keep this short. I wanted to follow up on your interest in the {product}. It really is a game-changer for enhancing your setup.\n\nAre you free for 10 mins this Thursday to chat?\n\nBest,"
        return fallback
