"""Test session execution application"""

from __future__ import annotations

import asyncio
import base64
import plistlib
from pathlib import Path
from types import MappingProxyType

import structlog.contextvars

from noqa_runner.application.services.mobile_service import MobileService
from noqa_runner.config import settings
from noqa_runner.domain.exceptions import AgentAPIError, AppiumError, BuildNotFoundError
from noqa_runner.domain.models.actions.stop import Stop
from noqa_runner.domain.models.state.screen import Screen
from noqa_runner.domain.models.state.step import Step
from noqa_runner.domain.models.state.test_state import TestState, TestStatus
from noqa_runner.domain.models.test_info import RunnerTestInfo
from noqa_runner.infrastructure.adapters.http.agent_api import AgentApiAdapter
from noqa_runner.infrastructure.adapters.http.generic import generic_adapter
from noqa_runner.infrastructure.adapters.mobile.appium_adapter import AppiumClient
from noqa_runner.infrastructure.adapters.storage.local_storage_adapter import (
    LocalStorageAdapter,
)
from noqa_runner.logging_config import get_logger
from noqa_runner.utils.graceful_shutdown import register_task

logger = get_logger(__name__)


# Default Appium capabilities (immutable)
DEFAULT_APPIUM_CAPABILITIES = MappingProxyType(
    {
        "platformName": "iOS",
        "appium:automationName": "XCUITest",
        "appium:waitForIdleTimeout": 2,
        "appium:showXcodeLog": True,
    }
)


class RunnerSession:
    """Application for running test sessions"""

    async def execute(
        self,
        noqa_api_token: str,
        tests: list[RunnerTestInfo],
        app_context: str | None = None,
        app_bundle_id: str | None = None,
        app_store_id: str | None = None,
        app_build_path: str | None = None,
        apple_developer_team_id: str | None = None,
        device_id: str | None = None,
        appium_url: str | None = None,
        agent_api_url: str | None = None,
        max_steps: int | None = None,
    ) -> list[TestState]:
        """
        Run multiple tests in a session with mobile service

        Args:
            device_id: Device UDID
            appium_url: Appium server URL
            build_path: Path to IPA build
            noqa_api_token: API token for authentication
            tests: List of test cases to execute
            agent_api_url: Agent API base URL
            app_context: Optional application context

        Returns:
            List of final test states
        """
        if max_steps is None:
            max_steps = settings.MAX_STEPS

        appium_caps = dict(DEFAULT_APPIUM_CAPABILITIES)
        if apple_developer_team_id:
            appium_caps["appium:xcodeOrgId"] = apple_developer_team_id
            appium_caps["appium:xcodeSigningId"] = "iPhone Developer"
        if device_id:
            appium_caps["appium:udid"] = device_id

        # Validate build or TestFlight parameters
        if app_build_path:
            appium_caps["appium:app"] = app_build_path
        elif app_store_id:
            logger.info(
                "Using TestFlight for app installation", app_store_id=app_store_id
            )

        # Extract bundle ID from build if not provided
        if not app_bundle_id:
            if app_build_path:
                try:
                    app_bundle_id = await self._extract_bundle_id_from_build(
                        build_path=app_build_path
                    )
                    logger.info(
                        "Bundle ID extracted from build", bundle_id=app_bundle_id
                    )
                except Exception as e:
                    logger.error(
                        "Failed to extract bundle ID from build",
                        build_path=app_build_path,
                        error=str(e),
                        exc_info=True,
                    )
                    raise
            else:
                raise ValueError(
                    "app_bundle_id must be provided when using TestFlight (app_store_id)"
                )

        agent_api_url = agent_api_url or settings.AGENT_API_URL
        appium_url = appium_url or settings.DEFAULT_APPIUM_URL

        logger.info("Starting test session", test_count=len(tests), device_id=device_id)

        results = []

        # Execute tests sequentially, creating new Appium client for each test
        for test_info in tests:
            # Create test state
            state = TestState(
                test_id=test_info.test_id,
                bundle_id=app_bundle_id,
                case_name=test_info.case_name,
                case_instructions=test_info.case_instructions,
                app_context=app_context,
            )

            # Setup logging context for this test
            structlog.contextvars.bind_contextvars(test_id=str(state.test_id))

            # Use Appium client as async context manager for each test
            try:
                async with AppiumClient(
                    appium_url=appium_url, appium_capabilities=appium_caps
                ) as appium_client:
                    # Create mobile service for this test
                    mobile_service = MobileService(
                        appium_client=appium_client, bundle_id=app_bundle_id
                    )

                    # Run test as a task and register it for cancellation
                    task = asyncio.create_task(
                        self._run_single_test(
                            mobile_service=mobile_service,
                            state=state,
                            noqa_api_token=noqa_api_token,
                            agent_api_url=agent_api_url,
                            max_steps=max_steps,
                            app_store_id=app_store_id,
                        )
                    )
                    register_task(task)
                    await task
                    results.append(state)
            except asyncio.CancelledError:
                # Shutdown signal - stop session
                self._finalize_test_state(
                    state=state,
                    status=TestStatus.STOPPED,
                    message="Test stopped by shutdown signal",
                )
                results.append(state)
                break
            except (AppiumError, AgentAPIError, Exception) as e:
                error_msg = self._format_error_message(e)
                logger.error(
                    "Test execution failed, continuing with next test",
                    error=error_msg,
                    error_type=type(e).__name__,
                    exc_info=True,
                )
                self._finalize_test_state(
                    state=state,
                    status=TestStatus.ERROR,
                    message=f"Test execution failed: {error_msg}",
                )
                results.append(state)

            structlog.contextvars.unbind_contextvars("step_number", "test_id")

        return results

    async def _run_single_test(
        self,
        mobile_service: MobileService,
        state: TestState,
        noqa_api_token: str,
        agent_api_url: str,
        max_steps: int,
        app_store_id: str | None = None,
    ) -> None:
        """Execute single test and mutate state in place"""
        # Clean up alerts before starting
        try:
            await mobile_service.client.dismiss_system_alert()
        except Exception:
            pass

        # Install app via TestFlight if using app_store_id
        if app_store_id:
            if "-appstore" in app_store_id:
                logger.info(
                    "Installing app from App Store",
                    app_store_id=app_store_id,
                    bundle_id=state.bundle_id,
                )
                result = await mobile_service.client.install_app_appstore(
                    app_bundle_id=state.bundle_id,
                    app_store_id=app_store_id.split("-appstore")[0],
                )
            else:
                logger.info(
                    "Installing app via TestFlight",
                    app_store_id=app_store_id,
                    bundle_id=state.bundle_id,
                )
                result = await mobile_service.client.install_app_testflight(
                    app_bundle_id=state.bundle_id, app_store_id=app_store_id
                )

            if not result:
                raise AppiumError(
                    f"App installation timeout for bundle_id={state.bundle_id}",
                    TimeoutError.__name__,
                )

        # Use agent API adapter as async context manager
        async with AgentApiAdapter(
            base_url=agent_api_url, api_token=noqa_api_token
        ) as agent_api:
            # Prepare test with agent API (create conditions, fetch app metadata)
            prepared_state = await agent_api.prepare_test(state)
            state.conditions = prepared_state.conditions
            state.resolution = mobile_service.resolution

            # Log received conditions
            conditions = ", ".join([f"{x.condition}" for x in state.conditions])
            logger.info(
                f"Check list: {conditions}",
                conditions=[x.model_dump() for x in state.conditions],
            )

            # Main test execution loop
            step_count = 0
            while True:
                step_count += 1
                step_number = max(state.steps.keys(), default=0) + 1
                # Bind step_number to logging context
                structlog.contextvars.bind_contextvars(step_number=step_number)
                logger.info(f"Step {step_number}")

                # MAX STEPS HANDLING
                if step_count > max_steps:
                    self._finalize_test_state(
                        state=state,
                        status=TestStatus.ERROR,
                        message="Maximum number of steps reached",
                    )
                    break

                # Capture screen from device
                xml_source, screenshot_base64 = (
                    await mobile_service.get_appium_screen_data()
                )

                # App crash handling
                action_types = [
                    type(step.action_data.action).__name__
                    for step in state.steps.values()
                ]
                if (
                    "TerminateApp" not in action_types
                    and "BackgroundApp" not in action_types
                ):
                    is_home_screen = (
                        'name="Dock"' in xml_source
                        and "XCUIElementTypeIcon" in xml_source
                    )
                    if is_home_screen:
                        self._finalize_test_state(
                            state=state,
                            status=TestStatus.ERROR,
                            message="The application crashed",
                        )
                        break

                # Upload screenshot and get URLs
                screenshot_url = await self._upload_screenshot(
                    agent_api=agent_api,
                    screenshot_base64=screenshot_base64,
                    test_id=str(state.test_id),
                    step_number=step_number,
                )

                # Create step with screen data
                state.steps[step_number] = Step(
                    number=step_number,
                    screen=Screen(
                        elements_tree=xml_source, screenshot_url=screenshot_url
                    ),
                )
                logger.info("Captured screen")

                # Send to agent API for decision
                step_state = await agent_api.execute_step(state)
                state.steps = step_state.steps
                state.status = step_state.status
                state.result_summary = step_state.result_summary
                state.conditions = step_state.conditions

                logger.info(
                    state.current_step.action_data.action.get_action_description()
                )

                # Check if test is complete
                if isinstance(state.current_step.action_data.action, Stop):
                    self._finalize_test_state(
                        state=state, status=state.status, message=state.result_summary
                    )
                    break
                else:
                    # Execute action on device
                    await mobile_service.execute_action(
                        action=state.current_step.action_data.action,
                        screen=state.current_step.screen,
                    )

                structlog.contextvars.unbind_contextvars("step_number")

            self._finalize_test_state(
                state=state, status=state.status, message=state.result_summary
            )

    async def _extract_bundle_id_from_build(self, build_path: str) -> str:
        """
        Extract bundle_id from iOS build archive

        Args:
            build_path: Path to the local IPA build file

        Returns:
            Bundle ID (e.g., "com.example.app")

        Raises:
            BuildNotFoundError: If build file not found
            ValueError: If bundle ID cannot be extracted
        """
        # Check if build file exists
        if not Path(build_path).exists():
            raise BuildNotFoundError(build_path)

        # Extract Info.plist from the IPA archive using LocalStorageAdapter
        # Create adapter with the build file's directory as base_dir to allow access
        build_dir = str(Path(build_path).parent)
        file_storage = LocalStorageAdapter(output_dir=build_dir)
        plist_content = await file_storage.extract_file_from_zip(
            zip_path=build_path, filename=".app/Info.plist"
        )

        if not plist_content:
            raise ValueError(f"Info.plist not found in build {build_path}")

        # Parse plist to get bundle_id
        plist_data = plistlib.loads(plist_content)
        bundle_id = plist_data.get("CFBundleIdentifier")

        if not bundle_id:
            raise ValueError(
                f"CFBundleIdentifier not found in Info.plist for build {build_path}"
            )

        return bundle_id

    def _format_error_message(self, error: Exception) -> str:
        """Format error message with URL info for httpx errors"""
        error_type = type(error).__name__
        error_str = str(error)

        # Try to extract URL from httpx request attribute
        request = getattr(error, "request", None)
        if request is not None:
            url = getattr(request, "url", None)
            if url is not None:
                host = getattr(url, "host", str(url))
                if error_str:
                    return f"{error_str} ({host})"
                return f"{error_type} connecting to {host}"

        return error_str or error_type

    def _finalize_test_state(
        self, state: TestState, status: TestStatus, message: str
    ) -> None:
        """Update test state with final status and message"""
        structlog.contextvars.unbind_contextvars("step_number")
        state.status = status
        state.result_summary = message
        logger.info("test_result", status=status, test_state=state.export_dict())
        structlog.contextvars.unbind_contextvars("test_id")

    async def _upload_screenshot(
        self,
        agent_api: AgentApiAdapter,
        screenshot_base64: str,
        test_id: str,
        step_number: int,
    ) -> str:
        """Upload screenshot to storage and return download URL"""
        upload_url, download_url = await agent_api.get_screenshot_urls(
            test_id=test_id, step_number=step_number
        )

        # Upload screenshot using generic HTTP adapter singleton
        image_data = base64.b64decode(screenshot_base64)
        await generic_adapter.upload_bytes(
            url=upload_url, data=image_data, content_type="image/png"
        )

        # Return public URL
        return download_url

    def run(
        self,
        noqa_api_token: str,
        tests: list[RunnerTestInfo],
        app_context: str | None = None,
        app_bundle_id: str | None = None,
        app_store_id: str | None = None,
        app_build_path: str | None = None,
        apple_developer_team_id: str | None = None,
        device_id: str | None = None,
        appium_url: str | None = None,
        agent_api_url: str | None = None,
        max_steps: int | None = None,
    ) -> list[TestState]:
        """
        Synchronous method to run test session.

        Runs the async execute() method in a new event loop.
        This is the main API for synchronous code.

        Args:
            device_id: Device UDID
            appium_url: Appium server URL
            build_path: Path to IPA build
            noqa_api_token: API token for authentication
            tests: List of test cases to execute
            agent_api_url: Agent API base URL
            app_context: Optional application context

        Returns:
            List of final test states
        """
        return asyncio.run(
            self.execute(
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
        )
