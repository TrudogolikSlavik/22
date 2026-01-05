import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

# Simple in-memory session storage (use Redis in production)
sessions: Dict[str, dict] = {}


def create_session(user_id: int, email: str) -> str:
    """Create session for user"""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user_id": user_id,
        "email": email,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Get session by ID"""
    if session_id not in sessions:
        return None

    session = sessions[session_id]
    if datetime.now() > session["expires_at"]:
        del sessions[session_id]
        return None

    return session


def delete_session(session_id: str):
    """Delete session"""
    if session_id in sessions:
        del sessions[session_id]
