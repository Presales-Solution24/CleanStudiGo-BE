from flask import request, jsonify
from app.apis.content_api import content_bp
from app.models.content_models.models import ContentComment
from app.extensions import db
from app.utils.auth_utils import token_required
from datetime import datetime

# 1. Tambah komentar
@content_bp.route('/comment/add', methods=['POST'])
@token_required
def add_comment(current_user):
    data = request.get_json()

    content_id = data.get('content_id')
    comment_text = data.get('comment_text')

    if not content_id or not comment_text:
        return jsonify({'message': 'content_id and comment_text are required'}), 400

    comment = ContentComment(
        content_id=content_id,
        user_id=current_user.id,
        comment_text=comment_text
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201

# 2. List komentar by content_id
@content_bp.route('/comment/list/<int:content_id>', methods=['GET'])
@token_required
def list_comments(current_user, content_id):
    comments = (
        ContentComment.query
        .filter_by(content_id=content_id, rowstatus=1)
        .order_by(ContentComment.created_date.desc())
        .all()
    )

    result = [
        {
            'id': c.id,
            'user_id': c.user_id,
            'comment_text': c.comment_text,
            'created_date': c.created_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        for c in comments
    ]

    return jsonify(result), 200
