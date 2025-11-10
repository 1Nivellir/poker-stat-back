from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import jwt
from app.core.config import settings
from app.core.security import ALGORITHM, verify_token
from app.models import TokenPayload
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки JWT токенов на защищенных роутах
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Роуты которые НЕ требуют аутентификации
        self.excluded_paths = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/v1/auth/login",
            "/v1/auth/refresh-token",
            "/v1/auth/register",
            "/health",
            "/",
        }
        
        # Префиксы путей которые НЕ требуют аутентификации
        self.excluded_prefixes = [
            "/static/",
            "/favicon.ico",
        ]
    
    def _is_excluded_path(self, path: str) -> bool:
        """Проверяет нужно ли исключить путь из проверки токена"""
        # Точные совпадения
        if path in self.excluded_paths:
            return True
        
        # Проверка префиксов
        for prefix in self.excluded_prefixes:
            if path.startswith(prefix):
                return True
                
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Обрабатывает каждый HTTP запрос"""
        
        # Пропускаем исключенные пути
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Проверяем наличие токена
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header is required"}
            )
        
        # Проверяем формат токена (Bearer token)
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format. Use 'Bearer <token>'"}
            )
        
        # Верифицируем токен
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenPayload(**payload)
            
            if not token_data.sub:
                raise jwt.InvalidTokenError("Token missing subject")
                
            # Добавляем user_id в состояние запроса для использования в роутах
            request.state.user_id = token_data.sub
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired"}
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"}
            )
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token validation failed"}
            )
        
        # Продолжаем обработку запроса
        response = await call_next(request)
        return response

class OptionalAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для опциональной аутентификации
    Проверяет токен если он есть, но не требует его обязательного наличия
    """
    
    async def dispatch(self, request: Request, call_next):
        """Обрабатывает каждый HTTP запрос"""
        
        authorization = request.headers.get("Authorization")
        
        if authorization:
            try:
                scheme, token = authorization.split()
                if scheme.lower() == "bearer":
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
                    token_data = TokenPayload(**payload)
                    
                    if token_data.sub:
                        request.state.user_id = token_data.sub
                        request.state.authenticated = True
                    else:
                        request.state.authenticated = False
                else:
                    request.state.authenticated = False
            except (jwt.InvalidTokenError, ValueError, jwt.ExpiredSignatureError):
                request.state.authenticated = False
        else:
            request.state.authenticated = False
        
        response = await call_next(request)
        return response 