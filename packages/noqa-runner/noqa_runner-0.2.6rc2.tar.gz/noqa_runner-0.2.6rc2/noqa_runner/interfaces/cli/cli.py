#!/usr/bin/env python3
"""
noqa Runner - CLI for running mobile tests via Agent API

Usage:
    python -m runner run --device-id UDID --appium-url URL --build-path PATH \\
        --noqa-api-token TOKEN --case-input-json JSON
"""

from __future__ import annotations

import asyncio
import json
import uuid

import typer
from typing_extensions import Annotated

from noqa_runner.application.run_test_session import RunnerSession
from noqa_runner.config import sentry_init, settings
from noqa_runner.domain.exceptions import RunnerException
from noqa_runner.domain.models.test_info import RunnerTestInfo
from noqa_runner.logging_config import configure_logging, get_logger
from noqa_runner.utils.graceful_shutdown import install_signal_handlers

app = typer.Typer(
    name="noqa-runner",
    help="noqa Mobile Test Runner - Execute mobile tests via Agent API",
    add_completion=False,
)

logger = get_logger(__name__)


@app.command()
def run(
    noqa_api_token: Annotated[str, typer.Option(help="noqa API authentication token")],
    device_id: Annotated[
        str | None,
        typer.Option(help="Device UDID for testing (required for local runs)"),
    ] = None,
    build_path: Annotated[
        str | None, typer.Option(help="Path to IPA build file (local installation)")
    ] = None,
    app_store_id: Annotated[
        str | None, typer.Option(help="App Store ID for TestFlight installation")
    ] = None,
    app_bundle_id: Annotated[
        str | None,
        typer.Option(
            help="App bundle ID (required for TestFlight, auto-extracted from build)"
        ),
    ] = None,
    case_input_json: Annotated[
        str | None,
        typer.Option(
            help="JSON string with test cases (list of {test_id, case_instructions, bundle_id})"
        ),
    ] = None,
    case_ids: Annotated[
        list[str] | None,
        typer.Option(
            help="List of test case UUIDs to fetch from backend (not implemented yet)"
        ),
    ] = None,
    app_context: Annotated[
        str | None, typer.Option(help="Optional application context information")
    ] = None,
    agent_api_url: Annotated[
        str | None, typer.Option(help="Agent API base URL")
    ] = None,
    log_level: Annotated[
        str | None, typer.Option(help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    ] = None,
    appium_url: Annotated[str | None, typer.Option(help="Appium server URL")] = None,
    apple_developer_team_id: Annotated[
        str | None, typer.Option(help="Apple Developer Team ID for code signing")
    ] = None,
    max_steps: Annotated[
        int | None, typer.Option(help="Maximum number of steps for test execution")
    ] = None,
):
    """
    Run mobile tests on device via Agent API

    Example (with local build):
        noqa-runner run --device-id abc123 \\
            --build-path /path/to/app.ipa --noqa-api-token secret \\
            --case-input-json '[{"test_id":"uuid","case_instructions":"Login"}]' \\
            --apple-developer-team-id TEAM123456

    Example (with TestFlight):
        noqa-runner run --device-id abc123 \\
            --app-store-id 123456789 --app-bundle-id com.example.app \\
            --noqa-api-token secret \\
            --case-input-json '[{"test_id":"uuid","case_instructions":"Login"}]'
    """
    try:
        asyncio.run(
            _run_async(
                device_id=device_id,
                app_build_path=build_path,
                app_store_id=app_store_id,
                app_bundle_id=app_bundle_id,
                noqa_api_token=noqa_api_token,
                case_input_json=case_input_json,
                case_ids=case_ids,
                app_context=app_context,
                agent_api_url=agent_api_url,
                log_level=log_level,
                appium_url=appium_url,
                apple_developer_team_id=apple_developer_team_id,
                max_steps=max_steps,
            )
        )
    except (KeyboardInterrupt, SystemExit):
        # Graceful shutdown on external termination
        typer.echo("\n⚠️  Test interrupted by user", err=True)
        raise typer.Exit(code=130)  # Standard exit code for SIGINT


async def _run_async(
    noqa_api_token: str,
    device_id: str | None,
    app_build_path: str | None,
    app_store_id: str | None,
    app_bundle_id: str | None,
    case_input_json: str | None,
    case_ids: list[str] | None,
    app_context: str | None,
    agent_api_url: str | None,
    log_level: str | None,
    appium_url: str | None,
    apple_developer_team_id: str | None,
    max_steps: int | None,
):
    # Apply defaults
    if log_level is None:
        log_level = "INFO"

    # Configure logging
    configure_logging(is_simple=True, log_level=log_level)

    # Initialize Sentry
    sentry_init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)

    # Install signal handlers for graceful shutdown
    install_signal_handlers()

    # Validate inputs
    if not case_input_json and not case_ids:
        logger.error(
            "validation_error",
            error="Either --case-input-json or --case-ids must be provided",
        )
        typer.echo(
            "Error: Either --case-input-json or --case-ids must be provided", err=True
        )
        raise typer.Exit(code=1)

    if apple_developer_team_id and len(apple_developer_team_id) != 10:
        logger.error(
            "validation_error",
            error="Apple Developer Team ID must be exactly 10 characters",
        )
        typer.echo(
            "Error: Apple Developer Team ID must be exactly 10 characters", err=True
        )
        raise typer.Exit(code=1)

    if case_ids:
        logger.error("feature_not_implemented", feature="--case-ids")
        typer.echo(
            "Error: --case-ids is not implemented yet. Use --case-input-json instead.",
            err=True,
        )
        raise typer.Exit(code=1)

    # Parse test cases from JSON
    try:
        tests_data = json.loads(case_input_json)
        tests = [
            RunnerTestInfo(
                test_id=test.get("test_id", uuid.uuid4().hex),
                case_instructions=test["case_instructions"],
                case_name=test.get("case_name", ""),
            )
            for test in tests_data
        ]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error("json_parse_error", error=str(e))
        typer.echo(f"Error: Invalid JSON format: {e}", err=True)
        raise typer.Exit(code=1)

    # Run tests using application
    test_session = RunnerSession()
    try:
        results = await test_session.execute(
            noqa_api_token=noqa_api_token,
            tests=tests,
            app_context=app_context,
            app_bundle_id=app_bundle_id,
            app_store_id=app_store_id,
            app_build_path=app_build_path,
            apple_developer_team_id=apple_developer_team_id,
            device_id=device_id,
            appium_url=appium_url,
            agent_api_url=agent_api_url,
            max_steps=max_steps,
        )

        # Output results as JSON
        results_json = json.dumps(
            [result.export_dict() for result in results], indent=2
        )
        typer.echo(results_json)
    except RunnerException as e:
        # All runner exceptions (BuildNotFoundError, AppiumConnectionError, etc.)
        logger.error("runner_error", error=str(e), error_type=type(e).__name__)
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)
    except asyncio.CancelledError:
        # Tests were cancelled - this is expected on shutdown
        logger.info("Test session cancelled by shutdown signal")
        typer.echo("\n⚠️  Tests interrupted by shutdown signal", err=True)
        raise typer.Exit(code=130)


@app.command()
def run_cloud():
    """Run tests on AWS Device Farm (not implemented yet)"""
    typer.echo("⚠️  run_cloud command is not implemented yet")
    typer.echo("This command will allow running tests on AWS Device Farm in the future")
    raise typer.Exit(code=1)


def main():
    """Entry point for CLI"""
    # Typer doesn't automatically handle async functions, so we need to wrap the app call
    app()


if __name__ == "__main__":
    main()
