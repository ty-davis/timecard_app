from database import db
from datetime import datetime, timezone
from cryptography.fernet import Fernet
import os

# Get encryption key from environment (will be set in config)
ENCRYPTION_KEY = os.getenv('JIRA_ENCRYPTION_KEY', Fernet.generate_key())
if isinstance(ENCRYPTION_KEY, str):
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
cipher = Fernet(ENCRYPTION_KEY)


class JiraConnection(db.Model):
    """Store user's JIRA connection credentials"""
    __tablename__ = 'jira_connection'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jira_url = db.Column(db.String(255), nullable=False)  # e.g., "https://company.atlassian.net"
    auth_type = db.Column(db.String(20), nullable=False, default='api_token')  # "api_token" or "oauth"
    email = db.Column(db.String(255), nullable=True)  # For API token auth
    api_token_encrypted = db.Column(db.Text, nullable=True)  # Encrypted API token
    oauth_access_token_encrypted = db.Column(db.Text, nullable=True)  # Encrypted OAuth token
    oauth_refresh_token_encrypted = db.Column(db.Text, nullable=True)  # Encrypted OAuth refresh token
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = db.relationship('User', backref='jira_connections')
    
    def set_api_token(self, token: str):
        """Encrypt and store API token"""
        if token:
            self.api_token_encrypted = cipher.encrypt(token.encode()).decode()
    
    def get_api_token(self) -> str | None:
        """Decrypt and return API token"""
        if self.api_token_encrypted:
            return cipher.decrypt(self.api_token_encrypted.encode()).decode()
        return None
    
    def set_encrypted_token(self, token: str):
        """Alias for set_api_token for backwards compatibility"""
        self.set_api_token(token)
    
    def get_decrypted_token(self) -> str | None:
        """Get the appropriate decrypted token based on auth_type"""
        if self.auth_type == 'api_token':
            return self.get_api_token()
        elif self.auth_type == 'oauth':
            access_token, _ = self.get_oauth_tokens()
            return access_token
        return None
    
    def set_oauth_tokens(self, access_token: str, refresh_token: str):
        """Encrypt and store OAuth tokens"""
        if access_token:
            self.oauth_access_token_encrypted = cipher.encrypt(access_token.encode()).decode()
        if refresh_token:
            self.oauth_refresh_token_encrypted = cipher.encrypt(refresh_token.encode()).decode()
    
    def get_oauth_tokens(self) -> tuple[str | None, str | None]:
        """Decrypt and return OAuth tokens"""
        access_token = None
        refresh_token = None
        if self.oauth_access_token_encrypted:
            access_token = cipher.decrypt(self.oauth_access_token_encrypted.encode()).decode()
        if self.oauth_refresh_token_encrypted:
            refresh_token = cipher.decrypt(self.oauth_refresh_token_encrypted.encode()).decode()
        return access_token, refresh_token
    
    def to_dict(self):
        """Return public representation (no tokens)"""
        return {
            'id': self.id,
            'jira_url': self.jira_url,
            'auth_type': self.auth_type,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<JiraConnection {self.id}: {self.jira_url} (user={self.user_id})>'


class JiraSyncLog(db.Model):
    """Track history of JIRA worklog syncs"""
    __tablename__ = 'jira_sync_log'
    
    id = db.Column(db.Integer, primary_key=True)
    time_record_id = db.Column(db.Integer, db.ForeignKey('time_record.id'), nullable=False)
    jira_issue_key = db.Column(db.String(50), nullable=False)  # e.g., "PROJ-123"
    jira_worklog_id = db.Column(db.String(50), nullable=True)  # JIRA's worklog ID
    sync_status = db.Column(db.String(20), nullable=False)  # "pending", "success", "failed"
    sync_error = db.Column(db.Text, nullable=True)  # Error message if failed
    synced_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    synced_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    time_record = db.relationship('TimeRecord', backref='sync_logs')
    synced_by = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'time_record_id': self.time_record_id,
            'jira_issue_key': self.jira_issue_key,
            'jira_worklog_id': self.jira_worklog_id,
            'sync_status': self.sync_status,
            'sync_error': self.sync_error,
            'synced_at': self.synced_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.synced_at else None,
            'synced_by_user_id': self.synced_by_user_id,
        }
    
    def __repr__(self):
        return f'<JiraSyncLog {self.id}: {self.jira_issue_key} - {self.sync_status}>'
