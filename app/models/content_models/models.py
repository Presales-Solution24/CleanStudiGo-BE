from app.extensions import db
from datetime import datetime

class Content(db.Model):
    __tablename__ = 'tbl_contents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(50))  # video/image/pdf
    file_url = db.Column(db.String(500))
    category_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.String(36), nullable=True)
    views = db.Column(db.Integer, default=0)
    rowstatus = db.Column(db.Integer, default=1)
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)

    comments = db.relationship('ContentComment', backref='content', lazy=True)
    ratings = db.relationship('ContentRating', backref='content', lazy=True)


class ContentComment(db.Model):
    __tablename__ = 'tbl_content_comments'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('tbl_contents.id'), nullable=False)
    user_id = db.Column(db.Integer)
    comment_text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    rowstatus = db.Column(db.Integer, default=1)


class ContentRating(db.Model):
    __tablename__ = 'tbl_content_ratings'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('tbl_contents.id'), nullable=False)
    user_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)  # 1 to 5
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)
