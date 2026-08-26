from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_admin
from app.repositories import user_repo
from app.services import auth_service
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account. Role can be: admin or evaluator"""
    return auth_service.register_user(
        db=db,
        username=request.username,
        full_name=request.full_name,
        password=request.password,
        role=request.role
    )

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    Returns JWT token — use in all future requests.
    """
    return auth_service.login_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    """Returns currently logged in user info."""
    return current_user


@router.get("/evaluators")
def list_evaluators(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    """List all evaluator accounts. Admin only."""
    return user_repo.get_all_evaluators(db)