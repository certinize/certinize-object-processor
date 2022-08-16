import fastapi
import orjson
from starlette import requests

from app import services
from app.api.dependencies import tempaltes

router = fastapi.APIRouter(prefix="/templates")


@router.post("", status_code=201)
async def add_certificate_template(
    _: requests.Request,
    filename: str = fastapi.Form(),
    options: str = fastapi.Form(),
    fileb: fastapi.UploadFile = fastapi.File(),
    imagekit_client: services.ImageKitClient = fastapi.Depends(
        tempaltes.get_imagekit_client
    ),
):
    return await imagekit_client.upload_file(
        file=fileb.file.read(), file_name=filename, options=orjson.loads(options)
    )
