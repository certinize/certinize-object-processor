import fastapi

router = fastapi.APIRouter(prefix="/healthz")


@router.get("/")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
