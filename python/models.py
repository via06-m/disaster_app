# SQLAlchemy models and a single shared db instance.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    # User accounts with roles ('user' or 'admin').
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    role = db.Column(db.String(50), default="user", nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Password helpers for secure storage and checking.
    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class Article(db.Model):
    # Educational content (guides, tips, plans).
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))  # Emergency Kit Guide, Contingency Plan, Article
    content = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)


class CommunityReport(db.Model):
    # Disaster/hazard reports submitted by users.
    __tablename__ = "community_report"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    disaster_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="pending", nullable=False)  # pending, verified, resolved
    verified_by_admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to user/admin.
    user = db.relationship("User", foreign_keys=[user_id])
    verified_by_admin = db.relationship("User", foreign_keys=[verified_by_admin_id])


class Resource(db.Model):
    # Directory of emergency services/resources.
    __tablename__ = "resource"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))  # Hospital, Evacuation Center, Hotline, etc.
    address = db.Column(db.Text)
    contact = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(9, 6))
    longitude = db.Column(db.Numeric(9, 6))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmergencyPlan(db.Model):
    # For Personalizing emergency plans per user.
    __tablename__ = "emergency_plan"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    household_members = db.Column(db.Integer, default=1)
    meeting_point = db.Column(db.String(255))
    evacuation_routes = db.Column(db.Text)
    supply_checklist = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #  Relationship to user.
    user = db.relationship("User")


class SafetyCheck(db.Model):
    # Safety status entries ('Safe', 'Needs Help', 'Missing').
    __tablename__ = "safety_check"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Explanation: Relationship to user.
    user = db.relationship("User")
