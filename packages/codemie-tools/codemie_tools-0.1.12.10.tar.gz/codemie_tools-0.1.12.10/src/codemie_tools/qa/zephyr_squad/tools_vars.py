from codemie_tools.base.models import ToolMetadata
from codemie_tools.qa.zephyr_squad.models import ZephyrSquadConfig

ZEPHYR_SQUAD_TOOL = ToolMetadata(
    name="ZephyrSquad",
    description=
    """
    Zephyr SquatTool that provides access to Zephyr Squad API, enabling interaction with Zephyr test cases,
    cycles or executions etc.
    You must provide the following args: method, relative_path.
    1. 'method': HTTP method to be used in an API call
    2. 'relative_path': Relative path excluding base url and /public/rest/api/1.0/config/, e.x.:
    - /cycle?expand=123&cloned123CycleId=123
    - /executions/search?executionId=123
    - ...
    3. 'body': an optional JSON parameter. Must be a valid JSON
    """.strip(),
    label="Zephyr Squad",
    user_description="""
    Provides access to the Zephyr Squad Cloud API.

    Before using it, the following credentials must be obtained:
    1. Jira Account ID.

    The easiest way to retrieve the AccountID is to click on the icon on the left-hand menu and then click the Profile link.
    Within the URL, you can find your AccountID after the last "/".
    Example: https://********.atlassian.net/people/5bb7ad0ccc53fd0760103780
    Or get from https://*****.atlassian.net/rest/api/3/myself

    2. Zephyr API Access and Secret keys, obtained via Zephyr UI in Jira
    """.strip(),
    settings_config=True,
    config_class=ZephyrSquadConfig
)
