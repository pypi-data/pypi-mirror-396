import argparse
import asyncio
import json
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from cli_utils import (
    find_workspace_root,
    resolve_test_by_partial_id,
    resolve_environment_by_name,
    resolve_fixture_from_id,
    list_tests_in_folder,
    list_available_environments,
)
from src.run import run_test_from_file
from src.config import Config
import os

logger = logging.getLogger(__name__)

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def format_status(success: bool, short: bool = False) -> str:
    """Format pass/fail status with color."""
    if short:
        return f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
    return f"{GREEN}✓ PASSED{RESET}" if success else f"{RED}✗ FAILED{RESET}"


def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate pass/fail statistics from results."""
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    success_rate = passed / len(results) if results else 0
    return {
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "success_rate": success_rate,
    }


def print_results_table(
    results: List[Dict[str, Any]], 
    num_runs: int, 
    test_names: List[str]
) -> None:
    """Print a table with test names on Y-axis and run numbers on X-axis."""
    # Group results by test name
    by_test = defaultdict(list)
    for r in results:
        by_test[r["test_name"]].append(r)
    
    # Calculate column widths
    max_name_len = max(len(name) for name in test_names) if test_names else 10
    max_name_len = max(max_name_len, 10)  # Minimum width
    run_col_width = 6  # Width for each run column (e.g., "Run 1")
    
    # Build header
    header = "Test Name".ljust(max_name_len)
    for run_num in range(1, num_runs + 1):
        header += f" | R{run_num}".center(run_col_width)
    header += " | Total"
    
    print()
    print("=" * len(header.replace(GREEN, "").replace(RED, "").replace(YELLOW, "").replace(RESET, "")))
    print("RESULTS TABLE")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    
    # Print each test row
    for test_name in test_names:
        runs = by_test.get(test_name, [])
        # Sort runs by run_number
        runs_sorted = sorted(runs, key=lambda r: r.get("run_number", 1))
        
        row = test_name[:max_name_len].ljust(max_name_len)
        test_passed = 0
        for run_num in range(1, num_runs + 1):
            # Find result for this run
            run_result = next((r for r in runs_sorted if r.get("run_number") == run_num), None)
            if run_result:
                success = run_result["success"]
                if success:
                    test_passed += 1
                status = format_status(success, short=True)
                row += f" |  {status}   "
            else:
                row += " |  -   "
        
        # Total column
        test_total = len(runs_sorted)
        if test_passed == test_total and test_total > 0:
            total_str = f"{GREEN}{test_passed}/{test_total}{RESET}"
        elif test_passed == 0 and test_total > 0:
            total_str = f"{RED}{test_passed}/{test_total}{RESET}"
        else:
            total_str = f"{YELLOW}{test_passed}/{test_total}{RESET}"
        row += f" | {total_str}"
        
        print(row)
    
    print("=" * len(header))


def build_result_data(
    results: List[Dict[str, Any]],
    stats: Dict[str, Any],
    start_time: datetime,
    end_time: datetime,
    environment: str,
    test_id: Optional[str] = None,
    test_name: Optional[str] = None,
    folder: Optional[str] = None,
    num_runs: int = 1,
    num_tests: int = 1,
) -> Dict[str, Any]:
    """Build the JSON result data structure."""
    summary = {
        "environment": environment,
        "total_runs": len(results),
        "passed": stats["passed"],
        "failed": stats["failed"],
        "success_rate": round(stats["success_rate"], 4),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_duration_seconds": round((end_time - start_time).total_seconds(), 2),
    }
    
    if folder:
        summary["folder"] = folder
        summary["total_tests"] = num_tests
        summary["runs_per_test"] = num_runs
    else:
        summary["test_id"] = test_id
        summary["test_name"] = test_name
    
    return {
        "summary": summary,
        "runs": [
            {
                "test_id": r.get("test_id", test_id or ""),
                "test_name": r.get("test_name", test_name or ""),
                "run_number": r.get("run_number", 1),
                "success": r.get("success", False),
                "duration_seconds": r.get("duration_seconds", 0),
                "errors": r.get("errors", []),
            }
            for r in results
        ],
    }


def save_results(
    result_data: Dict[str, Any],
    output_path: Optional[str],
    workspace_folder: Path,
    default_name: str,
    timestamp: datetime,
) -> Path:
    """Save results to JSON file and return the path."""
    if output_path:
        path = Path(output_path)
    else:
        ts = timestamp.strftime("%Y%m%d_%H%M%S")
        results_dir = workspace_folder / ".webtestpilot" / ".results"
        results_dir.mkdir(parents=True, exist_ok=True)
        path = results_dir / f"{default_name}_{ts}.json"
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)
    
    return path


async def execute_test_runs(
    test_files: List[Path],
    environment_path: Path,
    workspace_folder: Path,
    num_runs: int,
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    """Execute tests with multiple runs, returning all results."""
    all_results = []
    
    for i, test_file in enumerate(test_files, 1):
        # Load test metadata
        with open(test_file, "r", encoding="utf-8") as f:
            test_data = json.load(f)
            test_name = test_data.get("name", test_file.stem)
            test_id = test_data.get("id", "")
        
        if verbose:
            print(f"\n[{i}/{len(test_files)}] Test: {test_name}")
            print(f"ID: {test_id}")
            print(f"File: {test_file.name}")
        
        for run_num in range(1, num_runs + 1):
            if verbose:
                if num_runs > 1:
                    print(f"  Run {run_num}/{num_runs}:", end=" ")
                else:
                    print("  Result:", end=" ")
            
            start_time = time.time()
            result = await run_single_test(
                test_file,
                environment_path,
                workspace_folder,
            )
            duration = time.time() - start_time
            
            result["run_number"] = run_num
            result["duration_seconds"] = round(duration, 2)
            all_results.append(result)
            
            if verbose:
                status = format_status(result["success"])
                print(f"{status} ({duration:.1f}s)")
    
    return all_results


async def run_single_test(
    test_path: Path,
    environment_path: Path,
    workspace_folder: Path,
) -> dict:
    """Execute a single test"""
    # Load test to get fixture ID and generate cache path
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        fixture_id = test_data.get("fixtureId", "")
        test_id = test_data.get("id", "")
        test_name = test_data.get("name", "Unnamed Test")

    # Load environment to get ID for cache path
    with open(environment_path, "r", encoding="utf-8") as f:
        env_data = json.load(f)
        environment_id = env_data.get("id", "")

    fixture_path = resolve_fixture_from_id(workspace_folder, fixture_id)
    cache_path = (
        workspace_folder
        / ".webtestpilot"
        / ".cache"
        / f"{test_id} - {environment_id}"
        / "cache.json"
    )

    config_path = str(Path(__file__).parent / "src" / "config.yaml")
    cdp_endpoint = "http://localhost:9222"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(cdp_endpoint)
        result = await run_test_from_file(
            browser=browser,
            test_file_path=str(test_path),
            config_path=config_path,
            target_id=None,
            fixture_file_path=str(fixture_path) if fixture_path else None,
            environment_file_path=str(environment_path),
            enable_assertions=True,
            cache_path=cache_path,
        )
        # Add test metadata to result for logging
        result["test_name"] = test_name
        result["test_id"] = test_id
        return result


def main():
    """Main CLI entry point with simplified syntax"""
    parser = argparse.ArgumentParser(
        description="WebTestPilot CLI - Run automated web tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gui-test 1.1.1 --env production
  gui-test ieee-gui /12306/dining-service --env staging
  gui-test ieee-gui "test name with spaces" --env dev
        """,
    )

    parser.add_argument(
        "test_id",
        type=str,
        help="Test ID (1.1.1, ...), exact test name, or folder path (starting with /, e.g. /ctrip/manage-addresses)",
    )

    parser.add_argument(
        "--env",
        type=str,
        required=True,
        help="Environment name (e.g., production, staging, dev)",
    )

    parser.add_argument(
        "--openai_api_key",
        type=str,
        required=False,
        help="OpenAI API key (will be set to OPENAI_QQ_API_KEY environment variable)",
    )

    parser.add_argument(
        "--runs", "-n",
        type=int,
        default=1,
        help="Number of times to run the test(s) (default: 1)",
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        required=False,
        help="Path to output JSON results file (default: .webtestpilot/.results/{test_id}_{timestamp}.json)",
    )

    args = parser.parse_args()

    # Set OpenAI API key if provided
    if args.openai_api_key:
        os.environ["OPENAI_QQ_API_KEY"] = args.openai_api_key

    # os.environ["BAML_LOG"] = "error"

    # Load config early to initialize logging before any operations
    config_path = Path(__file__).parent / "src" / "config.yaml"
    Config.load(config_path)

    # Find workspace root
    current_dir = Path.cwd()
    
    # Load environment variables from current_dir/.env
    load_dotenv(current_dir / ".env")
    
    # Print OpenAI QQ API key status
    openai_key = os.environ.get("OPENAI_QQ_API_KEY")
    if openai_key:
        print(f"OPENAI_QQ_API_KEY: {openai_key[:10]}...{openai_key[-4:] if len(openai_key) > 14 else ''}")
    else:
        print("OPENAI_QQ_API_KEY: Not set")
    
    workspace_folder = find_workspace_root(current_dir)

    if not workspace_folder:
        print(
            """Error: Could not find .webtestpilot folder in current directory
Hint: Go to folder with .webtestpilot inside or move .webtestpilot folder here."""
        )
        sys.exit(1)
        
    

    print(f"Using workspace: {workspace_folder}")

    # Resolve environment
    environment_path = resolve_environment_by_name(workspace_folder, args.env)
    if not environment_path:
        available_envs = list_available_environments(workspace_folder)
        print(f"Error: Environment '{args.env}' not found")
        if available_envs:
            print("\nAvailable environments:")
            for env in available_envs:
                print(f"  - {env}")
        else:
            print("  No environments found in workspace")
        sys.exit(1)

    print(f"Using environment: {args.env} ({environment_path})")

    # Determine if test_id is a folder path or test ID
    is_folder = args.test_id.startswith("/")
    num_runs = args.runs

    if is_folder:
        # Handle folder mode - run all tests in folder
        folder_path = args.test_id.lstrip("/")
        test_files = list_tests_in_folder(workspace_folder, folder_path)

        if not test_files:
            print(f"Error: No tests found in folder '{folder_path}'")
            sys.exit(1)

        # Get test names for table display
        test_names = []
        for tf in test_files:
            with open(tf, "r", encoding="utf-8") as f:
                td = json.load(f)
                test_names.append(td.get("name", tf.stem))

        print(f"Found {len(test_files)} test(s) in folder '{folder_path}'")
        if num_runs > 1:
            print(f"Each test will be run {num_runs} time(s)")

        overall_start_time = datetime.now()

        # Run all tests
        all_results = asyncio.run(
            execute_test_runs(test_files, environment_path, workspace_folder, num_runs)
        )
        overall_end_time = datetime.now()

        # Calculate and print statistics
        stats = calculate_statistics(all_results)

        # Print results table
        print_results_table(all_results, num_runs, test_names)

        # Print summary
        print(f"\nFolder: {folder_path}")
        print(f"Environment: {args.env}")
        print(f"Tests: {len(test_files)} | Runs per test: {num_runs} | Total runs: {stats['total']}")
        print(f"Total: {GREEN}{stats['passed']} passed{RESET}, {RED}{stats['failed']} failed{RESET} ({stats['success_rate']:.1%} success rate)")

        # Build and save results
        result_data = build_result_data(
            results=all_results,
            stats=stats,
            start_time=overall_start_time,
            end_time=overall_end_time,
            environment=args.env,
            folder=folder_path,
            num_runs=num_runs,
            num_tests=len(test_files),
        )

        safe_folder = folder_path.replace("/", "_")
        output_path = save_results(
            result_data, args.output, workspace_folder, safe_folder, overall_start_time
        )
        print(f"Results saved to: {output_path}")

        sys.exit(0 if stats["failed"] == 0 else 1)

    else:
        # Handle single test mode
        test_path = resolve_test_by_partial_id(workspace_folder, args.test_id)

        if not test_path:
            print(f"Error: No test found with ID containing '{args.test_id}'")
            sys.exit(1)

        # Load test metadata
        with open(test_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
            test_name = test_data.get("name", test_path.stem)
            test_id = test_data.get("id", "")

        print(f"\nRunning: {test_name}")
        print(f"ID: {test_id}")
        print(f"File: {test_path.name}")
        if num_runs > 1:
            print(f"# Runs: {num_runs}")

        overall_start_time = datetime.now()

        # Run the test
        all_results = asyncio.run(
            execute_test_runs([test_path], environment_path, workspace_folder, num_runs)
        )
        overall_end_time = datetime.now()

        # Calculate statistics
        stats = calculate_statistics(all_results)

        # Print results table for multi-run
        if num_runs > 1:
            print_results_table(all_results, num_runs, [test_name])
            print(f"\nTest: {test_name}")
            print(f"ID: {test_id}")
            print(f"Environment: {args.env}")
            print(f"Total: {GREEN}{stats['passed']} passed{RESET}, {RED}{stats['failed']} failed{RESET} ({stats['success_rate']:.1%} success rate)")

        # Build and save results
        result_data = build_result_data(
            results=all_results,
            stats=stats,
            start_time=overall_start_time,
            end_time=overall_end_time,
            environment=args.env,
            test_id=test_id,
            test_name=test_name,
            num_runs=num_runs,
        )

        output_path = save_results(
            result_data, args.output, workspace_folder, test_id, overall_start_time
        )
        print(f"Results saved to: {output_path}")

        sys.exit(0 if stats["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
