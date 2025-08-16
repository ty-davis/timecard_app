from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.time_record import TimeRecord

time_records_bp = Blueprint('time_records', __name__)

@time_records_bp.route('/timerecords', methods=['GET'])
@jwt_required()
def get_time_records():
    current_user_id = get_jwt_identity()
    items = TimeRecord.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.to_dict() for item in items])
