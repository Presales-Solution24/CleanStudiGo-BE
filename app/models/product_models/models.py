from app.extensions import db
from datetime import datetime
import uuid

class Category(db.Model):
    __tablename__ = 'tbl_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Common fields
    rowstatus = db.Column(db.Integer, default=1)  # 1 = Active, 0 = Deleted
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationship
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'tbl_products'

    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('tbl_categories.id'), nullable=False)
    image_url = db.Column(db.String(255))

    # Common fields
    rowstatus = db.Column(db.Integer, default=1)  # 1 = Active, 0 = Deleted
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)
