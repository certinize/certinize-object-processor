import typing

import fastapi
from starlette import requests

from app import models, services
from app.api.dependencies import tempaltes

router = fastapi.APIRouter(prefix="/templates")


@router.post("", status_code=201)
async def add_certificate_template(
    _: requests.Request,
    template: models.TemplateUpload,
    imagekit_client: services.ImageKitClient = fastapi.Depends(
        tempaltes.get_imagekit_client
    ),
) -> dict[str, typing.Any]:
    return await imagekit_client.upload_file(
        file=template.fileb,
        file_name=template.filename,
        options=template.options,
    )
