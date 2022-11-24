import base64
import dataclasses
import typing

import pydantic


class Recipient(pydantic.BaseModel):
    recipient_name: str = pydantic.Field(min_length=1)


class CertificateTextMeta(pydantic.BaseModel):
    font_size: int
    font_url: pydantic.HttpUrl
    position: dict[str, int]
    template_height: int | None = None

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
    template_url: pydantic.HttpUrl
    recipients: list[Recipient]


class TemplateUpload(pydantic.BaseModel):
    filename: str
    options: dict[str, typing.Any]
    fileb: str

    @pydantic.validator("fileb")
    @classmethod
    def fileb_must_be_valid_base64(cls, value: str):
        try:
            base64.b64decode(value)
        except Exception as exc:
            raise ValueError("fileb must be a valid base64 encoded image") from exc

        return value


@dataclasses.dataclass
class CertificateRecipient:
    recipient_name: str
    text_position: tuple[int, int]
    text_size: int


@dataclasses.dataclass
class CertificateIssuanceDate:
    text_position: tuple[int, int]
    text_size: int


@dataclasses.dataclass
class CertificateMeta:
    font_color: str
    template: bytes
    name_font_style: bytes
    template_height: int | None = None
