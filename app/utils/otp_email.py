import smtplib
from email.message import EmailMessage
import random
import os

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')

        # Cek ENV sudah ke-load atau belum
        if not smtp_server or not smtp_port or not smtp_user or not smtp_password:
            print("[ERROR] SMTP config belum lengkap atau belum ke-load dari .env")
            return False

        print(f"[INFO] Kirim email ke {to_email} via {smtp_server}:{smtp_port}")

        msg = EmailMessage()
        msg['Subject'] = 'Your Login OTP'
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg.set_content(f'Your OTP code is: {otp}')

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()               # say hello ke server
            server.starttls()          # upgrade koneksi ke TLS
            server.ehlo()               # say hello lagi setelah TLS aktif
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print("[INFO] Email OTP berhasil dikirim.")
        return True

    except Exception as e:
        print(f"[ERROR] Gagal kirim email: {str(e)}")
        return False