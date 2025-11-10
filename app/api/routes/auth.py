from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_refresh_token
from app.models import Token, TokenWithRefresh, RefreshTokenRequest, UserPublic, UserRegister, UserLogin, Message
from app.api.deps import get_current_user


router = APIRouter(tags=["auth"])

@router.post('/register', response_model=UserPublic)
def create_user(user_in: UserRegister, session: SessionDep):
    """
    Регистрация нового пользователя
    """
    # Проверяем, что пользователь с таким email не существует
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует в системе.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    return user

@router.post("/login", response_model=TokenWithRefresh)
def login_json(user_login: UserLogin, session: SessionDep):
		"""
		Вход с JSON: {"email": "...", "password": "..."}
		"""
		user = crud.get_user_by_email(session=session, email=user_login.email)
		if not user:
			raise HTTPException(status_code=401, detail="Неверный email или пароль")
		if not verify_password(user_login.password, user.hashed_password):
			raise HTTPException(status_code=401, detail="Неверный email или пароль")
		
		access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
		access_token = create_access_token(user.id, expires_delta=access_token_expires)
		
		refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
		refresh_token = create_refresh_token(user.id, expires_delta=refresh_token_expires)
		
		return {
			"access_token": access_token, 
			"refresh_token": refresh_token,
			"token_type": "bearer"
		}

@router.post("/login/form", response_model=TokenWithRefresh)
def login_form(
		form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
		session: SessionDep,
    ):
		"""
		OAuth2 compatible token login (для Swagger UI).
		Использует form-data: username (email) и password
		"""
		user = crud.get_user_by_email(session=session, email=form_data.username)
		if not user:
			raise HTTPException(status_code=401, detail="Incorrect username or password")
		if not verify_password(form_data.password, user.hashed_password):
			raise HTTPException(status_code=401, detail="Incorrect username or password")
		
		access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
		access_token = create_access_token(user.id, expires_delta=access_token_expires)
		
		refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
		refresh_token = create_refresh_token(user.id, expires_delta=refresh_token_expires)
		
		return {
			"access_token": access_token, 
			"refresh_token": refresh_token,
			"token_type": "bearer"
		}

@router.post('/refresh-token', response_model=Token)
def refresh_token(
    request: RefreshTokenRequest | None = None,
    refresh_token: str | None = None
):
    """
    Refresh access token using refresh token.
    Accepts token either in request body or as query parameter.
    """
    # Get token from body or query parameter
    token = None
    if request and request.refresh_token:
        token = request.refresh_token
    elif refresh_token:
        token = refresh_token
    
    if not token:
        raise HTTPException(
            status_code=422,
            detail="refresh_token is required either in request body or as query parameter"
        )
    
    user_id = verify_refresh_token(token)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Неверный или просроченный токен обновления"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(user_id, expires_delta=access_token_expires)
    
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post('/logout', response_model=Message)
def logout(current_user: Annotated[Any, Depends(get_current_user)]):
    """
    Logout current user
    """
    return {"message": "User logged out successfully"}

