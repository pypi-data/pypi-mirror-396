"""
SQLAlchemy ORM models for Globe Server.

This module defines the SQLAlchemy ORM models that represent the database tables,
providing object-oriented access to the database.
"""

from sqlalchemy import (
    Column, Integer, Float, String, Boolean, ForeignKey, Table,
    MetaData, create_engine, event, inspect
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import logging
import os
from globe_server import config

logger = logging.getLogger(__name__)

# Create a base class for declarative models
Base = declarative_base()

# Create engine and session factory
DATABASE_URL = f"sqlite:///{config.DATABASE_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Define SQLAlchemy ORM models
class Media(Base):
    """Media item that can be displayed on the globe."""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    filepath = Column(String)
    display_duration = Column(Integer, nullable=False)
    planet_options = Column(String)  # JSON string
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat())
    
    # Relationships
    playlist_items = relationship("PlaylistItem", back_populates="media", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Media(id={self.id}, name={self.name}, type={self.type})>"
    
    @property
    def planet_options_dict(self) -> Optional[Dict[str, Any]]:
        """Return planet_options as a Python dict."""
        if not self.planet_options:
            return None
        try:
            return json.loads(self.planet_options)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in planet_options for media {self.id}")
            return None
    
    @planet_options_dict.setter
    def planet_options_dict(self, value: Dict[str, Any]):
        """Set planet_options from a Python dict."""
        if value is None:
            self.planet_options = None
        else:
            self.planet_options = json.dumps(value)


class PlaylistItem(Base):
    """Item in the playlist queue."""
    __tablename__ = "playlist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    position = Column(Integer, nullable=False)
    status = Column(String, nullable=False)  # unplayed, playing, played, paused
    elapsed_time = Column(Float, default=0.0)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat())
    
    # Relationships
    media = relationship("Media", back_populates="playlist_items")
    
    def __repr__(self):
        return f"<PlaylistItem(id={self.id}, media_id={self.media_id}, position={self.position}, status={self.status})>"


class Settings(Base):
    """Application settings stored as a single row."""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, default=1)
    autoplay = Column(Integer, default=1)
    autostart = Column(Integer, default=1)
    loop = Column(Integer, default=1)
    red_brightness = Column(Integer, default=255)
    green_brightness = Column(Integer, default=255)
    blue_brightness = Column(Integer, default=255)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat())
    
    def __repr__(self):
        return f"<Settings(id={self.id})>"


class NetworkConfig(Base):
    """Network configuration stored as a single row."""
    __tablename__ = "network_config"
    
    id = Column(Integer, primary_key=True, default=1)
    external_ssid = Column(String, nullable=True)
    external_password = Column(String, nullable=True)
    updated_at = Column(String, default=lambda: datetime.now().isoformat())
    
    def __repr__(self):
        return f"<NetworkConfig(id={self.id}, external_ssid={self.external_ssid})>"


class ErrorLog(Base):
    """Error log entries."""
    __tablename__ = "errors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, default=lambda: datetime.now().isoformat())
    endpoint = Column(String)
    message = Column(String)
    stacktrace = Column(String)
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, endpoint={self.endpoint})>"


# Update table triggers for updated_at timestamps
@event.listens_for(Media, 'before_update')
def update_media_timestamp(mapper, connection, target):
    target.updated_at = datetime.now().isoformat()

@event.listens_for(PlaylistItem, 'before_update')
def update_playlist_item_timestamp(mapper, connection, target):
    target.updated_at = datetime.now().isoformat()

@event.listens_for(Settings, 'before_update')
def update_settings_timestamp(mapper, connection, target):
    target.updated_at = datetime.now().isoformat()

@event.listens_for(NetworkConfig, 'before_update')
def update_network_config_timestamp(mapper, connection, target):
    target.updated_at = datetime.now().isoformat()



