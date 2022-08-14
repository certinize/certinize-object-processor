import typing

import fastapi

from app import services
from app.api.dependencies import certificates

router = fastapi.APIRouter(prefix="/certificates")


@router.post("/")
async def generate_ecertificate(
    image_file: bytes = fastapi.File(),
    image_processor: services.ImageProcessor = fastapi.Depends(
        certificates.get_image_processor
    ),
    imagekit_client: services.ImageKitClient = fastapi.Depends(
        certificates.get_imagekit_client
    ),
) -> dict[str, typing.Any]:
    # fetch e-Certificate template from its repository
    # generate e-Certificate
    # upload to file to cloud storage
    # return url of generated e-Certificate

    return {}
