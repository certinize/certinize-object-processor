from starlette import requests as requests_

from app import services


def get_imagekit_client(requests: requests_.Request) -> services.ImageKitClient:
    return requests.app.state.imagekit_client
