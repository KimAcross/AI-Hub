"""Main API v1 router that combines all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.assistants import router as assistants_router
from app.api.v1.audit import router as audit_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.files import router as files_router
from app.api.v1.health import router as health_router
from app.api.v1.models import router as models_router
from app.api.v1.quotas import router as quotas_router
from app.api.v1.settings import router as settings_router
from app.api.v1.users import auth_router, router as users_router

# Create main v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(health_router)
api_router.include_router(assistants_router)
api_router.include_router(files_router)
api_router.include_router(conversations_router)
api_router.include_router(models_router)
api_router.include_router(settings_router)
api_router.include_router(admin_router)

# Admin management routers
api_router.include_router(users_router)
api_router.include_router(api_keys_router)
api_router.include_router(quotas_router)
api_router.include_router(audit_router)

# User authentication router
api_router.include_router(auth_router)
