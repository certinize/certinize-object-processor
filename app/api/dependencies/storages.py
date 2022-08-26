import types_aiobotocore_s3
from starlette import requests as requests_

from app import services


async def get_filebase_client(requests: requests_.Request) -> services.FilebaseClient:
    return requests.app.state.filebase_client


async def get_s3_client(requests: requests_.Request) -> types_aiobotocore_s3.S3Client:
    return requests.app.state.s3_client
