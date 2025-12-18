"""Provider selection screen for onboarding."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Vertical
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from vibe.setup.onboarding.base import OnboardingScreen

# Available providers with their display names and descriptions
PROVIDERS = [
    ("mistral", "Mistral AI", "Official Mistral API (codestral, devstral)"),
    ("watsonx", "IBM WatsonX", "IBM Cloud WatsonX.ai (gpt-oss-120b, granite, llama)"),
    ("llamacpp", "Local (llama.cpp)", "Local llama.cpp server (localhost:8080)"),
]


class ProviderSelectionScreen(OnboardingScreen):
    """Screen for selecting the LLM provider."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("enter", "select", "Select", show=False),
    ]

    # Next screen depends on provider selection - handled dynamically
    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self.selected_provider: str | None = None

    def compose(self) -> ComposeResult:
        options = [
            Option(f"{name}\n[dim]{desc}[/]", id=provider_id)
            for provider_id, name, desc in PROVIDERS
        ]

        self.option_list = OptionList(*options, id="provider-list")

        with Vertical(id="provider-outer"):
            yield Static("", classes="spacer")
            yield Center(Static("Select Your Provider", id="provider-title"))
            yield Static("", classes="spacer-small")
            yield Center(
                Static(
                    "[dim]Choose the LLM provider you want to use[/]",
                    id="provider-subtitle",
                )
            )
            yield Static("", classes="spacer-small")
            yield Center(self.option_list)
            yield Static("", classes="spacer")
            yield Center(
                Static(
                    "[dim]Use arrow keys to navigate, Enter to select[/]",
                    id="provider-hint",
                )
            )

    def on_mount(self) -> None:
        self.option_list.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle provider selection."""
        if event.option.id:
            self.selected_provider = event.option.id
            self._navigate_to_provider_config()

    def action_select(self) -> None:
        """Handle Enter key press."""
        if self.option_list.highlighted is not None:
            option = self.option_list.get_option_at_index(self.option_list.highlighted)
            if option.id:
                self.selected_provider = option.id
                self._navigate_to_provider_config()

    def _navigate_to_provider_config(self) -> None:
        """Navigate to the appropriate configuration screen based on provider."""
        if self.selected_provider == "watsonx":
            # Store selection for later screens
            self.app.selected_provider = self.selected_provider  # type: ignore[attr-defined]
            self.app.push_screen("watsonx_config")
        elif self.selected_provider == "mistral":
            self.app.selected_provider = self.selected_provider  # type: ignore[attr-defined]
            self.app.push_screen("api_key")
        elif self.selected_provider == "llamacpp":
            # Local provider doesn't need API key, go straight to completion
            self.app.selected_provider = self.selected_provider  # type: ignore[attr-defined]
            self._save_local_provider_and_finish()

    def _save_local_provider_and_finish(self) -> None:
        """Save local provider configuration and finish onboarding."""
        # For local provider, we just need to set the active model
        # No API key needed
        self.app.exit("completed:llamacpp")