"""WatsonX-specific onboarding screen for API key, project ID, and endpoint configuration."""

from __future__ import annotations

import os
from typing import ClassVar

from dotenv import set_key
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.events import MouseUp
from textual.validation import Length, Regex
from textual.widgets import Input, Link, Select, Static

from vibe.cli.clipboard import copy_selection_to_clipboard
from vibe.core.config_path import GLOBAL_ENV_FILE
from vibe.setup.onboarding.base import OnboardingScreen

# WatsonX regional endpoints
WATSONX_REGIONS = [
    ("us-south", "Dallas (us-south)"),
    ("eu-de", "Frankfurt (eu-de)"),
    ("eu-gb", "London (eu-gb)"),
    ("jp-tok", "Tokyo (jp-tok)"),
    ("au-syd", "Sydney (au-syd)"),
]

WATSONX_DOCS_URL = "https://cloud.ibm.com/apidocs/watsonx-ai"
WATSONX_CONSOLE_URL = "https://cloud.ibm.com/iam/apikeys"

# UUID length for project ID validation
UUID_LENGTH = 36


def _save_env_value(env_key: str, value: str) -> None:
    """Save a single environment variable to the global .env file."""
    GLOBAL_ENV_FILE.path.parent.mkdir(parents=True, exist_ok=True)
    set_key(GLOBAL_ENV_FILE.path, env_key, value)


class WatsonXSetupScreen(OnboardingScreen):
    """Setup screen for WatsonX configuration.

    Collects:
    - WATSONX_API_KEY: IBM Cloud IAM API key
    - WATSONX_PROJECT_ID: WatsonX project ID
    - WATSONX_REGION: Regional endpoint (us-south, eu-de, etc.)
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("tab", "focus_next", "Next field", show=False),
        Binding("shift+tab", "focus_previous", "Previous field", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self._current_field = 0
        self._fields: list[Input | Select] = []

    def compose(self) -> ComposeResult:
        self.api_key_input = Input(
            password=True,
            id="watsonx-api-key",
            placeholder="IBM Cloud IAM API key",
            validators=[Length(minimum=1, failure_description="API key is required.")],
        )

        self.project_id_input = Input(
            id="watsonx-project-id",
            placeholder="WatsonX project ID (UUID format)",
            validators=[
                Length(minimum=1, failure_description="Project ID is required."),
                Regex(
                    r"^[a-f0-9\-]{36}$",
                    failure_description="Project ID should be a UUID (e.g., 12345678-1234-1234-1234-123456789abc)",
                ),
            ],
        )

        self.region_select: Select[str] = Select(
            [(label, value) for value, label in WATSONX_REGIONS],
            id="watsonx-region",
            prompt="Select region",
            value="us-south",
        )

        self._fields = [self.api_key_input, self.project_id_input, self.region_select]

        with Vertical(id="watsonx-setup-outer"):
            yield Center(Static("WatsonX Configuration", id="watsonx-title"))

            with Center():
                with Vertical(id="watsonx-setup-content"):
                    # API Key section
                    yield Static("[bold]1. API Key[/]")
                    yield Horizontal(
                        Static("   Get from: ", classes="link-chevron"),
                        Link(WATSONX_CONSOLE_URL, url=WATSONX_CONSOLE_URL),
                        classes="link-row",
                    )
                    yield self.api_key_input

                    # Project ID section
                    yield Static("[bold]2. Project ID[/]")
                    yield Static(
                        "[dim]   Find in your WatsonX project settings[/]",
                        classes="field-hint",
                    )
                    yield self.project_id_input

                    # Region section
                    yield Static("[bold]3. Region[/]")
                    yield self.region_select

                    yield Static("", id="feedback")
                    yield Static(
                        "[dim]Tab: next field | Enter: submit[/]",
                        id="hint",
                    )

    def on_mount(self) -> None:
        self.api_key_input.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._update_feedback()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Move to next field or submit if all valid
        if self._all_fields_valid():
            self._save_and_finish()
        else:
            self.screen.focus_next()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._update_feedback()

    def _update_feedback(self) -> None:
        """Update the feedback message based on current field states."""
        feedback = self.query_one("#feedback", Static)

        api_key_valid = bool(self.api_key_input.value.strip())
        project_id_value = self.project_id_input.value.strip()
        project_id_valid = bool(project_id_value) and len(project_id_value) >= UUID_LENGTH

        if api_key_valid and project_id_valid:
            feedback.update("[green]Press Enter to save configuration[/]")
        elif not api_key_valid:
            feedback.update("[dim]Enter your IBM Cloud API key[/]")
        elif not project_id_valid:
            feedback.update("[dim]Enter your WatsonX project ID[/]")
        else:
            feedback.update("")

    def _all_fields_valid(self) -> bool:
        """Check if all required fields have valid values."""
        api_key = self.api_key_input.value.strip()
        project_id = self.project_id_input.value.strip()
        region = self.region_select.value

        return bool(api_key) and bool(project_id) and region != Select.BLANK

    def _save_and_finish(self) -> None:
        """Save all WatsonX configuration to environment and .env file."""
        api_key = self.api_key_input.value.strip()
        project_id = self.project_id_input.value.strip()
        region = str(self.region_select.value)

        # Set in current environment
        os.environ["WATSONX_API_KEY"] = api_key
        os.environ["WATSONX_PROJECT_ID"] = project_id
        os.environ["WATSONX_REGION"] = region

        # Persist to .env file
        try:
            _save_env_value("WATSONX_API_KEY", api_key)
            _save_env_value("WATSONX_PROJECT_ID", project_id)
            _save_env_value("WATSONX_REGION", region)
        except OSError as err:
            self.app.exit(f"save_error:{err}")
            return

        # Navigate to model selection screen
        self.app.push_screen("model_selection")

    def on_mouse_up(self, event: MouseUp) -> None:
        copy_selection_to_clipboard(self.app)