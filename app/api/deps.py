from typing import Callable, Generator
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import User
from app.repositories.user_repository import UserRepository

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication required. Missing Bearer token.")

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token subject.")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User not found.")

    if user.status == "SUSPENDED":
        raise ForbiddenException("User account has been suspended.")

    return user


def require_role(*allowed_roles: str) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.upper()
        allowed = [r.upper() for r in allowed_roles]
        if user_role not in allowed and "ADMIN" not in allowed:  # Admins can access if permitted
            if user_role != "ADMIN":
                raise ForbiddenException(f"Role '{current_user.role}' is not authorized for this resource.")
        elif user_role not in allowed:
            raise ForbiddenException(f"Role '{current_user.role}' is not authorized for this resource.")
        return current_user

    return role_checker
