from __future__ import annotations

import sys

from rich import print as rprint
from textual.app import App

from vibe.core.config import VibeConfig
from vibe.core.config_path import GLOBAL_ENV_FILE
from vibe.setup.onboarding.screens import (
    ApiKeyScreen,
    ModelSelectionScreen,
    ProviderSelectionScreen,
    ThemeSelectionScreen,
    WatsonXSetupScreen,
    WelcomeScreen,
)


class OnboardingApp(App[str | None]):
    CSS_PATH = "onboarding.tcss"

    # Track selected provider across screens
    selected_provider: str | None = None

    def on_mount(self) -> None:
        # Install all screens
        self.install_screen(WelcomeScreen(), "welcome")
        self.install_screen(ThemeSelectionScreen(), "theme_selection")
        self.install_screen(ProviderSelectionScreen(), "provider_selection")

        # Provider-specific config screens
        self.install_screen(ApiKeyScreen(), "api_key")
        self.install_screen(WatsonXSetupScreen(), "watsonx_config")

        # Model selection (used after provider config)
        self.install_screen(ModelSelectionScreen(provider="watsonx"), "model_selection")

        self.push_screen("welcome")


def run_onboarding(app: App | None = None) -> None:
    result = (app or OnboardingApp()).run()
    match result:
        case None:
            rprint("\n[yellow]Setup cancelled. See you next time![/]")
            sys.exit(0)
        case str() as s if s.startswith("save_error:"):
            err = s.removeprefix("save_error:")
            rprint(
                f"\n[yellow]Warning: Could not save configuration to .env file: {err}[/]"
                "\n[dim]Configuration is set for this session only. "
                f"You may need to set it manually in {GLOBAL_ENV_FILE.path}[/]\n"
            )
        case str() as s if s.startswith("completed:"):
            # Parse completion result: "completed:provider" or "completed:provider:model"
            parts = s.removeprefix("completed:").split(":", 1)
            provider = parts[0]
            model = parts[1] if len(parts) > 1 else None
            _apply_provider_config(provider, model)
        case "completed":
            pass


def _apply_provider_config(provider: str, model: str | None = None) -> None:
    """Apply provider-specific configuration after onboarding.

    Args:
        provider: The selected provider (mistral, watsonx, llamacpp)
        model: The selected model ID, or None to use default
    """
    # Use selected model or fall back to provider default
    if model:
        selected_model = model
    else:
        # Map providers to their default models
        provider_default_models = {
            "mistral": "mistral-vibe-cli-latest",
            "watsonx": "openai/gpt-oss-120b",
            "llamacpp": "devstral",
        }
        selected_model = provider_default_models.get(provider)

    if selected_model:
        try:
            # For WatsonX, we need to ensure the model is added to config if it's dynamic
            _ensure_model_in_config(provider, selected_model)
            VibeConfig.save_updates({"active_model": selected_model})
            rprint(f"[green]Configuration saved! Using model: {selected_model}[/]")
        except OSError as e:
            rprint(f"[yellow]Warning: Could not save active model: {e}[/]")


def _ensure_model_in_config(provider: str, model_id: str) -> None:
    """Ensure a dynamically selected model exists in the config.

    If the model was fetched dynamically and isn't in the default config,
    we need to add it.
    """
    try:
        config = VibeConfig.load()

        # Check if model already exists
        for m in config.models:
            if m.name == model_id:
                return  # Already exists

        # Add the new model to config
        from vibe.core.config import ModelConfig

        new_model = ModelConfig(
            name=model_id,
            provider=provider,
            alias=model_id,  # Use model_id as alias
            input_price=0.0,  # Unknown pricing for dynamic models
            output_price=0.0,
        )

        # Update config with the new model
        updated_models = list(config.models) + [new_model]
        VibeConfig.save_updates({"models": [m.model_dump() for m in updated_models]})

    except Exception:
        # If we can't update config, the model might still work if it's in defaults
        pass
