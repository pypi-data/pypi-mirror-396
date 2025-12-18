"""Model selection screen for onboarding - fetches models dynamically from provider."""

from __future__ import annotations

import os
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Vertical
from textual.widgets import LoadingIndicator, OptionList, Static
from textual.widgets.option_list import Option
from textual.worker import Worker, WorkerState

from vibe.core.llm.backend.watsonx.models import WatsonXModel, fetch_watsonx_models
from vibe.setup.onboarding.base import OnboardingScreen

# Max description length before truncation
MAX_DESC_LENGTH = 60


class ModelSelectionScreen(OnboardingScreen):
    """Screen for selecting a model from the provider's available models."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("r", "refresh", "Refresh", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self, provider: str = "watsonx") -> None:
        super().__init__()
        self.provider = provider
        self.models: list[WatsonXModel] = []
        self.selected_model: str | None = None
        self._fetch_worker: Worker[list[WatsonXModel]] | None = None

    @property
    def loading_indicator(self) -> LoadingIndicator:
        """Get the loading indicator widget."""
        return self.query_one("#model-loading", LoadingIndicator)

    @property
    def status_label(self) -> Static:
        """Get the status widget."""
        return self.query_one("#model-status", Static)

    @property
    def model_list(self) -> OptionList:
        """Get the option list widget."""
        return self.query_one("#model-list", OptionList)

    def compose(self) -> ComposeResult:
        loading = LoadingIndicator(id="model-loading")
        status = Static("Fetching available models...", id="model-status")
        options = OptionList(id="model-list")
        options.display = False

        with Vertical(id="model-outer"):
            yield Static("", classes="spacer")
            yield Center(Static("Select a Model", id="model-title"))
            yield Static("", classes="spacer-small")
            yield Center(status)
            yield Static("", classes="spacer-small")
            yield Center(loading)
            yield Center(options)
            yield Static("", classes="spacer")
            yield Center(
                Static(
                    "[dim]Use arrow keys to navigate, Enter to select, R to refresh[/]",
                    id="model-hint",
                )
            )

    def on_mount(self) -> None:
        self._start_fetch()

    def _start_fetch(self) -> None:
        """Start fetching models from the provider."""
        self.loading_indicator.display = True
        self.model_list.display = False
        self.status_label.update("Fetching available models...")

        if self.provider == "watsonx":
            self._fetch_worker = self.run_worker(
                self._fetch_watsonx_models(),
                name="fetch_models",
                exclusive=True,
            )

    async def _fetch_watsonx_models(self) -> list[WatsonXModel]:
        """Fetch models from WatsonX API."""
        api_key = os.environ.get("WATSONX_API_KEY", "")
        region = os.environ.get("WATSONX_REGION", "us-south")

        if not api_key:
            return []

        try:
            return await fetch_watsonx_models(api_key=api_key, region=region)
        except Exception:
            return []

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.worker.name != "fetch_models":
            return

        if event.state == WorkerState.SUCCESS:
            self.models = event.worker.result or []
            self._populate_model_list()
        elif event.state == WorkerState.ERROR:
            self.loading_indicator.display = False
            self.status_label.update(
                "[red]Failed to fetch models. Press R to retry.[/]"
            )

    def _populate_model_list(self) -> None:
        """Populate the option list with fetched models."""
        self.loading_indicator.display = False
        self.model_list.clear_options()

        if not self.models:
            self.status_label.update(
                "[yellow]No models found. Press R to retry.[/]"
            )
            return

        self.status_label.update(f"[green]Found {len(self.models)} models[/]")
        self.model_list.display = True

        # Group models by provider
        current_provider = ""
        for model in self.models:
            if model.provider != current_provider:
                current_provider = model.provider
                # Add a separator/header for the provider
                self.model_list.add_option(
                    Option(f"── {current_provider.upper()} ──", disabled=True)
                )

            # Create option with model info
            desc = model.short_description[:MAX_DESC_LENGTH] + "..." if len(model.short_description) > MAX_DESC_LENGTH else model.short_description
            label = f"{model.model_id}\n[dim]{desc}[/]"
            self.model_list.add_option(Option(label, id=model.model_id))

        self.model_list.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle model selection."""
        if event.option.id and not event.option.disabled:
            self.selected_model = event.option.id
            self._save_and_finish()

    def action_select(self) -> None:
        """Handle Enter key press."""
        if self.model_list.highlighted is not None:
            option = self.model_list.get_option_at_index(self.model_list.highlighted)
            if option.id and not option.disabled:
                self.selected_model = option.id
                self._save_and_finish()

    def action_refresh(self) -> None:
        """Refresh the model list."""
        self._start_fetch()

    def _save_and_finish(self) -> None:
        """Save the selected model and finish onboarding."""
        if self.selected_model:
            # Pass the selected model back via the exit result
            self.app.exit(f"completed:{self.provider}:{self.selected_model}")