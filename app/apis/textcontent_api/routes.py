from flask import request, jsonify
from app.extensions import db
from app.models.textcontent_models.models import TextContent # pastikan import-nya sesuai
from app.apis.textcontent_api import textcontent_bp  # asumsi kamu buat blueprint baru

# Add New TextContent
@textcontent_bp.route('/textcontent', methods=['POST'])
def add_textcontent():
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    content_type = data.get('content_type')
    file_url = data.get('file_url')
    category_id = data.get('category_id')
    product_id = data.get('product_id')
    created_by = data.get('created_by')

    if not title:
        return jsonify({'message': 'Title is required'}), 400

    new_content = TextContent(
        title=title,
        description=description,
        content_type=content_type,
        file_url=file_url,
        category_id=category_id,
        product_id=product_id,
        created_by=created_by
    )

    db.session.add(new_content)
    db.session.commit()

    return jsonify({'message': 'TextContent added successfully', 'id': new_content.id}), 201


# Edit Existing TextContent by ID
@textcontent_bp.route('/textcontent/<int:id>', methods=['PUT'])
def edit_textcontent(id):
    data = request.get_json()

    content = TextContent.query.get(id)
    if not content or content.rowstatus != 1:
        return jsonify({'message': 'TextContent not found'}), 404

    # Update fields if provided
    content.title = data.get('title', content.title)
    content.description = data.get('description', content.description)
    content.content_type = data.get('content_type', content.content_type)
    content.file_url = data.get('file_url', content.file_url)
    content.category_id = data.get('category_id', content.category_id)
    content.product_id = data.get('product_id', content.product_id)
    content.modified_by = data.get('modified_by', content.modified_by)

    db.session.commit()

    return jsonify({'message': 'TextContent updated successfully'}), 200


@textcontent_bp.route('/textcontent', methods=['GET'])
def get_textcontents():
    content_type = request.args.get('content_type')
    category_id = request.args.get('category_id')

    query = TextContent.query.filter_by(rowstatus=1)

    if content_type:
        query = query.filter_by(content_type=content_type)
    if category_id:
        query = query.filter_by(category_id=category_id)

    contents = query.all()

    result = []
    for content in contents:
        result.append({
            'id': content.id,
            'title': content.title,
            'description': content.description,
            'content_type': content.content_type,
            'file_url': content.file_url,
            'category_id': content.category_id,
            'product_id': content.product_id,
            'created_by': content.created_by,
            'created_date': content.created_date.isoformat() if content.created_date else None,
            'modified_by': content.modified_by,
            'modified_date': content.modified_date.isoformat() if content.modified_date else None
        })

    return jsonify({'data': result}), 200