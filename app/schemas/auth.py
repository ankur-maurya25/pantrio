from typing import Optional
from pydantic import EmailStr
from app.schemas.common import CamelModel


class RegisterRequest(CamelModel):
    name: str
    email: EmailStr
    password: str
    role: str = "CUSTOMER"
    location: Optional[str] = "Mainpuri"


class LoginRequest(CamelModel):
    email: EmailStr
    password: str


class RefreshRequest(CamelModel):
    refresh_token: str


class LogoutRequest(CamelModel):
    refresh_token: str


class UserResponse(CamelModel):
    id: str
    name: str
    email: str
    role: str
    joined_at: str
    status: str
    activity_metric: str = "0 orders placed"
    version: int = 1
    location: Optional[str] = "Mainpuri"


class AuthResponse(CamelModel):
    access_token: str
    refresh_token: str
    expires_in: int = 900
    user: UserResponse


class TokenRefreshResponse(CamelModel):
    access_token: str
    refresh_token: str
    expires_in: int = 900


class ForgotPasswordRequest(CamelModel):
    email: EmailStr


class ResetPasswordRequest(CamelModel):
    email: EmailStr
    new_password: str
    otp: Optional[str] = None


class ForgotPasswordResponse(CamelModel):
    success: bool = True
    message: str = "Password reset code sent successfully."
    otp: Optional[str] = None
