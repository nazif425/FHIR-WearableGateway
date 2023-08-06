from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    platform_user_id = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    patient_id = db.Column(db.String(100), nullable=True)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=False)
    expires_in = db.Column(db.String(10), nullable=False)
    scope = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'{self.id}: user - {self.platform_user_id}, platform - {self.platform}'

