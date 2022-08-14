from starlette import requests

from app import services


def get_imagekit_client(requests: requests.Request) -> services.ImageKitClient:
    return requests.app.state.imagekit_client
