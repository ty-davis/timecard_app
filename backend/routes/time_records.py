from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.time_record import TimeRecord, RecordAttribute
from database import db
from datetime import datetime, timezone

time_records_bp = Blueprint('time_records', __name__)

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

@time_records_bp.route('/timerecords', methods=['GET'])
@jwt_required()
def get_time_records():
    current_user_id = get_jwt_identity()

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = TimeRecord.query.filter_by(user_id=current_user_id)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, DATE_FORMAT)
            query = query.filter(TimeRecord.timein >= start_date)
        except ValueError:
            return jsonify({"msg": "Invalid start date format. Use YYYY-MM-DDTHH:MM:SS.sssZ"}), 400

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, DATE_FORMAT)
            query = query.filter(TimeRecord.timein < end_date)
        except ValueError:
            return jsonify({"msg": "Invalid end date format. Use YYYY-MM-DDTHH:MM:SS.sssZ"}), 400


    items = query.order_by(TimeRecord.timein.desc()).all()
    return jsonify([item.to_dict() for item in items])


@time_records_bp.route('/recordattributes', methods=['GET'])
@jwt_required()
def get_record_attributes():
    current_user_id = get_jwt_identity()
    items = RecordAttribute.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.to_dict() for item in items])

def create_record_attribute(user_id, name, parent_id, level_num):
    if not name:
        raise ValueError("name was not specified for new record attribute")

    domain_attr = RecordAttribute.query.filter(
        RecordAttribute.name == name,
        RecordAttribute.user_id == user_id,
        RecordAttribute.level_num == level_num).first()
    if not domain_attr:
        domain_attr = RecordAttribute(
            user_id = user_id,
            name = name,
            parent_id = parent_id,
            level_num = level_num,
        )
        db.session.add(domain_attr)
        db.session.commit()
    return domain_attr.id

@time_records_bp.route('/timerecords', methods=['POST'])
@jwt_required()
def create_time_record():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not all(key in data for key in ['domain_id', 'category_id', 'title_id']):
        return jsonify({"msg": "Missing required fields"}), 400

    if not data['domain_id']:
        return jsonify({"msg": "That domain is not yet specified"}), 400

    if not isinstance(data['domain_id'], int):
        domain_id = create_record_attribute(current_user_id, data['domain_id'], None, 1)
        data['domain_id'] = domain_id

    if not isinstance(data['category_id'], int):
        category_id = create_record_attribute(current_user_id, data['category_id'], data['domain_id'], 2)
        data['category_id'] = category_id

    if not isinstance(data['title_id'], int):
        title_id = create_record_attribute(current_user_id, data['title_id'], data['category_id'], 3)
        data['title_id'] = title_id


    timein = datetime.strptime(data['timein'], DATE_FORMAT)
    timein.replace(tzinfo=timezone.utc)
    new_record = TimeRecord(
        user_id = current_user_id,
        domain_id = data['domain_id'],
        category_id = data['category_id'],
        title_id = data['title_id'],
        timein = timein,
        external_link = data.get('external_link'),
        notes = data.get('notes'),
        jira_issue_key = data.get('jira_issue_key'),
    )

    db.session.add(new_record)
    db.session.commit()

    return jsonify(new_record.to_dict()), 201

@time_records_bp.route('/timerecords/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_time_record(record_id):
    current_user_id = get_jwt_identity()

    record = TimeRecord.query.filter_by(id=record_id, user_id=current_user_id).first()

    if not record:
        return jsonify({"msg": "Record not found or access denied"}), 404

    data = request.get_json()

    if not isinstance(data['domain_id'], int):
        domain_id = create_record_attribute(current_user_id, data['domain_id'], None, 1)
        record.domain_id = domain_id
    else:
        record.domain_id = data['domain_id']


    if not isinstance(data['category_id'], int):
        category_id = create_record_attribute(current_user_id, data['category_id'], record.domain_id, 2)
        record.category_id = category_id
    else:
        record.category_id = data['category_id']

    if not isinstance(data['title_id'], int):
        title_id = create_record_attribute(current_user_id, data['title_id'], record.category_id, 3)
        record.title_id = title_id
    else:
        record.title_id = data['title_id']

    if 'timein' in data and data['timein']:
        try:
            timein = datetime.strptime(data['timein'], DATE_FORMAT)
            timein.replace(tzinfo=timezone.utc)
            record.timein = timein
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid timein format."}), 400

    if 'timeout' in data and data['timeout']:
        try:
            timeout = datetime.strptime(data['timeout'], DATE_FORMAT)
            timeout.replace(tzinfo=timezone.utc)
            record.timeout = timeout
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid timeout format."}), 400
    else:
        record.timeout = None

    if 'external_link' in data and data['external_link']:
        record.external_link = data['external_link']
    if 'notes' in data and data['notes']:
        record.notes = data['notes']
    if 'jira_issue_key' in data:
        record.jira_issue_key = data['jira_issue_key']

    db.session.commit()

    return jsonify(record.to_dict()), 200


@time_records_bp.route('/timerecords/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_time_record(record_id):
    current_user_id = get_jwt_identity()
    
    record = TimeRecord.query.filter_by(id=record_id, user_id=current_user_id).first()
    
    if not record:
        return jsonify({"msg": "Record not found or access denied"}), 404
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({"msg": "Record deleted successfully"}), 200




@time_records_bp.route('/recordattributes/<int:attribute_id>', methods=['PUT'])
@jwt_required()
def update_record_attribute(attribute_id):
    current_user_id = get_jwt_identity()

    # Find the specific attribute ensuring it belongs to the current user
    attribute = RecordAttribute.query.filter_by(id=attribute_id, user_id=current_user_id).first()

    if not attribute:
        return jsonify({"msg": "Record attribute not found or access denied"}), 404

    data = request.get_json()

    # Update fields if they are present in the request data
    if 'name' in data:
        attribute.name = data['name']
    
    if 'color' in data:
        attribute.color = data['color']
    
    # Note: It's generally not recommended to allow changing parent_id or level_num
    # via a simple update, as it can break the hierarchical integrity.
    # If you need this functionality, add it with careful validation.

    db.session.commit()

    return jsonify(attribute.to_dict()), 200
