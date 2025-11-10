from sqlmodel import Session, SQLModel, select
from collections.abc import Generator
from app.core.db import engine
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from app.core.security import get_current_user_id
from app import crud
from app.models import User

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def get_current_user(
    session: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[str, Depends(get_current_user_id)]
) -> User:
    """
    Get current authenticated user
    """
    user = crud.get_user_by_id(session=session, user_id=current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current active user (alias for get_current_user since it already checks is_active)
    """
    return current_user

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]