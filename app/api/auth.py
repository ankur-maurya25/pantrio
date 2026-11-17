from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    AuthResponse,
    TokenRefreshResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ForgotPasswordResponse
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(req)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(req)


@router.post("/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh(req)


@router.post("/logout", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def logout(req: LogoutRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(req)
    return SuccessResponse(success=True)


@router.post("/forgot-password", response_model=ForgotPasswordResponse, status_code=status.HTTP_200_OK)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.forgot_password(req)


@router.post("/reset-password", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.reset_password(req)
