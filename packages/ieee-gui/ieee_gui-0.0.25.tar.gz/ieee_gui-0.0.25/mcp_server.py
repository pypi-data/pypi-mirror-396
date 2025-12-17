import asyncio
import json
from pathlib import Path
import traceback
from typing import Annotated

from fastmcp import Context, FastMCP
from playwright.async_api import async_playwright, Browser

from src.run import run_test_from_file

mcp = FastMCP(
    "WebTestPilot ᕦ(ò_óˇ)ᕤ",
    instructions="""You are WebTestPilot (WTP), an AI agent that helps users run, and manage GUI E2E tests for web applications.
2 main entities you will work with:
- Tests: step-by-step natural language description of the test scenario and expected outcomes.
- Environments: Different configurations applied to tests, i.e. URL, ...""",
    version="0.0.2",
    host="0.0.0.0",
)


def resolve_fixture_from_id(
    workspace_folder: Path, fixture_id: str | None
) -> Path | None:
    if not fixture_id:
        return None

    fixture_folder = workspace_folder / ".webtestpilot" / ".fixture"
    for filepath in fixture_folder.rglob("*.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            fixture_data = json.load(f)
            if fixture_data.get("id") == fixture_id:
                return filepath

    raise FileNotFoundError(f"Fixture with ID {fixture_id} not found.")


def resolve_test_from_id(workspace_folder: Path, test_id: str) -> Path | None:
    if not test_id:
        return None

    test_folder = workspace_folder / ".webtestpilot" / ".test"
    for filepath in test_folder.rglob("*.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                test_data = json.load(f)
            except json.JSONDecodeError:
                print("Failed to decode JSON for test file:", filepath)
                continue
            if test_data.get("id") == test_id:
                return filepath

    raise FileNotFoundError(f"Test with ID {test_id} not found.")


def resolve_environment_from_id(
    workspace_folder: Path, environment_id: str
) -> Path | None:
    if not environment_id:
        return None

    environment_folder = workspace_folder / ".webtestpilot" / ".environment"
    for filepath in environment_folder.rglob("*.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                environment_data = json.load(f)
            except json.JSONDecodeError:
                print("Failed to decode JSON for environment file:", filepath)
                continue
            if environment_data.get("id") == environment_id:
                return filepath

    raise FileNotFoundError(f"Environment with id {environment_id} not found.")


def list_all_tests_in_workspace(workspace_folder: Path) -> list[dict]:
    test_folder = workspace_folder / ".webtestpilot" / ".test"
    tests = []

    if not test_folder.exists():
        return []

    for filepath in test_folder.rglob("*.json"):
        parent_path = filepath.relative_to(test_folder).parent

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                test_data = json.load(f)
                tests.append(
                    {
                        "id": test_data.get("id", ""),
                        "name": test_data.get("name", "Unnamed Test"),
                        "parent_path": str(parent_path),
                    }
                )
        except json.JSONDecodeError:
            print("Failed to decode JSON for test file:", filepath)
            continue

    return tests


def list_all_environments_in_workspace(workspace_folder: Path) -> list[dict]:
    environment_path = workspace_folder / ".webtestpilot" / ".environment"
    environments: list[dict] = []

    if not environment_path.exists():
        return environments

    for filepath in environment_path.rglob("*.json"):
        parent_path = filepath.relative_to(environment_path).parent

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                environments.append(
                    {
                        "id": data.get("id", ""),
                        "name": data.get("name", "Unnamed Environment"),
                        "parent_path": str(parent_path),
                    }
                )
        except json.JSONDecodeError:
            print("Failed to decode JSON for test file:", filepath)
            continue

    return environments


def list_tests_in_folder(workspace_folder: Path, folder_path: str) -> list[dict]:
    """List all tests within a specific folder path"""
    test_folder = workspace_folder / ".webtestpilot" / ".test" / folder_path
    tests = []

    if not test_folder.exists():
        return []

    for filepath in test_folder.rglob("*.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            test_data = json.load(f)
            tests.append(
                {
                    "id": test_data.get("id", ""),
                    "name": test_data.get("name", "Unnamed Test"),
                    "path": str(filepath),
                }
            )

    return tests


async def _execute_single_test(
    browser: Browser,
    workspace_folder: Path,
    test_id: str,
    environment_path: Path,
    environment_id: str,
    ctx: Context,
) -> dict:
    """Execute a single test with given environment"""
    test_path = resolve_test_from_id(workspace_folder, test_id)
    assert test_path is not None, "Cant find test ID provided."

    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        fixture_id = test_data.get("fixtureId", "")
        test_name = test_data.get("name", "Unnamed Test")

    fixture_path = resolve_fixture_from_id(workspace_folder, fixture_id)
    cache_path = (
        workspace_folder
        / ".webtestpilot"
        / ".cache"
        / f"{test_id} - {environment_id}"
        / "cache.json"
    )

    try:
        result = await run_test_from_file(
            browser=browser,
            test_file_path=str(test_path),
            config_path=str(Path(__file__).parent / "src" / "config.yaml"),
            target_id=None,
            enable_assertions=True,
            fixture_file_path=str(fixture_path) if fixture_path else None,
            environment_file_path=str(environment_path),
            cache_path=cache_path,
            mcp_report_progress=ctx.report_progress,
        )
        result["test_id"] = test_id
        result["test_name"] = test_name
        return result
    except Exception as e:
        return {
            "test_id": test_id,
            "test_name": test_name,
            "success": False,
            "error": str(e),
        }


@mcp.tool(
    name="run_gui_test",
    description="Run a GUI E2E test based on Natural Language description and expectation using WebTestPilot agent",
    tags={"webtestpilot", "e2e", "gui", "testing"},
)
async def run_test(
    workspace_folder: Annotated[Path, "The user's current workspace folder"],
    test_id: Annotated[str, "ID of the test to run"],
    environment_id: Annotated[str, "ID of the environment to use"],
    ctx: Context,
) -> dict:
    try:
        test_path = resolve_test_from_id(workspace_folder, test_id)

        assert test_path is not None, f"Test with ID {test_id} not found."

        environment_path = resolve_environment_from_id(workspace_folder, environment_id)
        assert environment_path is not None, "Cant find environment ID provided."

        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(
                "http://localhost:9222"
            )
            return await _execute_single_test(
                browser,
                workspace_folder,
                test_id,
                environment_path,
                environment_id,
                ctx,
            )
    except Exception as e:
        traceback.print_exc()
        await ctx.log(f"Error running test {test_id}: {traceback.format_exc()}")
        return {
            "test_id": test_id,
            "success": False,
            "error": str(e),
        }


# @mcp.tool(
#     name="run_multiple_gui_tests",
#     description="Run multiple GUI E2E tests by their IDs (max 3 tests). Tests run in parallel.",
#     tags={"webtestpilot", "e2e", "gui", "testing", "batch"},
# )
# async def run_multiple_tests(
#     workspace_folder: Annotated[Path, "The user's current workspace folder"],
#     test_ids: Annotated[list[str], "List of test IDs to run"],
#     environment_id: Annotated[str, "ID of the environment to use for all tests"],
#     ctx: Context,
# ) -> dict:
#     test_ids = list(set(test_ids))  # Deduplicate

#     if len(test_ids) > 3:
#         return {
#             "error": f"Cannot run {len(test_ids)} tests. Maximum is 3.",
#             "test_count": len(test_ids),
#         }

#     if not test_ids:
#         return {"error": "No test IDs provided"}

#     environment_path = resolve_environment_from_id(workspace_folder, environment_id)
#     assert environment_path is not None, "Cant find environment ID provided."

#     await ctx.log(f"Running {len(test_ids)} tests in parallel")

#     async with async_playwright() as playwright:
#         browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
#         tasks = [
#             _execute_single_test(
#                 browser,
#                 workspace_folder,
#                 test_id,
#                 environment_path,
#                 environment_id,
#                 ctx,
#             )
#             for test_id in test_ids
#         ]
#         results = await asyncio.gather(*tasks)

#     passed = sum(1 for r in results if r.get("success"))
#     return {
#         "total_tests": len(test_ids),
#         "passed": passed,
#         "failed": len(test_ids) - passed,
#         "results": results,
#     }


@mcp.tool(
    name="list_gui_tests_and_environments",
    description="List all GUI E2E tests & environments in a workspace. Only workspace_folder is needed.",
    tags={"listing"},
)
async def list_all(
    workspace_folder: Annotated[
        Path, "The user's current workspace folder, must be full path."
    ],
    ctx: Context,
) -> dict:
    test_folder = workspace_folder / ".webtestpilot" / ".test"
    await ctx.log("Listing all in: " + str(test_folder))

    tests = list_all_tests_in_workspace(workspace_folder)
    environments: list[dict] = list_all_environments_in_workspace(workspace_folder)

    return {
        "tests": tests,
        "environments": environments,
        "workspace_folder": workspace_folder,
        "accessed_at": ctx.request_id,
        "total": len(tests),
    }


def main():
    """Main entry point for the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
