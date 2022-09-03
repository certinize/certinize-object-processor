import aiohttp
from starlette import requests as requests_

from app import services


async def get_s3_client_interface(requests: requests_.Request) -> services.S3Client:
    return requests.app.state.s3_client_interface


async def get_filebase_s3_client(
    requests: requests_.Request,
) -> services.S3ClientSession:
    return requests.app.state.filebase_client_session


async def get_storj_s3_client(
    requests: requests_.Request,
) -> services.S3ClientSession:
    return requests.app.state.storj_client_session


async def get_http_client(requests: requests_.Request) -> aiohttp.ClientSession:
    return requests.app.state.http_client


async def get_nft_storage_client(requests: requests_.Request) -> aiohttp.ClientSession:
    return requests.app.state.nft_storage_client
