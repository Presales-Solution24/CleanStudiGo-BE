import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.apis.content_api import content_bp
from app.models.content_models.models import Content
from app.extensions import db
from app.utils.auth_utils import token_required
from datetime import datetime

# 1. List konten
@content_bp.route('/list', methods=['GET'])
@token_required
def list_content(current_user):
    category_id = request.args.get('category_id', type=int)
    product_id = request.args.get('product_id', type=int)

    query = Content.query.filter_by(rowstatus=1)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if product_id:
        query = query.filter_by(product_id=product_id)

    contents = query.order_by(Content.created_date.desc()).all()

    result = [{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'content_type': c.content_type,
        'file_url': c.file_url,
        'views': c.views,
        'category_id': c.category_id,
        'product_id': c.product_id
    } for c in contents]

    return jsonify(result), 200

# 2. Tambah konten
# File types allowed
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Final /save endpoint
@content_bp.route('/save', methods=['POST'])
@token_required
def save_content(current_user):
    title = request.form.get('title')
    description = request.form.get('description')
    content_type = request.form.get('content_type')
    category_id = request.form.get('category_id')
    product_id = request.form.get('product_id')
    file = request.files.get('file')

    if not title or not content_type:
        return jsonify({'message': 'Missing required fields'}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({'message': 'Valid file is required (.jpg, .pdf, .mp4, etc)'}), 400

    # Handle secure filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    # Save path
    save_dir = os.path.join(current_app.root_path, 'uploads', 'contents')
    os.makedirs(save_dir, exist_ok=True)
    full_path = os.path.join(save_dir, unique_filename)
    file.save(full_path)

    # File URL for client access
    file_url = f"/uploads/contents/{unique_filename}"

    new_content = Content(
        title=title,
        description=description,
        content_type=content_type,
        file_url=file_url,
        category_id=int(category_id) if category_id else None,
        product_id=product_id if product_id else None,
        created_by=current_user.username
    )

    db.session.add(new_content)
    db.session.commit()

    return jsonify({'message': 'Content uploaded successfully', 'file_url': file_url}), 201

# 3. Detail + naikkan views
@content_bp.route('/view/<int:content_id>', methods=['GET'])
@token_required
def view_content(current_user, content_id):
    content = Content.query.filter_by(id=content_id, rowstatus=1).first()
    if not content:
        return jsonify({'message': 'Content not found'}), 404

    # Naikkan views
    content.views = (content.views or 0) + 1
    db.session.commit()

    result = {
        'id': content.id,
        'title': content.title,
        'description': content.description,
        'content_type': content.content_type,
        'file_url': content.file_url,
        'category_id': content.category_id,
        'product_id': content.product_id,
        'views': content.views
    }

    return jsonify(result), 200

@content_bp.route('/delete/<int:content_id>', methods=['DELETE'])
@token_required
def delete_content(current_user, content_id):
    from app.models.content_models.models import Content  # safe import kalau belum ada

    content = Content.query.filter_by(id=content_id, rowstatus=1).first()

    if not content:
        return jsonify({'message': 'Content not found'}), 404

    # Hapus file fisik jika ada (opsional)
    if content.file_url:
        import os
        from flask import current_app

        file_path = os.path.join(current_app.root_path, content.file_url.lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)

    # Soft delete
    content.rowstatus = 0
    content.modified_by = current_user.username
    db.session.commit()

    return jsonify({'message': 'Content deleted successfully'}), 200
