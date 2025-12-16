from __future__ import annotations

import asyncio
import functools
import json

from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from noqa_runner.domain.exceptions import AppiumError
from noqa_runner.logging_config import get_logger
from noqa_runner.utils.retry_decorator import with_retry

logger = get_logger(__name__)


def get_appstore_url(app_store_id: str, country_code: str = "us") -> str:
    return f"https://apps.apple.com/{country_code}/app/{app_store_id}"


def handle_appium_errors(func):
    """Decorator to catch Appium errors and convert them to AppiumError"""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except WebDriverException as e:
            logger.error(
                "appium_command_error",
                command=func.__name__,
                error=str(e),
                exc_info=True,
            )
            raise AppiumError(
                appium_url=self.appium_url, original_error=f"{func.__name__}: {str(e)}"
            )

    return wrapper


class AppiumClient:
    """Appium client adapter for mobile automation (async context manager)"""

    driver: webdriver.Remote
    resolution: dict
    _loop: asyncio.AbstractEventLoop | None
    _capabilities: dict | None
    _platform_name: str | None

    @with_retry(
        max_attempts=3, min_wait=1, max_wait=3, exceptions=(WebDriverException,)
    )
    def __init__(self, appium_url: str, appium_capabilities=None):
        self.appium_url = appium_url
        self.appium_capabilities = appium_capabilities
        self._loop = None
        self._capabilities = None
        self._platform_name = None

        logger.info("Initializing Appium session", capabilities=appium_capabilities)

        # Initialize driver immediately with retry
        try:
            self.driver = webdriver.Remote(
                self.appium_url,
                options=AppiumOptions().load_capabilities(
                    self.appium_capabilities or {}
                ),
            )
            self.driver.implicitly_wait(5)
            self.resolution = self.driver.get_window_size()
        except Exception as e:
            # Any other error during driver initialization
            raise AppiumError(appium_url=self.appium_url, original_error=str(e))

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup driver"""
        await self.close()
        return False

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    @property
    def capabilities(self) -> dict:
        """Get driver capabilities"""
        if self._capabilities is None:
            self._capabilities = self.driver.capabilities
        return self._capabilities

    @property
    def platform_name(self) -> str:
        """Get platform name (iOS or Android)"""
        if self._platform_name is None:
            self._platform_name = self.capabilities.get("platformName", "iOS").lower()
        return self._platform_name

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def get_page_source(self) -> str:
        """Get page source XML from driver"""
        # Run in executor to avoid blocking the event loop
        return await self.loop.run_in_executor(None, lambda: self.driver.page_source)

    @handle_appium_errors
    async def get_element(self, ios_locator: str, by: str = AppiumBy.IOS_PREDICATE):
        """Get single element by iOS Predicate locator"""
        try:
            element = await self.loop.run_in_executor(
                None, lambda: self.driver.find_element(by, ios_locator)
            )
            return element
        except Exception:
            logger.debug(f"Element with iOS predicate '{ios_locator}' not found")
            return None

    @handle_appium_errors
    async def get_elements(self, locator: str, by: str = AppiumBy.IOS_PREDICATE):
        """Get multiple elements by locator"""
        try:
            elements = await self.loop.run_in_executor(
                None, lambda: self.driver.find_elements(by, locator)
            )
            return elements
        except Exception:
            logger.debug(f"Elements with locator '{locator}' not found")
            return None

    @handle_appium_errors
    async def tap_by_coords(self, x: int, y: int) -> None:
        """Tap at specific coordinates"""
        await self.loop.run_in_executor(None, lambda: self.driver.tap([(x, y)]))

    @handle_appium_errors
    @with_retry(
        max_attempts=3,
        min_wait=1,
        max_wait=2,
        exceptions=(StaleElementReferenceException,),
    )
    async def tap(self, ios_locator: str) -> bool:
        """Tap element by iOS Predicate String locator"""
        try:
            element = await self.loop.run_in_executor(
                None,
                lambda: self.driver.find_element(AppiumBy.IOS_PREDICATE, ios_locator),
            )
        except Exception:
            logger.debug(f"Element with iOS predicate '{ios_locator}' not found")
            return False

        await self.loop.run_in_executor(None, lambda: element.click())
        return True

    @handle_appium_errors
    async def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 1000,
    ) -> None:
        """Swipe from start coordinates to end coordinates

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration_ms: Swipe duration in milliseconds (default 1000)
        """
        await self.loop.run_in_executor(
            None, lambda: self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        )

    @handle_appium_errors
    async def open_url(self, url: str) -> None:
        """Navigate to URL"""
        await self.loop.run_in_executor(None, lambda: self.driver.get(url))

    async def accept_system_alert(self) -> None:
        """Accept system alert"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.switch_to.alert.accept()
        )

    async def dismiss_system_alert(self) -> None:
        """Dismiss system alert"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.switch_to.alert.dismiss()
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def get_screenshot(self) -> str:
        """Get current screenshot as base64"""
        return await self.loop.run_in_executor(
            None, lambda: self.driver.get_screenshot_as_base64()
        )

    @handle_appium_errors
    async def hide_keyboard(self) -> None:
        """Hide keyboard using platform-specific approach"""
        # iOS: Look for Done button in toolbar
        element = await self.get_element(
            "type CONTAINS 'TextField' or type CONTAINS 'TextView'"
        )
        if element:
            rect = json.loads(element.get_attribute("rect"))
            await self.tap_by_coords(rect.get("x"), rect.get("y"))

    @handle_appium_errors
    @with_retry(
        max_attempts=3,
        min_wait=1,
        max_wait=2,
        exceptions=(StaleElementReferenceException,),
    )
    async def input_text_in_element(self, ios_locator: str, text: str) -> bool:
        """Input text into element using iOS Predicate locator. Clears the field before input."""
        try:
            element = await self.loop.run_in_executor(
                None,
                lambda: self.driver.find_element(AppiumBy.IOS_PREDICATE, ios_locator),
            )
        except Exception:
            logger.debug(f"Element with iOS predicate '{ios_locator}' not found")
            return False

        def _clear_and_input_text():
            element.clear()
            element.send_keys(text)
            return True

        result = await self.loop.run_in_executor(None, _clear_and_input_text)
        # Sleep asynchronously after the synchronous operation
        return result

    @handle_appium_errors
    async def get_alert_text(self) -> str | None:
        """Get alert text"""

        def _get_alert_text():
            try:
                return self.driver.switch_to.alert.text
            except Exception:
                return None

        return await self.loop.run_in_executor(None, _get_alert_text)

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def activate_app(self, bundle_id: str) -> None:
        """Activate app by bundle ID"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.activate_app(bundle_id)
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def terminate_app(self, bundle_id: str) -> None:
        """Terminate app by bundle ID"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.terminate_app(bundle_id)
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def background_app(self) -> None:
        """Background app"""
        await self.loop.run_in_executor(None, lambda: self.driver.background_app(-1))

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def remove_app(self, bundle_id: str) -> None:
        """Remove app by bundle ID"""
        await self.loop.run_in_executor(None, lambda: self.driver.remove_app(bundle_id))

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def query_app_state(self, bundle_id: str) -> int:
        """Query app state by bundle ID. Returns state code (4 = running)"""
        return await self.loop.run_in_executor(
            None, lambda: self.driver.query_app_state(bundle_id)
        )

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def get_active_app_info(self) -> dict | None:
        """Get information about the currently active app. Returns dict with bundleId key or None on error."""

        def _get_active_app_info():
            return self.driver.execute_script("mobile: activeAppInfo")

        return await self.loop.run_in_executor(None, _get_active_app_info)

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def install_app_testflight(
        self, app_bundle_id: str, app_store_id: str | None = None
    ) -> bool:
        """
        Install app via TestFlight by simulating user interaction.
        """
        # Remove existing app
        await self.remove_app(app_bundle_id)
        await self.terminate_app("com.apple.TestFlight")
        logger.info("Existing app removed", bundle_id=app_bundle_id)

        # Activate TestFlight app
        await self.activate_app("com.apple.TestFlight")
        logger.info("TestFlight activated")

        initial_button_name = None

        # Wait for app to be installed
        max_wait_time = 40
        wait_start = 0
        while wait_start < max_wait_time:
            await asyncio.sleep(1)
            wait_start += 1

            try:
                xml_str = await self.get_page_source()

                # Handle alerts (e.g., "Do you want to install this app?")
                if "XCUIElementTypeAlert" in xml_str:
                    alert_buttons = await self.get_elements(
                        "//XCUIElementTypeAlert//XCUIElementTypeButton"
                    )
                    if alert_buttons:
                        alert_buttons[-1].click()
                        continue

                main_buttons = await self.get_elements(
                    f"//XCUIElementTypeOther[@name='{app_store_id}']//XCUIElementTypeButton",
                    by=AppiumBy.XPATH,
                )
                if main_buttons:
                    main_button = main_buttons[-1]
                    if (
                        main_button.get_attribute("name")
                        and len(main_button.get_attribute("name")) > 2
                    ):
                        if not initial_button_name:
                            initial_button_name = main_button.get_attribute("name")
                        else:
                            await self.terminate_app("com.apple.TestFlight")
                            await asyncio.sleep(1)
                            await self.activate_app(app_bundle_id)
                            return True
                        main_button.click()
                        continue

            except Exception:
                pass

        logger.error(
            "TestFlight installation timeout",
            bundle_id=app_bundle_id,
            timeout_seconds=max_wait_time,
        )
        return False

    @handle_appium_errors
    @with_retry(max_attempts=3)
    async def install_app_appstore(
        self, app_bundle_id: str, app_store_id: str | None = None
    ) -> bool | None:
        # Remove existing app
        await self.remove_app(app_bundle_id)
        await self.terminate_app("com.apple.AppStore")
        logger.info("Existing app removed", bundle_id=app_bundle_id)

        max_wait_time = 40
        wait_start = 0
        while wait_start < max_wait_time:
            await asyncio.sleep(1)
            wait_start += 1

            try:
                app_state = await self.query_app_state(app_bundle_id)
                if app_state == 4:
                    logger.info(
                        "App installed and running",
                        bundle_id=app_bundle_id,
                        app_state=app_state,
                    )
                    return True

                appstore_state = await self.query_app_state("com.apple.AppStore")
                if appstore_state != 4:
                    self.driver.get(get_appstore_url(app_store_id=app_store_id))
                    continue

                # Get current page source
                xml_str = await self.get_page_source()

                if "payment-sheet" in xml_str:
                    buttons = await self.get_elements(
                        "//XCUIElementTypeOther[@name='payment-sheet']//XCUIElementTypeButton",
                        by=AppiumBy.XPATH,
                    )
                    if buttons:
                        buttons[-1].click()
                        continue

                if "AppStore.offerButton" in xml_str:
                    if (
                        "AppStore.offerButton[state=downloading]" in xml_str
                        or "AppStore.offerButton[state=loading]" in xml_str
                    ):
                        logger.info("App is downloading, waiting...")
                        continue
                    elif "AppStore.offerButton[state=open]" in xml_str:
                        open_button = await self.get_element(
                            "//XCUIElementTypeCell[contains(@name, 'AppStore.shelfItem.productTopLockup')]//XCUIElementTypeButton[@name='AppStore.offerButton[state=open]']",
                            by=AppiumBy.XPATH,
                        )
                        if open_button:
                            await self.terminate_app("com.apple.AppStore")
                            await asyncio.sleep(1)
                            await self.activate_app(app_bundle_id)
                            continue
                    elif "AppStore.offerButton[state=redownload]" in xml_str:
                        main_button = await self.get_element(
                            "//XCUIElementTypeCell[contains(@name, 'AppStore.shelfItem.productTopLockup')]//XCUIElementTypeButton[@name='AppStore.offerButton[state=redownload]']",
                            by=AppiumBy.XPATH,
                        )
                        if main_button:
                            main_button.click()
                            continue
                    elif "AppStore.offerButton[state=get]" in xml_str:
                        main_button = await self.get_element(
                            "//XCUIElementTypeCell[contains(@name, 'AppStore.shelfItem.productTopLockup')]//XCUIElementTypeButton[@name='AppStore.offerButton[state=get]']",
                            by=AppiumBy.XPATH,
                        )
                        if main_button:
                            main_button.click()
                            continue
            except Exception as e:
                logger.info("Transient error during installation check", error=str(e))

        logger.error(
            "App Store installation timeout",
            bundle_id=app_bundle_id,
            timeout_seconds=max_wait_time,
        )
        return None

    async def close(self) -> None:
        """Close the Appium driver connection"""
        if self.driver and hasattr(self.driver, "quit"):
            try:
                await self.loop.run_in_executor(None, lambda: self.driver.quit())
            finally:
                self.driver = None
