from typing import List

from codemie_tools.base.base_toolkit import DiscoverableToolkit
from codemie_tools.base.models import ToolKit, Tool, ToolSet
from codemie_tools.qa.zephyr.tools import ZephyrGenericTool
from codemie_tools.qa.zephyr.tools_vars import ZEPHYR_TOOL
from codemie_tools.qa.zephyr_squad.tools import ZephyrSquadGenericTool
from codemie_tools.qa.zephyr_squad.tools_vars import ZEPHYR_SQUAD_TOOL


class QualityAssuranceToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.QUALITY_ASSURANCE
    tools: List[Tool] = [
        Tool.from_metadata(ZEPHYR_TOOL, tool_class=ZephyrGenericTool),
        Tool.from_metadata(ZEPHYR_SQUAD_TOOL, tool_class=ZephyrSquadGenericTool),
    ]
    label: str = ToolSet.QUALITY_ASSURANCE.value


class QualityAssuranceToolkit(DiscoverableToolkit):
    @classmethod
    def get_definition(cls):
        return QualityAssuranceToolkitUI()
