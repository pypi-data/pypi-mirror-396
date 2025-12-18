from hamcrest import assert_that, contains_string
from playwright.sync_api import Page, expect
from reportportal_client import step


class AssistantViewPage:
    def __init__(self, page: Page):
        self.page = page

    # ----------------
    # --- LOCATORS ---
    # ----------------

    @property
    def assistant_name(self):
        return self.page.locator("h4.name-target")

    @property
    def assistant_author(self):
        return self.page.locator(".text-xs.text-text-secondary > p")

    @property
    def about_heading(self):
        return self.page.locator("h5.font-bold.text-sm:text('About Assistant:')")

    @property
    def about_content(self):
        # Paragraph under "About Assistant:"
        return self.about_heading.locator("xpath=../p")

    @property
    def system_instructions_heading(self):
        return self.page.locator(
            "div.flex.bg-new-panel.border.rounded-lg [class*='text-xs']:text('System Instructions')"
        )

    @property
    def system_instructions_content(self):
        return self.page.locator("div.flex.bg-new-panel.border.rounded-lg > p.text-sm")

    # --- Overview Block ---
    @property
    def overview_block(self):
        return self.page.locator("p:text-is('OVERVIEW')").locator("xpath=..")

    @property
    def overview_project(self):
        return self.overview_block.locator(
            "div.flex:has(p.text-text-tertiary:text('Project:')) > p:not(.text-text-tertiary)"
        )

    @property
    def overview_shared_status(self):
        return self.overview_block.locator(
            "div.flex:has(p.text-text-tertiary:text('Shared status:')) > p:not(.text-text-tertiary)"
        )

    @property
    def overview_assistant_id(self):
        return self.overview_block.locator(
            "div.flex.flex-col.gap-2.mt-2.font-semibold input[readonly]"
        )

    # --- Links Block ---
    @property
    def access_links_block(self):
        return self.page.locator(
            "p.text-xs.text-text-main.font-semibold:text('ACCESS LINKS')"
        ).locator("xpath=..")

    @property
    def details_link_input(self):
        return self.access_links_block.locator(
            "div.flex.flex-col.gap-2:has(p:text('Link to assistant details:')) input[readonly]"
        )

    @property
    def chat_link_input(self):
        return self.access_links_block.locator(
            "div.flex.flex-col.gap-2:has(p:text('Link to start a chat')) input[readonly]"
        )

    # --- Configuration ---
    @property
    def configuration_block(self):
        return self.page.locator(
            "p.text-xs.text-text-main.font-semibold:text('CONFIGURATION')"
        ).locator("xpath=..")

    @property
    def config_llm_model(self):
        return self.configuration_block.locator("p:text('LLM model:')").locator(
            "xpath=../div"
        )

    @property
    def config_temperature(self):
        return self.configuration_block.locator("p:text('Temperature:')").locator(
            "xpath=../div"
        )

    @property
    def config_top_p(self):
        return self.configuration_block.locator("p:text('Top P:')").locator(
            "xpath=../div"
        )

    @property
    def config_additional_datasource_context(self):
        return self.configuration_block.locator(
            "div:has(p:text('Additional datasource context')) div.bg-new-panel.py-1\\.5.px-2"
        )

    # --- Tools & Capabilities ---

    @property
    def tools_block(self):
        """Block containing all toolkits under 'TOOLS & CAPABILITIES'."""
        return self.page.locator(
            "p.text-xs.text-text-main.font-semibold:text('TOOLS & CAPABILITIES')"
        ).locator("xpath=..")

    def toolkit_block(self, toolkit_name: str):
        """Returns the block for the toolkit (e.g., 'Git', 'VCS', etc.)."""
        return self.tools_block.locator(
            f"div.text-xs.flex.flex-col.gap-2:has(p.text-sm:has-text('{toolkit_name}'))"
        )

    def toolkit_tool_labels(self, toolkit_name: str):
        """Returns elements for all tool labels under a given toolkit block."""
        return self.toolkit_block(toolkit_name).locator(
            "div.flex.flex-wrap.gap-2 > div"
        )

    def toolkit_tool_label(self, toolkit_name: str, tool_label: str):
        """Returns the div for a specific tool label (exact match, trimmed)."""
        return self.toolkit_block(toolkit_name).locator(
            f"div.flex.flex-wrap.gap-2 > div:text-is('{tool_label}')"
        )

    # --------------------------
    # --- EXPECT/VERIFY ---
    # --------------------------

    @step
    def should_have_all_form_fields_visible(
        self, name: str, author: str, description: str
    ):
        expect(self.assistant_name).to_be_visible()
        expect(self.assistant_name).to_have_text(name)
        expect(self.assistant_author).to_be_visible()
        expect(self.assistant_author).to_have_text(f"by {author}")
        expect(self.about_content).to_be_visible()
        expect(self.about_content).to_have_text(description)
        expect(self.system_instructions_content).to_be_visible()
        return self

    @step
    def should_have_overview_form_fields_visible(
        self, project: str, status: str, assistant_id: str
    ):
        expect(self.overview_project).to_be_visible()
        expect(self.overview_project).to_have_text(project)
        expect(self.overview_shared_status).to_be_visible()
        expect(self.overview_shared_status).to_have_text(status)
        expect(self.overview_assistant_id).to_be_visible()
        expect(self.overview_assistant_id).to_have_value(assistant_id)
        return self

    @step
    def should_have_access_links_form_fields_visible(
        self, assistant_id: str, assistant_name: str
    ):
        expect(self.details_link_input).to_be_visible()
        assert_that(
            self.details_link_input.input_value(), contains_string(assistant_id)
        )
        expect(self.chat_link_input).to_be_visible()
        assert_that(self.chat_link_input.input_value(), contains_string(assistant_name))
        return self

    @step
    def should_have_configuration_form_fields_visible(
        self, temperature: str, top_p: str
    ):
        expect(self.config_temperature).to_be_visible()
        expect(self.config_temperature).to_have_text(temperature)
        expect(self.config_top_p).to_be_visible()
        expect(self.config_top_p).to_have_text(top_p)
        return self

    @step
    def should_see_assistant_name(self, expected):
        expect(self.assistant_name).to_have_text(expected)

    @step
    def should_see_assistant_author(self, expected):
        expect(self.assistant_author).to_have_text(expected)

    @step
    def should_see_about_content(self, expected):
        expect(self.about_content).to_have_text(expected)

    @step
    def should_see_system_instructions(self, expected):
        expect(self.system_instructions_content).to_have_text(expected)

    @step
    def should_see_overview_project(self, expected):
        expect(self.overview_project()).to_have_text(expected)

    @step
    def should_see_overview_shared_status(self, expected):
        expect(self.overview_shared_status()).to_have_text(expected)

    @step
    def should_see_assistant_id(self, expected):
        expect(self.assistant_id_value).to_have_value(expected)

    @step
    def should_see_links(self, details_link, chat_link):
        expect(self.details_link_input()).to_have_value(details_link)
        expect(self.chat_link_input()).to_have_value(chat_link)

    @step
    def should_see_config_llm_model(self, expected):
        expect(self.config_llm_model()).to_have_text(expected)

    @step
    def should_see_config_temperature(self, expected):
        expect(self.config_temperature()).to_have_text(expected)

    @step
    def should_see_config_top_p(self, expected):
        expect(self.config_top_p()).to_have_text(expected)

    @step
    def should_see_toolkit_visible(self, toolkit_name: str):
        """Assert that the toolkit with the given name is visible."""
        expect(self.toolkit_block(toolkit_name)).to_be_visible()

    @step
    def should_see_toolkit_contains(self, toolkit_name: str, tool_label: str):
        """Assert a toolkit contains a tool label (visible)."""
        expect(self.toolkit_tool_label(toolkit_name, tool_label)).to_be_visible()

    @step
    def should_see_tool_not_present(self, toolkit_name: str, tool_label: str):
        """Assert a toolkit does NOT contain a tool label."""
        expect(self.toolkit_tool_label(toolkit_name, tool_label)).not_to_be_visible()

    @step
    def should_see_toolkit_tools(self, toolkit_name: str, expected_tools: list):
        """Assert all expected tool labels are present in a toolkit."""
        for tool in expected_tools:
            self.expect_toolkit_contains(toolkit_name, tool)
