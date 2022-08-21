import asyncio
import io
import uuid

import aiohttp
import fastapi
from fastapi import responses

from app import models, services
from app.api.dependencies import certificates

router = fastapi.APIRouter(prefix="/certificates")


async def _upload_ecertificates(
    gdrive_client: services.GoogleDriveClient, ecerts: list[io.BytesIO]
) -> list[tuple[str, str]]:
    responses: list[tuple[str, str]] = []
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
        responses.append(response)

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

    return responses


async def _generate_ecertificate(
    http_client: aiohttp.ClientSession,
    certificate_template_meta: models.CertificateTemplateMeta,
    image_processor: services.ImageProcessor,
    gdrive_client: services.GoogleDriveClient,
) -> list[dict[str, str]]:
    font_src = await http_client.get(certificate_template_meta.font_url)
    font_style = await font_src.read()

    template_src = await http_client.get(certificate_template_meta.template_url)
    template = await template_src.read()

    recipient_name_meta = certificate_template_meta.recipient_name_meta
    recipient_name_fontsize = recipient_name_meta["font_size"]
    assert isinstance(recipient_name_fontsize, int)

    issuance_date_meta = certificate_template_meta.issuance_date_meta
    issuance_date_fontsize = issuance_date_meta["font_size"]
    assert isinstance(issuance_date_fontsize, int)

    recipient_name_position = (0, 0)
    issuance_date_position = (0, 0)

    if not isinstance(
        (recname_meta_pos := recipient_name_meta["position"]), int
    ) and not isinstance((issuance_meta_pos := issuance_date_meta["position"]), int):
        recipient_name_position = (recname_meta_pos["x"], recname_meta_pos["y"])
        issuance_date_position = (issuance_meta_pos["x"], issuance_meta_pos["y"])

    certificate_issuance_date = models.CertificateIssuanceDate(
        issuance_date=str(certificate_template_meta.issuance_date),
        text_position=issuance_date_position,
        text_size=issuance_date_fontsize,
    )

    certificate_meta = models.CertificateMeta(
        font_style=font_style, font_color="black", template=template
    )

    certificate_recipients: list[models.CertificateRecipient] = []

    for name in certificate_template_meta.recipients:
        certificate_recipients.append(
            models.CertificateRecipient(
                recipient_name=name["recipient_name"],
                text_position=recipient_name_position,
                text_size=recipient_name_fontsize,
            )
        )

    results = await image_processor.attach_text(
        certificate_issuance_date=certificate_issuance_date,
        certificate_meta=certificate_meta,
        certificate_recipients=certificate_recipients,
    )

    ecerts: list[dict[str, str]] = []
    ecerts_loc = await _upload_ecertificates(
        gdrive_client=gdrive_client, ecerts=[io.BytesIO(result) for result in results]
    )

    for ecert, recipient in zip(ecerts_loc, certificate_recipients):
        ecerts.append(
            {
                "certificate_url": ecert[0],
                "file_id": ecert[1],
                "recipient_name": recipient.recipient_name,
                "issuance_date": certificate_issuance_date.issuance_date,
            }
        )

    return ecerts


@router.post("/")
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
    assert isinstance(requests.app.state.http_client, aiohttp.ClientSession)

    result = await _generate_ecertificate(
        http_client=requests.app.state.http_client,
        certificate_template_meta=certificate_template_meta,
        image_processor=image_processor,
        gdrive_client=gdrive_client,
    )

    return responses.ORJSONResponse(content={"certificate": result}, status_code=201)
