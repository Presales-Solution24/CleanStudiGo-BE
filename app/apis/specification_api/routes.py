from flask import request, jsonify
from app.apis.specification_api import specification_bp
from app.models.product_models.models import Product
from app.models.specification_models.models import SpecificationDefinition, SpecificationValue

from app.extensions import db
from app.utils.auth_utils import token_required
from datetime import datetime


# 1. List Specification Definitions
@specification_bp.route('/definition/list', methods=['GET'])
@token_required
def list_specification_definitions(current_user):
    category_id = request.args.get('category_id', type=int)

    if not category_id:
        return jsonify({'message': 'category_id is required'}), 400

    definitions = SpecificationDefinition.query.filter_by(
        category_id=category_id,
        rowstatus=1
    ).all()

    result = [
        {
            'id': definition.id,
            'category_id': definition.category_id,
            'name': definition.name,
            'unit': definition.unit
        } for definition in definitions
    ]

    return jsonify(result), 200

# 2. Save or Update Specification Definition
@specification_bp.route('/definition/save', methods=['POST'])
@token_required
def save_or_update_specification_definition(current_user):
    data = request.get_json()

    definition_id = data.get('id')
    category_id = data.get('category_id')
    name = data.get('name')
    unit = data.get('unit', '')
    better_preference = data.get('better_preference', None)  # Ambil field baru

    # Basic validation
    if not category_id or not name:
        return jsonify({'message': 'category_id and name are required fields.'}), 400

    if definition_id:
        # Update existing definition
        definition = SpecificationDefinition.query.filter_by(id=definition_id, rowstatus=1).first()

        if not definition:
            return jsonify({'message': 'Specification Definition not found'}), 404

        definition.category_id = category_id
        definition.name = name
        definition.unit = unit
        definition.better_preference = better_preference
        definition.modified_by = current_user.username
        definition.modified_date = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Specification Definition updated successfully'}), 200

    else:
        # Create new definition
        new_definition = SpecificationDefinition(
            category_id=category_id,
            name=name,
            unit=unit,
            better_preference=better_preference,
            created_by=current_user.username
        )
        db.session.add(new_definition)
        db.session.commit()

        return jsonify({'message': 'Specification Definition created successfully'}), 201

# 1. List Specification Values by Product
@specification_bp.route('/value/list', methods=['GET'])
@token_required
def list_specification_values(current_user):
    product_id = request.args.get('product_id')

    if not product_id:
        return jsonify({'message': 'product_id is required'}), 400

    product = Product.query.filter_by(id=product_id, rowstatus=1).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Ambil semua definition untuk kategori product tersebut
    definitions = SpecificationDefinition.query.filter_by(
        category_id=product.category_id,
        rowstatus=1
    ).all()

    result = []

    for definition in definitions:
        value_entry = SpecificationValue.query.filter_by(
            product_id=product_id,
            specification_id=definition.id,
            rowstatus=1
        ).first()

        result.append({
            'specification_id': definition.id,
            'name': definition.name,
            'unit': definition.unit,
            'better_preference': definition.better_preference,
            'value': value_entry.value if value_entry else None
        })

    return jsonify(result), 200

# 2. Save/Update Specification Values
@specification_bp.route('/value/save', methods=['POST'])
@token_required
def save_or_update_specification_values(current_user):
    data = request.get_json()

    product_id = data.get('product_id')
    specifications = data.get('specifications', [])

    if not product_id or not specifications:
        return jsonify({'message': 'product_id and specifications are required fields.'}), 400

    product = Product.query.filter_by(id=product_id, rowstatus=1).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    for spec in specifications:
        spec_id = spec.get('specification_id')
        value = spec.get('value')

        if not spec_id:
            continue  # Skip jika tidak ada spec id

        spec_value = SpecificationValue.query.filter_by(
            product_id=product_id,
            specification_id=spec_id,
            rowstatus=1
        ).first()

        if spec_value:
            # Update
            spec_value.value = value
            spec_value.modified_by = current_user.username
            spec_value.modified_date = datetime.utcnow()
        else:
            # Insert
            new_spec_value = SpecificationValue(
                product_id=product_id,
                specification_id=spec_id,
                value=value,
                created_by=current_user.username
            )
            db.session.add(new_spec_value)

    db.session.commit()

    return jsonify({'message': 'Specification values saved successfully'}), 200

@specification_bp.route('/compare', methods=['GET'])
@token_required
def compare_products(current_user):
    product_a_id = request.args.get('product_a')
    product_b_id = request.args.get('product_b')

    if not product_a_id or not product_b_id:
        return jsonify({'message': 'Both product_a and product_b are required'}), 400

    product_a = Product.query.filter_by(id=product_a_id, rowstatus=1).first()
    product_b = Product.query.filter_by(id=product_b_id, rowstatus=1).first()

    if not product_a or not product_b:
        return jsonify({'message': 'One or both products not found'}), 404

    if product_a.category_id != product_b.category_id:
        return jsonify({'message': 'Products must be in the same category to compare'}), 400

    category_id = product_a.category_id

    # Ambil semua spek di kategori tersebut
    definitions = SpecificationDefinition.query.filter_by(category_id=category_id, rowstatus=1).all()

    result = []

    for spec in definitions:
        value_a = SpecificationValue.query.filter_by(
            product_id=product_a_id,
            specification_id=spec.id,
            rowstatus=1
        ).first()

        value_b = SpecificationValue.query.filter_by(
            product_id=product_b_id,
            specification_id=spec.id,
            rowstatus=1
        ).first()

        result.append({
            'specification_id': spec.id,
            'name': spec.name,
            'unit': spec.unit,
            'better_preference': spec.better_preference,
            'value_a': value_a.value if value_a else None,
            'value_b': value_b.value if value_b else None
        })

#Kalau better_preference == "higher" ➜ nilai lebih besar = lebih bagus.
#Kalau better_preference == "lower" ➜ nilai lebih kecil = lebih bagus.
#Kalau value_b == null ➜ tampilkan "N/A".
#Bisa tambahkan kolom winner: "A"/"B"/"tie" jika butuh logic di backend (optional).

    return jsonify(result), 200