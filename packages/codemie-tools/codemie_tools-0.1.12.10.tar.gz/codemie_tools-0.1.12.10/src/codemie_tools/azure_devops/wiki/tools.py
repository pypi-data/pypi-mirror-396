import os
from typing import Type, Optional

from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from azure.devops.v7_0.core import CoreClient
from azure.devops.v7_0.search import SearchClient
from azure.devops.v7_0.search.models import WikiSearchRequest
from azure.devops.v7_0.wiki import (
    WikiClient,
    WikiPageCreateOrUpdateParameters,
    WikiCreateParametersV2,
    WikiPageMoveParameters,
    WikiV2,
)
from azure.devops.v7_0.wiki.models import GitVersionDescriptor
from langchain_core.tools import ToolException
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel

from codemie_tools.azure_devops.wiki.models import (
    AzureDevOpsWikiConfig,
    GetWikiInput,
    GetPageByPathInput,
    GetPageByIdInput,
    ModifyPageInput,
    CreatePageInput,
    RenamePageInput,
    SearchWikiPagesInput,
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
from codemie_tools.base.codemie_tool import CodeMieTool, logger

# Ensure Azure DevOps cache directory is set
if not os.environ.get("AZURE_DEVOPS_CACHE_DIR", None):
    os.environ["AZURE_DEVOPS_CACHE_DIR"] = ""

# Constants for error messages
INVALID_VERSION_ERROR = "The version '{0}' either is invalid or does not exist."


class BaseAzureDevOpsWikiTool(CodeMieTool):
    """Base class for Azure DevOps Wiki tools."""

    config: AzureDevOpsWikiConfig
    __client: Optional[WikiClient] = None
    __core_client: Optional[CoreClient] = None
    __search_client: Optional[SearchClient] = None
    __connection: Optional[Connection] = None

    @property
    def _connection(self) -> Connection:
        """Get or create Azure DevOps connection (lazy initialization)."""
        if self.__connection is None:
            try:
                # Set up connection to Azure DevOps using Personal Access Token (PAT)
                credentials = BasicAuthentication("", self.config.token)
                self.__connection = Connection(
                    base_url=self.config.organization_url, creds=credentials
                )
            except Exception as e:
                logger.error(f"Failed to connect to Azure DevOps: {e}")
                raise ToolException(f"Failed to connect to Azure DevOps: {e}")
        return self.__connection

    @_connection.setter
    def _connection(self, value: Connection) -> None:
        """Set the Azure DevOps connection (useful for testing)."""
        self.__connection = value

    @property
    def _client(self) -> WikiClient:
        """Get or create Azure DevOps wiki client (lazy initialization)."""
        if self.__client is None:
            self.__client = self._connection.clients.get_wiki_client()
        return self.__client

    @_client.setter
    def _client(self, value: WikiClient) -> None:
        """Set the Azure DevOps wiki client (useful for testing)."""
        self.__client = value

    @property
    def _core_client(self) -> CoreClient:
        """Get or create Azure DevOps core client (lazy initialization)."""
        if self.__core_client is None:
            self.__core_client = self._connection.clients.get_core_client()
        return self.__core_client

    @_core_client.setter
    def _core_client(self, value: CoreClient) -> None:
        """Set the Azure DevOps core client (useful for testing)."""
        self.__core_client = value

    @property
    def _search_client(self) -> SearchClient:
        """Get or create Azure DevOps search client (lazy initialization)."""
        if self.__search_client is None:
            self.__search_client = self._connection.clients.get_search_client()
        return self.__search_client

    @_search_client.setter
    def _search_client(self, value: SearchClient) -> None:
        """Set the Azure DevOps search client (useful for testing)."""
        self.__search_client = value

    def _extract_page_id_from_path(self, page_name: str) -> Optional[int]:
        """
        Extract page ID from path format like '/10330/This-is-sub-page'.

        Returns page ID if found, None otherwise.
        """
        if not page_name or not page_name.startswith("/"):
            return None

        parts = page_name.lstrip("/").split("/", 1)
        if parts and parts[0].isdigit():
            return int(parts[0])
        return None

    def _get_full_path_from_id(self, wiki_identified: str, page_id: int) -> str:
        """
        Get the full hierarchical path of a page using its ID.

        Returns the full path like '/Parent/Child/Page'.
        """
        try:
            page = self._client.get_page_by_id(
                project=self.config.project,
                wiki_identifier=wiki_identified,
                id=page_id,
                include_content=False,
            )
            return page.page.path
        except Exception as e:
            logger.error(f"Failed to get page path from ID {page_id}: {str(e)}")
            raise ToolException(f"Failed to get page path from ID {page_id}: {str(e)}")

    def _get_project_id(self) -> Optional[str]:
        """Get project ID from project name."""
        projects = self._core_client.get_projects()
        for project in projects:
            if project.name == self.config.project:
                return project.id
        return None

    def _create_wiki_if_not_exists(self, wiki_identified: str) -> Optional[str]:
        """Create wiki if it doesn't exist."""
        all_wikis = [wiki.name for wiki in self._client.get_all_wikis(project=self.config.project)]
        if wiki_identified in all_wikis:
            return None

        logger.info(f"Wiki name '{wiki_identified}' doesn't exist. New wiki will be created.")
        try:
            project_id = self._get_project_id()
            if not project_id:
                return "Project ID has not been found."

            self._client.create_wiki(
                project=self.config.project,
                wiki_create_params=WikiCreateParametersV2(
                    name=wiki_identified, project_id=project_id
                ),
            )
            logger.info(f"Wiki '{wiki_identified}' has been created")
            return None
        except Exception as create_wiki_e:
            error_msg = f"Unable to create new wiki due to error: {create_wiki_e}"
            logger.error(error_msg)
            return error_msg

    def _construct_page_url(self, wiki_identified: str, page_id: int, page_name: str) -> str:
        """
        Construct a full Azure DevOps wiki page URL.

        Args:
            wiki_identified: Wiki name or ID
            page_id: Page ID
            page_name: Page name (will be converted to URL slug)

        Returns:
            Full page URL like: https://dev.azure.com/{org}/{project}/_wiki/wikis/{wiki}/{id}/{slug}
        """
        # Convert page name to URL slug (spaces to hyphens)
        page_slug = page_name.replace(" ", "-")
        # Build full URL
        page_url = (
            f"{self.config.organization_url}/{self.config.project}/"
            f"_wiki/wikis/{wiki_identified}/{page_id}/{page_slug}"
        )
        return page_url

    def _get_page_info(
        self, wiki_identified: str, page_path: str, include_content: bool = False
    ) -> tuple[Optional[int], Optional[str], Optional[str]]:
        """
        Get page information (ID, name, URL) from a page path.

        Args:
            wiki_identified: Wiki name or ID
            page_path: Full hierarchical page path (e.g., "/Parent/Child/Page")
            include_content: Whether to include page content in the response

        Returns:
            Tuple of (page_id, page_name, page_url), or (None, None, None) if page not found
        """
        try:
            page_response = self._client.get_page(
                project=self.config.project,
                wiki_identifier=wiki_identified,
                path=page_path,
                include_content=include_content,
            )
            if hasattr(page_response.page, "id"):
                page_id = page_response.page.id
                # Extract page name from path (last segment)
                page_name = page_path.split("/")[-1] if page_path else ""
                # Construct full URL
                page_url = self._construct_page_url(wiki_identified, page_id, page_name)
                return page_id, page_name, page_url
            return None, None, None
        except Exception as e:
            logger.debug(f"Could not get page info for {page_path}: {str(e)}")
            return None, None, None


class GetWikiTool(BaseAzureDevOpsWikiTool):
    """Tool to get information about a wiki in Azure DevOps."""

    name: str = GET_WIKI_TOOL.name
    description: str = GET_WIKI_TOOL.description
    args_schema: Type[BaseModel] = GetWikiInput

    def execute(self, wiki_identified: str):
        """Extract ADO wiki information."""
        try:
            wiki: WikiV2 = self._client.get_wiki(
                project=self.config.project, wiki_identifier=wiki_identified
            )
            return wiki.as_dict()
        except Exception as e:
            logger.error(f"Error during the attempt to extract wiki: {str(e)}")
            raise ToolException(f"Error during the attempt to extract wiki: {str(e)}")


class GetWikiPageByPathTool(BaseAzureDevOpsWikiTool):
    """Tool to get wiki page content by path in Azure DevOps."""

    name: str = GET_WIKI_PAGE_BY_PATH_TOOL.name
    description: str = GET_WIKI_PAGE_BY_PATH_TOOL.description
    args_schema: Type[BaseModel] = GetPageByPathInput

    def execute(self, wiki_identified: str, page_name: str):
        """Extract ADO wiki page content."""
        try:
            # Try to extract page ID from path format like '/10330/This-is-sub-page'
            page_id = self._extract_page_id_from_path(page_name)

            if page_id is not None:
                # Get full hierarchical path using page ID
                logger.info(f"Extracted page ID {page_id} from path, discovering full path...")
                full_path = self._get_full_path_from_id(wiki_identified, page_id)
                logger.info(f"Discovered full path: {full_path}")
                page_name = full_path

            # Get page content using the (possibly resolved) path
            page = self._client.get_page(
                project=self.config.project,
                wiki_identifier=wiki_identified,
                path=page_name,
                include_content=True,
            )
            return page.page.content
        except Exception as e:
            logger.error(f"Error during the attempt to extract wiki page: {str(e)}")
            raise ToolException(f"Error during the attempt to extract wiki page: {str(e)}")


class GetWikiPageByIdTool(BaseAzureDevOpsWikiTool):
    """Tool to get wiki page content by ID in Azure DevOps."""

    name: str = GET_WIKI_PAGE_BY_ID_TOOL.name
    description: str = GET_WIKI_PAGE_BY_ID_TOOL.description
    args_schema: Type[BaseModel] = GetPageByIdInput

    def execute(self, wiki_identified: str, page_id: int):
        """Extract ADO wiki page content."""
        try:
            page = self._client.get_page_by_id(
                project=self.config.project,
                wiki_identifier=wiki_identified,
                id=page_id,
                include_content=True,
            )
            return page.page.content
        except Exception as e:
            logger.error(f"Error during the attempt to extract wiki page: {str(e)}")
            raise ToolException(f"Error during the attempt to extract wiki page: {str(e)}")


class DeletePageByPathTool(BaseAzureDevOpsWikiTool):
    """Tool to delete wiki page by path in Azure DevOps."""

    name: str = DELETE_PAGE_BY_PATH_TOOL.name
    description: str = DELETE_PAGE_BY_PATH_TOOL.description
    args_schema: Type[BaseModel] = GetPageByPathInput

    def execute(self, wiki_identified: str, page_name: str):
        """Delete ADO wiki page by path."""
        try:
            # Try to extract page ID from path format like '/10330/This-is-sub-page'
            page_id = self._extract_page_id_from_path(page_name)

            if page_id is not None:
                # Get full hierarchical path using page ID
                logger.info(f"Extracted page ID {page_id} from path, discovering full path...")
                full_path = self._get_full_path_from_id(wiki_identified, page_id)
                logger.info(f"Discovered full path: {full_path}")
                page_name = full_path

            # Delete page using the (possibly resolved) path
            self._client.delete_page(
                project=self.config.project, wiki_identifier=wiki_identified, path=page_name
            )
            return f"Page '{page_name}' in wiki '{wiki_identified}' has been deleted"
        except Exception as e:
            logger.error(f"Unable to delete wiki page: {str(e)}")
            raise ToolException(f"Unable to delete wiki page: {str(e)}")


class DeletePageByIdTool(BaseAzureDevOpsWikiTool):
    """Tool to delete wiki page by ID in Azure DevOps."""

    name: str = DELETE_PAGE_BY_ID_TOOL.name
    description: str = DELETE_PAGE_BY_ID_TOOL.description
    args_schema: Type[BaseModel] = GetPageByIdInput

    def execute(self, wiki_identified: str, page_id: int):
        """Delete ADO wiki page by ID."""
        try:
            self._client.delete_page_by_id(
                project=self.config.project, wiki_identifier=wiki_identified, id=page_id
            )
            return f"Page with id '{page_id}' in wiki '{wiki_identified}' has been deleted"
        except Exception as e:
            logger.error(f"Unable to delete wiki page: {str(e)}")
            raise ToolException(f"Unable to delete wiki page: {str(e)}")


class RenameWikiPageTool(BaseAzureDevOpsWikiTool):
    """Tool to rename wiki page in Azure DevOps."""

    name: str = RENAME_WIKI_PAGE_TOOL.name
    description: str = RENAME_WIKI_PAGE_TOOL.description
    args_schema: Type[BaseModel] = RenamePageInput

    def _verify_page_exists(self, wiki_identified: str, page_path: str) -> None:
        """
        Verify that the page exists.

        Raises ToolException if page doesn't exist.
        """
        try:
            self._client.get_page(
                project=self.config.project, wiki_identifier=wiki_identified, path=page_path
            )
            logger.info(f"Page '{page_path}' exists and can be renamed")
        except Exception as e:
            error_msg = f"Page '{page_path}' not found. Cannot rename a page that doesn't exist. Error: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)

    def execute(
        self,
        wiki_identified: str,
        old_page_name: str,
        new_page_name: str,
        version_identifier: str,
        version_type: str = "branch",
    ):
        """Rename page in Azure DevOps wiki from old page name to new page name."""
        try:
            # Try to extract page ID from old path format like '/10330/This-is-sub-page'
            page_id = self._extract_page_id_from_path(old_page_name)

            if page_id is not None:
                # Get full hierarchical path using page ID
                logger.info(f"Extracted page ID {page_id} from path, discovering full path...")
                full_path = self._get_full_path_from_id(wiki_identified, page_id)
                logger.info(f"Discovered full path: {full_path}")
                old_page_name = full_path

            # Verify the page exists before attempting rename
            self._verify_page_exists(wiki_identified, old_page_name)

            # Construct new path based on input format
            if not new_page_name.startswith("/"):
                # If new_page_name is just a name (not a path), keep it in the same parent directory
                # Extract parent path from old_page_name
                parent_path = "/".join(old_page_name.rsplit("/", 1)[:-1])
                if parent_path:
                    new_page_name = f"{parent_path}/{new_page_name}"
                else:
                    new_page_name = f"/{new_page_name}"
            # If new_page_name starts with "/", use it as-is (full path move)

            logger.info(f"Renaming page from '{old_page_name}' to '{new_page_name}'")

            # Rename the page
            try:
                result = self._client.create_page_move(
                    project=self.config.project,
                    wiki_identifier=wiki_identified,
                    comment=f"Page rename from '{old_page_name}' to '{new_page_name}'",
                    page_move_parameters=WikiPageMoveParameters(
                        new_path=new_page_name, path=old_page_name
                    ),
                    version_descriptor=GitVersionDescriptor(
                        version=version_identifier, version_type=version_type
                    ),
                )
                return {
                    "response": result,
                    "status": "Success",
                    "message": f"Page renamed from '{old_page_name}' to '{new_page_name}'",
                }
            except AzureDevOpsServiceError as e:
                if INVALID_VERSION_ERROR in str(e):
                    # Retry the request without version_descriptor
                    result = self._client.create_page_move(
                        project=self.config.project,
                        wiki_identifier=wiki_identified,
                        comment=f"Page rename from '{old_page_name}' to '{new_page_name}'",
                        page_move_parameters=WikiPageMoveParameters(
                            new_path=new_page_name, path=old_page_name
                        ),
                    )
                    return {
                        "response": result,
                        "status": "Success",
                        "message": f"Page renamed from '{old_page_name}' to '{new_page_name}' (without version)",
                    }
                else:
                    raise
        except Exception as e:
            logger.error(f"Unable to rename wiki page: {str(e)}")
            raise ToolException(f"Unable to rename wiki page: {str(e)}")


class CreateWikiPageTool(BaseAzureDevOpsWikiTool):
    """Tool to create a new wiki page in Azure DevOps."""

    name: str = CREATE_WIKI_PAGE_TOOL.name
    description: str = CREATE_WIKI_PAGE_TOOL.description
    args_schema: Type[BaseModel] = CreatePageInput

    def execute(
        self,
        wiki_identified: str,
        parent_page_path: str,
        new_page_name: str,
        page_content: str,
        version_identifier: str,
        version_type: str = "branch",
    ):
        """Create a new ADO wiki page under the specified parent page."""
        try:
            # Create wiki if needed
            error = self._create_wiki_if_not_exists(wiki_identified)
            if error:
                raise ToolException(error)

            # Try to extract page ID from parent path format like '/10330/This-is-sub-page'
            page_id = self._extract_page_id_from_path(parent_page_path)

            if page_id is not None:
                # Get full hierarchical path using page ID
                logger.info(
                    f"Extracted page ID {page_id} from parent path, discovering full path..."
                )
                parent_page_path = self._get_full_path_from_id(wiki_identified, page_id)
                logger.info(f"Discovered full parent path: {parent_page_path}")

            # Construct the full path for the new page
            if parent_page_path == "/":
                full_path = f"/{new_page_name}"
            else:
                # Ensure parent path starts with /
                parent = (
                    parent_page_path if parent_page_path.startswith("/") else f"/{parent_page_path}"
                )
                full_path = f"{parent}/{new_page_name}"

            logger.info(f"Creating new page at path: {full_path}")

            # Create the page
            try:
                result = self._client.create_or_update_page(
                    project=self.config.project,
                    wiki_identifier=wiki_identified,
                    path=full_path,
                    parameters=WikiPageCreateOrUpdateParameters(content=page_content),
                    version=None,  # New page, no version
                    version_descriptor=GitVersionDescriptor(
                        version=version_identifier, version_type=version_type
                    ),
                )
                return {
                    "response": result,
                    "message": f"Page '{full_path}' has been created successfully",
                }
            except AzureDevOpsServiceError as e:
                if INVALID_VERSION_ERROR in str(e):
                    # Retry without version descriptor
                    result = self._client.create_or_update_page(
                        project=self.config.project,
                        wiki_identifier=wiki_identified,
                        path=full_path,
                        parameters=WikiPageCreateOrUpdateParameters(content=page_content),
                        version=None,
                    )
                    return {
                        "response": result,
                        "message": f"Page '{full_path}' has been created successfully (without version)",
                    }
                else:
                    raise
        except Exception as e:
            error_msg = f"Unable to create wiki page: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)


class ModifyWikiPageTool(BaseAzureDevOpsWikiTool):
    """Tool to update existing wiki page in Azure DevOps."""

    name: str = MODIFY_WIKI_PAGE_TOOL.name
    description: str = MODIFY_WIKI_PAGE_TOOL.description
    args_schema: Type[BaseModel] = ModifyPageInput

    def _get_page_version(self, wiki_identified: str, page_name: str) -> str:
        """
        Get page version (eTag) if page exists.

        Raises ToolException if page doesn't exist.
        """
        try:
            page = self._client.get_page(
                project=self.config.project, wiki_identifier=wiki_identified, path=page_name
            )
            version = page.eTag
            logger.info(f"Existing page found with eTag: {version}")
            return version
        except Exception as e:
            error_msg = f"Page '{page_name}' not found. Use 'create_wiki_page' tool to create new pages. Error: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)

    def execute(
        self,
        wiki_identified: str,
        page_name: str,
        page_content: str,
        version_identifier: str,
        version_type: str = "branch",
    ):
        """Update existing ADO wiki page content."""
        try:
            # Try to extract page ID from path format like '/10330/This-is-sub-page'
            page_id = self._extract_page_id_from_path(page_name)

            if page_id is not None:
                # Get full hierarchical path using page ID
                logger.info(f"Extracted page ID {page_id} from path, discovering full path...")
                full_path = self._get_full_path_from_id(wiki_identified, page_id)
                logger.info(f"Discovered full path: {full_path}")
                page_name = full_path

            # Get page version (will fail if page doesn't exist)
            version = self._get_page_version(wiki_identified, page_name)

            # Update the page
            try:
                result = self._client.create_or_update_page(
                    project=self.config.project,
                    wiki_identifier=wiki_identified,
                    path=page_name,
                    parameters=WikiPageCreateOrUpdateParameters(content=page_content),
                    version=version,
                    version_descriptor=GitVersionDescriptor(
                        version=version_identifier, version_type=version_type
                    ),
                )
                return {
                    "response": result,
                    "message": f"Page '{page_name}' has been updated successfully",
                }
            except AzureDevOpsServiceError as e:
                if INVALID_VERSION_ERROR in str(e):
                    # Retry without version descriptor
                    result = self._client.create_or_update_page(
                        project=self.config.project,
                        wiki_identifier=wiki_identified,
                        path=page_name,
                        parameters=WikiPageCreateOrUpdateParameters(content=page_content),
                        version=version,
                    )
                    return {
                        "response": result,
                        "message": f"Page '{page_name}' has been updated successfully (without version)",
                    }
                else:
                    raise
        except Exception as e:
            error_msg = f"Unable to modify wiki page: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)


class SearchWikiPagesTool(BaseAzureDevOpsWikiTool):
    """Tool to search for text content across wiki pages in Azure DevOps."""

    name: str = SEARCH_WIKI_PAGES_TOOL.name
    description: str = SEARCH_WIKI_PAGES_TOOL.description
    args_schema: Type[BaseModel] = SearchWikiPagesInput

    def execute(
        self,
        wiki_identified: str,
        search_text: str,
        include_context: Optional[bool] = True,
        max_results: Optional[int] = 50,
    ):
        """
        Search for text content across wiki pages using Azure DevOps Search API.

        Args:
            wiki_identified: Wiki name or ID
            search_text: Text to search for
            include_context: Whether to include content snippets (hits)
            max_results: Maximum number of results to return

        Returns:
            Search results with full URLs added to each result
        """
        try:
            # Create search request using SDK models
            search_request = WikiSearchRequest(
                search_text=search_text,
                skip=0,
                top=min(max_results, 100),  # API max is 100 per request
                filters={"Wiki": [wiki_identified]},
                order_by=None,
                include_facets=False,
            )

            # Call search API using SDK
            search_response = self._search_client.fetch_wiki_search_results(
                request=search_request, project=self.config.project
            )

            # Convert SDK response to dict
            response_dict = search_response.as_dict()

            # Process results to add full URLs
            if "results" in response_dict:
                from urllib.parse import quote

                for result in response_dict["results"]:
                    # Remove hits if include_context is False
                    if not include_context and "hits" in result:
                        del result["hits"]

                    # Construct URL using query parameter pattern
                    # Format: {organization_url}/{project}/_wiki/wikis/{wikiName}?pagePath={encodedPath}
                    wiki_name = result.get("wiki", {}).get("name")
                    path = result.get("path", "")

                    if wiki_name and path:
                        # Remove .md extension and URL-encode the path (keep leading slash)
                        page_path = path.replace(".md", "").replace(".MD", "")
                        encoded_path = quote(page_path, safe="")

                        # Construct full URL using config's organization_url and project
                        full_url = (
                            f"{self.config.organization_url}/{self.config.project}"
                            f"/_wiki/wikis/{quote(wiki_name, safe='')}"
                            f"?pagePath={encoded_path}"
                        )
                        result["full_url"] = full_url

            return response_dict

        except Exception as e:
            error_msg = f"Unable to search wiki pages: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
