from app.extensions import db
from datetime import datetime

class TextContent(db.Model):
    __tablename__ = 'tbl_textcontents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(50))  # glosary/article/pricelist
    file_url = db.Column(db.String(500))
    category_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.String(36), nullable=True)
    rowstatus = db.Column(db.Integer, default=1)
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)