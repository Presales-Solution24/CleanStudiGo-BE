import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.apis.category_api import category_bp
from app.models.product_models.models import Product, Category
from app.models.specification_models.models import SpecificationDefinition, SpecificationValue
from app.extensions import db
from app.utils.auth_utils import token_required

UPLOAD_FOLDER = 'uploads/category'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@category_bp.route('/list', methods=['GET'])
@token_required
def list_categories(current_user):
    keyword = request.args.get('keyword', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Category.query.filter(Category.rowstatus == 1)

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            (Category.name.ilike(search))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    categories = pagination.items

    result = {
        'total': pagination.total,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'categories': [
            {
                'id': category.id,
                'name': category.name,
                'image_url': category.image_url
            } for category in categories
        ]
    }

    return jsonify(result), 200


# 2. GetData
@category_bp.route('/get/<string:category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    category = Category.query.filter_by(id=category_id, rowstatus=1).first()

    if not Category:
        return jsonify({'message': 'Category not found'}), 404

    result = {
        'id': category.id,
        'name': category.name,
        'image_url': category.image_url,
        'created_date': category.created_date.strftime('%Y-%m-%d %H:%M:%S') if category.created_date else None,
        'modified_date': category.modified_date.strftime('%Y-%m-%d %H:%M:%S') if category.modified_date else None
    }

    return jsonify(result), 200

# 3. SaveUpdate
@category_bp.route('/save', methods=['POST'])
@token_required
def save_or_update_category(current_user):
    # Karena sekarang multipart, ambil pakai request.form
    category_id = request.form.get('id')
    name = request.form.get('name')
    # brand = request.form.get('brand')
    # category_id = request.form.get('category_id', type=int)
    image_file = request.files.get('image')  # File gambar opsional

    # Basic validation
    required_fields = ['name']
    # missing_fields = [field for field in required_fields if not locals().get(field)]

    # if missing_fields:
    #     return jsonify({
    #         'message': f'Missing required fields: {", ".join(missing_fields)}'
    #     }), 400
    
    missing_fields = []
    for field in required_fields:
        if not request.form.get(field):
            missing_fields.append(field)

    if missing_fields:
        return jsonify({
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400

    # Cek dan buat folder upload jika belum ada
    upload_folder_full = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_folder_full, exist_ok=True)

    # Simpan file kalau ada image
    image_url = None
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(f"{str(uuid.uuid4())}.{image_file.filename.rsplit('.', 1)[1].lower()}")
        image_path = os.path.join(upload_folder_full, filename)
        image_file.save(image_path)
        image_url = f"/{UPLOAD_FOLDER}/{filename}"

    if category_id:
        # Update existing category
        category = Category.query.filter_by(id=category_id, rowstatus=1).first()

        if not category:
            return jsonify({'message': 'Category not found'}), 404

        category.name = name
        # category.brand = brand
        # category.category_id = category_id

        if image_url:
            category.image_url = image_url  # Update image only if new image uploaded

        category.modified_by = current_user.username
        db.session.commit()

        return jsonify({'message': 'Category updated successfully'}), 200

    else:
        # Create new category
        new_category = Category(
            name=name,
            # brand=brand,
            # category_id=category_id,
            image_url=image_url,
            created_by=current_user.username
        )
        db.session.add(new_category)
        db.session.commit()

        return jsonify({'message': 'Category created successfully'}), 201


@category_bp.route('/delete/<string:category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    category = Category.query.filter_by(id=category_id, rowstatus=1).first()

    if not category:
        return jsonify({'message': 'Category not found'}), 404

    # Hapus file image jika ada
    if category.image_url:
        image_path = os.path.join(current_app.root_path, category.image_url.lstrip('/'))
        if os.path.exists(image_path):
            os.remove(image_path)

    # Soft delete category
    category.rowstatus = 0
    category.modified_by = current_user.username

    db.session.commit()

    return jsonify({'message': 'Category deleted successfully'}), 200
