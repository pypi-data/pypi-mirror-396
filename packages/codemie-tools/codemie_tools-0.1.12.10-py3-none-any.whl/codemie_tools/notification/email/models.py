from codemie_tools.base.models import CodeMieToolConfig, RequiredField, CredentialTypes

from pydantic import Field

class EmailToolConfig(CodeMieToolConfig):
    credential_type: CredentialTypes = Field(default=CredentialTypes.EMAIL, exclude=True, frozen=True)
    url: str = RequiredField(
        description="SMTP server URL including port, e.g. smtp.gmail.com:587",
        json_schema_extra={"placeholder": "smtp.gmail.com:587"},
    )
    smtp_username: str = RequiredField(
        description="SMTP server username/email",
        json_schema_extra={"placeholder": "user@example.com"},
    )
    smtp_password: str = RequiredField(
        description="SMTP server password or app-specific password for accounts with 2FA",
        json_schema_extra={"placeholder": "password", "sensitive": True},
    )
