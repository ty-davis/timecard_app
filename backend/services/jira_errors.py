"""
Error handling utilities for JIRA integration
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class JiraError(Exception):
    """Base exception for JIRA-related errors"""
    def __init__(self, message: str, error_type: str = 'general'):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class JiraConnectionError(JiraError):
    """Raised when JIRA connection fails"""
    def __init__(self, message: str):
        super().__init__(message, 'connection')


class JiraAuthenticationError(JiraError):
    """Raised when JIRA authentication fails"""
    def __init__(self, message: str):
        super().__init__(message, 'authentication')


class JiraPermissionError(JiraError):
    """Raised when user lacks permissions"""
    def __init__(self, message: str):
        super().__init__(message, 'permission')


class JiraValidationError(JiraError):
    """Raised when data validation fails"""
    def __init__(self, message: str):
        super().__init__(message, 'validation')


class JiraRateLimitError(JiraError):
    """Raised when JIRA API rate limit is hit"""
    def __init__(self, message: str):
        super().__init__(message, 'rate_limit')


def parse_jira_error(error: Exception) -> Dict:
    """
    Parse JIRA API errors into user-friendly messages
    """
    error_str = str(error).lower()
    
    # Authentication errors
    if 'unauthorized' in error_str or '401' in error_str:
        return {
            'type': 'authentication',
            'message': 'Invalid JIRA credentials. Please check your email and API token.',
            'user_message': 'Authentication failed. Your JIRA credentials may be incorrect or expired.'
        }
    
    # Permission errors
    if 'forbidden' in error_str or '403' in error_str:
        return {
            'type': 'permission',
            'message': 'Insufficient permissions to perform this action.',
            'user_message': 'You do not have permission to log time on this JIRA issue. Please check your JIRA project permissions.'
        }
    
    # Not found errors
    if 'not found' in error_str or '404' in error_str:
        return {
            'type': 'not_found',
            'message': 'JIRA issue or resource not found.',
            'user_message': 'The JIRA issue was not found. It may have been deleted or you may not have access to it.'
        }
    
    # Rate limit errors
    if 'rate limit' in error_str or '429' in error_str:
        return {
            'type': 'rate_limit',
            'message': 'JIRA API rate limit exceeded.',
            'user_message': 'Too many requests to JIRA. Please wait a few minutes and try again.'
        }
    
    # Network/connection errors
    if any(x in error_str for x in ['connection', 'timeout', 'network', 'unreachable']):
        return {
            'type': 'connection',
            'message': 'Failed to connect to JIRA.',
            'user_message': 'Could not connect to JIRA. Please check your internet connection and JIRA URL.'
        }
    
    # Validation errors
    if 'invalid' in error_str or 'required' in error_str:
        return {
            'type': 'validation',
            'message': 'Invalid data provided.',
            'user_message': 'The data provided is invalid. Please check all required fields.'
        }
    
    # Duplicate worklog detection
    if 'duplicate' in error_str or 'already exists' in error_str:
        return {
            'type': 'duplicate',
            'message': 'Worklog may already exist.',
            'user_message': 'This time entry may already be synced to JIRA.'
        }
    
    # Generic error
    return {
        'type': 'general',
        'message': str(error),
        'user_message': f'An error occurred: {str(error)[:200]}'
    }


def validate_time_record_for_sync(record) -> Optional[str]:
    """
    Validate that a time record has all required fields for JIRA sync
    Returns: Error message if validation fails, None if valid
    """
    if not record.jira_issue_key:
        return "Time record must have a JIRA issue linked"
    
    if not record.timein:
        return "Time record must have a start time"
    
    if not record.timeout:
        return "Time record must have an end time (clock out required)"
    
    # Check that timeout is after timein
    if record.timeout <= record.timein:
        return "End time must be after start time"
    
    # Calculate duration in seconds
    duration = (record.timeout - record.timein).total_seconds()
    
    # JIRA worklogs must be at least 1 minute
    if duration < 60:
        return "Time record must be at least 1 minute long"
    
    # Warn if duration is unusually long (more than 24 hours)
    if duration > 86400:
        logger.warning(f"Record {record.id} has duration over 24 hours: {duration}s")
    
    return None


def validate_jira_issue_key(issue_key: str) -> Optional[str]:
    """
    Validate JIRA issue key format (e.g., PROJ-123)
    Returns: Error message if invalid, None if valid
    """
    if not issue_key:
        return "Issue key cannot be empty"
    
    if '-' not in issue_key:
        return "Issue key must be in format: PROJECT-123"
    
    parts = issue_key.split('-')
    if len(parts) != 2:
        return "Issue key must be in format: PROJECT-123"
    
    project_key, issue_number = parts
    
    if not project_key.isupper():
        return "Project key must be uppercase"
    
    if not issue_number.isdigit():
        return "Issue number must be numeric"
    
    return None
