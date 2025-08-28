from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.time_record import TimeRecord, RecordAttribute
from database import db
from datetime import datetime

time_records_bp = Blueprint('time_records', __name__)

@time_records_bp.route('/timerecords', methods=['GET'])
@jwt_required()
def get_time_records():
    current_user_id = get_jwt_identity()
    items = TimeRecord.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.to_dict() for item in items])


@time_records_bp.route('/recordattributes', methods=['GET'])
@jwt_required()
def get_record_attributes():
    current_user_id = get_jwt_identity()
    items = RecordAttribute.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.to_dict() for item in items])


@time_records_bp.route('/timerecords', methods=['POST'])
@jwt_required()
def create_time_record():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not all(key in data for key in ['domain_id', 'category_id', 'title_id']):
        return jsonify({"msg": "Missing required fields"}), 400

    new_record = TimeRecord(
        user_id = current_user_id,
        domain_id = data['domain_id'],
        category_id = data['category_id'],
        title_id = data['title_id']
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

    if 'domain_id' in data:
        record.domain_id = data['domain_id']
    if 'category_id' in data:
        record.category_id = data['category_id']
    if 'title_id' in data:
        record.title_id = data['title_id']

    if 'timeout' in data and data['timeout']:
        try:
            record.timeout = datetime.strptime(data['timeout'], '%Y-%m-%dT%H:%M:%S')
        except (ValueError, TypeError):
            return jsonify({"msg": "Invalid timeout format."}), 400
    else:
        record.timeout = None

    db.session.commit()

    return jsonify(record.to_dict()), 200
