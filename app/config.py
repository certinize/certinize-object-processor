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

    gdrive_svcs_acc_auth_provider_x509_cert_url = ""
    gdrive_svcs_acc_auth_uri = ""
    gdrive_svcs_acc_client_email = ""
    gdrive_svcs_acc_client_id = ""
    gdrive_svcs_acc_client_x509_cert_url = ""
    gdrive_svcs_acc_private_key = ""
    gdrive_svcs_acc_private_key_id = ""
    gdrive_svcs_acc_project_id = ""
    gdrive_svcs_acc_token_uri = ""
    gdrive_svcs_acc_type = "service_account"

    logging_level = "INFO"

    class Config(BaseAppSettings.Config):
        validate_assignment = True


settings = AppSettings()
