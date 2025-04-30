from app.extensions import db
from datetime import datetime

class SpecificationDefinition(db.Model):
    __tablename__ = 'tbl_specification_definitions'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, nullable=False)  # Relasi ke tbl_categories.id
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20))
    better_preference = db.Column(db.String(10))  # New Field: 'higher' or 'lower'
    rowstatus = db.Column(db.Integer, default=1)
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)


class SpecificationValue(db.Model):
    __tablename__ = 'tbl_specification_values'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('tbl_products.id'), nullable=False)
    specification_id = db.Column(db.Integer, db.ForeignKey('tbl_specification_definitions.id'), nullable=False)
    value = db.Column(db.String(100))
    rowstatus = db.Column(db.Integer, default=1)
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)
