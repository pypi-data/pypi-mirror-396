from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from vibe.core.utils import VIBE_WARNING_TAG

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from vibe.core.config import VibeConfig
    from vibe.core.types import AgentStats, LLMMessage

logger = logging.getLogger(__name__)


class MiddlewareAction(StrEnum):
    CONTINUE = auto()
    STOP = auto()
    COMPACT = auto()
    INJECT_MESSAGE = auto()
    ENHANCE_RESPONSE = auto()  # Silently re-run LLM with additional context


class ResetReason(StrEnum):
    STOP = auto()
    COMPACT = auto()


@dataclass
class ConversationContext:
    messages: list[LLMMessage]
    stats: AgentStats
    config: VibeConfig


@dataclass
class MiddlewareResult:
    action: MiddlewareAction = MiddlewareAction.CONTINUE
    message: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ConversationMiddleware(Protocol):
    async def before_turn(self, context: ConversationContext) -> MiddlewareResult: ...

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult: ...

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None: ...


class TurnLimitMiddleware:
    def __init__(self, max_turns: int) -> None:
        self.max_turns = max_turns

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if context.stats.steps - 1 >= self.max_turns:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Turn limit of {self.max_turns} reached",
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        pass


class PriceLimitMiddleware:
    def __init__(self, max_price: float) -> None:
        self.max_price = max_price

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if context.stats.session_cost > self.max_price:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Price limit exceeded: ${context.stats.session_cost:.4f} > ${self.max_price:.2f}",
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        pass


class AutoCompactMiddleware:
    def __init__(self, threshold: int) -> None:
        self.threshold = threshold

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if context.stats.context_tokens >= self.threshold:
            return MiddlewareResult(
                action=MiddlewareAction.COMPACT,
                metadata={
                    "old_tokens": context.stats.context_tokens,
                    "threshold": self.threshold,
                },
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        pass


class ContextWarningMiddleware:
    def __init__(
        self, threshold_percent: float = 0.5, max_context: int | None = None
    ) -> None:
        self.threshold_percent = threshold_percent
        self.max_context = max_context
        self.has_warned = False

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if self.has_warned:
            return MiddlewareResult()

        max_context = self.max_context
        if max_context is None:
            return MiddlewareResult()

        if context.stats.context_tokens >= max_context * self.threshold_percent:
            self.has_warned = True

            percentage_used = (context.stats.context_tokens / max_context) * 100
            warning_msg = f"<{VIBE_WARNING_TAG}>You have used {percentage_used:.0f}% of your total context ({context.stats.context_tokens:,}/{max_context:,} tokens)</{VIBE_WARNING_TAG}>"

            return MiddlewareResult(
                action=MiddlewareAction.INJECT_MESSAGE, message=warning_msg
            )

        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        self.has_warned = False


class MiddlewarePipeline:
    def __init__(self) -> None:
        self.middlewares: list[ConversationMiddleware] = []

    def add(self, middleware: ConversationMiddleware) -> MiddlewarePipeline:
        self.middlewares.append(middleware)
        return self

    def clear(self) -> None:
        self.middlewares.clear()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        for mw in self.middlewares:
            mw.reset(reset_reason)

    async def run_before_turn(self, context: ConversationContext) -> MiddlewareResult:
        messages_to_inject = []

        for mw in self.middlewares:
            result = await mw.before_turn(context)
            if result.action == MiddlewareAction.INJECT_MESSAGE and result.message:
                messages_to_inject.append(result.message)
            elif result.action in {MiddlewareAction.STOP, MiddlewareAction.COMPACT}:
                return result
        if messages_to_inject:
            combined_message = "\n\n".join(messages_to_inject)
            return MiddlewareResult(
                action=MiddlewareAction.INJECT_MESSAGE, message=combined_message
            )

        return MiddlewareResult()

    async def run_after_turn(self, context: ConversationContext) -> MiddlewareResult:
        messages_to_inject = []

        for mw in self.middlewares:
            result = await mw.after_turn(context)
            if result.action == MiddlewareAction.INJECT_MESSAGE and result.message:
                messages_to_inject.append(result.message)
            elif result.action in {
                MiddlewareAction.STOP,
                MiddlewareAction.COMPACT,
                MiddlewareAction.ENHANCE_RESPONSE,
            }:
                return result
        if messages_to_inject:
            combined_message = "\n\n".join(messages_to_inject)
            return MiddlewareResult(
                action=MiddlewareAction.INJECT_MESSAGE, message=combined_message
            )

        return MiddlewareResult()


class ContextInjectionMiddleware:
    """Middleware that injects relevant codebase context from VIBE-ANALYSIS.

    Uses a two-pass LLM approach:
    1. Scan JSON index chunks to find relevant content
    2. Extract markdown and synthesize focused context

    This middleware only activates when VIBE-ANALYSIS.md and .json exist.
    """

    # Tag used to identify enhancement messages (to prevent re-enhancement loops)
    ENHANCEMENT_TAG = "<codebase-analysis-context>"

    def __init__(
        self,
        workspace: Path,
        llm_complete: Callable[[str], AsyncGenerator[str, None]],
        enabled: bool = True,
        max_context_tokens: int = 4000,
    ) -> None:
        """Initialize the context injection middleware.

        Args:
            workspace: Root directory of the project
            llm_complete: Async function to call LLM for context analysis
            enabled: Whether context injection is enabled
            max_context_tokens: Maximum tokens for injected context
        """
        self.workspace = workspace
        self.llm_complete = llm_complete
        self.enabled = enabled
        self.max_context_tokens = max_context_tokens

        # Lazy-load the injector
        self._injector: Any | None = None
        self._initialized = False
        self._pending_user_input: str | None = None
        self._already_enhanced: bool = False  # Prevent re-enhancement loops

    def _get_injector(self) -> Any | None:
        """Get or create the context injector."""
        if self._initialized:
            return self._injector

        self._initialized = True

        # Only import when needed to avoid circular imports
        from vibe.core.context_injector import ContextInjector

        injector = ContextInjector(
            workspace=self.workspace,
            llm_complete=self.llm_complete,
            max_context_tokens=self.max_context_tokens,
        )

        if injector.is_available():
            self._injector = injector
            logger.info("Context injection enabled (VIBE-ANALYSIS files found)")
        else:
            logger.debug("Context injection unavailable (no VIBE-ANALYSIS files)")

        return self._injector

    def _get_latest_user_input(self, messages: list[LLMMessage]) -> str | None:
        """Extract the latest user message content.

        Args:
            messages: List of conversation messages

        Returns:
            Latest user message content, or None
        """
        from vibe.core.types import Role

        for msg in reversed(messages):
            if msg.role == Role.user:
                content = msg.content
                if content:
                    return content
        return None

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        """No action before turn - let LLM do its normal work first."""
        if not self.enabled:
            return MiddlewareResult()

        # Capture user input for later use in after_turn
        user_input = self._get_latest_user_input(context.messages)

        # Skip if the "user input" is actually our enhancement context (prevents infinite loop)
        if user_input and self.ENHANCEMENT_TAG in user_input:
            self._pending_user_input = None
            return MiddlewareResult()

        if user_input and len(user_input.strip()) >= 20:
            self._pending_user_input = user_input
            self._already_enhanced = False  # Reset for new genuine user input
        else:
            self._pending_user_input = None

        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        """Inject context AFTER the LLM has done its work, to enhance the response."""
        if not self.enabled:
            return MiddlewareResult()

        # Prevent re-enhancement loops - only enhance once per user turn
        if self._already_enhanced:
            return MiddlewareResult()

        # Only inject if we captured a user input worth enhancing
        if not self._pending_user_input:
            return MiddlewareResult()

        # Check if this is a final response (not in the middle of tool execution)
        # Only inject context when the conversation has settled
        if not self._is_final_response(context.messages):
            return MiddlewareResult()

        user_input = self._pending_user_input
        self._pending_user_input = None  # Clear for next turn

        injector = self._get_injector()
        if not injector:
            return MiddlewareResult()

        try:
            from vibe.core.context_injector import format_context_for_enhancement

            logger.info(f"Context injection: analyzing user input ({len(user_input)} chars)")
            result = await injector.get_context(user_input)

            if result.has_context and result.synthesized_context:
                formatted = format_context_for_enhancement(result)
                if formatted:
                    logger.info(
                        f"Context injection: ENHANCING response with {result.token_estimate} tokens, "
                        f"{len(result.relevant_items)} relevant items"
                    )
                    # Mark as enhanced to prevent infinite loop
                    self._already_enhanced = True
                    return MiddlewareResult(
                        action=MiddlewareAction.ENHANCE_RESPONSE,
                        message=formatted,
                        metadata={
                            "context_tokens": result.token_estimate,
                            "relevant_items": len(result.relevant_items),
                        },
                    )
            else:
                logger.info(
                    f"Context injection: no relevant context found "
                    f"(has_context={result.has_context}, items={len(result.relevant_items)})"
                )

        except Exception as e:
            logger.warning(f"Context enhancement failed: {e}")

        return MiddlewareResult()

    def _is_final_response(self, messages: list[LLMMessage]) -> bool:
        """Check if the last message is a final assistant response ready for enhancement.

        We only want to inject enhancement context when:
        1. The assistant has completed its response (no pending tool calls)
        2. The assistant has actually USED tools in this turn (read files, searched, etc.)

        This prevents enhancement from triggering too early, before the LLM
        has done its actual work.

        Args:
            messages: List of conversation messages

        Returns:
            True if this appears to be a final response ready for enhancement
        """
        from vibe.core.types import Role

        if not messages:
            return False

        last_msg = messages[-1]

        # Must be an assistant message with no pending tool calls
        if last_msg.role != Role.assistant:
            return False
        if last_msg.tool_calls:
            return False  # Still in tool execution loop

        # Check if tools were actually used in this turn
        # Enhancement should only happen AFTER the LLM has done its work
        if not self._has_used_tools_this_turn(messages):
            return False

        return True

    def _has_used_tools_this_turn(self, messages: list[LLMMessage]) -> bool:
        """Check if the LLM has used any tools since the last genuine user message.

        This ensures we don't enhance too early (before the LLM has read files,
        searched code, etc.).

        Args:
            messages: List of conversation messages

        Returns:
            True if tool messages exist between last user message and now
        """
        from vibe.core.types import Role

        # Walk backwards from the end, looking for tool messages
        # Stop when we hit the genuine user message (not our enhancement context)
        found_tool_message = False

        for msg in reversed(messages):
            if msg.role == Role.tool:
                found_tool_message = True
            elif msg.role == Role.user:
                # Check if this is the genuine user message or our enhancement context
                content = msg.content or ""
                if self.ENHANCEMENT_TAG in content:
                    continue  # Skip enhancement context, keep looking
                # Found the genuine user message - stop here
                break

        return found_tool_message

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        """Reset the middleware state."""
        self._pending_user_input = None
        self._already_enhanced = False
        # Reload analysis files on reset
        if self._injector:
            self._injector.reload()
