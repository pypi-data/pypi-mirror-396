from typing import List

from codemie_tools.base.base_toolkit import DiscoverableToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.azure_devops.work_item.tools import (
    SearchWorkItemsTool,
    CreateWorkItemTool,
    UpdateWorkItemTool,
    GetWorkItemTool,
    LinkWorkItemsTool,
    GetRelationTypesTool,
    GetCommentsTool
)
from codemie_tools.azure_devops.work_item.tools_vars import (
    SEARCH_WORK_ITEMS_TOOL,
    CREATE_WORK_ITEM_TOOL,
    UPDATE_WORK_ITEM_TOOL,
    GET_WORK_ITEM_TOOL,
    LINK_WORK_ITEMS_TOOL,
    GET_RELATION_TYPES_TOOL,
    GET_COMMENTS_TOOL
)


class AzureDevOpsWorkItemToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.AZURE_DEVOPS_WORK_ITEM
    tools: List[Tool] = [
        Tool.from_metadata(SEARCH_WORK_ITEMS_TOOL, tool_class=SearchWorkItemsTool),
        Tool.from_metadata(CREATE_WORK_ITEM_TOOL, tool_class=CreateWorkItemTool),
        Tool.from_metadata(UPDATE_WORK_ITEM_TOOL, tool_class=UpdateWorkItemTool),
        Tool.from_metadata(GET_WORK_ITEM_TOOL, tool_class=GetWorkItemTool),
        Tool.from_metadata(LINK_WORK_ITEMS_TOOL, tool_class=LinkWorkItemsTool),
        Tool.from_metadata(GET_RELATION_TYPES_TOOL, tool_class=GetRelationTypesTool),
        Tool.from_metadata(GET_COMMENTS_TOOL, tool_class=GetCommentsTool),
    ]
    label: str = ToolSet.AZURE_DEVOPS_WORK_ITEM.value
    settings_config: bool = True


class AzureDevOpsWorkItemToolkit(DiscoverableToolkit):

    @classmethod
    def get_definition(cls):
        return AzureDevOpsWorkItemToolkitUI()
