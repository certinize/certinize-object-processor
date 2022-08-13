import fastapi

from app import endpoints

router = fastapi.APIRouter()
router.include_router(endpoints.router)