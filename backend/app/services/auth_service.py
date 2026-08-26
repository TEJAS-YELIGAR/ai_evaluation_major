from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.core.security import verify_password, create_access_token
from fastapi import HTTPException

def register_user(db: Session, username: str, full_name: str, password: str, role: str):
    # Check if username already exists
    existing = user_repo.get_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Validate role
    if role not in ("admin", "evaluator"):
        raise HTTPException(status_code=400, detail="Role must be admin or evaluator")

    # Create user
    user = user_repo.create(db, username, full_name, password, role)
    return user

def login_user(db: Session, username: str, password: str):
    # Find user
    user = user_repo.get_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Check password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token
    token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role,
        "username": user.username
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name
    }