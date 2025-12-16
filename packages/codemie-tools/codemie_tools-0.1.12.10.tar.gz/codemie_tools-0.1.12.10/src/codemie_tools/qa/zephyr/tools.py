import json
from types import GeneratorType
from typing import Optional, Type
from pydantic import BaseModel, Field
from zephyr import ZephyrScale

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.qa.zephyr.models import ZephyrConfig, ZephyrToolInput
from codemie_tools.qa.zephyr.tools_vars import ZEPHYR_TOOL

# Entity and method that is used for integration healthcheck
ZEPHYR_HEALTHCHECK_ENTITY = "healthcheck"
ZEPHYR_HEALTHCHECK_METHOD = "get_health"


class ZephyrGenericTool(CodeMieTool):
    config: Optional[ZephyrConfig] = Field(exclude=True, default=None)
    name: str = ZEPHYR_TOOL.name
    description: str = ZEPHYR_TOOL.description
    args_schema: Type[BaseModel] = ZephyrToolInput

    def _healthcheck(self):
        """Performs a healthcheck by querying the health endpoint"""
        self.execute(entity_str=ZEPHYR_HEALTHCHECK_ENTITY, method_str=ZEPHYR_HEALTHCHECK_METHOD)

    def execute(self, entity_str: str, method_str: str, body: Optional[str] = None):
        if not self.config:
            raise ValueError("Zephyr Scale config is not provided. Please set it before using the tool.")
        zephyr_base_url = self.config.url
        if not zephyr_base_url.endswith("/"):
            zephyr_base_url += "/"

        zephyr_api = ZephyrScale(base_url=zephyr_base_url, token=self.config.token).api
        entity = getattr(zephyr_api, entity_str)

        if method_str == "dir":
            return dir(entity)

        method = getattr(entity, method_str)
        params = json.loads(body) if body else {}
        result = method(**params)

        if isinstance(result, GeneratorType):
            return list(result)
        else:
            return result
