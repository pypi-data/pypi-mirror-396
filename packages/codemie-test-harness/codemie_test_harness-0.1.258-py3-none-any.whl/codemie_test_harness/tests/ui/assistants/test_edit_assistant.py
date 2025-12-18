import pytest
from codemie_test_harness.tests import TEST_USER, PROJECT
from codemie_test_harness.tests.ui.pageobject.assistants.assistant_view_page import (
    AssistantViewPage,
)

from codemie_test_harness.tests.ui.pageobject.assistants.assistants_page import (
    AssistantsPage,
)
from codemie_test_harness.tests.ui.test_data.assistant_test_data import (
    ExternalToolKit,
    MCPServersTool,
    get_minimal_assistant_mcp_config_data,
)


from codemie_test_harness.tests.ui.test_data.assistant_test_data import (
    TOOLKIT_TOOLS,
    AssistantPopUpMessages,
    AssistantValidationErrors,
)
from codemie_test_harness.tests.ui.pageobject.assistants.create_edit_assistant_page import (
    CreateEditAssistantPage,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.assistant_ui
@pytest.mark.ui
def test_edit_assistant_page_elements_visibility(page, assistant):
    """
    Test all main elements are visible on Edit Assistant page—fields, toolkits, checkboxes, etc.
    """
    edit_page = CreateEditAssistantPage(page)
    assistant_page = AssistantsPage(page)
    assistant = assistant()

    assistant_page.navigate_to()
    assistant_page.search_assistants(assistant.name)
    assistant_page.click_assistant_edit(assistant.name)

    edit_page.should_have_all_form_fields_visible()
    edit_page.should_have_top_p_and_temperature()
    edit_page.should_have_datasource_context()
    edit_page.should_have_sub_assistants_context()
    edit_page.should_have_categories_visible()

    for section, toolkits in TOOLKIT_TOOLS.items():
        edit_page.select_section(section.value)
        for toolkit, tools in toolkits.items():
            edit_page.select_toolkit(section.value, toolkit.value)
            for tool in tools:
                edit_page.should_be_visible_tool(tool.value)


@pytest.mark.assistant_ui
@pytest.mark.ui
def test_edit_assistant_form_field_interactions(page, assistant):
    """
    Test interacting with all editable form fields.
    """
    EDITED = " EDITED"
    edit_page = CreateEditAssistantPage(page)
    view_page = AssistantViewPage(page)
    assistant_page = AssistantsPage(page)
    assistant = assistant()

    assistant_page.navigate_to()
    assistant_page.search_assistants(assistant.name)
    assistant_page.click_assistant_edit(assistant.name)

    edit_page.fill_name(assistant.name + EDITED)
    edit_page.should_have_name_value(assistant.name + EDITED)
    edit_page.fill_description(assistant.description + EDITED)
    edit_page.should_have_description_value(assistant.description + EDITED)

    edit_page.toggle_shared_assistant(True)
    edit_page.should_have_shared_checked()
    edit_page.toggle_shared_assistant(False)
    edit_page.should_have_shared_unchecked()

    edit_page.fill_temperature("0.5")
    edit_page.fill_top_p("0.5")
    edit_page.should_have_top_p_and_temperature_value("0.5", "0.5")
    edit_page.click_save()
    assistant_page.should_see_updating_popup(
        AssistantPopUpMessages.ASSISTANT_UPDATED_SUCCESS.value
    )
    assistant_page.should_see_assistant_with_name(assistant.name + EDITED)

    assistant_page.click_assistant_view(assistant.name + EDITED)
    view_page.should_have_all_form_fields_visible(
        name=assistant.name + EDITED,
        author=TEST_USER,
        description=assistant.description + EDITED,
    )
    view_page.should_have_overview_form_fields_visible(
        project=PROJECT, status="Not shared", assistant_id=assistant.id
    )
    view_page.should_have_access_links_form_fields_visible(
        assistant_id=assistant.id, assistant_name=assistant.name
    )
    view_page.should_have_configuration_form_fields_visible(
        temperature="0.5", top_p="0.5"
    )


@pytest.mark.assistant_ui
@pytest.mark.ui
def test_edit_assistant_tools_interactions(page, assistant):
    """
    Test interacting with all tools in assistant.
    """
    edit_page = CreateEditAssistantPage(page)
    view_page = AssistantViewPage(page)
    assistant_page = AssistantsPage(page)
    assistant = assistant()

    assistant_page.navigate_to()
    assistant_page.search_assistants(assistant.name)
    assistant_page.click_assistant_edit(assistant.name)

    for section, toolkits in TOOLKIT_TOOLS.items():
        edit_page.select_section(section.value)
        for toolkit, tools in toolkits.items():
            edit_page.select_toolkit(section.value, toolkit.value)
            for tool in tools:
                edit_page.select_tool(tool.value)
    edit_page.click_save()
    assistant_page.should_see_updating_popup(
        AssistantPopUpMessages.ASSISTANT_UPDATED_SUCCESS.value
    )

    assistant_page.click_assistant_view(assistant.name)
    for section, toolkits in TOOLKIT_TOOLS.items():
        for toolkit, tools in toolkits.items():
            toolkit_label = toolkit.value
            if ExternalToolKit.MCP_SERVERS.value in toolkit.value:
                toolkit_label = "MCP"
            view_page.should_see_toolkit_visible(toolkit_label)
            for tool in tools:
                test_data = get_minimal_assistant_mcp_config_data()
                tool_label = tool.value
                if MCPServersTool.ADD_MCP_SERVER.value in tool.value:
                    tool_label = test_data.name
                view_page.should_see_toolkit_contains(toolkit_label, tool_label)


@pytest.mark.assistant_ui
@pytest.mark.ui
def test_edit_assistant_incorrect_form(page, assistant):
    """
    Test interacting with incorrect data.
    """
    edit_page = CreateEditAssistantPage(page)
    assistant_page = AssistantsPage(page)
    assistant = assistant()

    assistant_page.navigate_to()
    assistant_page.search_assistants(assistant.name)
    assistant_page.click_assistant_edit(assistant.name)

    edit_page.fill_name("")
    edit_page.should_have_name_error_textarea(
        AssistantValidationErrors.NAME_REQUIRED.value
    )
    edit_page.fill_name(get_random_name())

    edit_page.fill_icon_url(get_random_name())
    edit_page.should_have_icon_error_textarea(
        AssistantValidationErrors.ICON_URL_NOT_VALID.value
    )
    edit_page.fill_icon_url("")

    edit_page.fill_description("")
    edit_page.should_have_description_error_textarea(
        AssistantValidationErrors.DESCRIPTION_REQUIRED.value
    )
    edit_page.fill_description(get_random_name())

    edit_page.fill_system_prompt("")
    edit_page.should_have_system_prompt_error_textarea(
        AssistantValidationErrors.SYSTEM_PROMPT_REQUIRED.value
    )
    edit_page.fill_system_prompt(get_random_name())

    edit_page.fill_temperature("3")
    edit_page.should_have_temperature_error_textarea(
        AssistantValidationErrors.TEMPERATURE_NOT_VALID.value
    )
    edit_page.fill_temperature("1")

    edit_page.fill_top_p("2")
    edit_page.should_have_top_p_error_textarea(
        AssistantValidationErrors.TOP_P_NOT_VALID.value
    )
    edit_page.fill_top_p("1")

    edit_page.click_save()
    assistant_page.should_see_updating_popup(
        AssistantPopUpMessages.ASSISTANT_UPDATED_SUCCESS.value
    )
