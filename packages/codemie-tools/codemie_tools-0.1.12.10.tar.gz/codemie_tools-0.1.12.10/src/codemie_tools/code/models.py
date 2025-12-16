from pydantic import Field

from codemie_tools.base.models import CodeMieToolConfig, RequiredField, CredentialTypes


class SonarConfig(CodeMieToolConfig):
    """Configuration for SonarQube integration.

    Maps backend fields:
    - url -> url
    - sonar_token -> token
    - sonar_project_name -> sonar_project_name
    """
    credential_type: CredentialTypes = Field(default=CredentialTypes.SONAR, exclude=True, frozen=True)
    url: str = RequiredField(
        description="SonarQube server URL",
        json_schema_extra={"placeholder": "https://sonarqube.example.com"}
    )
    token: str = RequiredField(
        description="SonarQube authentication token",
        json_schema_extra={
            "sensitive": True,
            "help": "https://docs.sonarqube.org/latest/user-guide/user-token/"
        }
    )
    sonar_project_name: str = RequiredField(
        description="SonarQube project key",
        json_schema_extra={"placeholder": "my-project-key"}
    )
