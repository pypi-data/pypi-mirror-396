from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, model_validator, AliasChoices

from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes, RequiredField

# Constants for repeated field descriptions
WIKI_IDENTIFIER_DESCRIPTION = "Wiki ID or wiki name"
VERSION_IDENTIFIER_DESCRIPTION = "Version string identifier (name of tag/branch, SHA1 of commit)"
VERSION_TYPE_DESCRIPTION = "Version type (branch, tag, or commit). Determines how Id is interpreted"


class AzureDevOpsWikiConfig(CodeMieToolConfig):
    """Configuration for Azure DevOps Wiki integration.

    Supports both direct configuration and mapping from separate fields:
    - Direct: organization_url, project, token
    - Mapped: url/base_url + organization -> organization_url, access_token -> token
    """

    credential_type: CredentialTypes = Field(
        default=CredentialTypes.AZURE_DEVOPS, exclude=True, frozen=True
    )

    organization_url: str = RequiredField(
        description="Azure DevOps organization URL",
        json_schema_extra={
            "placeholder": "https://dev.azure.com/your-organization",
            "help": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization",
        },
    )

    project: str = RequiredField(
        description="Azure DevOps project name", json_schema_extra={"placeholder": "MyProject"}
    )

    token: str = RequiredField(
        description="Personal Access Token (PAT) for authentication",
        validation_alias=AliasChoices("token", "access_token"),
        json_schema_extra={
            "placeholder": "your_personal_access_token",
            "sensitive": True,
            "help": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate",
        },
    )

    @model_validator(mode="before")
    def build_organization_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build organization_url from url/base_url + organization if not provided directly.

        Supports legacy mapping:
        - url or base_url + organization -> organization_url
        - access_token -> token (handled by AliasChoices)
        """
        if not isinstance(values, dict):
            return values

        # If organization_url is not provided, try to build it from url + organization
        if "organization_url" not in values:
            url = values.get("url") or values.get("base_url")
            organization = values.get("organization")

            if url and organization:
                base_url = url.rstrip('/')
                values["organization_url"] = f"{base_url}/{organization}"

        return values


# Input models for Azure DevOps wiki operations
class GetWikiInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)


class GetPageByPathInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    page_name: str = Field(
        description="Wiki page path. For URLs, extract the '/{page_id}/{page-slug}' portion. "
        "Example: from URL '...wikis/MyWiki.wiki/123/My-Page', use '/123/My-Page'"
    )


class GetPageByIdInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    page_id: int = Field(description="Wiki page ID")


class ModifyPageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    page_name: str = Field(
        description="Wiki page path. For URLs, extract the '/{page_id}/{page-slug}' portion. "
        "Example: from URL '...wikis/MyWiki.wiki/123/My-Page', use '/123/My-Page'"
    )
    page_content: str = Field(description="Wiki page content")
    version_identifier: str = Field(description=VERSION_IDENTIFIER_DESCRIPTION)
    version_type: Optional[str] = Field(
        description=VERSION_TYPE_DESCRIPTION,
        default="branch",
    )


class CreatePageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    parent_page_path: str = Field(
        description="Parent page path where the new page will be created. "
        "For URLs, extract the '/{page_id}/{page-slug}' portion. "
        "Use '/' for root level pages. "
        "Examples: '/123/Parent-Page' (from URL) or '/Parent Page' (direct path)"
    )
    new_page_name: str = Field(
        description="Name of the new page to create (without path, just the name). "
        "Example: 'My New Page'"
    )
    page_content: str = Field(description="Markdown content for the new wiki page")
    version_identifier: str = Field(description=VERSION_IDENTIFIER_DESCRIPTION)
    version_type: Optional[str] = Field(
        description=VERSION_TYPE_DESCRIPTION,
        default="branch",
    )


class RenamePageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    old_page_name: str = Field(
        description="Wiki page path to rename. For URLs, extract the '/{page_id}/{page-slug}' portion. "
        "Example: from URL '...wikis/MyWiki.wiki/123/My-Page', use '/123/My-Page'",
        examples=["/123/TestPageName", "/TestPageName"],
    )
    new_page_name: str = Field(
        description="New Wiki page name", examples=["RenamedName", "/RenamedName"]
    )
    version_identifier: str = Field(description=VERSION_IDENTIFIER_DESCRIPTION)
    version_type: Optional[str] = Field(
        description=VERSION_TYPE_DESCRIPTION,
        default="branch",
    )


class SearchWikiPagesInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    search_text: str = Field(description="Text to search for across wiki pages (case-insensitive)")
    include_context: bool = Field(
        default=True,
        description="Whether to include content snippets showing where the search text was found",
    )
    max_results: int = Field(
        default=50,
        description="Maximum number of results to return (default: 50)",
    )
