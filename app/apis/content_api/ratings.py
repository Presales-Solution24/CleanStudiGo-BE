from flask import request, jsonify
from app.apis.content_api import content_bp
from app.models.content_models.models import ContentRating
from app.extensions import db
from app.utils.auth_utils import token_required
from datetime import datetime

# 1. Submit rating
@content_bp.route('/rating/submit', methods=['POST'])
@token_required
def submit_rating(current_user):
    data = request.get_json()
    content_id = data.get('content_id')
    rating_value = data.get('rating')

    if not content_id or not rating_value:
        return jsonify({'message': 'content_id and rating are required'}), 400

    if not (1 <= int(rating_value) <= 5):
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400

    # Cek apakah user sudah pernah rating
    existing = ContentRating.query.filter_by(content_id=content_id, user_id=current_user.id).first()

    if existing:
        existing.rating = rating_value
        existing.modified_date = datetime.utcnow()
    else:
        new_rating = ContentRating(
            content_id=content_id,
            user_id=current_user.id,
            rating=rating_value
        )
        db.session.add(new_rating)

    db.session.commit()
    return jsonify({'message': 'Rating submitted successfully'}), 200

# 2. Get average rating
@content_bp.route('/rating/average/<int:content_id>', methods=['GET'])
@token_required
def get_average_rating(current_user, content_id):
    ratings = ContentRating.query.filter_by(content_id=content_id).all()

    if not ratings:
        return jsonify({'average_rating': 0, 'total_ratings': 0}), 200

    total = sum(r.rating for r in ratings)
    count = len(ratings)
    average = round(total / count, 2)

    return jsonify({
        'average_rating': average,
        'total_ratings': count
    }), 200
