import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from src.baml_client.types import History

logger = logging.getLogger(__name__)


@dataclass
class PageContent:
    name: str
    description: str
    layout: str


@dataclass
class CaptureStateCache:
    screenshot: str
    page_content: PageContent
    prev_action: Optional[str] = None  # Track what action led to this state


@dataclass
class ActionCache:
    screenshot: str
    action: str
    proposed_code: str


@dataclass
class HistoryItem:
    page_id: str
    layout: Optional[str]
    description: Optional[str]
    prev_action: Optional[str]


@dataclass
class VerifyPostconditionCache:
    assertion: str
    action: str
    proposed_code: str
    history: list[HistoryItem]
    screenshot: str

    @classmethod
    def create(
        cls,
        assertion: str,
        action: str,
        proposed_code: str,
        history: list[History],
        screenshot: str,
    ) -> "VerifyPostconditionCache":
        history_items = [
            HistoryItem(
                page_id=h.page_id,
                layout=h.layout,
                description=h.description,
                prev_action=h.prev_action,
            )
            for h in history
        ]
        return cls(
            assertion=assertion,
            action=action,
            proposed_code=proposed_code,
            history=history_items,
            screenshot=screenshot,
        )


class Cache:
    """Simple cache class for storing and retrieving test execution results."""

    def __init__(self, cache_path: Optional[Path] = None):
        self.cache_path = cache_path
        self.data: dict[str, dict] = {}

        # Load existing cache if path provided
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                logger.info(f"Loaded cache from: {cache_path}")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.data = {}

    def get_capture_state(
        self, step_number: int, prev_action: Optional[str] = None
    ) -> Optional[CaptureStateCache]:
        """Get capture_state cache for a step, optionally validating prev_action matches.

        Args:
            step_number: The step number to get cache for.
            prev_action: The previous action to validate against cached prev_action.

        Returns:
            CaptureStateCache if cache exists and prev_action matches (if provided), None otherwise.
        """
        step_data = self.data.get(f"step_{step_number}", {})
        if "capture_state" not in step_data:
            return None

        cs = step_data["capture_state"]
        cached = CaptureStateCache(
            screenshot=cs["screenshot"],
            page_content=PageContent(**cs["page_content"]),
            prev_action=cs.get(
                "prev_action"
            ),  # Handle old cache format without prev_action
        )

        # Validate prev_action matches if provided
        if prev_action is not None and cached.prev_action != prev_action:
            logger.debug(
                f"prev_action mismatch at step {step_number}: cached='{cached.prev_action}' vs current='{prev_action}'"
            )
            return None

        return cached

    def set_capture_state(self, step_number: int, cache: CaptureStateCache) -> None:
        """Set capture_state cache for a step."""
        step_key = f"step_{step_number}"
        if step_key not in self.data:
            self.data[step_key] = {}
        self.data[step_key]["capture_state"] = asdict(cache)

    def get_action(self, step_number: int, action: str) -> Optional[ActionCache]:
        """Get action cache for a step, validating action matches.

        Args:
            step_number: The step number to get cache for.
            action: The action string to validate against cached action.

        Returns:
            ActionCache if cache exists and action matches, None otherwise.
        """
        step_data = self.data.get(f"step_{step_number}", {})
        if "action" not in step_data:
            return None

        cached = ActionCache(**step_data["action"])
        # Validate action matches
        if cached.action != action:
            logger.debug(
                f"Action mismatch at step {step_number}: cached='{cached.action}' vs current='{action}'"
            )
            return None

        return cached

    def set_action(self, step_number: int, cache: ActionCache) -> None:
        """Set action cache for a step."""
        step_key = f"step_{step_number}"
        if step_key not in self.data:
            self.data[step_key] = {}
        self.data[step_key]["action"] = asdict(cache)

    def get_verify_postcondition(
        self, step_number: int, assertion: str
    ) -> Optional[VerifyPostconditionCache]:
        """Get verify_postcondition cache for a step, validating assertion matches.

        Args:
            step_number: The step number to get cache for.
            assertion: The assertion/expectation string to validate against cached assertion.

        Returns:
            VerifyPostconditionCache if cache exists and assertion matches, None otherwise.
        """
        step_data = self.data.get(f"step_{step_number}", {})
        if "verify_postcondition" not in step_data:
            return None

        vpc = step_data["verify_postcondition"]
        cached = VerifyPostconditionCache(
            assertion=vpc["assertion"],
            action=vpc["action"],
            proposed_code=vpc["proposed_code"],
            history=[HistoryItem(**h) for h in vpc["history"]],
            screenshot=vpc["screenshot"],
        )
        # Validate assertion matches
        if cached.assertion != assertion:
            logger.debug(
                f"Assertion mismatch at step {step_number}: cached='{cached.assertion}' vs current='{assertion}'"
            )
            return None

        return cached

    def set_verify_postcondition(
        self, step_number: int, cache: VerifyPostconditionCache
    ) -> None:
        """Set verify_postcondition cache for a step."""
        step_key = f"step_{step_number}"
        if step_key not in self.data:
            self.data[step_key] = {}
        self.data[step_key]["verify_postcondition"] = asdict(cache)

    def save(self) -> None:
        """Save cache to file."""
        if not self.cache_path:
            logger.warning("No cache path specified, skipping save")
            return

        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved cache to: {self.cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def save_at_step(self, step_number: int) -> None:
        """Save cache to file."""
        if not self.cache_path:
            logger.warning("No cache path specified, skipping save")
            return

        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            # change name from cache.json to cache_step_{step_number}.json

            with open(
                self.cache_path.parent / f"cache_step_{step_number}.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved cache to: {self.cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
