from database import db
from datetime import datetime, timezone

class RecordAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('record_attribute.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_num = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(8), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'user_id': self.user_id,
            'level_num': self.level_num,
            'color': self.color
        }

    def __str__(self):
        return f"{self.id}: {self.name} - {self.parent_id} | {self.user_id} | {self.level_num} | {self.color}"


class TimeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('record_attribute.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('record_attribute.id'), nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('record_attribute.id'), nullable=False)
    timein = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    timeout = db.Column(db.DateTime, nullable=True)
    external_link = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    domain = db.relationship('RecordAttribute', foreign_keys=[domain_id])
    category = db.relationship('RecordAttribute', foreign_keys=[category_id])
    title = db.relationship('RecordAttribute', foreign_keys=[title_id])

    def to_dict(self):
        return {
            'id': self.id,
            'domain_id': self.domain_id,
            'category_id': self.category_id,
            'title_id': self.title_id,
            'timein': self.timein.strftime('%Y-%m-%dT%H:%M:%SZ') if self.timein else None,
            'timeout': self.timeout.strftime('%Y-%m-%dT%H:%M:%SZ') if self.timeout else None,
            'external_link': self.external_link,
            'notes': self.notes,
        }

    def __str__(self):
        return f"{self.id}: {self.domain_id} {self.category_id} {self.title_id} || {self.timein} - {self.timeout}"

