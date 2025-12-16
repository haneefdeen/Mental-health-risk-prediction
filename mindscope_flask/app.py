"""
MindScope AI - Flask Application
Full-stack CPU-friendly multimodal emotion analysis with user/admin modes.
"""

from __future__ import annotations

import base64
import json
import logging
import statistics
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from flask import Flask, jsonify, render_template, request, send_file, current_app
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from jose import JWTError, jwt
from werkzeug.security import check_password_hash, generate_password_hash

from backend.model.behavioral_analyzer import BehavioralAnalyzer
from backend.model.fusion_model import FusionModel
from backend.model.image_analyzer import ImageAnalyzer
from backend.model.text_analyzer import TextAnalyzer
from backend.model.explainability import (
    ExplainabilityEngine,
    get_text_importance_tokens,
    generate_gradcam_for_image,
)
from backend.utils.report_generator import ReportGenerator
from backend.config.labels import (
    PRIMARY_EMOJI,
    STRESS_DISPLAY,
    FER_TO_PLATFORM_EMOTION
)
from backend.services.risk_utils import (
    stress_label_to_risk_score,
    stress_score_to_label,
    stress_category_to_risk_score
)
from backend.services.advice import generate_coping_suggestions, generate_wellness_tip
from backend.services.stress_mapping import (
    map_emotion_to_stress,
    combine_stress,
    stress_category_to_internal_label
)

# ---------------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR = BASE_DIR / "uploads" / "analysis"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = "mindscope-ai-secret-key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'mindscope_ai_flask.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRY_MINUTES = 90
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
    JSON_SORT_KEYS = False


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
report_generator = ReportGenerator()


def _run_migrations() -> None:
    """Run database migrations to add new columns/tables"""
    import sqlite3
    try:
        db_path = INSTANCE_DIR / "mindscope_ai_flask.db"
        if not db_path.exists():
            return  # Will be created by db.create_all()
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check and add User table columns
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'high_risk_flag' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN high_risk_flag BOOLEAN DEFAULT 0")
        if 'high_risk_reason' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN high_risk_reason VARCHAR(500)")
        if 'high_risk_updated_at' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN high_risk_updated_at DATETIME")
        
        # Check if Resource table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE resource (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    type VARCHAR(50) NOT NULL,
                    url_or_path VARCHAR(500) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Check if AdminAuditLog table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_audit_log'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE admin_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES user (id)
                )
            """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Migration check failed (may be normal on first run): {e}")


def create_app(config: Optional[Config] = None) -> Flask:
    """Application factory."""

    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "assets"),
        template_folder=str(BASE_DIR / "templates"),
    )
    app.config.from_object(config or Config())

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    with app.app_context():
        # Run migrations for new columns/tables
        _run_migrations()
        db.create_all()
        seed_default_accounts()

    register_routes(app)
    return app


# ---------------------------------------------------------------------------
# Database models
# ---------------------------------------------------------------------------


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), default="")
    role = db.Column(db.String(20), default="user")  # user or admin
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)
    behavioral_profile = db.Column(db.JSON, default=dict)
    emoji_fingerprint = db.Column(db.JSON, default=dict)
    total_sessions = db.Column(db.Integer, default=0)
    stress_alerts = db.Column(db.Integer, default=0)
    # High-risk user flagging
    high_risk_flag = db.Column(db.Boolean, default=False)
    high_risk_reason = db.Column(db.String(500), nullable=True)
    high_risk_updated_at = db.Column(db.DateTime, nullable=True)

    analyses = db.relationship(
        "AnalysisRecord", backref="user", lazy=True, cascade="all, delete-orphan"
        )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat()
            if self.last_login_at
            else None,
            "total_sessions": self.total_sessions,
            "stress_alerts": self.stress_alerts,
            "behavioral_profile": self.behavioral_profile or {},
            "high_risk_flag": self.high_risk_flag,
            "high_risk_reason": self.high_risk_reason,
            "high_risk_updated_at": self.high_risk_updated_at.isoformat() if self.high_risk_updated_at else None,
        }


class AnalysisRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    mode = db.Column(db.String(32), default="text")  # text, image, fusion, webcam
    emotion = db.Column(db.String(32))
    emotion_emoji = db.Column(db.String(8))
    stress_level = db.Column(db.String(16))
    stress_score = db.Column(db.Float, default=0.5)
    risk_level = db.Column(db.String(16))
    confidence = db.Column(db.Float, default=0.0)
    ai_tip = db.Column(db.Text)
    suggestions = db.Column(db.JSON, default=list)
    # Use a different Python attribute name to avoid clashing with SQLAlchemy's Base.metadata
    meta = db.Column("metadata", db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mode": self.mode,
            "emotion": self.emotion,
            "emoji": self.emotion_emoji,
            "stress_level": self.stress_level,
            "stress_score": self.stress_score,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "ai_tip": self.ai_tip,
            "suggestions": self.suggestions,
            # Keep API field name as 'metadata' for compatibility
            "metadata": self.meta,
            "created_at": self.created_at.isoformat(),
            "is_high_risk": self.stress_level in {"high", "critical", "severe_stress", "moderate_stress"},
        }


class Message(db.Model):
    """Admin-to-user messaging system"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # NULL for broadcast
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_broadcast = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")


class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    admin_username = db.Column(db.String(64))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    severity = db.Column(db.String(16), default="high")
    stress_count = db.Column(db.Integer, default=0)
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Resource(db.Model):
    """Wellness resources (PDFs, articles, videos)"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)  # "pdf", "article", "video", "link"
    url_or_path = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminAuditLog(db.Model):
    """Audit log for admin actions"""
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # e.g., "SEND_BROADCAST", "TRAIN_MODEL"
    details = db.Column(db.Text, nullable=True)  # JSON string or text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship("User", foreign_keys=[admin_id])


# ---------------------------------------------------------------------------
# ML analyzers (global singletons – CPU friendly)
# ---------------------------------------------------------------------------

text_analyzer = TextAnalyzer()
image_analyzer = ImageAnalyzer()
behavioral_analyzer = BehavioralAnalyzer()
fusion_model = FusionModel()
explain_engine = ExplainabilityEngine()

EMOJI_MAP = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😡",
    "stressed": "😰",
    "calm": "😌",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def seed_default_accounts() -> None:
    """Create default admin/user accounts if missing."""
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@mindscope.ai",
            full_name="MindScope Admin",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

    if not User.query.filter_by(username="user1").first():
        user = User(
            username="user1",
            email="user@mindscope.ai",
            full_name="MindScope Demo User",
            role="user",
        )
        user.set_password("user123")
        db.session.add(user)

    db.session.commit()


def generate_token(user: User) -> str:
    expiry_minutes = current_app.config.get("TOKEN_EXPIRY_MINUTES", 90)
    payload = {
        "sub": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(minutes=expiry_minutes),
    }
    secret = current_app.config.get("SECRET_KEY", Config.SECRET_KEY)
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    secret = current_app.config.get("SECRET_KEY", Config.SECRET_KEY)
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        return None


def get_user_from_request() -> Optional[User]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None
    return User.query.filter_by(username=payload["sub"]).first()


def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_request()
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


def categorize_stress(score: float) -> str:
    """Map stress score to standard stress categories"""
    stress_label = stress_score_to_label(score)
    return STRESS_DISPLAY.get(stress_label, "Moderate Stress")


def categorize_risk(stress_level: str, confidence: float) -> str:
    """Map stress level to standard risk labels"""
    mapping = {
        "No Apparent Stress": "No Stress",
        "Low Stress": "Low Stress",
        "Moderate Stress": "Moderate Stress",
        "High Stress": "High Stress",
        "Severe Stress": "Severe Stress",
        # Legacy mappings for backward compatibility
        "no_stress": "No Stress",
        "mild_stress": "Low Stress",
        "moderate_stress": "Moderate Stress",
        "severe_stress": "Severe Stress",
        "low": "Low Stress",
        "moderate": "Moderate Stress",
        "high": "High Stress",
        "critical": "Severe Stress",
    }
    return mapping.get(stress_level, "Moderate Stress")


def get_risk_level_from_score(risk_score: float) -> str:
    """Map risk score (0-100) to risk level"""
    if risk_score <= 30:
        return "Low Risk"
    if risk_score <= 60:
        return "Moderate Risk"
    if risk_score <= 85:
        return "High Risk"
    return "Critical Risk"


def get_emotion_emoji(emotion: str) -> str:
    """Get emoji for emotion label"""
    return PRIMARY_EMOJI.get(emotion.lower(), "😐")


def get_emotion_description(emotion: str) -> str:
    """Get description for emotion"""
    descriptions = {
        "happy": "Your emotional tone appears positive and calm.",
        "sad": "Your emotional tone appears low and withdrawn.",
        "anxious": "Your emotional tone shows signs of worry and tension.",
        "fearful": "Your emotional tone indicates fear or apprehension.",
        "neutral": "Your emotional tone appears balanced and neutral.",
        "surprised": "Your emotional tone shows surprise or unexpected feelings.",
        "disgusted": "Your emotional tone indicates aversion or disgust.",
        "angry": "Your emotional tone shows frustration or irritation.",
        "stressed": "Your emotional tone indicates stress and pressure.",
        "calm": "Your emotional tone appears peaceful and relaxed.",
    }
    return descriptions.get(emotion.lower(), "Your emotional tone has been analyzed.")


def get_stress_category_description(stress_category: str) -> str:
    """Get description for stress category"""
    descriptions = {
        "No Apparent Stress": "Minimal indicators of emotional strain detected.",
        "Low Stress": "Some mild indicators of stress are present.",
        "Moderate Stress": "Some indicators of emotional strain are present.",
        "High Stress": "Multiple indicators of significant stress detected.",
        "Severe Stress": "Severe indicators of stress require attention.",
    }
    return descriptions.get(stress_category, "Stress level has been assessed.")


def generate_key_indicators(stress_score: float, emotion: str, text_result: Optional[Dict] = None, image_result: Optional[Dict] = None) -> Dict[str, str]:
    """Generate key indicators based on actual analysis results"""
    emotion_lower = emotion.lower()
    
    # Determine mood tone based on emotion and stress
    if emotion_lower in ["happy", "joy", "excited", "calm", "peaceful"]:
        if stress_score < 0.3:
            mood_tone = "Positive"
        elif stress_score < 0.5:
            mood_tone = "Mostly Positive"
        else:
            mood_tone = "Mixed"
    elif emotion_lower in ["sad", "sadness", "depressed", "lonely"]:
        mood_tone = "Negative"
    elif emotion_lower in ["anxious", "fearful", "stressed", "worried"]:
        mood_tone = "Anxious"
    elif emotion_lower in ["angry", "anger", "frustrated"]:
        mood_tone = "Irritable"
    elif emotion_lower in ["neutral", "calm"]:
        mood_tone = "Stable"
    else:
        mood_tone = "Neutral" if stress_score < 0.5 else "Negative"
    
    # Cognitive clues based on text analysis
    cognitive_clues = "Neutral language patterns"
    if text_result:
        has_stress = text_result.get("has_stress_keywords", False)
        has_positive = text_result.get("has_positive_keywords", False)
        dominant_emotion = text_result.get("dominant_emotion", "")
        
        if has_positive and not has_stress:
            cognitive_clues = "Positive language and optimistic expressions"
        elif has_stress and stress_score > 0.6:
            cognitive_clues = "Stress-related keywords and negative patterns"
        elif has_stress:
            cognitive_clues = "Some stress-related keywords detected"
        elif dominant_emotion in ["joy", "surprise"]:
            cognitive_clues = "Positive emotional expressions"
        elif dominant_emotion in ["sadness", "fear", "anger"]:
            cognitive_clues = "Negative emotional indicators"
    elif image_result:
        img_emotion = image_result.get("dominant_emotion", "")
        if img_emotion in ["happy", "surprised"]:
            cognitive_clues = "Positive facial expressions"
        elif img_emotion in ["sad", "fearful", "angry"]:
            cognitive_clues = "Negative facial expressions detected"
    
    # Social cues based on stress and emotion
    if stress_score < 0.3:
        social_cues = "Connected & active engagement"
    elif stress_score < 0.5:
        if emotion_lower in ["happy", "calm"]:
            social_cues = "Normal engagement patterns"
        else:
            social_cues = "Moderate engagement, some withdrawal possible"
    elif stress_score < 0.75:
        social_cues = "Possible withdrawal or reduced engagement"
    else:
        social_cues = "Avoidant / withdrawn patterns"
    
    return {
        "mood_tone": mood_tone,
        "cognitive_clues": cognitive_clues,
        "social_cues": social_cues
    }


def generate_text_explanation(text: str, text_result: Dict) -> Dict[str, Any]:
    """Generate text explainability data"""
    keywords = []
    if text_result.get("has_stress_keywords"):
        # Extract stress keywords from text
        stress_keywords = ["stressed", "anxious", "worried", "overwhelmed", "panic", "nervous", "tired", "exhausted", "depressed", "hopeless", "lonely"]
        text_lower = text.lower()
        for kw in stress_keywords:
            if kw in text_lower:
                keywords.append(kw)
    
    if text_result.get("has_positive_keywords"):
        positive_keywords = ["happy", "grateful", "excited", "good", "confident", "proud"]
        text_lower = text.lower()
        for kw in positive_keywords:
            if kw in text_lower:
                keywords.append(kw)
    
    # Determine tone
    stress_score = text_result.get("stress_level", 0.5)
    if stress_score < 0.3:
        tone = "Positive / optimistic"
    elif stress_score < 0.6:
        tone = "Neutral / reflective"
    else:
        tone = "Negative / reflective"
    
    summary = f"The text contains {'negative' if stress_score > 0.5 else 'neutral to positive'} emotional words indicating {text_result.get('primary_emotion', 'neutral')} and {'mental fatigue' if stress_score > 0.6 else 'emotional balance'}."
    
    return {
        "summary": summary,
        "keywords": keywords[:5],  # Limit to 5 keywords
        "tone": tone
    }


def generate_image_explanation(image_result: Dict) -> Dict[str, Any]:
    """Generate image explainability data"""
    dominant_emotion = image_result.get("dominant_emotion", "neutral")
    stress_score = image_result.get("stress_level", 0.5)
    
    emotion_descriptions = {
        "happy": "Facial expression suggests happiness with upturned mouth and bright eyes.",
        "sad": "Facial expression suggests sadness with lowered gaze and lack of smile.",
        "angry": "Facial expression shows anger with furrowed brows and tense features.",
        "fearful": "Facial expression indicates fear with wide eyes and raised eyebrows.",
        "surprised": "Facial expression shows surprise with raised eyebrows and open mouth.",
        "disgusted": "Facial expression suggests disgust with wrinkled nose.",
        "neutral": "Facial expression appears neutral with relaxed features.",
    }
    
    summary = emotion_descriptions.get(dominant_emotion, f"Facial expression detected: {dominant_emotion}.")
    
    if stress_score > 0.6:
        summary += " Eye and mouth regions contributed the most to stress detection."
    
    return {
        "summary": summary,
        "emotion_from_face": dominant_emotion.capitalize(),
        "cam_hint": "Eye and mouth regions contributed the most." if stress_score > 0.5 else "Facial features analyzed across all regions."
    }


def wellness_tip(emotion: str, stress_level: str) -> str:
    """Generate emotion-specific wellness tips"""
    emotion_lower = emotion.lower()
    
    tips = {
        "happy": "Keep sharing gratitude and take a mindful break to lock-in the good vibes.",
        "joy": "Keep sharing gratitude and take a mindful break to lock-in the good vibes.",
        "excited": "Channel your energy into a creative project or physical activity.",
        "sad": "Reach out to a friend or write down three things you appreciate today.",
        "sadness": "Reach out to a friend or write down three things you appreciate today.",
        "depressed": "Consider talking to someone you trust or engaging in a gentle activity you enjoy.",
        "angry": "Step away for a short walk and practice box breathing (inhale-4, hold-4, exhale-4).",
        "anger": "Step away for a short walk and practice box breathing (inhale-4, hold-4, exhale-4).",
        "frustrated": "Take a break and try a different approach or perspective.",
        "stressed": "Try a five-minute body scan meditation and limit screen time for an hour.",
        "anxious": "Practice grounding techniques: name 5 things you see, 4 you hear, 3 you feel.",
        "fearful": "Focus on what you can control right now and take one small step forward.",
        "worried": "Write down your concerns and identify which ones you can address today.",
        "calm": "Maintain your calm by stretching and planning a micro-goal you can celebrate.",
        "neutral": "Take a moment to check in with yourself and acknowledge how you're feeling.",
        "surprised": "Embrace the unexpected and see it as an opportunity for growth.",
    }
    
    base = tips.get(emotion_lower, "Take a deep breath and give yourself credit for checking in.")
    
    # Add stress-level specific advice
    stress_lower = stress_level.lower() if isinstance(stress_level, str) else ""
    if stress_lower in {"high stress", "severe stress", "critical", "severe_stress", "high"}:
        base += " Consider talking with a trusted professional if symptoms persist."
    elif stress_lower in {"moderate stress", "moderate_stress", "moderate"}:
        base += " Regular self-care practices can help manage stress levels."
    
    return base


def update_behavioral_profile(user: User, record: AnalysisRecord, text: str = "") -> None:
    profile = user.behavioral_profile or {}
    emoji_fp = user.emoji_fingerprint or {}

    profile.setdefault("history", []).append(
        {
            "emotion": record.emotion,
            "stress": record.stress_level,
            "timestamp": record.created_at.isoformat(),
        }
    )
    profile["history"] = profile["history"][-50:]  # cap history

    emoji_fp.setdefault(record.emotion, 0)
    emoji_fp[record.emotion] += 1

    profile["average_confidence"] = float(
        statistics.fmean([r.confidence for r in user.analyses[-10:]])
    ) if user.analyses else record.confidence

    profile["last_tip"] = record.ai_tip
    profile["updated_at"] = datetime.utcnow().isoformat()

    user.behavioral_profile = profile
    user.emoji_fingerprint = emoji_fp


def record_high_stress_alert(user: User, record: AnalysisRecord) -> None:
    user.stress_alerts += 1
    alert = AdminAlert.query.filter_by(user_id=user.id, resolved=False).first()
    if not alert:
        alert = AdminAlert(user_id=user.id, stress_count=1)
        db.session.add(alert)
    else:
        alert.stress_count += 1
        alert.updated_at = datetime.utcnow()

    if alert.stress_count >= 3:
        alert.severity = "critical"


def serialize_admin_alert(alert: AdminAlert) -> Dict[str, Any]:
    return {
        "id": alert.id,
        "user_id": alert.user_id,
        "severity": alert.severity,
        "stress_count": alert.stress_count,
        "resolved": alert.resolved,
        "created_at": alert.created_at.isoformat(),
        "updated_at": alert.updated_at.isoformat(),
    }


def log_admin_action(admin_id: int, action: str, details: Optional[str] = None) -> None:
    """Log admin action to audit log"""
    try:
        audit_log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            details=details
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
        db.session.rollback()


def check_and_flag_high_risk_user(user: User) -> None:
    """Auto-flag users with repeated high stress or negative emotions"""
    try:
        # Get last 10 analyses for this user
        recent_analyses = AnalysisRecord.query.filter_by(user_id=user.id)\
            .order_by(AnalysisRecord.created_at.desc())\
            .limit(10)\
            .all()
        
        if len(recent_analyses) < 5:  # Need at least 5 analyses
            return
        
        # Count high stress and negative emotions
        high_stress_count = 0
        negative_emotion_count = 0
        negative_emotions = ["sad", "anxious", "fearful", "angry", "depressed"]
        
        for analysis in recent_analyses[:5]:  # Check last 5
            # Check stress level
            stress_level = analysis.stress_level or ""
            if stress_level.lower() in ["high stress", "high", "severe stress", "severe"]:
                high_stress_count += 1
            
            # Check emotion
            emotion = (analysis.emotion or "").lower()
            if emotion in negative_emotions:
                negative_emotion_count += 1
        
        # Flag if at least 3 out of 5 have high stress OR negative emotions
        if high_stress_count >= 3 or negative_emotion_count >= 3:
            user.high_risk_flag = True
            if high_stress_count >= 3:
                user.high_risk_reason = f"Repeated high stress predictions in last {len(recent_analyses[:5])} analyses ({high_stress_count} high stress)."
            else:
                user.high_risk_reason = f"Repeated negative emotions in last {len(recent_analyses[:5])} analyses ({negative_emotion_count} negative emotions)."
            user.high_risk_updated_at = datetime.utcnow()
            db.session.commit()
        elif user.high_risk_flag and (high_stress_count < 2 and negative_emotion_count < 2):
            # Clear flag if conditions no longer met
            user.high_risk_flag = False
            user.high_risk_reason = None
            user.high_risk_updated_at = datetime.utcnow()
            db.session.commit()
    except Exception as e:
        logger.error(f"Error checking high-risk user: {e}")
        db.session.rollback()


# ---------------------------------------------------------------------------
# Core analysis routines
# ---------------------------------------------------------------------------


def run_text_analysis(user: User, payload: Dict[str, Any]) -> AnalysisRecord:
    text = payload.get("text", "")
    if not text.strip():
        raise ValueError("Text input is required.")

    # Use pre-analyzed result if provided, otherwise analyze
    raw_result = payload.get("text_result") or text_analyzer.analyze(text)
    primary_emotion = raw_result.get("primary_emotion", "calm")
    stress_score = raw_result.get("stress_level", 0.5)
    stress_level = categorize_stress(stress_score)
    confidence = raw_result.get("confidence", 0.0)
    risk_level = categorize_risk(stress_level, confidence)
    # Use emotion-aware coping suggestions
    tips = fusion_model.get_coping_suggestions({
        "stress_level": stress_score,
        "emotion": primary_emotion,
        "primary_emotion": primary_emotion
    })

    record = AnalysisRecord(
        user_id=user.id,
        mode="text",
        emotion=primary_emotion,
        emotion_emoji=EMOJI_MAP.get(primary_emotion, "🙂"),
        stress_level=stress_level,
        stress_score=stress_score,
        confidence=confidence,
        risk_level=risk_level,
        suggestions=tips,
        ai_tip=wellness_tip(primary_emotion, stress_level),
        meta={
            "raw_emotions": raw_result.get("emotions"),
            "dominant_emotion": raw_result.get("dominant_emotion"),
            "word_count": raw_result.get("word_count"),
            "dataset_stress_probability": raw_result.get("dataset_stress_probability"),
        },
    )
    db.session.add(record)
    db.session.flush()

    update_behavioral_profile(user, record, text=text)
    user.total_sessions += 1
    user.last_login_at = datetime.utcnow()

    if stress_level in {"high", "critical", "severe_stress"}:
        record_high_stress_alert(user, record)
    
    # Auto-flag high-risk users
    check_and_flag_high_risk_user(user)

    db.session.commit()
    return record


def run_image_analysis(user: User, payload: Dict[str, Any]) -> AnalysisRecord:
    image_data = payload.get("image_data")
    if not image_data:
        raise ValueError("Image data missing.")

    # Use pre-analyzed result if provided, otherwise analyze
    if payload.get("image_result"):
        raw_result = payload.get("image_result")
    else:
        image_bytes = base64.b64decode(image_data.split(",")[-1])
        raw_result = image_analyzer.analyze(image_bytes)
    
    dominant = raw_result.get("dominant_emotion", "neutral")
    emotion_map = {
        "happy": "happy",
        "surprised": "happy",
        "sad": "sad",
        "disgusted": "sad",
        "angry": "angry",
        "fearful": "stressed",
        "neutral": "calm",
    }
    mapped_emotion = emotion_map.get(dominant, "calm")
    stress_score = raw_result.get("stress_level", 0.5)
    stress_level = categorize_stress(stress_score)
    confidence = raw_result.get("confidence", 0.0)
    risk_level = categorize_risk(stress_level, confidence)
    # Use emotion-aware coping suggestions
    tips = fusion_model.get_coping_suggestions({
        "stress_level": stress_score,
        "emotion": mapped_emotion,
        "primary_emotion": mapped_emotion,
        "dominant_emotion": dominant
    })

    record = AnalysisRecord(
        user_id=user.id,
        mode="image",
        emotion=mapped_emotion,
        emotion_emoji=EMOJI_MAP.get(mapped_emotion, "🙂"),
        stress_level=stress_level,
        stress_score=stress_score,
        confidence=confidence,
        risk_level=risk_level,
        suggestions=tips,
        ai_tip=wellness_tip(mapped_emotion, stress_level),
        meta={
            "raw_emotions": raw_result.get("emotions"),
            "facial_features": raw_result.get("facial_features"),
        },
    )
    db.session.add(record)
    db.session.flush()

    update_behavioral_profile(user, record)
    user.total_sessions += 1
    user.last_login_at = datetime.utcnow()

    if stress_level in {"high", "critical", "severe_stress"}:
        record_high_stress_alert(user, record)
    
    # Auto-flag high-risk users
    check_and_flag_high_risk_user(user)

    db.session.commit()
    return record


def run_fusion_analysis(user: User, payload: Dict[str, Any]) -> AnalysisRecord:
    text = payload.get("text", "")
    image_data = payload.get("image_data")
    behavioral_payload = payload.get("behavioral_data", {})

    # Use pre-analyzed results if provided
    text_result = payload.get("text_result") or (text_analyzer.analyze(text) if text else None)
    image_result = payload.get("image_result")
    if not image_result and image_data:
        image_bytes = base64.b64decode(image_data.split(",")[-1])
        image_result = image_analyzer.analyze(image_bytes)

    behavioral_result = behavioral_analyzer.analyze(behavioral_payload) if behavioral_payload else None

    fusion_result = fusion_model.fuse_predictions(
        text_result, image_result, behavioral_result
    )

    stress_score = fusion_result.get("fused_stress_level", 0.5)
    stress_level = fusion_result.get("stress_category", categorize_stress(stress_score))
    confidence = fusion_result.get("confidence", 0.0)
    risk_level = categorize_risk(stress_level, confidence)
    emotion = (
        (text_result or {}).get("primary_emotion")
        or (image_result or {}).get("dominant_emotion")
        or "calm"
    )
    emotion = {
        "joy": "happy",
        "happy": "happy",
        "sadness": "sad",
        "sad": "sad",
        "anger": "angry",
        "fear": "stressed",
        "neutral": "calm",
    }.get(emotion, "calm")

    # Get emotion-aware coping suggestions
    suggestions = fusion_model.get_coping_suggestions({
        "stress_level": stress_score,
        "emotion": emotion,
        "primary_emotion": emotion
    })
    if not suggestions:
        suggestions = fusion_result.get("recommendations", [])

    record = AnalysisRecord(
        user_id=user.id,
        mode="fusion",
        emotion=emotion,
        emotion_emoji=EMOJI_MAP.get(emotion, "🙂"),
        stress_level=stress_level,
        stress_score=stress_score,
        confidence=confidence,
        risk_level=risk_level,
        suggestions=suggestions,
        ai_tip=wellness_tip(emotion, stress_level),
        meta={
            "modalities_used": fusion_result.get("modalities_used"),
            "individual_scores": fusion_result.get("individual_scores"),
            "analysis": fusion_result.get("analysis"),
            "behavioral": behavioral_result,
        },
    )
    db.session.add(record)
    db.session.flush()

    update_behavioral_profile(user, record, text=text)
    user.total_sessions += 1
    user.last_login_at = datetime.utcnow()

    if stress_level in {"high", "critical", "severe_stress"}:
        record_high_stress_alert(user, record)
    
    # Auto-flag high-risk users
    check_and_flag_high_risk_user(user)

    db.session.commit()
    return record


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------


def register_routes(app: Flask) -> None:
    @app.get("/")
    def home():
        return render_template("index.html")
    
    @app.get("/admin")
    def admin_dashboard():
        """Admin dashboard page"""
        return render_template("admin.html")

    # ---------------- Authentication ---------------- #
    @app.post("/api/auth/signup")
    def signup():
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        full_name = data.get("full_name", "")
        role = data.get("role", "user").lower()  # Accept role from form

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"error": "User already exists"}), 400

        # Validate role
        if role not in {"user", "admin"}:
            role = "user"

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Signup successful", "role": role}), 201

    @app.post("/api/auth/login")
    def login():
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Invalid credentials"}), 401

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        user.last_login_at = datetime.utcnow()
        db.session.commit()

        token = generate_token(user)
        return jsonify({"access_token": token, "user": user.to_public_dict()})

    @app.get("/api/auth/me")
    def me():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify({"user": user.to_public_dict()})

    # ---------------- Analysis ---------------- #
    @app.post("/api/analyze/text")
    def analyze_text_endpoint():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            record = run_text_analysis(user, request.get_json() or {})
            return jsonify({"analysis": record.to_dict()})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/predict")
    def unified_predict():
        """
        Unified prediction endpoint with new response format.
        Expects JSON:
        {
            "mode": "text" | "image" | "fusion" | "webcam",
            "text": "...",
            "image_base64": "..."  # or image_data
        }
        Returns unified format with primary_emotion, stress_category, risk_score, etc.
        """
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        mode = (data.get("mode") or "text").lower()
        text = data.get("text", "")
        image_b64 = data.get("image_base64") or data.get("image_data")
        behavioral_data = data.get("behavioral_data", {})

        # Run analysis and capture raw results for explainability
        text_result = None
        image_result = None
        
        try:
            if mode == "text":
                if text:
                    text_result = text_analyzer.analyze(text)
                    # Use text_result for record creation
                    record = run_text_analysis(user, {"text": text, "text_result": text_result})
                else:
                    return jsonify({"error": "Text is required for text mode"}), 400
            elif mode in {"image", "webcam"}:
                if image_b64:
                    image_bytes = base64.b64decode(image_b64.split(",")[-1])
                    image_result = image_analyzer.analyze(image_bytes)
                    record = run_image_analysis(user, {"image_data": image_b64, "image_result": image_result})
                else:
                    return jsonify({"error": "Image is required for image mode"}), 400
            elif mode == "fusion":
                if text:
                    text_result = text_analyzer.analyze(text)
                if image_b64:
                    image_bytes = base64.b64decode(image_b64.split(",")[-1])
                    image_result = image_analyzer.analyze(image_bytes)
                record = run_fusion_analysis(
                    user,
                    {"text": text, "image_data": image_b64, "behavioral_data": behavioral_data,
                     "text_result": text_result, "image_result": image_result},
                )
            else:
                return jsonify({"error": "Unsupported mode"}), 400
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        rec_dict = record.to_dict()
        stress_score = float(rec_dict.get("stress_score", 0.5))
        
        # Determine primary emotion FIRST: prioritize image if available, otherwise text
        emotion = "neutral"
        if image_result:
            img_emotion = image_result.get("primary_emotion") or image_result.get("dominant_emotion", "neutral")
            # Map FER emotion to platform emotion if needed
            emotion = FER_TO_PLATFORM_EMOTION.get(img_emotion, img_emotion)
        elif text_result:
            emotion = text_result.get("primary_emotion", text_result.get("dominant_emotion", "neutral"))
            # Map DistilBERT emotion to platform emotion if needed
            if emotion not in PRIMARY_EMOJI:
                from backend.config.labels import DISTILBERT_TO_PLATFORM_EMOTION
                emotion = DISTILBERT_TO_PLATFORM_EMOTION.get(emotion, "neutral")
        
        emotion_label = emotion.capitalize()  # For mapping (e.g., "Sad", "Happy")
        emotion_emoji = get_emotion_emoji(emotion)
        emotion_description = get_emotion_description(emotion)
        
        # Get model stress category (from text_result or computed from stress_score)
        model_stress_category = None
        if text_result and "stress_label" in text_result:
            model_stress_label = text_result["stress_label"]
            model_stress_category = STRESS_DISPLAY.get(model_stress_label, None)
        elif image_result:
            # For images, compute from stress_score
            model_stress_label = stress_score_to_label(stress_score)
            model_stress_category = STRESS_DISPLAY.get(model_stress_label, None)
        else:
            # Fallback: compute from stress_score
            model_stress_label = stress_score_to_label(stress_score)
            model_stress_category = STRESS_DISPLAY.get(model_stress_label, None)
        
        # Map emotion to base stress category
        emotion_stress_category = map_emotion_to_stress(emotion_label)
        
        # Combine model stress with emotion-based stress
        final_stress_category = combine_stress(model_stress_category, emotion_stress_category)
        
        # Convert final stress category to internal label
        final_stress_label = stress_category_to_internal_label(final_stress_category)
        
        # Compute risk score and level based on FINAL stress category (using display string)
        risk_score, risk_level = stress_category_to_risk_score(final_stress_category)
        
        # Generate key indicators (use final stress score for consistency)
        # Recalculate stress_score from final_stress_label for consistency
        final_stress_score_map = {
            "no_stress": 0.1,
            "low": 0.3,
            "moderate": 0.6,
            "high": 0.85
        }
        final_stress_score = final_stress_score_map.get(final_stress_label, stress_score)
        key_indicators = generate_key_indicators(final_stress_score, emotion, text_result, image_result)
        
        # Get coping suggestions using new advice service (use final stress label)
        coping_suggestions = generate_coping_suggestions(emotion, final_stress_label, risk_level)
        
        # Get wellness tip using new advice service (use final stress label)
        wellness_tip_text = generate_wellness_tip(emotion, final_stress_label, risk_level)
        
        # Generate explainability
        text_explain = {}
        if text and text_result:
            text_explain = generate_text_explanation(text, text_result)
            text_explain["has_text"] = True
        else:
            text_explain = {
                "has_text": False,
                "summary": "No text was analyzed for this prediction.",
                "keywords": [],
                "tone": "N/A"
            }
        
        image_explain = {}
        if image_result:
            image_explain = generate_image_explanation(image_result)
            image_explain["has_image"] = True
        else:
            image_explain = {
                "has_image": False,
                "summary": "No image was analyzed for this prediction.",
                "emotion_from_face": None,
                "cam_hint": "N/A"
            }
        
        # Build unified response
        response = {
            "primary_emotion": {
                "label": emotion_label,
                "emoji": emotion_emoji,
                "description": emotion_description
            },
            "stress_category": final_stress_label,  # Internal label
            "stress_category_display": final_stress_category,  # Display label
            "risk_score": risk_score,
            "risk_level": risk_level,
            "key_indicators": key_indicators,
            "coping_suggestions": coping_suggestions,
            "wellness_tip": wellness_tip_text,
            "text_explain": text_explain,
            "image_explain": image_explain,
            # Legacy fields for backward compatibility
            "emotion": emotion,
            "emotion_emoji": emotion_emoji,
            "stress_level": final_stress_category,
            "confidence": rec_dict.get("confidence", 0.0),
        }
        
        return jsonify(response)

    @app.post("/api/analyze/image")
    def analyze_image_endpoint():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            record = run_image_analysis(user, request.get_json() or {})
            return jsonify({"analysis": record.to_dict()})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/analyze/fusion")
    def analyze_fusion_endpoint():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            record = run_fusion_analysis(user, request.get_json() or {})
            return jsonify({"analysis": record.to_dict()})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/analyze/webcam")
    def analyze_webcam_endpoint():
        # Webcam capture reuses image pipeline
        return analyze_image_endpoint()

    @app.get("/api/analyze/history")
    def analysis_history():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        limit = int(request.args.get("limit", 25))
        records = (
            AnalysisRecord.query.filter_by(user_id=user.id)
            .order_by(AnalysisRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return jsonify({"analyses": [rec.to_dict() for rec in records]})

    @app.get("/api/user/timeline")
    def user_timeline():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        records = (
            AnalysisRecord.query.filter_by(user_id=user.id)
            .order_by(AnalysisRecord.created_at.asc())
            .limit(50)
            .all()
        )
        timeline = [
            {
                "timestamp": rec.created_at.strftime("%Y-%m-%d %H:%M"),
                "emotion": rec.emotion,
                "stress_level": rec.stress_level,
                "stress_score": rec.stress_score,
            }
            for rec in records
        ]
        return jsonify({"timeline": timeline})

    @app.get("/api/user/behavioral")
    def user_behavioral():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify(
            {
                "behavioral_profile": user.behavioral_profile or {},
                "emoji_fingerprint": user.emoji_fingerprint or {},
                "total_sessions": user.total_sessions,
            }
        )

    @app.delete("/api/user/data")
    def delete_user_data():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        AnalysisRecord.query.filter_by(user_id=user.id).delete()
        user.behavioral_profile = {}
        user.emoji_fingerprint = {}
        user.total_sessions = 0
        user.stress_alerts = 0
        db.session.commit()
        return jsonify({"message": "All personal data cleared"})

    # ---------------- Explainability ---------------- #
    @app.post("/api/explain/text")
    def explain_text_endpoint():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        text = data.get("text", "")
        if not text.strip():
            return jsonify({"error": "Text input is required"}), 400

        raw_result = text_analyzer.analyze(text)
        explanation = explain_engine.explain_text(text, raw_result)
        return jsonify(
            {
                "tokens": explanation.get("token_explanations", []),
                "heatmap": explanation.get("heatmap_data", []),
                "summary": explanation.get("explanation_summary", ""),
            }
        )

    @app.post("/api/explain/image")
    def explain_image_endpoint():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        image_b64 = data.get("image_base64") or data.get("image_data")
        if not image_b64:
            return jsonify({"error": "Image data missing"}), 400

        try:
            image_bytes = base64.b64decode(image_b64.split(",")[-1])
        except Exception:
            return jsonify({"error": "Invalid image encoding"}), 400

        gradcam_payload = generate_gradcam_for_image(image_bytes)
        if not gradcam_payload.get("overlay_base64"):
            return jsonify({"error": "Unable to generate explanation"}), 500

        return jsonify(
            {
                "overlay_base64": gradcam_payload["overlay_base64"],
                "dominant_emotion": gradcam_payload.get("dominant_emotion"),
                "confidence": gradcam_payload.get("confidence"),
            }
        )

    # ---------------- Reports & Data Export ---------------- #
    @app.post("/api/reports/pdf")
    def generate_pdf_report():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        # Get all analyses for comprehensive report
        all_records = (
            AnalysisRecord.query.filter_by(user_id=user.id)
            .order_by(AnalysisRecord.created_at.desc())
            .all()
        )
        
        if not all_records:
            return jsonify({"error": "No analyses found"}), 400

        latest_record = all_records[0]
        
        # Enhanced analysis data with all records
        analysis_data = latest_record.to_dict()
        analysis_data["behavioral_analysis"] = user.behavioral_profile or {}
        analysis_data["all_analyses"] = [rec.to_dict() for rec in all_records]
        analysis_data["analysis_count"] = len(all_records)
        analysis_data["analysis_summary"] = {
            "total": len(all_records),
            "date_range": {
                "first": all_records[-1].created_at.isoformat() if all_records else None,
                "last": all_records[0].created_at.isoformat() if all_records else None,
            }
        }

        report_path = report_generator.generate_report(
            user.to_public_dict(), 
            analysis_data, 
            output_path=str(REPORTS_DIR / f"mindscope_report_{user.username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf")
        )
        return send_file(report_path, as_attachment=True)

    @app.post("/api/reports/export")
    def export_data_zip():
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        records = (
            AnalysisRecord.query.filter_by(user_id=user.id)
            .order_by(AnalysisRecord.created_at.asc())
            .all()
        )
        
        # Enhanced export with detailed analysis information
        export_payload = {
            "user": user.to_public_dict(),
            "analyses": [rec.to_dict() for rec in records],
            "analysis_summary": {
                "total_analyses": len(records),
                "date_range": {
                    "first": records[0].created_at.isoformat() if records else None,
                    "last": records[-1].created_at.isoformat() if records else None,
                },
                "emotion_distribution": {},
                "stress_distribution": {},
                "risk_distribution": {},
            },
            "behavioral_profile": user.behavioral_profile or {},
            "emoji_fingerprint": user.emoji_fingerprint or {},
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        # Calculate distributions
        for rec in records:
            emotion = rec.emotion or "unknown"
            stress = rec.stress_level or "unknown"
            risk = rec.risk_level or "unknown"
            
            export_payload["analysis_summary"]["emotion_distribution"][emotion] = \
                export_payload["analysis_summary"]["emotion_distribution"].get(emotion, 0) + 1
            export_payload["analysis_summary"]["stress_distribution"][stress] = \
                export_payload["analysis_summary"]["stress_distribution"].get(stress, 0) + 1
            export_payload["analysis_summary"]["risk_distribution"][risk] = \
                export_payload["analysis_summary"]["risk_distribution"].get(risk, 0) + 1

        export_path = EXPORT_DIR / f"mindscope_export_{user.username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(export_path, "w") as zf:
            json_bytes = json.dumps(export_payload, indent=2).encode("utf-8")
            zf.writestr("mindscope_export.json", json_bytes)
            
            # Also create a readable summary text file
            summary_text = f"""MindScope AI - Analysis Report Export
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
User: {user.username} ({user.email})

SUMMARY
=======
Total Analyses: {len(records)}
Date Range: {export_payload['analysis_summary']['date_range']['first']} to {export_payload['analysis_summary']['date_range']['last']}

EMOTION DISTRIBUTION
===================
{chr(10).join([f"{emotion}: {count}" for emotion, count in export_payload['analysis_summary']['emotion_distribution'].items()])}

STRESS DISTRIBUTION
===================
{chr(10).join([f"{stress}: {count}" for stress, count in export_payload['analysis_summary']['stress_distribution'].items()])}

RISK DISTRIBUTION
================
{chr(10).join([f"{risk}: {count}" for risk, count in export_payload['analysis_summary']['risk_distribution'].items()])}

DETAILED ANALYSES
=================
See mindscope_export.json for complete analysis records with timestamps, emotions, stress levels, and risk scores.
"""
            zf.writestr("summary.txt", summary_text.encode("utf-8"))

        return send_file(export_path, as_attachment=True)

    # ---------------- Admin endpoints ---------------- #
    @app.get("/api/admin/users")
    @admin_required
    def admin_users():
        # Only get regular users, exclude admins
        users = User.query.filter(User.role == "user").all()
        # Anonymize user data for admin view (hash IDs)
        import hashlib
        anonymized = []
        for u in users:
            user_dict = u.to_public_dict()
            # Hash user ID for privacy
            user_dict["hashed_id"] = hashlib.sha256(str(u.id).encode()).hexdigest()[:8]
            # Keep original ID for admin operations (like reports)
            user_dict["id"] = u.id
            anonymized.append(user_dict)
        return jsonify({"users": anonymized})
    
    @app.get("/api/admin/users/<int:user_id>/analyses")
    @admin_required
    def admin_user_analyses(user_id):
        """Get all analyses for a specific user (admin only)"""
        user = User.query.get_or_404(user_id)
        if user.role == "admin":
            return jsonify({"error": "Cannot get admin analyses"}), 403
        
        analyses = AnalysisRecord.query.filter_by(user_id=user_id)\
            .order_by(AnalysisRecord.created_at.desc()).all()
        
        return jsonify({
            "user_id": user_id,
            "analyses": [rec.to_dict() for rec in analyses],
            "total": len(analyses)
        })

    @app.get("/api/admin/analytics")
    @admin_required
    def admin_analytics():
        # Only count regular users, exclude admins
        total_users = User.query.filter(User.role == "user").count()
        
        # Only count analyses from regular users
        user_ids = [u.id for u in User.query.filter(User.role == "user").all()]
        total_analyses = AnalysisRecord.query.filter(AnalysisRecord.user_id.in_(user_ids)).count() if user_ids else 0
        
        # Stress distribution from user analyses only
        user_analyses = AnalysisRecord.query.filter(AnalysisRecord.user_id.in_(user_ids)).all() if user_ids else []
        stress_distribution = {
            "low": sum(1 for a in user_analyses if a.stress_level and "low" in a.stress_level.lower()),
            "moderate": sum(1 for a in user_analyses if a.stress_level and "moderate" in a.stress_level.lower()),
            "high": sum(1 for a in user_analyses if a.stress_level and "high" in a.stress_level.lower()),
            "critical": sum(1 for a in user_analyses if a.stress_level and "critical" in a.stress_level.lower()),
        }
        
        # Emotion counts from user analyses only
        emotion_counts = {}
        for emotion in EMOJI_MAP.keys():
            emotion_counts[emotion] = sum(1 for a in user_analyses if a.emotion and a.emotion.lower() == emotion.lower())

        # Only alerts for regular users
        user_alert_ids = [u.id for u in User.query.filter(User.role == "user").all()]
        alerts = [serialize_admin_alert(alert) for alert in AdminAlert.query.filter(AdminAlert.user_id.in_(user_alert_ids)).all()] if user_alert_ids else []
        
        # Get recent predictions from users only (anonymized)
        recent_records = AnalysisRecord.query.filter(AnalysisRecord.user_id.in_(user_ids)).order_by(AnalysisRecord.created_at.desc()).limit(50).all() if user_ids else []
        import hashlib
        recent_predictions = []
        for rec in recent_records:
            user_hash = hashlib.sha256(str(rec.user_id).encode()).hexdigest()[:8]
            recent_predictions.append({
                "hashed_user_id": user_hash,
                "risk_level": rec.risk_level,
                "timestamp": rec.created_at.isoformat(),
                "mode": rec.mode,
                "emotion": rec.emotion,
                "stress_level": rec.stress_level,
            })

        return jsonify(
            {
                "total_users": total_users,
                "total_analyses": total_analyses,
                "stress_distribution": stress_distribution,
                "emotion_distribution": emotion_counts,
                "alerts": alerts,
                "recent_predictions": recent_predictions,
            }
        )

    @app.post("/api/admin/messages")
    @admin_required
    def admin_send_message():
        """Send message to a specific user or broadcast to all"""
        user = get_user_from_request()
        data = request.get_json() or {}
        receiver_id = data.get("receiver_id")  # NULL for broadcast
        title = data.get("title", "Support Message")
        body = data.get("body", "")
        is_broadcast = data.get("is_broadcast", False) or receiver_id is None

        if not body.strip():
            return jsonify({"error": "Message body is required"}), 400

        if is_broadcast:
            # Send to all users
            all_users = User.query.filter(User.role == "user").all()
            for target in all_users:
                msg = Message(
                    sender_id=user.id,
                    receiver_id=target.id,
                    title=title,
                    body=body,
                    is_broadcast=True,
                )
                db.session.add(msg)
            
            # Log admin action
            log_admin_action(
                user.id,
                "SEND_BROADCAST",
                f"Broadcasted '{title}' to {len(all_users)} users"
            )
            
            db.session.commit()
            return jsonify({"message": f"Message broadcasted to {len(all_users)} users"})
        else:
            target = User.query.get(receiver_id)
            if not target:
                return jsonify({"error": "User not found"}), 404
            msg = Message(
                sender_id=user.id,
                receiver_id=target.id,
                title=title,
                body=body,
                is_broadcast=False,
            )
            db.session.add(msg)
            db.session.commit()
            return jsonify({"message": "Message sent successfully"})

    @app.get("/api/user/messages")
    def user_get_messages():
        """Get all messages for the current user"""
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        # Get direct messages and broadcasts
        messages = Message.query.filter(
            (Message.receiver_id == user.id) | (Message.is_broadcast == True)
        ).order_by(Message.created_at.desc()).all()

        return jsonify({
            "messages": [{
                "id": m.id,
                "title": m.title,
                "body": m.body,
                "is_read": m.is_read,
                "is_broadcast": m.is_broadcast,
                "created_at": m.created_at.isoformat(),
                "sender": m.sender.username if m.sender else "System",
            } for m in messages]
        })

    @app.post("/api/user/messages/read")
    def user_mark_read():
        """Mark one or more messages as read"""
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        message_ids = data.get("message_ids", [])
        if not message_ids:
            return jsonify({"error": "message_ids required"}), 400

        messages = Message.query.filter(
            Message.id.in_(message_ids),
            (Message.receiver_id == user.id) | (Message.is_broadcast == True)
        ).all()

        for msg in messages:
            msg.is_read = True
        db.session.commit()

        return jsonify({"message": f"Marked {len(messages)} messages as read"})

    @app.post("/api/admin/support")
    @admin_required
    def admin_support():
        """Legacy endpoint - redirects to new messaging system"""
        data = request.get_json() or {}
        target_id = data.get("user_id")
        message = data.get("message", "")
        if not message:
            return jsonify({"error": "Message body is required"}), 400
        payload = {
            "title": "Support Message",
            "body": message,
        }
        if target_id:
            payload["receiver_id"] = target_id
            payload["is_broadcast"] = False
        else:
            payload["is_broadcast"] = True
        return admin_send_message()

    @app.get("/api/admin/metrics")
    @admin_required
    def admin_metrics():
        metrics_file = BASE_DIR / "models" / "metrics.json"
        if not metrics_file.exists():
            return jsonify({"metrics": None, "message": "Metrics not evaluated yet"})

        try:
            metrics = json.loads(metrics_file.read_text())
        except Exception:
            return jsonify({"metrics": None, "message": "Failed to read metrics file"}), 500

        return jsonify({"metrics": metrics})

    # ========================================================================
    # NEW ADMIN FEATURES - User Analytics Only
    # ========================================================================

    @app.get("/api/admin/emotion-stats")
    @admin_required
    def admin_emotion_stats():
        """Get emotion distribution for last 7 days (users only, exclude admins)"""
        range_days = int(request.args.get("days", 7))
        limit = int(request.args.get("limit", 500))
        
        cutoff_date = datetime.utcnow() - timedelta(days=range_days)
        
        # Only get analyses from regular users, exclude admins
        user_ids = [u.id for u in User.query.filter(User.role == "user").all()]
        
        if not user_ids:
            return jsonify({
                "range_days": range_days,
                "total_analyses": 0,
                "emotion_counts": {}
            })
        
        # Get recent analyses from users only
        recent_analyses = AnalysisRecord.query.filter(
            AnalysisRecord.created_at >= cutoff_date,
            AnalysisRecord.user_id.in_(user_ids)
        ).order_by(AnalysisRecord.created_at.desc()).limit(limit).all()
        
        # Count emotions
        emotion_counts = {}
        for analysis in recent_analyses:
            emotion = analysis.emotion or "neutral"
            emotion_label = emotion.capitalize()
            emotion_counts[emotion_label] = emotion_counts.get(emotion_label, 0) + 1
        
        return jsonify({
            "range_days": range_days,
            "total_analyses": len(recent_analyses),
            "emotion_counts": emotion_counts
        })

    @app.get("/api/admin/login-stats")
    @admin_required
    def admin_login_stats():
        """Get login activity for last 7 days (users only, exclude admins)"""
        range_days = int(request.args.get("days", 7))
        
        daily_logins = []
        for i in range(range_days):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            # Count distinct regular users who logged in on this day (exclude admins)
            users_logged_in = User.query.filter(
                User.role == "user",
                User.last_login_at >= start_of_day,
                User.last_login_at <= end_of_day
            ).count()
            
            daily_logins.append({
                "date": date.isoformat(),
                "count": users_logged_in
            })
        
        # Reverse to show oldest first
        daily_logins.reverse()
        
        return jsonify({
            "range_days": range_days,
            "daily_logins": daily_logins
        })

    @app.post("/api/admin/messages/broadcast")
    @admin_required
    def admin_broadcast_message():
        """Send wellness broadcast to all users"""
        user = get_user_from_request()
        data = request.get_json() or {}
        title = data.get("title", "Wellness Message")
        body = data.get("body", "")
        
        if not body.strip():
            return jsonify({"error": "Message body is required"}), 400
        
        # Send to all users (exclude admins)
        all_users = User.query.filter(User.role == "user").all()
        for target in all_users:
            msg = Message(
                sender_id=user.id,
                receiver_id=target.id,
                title=title,
                body=body,
                is_broadcast=True,
            )
            db.session.add(msg)
        
        # Log admin action
        log_admin_action(
            user.id,
            "SEND_BROADCAST",
            f"Broadcasted '{title}' to {len(all_users)} users"
        )
        
        db.session.commit()
        return jsonify({
            "message": f"Message broadcasted to {len(all_users)} users",
            "count": len(all_users)
        })

    @app.get("/api/admin/messages/sent")
    @admin_required
    def admin_sent_messages():
        """Get messages sent by admins"""
        user = get_user_from_request()
        limit = int(request.args.get("limit", 50))
        
        messages = Message.query.filter(
            Message.sender_id == user.id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        return jsonify({
            "messages": [{
                "id": m.id,
                "title": m.title,
                "body": m.body[:100] + "..." if len(m.body) > 100 else m.body,
                "is_broadcast": m.is_broadcast,
                "receiver_id": m.receiver_id,
                "created_at": m.created_at.isoformat(),
            } for m in messages]
        })

    @app.get("/api/admin/resources")
    @admin_required
    def admin_get_resources():
        """Get all resources (admin view)"""
        resources = Resource.query.order_by(Resource.created_at.desc()).all()
        return jsonify({
            "resources": [{
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "type": r.type,
                "url_or_path": r.url_or_path,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            } for r in resources]
        })

    @app.post("/api/admin/resources")
    @admin_required
    def admin_create_resource():
        """Create a new resource"""
        user = get_user_from_request()
        data = request.get_json() or {}
        
        title = data.get("title", "").strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400
        
        resource = Resource(
            title=title,
            description=data.get("description", ""),
            type=data.get("type", "link"),
            url_or_path=data.get("url_or_path", ""),
            is_active=data.get("is_active", True)
        )
        db.session.add(resource)
        
        log_admin_action(
            user.id,
            "ADD_RESOURCE",
            f"Added resource: {title}"
        )
        
        db.session.commit()
        return jsonify({
            "message": "Resource created successfully",
            "resource": {
                "id": resource.id,
                "title": resource.title,
                "type": resource.type,
            }
        }), 201

    @app.put("/api/admin/resources/<int:resource_id>")
    @admin_required
    def admin_update_resource(resource_id: int):
        """Update a resource"""
        user = get_user_from_request()
        resource = Resource.query.get_or_404(resource_id)
        data = request.get_json() or {}
        
        if "title" in data:
            resource.title = data["title"]
        if "description" in data:
            resource.description = data["description"]
        if "type" in data:
            resource.type = data["type"]
        if "url_or_path" in data:
            resource.url_or_path = data["url_or_path"]
        if "is_active" in data:
            resource.is_active = data["is_active"]
        resource.updated_at = datetime.utcnow()
        
        log_admin_action(
            user.id,
            "UPDATE_RESOURCE",
            f"Updated resource: {resource.title}"
        )
        
        db.session.commit()
        return jsonify({"message": "Resource updated successfully"})

    @app.delete("/api/admin/resources/<int:resource_id>")
    @admin_required
    def admin_delete_resource(resource_id: int):
        """Delete a resource"""
        user = get_user_from_request()
        resource = Resource.query.get_or_404(resource_id)
        title = resource.title
        
        log_admin_action(
            user.id,
            "DELETE_RESOURCE",
            f"Deleted resource: {title}"
        )
        
        db.session.delete(resource)
        db.session.commit()
        return jsonify({"message": "Resource deleted successfully"})

    @app.get("/api/resources")
    def get_resources():
        """Get active resources (user-facing)"""
        resources = Resource.query.filter_by(is_active=True)\
            .order_by(Resource.created_at.desc()).all()
        return jsonify({
            "resources": [{
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "type": r.type,
                "url_or_path": r.url_or_path,
                "created_at": r.created_at.isoformat(),
            } for r in resources]
        })

    @app.get("/api/admin/model-versions")
    @admin_required
    def admin_model_versions():
        """Get model version and training history"""
        metrics_file = BASE_DIR / "models" / "metrics.json"
        
        result = {
            "model_version": "v1.0",
            "last_trained_at": None,
            "metrics": None
        }
        
        if metrics_file.exists():
            try:
                metrics = json.loads(metrics_file.read_text())
                result["metrics"] = metrics
                result["model_version"] = metrics.get("model_version", "v1.0")
                result["last_trained_at"] = metrics.get("last_trained_at")
            except Exception as e:
                logger.error(f"Failed to read metrics: {e}")
        
        return jsonify(result)

    @app.get("/api/admin/logs")
    @admin_required
    def admin_get_logs():
        """Get admin audit logs (all admin actions)"""
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        
        logs = AdminAuditLog.query.order_by(AdminAuditLog.created_at.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            "logs": [{
                "id": log.id,
                "admin_email": log.admin.email if log.admin else "Unknown",
                "admin_id": log.admin_id,
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            } for log in logs],
            "total": AdminAuditLog.query.count()
        })

    @app.get("/api/admin/analyses")
    @admin_required
    def admin_get_analyses():
        """Get all user analyses (users only, exclude admins)"""
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        
        # Only get analyses from regular users
        user_ids = [u.id for u in User.query.filter(User.role == "user").all()]
        
        if not user_ids:
            return jsonify({
                "analyses": [],
                "total": 0
            })
        
        analyses = AnalysisRecord.query.filter(
            AnalysisRecord.user_id.in_(user_ids)
        ).order_by(AnalysisRecord.created_at.desc()).limit(limit).offset(offset).all()
        
        import hashlib
        result = []
        for analysis in analyses:
            user_hash = hashlib.sha256(str(analysis.user_id).encode()).hexdigest()[:8]
            result.append({
                "id": analysis.id,
                "hashed_user_id": user_hash,
                "emotion": analysis.emotion,
                "emotion_emoji": analysis.emotion_emoji,
                "stress_level": analysis.stress_level,
                "stress_score": analysis.stress_score,
                "risk_level": analysis.risk_level,
                "mode": analysis.mode,
                "created_at": analysis.created_at.isoformat(),
            })
        
        total = AnalysisRecord.query.filter(AnalysisRecord.user_id.in_(user_ids)).count()
        
        return jsonify({
            "analyses": result,
            "total": total,
            "limit": limit,
            "offset": offset
        })

    @app.get("/api/system/status")
    def system_status():
        return jsonify(
            {
                "status": "ok",
                "models": {
                    "text": True,
                    "image": True,
                    "behavioral": True,
                    "fusion": True,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


# Instantiate default app for convenience (python mindscope_flask/app.py)
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

