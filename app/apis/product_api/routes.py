from flask import request, jsonify
from app.apis.product_api import product_bp
from app.models.product_models.models import Product, Category
from app.extensions import db
from app.utils.auth_utils import token_required


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
    data = request.get_json()

    required_fields = ['name', 'brand', 'category_id']
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400

    product_id = data.get('id')  # UUID string
    name = data['name']
    brand = data['brand']
    category_id = data['category_id']
    image_url = data.get('image_url', '')

    if product_id:
        # Update existing product
        product = Product.query.filter_by(id=product_id, rowstatus=1).first()

        if not product:
            return jsonify({'message': 'Product not found'}), 404

        product.name = name
        product.brand = brand
        product.category_id = category_id
        product.image_url = image_url
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


# 4. Delete (soft delete)
@product_bp.route('/delete/<string:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id, rowstatus=1).first()

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    product.rowstatus = 0
    product.modified_by = current_user.username
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200
