import base64
import json
import logging
from pathlib import Path
from typing import Any, Callable, Optional

from playwright.async_api import Page, Browser

from .baml_client.types import Step
from .config import Config
from .executor import BugReport
from .main import WebTestPilot
from .utils.video import webm_to_mp4_moviepy, create_evidence_clip

logger = logging.getLogger(__name__)
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


def parse_test_action_to_step(action: dict[str, Any]) -> Step:
    """
    Convert a test action from VS Code format to WebTestPilot Step format

    VS Code format:
    {
        "action": "Click the login button",
        "expectedResult": "Login form appears"
    }

    WebTestPilot Step format:
    Step(condition="", action="...", expectation="...")
    """
    return Step(
        condition="",
        action=action.get("action", ""),
        expectation=action.get("expectedResult", ""),
    )


def inject_environment_values(
    environment_data: dict[str, str], test_steps: list[Step]
) -> list[Step]:
    """i.e. ${{username}} -> actual value from environment file"""
    injected_steps = []
    for step in test_steps:
        injected_action = step.action
        injected_expectation = step.expectation

        for var_name, var_value in environment_data.items():
            placeholder = f"${{{var_name}}}"
            injected_action = injected_action.replace(placeholder, var_value)
            injected_expectation = injected_expectation.replace(placeholder, var_value)

        injected_steps.append(
            Step(
                condition=step.condition,
                action=injected_action,
                expectation=injected_expectation,
            )
        )

    return injected_steps


def load_and_parse_test_file(
    test_file_path: str,
    fixture_file_path: str | None,
    environment_file_path: str | None,
) -> tuple[dict[str, Any], list[Step]]:
    # Order: Load test -> Fixtures -> Parse Test + Fixture -> Merge -> Inject Environment values
    with open(test_file_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    logger.debug(f"Loaded test: {test_data.get('name', 'Unnamed Test')}")
    logger.debug(f"Test URL: {test_data.get('url', 'No URL specified')}")

    # Fixtures will be pre-pended to test steps.
    fixture_actions = []
    if fixture_file_path:
        logger.debug(f"Using fixture file: {fixture_file_path}")
        with open(fixture_file_path, "r", encoding="utf-8") as fixture_file:
            fixture_data: dict = json.load(fixture_file)
            fixture_actions = fixture_data.get("actions", [])

    actions = test_data.get("actions", [])
    if not actions:
        raise ValueError("No actions defined in test")

    fixture_steps = [parse_test_action_to_step(action) for action in fixture_actions]
    test_steps = [parse_test_action_to_step(action) for action in actions]

    logger.debug(f"Converted {len(test_steps)} actions to test steps")
    merged_steps = fixture_steps + test_steps
    logger.debug(f"Total steps after merging fixture: {len(merged_steps)}")

    # Inject last to ensure all placeholders are replaced.
    logger.debug(environment_file_path)
    if environment_file_path:
        logger.debug(f"Using environment file: {environment_file_path}")
        with open(environment_file_path, "r", encoding="utf-8") as env_file:
            environment_data: dict = json.load(env_file)
            merged_steps = inject_environment_values(
                environment_data=environment_data.get("environmentVariables", {}),
                test_steps=merged_steps,
            )
            # Variable templates in the url
            if test_data["url"]:
                for var_name, var_value in environment_data.get(
                    "environmentVariables", {}
                ).items():
                    placeholder = f"${{{var_name}}}"
                    test_data["url"] = test_data["url"].replace(placeholder, var_value)

    return test_data, merged_steps


async def run_test_from_file(
    browser: Browser,
    test_file_path: str,
    config_path: str,
    target_id: str | None,
    fixture_file_path: Optional[str],
    environment_file_path: Optional[str],
    enable_assertions: bool,
    cache_path: Optional[Path] = None,
    # Have to use here instead of fastmcp.Context due to circular import when used in extension
    mcp_report_progress: Callable | None = None,
) -> dict[str, Any]:
    try:
        # Load and parse test data
        test_data, test_steps = load_and_parse_test_file(
            test_file_path, fixture_file_path, environment_file_path
        )
        test_name = test_data.get("name", "Unnamed Test")

        # Configs
        config = Config.load(config_path)
        video_directory = cache_path.parent / "video" if cache_path else None
        if video_directory:
            video_directory.mkdir(parents=True, exist_ok=True)

        result: dict[str, Any] = {
            "success": True,
            "test_name": test_name,
            "url": test_data.get("url"),
            "steps_executed": 0,
            "errors": [],
        }

        if mcp_report_progress:
            await mcp_report_progress(0, len(test_steps), "Setting up test context...")

        # Get or create context

        # NOTE: having target_id means it comes from VSCode. VSCode needs to
        # share the same context to stream the right tab ID.
        if target_id:
            context = (
                browser.contexts[0]
                if browser.contexts
                else await browser.new_context(
                    viewport={
                        "width": VIEWPORT_WIDTH,
                        "height": VIEWPORT_HEIGHT,
                    },
                    record_video_dir=video_directory,
                    record_video_size={
                        "width": VIEWPORT_WIDTH,
                        "height": VIEWPORT_HEIGHT,
                    },
                )
            )
        else:
            # Coming from MCP, needs to have the right video directory.
            context = (
                browser.contexts[0]
                if browser.contexts
                else await browser.new_context(
                    viewport={
                        "width": VIEWPORT_WIDTH,
                        "height": VIEWPORT_HEIGHT,
                    },
                    record_video_dir=video_directory,
                    record_video_size={
                        "width": VIEWPORT_WIDTH,
                        "height": VIEWPORT_HEIGHT,
                    },
                )
            )

        # Get the correct page based on target_id
        page: Page | None = None
        for tab in context.pages:
            cdp = await context.new_cdp_session(tab)
            info = await cdp.send("Target.getTargetInfo")

            if info["targetInfo"]["targetId"] == target_id:
                page = tab
                break

        # MCP does can't access target_id.
        if not page and not target_id:
            page = await context.new_page()

        if not page:
            raise ValueError(
                f"Tab with target id {target_id} not found in browser context."
            )

        assert page

        # This is important for consistent grounding results.
        await page.set_viewport_size(
            {
                "width": VIEWPORT_WIDTH,
                "height": VIEWPORT_HEIGHT,
            }
        )

        # Navigate to test URL if specified
        test_url = test_data.get("url")
        assert test_url, "Test URL must be specified in the test data"

        logger.info(f"Navigating to {test_url}")
        if mcp_report_progress:
            await mcp_report_progress(
                0, len(test_steps), f"Navigating to {test_url}..."
            )
        await page.goto(test_url, timeout=15000, wait_until="domcontentloaded")

        session = None
        try:
            # Run the test
            logger.info(f"Starting test execution with {len(test_steps)} steps")
            session = await WebTestPilot.run_parallel(
                page,
                config,
                test_steps,
                assertion=enable_assertions,
                cache_path=cache_path,
                mcp_report_progress=mcp_report_progress,
            )

            # Passed
            if session.success:
                result["steps_executed"] = len(test_steps)
                if mcp_report_progress:
                    await mcp_report_progress(
                        len(test_steps),
                        len(test_steps),
                        f"TEST {test_name} PASSED!",
                    )
            else:
                # Bug raised
                if mcp_report_progress:
                    await mcp_report_progress(
                        len(test_steps),
                        len(test_steps),
                        f"TEST {test_name} FAILED!",
                    )
                result["success"] = False
                bug_report_str = (
                    str(session.bug_report) if session.bug_report else "Unknown error"
                )
                result[
                    "detailed_error"
                ] = f"""Leading up steps: {"\n - ".join([step.action for step in test_steps[: session.failed_step]])}
Failed step: {session.failed_step} when executing action: "{test_steps[min(session.failed_step, len(test_steps) - 1)].action if session.failed_step is not None else "N/A"}"
Bug detected: {bug_report_str}"""
                result["errors"].append(bug_report_str)

        except Exception as e:
            if mcp_report_progress:
                await mcp_report_progress(
                    len(test_steps), len(test_steps), f"TEST {test_name} FAILED!"
                )
            logger.error(f"Test execution failed: {str(e)}", exc_info=True)
            result["success"] = False
            result["errors"].append(str(e))

        # It'll close the tab and browser.
        await context.close()
        # await browser.close()

        # Post-processing artifacts: screenshots, video.
        if cache_path:
            if mcp_report_progress:
                await mcp_report_progress(
                    len(test_steps), len(test_steps), "Preparing test artifacts..."
                )

            # Screenshots
            if session:
                screenshots_directory = cache_path.parent / "screenshots"
                screenshots_directory.mkdir(parents=True, exist_ok=True)

                for step_number, state in enumerate(session.history):
                    screenshot_path = (
                        screenshots_directory / f"step_{step_number}_screenshot.png"
                    )
                    with open(screenshot_path, "wb") as img_file:
                        img_file.write(base64.b64decode(state.screenshot))

                logger.info(f"Screenshots saved to {screenshots_directory}")
                result["screenshot_directory"] = str(screenshots_directory)
                result["screenshot_files"] = [
                    str(p) for p in screenshots_directory.glob("*.png")
                ]

                if session.bug_report and session.failed_step:
                    bug_evidence_path = screenshots_directory / "bug_evidence_image.png"
                    with open(bug_evidence_path, "wb") as img_file:
                        failed_step = session.failed_step
                        img_file.write(
                            base64.b64decode(session.history[failed_step].screenshot)
                        )

            assert video_directory

            # Video, there should only be 1 video file.
            playback_path = video_directory / "playback.webm"
            # for webm_file in video_directory.glob("*.webm"):
            # webm_to_mp4_moviepy(webm_file, mp4_playback_path)
            # webm_file.unlink()
            # webm_file.rename(video_directory / "playback.webm")
            # break

            logger.info(f"Video playback saved to {playback_path}")
            result["playback_video_path"] = str(playback_path)

            # Create pass/fail evidence clip
            # if session and session.action_timestamps and mp4_playback_path.exists():
            #     # TODO: consider refactor to "outcome": "passed/failed" instead.
            #     result_string = "pass" if result["success"] else "fail"
            #     evidence_path = video_directory / f"{result_string}_evidence_video.mp4"
            #     _ = create_evidence_clip(
            #         mp4_playback_path,
            #         session.action_timestamps,
            #         evidence_path,
            #     )
            #     result[f"{result_string}_evidence_video_path"] = str(evidence_path)
            #     logger.info(f"Evidence clip created: {evidence_path}")

            # Sometimes model try to verify if file paths exist, slow & annoying.
            # result["note"] = "All file paths exists."

        if mcp_report_progress:
            await mcp_report_progress(
                len(test_steps),
                len(test_steps),
                f"TEST {test_name} {'PASSED' if result['success'] else 'FAILED'}!",
            )

        return result
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
