import dataclasses
import datetime
import typing

import pydantic


class Recipient(pydantic.BaseModel):
    recipient_name: str = pydantic.Field(min_length=1)


class CertificateTextMeta(pydantic.BaseModel):
    font_size: int
    position: dict[str, int]

    @pydantic.validator("position")
    @classmethod
    def position_must_have_axes(cls, value: typing.Any):
        if "x" not in value:
            raise ValueError("position must have x axis")

        if "y" not in value:
            raise ValueError("position must have y axis")

        return value


class CertificateTemplateMeta(pydantic.BaseModel):
    recipient_name_meta: CertificateTextMeta
    issuance_date_meta: CertificateTextMeta
    template_url: pydantic.HttpUrl
    font_url: pydantic.HttpUrl
    issuance_date: datetime.date
    recipients: list[Recipient]


@dataclasses.dataclass
class CertificateRecipient:
    recipient_name: str
    text_position: tuple[int, int]
    text_size: int


@dataclasses.dataclass
class CertificateIssuanceDate:
    issuance_date: str
    text_position: tuple[int, int]
    text_size: int


@dataclasses.dataclass
class CertificateMeta:
    font_style: bytes
    font_color: str
    template: bytes
