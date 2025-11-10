from fastapi import APIRouter

from app.api.routes import tourney, auth, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(user.router, prefix="/user")
api_router.include_router(tourney.router)