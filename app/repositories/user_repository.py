from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import User, RefreshToken, CustomerLocation


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_users_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role.upper())
        if search:
            query = query.filter(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))

        total = query.count()
        offset = (page - 1) * limit
        users = query.order_by(User.joined_at.desc()).offset(offset).limit(limit).all()
        return users, total

    # Refresh tokens
    def save_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_refresh_token(self, token_hash: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        ).first()

    def revoke_refresh_token(self, token_hash: str) -> bool:
        token = self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if token:
            token.revoked = True
            self.db.commit()
            return True
        return False

    # Customer location
    def get_customer_location(self, user_id: str) -> Optional[CustomerLocation]:
        return self.db.query(CustomerLocation).filter(CustomerLocation.user_id == user_id).first()

    def save_customer_location(self, location: CustomerLocation) -> CustomerLocation:
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location
