from fastapi import APIRouter

from app.api.endpoints import auth, components, curricula, departments, programs, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(departments.router, tags=["departments"])
api_router.include_router(programs.router, tags=["programs"])
api_router.include_router(curricula.router, tags=["curricula"])
api_router.include_router(components.router, tags=["components"])
