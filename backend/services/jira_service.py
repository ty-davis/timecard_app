from atlassian import Jira
from typing import Dict, List, Optional
from datetime import datetime
from models.jira import JiraConnection
import logging

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with JIRA API"""
    
    def __init__(self, connection: JiraConnection):
        """Initialize JIRA client with connection details"""
        self.connection = connection
        decrypted_token = connection.get_decrypted_token()
        
        if not decrypted_token:
            raise ValueError("Failed to decrypt JIRA token")
        
        self.client = Jira(
            url=connection.jira_url,
            username=connection.email,
            password=decrypted_token,
            cloud=True  # Assuming Atlassian Cloud by default
        )
    
    def test_connection(self) -> Dict:
        """
        Test if the JIRA connection is valid
        Returns: Dict with 'success' boolean and optional 'error' message
        """
        try:
            # Try to get server info to verify connection
            server_info = self.client.get_server_info()
            return {
                'success': True,
                'server_info': {
                    'version': server_info.get('version'),
                    'deployment_type': server_info.get('deploymentType', 'cloud')
                }
            }
        except Exception as e:
            logger.error(f"JIRA connection test failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_issues(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Search for JIRA issues using JQL or text search
        
        Args:
            query: Search query (will be used in JQL)
            max_results: Maximum number of results to return
            
        Returns: List of issue dicts with key, summary, status, etc.
        """
        try:
            # Build JQL query - search in summary and key
            jql = f'text ~ "{query}" OR key ~ "{query}"'
            
            logger.info(f"Searching JIRA with JQL: {jql}")
            
            # Search with specific fields
            results = self.client.jql(
                jql,
                limit=max_results,
                fields='key,summary,status,assignee,issuetype,project'
            )
            
            logger.info(f"JIRA search returned {len(results.get('issues', []))} results")
            
            issues = []
            for issue_data in results.get('issues', []):
                fields = issue_data.get('fields', {})
                assignee = fields.get('assignee')
                status = fields.get('status')
                issuetype = fields.get('issuetype')
                project = fields.get('project')
                
                issues.append({
                    'key': issue_data.get('key'),
                    'summary': fields.get('summary', ''),
                    'status': status.get('name') if status else 'Unknown',
                    'assignee': assignee.get('displayName') if assignee else None,
                    'issueType': issuetype.get('name') if issuetype else 'Unknown',
                    'project': project.get('key') if project else 'Unknown'
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"JIRA issue search failed: {str(e)}", exc_info=True)
            raise
    
    def get_assigned_issues(self, email: str, max_results: int = 50) -> List[Dict]:
        """
        Get issues assigned to a specific user
        
        Args:
            email: User's email address
            max_results: Maximum number of results
            
        Returns: List of assigned issues
        """
        try:
            # JQL to find assigned issues
            jql = f'assignee = "{email}" AND resolution = Unresolved ORDER BY updated DESC'
            
            results = self.client.jql(
                jql,
                limit=max_results,
                fields='key,summary,status,assignee,issuetype,project'
            )
            
            issues = []
            for issue_data in results.get('issues', []):
                fields = issue_data.get('fields', {})
                assignee = fields.get('assignee')
                status = fields.get('status')
                issuetype = fields.get('issuetype')
                project = fields.get('project')
                
                issues.append({
                    'key': issue_data.get('key'),
                    'summary': fields.get('summary', ''),
                    'status': status.get('name') if status else 'Unknown',
                    'assignee': assignee.get('displayName') if assignee else None,
                    'issueType': issuetype.get('name') if issuetype else 'Unknown',
                    'project': project.get('key') if project else 'Unknown'
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"Failed to get assigned issues: {str(e)}")
            raise
    
    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """
        Get detailed information about a specific issue
        
        Args:
            issue_key: JIRA issue key (e.g., "PROJ-123")
            
        Returns: Issue details dict or None if not found
        """
        try:
            issue = self.client.issue(issue_key)
            fields = issue.get('fields', {})
            assignee = fields.get('assignee')
            status = fields.get('status')
            issuetype = fields.get('issuetype')
            project = fields.get('project')
            
            return {
                'key': issue.get('key'),
                'summary': fields.get('summary', ''),
                'description': fields.get('description', ''),
                'status': status.get('name') if status else 'Unknown',
                'assignee': assignee.get('displayName') if assignee else None,
                'issueType': issuetype.get('name') if issuetype else 'Unknown',
                'project': project.get('key') if project else 'Unknown',
                'created': fields.get('created'),
                'updated': fields.get('updated')
            }
            
        except Exception as e:
            logger.error(f"Failed to get issue {issue_key}: {str(e)}")
            return None
    
    def create_worklog(self, issue_key: str, time_spent_seconds: int, 
                      started: datetime, comment: str = None) -> Dict:
        """
        Create a worklog entry in JIRA
        
        Args:
            issue_key: JIRA issue key
            time_spent_seconds: Time spent in seconds
            started: When the work started (datetime)
            comment: Optional comment for the worklog
            
        Returns: Dict with 'success' boolean and 'worklog_id' or 'error'
        """
        try:
            # Convert datetime to JIRA format (ISO 8601)
            started_str = started.strftime('%Y-%m-%dT%H:%M:%S.000%z')
            if not started_str.endswith('+0000'):
                # If no timezone, assume UTC
                started_str = started.strftime('%Y-%m-%dT%H:%M:%S.000+0000')
            
            # Build worklog data
            worklog_data = {
                'timeSpentSeconds': time_spent_seconds,
                'started': started_str
            }
            
            if comment:
                worklog_data['comment'] = comment
            
            # Create worklog
            result = self.client.issue_add_worklog(issue_key, worklog_data)
            
            return {
                'success': True,
                'worklog_id': result.get('id')
            }
            
        except Exception as e:
            logger.error(f"Failed to create worklog for {issue_key}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_worklog(self, issue_key: str, worklog_id: str) -> Dict:
        """
        Delete a worklog entry from JIRA
        
        Args:
            issue_key: JIRA issue key
            worklog_id: Worklog ID to delete
            
        Returns: Dict with 'success' boolean and optional 'error'
        """
        try:
            self.client.issue_worklog_delete(issue_key, worklog_id)
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to delete worklog {worklog_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
