import asyncio
import io
import uuid

import aiohttp
import fastapi
import PIL
from fastapi import responses

from app import models, services
from app.api.dependencies import certificates

router = fastapi.APIRouter(prefix="/certificates")


async def _upload_ecertificates(
    gdrive_client: services.GoogleDriveClient, ecerts: list[io.BytesIO]
) -> list[tuple[str, str]]:
    responses_: list[tuple[str, str]] = []
    loop = asyncio.get_running_loop()
    gdrive_folder = await gdrive_client.create_folder(
        loop=loop, folder_name=str(uuid.uuid4())
    )
    gdrive_folder_id: str = gdrive_folder["id"]

    for ecert in ecerts:
        response = await gdrive_client.upload_file(
            loop=loop,
            file=ecert,
            file_name=str(uuid.uuid1()),
            folder_id=gdrive_folder_id,
        )
        responses_.append(response)

    # This is the code we will use if we want to store the generated e-Certificates to
    # ImageKit.io instead:
    # folder = str(uuid.uuid1())
    # for ecert in ecerts:
    #     response = await imagekit_client.upload_file(
    #         file=ecert,
    #         file_name=str(uuid.uuid1()),
    #         options={"folder": folder},
    #     )
    #     responses.append(response)

    return responses_


async def _generate_ecertificate(
    http_client: aiohttp.ClientSession,
    certificate_template_meta: models.CertificateTemplateMeta,
    image_processor: services.ImageProcessor,
    gdrive_client: services.GoogleDriveClient,
) -> list[dict[str, str]]:
    # These assertions are purely for pyright to be able to understand the code; the
    # validators should have already checked the values.

    font_src = await http_client.get(certificate_template_meta.font_url)
    template_src = await http_client.get(certificate_template_meta.template_url)

    # Construct image processor options
    certificate_issuance_date = models.CertificateIssuanceDate(
        issuance_date=str(certificate_template_meta.issuance_date),
        text_position=(
            certificate_template_meta.issuance_date_meta.position["x"],
            certificate_template_meta.issuance_date_meta.position["y"],
        ),
        text_size=certificate_template_meta.issuance_date_meta.font_size,
    )

    certificate_meta = models.CertificateMeta(
        font_style=await font_src.read(),
        font_color="black",
        template=await template_src.read(),
    )

    certificate_recipients: list[models.CertificateRecipient] = [
        models.CertificateRecipient(
            recipient_name=name.recipient_name,
            text_position=(
                certificate_template_meta.recipient_name_meta.position["x"],
                certificate_template_meta.recipient_name_meta.position["y"],
            ),
            text_size=certificate_template_meta.recipient_name_meta.font_size,
        )
        for name in certificate_template_meta.recipients
    ]

    try:
        results = await image_processor.attach_text(
            certificate_issuance_date=certificate_issuance_date,
            certificate_meta=certificate_meta,
            certificate_recipients=certificate_recipients,
        )
    except PIL.UnidentifiedImageError as e:
        raise fastapi.HTTPException(
            status_code=400,
            detail=str(e),
        ) from e

    ecerts_loc = await _upload_ecertificates(
        gdrive_client=gdrive_client, ecerts=[io.BytesIO(result) for result in results]
    )

    return [
        {
            "certificate_url": ecert[0],
            "file_id": ecert[1],
            "recipient_name": recipient.recipient_name,
            "issuance_date": certificate_issuance_date.issuance_date,
        }
        for ecert, recipient in zip(ecerts_loc, certificate_recipients)
    ]


@router.post("")
async def generate_ecertificate(
    requests: fastapi.Request,
    certificate_template_meta: models.CertificateTemplateMeta,
    image_processor: services.ImageProcessor = fastapi.Depends(
        certificates.get_image_processor
    ),
    gdrive_client: services.GoogleDriveClient = fastapi.Depends(
        certificates.get_gdrive_client
    ),
) -> responses.ORJSONResponse:
    http_client = requests.app.state.http_client

    assert isinstance(http_client, aiohttp.ClientSession)

    result = await _generate_ecertificate(
        http_client=http_client,
        certificate_template_meta=certificate_template_meta,
        image_processor=image_processor,
        gdrive_client=gdrive_client,
    )

    return responses.ORJSONResponse(content={"certificate": result}, status_code=201)
