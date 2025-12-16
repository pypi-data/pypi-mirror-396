from enum import Enum
from typing import Optional, List, Annotated
from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, root_validator, validator, Field
from fastapi import Query

class LocaleEnum(str, Enum):
    en = "en"
    de = "de"

class RoleEnum(str, Enum):
    SUPER_ADMIN = "Super Admin"
    ADMIN = "Admin"
    USER = "User"

class EmailNormalizationMixin(BaseModel):
    """Mixin that automatically normalizes email fields."""

    @validator('email', pre=False, check_fields=False)
    def normalize_email_post(cls, v):
        """Normalize email after EmailStr validation to ensure full lowercase."""
        if v is None:
            return v
        return str(v).lower()


class PasswordPolicy(BaseModel):
    """Serializable password policy definition shared between backend and frontend."""

    min_length: int = 12
    require_digit: bool = True
    require_special: bool = True
    require_lowercase: bool = True
    require_uppercase: bool = True
    special_characters: str = "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?"
    special_characters_pattern: str = r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]"

    def collect_errors(self, password: str) -> List[str]:
        errors: List[str] = []

        if self.min_length and len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")

        if self.require_digit and not re.search(r"\d", password):
            errors.append("Password must contain at least 1 digit")

        if self.require_special and not re.search(self.special_characters_pattern, password):
            errors.append("Password must contain at least 1 special character")

        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least 1 lowercase letter")

        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least 1 uppercase letter")

        return errors


DEFAULT_PASSWORD_POLICY = PasswordPolicy()


def validate_password(password: Optional[str], policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY) -> List[str]:
    if password is None:
        return []
    return policy.collect_errors(password)


def enforce_password_policy(password: Optional[str], policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY) -> Optional[str]:
    if password is None:
        return password

    errors = validate_password(password, policy)
    if errors:
        raise ValueError(". ".join(errors))

    return password


def get_password_policy() -> PasswordPolicy:
    return DEFAULT_PASSWORD_POLICY

def validate_password_value(v):
    """Validate password meets security requirements and raise ValueError if invalid."""
    return enforce_password_policy(v)

class SignupRequest(EmailNormalizationMixin):
    username: str
    email: EmailStr
    locale: Optional[LocaleEnum] = LocaleEnum.en  # Default is 'en', but can be 'de'
    role: RoleEnum = RoleEnum.USER
    
class SignUpResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class LoginRequest(EmailNormalizationMixin):
    email: EmailStr
    password: str
    locale: Optional[LocaleEnum] = LocaleEnum.en
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class ForgotPasswordRequest(EmailNormalizationMixin):
    email: EmailStr
    locale: Optional[LocaleEnum] = LocaleEnum.en  # Default is 'en', but can be 'de'
    
class ResetPasswordRequest(EmailNormalizationMixin):
    email: EmailStr
    new_password: str
    otp: Optional[str] = None
    old_password: Optional[str] = None
    locale: Optional[str] = LocaleEnum.en
    
    @validator('new_password')
    def validate_new_password(cls, v):
        return validate_password_value(v)
    
    @root_validator
    def check_reset_method(cls, values):
        """Ensure that either OTP or old_password is provided, but not both."""
        otp = values.get('otp')
        old_password = values.get('old_password')
        
        if bool(otp) == bool(old_password):  # Both are provided or both are missing
            raise ValueError("Exactly one of 'otp' or 'old_password' must be provided")
            
        return values

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ApiKeyCreateInput(BaseModel):
    name: str

class ApiKeyCreateResponse(BaseModel):
    api_key: str

class ApiKeySort(str, Enum):
    ID = 'id'
    NAME = 'name'
    ROLE = 'role'
    EXPIRES_AT = 'expires_at'
    LAST_USED = 'last_used'

class ApiKeySearch(str, Enum):
    ID = 'id'
    NAME = 'name'
    ROLE = 'role'

class ApiKeyFilter(BaseModel):
    id__eq: Optional[str] = Field(None, description="Filter by API Key ID (exact match)")
    id__ilike: Optional[str] = Field(None, description="Filter by API Key ID (partial match)")
    name__eq: Optional[str] = Field(None, description="Filter by API Key name (exact match)")
    name__ilike: Optional[str] = Field(None, description="Filter by API Key name (partial match)")
    role__eq: Optional[str] = Field(None, description="Filter by role (exact match)")
    role__in: Optional[Annotated[List[str], Query(None, description="Filter by multiple roles")]] = None
    expires_at__gte: Optional[datetime] = Field(None, description="Filter by expires_at (greater than or equal)")
    expires_at__lte: Optional[datetime] = Field(None, description="Filter by expires_at (less than or equal)")
    last_used__gte: Optional[datetime] = Field(None, description="Filter by last_used (greater than or equal)")
    last_used__lte: Optional[datetime] = Field(None, description="Filter by last_used (less than or equal)")

    class Config:
        extra = "forbid"

class ApiKeyInfo(BaseModel):
    id: int
    name: str
    api_key: str
    role: RoleEnum
    expires_at: datetime
    last_used: Optional[datetime]

class ApiKeysGetResponse(BaseModel):
    api_keys: List[ApiKeyInfo]

class ApiKeyDeleteResponse(BaseModel):
    message: str
    deleted_key: str
    deleted_key_id: int
    deleted_key_name: str
class UserUpdateRequest(EmailNormalizationMixin):
    email: EmailStr | None = None
    user_id: int | None = None
    username: str | None = None
    role: RoleEnum | None = None
    
class UserUpdateResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
class PasswordPolicyResponse(BaseModel):
    min_length: int
    require_digit: bool
    require_special: bool
    require_lowercase: bool
    require_uppercase: bool
    special_characters: str
    special_characters_pattern: str
