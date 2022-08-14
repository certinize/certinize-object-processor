import typing

import aiohttp
import fastapi

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
    app.state.image_porcessor = services.ImageProcessor()


async def dispose_imagekit_client(app: fastapi.FastAPI) -> None:
    if isinstance(app.state.imagekit_client_session, aiohttp.ClientSession):
        await app.state.imagekit_client_session.close()


def create_start_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def start_app() -> None:
        await create_imagekit_client(app)
        await create_image_processor(app)

    return start_app


def create_stop_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def stop_app() -> None:
        await dispose_imagekit_client(app)

    return stop_app
