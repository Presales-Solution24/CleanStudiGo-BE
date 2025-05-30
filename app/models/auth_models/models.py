from app.extensions import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')


    def check_password(self, password):
        print('Comparing password:', password)
        print('Against hash:', self.password_hash)
        result = check_password_hash(self.password_hash, password)
        print('Result of check_password:', result)
        return result