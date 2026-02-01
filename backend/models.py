import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Paste(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    version = db.Column(db.Integer, primary_key=True, default=1)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "content": [self.content],
            "created_at": self.created_at.isoformat(),
        }
