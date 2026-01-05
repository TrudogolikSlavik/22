import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password
from app.core.sessions import create_session, delete_session, get_session
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class LoginRequest(BaseModel):
    email: str
    password: str


def get_current_user_web(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user for web interface"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    session = get_session(session_id)
    if not session:
        return None

    user = db.query(User).filter(User.id == session["user_id"]).first()
    return user


@router.post("/web-login")
async def web_login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login through web interface"""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create session
    session_id = create_session(user.id, user.email)

    # Set cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=24 * 60 * 60,  # 24 hours
        secure=False,  # Should be True in production
        samesite="lax"
    )

    return {"message": "Login successful", "user_id": user.id}


@router.post("/web-logout")
async def web_logout(response: Response, request: Request):
    """Logout from system"""
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)

    response.delete_cookie("session_id")
    return {"message": "Logout successful"}
