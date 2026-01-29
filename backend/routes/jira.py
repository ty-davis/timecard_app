from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.jira import JiraConnection, JiraSyncLog
from models.time_record import TimeRecord
from services.jira_service import JiraService
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

jira_bp = Blueprint('jira', __name__)


# ============================================================================
# Connection Management Routes
# ============================================================================

@jira_bp.route('/jira/connections', methods=['POST'])
@jwt_required()
def create_connection():
    """Create a new JIRA connection for the current user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['jira_url', 'email', 'api_token']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already has a connection (for now, only allow one)
        existing = JiraConnection.query.filter_by(user_id=user_id).first()
        if existing:
            return jsonify({'error': 'You already have a JIRA connection. Please update or delete it first.'}), 400
        
        # Create new connection
        connection = JiraConnection(
            user_id=user_id,
            jira_url=data['jira_url'].rstrip('/'),  # Remove trailing slash
            email=data['email'],
            auth_type='api_token',
            is_active=True
        )
        
        # Set encrypted token
        connection.set_encrypted_token(data['api_token'])
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'message': 'JIRA connection created successfully',
            'connection': connection.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating JIRA connection: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/connections', methods=['GET'])
@jwt_required()
def get_connections():
    """Get all JIRA connections for the current user"""
    try:
        user_id = get_jwt_identity()
        connections = JiraConnection.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'connections': [conn.to_dict() for conn in connections]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching JIRA connections: {str(e)}")
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/connections/<int:connection_id>', methods=['PUT'])
@jwt_required()
def update_connection(connection_id):
    """Update a JIRA connection"""
    try:
        user_id = get_jwt_identity()
        connection = JiraConnection.query.filter_by(
            id=connection_id,
            user_id=user_id
        ).first()
        
        if not connection:
            return jsonify({'error': 'Connection not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'jira_url' in data:
            connection.jira_url = data['jira_url'].rstrip('/')
        if 'email' in data:
            connection.email = data['email']
        if 'api_token' in data:
            connection.set_encrypted_token(data['api_token'])
        if 'is_active' in data:
            connection.is_active = data['is_active']
        
        connection.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'message': 'Connection updated successfully',
            'connection': connection.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating JIRA connection: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/connections/<int:connection_id>', methods=['DELETE'])
@jwt_required()
def delete_connection(connection_id):
    """Delete a JIRA connection"""
    try:
        user_id = get_jwt_identity()
        connection = JiraConnection.query.filter_by(
            id=connection_id,
            user_id=user_id
        ).first()
        
        if not connection:
            return jsonify({'error': 'Connection not found'}), 404
        
        db.session.delete(connection)
        db.session.commit()
        
        return jsonify({'message': 'Connection deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting JIRA connection: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/connections/<int:connection_id>/test', methods=['POST'])
@jwt_required()
def test_connection(connection_id):
    """Test a JIRA connection"""
    try:
        user_id = get_jwt_identity()
        connection = JiraConnection.query.filter_by(
            id=connection_id,
            user_id=user_id
        ).first()
        
        if not connection:
            return jsonify({'error': 'Connection not found'}), 404
        
        # Create JIRA service and test connection
        jira_service = JiraService(connection)
        result = jira_service.test_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Connection successful',
                'server_info': result.get('server_info')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error')
            }), 400
        
    except Exception as e:
        logger.error(f"Error testing JIRA connection: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Issue Operations Routes
# ============================================================================

@jira_bp.route('/jira/issues/search', methods=['GET'])
@jwt_required()
def search_issues():
    """Search for JIRA issues"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        # Get user's active connection
        connection = JiraConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'No active JIRA connection found'}), 404
        
        # Search issues
        jira_service = JiraService(connection)
        issues = jira_service.search_issues(query)
        
        return jsonify({'issues': issues}), 200
        
    except Exception as e:
        logger.error(f"Error searching JIRA issues: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/issues/<issue_key>', methods=['GET'])
@jwt_required()
def get_issue(issue_key):
    """Get details of a specific JIRA issue"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's active connection
        connection = JiraConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'No active JIRA connection found'}), 404
        
        # Get issue
        jira_service = JiraService(connection)
        issue = jira_service.get_issue(issue_key)
        
        if issue:
            return jsonify({'issue': issue}), 200
        else:
            return jsonify({'error': 'Issue not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting JIRA issue: {str(e)}")
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/issues/assigned', methods=['GET'])
@jwt_required()
def get_assigned_issues():
    """Get issues assigned to the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's active connection
        connection = JiraConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'No active JIRA connection found'}), 404
        
        # Get assigned issues
        jira_service = JiraService(connection)
        issues = jira_service.get_assigned_issues(connection.email)
        
        return jsonify({'issues': issues}), 200
        
    except Exception as e:
        logger.error(f"Error getting assigned JIRA issues: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Sync Operations Routes
# ============================================================================

@jira_bp.route('/jira/sync/record/<int:record_id>', methods=['POST'])
@jwt_required()
def sync_record(record_id):
    """Sync a single time record to JIRA"""
    try:
        user_id = get_jwt_identity()
        
        # Get the time record and verify ownership
        record = TimeRecord.query.filter_by(
            id=record_id,
            user_id=user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Time record not found'}), 404
        
        # Validate record has required fields
        if not record.jira_issue_key:
            return jsonify({'error': 'Time record does not have a JIRA issue key'}), 400
        
        if not record.timein or not record.timeout:
            return jsonify({'error': 'Time record must have both timein and timeout'}), 400
        
        # Get user's active connection
        connection = JiraConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'No active JIRA connection found'}), 404
        
        # Calculate time spent in seconds
        time_diff = record.timeout - record.timein
        time_spent_seconds = int(time_diff.total_seconds())
        
        # Prepare comment (use notes or default message)
        comment = record.notes if record.notes else "Time logged from Timecard App"
        
        # Create worklog in JIRA
        jira_service = JiraService(connection)
        result = jira_service.create_worklog(
            issue_key=record.jira_issue_key,
            time_spent_seconds=time_spent_seconds,
            started=record.timein,
            comment=comment
        )
        
        # Create sync log entry
        sync_log = JiraSyncLog(
            time_record_id=record.id,
            jira_issue_key=record.jira_issue_key,
            synced_by_user_id=user_id,
            synced_at=datetime.now(timezone.utc)
        )
        
        if result['success']:
            # Update time record
            record.jira_synced = True
            record.jira_worklog_id = result['worklog_id']
            record.jira_sync_error = None
            record.last_synced_at = datetime.now(timezone.utc)
            
            # Update sync log
            sync_log.jira_worklog_id = result['worklog_id']
            sync_log.sync_status = 'success'
            
            db.session.add(sync_log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Time record synced to JIRA successfully',
                'worklog_id': result['worklog_id']
            }), 200
        else:
            # Update time record with error
            record.jira_synced = False
            record.jira_sync_error = result['error']
            record.last_synced_at = datetime.now(timezone.utc)
            
            # Update sync log
            sync_log.sync_status = 'failed'
            sync_log.sync_error = result['error']
            
            db.session.add(sync_log)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Error syncing time record to JIRA: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@jira_bp.route('/jira/sync/bulk', methods=['POST'])
@jwt_required()
def bulk_sync():
    """Sync multiple time records to JIRA"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'record_ids' not in data or not isinstance(data['record_ids'], list):
            return jsonify({'error': 'record_ids array is required'}), 400
        
        record_ids = data['record_ids']
        
        # Get user's active connection
        connection = JiraConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'No active JIRA connection found'}), 404
        
        jira_service = JiraService(connection)
        
        results = {
            'total': len(record_ids),
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }
        
        for record_id in record_ids:
            # Get the time record and verify ownership
            record = TimeRecord.query.filter_by(
                id=record_id,
                user_id=user_id
            ).first()
            
            if not record:
                results['failed'] += 1
                results['errors'].append({
                    'record_id': record_id,
                    'error': 'Record not found'
                })
                continue
            
            # Validate record
            if not record.jira_issue_key:
                results['failed'] += 1
                results['errors'].append({
                    'record_id': record_id,
                    'error': 'No JIRA issue key'
                })
                continue
            
            if not record.timein or not record.timeout:
                results['failed'] += 1
                results['errors'].append({
                    'record_id': record_id,
                    'error': 'Missing timein or timeout'
                })
                continue
            
            # Calculate time spent
            time_diff = record.timeout - record.timein
            time_spent_seconds = int(time_diff.total_seconds())
            
            # Prepare comment
            comment = record.notes if record.notes else "Time logged from Timecard App"
            
            # Sync to JIRA
            result = jira_service.create_worklog(
                issue_key=record.jira_issue_key,
                time_spent_seconds=time_spent_seconds,
                started=record.timein,
                comment=comment
            )
            
            # Create sync log
            sync_log = JiraSyncLog(
                time_record_id=record.id,
                jira_issue_key=record.jira_issue_key,
                synced_by_user_id=user_id,
                synced_at=datetime.now(timezone.utc)
            )
            
            if result['success']:
                results['succeeded'] += 1
                
                # Update record
                record.jira_synced = True
                record.jira_worklog_id = result['worklog_id']
                record.jira_sync_error = None
                record.last_synced_at = datetime.now(timezone.utc)
                
                # Update sync log
                sync_log.jira_worklog_id = result['worklog_id']
                sync_log.sync_status = 'success'
            else:
                results['failed'] += 1
                results['errors'].append({
                    'record_id': record_id,
                    'error': result['error']
                })
                
                # Update record
                record.jira_synced = False
                record.jira_sync_error = result['error']
                record.last_synced_at = datetime.now(timezone.utc)
                
                # Update sync log
                sync_log.sync_status = 'failed'
                sync_log.sync_error = result['error']
            
            db.session.add(sync_log)
        
        db.session.commit()
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error in bulk sync: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/sync/history', methods=['GET'])
@jwt_required()
def get_sync_history():
    """Get sync history for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters for filtering
        status = request.args.get('status')  # 'success', 'failed', or None for all
        limit = request.args.get('limit', 100, type=int)
        
        # Build query - join with time_records to ensure user ownership
        query = db.session.query(JiraSyncLog).join(
            TimeRecord,
            JiraSyncLog.time_record_id == TimeRecord.id
        ).filter(
            TimeRecord.user_id == user_id
        )
        
        # Apply status filter if provided
        if status:
            query = query.filter(JiraSyncLog.sync_status == status)
        
        # Order by most recent first and limit
        sync_logs = query.order_by(
            JiraSyncLog.synced_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'history': [log.to_dict() for log in sync_logs]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching sync history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@jira_bp.route('/jira/worklog/<int:time_record_id>', methods=['DELETE'])
@jwt_required()
def delete_worklog(time_record_id):
    """Delete a worklog from JIRA and clear sync status"""
    try:
        user_id = get_jwt_identity()
        
        # Get the time record and verify ownership
        record = TimeRecord.query.filter_by(
            id=time_record_id,
            user_id=user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Time record not found'}), 404
        
        if not record.jira_worklog_id or not record.jira_issue_key:
            return jsonify({'error': 'Time record is not synced to JIRA'}), 400
        
        # Get user's active connection
        connection = JiraConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'No active JIRA connection found'}), 404
        
        # Delete worklog from JIRA
        jira_service = JiraService(connection)
        result = jira_service.delete_worklog(
            issue_key=record.jira_issue_key,
            worklog_id=record.jira_worklog_id
        )
        
        if result['success']:
            # Clear sync status from record
            record.jira_synced = False
            record.jira_worklog_id = None
            record.jira_sync_error = None
            record.last_synced_at = None
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Worklog deleted from JIRA'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Error deleting worklog: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
