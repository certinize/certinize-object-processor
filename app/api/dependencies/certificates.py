from starlette import requests as requests_

from app import services


async def get_image_processor(requests: requests_.Request) -> services.ImageProcessor:
    return requests.app.state.image_processor


async def get_imagekit_client(requests: requests_.Request) -> services.ImageKitClient:
    return requests.app.state.imagekit_client


async def get_gdrive_client(requests: requests_.Request) -> services.GoogleDriveClient:
    return requests.app.state.gdrive
