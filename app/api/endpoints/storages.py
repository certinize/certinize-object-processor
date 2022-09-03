import typing

import aiohttp
import fastapi
from fastapi import responses

from app import services
from app.api.dependencies import storages

router = fastapi.APIRouter(prefix="/storages")


@router.post("", status_code=201, response_class=responses.ORJSONResponse)
async def upload_permanent_object(
    file: list[fastapi.UploadFile],
    filebase_s3_client: services.S3ClientSession = fastapi.Depends(
        storages.get_filebase_s3_client
    ),
    nft_storage_client: services.NftStorageClient = fastapi.Depends(
        storages.get_nft_storage_client
    ),
    s3_client_interface: services.S3Client = fastapi.Depends(
        storages.get_s3_client_interface
    ),
    http_client: aiohttp.ClientSession = fastapi.Depends(storages.get_http_client),
):
    # Due to free-tier storage limitations, we have to use multiple pinning services.
    try:
        # Assume the entire form data only contains json objects.
        if file[0].content_type == "application/json":
            response_meta: list[typing.Any] = []

            for json_file in file:
                result = await s3_client_interface.put_object(
                    client=filebase_s3_client.s3client,
                    bucket=filebase_s3_client.bucket_name,
                    key=json_file.filename,
                    body=await json_file.read(),
                )
                meta = result["ResponseMetadata"]

                if isinstance(meta, dict):
                    meta = meta | {"Key": json_file.filename}

                response_meta.append(meta)

            bucket_name = f"{filebase_s3_client.bucket_name} (filebase.com)"
            network = "IPFS"
        else:
            file_: dict[str, tuple[str, bytes]] = {}

            for item in file:
                file_[item.filename] = (item.content_type, await item.read())

            response = await nft_storage_client.upload_file(
                http_client=http_client, file=file_
            )
            bucket_name = "files (nft.storage)"
            network = "IPFS"
            response_meta = response
    except ValueError as value_err:
        raise fastapi.HTTPException(status_code=400, detail=str(value_err))

    return {
        "bucket_name": bucket_name,
        "network": network,
        "response_meta": response_meta,
    }
