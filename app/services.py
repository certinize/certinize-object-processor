"""
app.services
~~~~~~~~~~~~
"""
import asyncio
import base64
import dataclasses
import io
import typing

import aiohttp
import orjson
from PIL import Image, ImageDraw, ImageFont

from app import models


@dataclasses.dataclass
class UploadFileApi:
    """Dataclass for keeping track of ImageKit.io's Upload File API"""

    UPLOAD_API = "https://upload.imagekit.io"
    FILE_UPLOAD_ENDPOINT = "/api/v1/files/upload"


@dataclasses.dataclass
class MediaApi:
    """Dataclass for keeping track of ImageKit.io's Media API"""

    MEDIA_API = "https://api.imagekit.io"
    FOLDER_ENDPOINT = "/v1/folder"


class ImageProcessor:
    """Image processing client."""

    async def _attach_text(
        self,
        image: Image.Image,
        certificate_issuance_date: models.CertificateIssuanceDate,
        certificate_meta: models.CertificateMeta,
        certificate_recipient: models.CertificateRecipient,
    ) -> bytes:
        """Attach text on an e-Certificate template.

        Args:
            draw (ImageDraw.ImageDraw): An instance of `PIL.ImageDraw.ImageDraw`.
            image (Image.Image): An instance of `PIL.Image.Image`.
            image_processor_params (models.ImageProcessorParams): An instance of
                `app.models.ImageProcessorParams`

        Returns:
            bytes: Text attachment result.
        """
        draw = ImageDraw.Draw(image)
        draw.text(  # type: ignore
            xy=certificate_recipient.text_position,
            text=certificate_recipient.recipient_name,
            fill=certificate_meta.font_color,
            font=ImageFont.truetype(
                io.BytesIO(certificate_meta.font_style),
                certificate_recipient.text_size,
            ),
            anchor="mm",
        )
        draw.text(  # type: ignore
            xy=certificate_issuance_date.text_position,
            text=certificate_issuance_date.issuance_date,
            fill=certificate_meta.font_color,
            font=ImageFont.truetype(
                io.BytesIO(certificate_meta.font_style),
                certificate_issuance_date.text_size,
            ),
            anchor="mm",
        )
        writer = io.BytesIO()
        image.save(writer, format="jpeg")
        return writer.getvalue()

    async def attach_text(
        self,
        certificate_issuance_date: models.CertificateIssuanceDate,
        certificate_meta: models.CertificateMeta,
        certificate_recipients: list[models.CertificateRecipient],
    ):
        """Attach a buch of texts on an e-Certificate template.

        Args:
            imp_collection (list[models.ImageProcessorParams]): List of e-Certificate
                metadata.

        Returns:
            list[pool.ApplyResult[typing.Any]]: Generated e-Certificates.
        """
        image = Image.open(io.BytesIO(certificate_meta.template))

        results = await asyncio.gather(
            *(
                self._attach_text(
                    image,
                    certificate_issuance_date,
                    certificate_meta,
                    recipient_meta,
                )
                for recipient_meta in certificate_recipients
            )
        )

        return results


class ImageKitClient:
    """Async ImageKit client."""

    DEFAULT_ENCODING = "utf-8"

    _private_key = ""
    _public_key = ""
    _endpoint_url = ""
    _headers = {}

    media_api: MediaApi
    upload_api: UploadFileApi
    session: aiohttp.ClientSession

    def __init__(self, private_key: str, public_key: str, url_endpoint: str) -> None:
        self._private_key = private_key
        self._public_key = public_key
        self._endpoint_url = url_endpoint
        self.media_api = MediaApi()
        self.upload_api = UploadFileApi()
        self._create_request_header()
        self._create_client_session()

    def _create_request_header(self) -> None:
        """Create default headers for the client session."""
        base64_private_key = base64.b64encode(
            f"{self._private_key}:".encode(encoding=self.DEFAULT_ENCODING)
        ).decode(encoding=self.DEFAULT_ENCODING)
        self._headers = {"Authorization": f"Basic {base64_private_key}"}

    def _create_client_session(self) -> None:
        """Initialize the client session."""
        self.session = aiohttp.ClientSession(
            headers=self._headers,
            json_serialize=lambda json_: orjson.dumps(  # pylint: disable=E1101
                json_
            ).decode(),
        )

    async def create_folder(
        self, folder_name: str, parent_folder_path: str
    ) -> dict[str, str | typing.Any]:
        """Create a folder in the ImageKit.io media library.

        References:
            https://docs.imagekit.io/api-reference

        Args:
            folder_name (str): The name of the folder to be created.
            parent_folder_path (str): The folder where the new folder should be
                created.

        Returns:
            dict[str, str | typing.Any]: JSON object containing the result of the
                folder creation process.
        """
        url = f"{self.upload_api.UPLOAD_API}{self.upload_api.FILE_UPLOAD_ENDPOINT}"
        request_body = {
            "folderName": folder_name,
            "parentFolderPath": parent_folder_path,
        }
        response = await self.session.post(url=url, json=request_body)

        if (json_response := await response.json()) == "{}":
            return request_body
        return json_response

    async def upload_file(
        self,
        file: bytes | typing.BinaryIO,
        file_name: str,
        options: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        """Upload files to the ImageKit.io media library.
        References:
            https://docs.imagekit.io/api-reference
        Args:
            file (bytes | typing.BinaryIO): The file content or URL.
            file_name (str): The name with which the file has to be uploaded.
            options (dict[str, typing.Any]): The rest of the requst structure.
        Returns:
            dict[str, typing.Any]: Dictionary containing the uploaded file details.
        """
        url = f"{self.upload_api.UPLOAD_API}{self.upload_api.FILE_UPLOAD_ENDPOINT}"
        request_body = {**{"fileName": file_name}, **options}
        form_data = aiohttp.FormData()

        for key, value in request_body.items():
            form_data.add_field(key, value)
        form_data.add_field("file", file)

        response = await self.session.post(url=url, data=form_data)
        return await response.json()
