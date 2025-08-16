from database import db
from datetime import datetime, timezone

class TimeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    timein = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    timeout = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'category': self.category,
            'title': self.title,
            'timein': self.timein.isoformat(),
            'timeout': self.timeout.isoformat() if self.timeout else None,
        }

