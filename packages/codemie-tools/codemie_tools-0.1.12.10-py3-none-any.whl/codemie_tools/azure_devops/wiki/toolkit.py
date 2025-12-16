from typing import List

from codemie_tools.base.base_toolkit import DiscoverableToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.azure_devops.wiki.tools import (
    GetWikiTool,
    GetWikiPageByPathTool,
    GetWikiPageByIdTool,
    DeletePageByPathTool,
    DeletePageByIdTool,
    CreateWikiPageTool,
    ModifyWikiPageTool,
    RenameWikiPageTool,
    SearchWikiPagesTool,
)
from codemie_tools.azure_devops.wiki.tools_vars import (
    GET_WIKI_TOOL,
    GET_WIKI_PAGE_BY_PATH_TOOL,
    GET_WIKI_PAGE_BY_ID_TOOL,
    DELETE_PAGE_BY_PATH_TOOL,
    DELETE_PAGE_BY_ID_TOOL,
    CREATE_WIKI_PAGE_TOOL,
    MODIFY_WIKI_PAGE_TOOL,
    RENAME_WIKI_PAGE_TOOL,
    SEARCH_WIKI_PAGES_TOOL,
)


class AzureDevOpsWikiToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.AZURE_DEVOPS_WIKI
    tools: List[Tool] = [
        Tool.from_metadata(GET_WIKI_TOOL, tool_class=GetWikiTool),
        Tool.from_metadata(GET_WIKI_PAGE_BY_PATH_TOOL, tool_class=GetWikiPageByPathTool),
        Tool.from_metadata(GET_WIKI_PAGE_BY_ID_TOOL, tool_class=GetWikiPageByIdTool),
        Tool.from_metadata(DELETE_PAGE_BY_PATH_TOOL, tool_class=DeletePageByPathTool),
        Tool.from_metadata(DELETE_PAGE_BY_ID_TOOL, tool_class=DeletePageByIdTool),
        Tool.from_metadata(CREATE_WIKI_PAGE_TOOL, tool_class=CreateWikiPageTool),
        Tool.from_metadata(MODIFY_WIKI_PAGE_TOOL, tool_class=ModifyWikiPageTool),
        Tool.from_metadata(RENAME_WIKI_PAGE_TOOL, tool_class=RenameWikiPageTool),
        Tool.from_metadata(SEARCH_WIKI_PAGES_TOOL, tool_class=SearchWikiPagesTool),
    ]
    label: str = ToolSet.AZURE_DEVOPS_WIKI.value
    settings_config: bool = True


class AzureDevOpsWikiToolkit(DiscoverableToolkit):

    @classmethod
    def get_definition(cls):
        return AzureDevOpsWikiToolkitUI()
