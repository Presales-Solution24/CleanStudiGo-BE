import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.apis.product_api import product_bp
from app.models.product_models.models import Product, Category
from app.extensions import db
from app.utils.auth_utils import token_required

UPLOAD_FOLDER = 'uploads/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@product_bp.route('/list', methods=['GET'])
@token_required
def list_products(current_user):
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Product.query.filter(Product.rowstatus == 1)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            (Product.name.ilike(search)) |
            (Product.brand.ilike(search))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    products = pagination.items

    result = {
        'total': pagination.total,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'brand': product.brand,
                'category_id': product.category_id,
                'image_url': product.image_url
            } for product in products
        ]
    }

    return jsonify(result), 200


# 2. GetData
@product_bp.route('/get/<string:product_id>', methods=['GET'])
@token_required
def get_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id, rowstatus=1).first()

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    result = {
        'id': product.id,
        'name': product.name,
        'brand': product.brand,
        'category_id': product.category_id,
        'image_url': product.image_url,
        'created_date': product.created_date.strftime('%Y-%m-%d %H:%M:%S') if product.created_date else None,
        'modified_date': product.modified_date.strftime('%Y-%m-%d %H:%M:%S') if product.modified_date else None
    }

    return jsonify(result), 200


# 3. SaveUpdate
@product_bp.route('/save', methods=['POST'])
@token_required
def save_or_update_product(current_user):
    # Karena sekarang multipart, ambil pakai request.form
    product_id = request.form.get('id')
    name = request.form.get('name')
    brand = request.form.get('brand')
    category_id = request.form.get('category_id', type=int)
    image_file = request.files.get('image')  # File gambar opsional

    # Basic validation
    required_fields = ['name', 'brand', 'category_id']
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

    if product_id:
        # Update existing product
        product = Product.query.filter_by(id=product_id, rowstatus=1).first()

        if not product:
            return jsonify({'message': 'Product not found'}), 404

        product.name = name
        product.brand = brand
        product.category_id = category_id

        if image_url:
            product.image_url = image_url  # Update image only if new image uploaded

        product.modified_by = current_user.username
        db.session.commit()

        return jsonify({'message': 'Product updated successfully'}), 200

    else:
        # Create new product
        new_product = Product(
            name=name,
            brand=brand,
            category_id=category_id,
            image_url=image_url,
            created_by=current_user.username
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({'message': 'Product created successfully'}), 201


@product_bp.route('/delete/<string:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id, rowstatus=1).first()

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Hapus file image jika ada
    if product.image_url:
        image_path = os.path.join(current_app.root_path, product.image_url.lstrip('/'))
        if os.path.exists(image_path):
            os.remove(image_path)

    # Soft delete produk
    product.rowstatus = 0
    product.modified_by = current_user.username
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200
