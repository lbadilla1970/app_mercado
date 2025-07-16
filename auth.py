from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from models import User, PasswordReset
from datetime import datetime, timedelta
import secrets
import smtplib
import os
from email.message import EmailMessage

RESET_EXPIRY_HOURS = 1

def authenticate(db: Session, email: str, password: str):
    user = db.query(User).filter_by(email=email).first()
    if user and bcrypt.verify(password, user.password_hash):
        return user
    return None

def create_user(db: Session, email: str, password: str, company_id: int, role_id: int):
    hashed = bcrypt.hash(password)
    user = User(email=email, password_hash=hashed,
                company_id=company_id, role_id=role_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def change_password(db: Session, user: User, new_password: str):
    user.password_hash = bcrypt.hash(new_password)
    db.commit()

def generate_reset_token(db: Session, user: User):
    token = secrets.token_urlsafe(16)
    expiry = datetime.utcnow() + timedelta(hours=RESET_EXPIRY_HOURS)
    rec = PasswordReset(user_id=user.id, token=token, expiry=expiry)
    db.add(rec)
    db.commit()
    return token

def verify_reset_token(db: Session, email: str, token: str):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        return None
    rec = db.query(PasswordReset).filter_by(user_id=user.id, token=token).first()
    if rec and rec.expiry >= datetime.utcnow():
        return user
    return None

def send_reset_email(to_email: str, token: str):
    server = os.getenv('SMTP_SERVER')
    port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER')
    password = os.getenv('SMTP_PASSWORD')
    if not all([server, port, user, password]):
        return
    msg = EmailMessage()
    msg['Subject'] = 'Recuperación de contraseña'
    msg['From'] = user
    msg['To'] = to_email
    msg.set_content(f'Su token de recuperación es: {token}')
    with smtplib.SMTP(server, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
