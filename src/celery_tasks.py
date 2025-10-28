from celery import Celery
from src.mail import mail, create_message, send_verification_email,mail_config
from asgiref.sync import async_to_sync
from fastapi_mail import FastMail
from pathlib import Path
celery_app = Celery()

celery_app.config_from_object("src.config")

TEMPLATE_FOLDER=Path(__file__).parent / "templates"

# verify_template = TEMPLATE_FOLDER / "verify_email.html"

# @celery_app.task()
# def send_email(recipients: list[str], subject: str, body: str):
#     message = create_message(recipients=recipients, subject=subject, body=body)
#     # send_verification_email(email=email, username=user_data.username, verify_link=Link)

#     async_to_sync(mail.send_message)(message)

fm = FastMail(mail_config)

@celery_app.task()
def send_templated_email_by_celery(email: str, username: str, verify_link: str):
    """Send a templated verification email by celery"""
    message =  send_verification_email(
        email, username, verify_link
    )
    
    async_to_sync(fm.send_message)(message, template_name="verify_email.html")
