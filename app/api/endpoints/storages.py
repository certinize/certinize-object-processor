import fastapi
import types_aiobotocore_s3
from fastapi import responses
from types_aiobotocore_s3 import type_defs

from app import services
from app.api.dependencies import storages

router = fastapi.APIRouter(prefix="/storages")


@router.post("", status_code=201, response_class=responses.ORJSONResponse)
async def upload_permanent_object(
    file: fastapi.UploadFile,
    bucket: str = fastapi.Form(),
    s3_client: types_aiobotocore_s3.S3Client = fastapi.Depends(storages.get_s3_client),
    filebase_client: services.FilebaseClient = fastapi.Depends(
        storages.get_filebase_client
    ),
) -> dict[str, str | type_defs.ResponseMetadataTypeDef]:
    try:
        result = await filebase_client.put_object(
            client=s3_client, bucket=bucket, key=file.filename, body=await file.read()
        )
        return {
            "bucket_name": bucket,
            "network": "IPFS",
            "response_meta": result["ResponseMetadata"],
        }
    except ValueError as value_err:
        raise fastapi.HTTPException(status_code=400, detail=str(value_err))
