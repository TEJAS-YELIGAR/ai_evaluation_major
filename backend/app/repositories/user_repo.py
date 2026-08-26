from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create(db: Session, username: str, full_name: str, password: str, role: str):
    user = User(
        username=username,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all(db: Session):
    return db.query(User).all()

def get_all_evaluators(db: Session):
    return db.query(User).filter(User.role == 'evaluator').all()