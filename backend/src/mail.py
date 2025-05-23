from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from config import Config
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
mail_config = ConnectionConfig(
    MAIL_USERNAME= Config.MAIL_USERNAME,
    MAIL_PASSWORD= Config.MAIL_PASSWORD,
    MAIL_FROM= Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER= Config.MAIL_SERVER,
    MAIL_FROM_NAME= Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS= False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

mail = FastMail(
    config= mail_config
)

def create_message(receipients: list[str], subject: str, body: str):

    message = MessageSchema(recipients=receipients, subject= subject, body = body, subtype= MessageType.html)

    return message

