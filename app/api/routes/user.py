from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import SessionDep
from app.models import Message, UserPublic, UserUpdate
from app import crud
from app.api.deps import get_current_user
router = APIRouter(tags=["user"])

@router.delete('/{user_id}', response_model=Message)
def delete_user(user_id: str, session: SessionDep):
    """
    Delete user
    """
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(session=session, user_id=user_id)
    return {"message": "User deleted successfully"}


@router.get("/me", response_model=UserPublic)
def get_me(current_user: Annotated[Any, Depends(get_current_user)]) -> Any:
    """
    Get current user info
    """
    return current_user


@router.put("/me", response_model=UserPublic)
def update_me(current_user: Annotated[Any, Depends(get_current_user)], user_update: UserUpdate):
    """
    Update current user info
    """
    return current_user