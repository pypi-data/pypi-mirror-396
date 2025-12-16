import json
import logging
from typing import Any, Dict, Tuple

from browserbase import Browserbase
from browserbase.types import SessionCreateResponse
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from playwright.sync_api import sync_playwright

from ..types import NoRunnersAvailableError

logger = logging.getLogger(__name__)


class BrowserController:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.bb = Browserbase(api_key=self.api_key)

        # Cache connections by connect_url
        self._connections: Dict[str, Tuple[Playwright, Browser, BrowserContext, Page]] = {}

    async def create_session(self) -> SessionCreateResponse:
        """Create a new Browserbase session"""
        try:
            session = self.bb.sessions.create(
                project_id=self.project_id,
                browser_settings={
                    "viewport": {"width": 1280, "height": 800},
                },
            )
            return session
        except Exception as e:
            # Check if error is due to rate limit or concurrency limit
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["rate limit", "concurrency", "quota", "limit exceeded", "too many"]):
                raise NoRunnersAvailableError(f"Browserbase concurrency/rate limit exceeded: {e}") from e
            raise

    async def _get_or_create_connection(self, connect_url: str) -> Tuple[Playwright, Browser, BrowserContext, Page]:
        """
        Get cached connection or create new one.

        Creating new one is very slow(~1 second)
        """
        if connect_url in self._connections:
            return self._connections[connect_url]

        playwright = await async_playwright().start()
        chromium = playwright.chromium
        browser = await chromium.connect_over_cdp(connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        self._connections[connect_url] = (playwright, browser, context, page)
        return self._connections[connect_url]

    async def _connect(self, connect_url: str) -> Tuple[Playwright, Browser, BrowserContext, Page]:
        """Get connection (cached or new)"""
        return await self._get_or_create_connection(connect_url)

    async def terminate_session(self, connect_url: str):
        """Terminate a session"""
        playwright, browser, context, page = await self._connect(connect_url)
        await self._disconnect(playwright, browser, page)
        del self._connections[connect_url]

    def terminate_session_sync(self, connect_url: str):
        """Terminate a session synchronously"""
        if connect_url not in self._connections:
            return

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(connect_url)
            context = browser.contexts[0]
            page = context.pages[0]
            page.close()
            browser.close()

        if connect_url in self._connections:
            del self._connections[connect_url]

    async def _disconnect(self, playwright: Playwright, browser: Browser, page: Page = None):
        """Internal method to cleanup browser resources"""
        if page:
            await page.close()
        if browser:
            await browser.close()
        await playwright.stop()

    async def get(self, connect_url: str, url: str, wait_until_loaded: bool = False):
        """Navigate to URL"""
        playwright, browser, context, page = await self._connect(connect_url)
        await page.goto(url, wait_until="load" if wait_until_loaded else None)

    async def exect_js(self, connect_url: str, js_script: str) -> Any:
        """Execute JavaScript"""
        playwright, browser, context, page = await self._connect(connect_url)
        return await page.evaluate(js_script)

    async def set_state(self, connect_url: str, state: Dict[str, Any]):
        """Sets the state of the dojo and waits until it's correctly set"""
        playwright, browser, context, page = await self._connect(connect_url)
        print(f"Setting state to: {state}")

        js_script = f"""
        () => {{
            return new Promise(async (resolve) => {{
                const targetState = {json.dumps(state)};
                if (typeof window.dojo === 'undefined') {{
                    await new Promise(resolve => setTimeout(resolve, 100));
                }}
                window.dojo.setState(targetState);

                const timeout = 2000; // 2 seconds
                const interval = 100; // Check every 100ms
                const startTime = Date.now();

                const checkState = () => {{
                    try {{
                        const currentState = window.dojo.getState();

                        // Deep comparison of the states
                        if (JSON.stringify(currentState) === JSON.stringify(targetState)) {{
                            resolve({{ success: true, reason: 'State successfully set' }});
                            return;
                        }}

                        if (Date.now() - startTime >= timeout) {{
                            resolve({{
                                success: false,
                                reason: 'Timeout: State not set correctly after 5s',
                                expected: targetState,
                                actual: currentState
                            }});
                            return;
                        }}

                        setTimeout(checkState, interval);
                    }} catch (error) {{
                        if (Date.now() - startTime >= timeout) {{
                            resolve({{
                                success: false,
                                reason: `Timeout: Error checking state after 2s: ${{error.message}}`
                            }});
                            return;
                        }}
                        setTimeout(checkState, interval);
                    }}
                }};

                // Start checking immediately after a small delay to allow React to update
                setTimeout(checkState, 50);
            }});
        }}
        """

        result = await page.evaluate(js_script)
        if not result.get("success", False):
            raise RuntimeError(f"Failed to set state: {result.get('reason', 'Unknown error')}")

    async def get_state(self, connect_url: str) -> Any:
        """Use dojo's getState method to get the actual app state"""
        playwright, browser, context, page = await self._connect(connect_url)

        js_script = r"""
        () => {
            if (window.dojo && typeof window.dojo.getState === 'function') {
                return window.dojo.getState();
            }
            return null;
        }
        """
        return await page.evaluate(js_script)

    async def check_dojo_loaded(self, connect_url: str) -> bool:
        """
        Check if Dojo is correctly loaded by verifying core functionality.
        Waits up to 5 seconds for dojo to load successfully.
        Returns True if Dojo is properly initialized and getState works.
        """
        playwright, browser, context, page = await self._connect(connect_url)
        js_script = r"""
        () => {
            return new Promise((resolve) => {
                const timeout = 3000; // 3 seconds
                const interval = 100; // Check every 100ms
                const startTime = Date.now();

                const checkDojo = () => {
                    try {
                        // Check 1: window.dojo exists
                        if (typeof window.dojo === 'undefined') {
                            if (Date.now() - startTime >= timeout) {
                                resolve({ loaded: false, reason: 'Timeout: window.dojo not found after 5s' });
                                return;
                            }
                            setTimeout(checkDojo, interval);
                            return;
                        }

                        // Check 2: dojo instance has getState method
                        const dojo = window.dojo;
                        if (typeof dojo.getState !== 'function') {
                            if (Date.now() - startTime >= timeout) {
                                resolve({ loaded: false, reason: 'Timeout: dojo.getState method not found after 5s' });
                                return;
                            }
                            setTimeout(checkDojo, interval);
                            return;
                        }

                        // Check 3: dojo.getState() works and returns a value
                        try {
                            const state = dojo.getState();
                            if (state === undefined) {
                                if (Date.now() - startTime >= timeout) {
                                    resolve({ loaded: false, reason: 'Timeout: dojo.getState() returned undefined in 5s' });
                                    return;
                                }
                                setTimeout(checkDojo, interval);
                                return;
                            }
                            // Success! State exists and is accessible
                            resolve({ loaded: true, reason: 'Dojo loaded and getState works' });
                        } catch (error) {
                            if (Date.now() - startTime >= timeout) {
                                resolve({ loaded: false, reason: `Timeout: dojo.getState() failed: ${error.message}` });
                                return;
                            }
                            setTimeout(checkDojo, interval);
                        }

                    } catch (error) {
                        if (Date.now() - startTime >= timeout) {
                            resolve({ loaded: false, reason: `Timeout: Unexpected error after 5s: ${error.message}` });
                            return;
                        }
                        setTimeout(checkDojo, interval);
                    }
                };

                // Start checking immediately
                checkDojo();
            });
        }
        """

        result = await page.evaluate(js_script)
        return result.get("loaded", False)

    async def screenshot(self, connect_url: str) -> bytes:
        """Take a screenshot"""
        playwright, browser, context, page = await self._connect(connect_url)
        try:
            screenshot_bytes = await page.screenshot()
            return screenshot_bytes
        except Exception as e:
            raise RuntimeError(f"Failed to take screenshot: {e}") from e

    async def perform_action(self, connect_url: str, action: dict[str, Any]):
        """Perform an action using the browser controller. Roughly simulates equivalents of pyautogui actions."""
        try:
            action_type = action.get("type")

            _, _, _, page = await self._connect(connect_url)
            if action_type == "click":
                x, y = action.get("x"), action.get("y")
                await page.mouse.click(x, y)

            elif action_type == "right_click":
                x, y = action.get("x"), action.get("y")
                await page.mouse.click(x, y, button="right")

            elif action_type == "double_click":
                x, y = action.get("x"), action.get("y")
                await page.mouse.dblclick(x, y)

            elif action_type == "middle_click":
                x, y = action.get("x"), action.get("y")
                await page.mouse.click(x, y, button="middle")

            elif action_type == "type":
                text = action.get("text", "")
                await page.keyboard.type(text)

            elif action_type == "key":
                key = action.get("key", "")
                await page.keyboard.press(normalize_key(key))

            elif action_type == "press":
                key = action.get("key", "")
                await page.keyboard.press(normalize_key(key))

            elif action_type == "hotkey":
                keys = action.get("keys", [])
                for key in keys[:-1]:
                    await page.keyboard.down(normalize_key(key))
                await page.keyboard.press(normalize_key(keys[-1]))
                for key in reversed(keys[:-1]):
                    await page.keyboard.up(normalize_key(key))

            elif action_type == "scroll":
                direction = action.get("direction", "up")
                amount = action.get("amount", 100)

                delta_y = -amount if direction == "up" else amount
                await page.mouse.wheel(0, delta_y)

            elif action_type == "drag":
                from_x = action.get("from_x")
                from_y = action.get("from_y")
                to_x = action.get("to_x")
                to_y = action.get("to_y")
                duration = action.get("duration", 1.0)

                await page.mouse.move(from_x, from_y)
                await page.mouse.down()
                steps = max(int(duration * 20), 1)
                await page.mouse.move(to_x, to_y, steps=steps)
                await page.mouse.up()

            elif action_type == "move_to":
                x, y = action.get("x"), action.get("y")
                duration = action.get("duration", 0.0)
                steps = max(int(duration * 20), 1) if duration > 0 else 1
                await page.mouse.move(x, y, steps=steps)

            elif action_type == "wait":
                seconds = action.get("seconds", 1)
                logger.warning(f"Waiting for {seconds} seconds")
                # await asyncio.sleep(seconds)

            elif action_type == "done":
                pass

            else:
                logger.warning(f"Unsupported action type: {action_type}")
        except Exception as e:
            logger.warning(f"Error performing action: {e}. Continuing...")
            return


def normalize_key(key: str) -> str:
    """
    Normalize key names to Playwright's expected format.
    Playwright uses DOM KeyboardEvent.key standard.
    """
    KEY_MAP = {
        "up": "ArrowUp",
        "down": "ArrowDown",
        "left": "ArrowLeft",
        "right": "ArrowRight",
        "return": "Enter",
        "esc": "Escape",
        "pageup": "PageUp",
        "pagedown": "PageDown",
        "ctrl": "Control",
        "alt": "Alt",
        "shift": "Shift",
        "meta": "Meta",
        "cmd": "Meta",
        "command": "Meta",
        "option": "Alt",
    }
    return KEY_MAP.get(key.lower(), key)
