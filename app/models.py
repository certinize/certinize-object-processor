import dataclasses
import datetime
import typing

import pydantic


class CertificateTemplateMeta(pydantic.BaseModel):
    recipient_name_meta: dict[str, int | dict[str, int]]
    issuance_date_meta: dict[str, int | dict[str, int]]
    template_url: pydantic.HttpUrl
    font_url: pydantic.HttpUrl
    issuance_date: datetime.date
    recipients: list[dict[str, str]]

    @pydantic.validator("recipient_name_meta")
    @classmethod
    def recipient_name_meta_must_have_valid_structure(
        cls, value: dict[str, typing.Any]
    ):
        # Check if value has font_size and position keys
        if "font_size" not in value:
            raise ValueError("recipient_name_meta must have a font_size key")

        if "position" not in value:
            raise ValueError("recipient_name_meta must have a position key")

        # Check if value font_size is an int
        if not isinstance(value["font_size"], int):
            raise ValueError("recipient_name_meta font_size must be an int")

        # Check if value position is a dict with x and y keys
        if "x" not in value["position"]:
            raise ValueError("recipient_name_meta position must have a x key")

        if "y" not in value["position"]:
            raise ValueError("recipient_name_meta position must have a y key")

        # Check if value position x is an int
        if not isinstance(value["position"]["x"], int):
            raise ValueError("recipient_name_meta position x must be an int")

        # Check if value position y is an int
        if not isinstance(value["position"]["y"], int):
            raise ValueError("recipient_name_meta position y must be an int")

        return value

    @pydantic.validator("issuance_date_meta")
    @classmethod
    def issuance_date_meta_must_have_valid_structure(cls, value: dict[str, typing.Any]):
        # Check if value has font_size and position keys
        if "font_size" not in value:
            raise ValueError("recipient_name_meta must have a font_size key")

        if "position" not in value:
            raise ValueError("recipient_name_meta must have a position key")

        # Check if value font_size is an int
        if not isinstance(value["font_size"], int):
            raise ValueError("recipient_name_meta font_size must be an int")

        # Check if value position is a dict with x and y keys
        if "x" not in value["position"]:
            raise ValueError("recipient_name_meta position must have a x key")

        if "y" not in value["position"]:
            raise ValueError("recipient_name_meta position must have a y key")

        # Check if value position x and y are integers
        if not isinstance(value["position"]["x"], int):
            raise ValueError("recipient_name_meta position x must be an int")

        if not isinstance(value["position"]["y"], int):
            raise ValueError("recipient_name_meta position y must be an int")

        return value

    @pydantic.validator("recipients")
    @classmethod
    def recipients_must_have_valid_structure(cls, value: list[dict[str, str]]):
        # Check if list contains dicts with name keys
        for recipient in value:
            if "name" not in recipient:
                raise ValueError("recipient must have a name key")

            # Check that value name does not have a zero length
            # We don't want users sending strings with zero length. They should be
            # marked as spam.
            if len(recipient["name"]) == 0:
                raise ValueError("recipient name must not be empty")


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
