from typing import List

from codemie_tools.base.base_toolkit import DiscoverableToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.code.sonar.tools import SonarTool
from codemie_tools.code.sonar.tools_vars import SONAR_TOOL


class CodeToolkitUI(ToolKit):
    """UI definition for Code toolkit - ONLY Sonar tool with credentials.

    Other code tools (search, tree, read) are added separately on the backend
    via context and do not require credentials.
    """
    toolkit: ToolSet = ToolSet.CODEBASE_TOOLS
    tools: List[Tool] = [
        Tool.from_metadata(SONAR_TOOL, tool_class=SonarTool)
    ]
    label: str = ToolSet.CODEBASE_TOOLS.value


class CodeToolkit(DiscoverableToolkit):
    """Discoverable toolkit for code-related tools requiring credentials.

    Currently contains only Sonar tool. Other code tools (search, tree, read)
    are added separately on the backend via context.
    """

    @classmethod
    def get_definition(cls):
        return CodeToolkitUI()
