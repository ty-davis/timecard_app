from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.time_record import TimeRecord, RecordAttribute
from database import db
from datetime import datetime, timezone

time_records_bp = Blueprint('time_records', __name__)

@time_records_bp.route('/timerecords', methods=['GET'])
@jwt_required()
def get_time_records():
    current_user_id = get_jwt_identity()
    items = TimeRecord.query.filter_by(user_id=current_user_id).all()
    for item in items:
        print(item)
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


    timein = datetime.strptime(data['timein'], '%Y-%m-%dT%H:%M:%S.%fZ')
    timein.replace(tzinfo=timezone.utc)
    new_record = TimeRecord(
        user_id = current_user_id,
        domain_id = data['domain_id'],
        category_id = data['category_id'],
        title_id = data['title_id'],
        timein = timein
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
            timein = datetime.strptime(data['timein'], '%Y-%m-%dT%H:%M:%S.%fZ')
            timein.replace(tzinfo=timezone.utc)
            record.timein = timein
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid timein format."}), 400

    if 'timeout' in data and data['timeout']:
        try:
            print("TIMEOUT", data['timeout'])
            timeout = datetime.strptime(data['timeout'], '%Y-%m-%dT%H:%M:%S.%fZ')
            timeout.replace(tzinfo=timezone.utc)
            record.timeout = timeout
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid timeout format."}), 400
    else:
        record.timeout = None

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
