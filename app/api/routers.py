import fastapi

from app.api.endpoints import certificates, storages, templates

router = fastapi.APIRouter()
router.include_router(templates.router)
router.include_router(certificates.router)
router.include_router(storages.router)
