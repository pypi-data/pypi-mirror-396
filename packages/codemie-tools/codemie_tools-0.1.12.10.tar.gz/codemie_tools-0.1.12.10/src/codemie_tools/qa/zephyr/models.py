from typing import Optional
from pydantic import BaseModel, Field
from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes


class ZephyrConfig(CodeMieToolConfig):
    credential_type: CredentialTypes = Field(default=CredentialTypes.ZEPHYR_SCALE, exclude=True, frozen=True)
    url: str
    token: str


class ZephyrToolInput(BaseModel):
    entity_str: str = Field(
        ...,
        description="""
        The Zephyr entity name.
        Can be one of the (test_cases, test_cycles, test_plans, test_executions,
        folders, statuses, priorities, environments, projects, links, issue_links,
        automations, healthcheck). Required parameter.
        """.strip()
    )
    method_str: str = Field(
        ...,
        description="""
        Required parameter: The method that should be executed on the entity.
        Always use "dir" as value before you run the real method to get the list of available methods.
        **Important:** If you receive an error that object has no attribute then use "dir".
        """
    )
    body: Optional[str] = Field(
        ...,
        description="""
        Optional JSON of input parameters of the method. MUST be string with valid JSON.
        """
    )
