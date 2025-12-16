import base64
import logging
import time
from typing import Optional

from baml_py import Image
from baml_py.baml_py import BamlImagePy

from src.baml_client.async_client import b
from src.baml_client.types import Feedback
from src.cache import ActionCache, VerifyPostconditionCache
from src.config import Config

from .assertion_api import execute_assertion
from .assertion_api.session import Session

logger = logging.getLogger(__name__)


class BugReport(Exception):
    def __init__(self, message, screenshots=None, steps=None):
        super().__init__(message)
        self.screenshots = screenshots or []
        self.steps = steps or []


async def verify_precondition(
    session: Session, condition: str, action: str, config: Config
) -> None:
    logger.info(f"Condition: {condition}")
    client_registry = config.assertion_generation
    collector = session.collector
    screenshot_b64 = base64.b64encode(await session.page.screenshot(type="png")).decode(
        "utf-8"
    )
    screenshot = Image.from_base64("image/png", screenshot_b64)
    history = session.get_history()

    response = await b.GeneratePrecondition(
        screenshot,
        history,
        action,
        condition,
        feedback=[],
        baml_options={"client_registry": client_registry, "collector": collector},
    )
    passed, message = execute_assertion(response, session)
    if passed:
        logger.info("Precondition passed.")
        return
    else:
        logger.info(f"Precondition failed: {message}")
        raise BugReport(message)


async def execute_action(
    session: Session, action: str, config: Config, step_number: Optional[int] = None
) -> None:
    # Increment step counter and output step info for VSCode parsing
    if step_number is None:
        session.step_counter += 1
        step_number = session.step_counter

    # Record timestamp before current action.
    session.action_timestamps.append(time.time() - session.start_time)

    await session.update_mcp_progress(f"Reasoning next action {step_number}...")

    logger.info(f"Action: {action}")
    # Also output in a format that's easy for VSCode to parse
    logger.info(f"STEP_{step_number}: {action}")

    client_registry = config.action_proposer
    client_name = config.action_proposer_name
    collector = session.collector
    screenshot_b64 = base64.b64encode(await session.page.screenshot(type="png")).decode(
        "utf-8"
    )
    screenshot: BamlImagePy = Image.from_base64("image/png", screenshot_b64)

    # Check cache for proposed code
    cached = session.cache.get_action(step_number, action)
    if cached:
        code = cached.proposed_code
        logger.info(f"Cache hit for action at step {step_number}/{len(session.steps)}")
        logger.info(f"Proposed code (cached):\n{code}")
    else:
        logger.debug("Reasoning next action...")
        code = await b.ProposeActions(
            screenshot,
            action,
            baml_options={"client_registry": client_registry, "collector": collector},
        )
        logger.info(f"Proposed code:\n{code}")

    # Save to cache
    session.cache.set_action(
        step_number,
        ActionCache(screenshot=screenshot_b64, action=action, proposed_code=code),
    )

    try:
        if client_name == "UITARS":
            from .automators import uitars as uitars_automator

            trace = await uitars_automator.execute(code, session.page)
        elif client_name == "InternVL3":
            from .automators import pyautogui as pyautogui_automator

            trace = await pyautogui_automator.execute(code, session.page)
        else:
            from .automators import custom as custom_automator

            trace = await custom_automator.execute(code, session.page, session)

        session.trace.extend(trace)
        await session.update_mcp_progress(f"Action successful step {step_number}!")
        logger.info(f"STEP_{step_number}_PASSED")
        print(f'Action PASSED {step_number}/{len(session.steps)}: "{action}".')
    except Exception as e:
        logger.info(f"STEP_{step_number}_FAILED: {str(e)}")
        print(
            f'Action FAILED {step_number}/{len(session.steps)}: "{action}", please try to be more specific about the element.'
        )
        raise


async def verify_postcondition(
    session: Session,
    action: str,
    assertion: str,
    config: Config,
    step_number: Optional[int] = None,
) -> None:
    if step_number is None:
        step_number = session.step_counter

    # For VSCode & MCP progress
    logger.info(f"Expectation: {assertion}")
    logger.info(f"VERIFYING_STEP_{step_number}: {assertion}")
    await session.update_mcp_progress(f"Verifying post-condition step {step_number}...")

    client_registry = config.assertion_generation
    collector = session.collector
    max_tries = config.max_tries
    history = session.get_history()

    screenshot_after_b64 = session.history[-1].screenshot
    screenshot_after = Image.from_base64("image/png", screenshot_after_b64)

    # Check cache for postcondition
    cached = session.cache.get_verify_postcondition(step_number, assertion)
    if cached:
        postcondition = cached.proposed_code
        logger.info(f"Cache hit for verify_postcondition at step {step_number}")
        logger.info(f"Postcondition (cached): {postcondition}")
        logger.info("Executing assertions...")
        passed, message = execute_assertion(postcondition, session)

        # Save to cache
        if passed:
            logger.info("Postcondition passed.")
            logger.info(f"VERIFYING_STEP_{step_number}_PASSED")
            await session.update_mcp_progress(
                f"Post-condition verified successfully step {step_number}!"
            )
            print(f"Verify PASSED {step_number}/{len(session.steps)}: {assertion}")
            session.cache.set_verify_postcondition(
                step_number,
                VerifyPostconditionCache.create(
                    assertion=assertion,
                    action=action,
                    proposed_code=postcondition,
                    history=history,
                    screenshot=screenshot_after_b64,
                ),
            )
            return
        else:
            logger.warning(f"Cached postcondition failed: {message}. Re-generating...")

    feedback: list[Feedback] = []
    message = "Post-condition verification failed after all retries"

    for _ in range(1, max_tries + 1):
        postcondition = await b.GeneratePostcondition(
            screenshot_after,
            history,
            action,
            assertion,
            feedback=feedback,
            baml_options={"client_registry": client_registry, "collector": collector},
        )
        logger.info(f"Postcondition: {postcondition}")
        logger.info("Executing assertions...")
        passed, message = execute_assertion(postcondition, session)
        if passed:
            print(f"Verify PASSED {step_number}/{len(session.steps)}: {assertion}")
            logger.info("Postcondition passed.")
            logger.info(f"VERIFYING_STEP_{step_number}_PASSED")
            await session.update_mcp_progress(
                f"Post-condition verified successfully step {step_number}!"
            )

            # Save to cache
            session.cache.set_verify_postcondition(
                step_number,
                VerifyPostconditionCache.create(
                    assertion=assertion,
                    action=action,
                    proposed_code=postcondition,
                    history=history,
                    screenshot=screenshot_after_b64,
                ),
            )
            return
        else:
            logger.info(f"Postcondition failed: {message}")
            feedback_item = Feedback(response=postcondition, reason=message)
            feedback.append(feedback_item)

    logger.info(f"VERIFYING_STEP_{step_number}_FAILED: {message}")
    print(f"\033[91mVerify FAILED {step_number}/{len(session.steps)}:")
    print(f"  Expectation: {assertion}")
    print(f"  Bug reported: {message}")
    print("\n  Steps leading to failure:")
    for i, step in enumerate(session.steps[:step_number], 1):
        print(f"    {i}. {step.action}")
    print("\033[0m")
    session.failed_step = step_number
    raise BugReport(message)
