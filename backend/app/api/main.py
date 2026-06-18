from fastapi import APIRouter

from app.api.routes import admin, games, itch_auth, moderation, newsletter, tags, users, utils

api_router = APIRouter()
api_router.include_router(itch_auth.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(games.router)
api_router.include_router(newsletter.router)
api_router.include_router(tags.router)
api_router.include_router(moderation.router)
api_router.include_router(admin.router)
