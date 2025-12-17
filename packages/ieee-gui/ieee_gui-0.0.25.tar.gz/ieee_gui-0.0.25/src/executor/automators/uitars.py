import ast
import re
import asyncio
from playwright.async_api import Page, ElementHandle

_current_page: Page | None = None


def _set_page(page: Page):
    global _current_page
    _current_page = page


def _require_page():
    if _current_page is None:
        raise RuntimeError("No active page. Call _set_page() first.")


def _parse_point(point_str: str) -> tuple[int, int]:
    """
    Parse string like '<point>x1 y1</point>' into (x1, y1).
    """
    match = re.match(r"<point>\s*(-?\d+)\s+(-?\d+)\s*</point>", point_str)
    if not match:
        raise ValueError(f"Invalid point format: {point_str}")
    x, y = map(int, match.groups())
    return x, y


async def _get_element(page: Page, x: int, y: int) -> ElementHandle | None:
    handle = await page.evaluate_handle(f"""
    () => {{
        const clickableTags = ['BUTTON', 'A', 'INPUT', 'TEXTAREA', 'SELECT'];
        const clickableRoles = ['button', 'link', 'menuitem'];

        const els = document.elementsFromPoint({x}, {y});
        for (const el of els) {{
            const style = window.getComputedStyle(el);
            if (
                style.pointerEvents !== 'none' &&
                style.visibility !== 'hidden' &&
                el.offsetWidth > 0 &&
                el.offsetHeight > 0 &&
                (
                    clickableTags.includes(el.tagName) ||
                    clickableRoles.includes(el.getAttribute('role')) ||
                    el.getAttribute('onclick')
                )
            ) {{
                return el;
            }}
        }}
        return els[0] || null;
    }}
    """)
    return handle.as_element() if handle else None


async def click(point: str):
    _require_page()
    x, y = _parse_point(point)
    el = await _get_element(_current_page, x, y)
    if el:
        await el.click()
    else:
        await _current_page.mouse.click(x, y)


async def left_double(point: str):
    _require_page()
    x, y = _parse_point(point)
    el = await _get_element(_current_page, x, y)
    if el:
        await el.dblclick()
    else:
        # Playwright mouse doesn't have dblclick with coordinates directly, do two clicks quickly
        await _current_page.mouse.click(x, y, click_count=2)


async def right_single(point: str):
    _require_page()
    x, y = _parse_point(point)
    el = await _get_element(_current_page, x, y)
    if el:
        await el.click(button="right")
    else:
        await _current_page.mouse.click(x, y, button="right")


async def drag(start_point: str, end_point: str):
    _require_page()
    sx, sy = _parse_point(start_point)
    ex, ey = _parse_point(end_point)

    await _current_page.mouse.move(sx, sy)
    await _current_page.mouse.down()
    # interpolate steps for smooth dragging
    steps = 10
    for i in range(1, steps + 1):
        nx = sx + (ex - sx) * i / steps
        ny = sy + (ey - sy) * i / steps
        await _current_page.mouse.move(nx, ny)
        await asyncio.sleep(0.02)
    await _current_page.mouse.up()


async def hotkey(key: str):
    _require_page()
    keys = key.lower().split()
    if not (1 <= len(keys) <= 3):
        raise ValueError("Hotkey supports 1 to 3 keys only")
    # Press keys sequentially with down and up events for modifiers
    for k in keys[:-1]:
        await _current_page.keyboard.down(k)
    await _current_page.keyboard.press(keys[-1])
    for k in reversed(keys[:-1]):
        await _current_page.keyboard.up(k)


async def type(content: str):
    _require_page()
    # The content may contain escape sequences, e.g., \n
    decoded_content = content.encode("utf-8").decode("unicode_escape")
    await _current_page.keyboard.type(decoded_content)


async def scroll(point: str | None, direction: str):
    _require_page()
    direction = direction.lower()
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError("Invalid scroll direction")

    coords = None
    if point is not None:
        coords = _parse_point(point)

    await _current_page.evaluate(
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


async def wait():
    _require_page()
    # Sleep 5 seconds
    await asyncio.sleep(5)
    # Optional: take screenshot for change detection
    # For example:
    # await _current_page.screenshot(path="wait_screenshot.png")


async def finished(content: str):
    _require_page()
    decoded_content = content.encode("utf-8").decode("unicode_escape")
    print(f"UITARS finished with content:\n{decoded_content}")


async def execute(code: str, page: Page) -> list[dict]:
    """
    Execute LLM-generated UITARS Python code blocks by exposing only the allowed functions.
    Returns an empty list for trace compatibility.
    """
    _set_page(page)

    # Create async wrapper functions
    async def _click(point: str):
        await click(point)
    
    async def _left_double(point: str):
        await left_double(point)
    
    async def _right_single(point: str):
        await right_single(point)
    
    async def _drag(start_point: str, end_point: str):
        await drag(start_point, end_point)
    
    async def _hotkey(key: str):
        await hotkey(key)
    
    async def _type(content: str):
        await type(content)
    
    async def _scroll(point: str | None, direction: str):
        await scroll(point, direction)
    
    async def _wait():
        await wait()
    
    async def _finished(content: str):
        await finished(content)

    local_vars = {
        "click": _click,
        "left_double": _left_double,
        "right_single": _right_single,
        "drag": _drag,
        "hotkey": _hotkey,
        "type": _type,
        "scroll": _scroll,
        "wait": _wait,
        "finished": _finished,
    }

    # Clean triple backticks if present
    cleaned_code = re.sub(
        r"^```(?:python)?|```$", "", code.strip(), flags=re.MULTILINE
    ).strip()
    
    # Parse the code and execute each call
    tree = ast.parse(cleaned_code)
    
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func_name = node.value.func.id if isinstance(node.value.func, ast.Name) else None
            if func_name and func_name in local_vars:
                args = []
                for arg in node.value.args:
                    if isinstance(arg, ast.Constant):
                        args.append(arg.value)
                    else:
                        args.append(eval(compile(ast.Expression(arg), '<string>', 'eval')))
                
                kwargs = {}
                for kw in node.value.keywords:
                    if isinstance(kw.value, ast.Constant):
                        kwargs[kw.arg] = kw.value.value
                    else:
                        kwargs[kw.arg] = eval(compile(ast.Expression(kw.value), '<string>', 'eval'))
                
                await local_vars[func_name](*args, **kwargs)
    
    return []
