import json
from typing import Any, Type, Optional

from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.data_management.elastic.elastic_wrapper import SearchElasticIndexResults
from codemie_tools.data_management.elastic.models import ElasticConfig, SearchElasticIndexInput
from codemie_tools.data_management.elastic.tools_vars import SEARCH_ES_INDEX_TOOL


class SearchElasticIndex(CodeMieTool):
    config: Optional[ElasticConfig] = Field(exclude=True, default=None)
    name: str = SEARCH_ES_INDEX_TOOL.name
    description: str = SEARCH_ES_INDEX_TOOL.description
    args_schema: Type[BaseModel] = SearchElasticIndexInput

    def execute(self, index: str, query: str, **kwargs: Any) -> Any:
        if not self.config:
            raise ValueError("Elastic configuration is not provided")
        mapping = json.loads(query)
        response = SearchElasticIndexResults.search(index=index, query=mapping, elastic_config=self.config)
        return response
