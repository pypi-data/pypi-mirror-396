import ast
import asyncio
import base64
from io import BytesIO
import logging
import re
from copy import deepcopy
from typing import Any

from src.baml_client.async_client import b
from baml_py import ClientRegistry, Collector, Image
from PIL import ImageDraw
from PIL import Image as PILImage
from ..assertion_api.session import Session
from playwright.async_api import ElementHandle, Page

# -------------------------
# Globals
# -------------------------
logger = logging.getLogger(__name__)
_current_session: Session | None = None
_trace: list[dict] = []


def _get_current_page() -> Page:
    """Get the current page from session, allowing dynamic updates (e.g., popups)."""
    if _current_session is None:
        raise RuntimeError("No active session. Call _set_session() first.")
    return _current_session.page


# -------------------------
# Helpers
# -------------------------
async def write_image_for_debug(path: str, x: int, y: int):
    # Annotate the screenshot and write to file for debugging
    page = _get_current_page()
    with open(
        path,
        "wb",
    ) as f:
        image_b64 = base64.b64encode(await page.screenshot(type="png")).decode("utf-8")
        # draw circle at (x,y)
        image = PILImage.open(BytesIO(base64.b64decode(image_b64)))
        ImageDraw.Draw(image).ellipse(
            (x - 5, y - 5, x + 5, y + 5),
            # outline="red",
            fill="red",
            width=4,
        )
        image.save(f, format="PNG")


def _parse_coordinates(output_text: str) -> tuple[float, float]:
    # Note: this assumes screenshot is 1920 * 1080px
    # Example: output_text = "[1130,534,1553,560]"
    box = eval(output_text)

    # NOTE: This is different because model's patch is 14x14
    input_height = 1092
    input_width = 1932
    abs_x1 = float(box[0]) / input_width
    abs_y1 = float(box[1]) / input_height
    abs_x2 = float(box[2]) / input_width
    abs_y2 = float(box[3]) / input_height
    bbox = [abs_x1, abs_y1, abs_x2, abs_y2]
    point = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
    return point[0] * 1920, point[1] * 1080


async def _get_element(
    page: Page, x: int, y: int, target_description: str
) -> ElementHandle | None:
    """Get element at coordinates, with special handling for ul/ol to find best matching li."""
    handle = await page.evaluate_handle(f"""
    () => {{
      const clickableTags = ['BUTTON','A','INPUT','TEXTAREA','SELECT'];
      const clickableRoles = ['button','link','menuitem'];

      // create a temporary highlight circle at (x,y)
      try {{
        const highlightId = '__wpt_highlight_circle';
        const existing = document.getElementById(highlightId);
        if (existing) existing.remove();

        const r = 35; // radius in px
        const div = document.createElement('div');
        div.id = highlightId;
        Object.assign(div.style, {{
          position: 'fixed',
          left: ({x} - r) + 'px',
          top: ({y} - r) + 'px',
          width: (r * 2) + 'px',
          height: (r * 2) + 'px',
          borderRadius: '50%',
          background: 'rgba(255,200,0,0.20)',
          boxShadow: '0 0 12px 4px rgba(255,200,0,0.6)',
          border: '2px solid rgba(255,165,0,0.95)',
          pointerEvents: 'none',
          zIndex: '2147483647',
          transition: 'opacity 0.45s ease-out, transform 0.45s ease-out',
          transform: 'scale(1)'
        }});
        document.body.appendChild(div);
        // fade and remove after a short delay
        setTimeout(() => {{
          div.style.opacity = '0';
          div.style.transform = 'scale(1.4)';
          setTimeout(() => div.remove(), 450);
        }}, 600);
      }} catch (e) {{
        // ignore highlight errors
      }}

      const els = document.elementsFromPoint({x}, {y});
      for (const el of els) {{
        const style = window.getComputedStyle(el);
        if (
          style.pointerEvents !== 'none' &&
          style.visibility !== 'hidden' &&
          el.offsetWidth > 0 &&
          el.offsetHeight > 0 &&
          (clickableTags.includes(el.tagName) ||
           clickableRoles.includes(el.getAttribute('role')) ||
           el.getAttribute('onclick'))
        ) {{
          return el;
        }}
      }}
      return els[0] || null; // fallback
    }}
    """)

    if not handle:
        logger.debug(f"No element handle found at ({x}, {y})")
        return None

    logger.debug(
        f"Element handle at ({x}, {y}): {handle} {handle.as_element()} {await handle.get_properties()}"
    )
    element = handle.as_element()

    if element:
        logger.debug(
            f"Element inner html {await element.inner_html()} {await element.get_properties()}"
        )

        # Handle ul/ol by finding best matching li if target_description is provided
        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
        if tag_name in ["ul", "ol"]:
            logger.debug(
                f"Detected {tag_name} element, searching for best matching <li>"
            )
            best_li = await _find_best_matching_li(element, target_description)
            if best_li:
                element = best_li
                logger.debug("Switched to best matching <li> element")

        logger.debug(f"Element tag name: {tag_name}")
        if tag_name in ["td"]:
            logger.debug(
                f"Detected {tag_name} element, searching for best matching <a>"
            )
            best_a = await _find_best_matching_a(element, target_description)
            if best_a:
                element = best_a
                logger.debug("Switched to best matching <a> element")

        return element

    return None


async def playwright_click(get_by: str, **kwargs):
    page = _get_current_page()
    await page.wait_for_timeout(3000)
    
    # Get the element to highlight it before clicking
    element = None
    if get_by == "selector":
        element = await page.query_selector(kwargs.get("selector"))
    elif get_by == "locator":
        element = await page.locator(**kwargs).element_handle()
    elif get_by == "text":
        element = await page.get_by_text(**kwargs).element_handle()
    elif get_by == "role":
        element = await page.get_by_role(**kwargs).element_handle()
    elif get_by == "label":
        element = await page.get_by_label(**kwargs).element_handle()
    elif get_by == "placeholder":
        element = await page.get_by_placeholder(**kwargs).element_handle()
    elif get_by == "alt_text":
        element = await page.get_by_alt_text(**kwargs).element_handle()
    elif get_by == "title":
        element = await page.get_by_title(**kwargs).element_handle()
    
    # Add highlight animation if element was found
    if element:
        try:
            box = await element.bounding_box()
            if box:
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                await page.evaluate(f"""
                () => {{
                  const highlightId = '__wpt_highlight_circle';
                  const existing = document.getElementById(highlightId);
                  if (existing) existing.remove();

                  const r = 35; // radius in px
                  const div = document.createElement('div');
                  div.id = highlightId;
                  Object.assign(div.style, {{
                    position: 'fixed',
                    left: ({x} - r) + 'px',
                    top: ({y} - r) + 'px',
                    width: (r * 2) + 'px',
                    height: (r * 2) + 'px',
                    borderRadius: '50%',
                    background: 'rgba(255,200,0,0.20)',
                    boxShadow: '0 0 12px 4px rgba(255,200,0,0.6)',
                    border: '2px solid rgba(255,165,0,0.95)',
                    pointerEvents: 'none',
                    zIndex: '2147483647',
                    transition: 'opacity 0.45s ease-out, transform 0.45s ease-out',
                    transform: 'scale(1)'
                  }});
                  document.body.appendChild(div);
                  // fade and remove after a short delay
                  setTimeout(() => {{
                    div.style.opacity = '0';
                    div.style.transform = 'scale(1.4)';
                    setTimeout(() => div.remove(), 450);
                  }}, 600);
                }}
                """)
        except Exception as e:
            logger.debug(f"Could not highlight element: {e}")
    
    # Perform the actual click
    if get_by == "selector":
        await page.click(**kwargs)
    elif get_by == "locator":
        await page.locator(**kwargs).click()
    elif get_by == "text":
        await page.get_by_text(**kwargs).click()
    elif get_by == "role":
        await page.get_by_role(**kwargs).click()
    elif get_by == "label":
        await page.get_by_label(**kwargs).click()
    elif get_by == "placeholder":
        await page.get_by_placeholder(**kwargs).click()
    elif get_by == "alt_text":
        await page.get_by_alt_text(**kwargs).click()
    elif get_by == "title":
        await page.get_by_title(**kwargs).click()

    # playwright_click("selector", selector="#base_bd > div.main.layoutfix > div.mb10.bs06.nobs1.tb_cner > table > tbody > tr > td:nth-child(7) > a.act_del_s")
    # playwright_click("table").get_by_role("link", name="删除").click()
    # playwright_click("button", name="确认").click()


def _simple_text_similarity(text1: str, text2: str) -> float:
    """Simple text similarity based on common word overlap."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    return len(intersection) / max(len(words1), len(words2))


async def _find_best_matching_li(
    element: ElementHandle, target_description: str
) -> ElementHandle | None:
    """Find the <li> child with the most matching text when parent is <ul> or <ol>."""
    try:
        li_elements = await element.query_selector_all("li")
        if not li_elements:
            return None

        best_match, best_score = None, -1.0
        for li in li_elements:
            score = _simple_text_similarity(await li.inner_text(), target_description)
            if score > best_score:
                best_match, best_score = li, score

        return best_match
    except Exception as e:
        logger.warning(f"Error finding best matching li: {e}")
        return None


async def _find_best_matching_a(
    element: ElementHandle, target_description: str
) -> ElementHandle | None:
    """Find the <li> child with the most matching text when parent is <ul> or <ol>."""
    try:
        li_elements = await element.query_selector_all("a")
        if not li_elements:
            return None

        best_match, best_score = None, -1.0
        for li in li_elements:
            score = _simple_text_similarity(await li.inner_text(), target_description)
            if score > best_score:
                best_match, best_score = li, score

        return best_match
    except Exception as e:
        logger.warning(f"Error finding best matching li: {e}")
        return None


async def _get_xpath(element: ElementHandle) -> str:
    return await element.evaluate("""
    (el) => {
        if (!el) return '';
        const parts = [];
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            let idx = 1;
            let sibling = el.previousElementSibling;
            while (sibling) {
                if (sibling.tagName === el.tagName) idx++;
                sibling = sibling.previousElementSibling;
            }
            parts.unshift(el.tagName.toLowerCase() + '[' + idx + ']');
            el = el.parentElement;
        }
        return '/' + parts.join('/');
    }
    """)


async def _get_screenshot() -> Image:
    page = _get_current_page()
    screenshot = base64.b64encode(await page.screenshot(type="png")).decode("utf-8")
    return Image.from_base64("image/png", screenshot)


def _set_session(session: Session):
    global _current_session
    _current_session = session


def _require_page():
    if _current_session is None:
        raise RuntimeError("No active session. Call _set_session() first.")

    page = _get_current_page()
    assert page is not None and not page.is_closed(), (
        "Current page is not set or closed"
    )


async def _focus(x: int, y: int) -> tuple[int, int]:
    """Make (x, y) center of viewport as much as possible.

    Returns:
        tuple[int, int]: (deltaX, deltaY) - the amount by which the coordinates shifted after scrolling
    """
    page = _get_current_page()
    result = await page.evaluate(
        """({ x, y }) => {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const docWidth = document.documentElement.scrollWidth;
            const docHeight = document.documentElement.scrollHeight;

            const initialScrollX = window.scrollX;
            const initialScrollY = window.scrollY;

            if (docWidth <= viewportWidth && docHeight <= viewportHeight) {
                // No scrolling possible
                return { deltaX: 0, deltaY: 0 };
            }

            let scrollX = x - viewportWidth / 2;
            let scrollY = y - viewportHeight / 2;

            const maxScrollX = docWidth - viewportWidth;
            const maxScrollY = docHeight - viewportHeight;
            scrollX = Math.max(0, Math.min(scrollX, maxScrollX));
            scrollY = Math.max(0, Math.min(scrollY, maxScrollY));

            window.scrollTo(scrollX, scrollY);
            
            const deltaX = window.scrollX - initialScrollX;
            const deltaY = window.scrollY - initialScrollY;
            
            return { deltaX, deltaY };
        }""",
        {"x": x, "y": y},
    )

    logger.debug(
        f"Scrolled to focus on ({x}, {y}), delta: ({result['deltaX']}, {result['deltaY']})"
    )
    return result["deltaX"], result["deltaY"]


async def click(cr: ClientRegistry, collector: Collector, target_description: str):
    _require_page()

    screenshot = await _get_screenshot()
    logger.debug(f"Locating element to click: {target_description}")
    coordinates = await b.LocateUIElement(
        screenshot,
        target_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    x, y = _parse_coordinates(coordinates)

    # Leads to scroll -> needs to update new coordinates
    delta_x, delta_y = await _focus(x, y)
    x -= delta_x
    y -= delta_y

    page = _get_current_page()
    element: ElementHandle = await _get_element(page, x, y, target_description)
    xpath = await _get_xpath(element)
    logger.debug(
        f"Clicking element at ({x}, {y}) with element: {element} and xpath: {xpath}"
    )
    await element.click(force=True)

    _trace.append({"action": {"name": "click", "args": {"xpath": xpath}}})


async def type(
    cr: ClientRegistry, collector: Collector, target_description: str, content: str
):
    _require_page()

    screenshot = await _get_screenshot()
    coordinates = await b.LocateUIElement(
        screenshot,
        target_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    x, y = _parse_coordinates(coordinates)

    delta_x, delta_y = await _focus(x, y)
    x -= delta_x
    y -= delta_y

    page = _get_current_page()
    element: ElementHandle = await _get_element(page, x, y, target_description)

    try:
        await element.fill(content)
    except Exception as e:
        logger.warning(f"Exception during fill: {str(e)}")
        if len(content) < 25:
            await element.type(content, delay=150)
        else:
            await element.type(content)

    _trace.append(
        {"action": {"name": "fill", "args": {"xpath": await _get_xpath(element)}}}
    )


async def drag(
    cr: ClientRegistry,
    collector: Collector,
    source_description: str,
    target_description: str,
):
    _require_page()
    page = _get_current_page()

    screenshot = await _get_screenshot()
    source_coordinates = await b.LocateUIElement(
        screenshot,
        source_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    source_x, source_y = _parse_coordinates(source_coordinates)
    target_coordinates = await b.LocateUIElement(
        screenshot,
        target_description,
        baml_options={"client_registry": cr, "collector": collector},
    )
    target_x, target_y = _parse_coordinates(target_coordinates)

    # Move to source position
    await page.mouse.move(source_x, source_y)

    # Press mouse button down
    await page.mouse.down()

    # Move to target position with intermediate steps
    steps = 10
    delay_ms = 200
    for i in range(1, steps + 1):
        ratio = i / steps
        intermediate_x = int(source_x + (target_x - source_x) * ratio)
        intermediate_y = int(source_y + (target_y - source_y) * ratio)
        await page.mouse.move(intermediate_x, intermediate_y)
        await asyncio.sleep(delay_ms / 1000)

    # Move to final target position
    await page.mouse.move(target_x, target_y)

    # Move again to ensure dragover events are properly triggered
    await page.mouse.move(target_x, target_y)

    # Release mouse button
    await page.mouse.up()

    _trace.append(
        {
            "action": {
                "name": "drag",
                "args": {
                    "source_xpath": await _get_xpath(
                        await _get_element(page, source_x, source_y, source_description)
                    ),
                    "target_xpath": await _get_xpath(
                        await _get_element(page, target_x, target_y, target_description)
                    ),
                },
            }
        }
    )


async def scroll(
    cr: ClientRegistry,
    collector: Collector,
    target_description: str | None,
    direction: str,
):
    _require_page()

    direction = direction.lower()
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError("direction must be one of 'up', 'down', 'left', or 'right'")

    # Default values: scroll window
    coords = None
    screenshot = await _get_screenshot()
    if target_description is not None:
        coordinates = await b.LocateUIElement(
            screenshot,
            target_description,
            baml_options={"client_registry": cr, "collector": collector},
        )
        x, y = _parse_coordinates(coordinates)
        coords = [x, y]

        page = _get_current_page()
        await page.evaluate(
            """
        ([coords, direction]) => {
        let el, scrollAmountVertical, scrollAmountHorizontal;

        if (coords) {
            const [x, y] = coords;
            el = document.elementFromPoint(x, y);
            if (!el) return;
            const rect = el.getBoundingClientRect();
            scrollAmountVertical = rect.height;
            scrollAmountHorizontal = rect.width;
        } else {
            el = window;
            scrollAmountVertical = window.innerHeight;
            scrollAmountHorizontal = window.innerWidth;
        }

        switch (direction) {
            case 'up':
            el.scrollBy(0, -scrollAmountVertical);
            break;
            case 'down':
            el.scrollBy(0, scrollAmountVertical);
            break;
            case 'left':
            el.scrollBy(-scrollAmountHorizontal, 0);
            break;
            case 'right':
            el.scrollBy(scrollAmountHorizontal, 0);
            break;
        }
        }
        """,
            [coords, direction],
        )


async def wait(duration: int):
    if duration <= 0:
        raise ValueError("Wait duration must be >0 miliseconds")

    await asyncio.sleep(duration / 1000)


async def finished():
    pass


async def execute(code: str, page: Page, session: Session) -> list[dict]:
    """
    Safely execute LLM-generated Python code blocks containing only automation actions.
    Automatically sets the current Playwright Page before execution.
    """
    cr: ClientRegistry = session.config.ui_locator
    collector: Collector = session.collector

    # Create async wrapper functions that will be awaited
    async def _click(target_description: str):
        await click(cr, collector, target_description)

    async def _type(target_description: str, content: str):
        await type(cr, collector, target_description, content)

    async def _drag(source_description: str, target_description: str):
        await drag(cr, collector, source_description, target_description)

    async def _scroll(target_description: str | None, direction: str):
        await scroll(cr, collector, target_description, direction)

    async def _wait(duration: int):
        await wait(duration)

    async def _finished():
        await finished()

    async def _playwright_click(get_by: str, **kwargs):
        await playwright_click(get_by, **kwargs)

    # Remove triple backticks and optional 'python' tag
    try:
        _set_session(
            session
        )  # Bind this run to the session (page accessed dynamically)

        cleaned_code = re.sub(
            r"^```(?:python)?|```$", "", code.strip(), flags=re.MULTILINE
        ).strip()

        # Execute the code in an async context
        # We need to wrap the exec in an async function and await the calls
        local_vars: dict[str, Any] = {
            "click": _click,
            "type": _type,
            "drag": _drag,
            "scroll": _scroll,
            "wait": _wait,
            "finished": _finished,
            "playwright_click": _playwright_click,
        }

        # Parse the code and wrap each call in await
        tree = ast.parse(cleaned_code)

        # Execute each statement
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                # Get function name
                func_name = (
                    node.value.func.id
                    if isinstance(node.value.func, ast.Name)
                    else None
                )
                if func_name and func_name in local_vars:
                    # Extract arguments
                    args = []
                    for arg in node.value.args:
                        if isinstance(arg, ast.Constant):
                            args.append(arg.value)
                        else:
                            # Evaluate the argument
                            args.append(
                                eval(compile(ast.Expression(arg), "<string>", "eval"))
                            )

                    kwargs = {}
                    for kw in node.value.keywords:
                        if isinstance(kw.value, ast.Constant):
                            kwargs[kw.arg] = kw.value.value
                        else:
                            kwargs[kw.arg] = eval(
                                compile(ast.Expression(kw.value), "<string>", "eval")
                            )

                    # Call the async function
                    await local_vars[func_name](*args, **kwargs)
    finally:
        trace = deepcopy(_trace)
        _trace.clear()

    return trace
