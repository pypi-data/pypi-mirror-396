from pydantic import Field

from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes


class TelegramConfig(CodeMieToolConfig):
    credential_type: CredentialTypes = Field(default=CredentialTypes.TELEGRAM, exclude=True, frozen=True)
    bot_token: str = Field(
        default="",
        alias="token",
        description="Telegram Bot API token",
        json_schema_extra={
            "placeholder": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "sensitive": True,
        },
    )
