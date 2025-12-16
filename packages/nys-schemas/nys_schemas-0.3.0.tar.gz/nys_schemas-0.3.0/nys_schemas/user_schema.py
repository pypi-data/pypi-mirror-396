from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated, List
from nys_schemas.auth_schema import RoleEnum
from fastapi import Query
from enum import Enum

class UserSort(str, Enum):
    USERNAME = 'username'
    EMAIL = 'email'
    ROLE = 'role'
    PASSWORD_EXPIRES_AT = 'password_expires_at'
    OTP_EXPIRES_AT = 'otp_expires_at'

class UserSearch(str, Enum):
    ID = 'id'
    USERNAME = 'username'
    EMAIL = 'email'
    ROLE = 'role'

class UserFilter(BaseModel):
    id__eq: Optional[str] = Field(None, description="Filter by User ID (exact match)")
    id__ilike: Optional[str] = Field(None, description="Filter by User ID (partial match)")
    username__eq: Optional[str] = Field(None, description="Filter by username (exact match)")
    username__ilike: Optional[str] = Field(None, description="Filter by username (partial match)")
    email__eq: Optional[str] = Field(None, description="Filter by email (exact match)")
    email__ilike: Optional[str] = Field(None, description="Filter by email (partial match)")
    role__eq: Optional[str] = Field(None, description="Filter by role (exact match)")
    role__in: Optional[Annotated[List[str], Query(None, description="Filter by multiple roles")]] = None
    password_expires_at__gte: Optional[datetime] = Field(None, description="Filter by password_expires_at (greater than or equal)")
    password_expires_at__lte: Optional[datetime] = Field(None, description="Filter by password_expires_at (less than or equal)")
    otp_expires_at__gte: Optional[datetime] = Field(None, description="Filter by otp_expires_at (greater than or equal)")
    otp_expires_at__lte: Optional[datetime] = Field(None, description="Filter by otp_expires_at (less than or equal)")

    class Config:
        extra = "forbid"

class UserSchema(BaseModel):
    id: Optional[int]
    username: str
    email: EmailStr
    role: RoleEnum
    password_expires_at: Optional[datetime] = None
    otp: Optional[str] = None
    otp_expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        """Create UserSchema from ORM object, mapping idx to id."""
        return cls(
            id=obj.idx,
            username=obj.username,
            email=obj.email,
            role=obj.role,
            password_expires_at=obj.password_expires_at,
            otp=obj.otp,
            otp_expires_at=obj.otp_expires_at,
        )
