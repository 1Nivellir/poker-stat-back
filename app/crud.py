import uuid
from typing import Union

from sqlmodel import Session, select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from app.models import User, UserCreate, UserRegister

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_user(*, session: Session, user_create: Union[UserCreate, UserRegister]) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user

def get_user_by_id(*, session: Session, user_id: str) -> User | None:
    statement = select(User).where(User.id == uuid.UUID(user_id))
    session_user = session.exec(statement).first()
    return session_user