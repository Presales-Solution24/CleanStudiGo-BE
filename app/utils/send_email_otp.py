from flask_mail import Message
from app import mail
import random

def send_email_otp(email):
    otp_code = str(random.randint(100000, 999999))
    msg = Message('Kode OTP Login Anda',
                  sender='youremail@gmail.com',
                  recipients=[email])
    msg.body = f'Kode OTP kamu: {otp_code}. Berlaku 5 menit.'

    mail.send(msg)
    return otp_code
