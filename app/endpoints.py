import fastapi
import services

router = fastapi.APIRouter(prefix="/certificates")


@router.post("")
async def process_image(
    image_processor: services.ImageProcessor = fastapi.Depends(services.ImageProcessor),
):
    # fetch e-Certificate template from its repository
    # generate e-Certificate
    # upload to file to cloud storage
    # return url of generated e-Certificate
    ...
