"""
app.services
~~~~~~~~~~~~
"""
import asyncio
import base64
import contextlib
import dataclasses
import io
import json
import sys
import typing

import aiohttp
import types_aiobotocore_s3
from PIL import Image, ImageDraw, ImageFont
from pydrive2 import drive, files, fs
from types_aiobotocore_s3 import client as s3client
from types_aiobotocore_s3 import type_defs

from app import models

IMAGEKIT_UPLOAD_API = "https://upload.imagekit.io"
IMAGEKIT_FILE_UPLOAD = "/api/v1/files/upload"


@dataclasses.dataclass
class S3ClientSession:
    bucket_name: str
    exit_stack: contextlib.AsyncExitStack
    s3client: types_aiobotocore_s3.S3Client


class ImageProcessor:  # pylint: disable=R0903
    """Image processing client."""

    async def _attach_text(
        self,
        certificate_meta: models.CertificateMeta,
        certificate_recipient: models.CertificateRecipient,
    ) -> bytes:
        """Attach a bunch of texts on an e-Certificate template.

        Args:
            certificate_meta (models.CertificateMeta): e-Certificate metadata.
            certificate_recipient (models.CertificateRecipient): e-Certificate recipient
                metadata.

        Returns:
            bytes: Generated e-Certificate in bytes.
        """
        image = Image.open(io.BytesIO(certificate_meta.template))
        image = image.convert("RGB")

        if certificate_meta.template_height is not None:
            image.thumbnail(
                (sys.maxsize, certificate_meta.template_height), Image.LANCZOS
            )

        draw = ImageDraw.Draw(image)
        draw.text(  # type: ignore
            xy=certificate_recipient.text_position,
            text=certificate_recipient.recipient_name,
            fill=certificate_meta.font_color,
            font=ImageFont.truetype(
                io.BytesIO(certificate_meta.name_font_style),
                certificate_recipient.text_size,
            ),
            anchor="mm",
        )
        writer = io.BytesIO()
        image.save(writer, format="jpeg")
        return writer.getvalue()

    async def attach_text(
        self,
        certificate_meta: models.CertificateMeta,
        certificate_recipients: list[models.CertificateRecipient],
    ):
        """Attach a bunch of texts on an e-Certificate template.

        Args:
            imp_collection (list[models.ImageProcessorParams]): List of e-Certificate
                metadata.

        Returns:
            list[pool.ApplyResult[typing.Any]]: Generated e-Certificates in bytes.
        """
        results = await asyncio.gather(
            *(
                self._attach_text(
                    certificate_meta,
                    recipient_meta,
                )
                for recipient_meta in certificate_recipients
            )
        )

        return results


class ImageKitClient:
    """Asynchronous ImageKit client."""

    DEFAULT_ENCODING = "utf-8"

    _private_key = ""
    _public_key = ""
    _endpoint_url = ""
    _headers = {}

    session: aiohttp.ClientSession

    def __init__(self, private_key: str, public_key: str, url_endpoint: str) -> None:
        self._private_key = private_key
        self._public_key = public_key
        self._endpoint_url = url_endpoint
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
        self.session = aiohttp.ClientSession(headers=self._headers)

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
        url = f"{IMAGEKIT_UPLOAD_API}{IMAGEKIT_FILE_UPLOAD}"
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
        file: str,
        file_name: str,
        options: dict[str, typing.Any],
    ) -> dict[str, typing.Any]:
        """Upload files to the ImageKit.io media library.

        References:
            https://docs.imagekit.io/api-reference

        Args:
            file (bytes): The file content or URL.
            file_name (str): The name with which the file has to be uploaded.
            options (dict[str, typing.Any]): The rest of the requst structure.

        Returns:
            dict[str, typing.Any]: Dictionary containing the uploaded file details.
        """
        url = f"{IMAGEKIT_UPLOAD_API}{IMAGEKIT_FILE_UPLOAD}"
        request_body = {**{"fileName": file_name}, **options}
        form_data = aiohttp.FormData()

        for key, value in request_body.items():
            form_data.add_field(key, value)

        form_data.add_field("file", file, content_type="image/jpeg")

        response = await self.session.post(url=url, data=form_data)
        return await response.json()


class GoogleDriveClient:
    """Asynchronous Google Drive client."""

    file_system: fs.GDriveFileSystem

    def __init__(self, client_json_file_path: str) -> None:
        self.file_system = fs.GDriveFileSystem(
            "root",
            use_service_account=True,
            client_json_file_path=client_json_file_path,
        )

    async def create_folder(
        self, loop: asyncio.AbstractEventLoop, folder_name: str
    ) -> files.GoogleDriveFile:
        """Create a Google Drive folder.

        Args:
            loop (asyncio.AbstractEventLoop): An asyncio event loop.
            folder_name (str): The name of the folder to create.
        """
        gdrive: drive.GoogleDrive = self.file_system.client  # type: ignore
        folder: files.GoogleDriveFile = await loop.run_in_executor(
            None,
            gdrive.CreateFile,  # type: ignore
            {"title": folder_name, "mimeType": "application/vnd.google-apps.folder"},
        )

        await loop.run_in_executor(None, folder.Upload)  # type: ignore

        return folder

    async def upload_file(
        self,
        loop: asyncio.AbstractEventLoop,
        file: bytes | io.BytesIO,
        file_name: str,
        folder_id: str,
    ) -> tuple[str, str]:
        """Upload a file object to a Google Drive folder.

        Args:
            loop (asyncio.AbstractEventLoop): An asyncio event loop.
            file (io.BytesIO): The file content.
            file_name (str): The name of the file to upload.
            folder_id (str): ID of the where the file will be stored.

        Returns:
            tuple[str, str]: A shareable link to the uploaded file and the file ID,
                respectively.
        """
        gdrive: drive.GoogleDrive = self.file_system.client  # type: ignore
        file_: files.GoogleDriveFile = await loop.run_in_executor(
            None,
            gdrive.CreateFile,  # type: ignore
            {"title": file_name, "parents": [{"id": folder_id}]},
        )
        file_.content = file

        await loop.run_in_executor(None, file_.Upload)  # type: ignore

        # Why not use GoogleDriveFile.InsertPermission()? InsertPermission() doesn't
        # include the supportsAllDrives param, which is necessary when we want to
        # create a file on a shared folder with the necessary permissions and get a
        # shareable link. In this case, we have to make the request ourselves and
        # manually set supportsAllDrives to True.
        access_token: str = gdrive.auth.credentials.access_token  # type: ignore
        file_id: str = file_["id"]
        url = (
            f"https://www.googleapis.com/drive/v3/files/"
            f"{file_id}/permissions?supportsAllDrives=true"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = json.dumps({"type": "anyone", "value": "anyone", "role": "reader"})

        link: str

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=payload, headers=headers) as _:
                # We have to assign the link here to get the shareable link on time.
                link = file_["alternateLink"]

        # Convert the link to download link.
        # From: https://drive.google.com/file/d/10SyD3uzY07cHX0KK1dxxrF-l3Y6Tt1VA/view?usp=drivesdk
        # To: https://drive.google.com/uc?export=download&id=10SyD3uzY07cHX0KK1dxxrF-l3Y6Tt1VA
        link = link.replace("/file/d/", "/uc?export=download&id=")
        link = link.replace("/view?usp=drivesdk", "")

        return link, file_id

    async def get_files(
        self, loop: asyncio.AbstractEventLoop, query: dict[str, str]
    ) -> list[files.GoogleDriveFile]:
        """Retrieve all files using a specified search query.

        For a list of possible search terms, refer to the Drive API docs:
        https://developers.google.com/drive/api/guides/ref-search-terms

        Args:
            loop (asyncio.AbstractEventLoop): _description_
            query (dict[str, str]): A query string containing a query term, operator,
                and values.

        Returns:
            list[files.GoogleDriveFile]: Files that matched the search query.
        """
        gdrive: drive.GoogleDrive = self.file_system.client  # type: ignore
        file_list: files.GoogleDriveFileList = await loop.run_in_executor(
            None,
            gdrive.ListFile,  # type: ignore
            query,
        )
        gdrive_files: list[files.GoogleDriveFile] = await loop.run_in_executor(
            None,
            file_list.GetList,  # type: ignore
        )

        return gdrive_files

    async def get_all_files(
        self, loop: asyncio.AbstractEventLoop
    ) -> list[files.GoogleDriveFile]:
        """Retrieve all files, including folders and subfolders, from Google Drive.

        Args:
            loop (asyncio.AbstractEventLoop): An asyncio event loop.

        Returns:
            list[files.GoogleDriveFile]: List of files stored in Google Drive.
        """
        return await self.get_files(loop=loop, query={"q": "trashed=false"})

    async def delete_folder(
        self, loop: asyncio.AbstractEventLoop, folder_id: str
    ) -> None:
        """Permanently delete a folder's content and the folder itself.

        Args:
            loop (asyncio.AbstractEventLoop): An asyncio event loop.
            folder_id (str): ID of the folder to delete.
        """
        folder_files = await self.get_files(
            loop=loop, query={"q": f"'{folder_id}' in parents and trashed=false"}
        )

        for file in folder_files:
            await loop.run_in_executor(None, file.Delete)  # type: ignore

        gdrive_files = await self.get_files(
            loop=loop, query={"q": "'root' in parents and trashed=false"}
        )

        for file in gdrive_files:
            if file["id"] == folder_id:
                await loop.run_in_executor(None, file.Delete)  # type: ignore
                break

    async def delete_all_files(self, loop: asyncio.AbstractEventLoop) -> None:
        """Permanently delete all files, including folders and subfolders.

        Args:
            loop (asyncio.AbstractEventLoop): An asyncio event loop.
        """
        gdrive_files = await self.get_files(loop=loop, query={"q": "trashed=false"})

        for file in gdrive_files:
            await loop.run_in_executor(None, file.Delete)  # type: ignore


class S3Client:
    """Client implementation for Filebase's S3-compatible API."""

    @staticmethod
    async def create_bucket(
        client: s3client.S3Client, bucket: str
    ) -> type_defs.CreateBucketOutputTypeDef:
        """Create a new S3 bucket.

        Args:
            client (s3client.S3Client): A client representing S3.
            bucket (str): The name of the bucket to create.

        Returns:
            type_defs.CreateBucketOutputTypeDef: Create bucket output.
        """
        return await client.create_bucket(Bucket=bucket)

    @staticmethod
    async def put_object(
        client: s3client.S3Client, bucket: str, key: str, body: bytes
    ) -> type_defs.PutObjectOutputTypeDef | dict[str, str]:
        """Upload an object to an S3 bucket.

        Args:
            client (s3client.S3Client): A client representing S3.
            bucket (str): Name of the bucket containing the object.
            key (str): Object key for which the PUT action was initiated.
            body (bytes): Object data.

        Returns:
            type_defs.PutObjectOutputTypeDef: Put object output.
        """
        try:
            return await client.put_object(Bucket=bucket, Key=key, Body=body)
        except client.exceptions.NoSuchBucket as bucket_err:
            raise ValueError(f"Bucket {bucket} does not exist.") from bucket_err

    @staticmethod
    async def get_object(
        client: s3client.S3Client, bucket: str, key: str
    ) -> type_defs.GetObjectOutputTypeDef:
        """Get an object from an S3 bucket.

        Args:
            client (s3client.S3Client): A client representing S3.
            bucket (str): Key of the object to get.
            key (str): Name of the object to get.

        Returns:
            type_defs.GetObjectOutputTypeDef: Get object output.
        """
        return await client.get_object(Bucket=bucket, Key=key)

    @staticmethod
    async def delete_object(
        client: s3client.S3Client, bucket: str, key: str
    ) -> type_defs.DeleteObjectOutputTypeDef:
        """Delete an object from an S3 bucket.

        Args:
            client (s3client.S3Client): A client representing S3.
            bucket (str): The bucket name of the bucket containing the object.
            key (str): Name of the object to delete.

        Returns:
            type_defs.DeleteObjectOutputTypeDef: Delete object output.
        """
        return await client.delete_object(Bucket=bucket, Key=key)

    @staticmethod
    async def generate_presigned_post(
        client: s3client.S3Client, bucket: str, key: str, expiration: int | None = None
    ) -> dict[str, typing.Any]:
        try:
            return await client.generate_presigned_post(
                Bucket=bucket, Key=key, ExpiresIn=expiration or 3600
            )
        except client.exceptions.ClientError as client_err:
            return {"details": str(client_err)}

    @staticmethod
    async def upload_with_presigned_post(
        http_client: aiohttp.ClientSession,
        presigned: dict[str, typing.Any],
        file: bytes,
    ):
        return await http_client.post(
            presigned["url"], data=presigned["fields"] | {"file": file}
        )


class NftStorageClient:  # pylint: disable=too-few-public-methods
    """nft.storage API client

    Docs: https://nft.storage/api-docs/
    """

    nft_storage_upload = "/upload"
    nft_storage_api = ""
    api_key = ""

    def __init__(self, nft_storage_api: str, api_key: str) -> None:
        self.nft_storage_api = nft_storage_api
        self.api_key = api_key

    async def upload_file(
        self, http_client: aiohttp.ClientSession, file: dict[str, tuple[str, bytes]]
    ):
        form_data = aiohttp.FormData()

        for filename, file_object in file.items():
            form_data.add_field(
                name="file",
                value=file_object[1],
                content_type=file_object[0],
                filename=filename,
            )

        response = await http_client.post(
            url=f"{self.nft_storage_api}{self.nft_storage_upload}",
            data=form_data,
            headers={
                # "Content-Type": "multipart/form-data",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        return await response.json()
