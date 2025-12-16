import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from playwright.async_api import async_playwright

from src.run import run_test_from_file

logger = logging.getLogger(__name__)
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WebTestPilot CLI - Run automated web tests from VS Code"
    )

    parser.add_argument("test_file", type=str, help="Path to the test JSON file")

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config.yaml file (default: config.yaml)",
    )

    parser.add_argument(
        "--cdp-endpoint",
        type=str,
        default="http://localhost:9222",
        help="CDP endpoint URL (default: http://localhost:9222)",
    )

    parser.add_argument(
        "--target-id",
        type=str,
        help="id of cdp session",
    )

    parser.add_argument(
        "--no-assertions",
        action="store_true",
        help="Disable assertion verification (only execute actions)",
    )

    parser.add_argument(
        "--fixture-file-path",
        type=str,
        default="",
        help="Path to fixture file",
    )

    parser.add_argument(
        "--environment-file-path",
        type=str,
        default="",
        help="Path to environment file",
    )

    parser.add_argument(
        "--cache-path",
        type=str,
        default="",
        help="Path to cache file (e.g., .webtestpilot/.cache/test_id.json)",
    )

    args = parser.parse_args()
    cache_path = Path(args.cache_path) if args.cache_path else None

    # Run the test
    async def run():
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(args.cdp_endpoint)
            return await run_test_from_file(
                browser=browser,
                test_file_path=args.test_file,
                config_path=args.config,
                target_id=args.target_id,
                fixture_file_path=args.fixture_file_path,
                environment_file_path=args.environment_file_path,
                enable_assertions=not args.no_assertions,
                cache_path=cache_path,
            )
    
    result = asyncio.run(run())

    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    logger.debug(f"Exiting with code: {0 if result['success'] else 1}")
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
