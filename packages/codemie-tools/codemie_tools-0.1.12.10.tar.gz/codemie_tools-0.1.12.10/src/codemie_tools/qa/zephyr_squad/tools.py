import json
from typing import Optional, Type

from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.qa.zephyr_squad.models import ZephyrSquadConfig, ZephyrSquadToolInput
from codemie_tools.qa.zephyr_squad.tools_vars import ZEPHYR_SQUAD_TOOL
from codemie_tools.qa.zephyr_squad.api_wrapper import ZephyrRestAPI

# URL that is used for integration healthcheck
ZEPHYR_SQUAD_HEALTHCHECK_URL = "/serverinfo"


class ZephyrSquadGenericTool(CodeMieTool):
    config: Optional[ZephyrSquadConfig] = Field(exclude=True, default=None)
    name: str = ZEPHYR_SQUAD_TOOL.name
    description: str = ZEPHYR_SQUAD_TOOL.description
    args_schema: Type[BaseModel] = ZephyrSquadToolInput

    def _healthcheck(self):
        """Performs a healthcheck by querying the serverinfo endpoint"""
        self.execute(relative_path=ZEPHYR_SQUAD_HEALTHCHECK_URL, method="GET")

    def execute(
            self,
            method: str,
            relative_path: str,
            body: Optional[str] = None,
            content_type: str = 'application/json'
    ):
        if not self.config:
            raise ValueError("Zephyr Squad config is not provided. Please set it before using the tool.")

        api = ZephyrRestAPI(
            account_id=self.config.account_id,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
        )

        data = json.loads(body) if body else {}

        return api.request(
            path=relative_path,
            method=method,
            json=data,
            headers={'Content-Type': content_type},
        ).content
