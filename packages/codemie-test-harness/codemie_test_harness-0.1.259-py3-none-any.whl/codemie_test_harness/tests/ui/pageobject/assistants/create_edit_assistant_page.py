from typing import Optional

from playwright.sync_api import expect, Locator
from reportportal_client import step

from codemie_test_harness.tests.ui.pageobject.assistants.generate_with_ai_modal import (
    AIAssistantGeneratorPage,
)
from codemie_test_harness.tests.ui.pageobject.base_page import BasePage
from codemie_test_harness.tests.ui.pageobject.assistants.assistant_mcp_server import (
    AssistantMCPIntegrationModal,
)
from codemie_test_harness.tests.ui.pageobject.assistants.assistant_sidebar import (
    AssistantSidebar,
)


class CreateEditAssistantPage(BasePage):
    """
    Create/Edit Assistant page object following Page Object Model (POM) best practices.

    This class encapsulates all interactions with the Create Assistant page,
    providing a clean interface for test automation while hiding implementation details.
    Updated with accurate locators based on real HTML structure.
    """

    page_url = "/#/assistants/new"

    def __init__(self, page):
        """Initialize the Create Assistant page object."""
        super().__init__(page)
        self.sidebar = AssistantSidebar(page)
        self.mcp = AssistantMCPIntegrationModal(page)
        self.ai_generator_modal = AIAssistantGeneratorPage(
            page
        )  # AI Assistant Generator modal

    # =============================================================================
    # LOCATORS - Core Page Elements
    # =============================================================================

    @property
    def main_container(self) -> Locator:
        """Main page container"""
        return self.page.locator("main.flex.flex-col.h-full.flex-1")

    @property
    def page_title(self) -> Locator:
        """Page title 'Create Assistant' element"""
        return self.page.locator(
            'h1.text-h3.text-text-main.font-semibold:has-text("Create Assistant")'
        )

    @property
    def generate_with_ai_button(self) -> Locator:
        """Generate with AI button in header with magical styling"""
        return self.page.locator(
            'button.bg-magical-button:has-text("Generate with AI")'
        ).first

    @property
    def create_button(self) -> Locator:
        """Create button with plus icon (primary button)"""
        return self.page.locator('button.bg-button-primary-bg:has-text("Create")')

    @property
    def save_button(self) -> Locator:
        """Save button"""
        return self.page.locator('button.bg-button-primary-bg:has-text("Save")')

    @property
    def cancel_button(self) -> Locator:
        """Cancel button"""
        return self.page.locator('button.bg-button-secondary-bg:has-text("Cancel")')

    @property
    def back_button(self) -> Locator:
        """Back button"""
        return self.page.locator(
            'button.bg-button-secondary-bg:has(svg[viewBox="0 0 18 18"])'
        )

    # =============================================================================
    # LOCATORS - Assistant Setup Section
    # =============================================================================

    @property
    def assistant_setup_section(self) -> Locator:
        """Assistant Setup section header"""
        return self.page.locator('h4:has-text("Assistant Setup")')

    @property
    def shared_toggle(self) -> Locator:
        """'Shared with project' toggle switch - returns the label which is clickable"""
        return self.page.locator('label:has-text("Shared with project")')

    @property
    def shared_toggle_checkbox(self) -> Locator:
        """'Shared with project' checkbox input (hidden) - use for checking state only"""
        return self.page.locator(
            'label:has-text("Shared with project") input[type="checkbox"]'
        )

    @property
    def name_input(self) -> Locator:
        """Assistant name input field with data-testid validation"""
        return self.page.locator('input[placeholder="Name*"]')

    @property
    def slug_input(self) -> Locator:
        """Assistant slug input field"""
        return self.page.locator('input[name="slug"]')

    @property
    def icon_url_input(self) -> Locator:
        """Assistant icon URL input field"""
        return self.page.locator('input[name="icon_url"]')

    @property
    def description_textarea(self) -> Locator:
        """Assistant description textarea with placeholder"""
        return self.page.locator(
            'textarea[name="description"][placeholder="Description*"]'
        )

    @property
    def categories_dropdown(self) -> Locator:
        """Categories selection multiselect dropdown"""
        return self.page.locator(
            'div.p-multiselect:has(div.p-multiselect-label:has-text("Select categories"))'
        )

    @property
    def conversation_starters_input(self) -> Locator:
        """Conversation starters input field with InputGroup"""
        return self.page.locator('input[name="conversation_starters"]')

    @property
    def add_conversation_starter_button(self) -> Locator:
        """Add conversation starter button with plus icon"""
        return self.page.locator(
            'label:has-text("Conversation starters") + button:has-text("Add")'
        )

    @property
    def delete_conversation_starter_button(self) -> Locator:
        """Delete conversation starter button (trash icon in InputGroup)"""
        return self.page.locator(".p-inputgroup button.bg-button-secondary-bg:has(svg)")

    @property
    def name_error_message(self):
        """Name field error message."""
        return self.page.locator(
            'label:has(input[name="name"]) div.text-sm.text-error-main.input-error-message'
        )

    @property
    def icon_error_message(self):
        """Icon field error message."""
        return self.page.locator(
            'label:has(input[name="icon_url"]) div.text-sm.text-error-main.input-error-message'
        )

    @property
    def description_error_message(self):
        """Description field error message."""
        return self.page.locator(
            'div:has(textarea[name="description"][placeholder="Description*"]) div.text-fire-50.text-sm'
        )

    @property
    def system_prompt_error_message(self):
        """System prompt field error message."""
        return self.page.locator(
            'div:has(textarea[placeholder="System Instructions*"]) div.text-fire-50.text-sm'
        )

    @property
    def temperature_error_message(self):
        """Temperature field error message."""
        return self.page.locator(
            'label:has(input[name="temperature"]) div.text-sm.text-error-main.input-error-message'
        )

    @property
    def top_p_error_message(self):
        """Top P field error message."""
        return self.page.locator(
            'label:has(input[name="top_p"]) div.text-sm.text-error-main.input-error-message'
        )

    # =============================================================================
    # LOCATORS - Behavior & Logic Section
    # =============================================================================

    @property
    def behavior_logic_section(self) -> Locator:
        """Behavior & Logic section header"""
        return self.page.locator('h4:has-text("Behavior & Logic")')

    @property
    def system_instructions_label(self) -> Locator:
        """System Instructions label"""
        return self.page.locator(
            'p.text-sm.font-semibold:has-text("System Instructions")'
        )

    @property
    def system_prompt_textarea(self) -> Locator:
        """System instructions textarea with full height"""
        return self.page.locator('textarea[placeholder="System Instructions*"]')

    @property
    def generate_with_ai_system_instructions_button(self) -> Locator:
        """Generate with AI button for system instructions"""
        return self.page.locator(
            'button.bg-magical-button:has-text("Generate with AI")'
        ).nth(1)

    @property
    def expand_system_prompt_button(self) -> Locator:
        """Expand system prompt button"""
        return self.page.locator('button.bg-button-secondary-bg:has-text("Expand")')

    @property
    def current_user_prompt_var_button(self) -> Locator:
        """Current User prompt variable button"""
        return self.page.locator('button:has-text("Current User")')

    @property
    def date_prompt_var_button(self) -> Locator:
        """Date prompt variable button"""
        return self.page.locator('button:has-text("Date")')

    @property
    def manage_prompt_vars_button(self) -> Locator:
        """Manage Prompt Vars button"""
        return self.page.locator(
            'button.bg-button-primary-bg:has-text("Manage Prompt Vars")'
        )

    @property
    def llm_model_dropdown(self) -> Locator:
        """LLM model selection dropdown"""
        return self.page.locator(
            'div.p-multiselect:has(div.p-multiselect-label:has-text("Default: GPT-4.1"))'
        )

    @property
    def temperature_input(self) -> Locator:
        """Temperature input field (0-2 range)"""
        return self.page.locator('input[name="temperature"][placeholder="0-2"]')

    @property
    def top_p_input(self) -> Locator:
        """Top P input field (0-1 range)"""
        return self.page.locator('input[name="top_p"][placeholder="0-1"]')

    # ==================== DataSource Context ====================
    @property
    def datasource_context_label(self):
        """Label 'Datasource Context' above the dropdown."""
        return self.page.locator(
            'div.text-xs.text-text-secondary:has-text("Datasource Context")'
        )

    @property
    def datasource_context_add_button(self):
        """'Add' button next to the Datasource Context label."""
        return self.page.locator(
            'div:has-text("Datasource Context") + button:has-text("Add")'
        )

    @property
    def datasource_context_dropdown(self):
        """Datasource Context dropdown (multiselect input)."""
        return self.page.locator("div.p-multiselect#context-selector")

    @property
    def datasource_context_dropdown_label(self):
        """The visible label text inside the datasource context dropdown."""
        return self.datasource_context_dropdown.locator("div.p-multiselect-label")

    # ==================== Sub-Assistant Context ====================
    @property
    def sub_assistants_label(self):
        """Label 'Sub-Assistants' above the sub assistants dropdown."""
        return self.page.get_by_text("Sub-Assistants", exact=True)

    @property
    def sub_assistants_dropdown(self):
        """Sub Assistants dropdown (multiselect input)."""
        return self.page.locator(
            'div.p-multiselect:has(div.p-multiselect-label:has-text("Select Sub-Assistants"))'
        )

    @property
    def sub_assistants_dropdown_label(self):
        """The label inside the sub assistants dropdown."""
        return self.sub_assistants_dropdown.locator("div.p-multiselect-label")

    # ======= Tools Accordion Locators =======

    @property
    def available_tools_accordion(self) -> Locator:
        """Available Tools accordion section"""
        return self.page.locator(
            'div.p-accordion-header:has(h1.font-bold:has-text("Available Tools"))'
        )

    @property
    def external_tools_accordion(self) -> Locator:
        """External Tools accordion section"""
        return self.page.locator(
            'div.p-accordion-header:has(h1.font-bold:has-text("External Tools"))'
        )

    @step
    def section(self, name: str) -> Locator:
        """Get main accordion section (Available Tools or External Tools) by name"""
        return self.page.locator(
            f'div.p-accordion-header:has(h1.font-bold.text-text-quaternary:has-text("{name}"))'
        )

    @step
    def toolkit(self, section_name: str, toolkit_name: str) -> Locator:
        """Get toolkit accordion header within a section by name
        Handles both spaced and non-spaced toolkit names (e.g., 'Open API' vs 'OpenAPI')"""
        # Try the exact name first, if not found try without spaces
        toolkit_name_no_space = toolkit_name.replace(" ", "")
        # Look for h2 with the toolkit name, which is inside the accordion header
        return self.page.locator(
            f'div.p-accordion-header:has(h2.font-medium:text-is("{toolkit_name}")),'
            f'div.p-accordion-header:has(h2.font-medium:text-is("{toolkit_name_no_space}"))'
        ).first

    @step
    def tool_rows_under_toolkit(self, toolkit_name: str) -> Locator:
        """Returns all tool rows (each with a label and a checkbox) under an expanded toolkit panel."""
        panel = self.page.locator(
            "div.p-accordion-tab.p-accordion-tab-active div.p-accordion-content"
        ).filter(has_text=toolkit_name)
        return panel.locator(
            "div.grid.grid-cols-[auto,1fr]"
        )  # Adapt selector to match tool row

    @step
    def tool_label_spans_under_toolkit(self, tool: str) -> Locator:
        tool_stripped = tool.strip()
        if "mcp" in tool_stripped.lower():
            return (
                self.page.locator("div.p-accordion-tab-active div.p-accordion-content")
                .locator('button, [id*="mcp"]')
                .filter(has_text=tool_stripped)
                .first
            )
        return self.page.locator(
            "div.p-accordion-tab-active div.p-accordion-content label"
        ).get_by_text(tool_stripped, exact=True)

    @step
    def tool_checkbox(self, tool_name: str) -> Locator:
        return (
            self.page.locator("span")
            .filter(has_text=tool_name)
            .locator("xpath=..")
            .locator("input[type=checkbox]")
        )

    @step
    def tool_row(self, tool_name: str) -> Locator:
        return (
            self.page.locator("span")
            .filter(has_text=tool_name)
            .locator("xpath=ancestor::div[contains(@class,'grid')]")
        )

    @step
    def select_section(self, section_name: str):
        self.section(section_name).click()
        return self

    @step
    def select_toolkit(self, section: str, toolkit: str):
        self.toolkit(section, toolkit).click()
        return self

    @step
    def should_be_visible_tool(self, tool: str):
        expect(self.tool_label_spans_under_toolkit(tool)).to_be_visible()
        return self

    @step
    def select_tool(self, tool: str):
        self.tool_label_spans_under_toolkit(tool).click()
        if self.mcp.is_pop_visible():
            self.mcp.fill_mcp_server_base_form()
        return self

    # ==================== NAVIGATION METHODS ====================

    @step
    def navigate_to(self):
        """
        Navigate to the Create Assistant page.

        Returns:
            self: Returns the page object for method chaining
        """
        self.page.goto(self.page_url)
        self.wait_for_page_load()

        # Handle AI Generator modal if it appears
        self.handle_ai_generator_modal_if_visible()

        return self

    # ==================== AI GENERATOR MODAL METHODS ====================

    @step
    def is_ai_generator_modal_visible(self) -> bool:
        """
        Check if the AI Assistant Generator modal is currently visible.

        Returns:
            bool: True if modal is visible, False otherwise
        """
        return self.ai_generator_modal.is_modal_visible()

    @step
    def close_ai_generator_modal(self):
        """
        Close the AI Assistant Generator modal if it's visible.

        Returns:
            self: Returns the page object for method chaining
        """
        if self.is_ai_generator_modal_visible():
            self.ai_generator_modal.close_modal()
        return self

    @step
    def handle_ai_generator_modal_if_visible(self):
        """
        Handle the AI Generator modal if it appears when navigating to Create Assistant page.
        This method will close the modal to proceed with manual assistant creation.

        Returns:
            self: Returns the page object for method chaining
        """
        # Wait a short moment for modal to potentially appear
        self.page.wait_for_timeout(1000)

        if self.is_ai_generator_modal_visible():
            # Modal is visible, close it to proceed with manual creation
            self.close_ai_generator_modal()

            # Wait for modal to fully disappear before proceeding
            self.page.wait_for_timeout(500)

        return self

    @step
    def verify_ai_generator_modal_visible(self):
        """
        Verify that the AI Assistant Generator modal is visible with correct structure.

        Returns:
            self: Returns the page object for method chaining
        """
        assert self.is_ai_generator_modal_visible(), (
            "AI Assistant Generator modal should be visible"
        )

        # Verify modal structure using updated methods
        self.ai_generator_modal.verify_modal_title()
        self.ai_generator_modal.verify_description_text()
        self.ai_generator_modal.verify_prompt_label()
        self.ai_generator_modal.verify_note_text()

        return self

    @step
    def verify_ai_generator_modal_not_visible(self):
        """
        Verify that the AI Assistant Generator modal is not visible.

        Returns:
            self: Returns the page object for method chaining
        """
        assert not self.is_ai_generator_modal_visible(), (
            "AI Assistant Generator modal should not be visible"
        )
        return self

    @step
    def create_manually_from_ai_modal(self):
        """
        Click 'Create Manually' from the AI Generator modal to proceed with manual creation.

        Returns:
            self: Returns the page object for method chaining
        """
        if self.is_ai_generator_modal_visible():
            self.ai_generator_modal.click_create_manually()
            # Wait for the modal to close and manual form to appear
            self.page.wait_for_timeout(1000)
        return self

    @step
    def generate_with_ai_from_modal(
        self,
        description: str,
        include_tools: bool = True,
        do_not_show_again: bool = False,
    ):
        """
        Use the AI Generator modal to create an assistant with AI.

        Args:
            description: Description of the assistant to generate
            include_tools: Whether to include tools in the assistant
            do_not_show_again: Whether to check 'do not show popup' option

        Returns:
            self: Returns the page object for method chaining
        """
        if self.is_ai_generator_modal_visible():
            self.ai_generator_modal.complete_ai_generation_workflow(
                prompt=description,
                include_tools=include_tools,
                dont_show_again=do_not_show_again,
            )
        return self

    # ==================== FORM INTERACTION METHODS ====================

    @step
    def fill_name(self, name: str):
        """
        Fill the assistant name field.

        Args:
            name: The name for the assistant

        Returns:
            self: Returns the page object for method chaining
        """
        self.name_input.clear()
        self.name_input.fill(name)
        return self

    @step
    def fill_description(self, description: str):
        """
        Fill the assistant description field.

        Args:
            description: The description for the assistant

        Returns:
            self: Returns the page object for method chaining
        """
        self.description_textarea.clear()
        self.description_textarea.fill(description)
        return self

    @step
    def fill_system_prompt(self, prompt: str):
        """
        Fill the system prompt field.

        Args:
            prompt: The system prompt text

        Returns:
            self: Returns the page object for method chaining
        """
        self.system_prompt_textarea.clear()
        self.system_prompt_textarea.fill(prompt)
        return self

    @step
    def fill_icon_url(self, icon_url: str):
        """
        Fill the icon URL field.

        Args:
            icon_url: The URL for the assistant icon

        Returns:
            self: Returns the page object for method chaining
        """
        self.icon_url_input.clear()
        self.icon_url_input.fill(icon_url)
        return self

    @step
    def fill_slug(self, slug: str):
        """
        Fill the slug field.

        Args:
            slug: The unique identifier for the assistant

        Returns:
            self: Returns the page object for method chaining
        """
        self.slug_input.clear()
        self.slug_input.fill(slug)
        return self

    @step
    def toggle_shared_assistant(self, shared: bool = True):
        """
        Toggle the shared/public setting for the assistant.

        Args:
            shared: Whether the assistant should be shared (True) or private (False)

        Returns:
            self: Returns the page object for method chaining
        """
        # Check current state using the hidden checkbox and toggle if needed by clicking the label
        is_currently_checked = self.shared_toggle_checkbox.is_checked()
        if (shared and not is_currently_checked) or (
            not shared and is_currently_checked
        ):
            self.shared_toggle.click()
        return self

    @step
    def fill_temperature(self, temperature: str):
        """
        Fill the temperature field.

        Args:
            temperature: Temperature value (0-2)

        Returns:
            self: Returns the page object for method chaining
        """
        self.temperature_input.clear()
        self.temperature_input.fill(temperature)
        return self

    @step
    def fill_top_p(self, top_p: str):
        """
        Fill the Top P field.

        Args:
            top_p: Top P value (0-1)

        Returns:
            self: Returns the page object for method chaining
        """
        self.top_p_input.clear()
        self.top_p_input.fill(top_p)
        return self

    # ==================== ACTION METHODS ====================

    @step
    def click_create(self):
        """
        Click the Create button to create the assistant.

        Returns:
            self: Returns the page object for method chaining
        """
        self.create_button.click()
        return self

    @step
    def click_save(self):
        """
        Click the Create button to create the assistant.

        Returns:
            self: Returns the page object for method chaining
        """
        self.save_button.click()
        return self

    @step
    def click_cancel(self):
        """
        Click the Cancel button to abort assistant creation.

        Returns:
            self: Returns the page object for method chaining
        """
        self.cancel_button.click()
        return self

    @step
    def click_back(self):
        """
        Click the Back button to return to assistants list.

        Returns:
            self: Returns the page object for method chaining
        """
        self.back_button.click()
        return self

    @step
    def click_generate_with_ai_header(self):
        """
        Click the Generate with AI button in the header.

        Returns:
            self: Returns the page object for method chaining
        """
        self.generate_with_ai_button.click()
        return self

    def select_tool_option(self, toolkit_name: str, label: str, checked: bool = True):
        self.expand_toolkit(toolkit_name)
        checkbox = self.toolkit_checkbox_by_label(toolkit_name, label)
        if checked != checkbox.is_checked():
            checkbox.click()
        return self

    def get_all_tools_in_toolkit(self, toolkit_name: str):
        """
        Returns a list of tuples (label, checked) for all tool features inside a toolkit accordion.
        """
        panel = self.toolkit_accordion_panel(toolkit_name)
        labels = panel.locator(".checkbox-label span.text-sm").all_text_contents()
        checkboxes = panel.locator('input[type="checkbox"]')
        return [
            (lbl, checkboxes.nth(idx).is_checked()) for idx, lbl in enumerate(labels)
        ]

    def toolkit_select_all_checkbox(self, toolkit_name: str):
        return self.toolkit_checkbox_by_label(toolkit_name, "Select all")

    # ==================== COMPREHENSIVE ASSISTANT CREATION METHOD ====================

    @step
    def create_assistant(
        self,
        name: str,
        description: str,
        system_prompt: str,
        icon_url: Optional[str] = None,
        shared: bool = False,
        temperature: Optional[str] = None,
        top_p: Optional[str] = None,
    ):
        """
        Complete assistant creation workflow with all required parameters.

        This method encapsulates the entire assistant creation process,
        following the critical happy path scenario outlined in the requirements.

        Args:
            name: Assistant name (required)
            description: Assistant description (required)
            system_prompt: System prompt for the assistant (required)
            slug: Optional unique identifier for the assistant
            icon_url: Optional icon URL for the assistant
            shared: Whether to make the assistant shared/public (default: False)
            temperature: Optional temperature value (0-2)
            top_p: Optional Top P value (0-1)

        Returns:
            self: Returns the page object for method chaining
        """
        # Fill essential required fields
        self.fill_name(name)
        self.fill_description(description)
        self.fill_system_prompt(system_prompt)

        # Fill optional fields if provided
        # if icon_url:
        #     self.fill_icon_url(icon_url)
        # if temperature:
        #     self.fill_temperature(temperature)
        # if top_p:
        #     self.fill_top_p(top_p)

        # Set sharing preference
        self.toggle_shared_assistant(shared)

        # Submit the form
        self.click_create()

        return self

    # ==================== VERIFICATION METHODS ====================

    @step
    def should_be_on_create_assistant_page(self):
        """Verify that we are on the Create Assistant page."""
        expect(self.page_title).to_be_visible()
        expect(self.page).to_have_url(f"{self.page_url}")
        return self

    @step
    def should_have_all_form_fields_visible(self):
        """Verify that all essential form fields are visible."""
        expect(self.name_input).to_be_visible()
        expect(self.slug_input).to_be_visible()
        expect(self.description_textarea).to_be_visible()
        expect(self.system_prompt_textarea).to_be_visible()
        return self

    @step
    def should_have_action_buttons_visible(self):
        """Verify that action buttons (Create, Cancel) are visible."""
        expect(self.create_button).to_be_visible()
        expect(self.cancel_button).to_be_visible()
        return self

    @step
    def should_have_name_value(self, expected_name: str):
        """Verify name field has expected value."""
        expect(self.name_input).to_have_value(expected_name)
        return self

    @step
    def should_have_description_value(self, expected_description: str):
        """Verify description field has expected value."""
        expect(self.description_textarea).to_have_value(expected_description)
        return self

    @step
    def should_have_system_prompt_value(self, expected_prompt: str):
        """Verify system prompt field has expected value."""
        expect(self.system_prompt_textarea).to_have_value(expected_prompt)
        return self

    @step
    def should_have_categories_visible(self):
        """Verify categories dropdown is visible.."""
        expect(self.categories_dropdown).to_be_visible()
        return self

    @step
    def should_have_icon_url_value(self, expected_url: str):
        """Verify icon URL field has expected value."""
        expect(self.icon_url_input).to_have_value(expected_url)
        return self

    @step
    def should_have_shared_checked(self):
        """Verify shared toggle is checked."""
        expect(self.shared_toggle_checkbox).to_be_checked()
        return self

    @step
    def should_have_shared_unchecked(self):
        """Verify shared toggle is unchecked."""
        expect(self.shared_toggle_checkbox).not_to_be_checked()
        return self

    @step
    def should_have_create_button_enabled(self):
        """Verify create button is enabled."""
        expect(self.create_button).to_be_enabled()
        return self

    @step
    def should_have_create_button_disabled(self):
        """Verify create button is disabled."""
        expect(self.create_button).to_be_disabled()
        return self

    @step
    def should_have_cancel_button_enabled(self):
        """Verify cancel button is enabled."""
        expect(self.cancel_button).to_be_enabled()
        return self

    @step
    def should_have_empty_fields(self):
        """Verify all form fields are empty."""
        expect(self.name_input).to_have_value("")
        expect(self.description_textarea).to_have_value("")
        expect(self.system_prompt_textarea).to_have_value("")
        expect(self.icon_url_input).to_have_value("")
        return self

    @step
    def should_have_top_p_and_temperature(self):
        """Verify top p and temperature fields are visible."""
        expect(self.temperature_input).to_be_visible()
        expect(self.top_p_input).to_be_visible()
        return self

    @step
    def should_have_top_p_and_temperature_value(self, temperature: str, top_p: str):
        """Verify top p and temperature field values is visible."""
        expect(self.temperature_input).to_have_value(temperature)
        expect(self.top_p_input).to_have_value(top_p)

    @step
    def should_have_datasource_context(self):
        """Verify datasource context fields are visible."""
        expect(self.datasource_context_label).to_be_visible()
        expect(self.datasource_context_add_button).to_be_visible()
        expect(self.datasource_context_dropdown).to_be_visible()
        return self

    @step
    def should_have_sub_assistants_context(self):
        """Verify sub assistants context fields are visible."""
        expect(self.sub_assistants_label).to_be_visible()
        expect(self.sub_assistants_dropdown).to_be_visible()
        return self

    @step
    def should_have_name_error_textarea(self, error_message: str):
        """Verify name error text field is visible."""
        expect(self.name_error_message).to_be_visible()
        expect(self.name_error_message).to_have_text(error_message)
        return self

    @step
    def should_have_description_error_textarea(self, error_message: str):
        """Verify description error text field is visible."""
        expect(self.description_error_message).to_be_visible()
        expect(self.description_error_message).to_have_text(error_message)
        return self

    @step
    def should_have_system_prompt_error_textarea(self, error_message: str):
        """Verify system prompt error text field is visible."""
        expect(self.system_prompt_error_message).to_be_visible()
        expect(self.system_prompt_error_message).to_have_text(error_message)
        return self

    @step
    def should_have_icon_error_textarea(self, error_message: str):
        """Verify icon error text field is visible."""
        expect(self.icon_error_message).to_be_visible()
        expect(self.icon_error_message).to_have_text(error_message)
        return self

    @step
    def should_have_temperature_error_textarea(self, error_message: str):
        """Verify temperature error text field is visible."""
        expect(self.temperature_error_message).to_be_visible()
        expect(self.temperature_error_message).to_have_text(error_message)
        return self

    @step
    def should_have_top_p_error_textarea(self, error_message: str):
        """Verify top p error text field is visible."""
        expect(self.top_p_error_message).to_be_visible()
        expect(self.top_p_error_message).to_have_text(error_message)
        return self
