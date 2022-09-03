import contextlib
import typing

import aiohttp
import fastapi
import orjson
from aiobotocore import session

from app import services
from app.config import settings


async def create_imagekit_client(app: fastapi.FastAPI) -> None:
    app.state.imagekit_client = services.ImageKitClient(
        private_key=settings.imagekit_private_key,
        public_key=settings.imagekit_public_key,
        url_endpoint=settings.imagekit_endpoint_url,
    )
    app.state.imagekit_client_session = app.state.imagekit_client.session


async def dispose_imagekit_client(app: fastapi.FastAPI) -> None:
    if isinstance(app.state.imagekit_client_session, aiohttp.ClientSession):
        await app.state.imagekit_client_session.close()


async def create_image_processor(app: fastapi.FastAPI) -> None:
    app.state.image_processor = services.ImageProcessor()


async def create_http_client_session(app: fastapi.FastAPI) -> None:
    app.state.http_client = aiohttp.ClientSession(
        json_serialize=lambda json_: orjson.dumps(  # pylint: disable=E1101
            json_
        ).decode(),
    )


async def dispose_http_client_session(app: fastapi.FastAPI) -> None:
    if isinstance(app.state.http_client, aiohttp.ClientSession):
        await app.state.http_client.close()


async def create_gdrive_client(app: fastapi.FastAPI) -> None:
    app.state.gdrive = services.GoogleDriveClient(
        client_json_file_path="certinize-gdrive-client.json"
    )


async def create_s3_client_interface(app: fastapi.FastAPI) -> None:
    app.state.s3_client_interface = services.S3Client()


async def create_filebase_s3_client(app: fastapi.FastAPI) -> None:
    exit_stack = contextlib.AsyncExitStack()
    app.state.filebase_client_session = services.S3ClientSession(
        bucket_name=settings.filebase_s3_bucket,
        exit_stack=exit_stack,
        s3client=await exit_stack.enter_async_context(
            session.AioSession().create_client(  # type: ignore
                "s3",
                endpoint_url=settings.filebase_s3_api_endpoint_url,
                aws_secret_access_key=settings.filebase_s3_secret_access_key,
                aws_access_key_id=settings.filebase_s3_access_key_id,
            )
        ),
    )


async def dispose_filebase_s3_client(app: fastapi.FastAPI) -> None:
    if isinstance(
        app.state.filebase_client_session.exit_stack, contextlib.AsyncExitStack
    ):
        await app.state.filebase_client_session.exit_stack.aclose()


async def create_storj_s3_client(app: fastapi.FastAPI) -> None:
    exit_stack = contextlib.AsyncExitStack()
    app.state.storj_client_session = services.S3ClientSession(
        bucket_name=settings.storj_s3_bucket,
        exit_stack=exit_stack,
        s3client=await exit_stack.enter_async_context(
            session.AioSession().create_client(  # type: ignore
                "s3",
                endpoint_url=settings.storj_s3_api_endpoint_url,
                aws_secret_access_key=settings.storj_s3_secret_access_key,
                aws_access_key_id=settings.storj_s3_access_key_id,
            )
        ),
    )


async def dispose_storj_s3_client(app: fastapi.FastAPI) -> None:
    if isinstance(app.state.storj_client_session.exit_stack, contextlib.AsyncExitStack):
        await app.state.storj_client_session.exit_stack.aclose()


async def create_nft_storage_client(app: fastapi.FastAPI) -> None:
    app.state.nft_storage_client = services.NftStorageClient(
        nft_storage_api=settings.nft_storage_api_endpoint_url,
        api_key=settings.nft_storage_api_key,
    )


def create_start_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def start_app() -> None:
        await create_http_client_session(app)
        await create_imagekit_client(app)
        await create_image_processor(app)
        await create_gdrive_client(app)
        await create_s3_client_interface(app)
        await create_filebase_s3_client(app)
        await create_storj_s3_client(app)
        await create_nft_storage_client(app)

    return start_app


def create_stop_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def stop_app() -> None:
        await dispose_http_client_session(app)
        await dispose_imagekit_client(app)
        await dispose_filebase_s3_client(app)
        await dispose_storj_s3_client(app)

    return stop_app
