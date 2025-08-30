import asyncio
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
from typing import AsyncGenerator

from .models import Base, BCISession, ConfusionData, ScreenshotAnalysis, HelpSuggestion, DeviceStatus, LearningAnalytics, UserPreferences

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bci_monitor.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False  # Set to True for SQL debugging
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Initialize the database and create tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

class DatabaseManager:
    """Manages database operations for BCI monitoring."""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def create_session(self, session_id: str, user_id: str, device_info: dict) -> BCISession:
        """Create a new BCI monitoring session."""
        async with self.session_factory() as db:
            try:
                session = BCISession(
                    session_id=session_id,
                    user_id=user_id,
                    device_info=device_info,
                    status="active"
                )
                db.add(session)
                await db.commit()
                await db.refresh(session)
                logger.info(f"Created new session: {session_id}")
                return session
            except Exception as e:
                await db.rollback()
                logger.error(f"Error creating session: {e}")
                raise
    
    async def record_confusion_data(self, session_id: str, confusion_level: float, 
                                  eeg_data: dict, features: dict, quality: dict) -> ConfusionData:
        """Record confusion level measurement."""
        async with self.session_factory() as db:
            try:
                confusion_record = ConfusionData(
                    session_id=session_id,
                    confusion_level=confusion_level,
                    raw_eeg_data=eeg_data,
                    processed_features=features,
                    signal_quality=quality,
                    threshold_exceeded=confusion_level > 0.7  # Default threshold
                )
                db.add(confusion_record)
                await db.commit()
                await db.refresh(confusion_record)
                return confusion_record
            except Exception as e:
                await db.rollback()
                logger.error(f"Error recording confusion data: {e}")
                raise
    
    async def record_screenshot_analysis(self, session_id: str, screenshot_path: str,
                                       confusion_level: float, analysis: dict) -> ScreenshotAnalysis:
        """Record screenshot analysis results."""
        async with self.session_factory() as db:
            try:
                screenshot_analysis = ScreenshotAnalysis(
                    session_id=session_id,
                    screenshot_path=screenshot_path,
                    confusion_level_trigger=confusion_level,
                    analysis_results=analysis.get("general_analysis", {}),
                    educational_context=analysis.get("educational_context", {}),
                    detected_elements=analysis.get("detected_elements", [])
                )
                db.add(screenshot_analysis)
                await db.commit()
                await db.refresh(screenshot_analysis)
                logger.info(f"Recorded screenshot analysis for session: {session_id}")
                return screenshot_analysis
            except Exception as e:
                await db.rollback()
                logger.error(f"Error recording screenshot analysis: {e}")
                raise
    
    async def record_help_suggestion(self, session_id: str, screenshot_analysis_id: int,
                                   confusion_level: float, suggestions: list, 
                                   subject: str, context: dict) -> HelpSuggestion:
        """Record generated help suggestions."""
        async with self.session_factory() as db:
            try:
                help_suggestion = HelpSuggestion(
                    session_id=session_id,
                    screenshot_analysis_id=screenshot_analysis_id,
                    confusion_level=confusion_level,
                    suggestions=suggestions,
                    subject=subject,
                    context=context
                )
                db.add(help_suggestion)
                await db.commit()
                await db.refresh(help_suggestion)
                logger.info(f"Recorded help suggestion for session: {session_id}")
                return help_suggestion
            except Exception as e:
                await db.rollback()
                logger.error(f"Error recording help suggestion: {e}")
                raise
    
    async def update_device_status(self, session_id: str, connected: bool, 
                                 device_info: dict, signal_quality: float = None) -> DeviceStatus:
        """Update BCI device status."""
        async with self.session_factory() as db:
            try:
                device_status = DeviceStatus(
                    session_id=session_id,
                    connected=connected,
                    device_type=device_info.get("device_type", "unknown"),
                    device_id=device_info.get("headset_id", "unknown"),
                    signal_quality=signal_quality
                )
                db.add(device_status)
                await db.commit()
                await db.refresh(device_status)
                return device_status
            except Exception as e:
                await db.rollback()
                logger.error(f"Error updating device status: {e}")
                raise
    
    async def get_session_analytics(self, session_id: str) -> dict:
        """Get analytics for a specific session."""
        async with self.session_factory() as db:
            try:
                from sqlalchemy import func, select
                
                # Get confusion data statistics
                confusion_stats = await db.execute(
                    select(
                        func.avg(ConfusionData.confusion_level).label('avg_confusion'),
                        func.max(ConfusionData.confusion_level).label('max_confusion'),
                        func.count(ConfusionData.id).label('total_measurements'),
                        func.count().filter(ConfusionData.threshold_exceeded == True).label('threshold_exceeded_count')
                    ).where(ConfusionData.session_id == session_id)
                )
                stats = confusion_stats.first()
                
                # Get help suggestions count
                help_count = await db.execute(
                    select(func.count(HelpSuggestion.id)).where(HelpSuggestion.session_id == session_id)
                )
                
                return {
                    "session_id": session_id,
                    "average_confusion": float(stats.avg_confusion) if stats.avg_confusion else 0.0,
                    "max_confusion": float(stats.max_confusion) if stats.max_confusion else 0.0,
                    "total_measurements": stats.total_measurements or 0,
                    "threshold_exceeded_count": stats.threshold_exceeded_count or 0,
                    "help_suggestions_count": help_count.scalar() or 0
                }
            except Exception as e:
                logger.error(f"Error getting session analytics: {e}")
                return {}
    
    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences, creating default if not exists."""
        async with self.session_factory() as db:
            try:
                from sqlalchemy import select
                
                result = await db.execute(
                    select(UserPreferences).where(UserPreferences.user_id == user_id)
                )
                preferences = result.scalar_one_or_none()
                
                if not preferences:
                    # Create default preferences
                    preferences = UserPreferences(user_id=user_id)
                    db.add(preferences)
                    await db.commit()
                    await db.refresh(preferences)
                    logger.info(f"Created default preferences for user: {user_id}")
                
                return preferences
            except Exception as e:
                logger.error(f"Error getting user preferences: {e}")
                raise
    
    async def update_user_preferences(self, user_id: str, preferences_data: dict) -> UserPreferences:
        """Update user preferences."""
        async with self.session_factory() as db:
            try:
                from sqlalchemy import select
                
                result = await db.execute(
                    select(UserPreferences).where(UserPreferences.user_id == user_id)
                )
                preferences = result.scalar_one_or_none()
                
                if not preferences:
                    preferences = UserPreferences(user_id=user_id)
                    db.add(preferences)
                
                # Update preferences
                for key, value in preferences_data.items():
                    if hasattr(preferences, key):
                        setattr(preferences, key, value)
                
                await db.commit()
                await db.refresh(preferences)
                logger.info(f"Updated preferences for user: {user_id}")
                return preferences
            except Exception as e:
                await db.rollback()
                logger.error(f"Error updating user preferences: {e}")
                raise
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage database size."""
        async with self.session_factory() as db:
            try:
                from sqlalchemy import delete
                from datetime import datetime, timedelta
                
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                
                # Clean up old confusion data
                await db.execute(
                    delete(ConfusionData).where(ConfusionData.created_at < cutoff_date)
                )
                
                # Clean up old device status records
                await db.execute(
                    delete(DeviceStatus).where(DeviceStatus.created_at < cutoff_date)
                )
                
                await db.commit()
                logger.info(f"Cleaned up data older than {days_to_keep} days")
            except Exception as e:
                await db.rollback()
                logger.error(f"Error cleaning up old data: {e}")
    
    async def close(self):
        """Close database connections."""
        await self.engine.dispose()
        logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()