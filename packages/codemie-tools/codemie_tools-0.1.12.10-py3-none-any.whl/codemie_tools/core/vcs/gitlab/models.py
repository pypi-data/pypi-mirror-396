from pydantic import Field
from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes, RequiredField


class GitlabConfig(CodeMieToolConfig):
    """Configuration for GitLab API access."""
    credential_type: CredentialTypes = Field(default=CredentialTypes.GIT, exclude=True, frozen=True)
    url: str = RequiredField(
        description="GitLab instance URL",
        json_schema_extra={"placeholder": "https://gitlab.example.com"}
    )
    token: str = RequiredField(
        description="GitLab Personal Access Token with appropriate scopes",
        json_schema_extra={
            "sensitive": True,
            "help": "https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html"
        }
    )
