"""User API schemas for requests and responses."""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


def validate_password_strength(password: str) -> str:
    """Validate password meets strength requirements."""
    errors = []
    if not re.search(r"[A-Z]", password):
        errors.append("at least 1 uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("at least 1 lowercase letter")
    if not re.search(r"\d", password):
        errors.append("at least 1 digit")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        errors.append("at least 1 special character")
    if errors:
        raise ValueError(f"Password must contain {', '.join(errors)}")
    return password


# Request schemas
class UserCreate(BaseModel):
    """Request schema for creating a user."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    name: str = Field(..., min_length=2, max_length=100, description="User's display name")
    role: UserRole = Field(default=UserRole.USER, description="User's role")

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    """Request schema for updating a user."""

    email: Optional[EmailStr] = Field(None, description="New email address")
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="New display name")
    role: Optional[UserRole] = Field(None, description="New role")


class UserPasswordChange(BaseModel):
    """Request schema for changing a user's password."""

    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


# Response schemas
class UserResponse(BaseModel):
    """Response schema for a user."""

    id: UUID = Field(description="User's unique ID")
    email: str = Field(description="User's email address")
    name: str = Field(description="User's display name")
    role: UserRole = Field(description="User's role")
    is_active: bool = Field(description="Whether the user is active")
    is_verified: bool = Field(description="Whether the user is verified")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(description="Account creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = {"from_attributes": True}


class UserLoginResponse(BaseModel):
    """Response schema for user login."""

    token: str = Field(description="JWT session token")
    expires_at: datetime = Field(description="Token expiration timestamp")
    csrf_token: str = Field(description="CSRF token for state-changing requests")
    user: UserResponse = Field(description="Logged in user details")


class UserListResponse(BaseModel):
    """Response schema for paginated user list."""

    users: list[UserResponse] = Field(description="List of users")
    total: int = Field(description="Total number of users matching filters")
    page: int = Field(description="Current page number")
    size: int = Field(description="Page size")
    pages: int = Field(description="Total number of pages")


# User API Key schemas
class UserApiKeyCreate(BaseModel):
    """Request schema for creating a user API key."""

    name: str = Field(..., min_length=1, max_length=100, description="Name for the API key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days")


class UserApiKeyResponse(BaseModel):
    """Response schema for a user API key."""

    id: UUID = Field(description="API key's unique ID")
    name: str = Field(description="API key name")
    key_prefix: str = Field(description="First 8 characters for identification")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    is_active: bool = Field(description="Whether the key is active")
    created_at: datetime = Field(description="Creation timestamp")

    model_config = {"from_attributes": True}


class UserApiKeyCreateResponse(UserApiKeyResponse):
    """Response schema for creating a user API key (includes the key itself)."""

    key: str = Field(description="The API key (only shown once)")
