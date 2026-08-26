from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    full_name: str
    password: str
    role: str = "evaluator"  # default role is evaluator

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