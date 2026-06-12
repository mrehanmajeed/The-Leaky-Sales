import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from config import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, plain_body: str, reply_to: str = None) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"ShopRocket Sales <{settings.GMAIL_SENDER_EMAIL}>"
        msg["To"] = to_email
        if reply_to:
            msg["Reply-To"] = reply_to

        # HTML version
        html_body = f"""
        <html>
          <body style="background-color: #f8f9fa; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-top: 4px solid #001f3f; font-family: Arial, sans-serif; border-radius: 4px;">
              <div style="white-space: pre-wrap; font-size: 15px; color: #333333; line-height: 1.6;">{plain_body}</div>
              <hr style="border: none; border-top: 1px solid #eeeeee; margin-top: 30px; margin-bottom: 20px;">
              <div style="font-size: 12px; color: #888888; text-align: center;">
                ShopRocket Electronics
              </div>
            </div>
          </body>
        </html>
        """

        part1 = MIMEText(plain_body, "plain")
        part2 = MIMEText(html_body, "html")

        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(settings.GMAIL_SENDER_EMAIL, settings.GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"SMTP Recipients Refused: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
