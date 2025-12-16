import asyncio
import logging
import traceback
from pathlib import Path
from typing import Callable, Optional

from playwright.async_api import Page

from .baml_client.types import Step
from .config import Config
from .executor import (
    BugReport,
    execute_action,
    verify_postcondition,
)
from .executor.assertion_api import Session
from .parser import parse

logger = logging.getLogger(__name__)
Hook = Callable[[BugReport], None]


class WebTestPilot:
    @staticmethod
    def parse(config: Config, description: str) -> list["Step"]:
        test_case = parse(description, config)
        return test_case.steps

    @staticmethod
    async def run(
        session: Session,
        steps: list["Step"],
        assertion: bool,
        hooks: Optional[list[Hook]] = None,
    ) -> Session:
        """
        This is used in baseline runners as well, sequential execution of steps.
        Session here is initialized from outside.
        Execute a test case on the given Session.

        Params:
            session: The current test session.
            test_input: Description string, a single Step, or list of Steps.
            hooks: Optional list of hooks to trigger (Callables) when a BugReport occurs.

        Returns:
            Session: The session object with success status and bug_report if failed.
        """
        assert isinstance(steps, list)
        assert all(isinstance(s, Step) for s in steps)

        config = session.config
        hooks = hooks or []

        for step in steps:
            try:
                await execute_action(session, step.action, config)
                page_snapshot = await session.get_current_page_snapshot()
                await session.capture_state(
                    prev_action=step.action, page_snapshot=page_snapshot
                )
                if assertion and step.expectation:
                    await verify_postcondition(
                        session, step.action, step.expectation, config
                    )

            except BugReport as report:
                logger.error(f"Bug reported: {str(report)}")
                session.success = False
                session.bug_report = report
                for hook in hooks:
                    try:
                        hook(report)
                    except Exception:
                        logger.error("Exception in hook:", traceback.format_exc())
                return session
            except Exception as e:
                logger.error("Exception in test session:", traceback.format_exc())
                session.success = False
                session.bug_report = e
                return session

        session.cache.save()
        return session

    @staticmethod
    async def run_parallel(
        page: Page,
        config: Config,
        steps: list["Step"],
        assertion: bool,
        hooks: Optional[list[Hook]] = None,
        cache_path: Optional[Path] = None,
        mcp_report_progress: Optional[Callable] = None,
    ) -> Session:
        """
        Main differences:
        - Session is initialized in this function.
        - These steps are in parallel: verify_postcondition (current step) // execute_action (next step)
        """
        assert isinstance(steps, list)
        assert all(isinstance(s, Step) for s in steps)
        assert len(steps) >= 1, "At least one step is required"

        hooks = hooks or []

        # Parallel strategy:
        # - Step 1: Initialize session (and capture initial state) + first action (before any steps)
        # - Step 2: The rest: capture_state & verify_postcondition (current step) // execute_action (next step)

        # Step 1: Initialize session + first action in parallel
        session = await Session.create(
            page,
            config,
            steps,
            defer_capture_state=True,
            cache_path=cache_path,
            mcp_report_progress=mcp_report_progress,
        )

        page_snapshot = await session.get_current_page_snapshot()
        capture_task = asyncio.create_task(
            session.capture_state(
                prev_action=None, page_snapshot=page_snapshot, step_number=0
            )
        )
        first_action_task = asyncio.create_task(
            execute_action(session, steps[0].action, config, step_number=1)
        )

        await capture_task
        await first_action_task

        # Step 2. The rest: capture_state & verify_postcondition (current step) // execute_action (next step)
        for step_idx, (step, next_step) in enumerate(
            zip(steps, steps[1:] + [None]), start=1
        ):
            try:
                # HACK: Ensure page is stable (some components & data render slow esp on page changes)
                try:
                    await session.page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass

                # Lock the snapshot to be before (action execution + verification) so they both look at same state snapshot.
                page_snapshot = await session.get_current_page_snapshot()
                current_step_num = step_idx
                next_step_num = step_idx + 1

                async def capture_and_verify(step: Step, step_num: int):
                    # Verify always after capture.
                    await session.capture_state(
                        prev_action=step.action,
                        page_snapshot=page_snapshot,
                        step_number=step_num,
                    )
                    if assertion and step.expectation:
                        await verify_postcondition(
                            session,
                            step.action,
                            step.expectation,
                            config,
                            step_number=step_num,
                        )

                # Step N's (capture -> verify) // Step N+1's action (if present)
                verify_task = asyncio.create_task(
                    capture_and_verify(step, current_step_num)
                )
                action_task: asyncio.Task[None] | None = (
                    asyncio.create_task(
                        execute_action(
                            session, next_step.action, config, step_number=next_step_num
                        )
                    )
                    if next_step
                    else None
                )

                # Collect both results
                await verify_task
                if action_task:
                    await action_task
                    
                # session.cache.save_at_step(current_step_num)
            except BugReport as report:
                logger.info(f"Bug reported: {str(report)}")
                session.success = False
                session.bug_report = report
                for hook in hooks:
                    try:
                        hook(report)
                    except Exception:
                        logger.info("Exception in hook:", traceback.format_exc())
                return session
            except Exception as e:
                logger.info("Exception in test session:", traceback.format_exc())
                session.success = False
                session.bug_report = e
                return session

        session.cache.save()
        return session


if __name__ == "__main__":
    pass
