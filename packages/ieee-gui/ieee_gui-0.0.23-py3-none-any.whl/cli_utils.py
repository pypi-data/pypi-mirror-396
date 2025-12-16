"""Shared utilities for CLI tools"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def find_workspace_root(current_path: Path) -> Path | None:
    """Find the workspace root by looking for .webtestpilot folder"""
    search_path = current_path
    while search_path != search_path.parent:
        if (search_path / ".webtestpilot").exists():
            return search_path
        search_path = search_path.parent
    return None


def resolve_test_by_partial_id(workspace_folder: Path, partial_id: str) -> Path | None:
    """Find the first test with ID containing the partial_id string"""
    test_folder = workspace_folder / ".webtestpilot" / ".test"
    if not test_folder.exists():
        return None

    matching_tests = []
    for filepath in test_folder.rglob("*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                test_data = json.load(f)
                test_id = test_data.get("id", "")
                if partial_id in test_id:
                    matching_tests.append((test_id, filepath))
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON for test file: {filepath}")
            continue
    
    if not matching_tests:
        return None
    
    matching_tests.sort(key=lambda x: x[0])
    return matching_tests[0][1]


def resolve_environment_by_name(workspace_folder: Path, env_name: str) -> Path | None:
    """Find the first environment with matching name"""
    environment_folder = workspace_folder / ".webtestpilot" / ".environment"
    if not environment_folder.exists():
        return None

    for filepath in environment_folder.rglob("*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                env_data = json.load(f)
                if env_data.get("name", "").lower() == env_name.lower():
                    return filepath
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON for environment file: {filepath}")
            continue
    return None


def resolve_fixture_from_id(
    workspace_folder: Path, fixture_id: str | None
) -> Path | None:
    """Resolve fixture path from fixture ID"""
    if not fixture_id:
        return None

    fixture_folder = workspace_folder / ".webtestpilot" / ".fixture"
    if not fixture_folder.exists():
        return None

    for filepath in fixture_folder.rglob("*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                fixture_data = json.load(f)
                if fixture_data.get("id") == fixture_id:
                    return filepath
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON for fixture file: {filepath}")
            continue
    return None


def list_tests_in_folder(workspace_folder: Path, folder_path: str) -> list[Path]:
    """List all test files within a specific folder path"""
    test_folder = workspace_folder / ".webtestpilot" / ".test" / folder_path
    if not test_folder.exists():
        return []

    test_files = []
    for filepath in test_folder.rglob("*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json.load(f)  # Validate it's valid JSON
                test_files.append(filepath)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON for test file: {filepath}")
            continue
    return test_files


def list_available_environments(workspace_folder: Path) -> list[str]:
    """List all available environment names in the workspace"""
    environment_folder = workspace_folder / ".webtestpilot" / ".environment"
    if not environment_folder.exists():
        return []

    env_names = []
    for filepath in environment_folder.rglob("*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                env_data = json.load(f)
                env_name = env_data.get("name", "")
                if env_name:
                    env_names.append(env_name)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON for environment file: {filepath}")
            continue
    return sorted(env_names)
