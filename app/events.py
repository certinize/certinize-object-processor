import typing

import aiohttp
import fastapi
import orjson

from app import services
from app.config import settings


async def create_imagekit_client(app: fastapi.FastAPI) -> None:
    app.state.imagekit_client = services.ImageKitClient(
        private_key=settings.imagekit_private_key,
        public_key=settings.imagekit_public_key,
        url_endpoint=settings.imagekit_endpoint_url,
    )
    app.state.imagekit_client_session = app.state.imagekit_client.session


async def create_image_processor(app: fastapi.FastAPI) -> None:
    app.state.image_processor = services.ImageProcessor()


async def create_http_client_session(app: fastapi.FastAPI) -> None:
    app.state.http_client = aiohttp.ClientSession(
        json_serialize=lambda json_: orjson.dumps(  # pylint: disable=E1101
            json_
        ).decode(),
    )


async def create_gdrive_client(app: fastapi.FastAPI) -> None:
    app.state.gdrive = services.GoogleDriveClient(
        client_json_file_path="certinize-gdrive-client.json"
    )


async def dispose_imagekit_client(app: fastapi.FastAPI) -> None:
    if isinstance(app.state.imagekit_client_session, aiohttp.ClientSession):
        await app.state.imagekit_client_session.close()


async def dispose_http_client_session(app: fastapi.FastAPI) -> None:
    if isinstance(app.state.http_client, aiohttp.ClientSession):
        await app.state.http_client.close()


def create_start_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def start_app() -> None:
        await create_http_client_session(app)
        await create_imagekit_client(app)
        await create_image_processor(app)
        await create_gdrive_client(app)

    return start_app


def create_stop_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def stop_app() -> None:
        await dispose_http_client_session(app)
        await dispose_imagekit_client(app)

    return stop_app
