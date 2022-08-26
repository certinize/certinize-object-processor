import pydantic


class BaseAppSettings(pydantic.BaseSettings):
    class Config(pydantic.BaseSettings.Config):
        env_file = ".env"


class AppSettings(BaseAppSettings):
    debug = False
    title = "Certinize image processor"
    version = "0.1.0"
    allow_origins: list[str] = ["*"]

    imagekit_endpoint_url: pydantic.AnyHttpUrl = pydantic.AnyHttpUrl(
        url="https://", scheme="https"
    )
    imagekit_public_key = ""
    imagekit_private_key = ""

    s3_api_endpoint_url: pydantic.AnyHttpUrl = pydantic.AnyHttpUrl(
        url="https://", scheme="https"
    )
    s3_access_key_id = ""
    s3_secret_access_key = ""

    logging_level = "INFO"

    class Config(BaseAppSettings.Config):
        validate_assignment = True


settings = AppSettings()
