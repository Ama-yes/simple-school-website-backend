from app.core.celery_app import celery_worker
from app.core.logging import setup_logger

logger = setup_logger()

@celery_worker.task
def send_email(name: str, email: str, message: str):
    with open("email.log", "a") as file:
        file.write(f"Sent to {email}:\nHey {name},\n\n{message}")
        
    logger.info(f"Email sent to {name}!")
    return f"Email sent to {name}!"