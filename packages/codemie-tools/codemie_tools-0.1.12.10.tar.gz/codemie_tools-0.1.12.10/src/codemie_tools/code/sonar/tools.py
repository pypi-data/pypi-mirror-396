import json
import traceback
from json import JSONDecodeError
from typing import Any, Dict, Type, Optional

import requests
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.code.models import SonarConfig
from codemie_tools.code.sonar.tools_vars import SONAR_TOOL


class SonarToolInput(BaseModel):
    relative_url: str = Field(
        ...,
        description="""
        Required parameter: The relative URI for SONAR REST API.
        URI must start with a forward slash and '/api/issues/search..'.
        Do not include query parameters in the URL, they must be provided separately in 'params'.
        For search/read operations, you MUST always get "cleanCodeAttributeCategories",
        "severity", "issueStatuses", "types" and set maxResult,
        until users ask explicitly for more fields.
        """
    )
    params: Optional[str] = Field(
        default="",
        description="""
        Optional JSON of parameters to be sent in request body or query params. MUST be string with
        valid JSON. For search/read operations, you MUST always get "cleanCodeAttributeCategories",
        "severity", "issueStatuses", "types" and set maxResult,
        until users ask explicitly for more fields.
        """
    )


def parse_payload_params(params: Optional[str]) -> Dict[str, Any]:
    if params:
        try:
            return json.loads(params)
        except JSONDecodeError:
            stacktrace = traceback.format_exc()
            raise ToolException(f"Sonar tool exception. Passed params are not valid JSON. {stacktrace}")
    return {}


class SonarTool(CodeMieTool):
    name: str = SONAR_TOOL.name
    config: SonarConfig
    args_schema: Type[BaseModel] = SonarToolInput
    description: str = SONAR_TOOL.description

    def _healthcheck(self):
        """Performs a healthcheck for Sonar integration.

        Validates the provided token and verifies that the specified
        project is accessible in SonarQube.
        """
        # Validate token
        response = self.execute("api/authentication/validate", "")

        if not response.get('valid', False):
            raise ToolException("Invalid token")

        # Validate project
        if not self.config.sonar_project_name:
            raise ToolException("Project name not provided")

        response = self.execute(
            "api/components/show",
            f'{{"component": "{self.config.sonar_project_name}"}}'
        )

        if 'component' not in response:
            errors = response.get("errors", [{"msg": "Error occurred when trying to get project information"}])
            error_msg = (" | ").join([error.get('msg', "") for error in errors])
            raise ToolException(error_msg)

        component = response.get("component", {})

        if component.get('key', "") == self.config.sonar_project_name and component.get('qualifier', "") == "TRK":
            return  # Success

        raise ToolException("Project not found or invalid qualifier")

    def execute(self, relative_url: str, params: str, *args) -> Any:
        payload_params = parse_payload_params(params)
        payload_params['componentKeys'] = self.config.sonar_project_name
        return requests.get(
            url=f"{self.config.url}/{relative_url}",
            auth=(self.config.token, ''),
            params=payload_params
        ).json()
