from app.core.celery_app import celery_worker
from app.core.logging import setup_logger
from app.core.config import settings
from email.message import EmailMessage
from smtplib import SMTP

logger = setup_logger()

@celery_worker.task
def send_email(email: str, message: str, subject: str):
    
    email_msg = EmailMessage()
    email_msg.set_content(message)
    email_msg["Subject"] = subject
    email_msg["From"] = settings.smtp_user or "noreply@schoolapp.com"
    email_msg["To"] = email
    
    try:
        with SMTP(settings.smtp_server, int(settings.smtp_port)) as server:
            if settings.smtp_user and settings.smtp_password:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            
            server.send_message(email_msg)
            
            logger.info(f'"{subject}" email sent to {email}')
            return f"Email sent to {email}"
        
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
        return f"Failure to send email {str(e)}"