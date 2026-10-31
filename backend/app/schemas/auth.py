from pydantic import BaseModel
from pydantic import field_validator

from app.utils.validation import validate_full_name

class RegisterRequest(BaseModel):
    username: str
    full_name: str
    password: str
    role: str = "evaluator"  # default role is evaluator

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return validate_full_name(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return value

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

    class Config:
        from_attributes = True