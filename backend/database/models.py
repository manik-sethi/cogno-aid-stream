from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

class BCISession(Base):
    """Model for BCI monitoring sessions."""
    
    __tablename__ = "bci_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True)
    user_id = Column(String(50), index=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    device_info = Column(JSON)
    status = Column(String(20), default="active")  # active, completed, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ConfusionData(Base):
    """Model for storing confusion level measurements."""
    
    __tablename__ = "confusion_data"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    confusion_level = Column(Float)  # 0.0 to 1.0
    raw_eeg_data = Column(JSON)  # Store raw EEG values
    processed_features = Column(JSON)  # Store extracted features
    signal_quality = Column(JSON)  # Store signal quality metrics
    threshold_exceeded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScreenshotAnalysis(Base):
    """Model for storing screenshot analysis results."""
    
    __tablename__ = "screenshot_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    screenshot_path = Column(String(255))
    confusion_level_trigger = Column(Float)  # Confusion level that triggered the screenshot
    analysis_results = Column(JSON)  # LLM analysis results
    educational_context = Column(JSON)  # Extracted educational context
    detected_elements = Column(JSON)  # UI elements detected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HelpSuggestion(Base):
    """Model for storing generated help suggestions."""
    
    __tablename__ = "help_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    screenshot_analysis_id = Column(Integer, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    confusion_level = Column(Float)
    suggestions = Column(JSON)  # List of help suggestions
    subject = Column(String(50))  # math, programming, etc.
    context = Column(JSON)  # Additional context used for generation
    user_feedback = Column(String(20), nullable=True)  # helpful, not_helpful, ignored
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DeviceStatus(Base):
    """Model for tracking BCI device connection status."""
    
    __tablename__ = "device_status"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    connected = Column(Boolean)
    device_type = Column(String(50))
    device_id = Column(String(100))
    signal_quality = Column(Float)  # Overall signal quality 0.0 to 1.0
    battery_level = Column(Float, nullable=True)  # If available
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LearningAnalytics(Base):
    """Model for storing learning analytics and insights."""
    
    __tablename__ = "learning_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    user_id = Column(String(50), index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Session metrics
    total_duration_minutes = Column(Float)
    average_confusion_level = Column(Float)
    max_confusion_level = Column(Float)
    confusion_spikes_count = Column(Integer)
    help_requests_count = Column(Integer)
    
    # Subject-specific metrics
    subject = Column(String(50))
    topics_covered = Column(JSON)  # List of topics/concepts
    difficulty_level = Column(String(20))
    
    # Performance indicators
    confusion_trend = Column(String(20))  # improving, declining, stable
    learning_velocity = Column(Float)  # Rate of confusion reduction
    engagement_score = Column(Float)  # Based on interaction patterns
    
    # Recommendations
    suggested_interventions = Column(JSON)
    next_session_recommendations = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserPreferences(Base):
    """Model for storing user preferences and settings."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True)
    
    # Threshold settings
    confusion_threshold = Column(Float, default=0.7)
    help_frequency = Column(String(20), default="auto")  # auto, frequent, minimal
    
    # Interface preferences
    dashboard_layout = Column(JSON)
    notification_settings = Column(JSON)
    
    # Learning preferences
    preferred_help_style = Column(String(20), default="guided")  # guided, hints, examples
    subjects_of_interest = Column(JSON)
    difficulty_preference = Column(String(20), default="adaptive")
    
    # Privacy settings
    data_sharing_consent = Column(Boolean, default=False)
    analytics_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Utility functions for model operations
def to_dict(model_instance) -> Dict[str, Any]:
    """Convert SQLAlchemy model instance to dictionary."""
    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result

def create_session_id() -> str:
    """Generate a unique session ID."""
    import uuid
    return f"session_{uuid.uuid4().hex[:12]}"

def create_user_id() -> str:
    """Generate a unique user ID."""
    import uuid
    return f"user_{uuid.uuid4().hex[:8]}"