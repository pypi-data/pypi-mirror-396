import base64
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional
from xml.etree.ElementTree import Element as XMLElement

from baml_py import Collector, Image
from playwright.async_api import Page

from src.baml_client.async_client import b
from src.baml_client.types import History, PageAbstract, Step
from src.cache import Cache, CaptureStateCache, PageContent
from src.config import Config

from ..page_reidentification.abstract import to_xml_tree
from ..page_reidentification.accessibility import AccessibilityTree
from ..page_reidentification.distance import tree_distance
from .element import Element, ElementFactory
from .state import State, StateFactory

logger = logging.getLogger(__name__)


@dataclass
class PageSnapshot:
    xml_tree: list[XMLElement]
    elements: dict[int, Element]
    title: str
    content: str
    screenshot: str


class Session:
    """
    Manages a browser test session with state tracking capabilities.

    Args:
        page (Page): A Playwright Page instance that accesses the application under test.
            It's assumed that the application is already loaded
            and any necessary prerequisites (e.g., fixtures, authentication) have been set up.
        config (Config): Runtime configurations for this test session.

    Raises:
        AssertionError: If the provided page is not a valid Page instance or is closed.
    """

    def __init__(
        self,
        page: Page,
        config: Config,
        steps: list[Step],
        cache_path: Optional[Path] = None,
        mcp_report_progress: Optional[Callable] = None,
    ):
        assert isinstance(page, Page) and not page.is_closed()

        self.trace: list[dict] = []
        self.page: Page = page
        self.config = config

        self.collector = Collector()
        self.state_factory = StateFactory(self)
        self.element_factory = ElementFactory(self)

        self.steps = steps  # Could be empty, only for mcp parallel flow now.
        self.step_counter = 0  # Track current step number for VSCode UI

        self._history: list[State] = []
        self.cache = Cache(cache_path)

        # For mcp progress update
        self.mcp_report_progress = mcp_report_progress

        self.start_time: float = time.time()
        self.action_timestamps: list[float] = []
        self.failed_step: Optional[int] = None
        self.bug_report: Optional[Any] = None  # Store BugReport if test fails
        self.success: bool = True  # Track overall test success

    @classmethod
    async def create(
        cls,
        page: Page,
        config: Config,
        steps: list[Step] = [],
        defer_capture_state: bool = False,
        cache_path: Optional[Path] = None,
        mcp_report_progress: Optional[Callable] = None,
    ) -> "Session":
        """
        Factory method to create and initialize a Session.

        Args:
            page (Page): A Playwright Page instance that accesses the application under test.
            config (Config): Runtime configurations for this test session.
            defer_capture (bool): If True, skip capturing the initial state.
            cache_path (Optional[Path]): Path to cache file for this test.

        Returns:
            Session: A fully initialized Session instance.
        """
        session = cls(page, config, steps, cache_path, mcp_report_progress)

        # --- Helper to keep following new tabs opened from the current page ---
        async def attach_popup_handler(current_page: Page):
            async def on_popup(popup: Page):
                try:
                    await popup.wait_for_load_state(timeout=30000)
                except Exception as e:
                    logger.warning(f"Timeout waiting for new tab to load: {e}")

                await popup.bring_to_front()
                session.page = popup  # now all further actions use the new tab

                # Get the new tab's target ID for screencast streaming
                try:
                    cdp = await popup.context.new_cdp_session(popup)
                    target_info = await cdp.send("Target.getTargetInfo")
                    new_target_id = target_info["targetInfo"]["targetId"]
                    # Log in a format the VS Code extension can parse
                    logger.info(f"NEW_TAB_OPENED: {new_target_id}")
                    # print(f"New tab opened: {popup.url} (targetId: {new_target_id})")
                except Exception as e:
                    logger.warning(f"Failed to get target ID for new tab: {e}")
                    # print(f"New tab opened: {popup.url}")

                # Also attach handler to this new page, in case it opens another tab.
                await attach_popup_handler(popup)

                # Close previous page after delay to avoid race conditions with screenshots
                await popup.wait_for_timeout(5000)
                await current_page.close()

            current_page.on("popup", on_popup)

        await attach_popup_handler(session.page)

        if not defer_capture_state:
            page_snapshot = await session.get_current_page_snapshot()
            await session.capture_state(prev_action=None, page_snapshot=page_snapshot)
        return session

    @property
    def history(self) -> list[State]:
        """
        Get the chronological history of captured states.

        Returns:
            list[State]: A read-only copy of all previously captured states in the test session,
                    ordered chronologically from oldest to newest.
        """
        return self._history.copy()

    async def update_mcp_progress(self, message: str) -> None:
        if not self.mcp_report_progress:
            return

        await self.mcp_report_progress(self.step_counter, len(self.steps), message)

    async def capture_state(
        self,
        prev_action: str | None,
        page_snapshot: PageSnapshot,
        step_number: Optional[int] = None,
    ) -> None:
        """
        Capture the current state of the browser page after an action.
        NOTE: Page snapshot is done outside and before calling this function.
        NOTE: to avoid race conditions due to page changes (in parallel action execution).
        NOTE: step_number: Optional explicit step number for cache access (for parallel execution).
        """
        step_num = step_number if step_number is not None else self.step_counter

        await self.update_mcp_progress(f"Capturing state step {step_number}...")

        cached = self.cache.get_capture_state(step_num, prev_action)
        if cached:
            page_id = cached.page_content.name
            description = cached.page_content.description
            layout = cached.page_content.layout
            logger.info(f"Cache hit for capture_state at step {step_num}")
        else:
            # Slow, blocking.
            page_id, description, layout = await self._page_reidentification(
                page_snapshot.xml_tree, page_snapshot.screenshot
            )

        # Save to cache
        self.cache.set_capture_state(
            step_num,
            CaptureStateCache(
                screenshot=page_snapshot.screenshot,
                page_content=PageContent(
                    name=page_id, description=description, layout=layout
                ),
                prev_action=prev_action,
            ),
        )

        # Update with new state
        state = self.state_factory.create(
            page_id=page_id,
            description=description,
            layout=layout,
            url=self.page.url,
            title=page_snapshot.title,
            content=page_snapshot.content,
            screenshot=page_snapshot.screenshot,
            elements=page_snapshot.elements,
            prev_action=prev_action,
            xml_tree=page_snapshot.xml_tree,
        )

        for e in page_snapshot.elements.values():
            e.state = state

        self._history.append(state)

    async def get_current_page_snapshot(self):
        tree = await AccessibilityTree.create(self.page)
        xml_tree = to_xml_tree(tree)
        elements = await self.capture_elements()
        page_title = await self.page.title()
        page_content = await self.page.content()
        screenshot = base64.b64encode(await self.page.screenshot(type="png")).decode(
            "utf-8"
        )
        return PageSnapshot(
            xml_tree=xml_tree,
            elements=elements,
            title=page_title,
            content=page_content,
            screenshot=screenshot,
        )

    async def capture_elements(self) -> dict[int, Element]:
        def _build_tree(
            elements_data: list[dict[str, Any]],
        ) -> tuple[dict[str, Element], Element]:
            elements: dict[str, Element] = {
                data["id"]: self.element_factory.create(data) for data in elements_data
            }
            root = None
            for el in elements.values():
                if el.parentId is not None:
                    parent = elements.get(el.parentId)
                    if parent:
                        parent.children.append(el)
                else:
                    root = el
            return elements, root  # type: ignore  # type: ignore

        elements_data = await self.page.evaluate("""
            (() => {
                let idCounter = 1;
                const nodes = [];

                function traverse(node, parentId = null) {
                    const id = idCounter++;
                    const rect = node.getBoundingClientRect();
                    const style = window.getComputedStyle(node);

                    const attributes = {};
                    for (const attr of node.attributes) {
                        attributes[attr.name] = attr.value;
                    }

                    nodes.push({
                        id,
                        parentId,
                        tagName: node.tagName,
                        outerHTML: node.outerHTML,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        zIndex: parseInt(style.zIndex) || 0,
                        visible: style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0',
                        attributes,
                        textContent: node.textContent.trim() || null
                    });

                    for (const child of node.children) {
                        traverse(child, id);
                    }
                }

                traverse(document.documentElement, null);
                return nodes;
            })()
        """)

        elements, _ = _build_tree(elements_data)
        return elements

    def get_history(
        self,
    ) -> list[History]:
        seen_pages = set()
        history = []
        for state in self.history:
            layout = state.layout if state.page_id not in seen_pages else None
            description = state.description if state.page_id not in seen_pages else None
            history.append(
                History(
                    page_id=state.page_id,
                    layout=layout,
                    description=description,
                    prev_action=state.prev_action,
                )
            )
            seen_pages.add(state.page_id)
        return history

    async def _page_reidentification(
        self, xml_tree: list[XMLElement], screenshot: str
    ) -> tuple[str, str, str]:
        """
        Determine if the current page matches any previously visited logical page.
        If matched, return the existing page ID and description.
        Otherwise, generate a new page ID and description.

        Returns:
            tuple[str, str]: A tuple containing:
                - page_id: A short identifier or name of the logical page.
                - description: A detailed textual description of the page.
        """
        current_img = Image.from_base64("image/png", screenshot)

        # Handle empty history — no page to compare
        if not self.history:
            logger.debug("Abstracting page...")
            page_abstract: PageAbstract = await b.AbstractPage(
                current_img,
                baml_options={
                    "client_registry": self.config.page_reidentification,
                    "collector": self.collector,
                },
            )
            return page_abstract.name, page_abstract.description, page_abstract.layout

        # Find the history state with the smallest tree distance to current page
        closest_state = min(
            self.history, key=lambda s: tree_distance(xml_tree, s.xml_tree)
        )
        closest_img = Image.from_base64("image/png", closest_state.screenshot)

        logger.info("Checking page re-identification...")
        if await b.IsSameLogicalPage(
            current_img,
            closest_img,
            baml_options={
                "client_registry": self.config.page_reidentification,
                "collector": self.collector,
            },
        ):
            return (
                closest_state.page_id,
                closest_state.description,
                closest_state.layout,
            )

        logger.debug("Abstracting page...")
        new_page_abstract: PageAbstract = await b.AbstractPage(
            current_img,
            baml_options={
                "client_registry": self.config.page_reidentification,
                "collector": self.collector,
            },
        )
        return (
            new_page_abstract.name,
            new_page_abstract.description,
            new_page_abstract.layout,
        )
