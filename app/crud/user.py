from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for users"""

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, user_data: UserCreate) -> User:
        """Create new user"""
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            is_active=user_data.is_active
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(
        self,
        db: Session,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[User]:
        """Update user"""
        user = self.get_by_id(db, user_id)
        if user:
            update_data = user_data.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["password_hash"] = get_password_hash(
                    update_data.pop("password")
                )

            for field, value in update_data.items():
                setattr(user, field, value)

            db.commit()
            db.refresh(user)
        return user

    def delete(self, db: Session, user_id: int) -> bool:
        """Delete user"""
        user = self.get_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False


crud_user = CRUDUser()
