import dataclasses
import datetime

import pydantic


class CertificateTemplateMeta(pydantic.BaseModel):
    recipient_name_meta: dict[str, int | dict[str, float]]
    issuance_date_meta: dict[str, int | dict[str, float]]
    template_url: pydantic.HttpUrl
    font_url: pydantic.HttpUrl
    issuance_date: datetime.date
    recipients: list[dict[str, str]]


@dataclasses.dataclass
class CertificateRecipient:
    recipient_name: str
    text_position: tuple[float, float]
    text_size: int


@dataclasses.dataclass
class CertificateIssuanceDate:
    issuance_date: str
    text_position: tuple[float, float]
    text_size: int


@dataclasses.dataclass
class CertificateMeta:
    font_style: bytes
    font_color: str
    template: bytes
