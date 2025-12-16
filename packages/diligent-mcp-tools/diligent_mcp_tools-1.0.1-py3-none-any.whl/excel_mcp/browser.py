"""
Browser automation tools using Playwright.

Portions of this code use Playwright, which is licensed under the Apache 2.0 License.
Copyright (c) Microsoft Corporation.

See the NOTICE file in the project root for license information.
"""

import logging
import asyncio
import base64
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger("excel-mcp.browser")

# Global browser instance management
_browser_instance: Optional[Browser] = None
_context_instance: Optional[BrowserContext] = None
_page_instance: Optional[Page] = None
_playwright_instance = None


async def get_browser_instance(browser_type: str = "chromium", headless: bool = False) -> Browser:
    """
    Get or create a browser instance.
    
    Args:
        browser_type: Browser type ("chromium", "firefox", or "webkit")
        headless: Whether to run in headless mode (default: False = visible browser)
        
    Returns:
        Browser instance
    """
    global _browser_instance, _playwright_instance
    
    if _browser_instance is None or not _browser_instance.is_connected():
        if _playwright_instance is None:
            _playwright_instance = await async_playwright().start()
        
        if browser_type == "chromium":
            _browser_instance = await _playwright_instance.chromium.launch(headless=headless, slow_mo=100)
        elif browser_type == "firefox":
            _browser_instance = await _playwright_instance.firefox.launch(headless=headless, slow_mo=100)
        elif browser_type == "webkit":
            _browser_instance = await _playwright_instance.webkit.launch(headless=headless, slow_mo=100)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        logger.info(f"Launched {browser_type} browser (headless={headless}, slow_mo=100ms)")
    
    return _browser_instance


async def get_context_instance(browser: Optional[Browser] = None, **options) -> BrowserContext:
    """
    Get or create a browser context.
    
    Args:
        browser: Browser instance (will create one if not provided)
        **options: Context options (viewport, user_agent, etc.)
        
    Returns:
        BrowserContext instance
    """
    global _context_instance
    
    if _context_instance is None or _context_instance.browser is None:
        if browser is None:
            browser = await get_browser_instance()
        _context_instance = await browser.new_context(**options)
        logger.info("Created new browser context")
    
    return _context_instance


async def get_page_instance(context: Optional[BrowserContext] = None) -> Page:
    """
    Get or create a page instance.
    
    Args:
        context: Browser context (will create one if not provided)
        
    Returns:
        Page instance
    """
    global _page_instance
    
    if _page_instance is None or _page_instance.is_closed():
        if context is None:
            context = await get_context_instance()
        _page_instance = await context.new_page()
        logger.info("Created new page")
    
    return _page_instance


async def cleanup_browser():
    """Clean up browser resources."""
    global _browser_instance, _context_instance, _page_instance, _playwright_instance
    
    if _page_instance and not _page_instance.is_closed():
        await _page_instance.close()
        _page_instance = None
    
    if _context_instance:
        await _context_instance.close()
        _context_instance = None
    
    if _browser_instance and _browser_instance.is_connected():
        await _browser_instance.close()
        _browser_instance = None
    
    if _playwright_instance:
        await _playwright_instance.stop()
        _playwright_instance = None
    
    logger.info("Browser cleanup completed")


async def navigate_to_url_impl(
    url: str,
    wait_until: str = "load",
    timeout: int = 30000
) -> Dict[str, Any]:
    """
    Navigate to a URL.
    
    Args:
        url: URL to navigate to
        wait_until: When to consider navigation successful ("load", "domcontentloaded", "networkidle")
        timeout: Navigation timeout in milliseconds
        
    Returns:
        Dict with status and page title
    """
    try:
        page = await get_page_instance()
        response = await page.goto(url, wait_until=wait_until, timeout=timeout)
        
        title = await page.title()
        
        return {
            "status": "success",
            "url": page.url,
            "title": title,
            "status_code": response.status if response else None
        }
    except Exception as e:
        logger.error(f"Error navigating to URL: {e}")
        raise


async def take_screenshot_impl(
    filepath: str,
    full_page: bool = False,
    selector: Optional[str] = None
) -> Dict[str, str]:
    """
    Take a screenshot of the current page or element.
    
    Args:
        filepath: Path where to save the screenshot
        full_page: Whether to capture the full page
        selector: CSS selector for specific element screenshot
        
    Returns:
        Dict with success message and file path
    """
    try:
        page = await get_page_instance()
        
        if selector:
            element = await page.query_selector(selector)
            if not element:
                raise ValueError(f"Element not found: {selector}")
            await element.screenshot(path=filepath)
        else:
            await page.screenshot(path=filepath, full_page=full_page)
        
        return {
            "message": f"Screenshot saved to {filepath}",
            "filepath": filepath
        }
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise


async def click_element_impl(
    selector: str,
    button: str = "left",
    click_count: int = 1,
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Click an element on the page.
    
    Args:
        selector: CSS selector for the element
        button: Mouse button ("left", "right", "middle")
        click_count: Number of clicks (1 for single, 2 for double)
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        await page.click(selector, button=button, click_count=click_count, timeout=timeout)
        
        return {
            "message": f"Clicked element: {selector}"
        }
    except Exception as e:
        logger.error(f"Error clicking element: {e}")
        raise


async def fill_input_impl(
    selector: str,
    value: str,
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Fill an input field with text.
    
    Args:
        selector: CSS selector for the input element
        value: Text to fill
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        await page.fill(selector, value, timeout=timeout)
        
        return {
            "message": f"Filled input '{selector}' with value"
        }
    except Exception as e:
        logger.error(f"Error filling input: {e}")
        raise


async def get_text_content_impl(
    selector: str,
    timeout: int = 30000
) -> Dict[str, Optional[str]]:
    """
    Get text content of an element.
    
    Args:
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with text content
    """
    try:
        page = await get_page_instance()
        element = await page.wait_for_selector(selector, timeout=timeout)
        text = await element.text_content()
        
        return {
            "selector": selector,
            "text": text
        }
    except Exception as e:
        logger.error(f"Error getting text content: {e}")
        raise


async def wait_for_selector_impl(
    selector: str,
    state: str = "visible",
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Wait for an element to be in a specific state.
    
    Args:
        selector: CSS selector for the element
        state: State to wait for ("attached", "detached", "visible", "hidden")
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        
        return {
            "message": f"Element {selector} is now {state}"
        }
    except Exception as e:
        logger.error(f"Error waiting for selector: {e}")
        raise


async def evaluate_javascript_impl(
    script: str
) -> Dict[str, Any]:
    """
    Execute JavaScript in the page context.
    
    Args:
        script: JavaScript code to execute
        
    Returns:
        Dict with execution result
    """
    try:
        page = await get_page_instance()
        result = await page.evaluate(script)
        
        return {
            "result": result
        }
    except Exception as e:
        logger.error(f"Error evaluating JavaScript: {e}")
        raise


async def get_page_content_impl() -> Dict[str, str]:
    """
    Get the full HTML content of the current page.
    
    Returns:
        Dict with HTML content
    """
    try:
        page = await get_page_instance()
        content = await page.content()
        title = await page.title()
        
        return {
            "url": page.url,
            "title": title,
            "html": content
        }
    except Exception as e:
        logger.error(f"Error getting page content: {e}")
        raise


async def wait_for_navigation_impl(
    timeout: int = 30000,
    wait_until: str = "load"
) -> Dict[str, str]:
    """
    Wait for navigation to complete.
    
    Args:
        timeout: Timeout in milliseconds
        wait_until: When to consider navigation successful
        
    Returns:
        Dict with navigation result
    """
    try:
        page = await get_page_instance()
        await page.wait_for_load_state(wait_until, timeout=timeout)
        
        return {
            "message": "Navigation completed",
            "url": page.url
        }
    except Exception as e:
        logger.error(f"Error waiting for navigation: {e}")
        raise


async def select_option_impl(
    selector: str,
    value: Optional[str] = None,
    label: Optional[str] = None,
    index: Optional[int] = None,
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Select an option in a dropdown.
    
    Args:
        selector: CSS selector for the select element
        value: Option value to select
        label: Option label to select
        index: Option index to select
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        
        if value is not None:
            await page.select_option(selector, value=value, timeout=timeout)
        elif label is not None:
            await page.select_option(selector, label=label, timeout=timeout)
        elif index is not None:
            await page.select_option(selector, index=index, timeout=timeout)
        else:
            raise ValueError("Must provide value, label, or index")
        
        return {
            "message": f"Selected option in {selector}"
        }
    except Exception as e:
        logger.error(f"Error selecting option: {e}")
        raise


async def check_checkbox_impl(
    selector: str,
    checked: bool = True,
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Check or uncheck a checkbox.
    
    Args:
        selector: CSS selector for the checkbox
        checked: Whether to check (True) or uncheck (False)
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        
        if checked:
            await page.check(selector, timeout=timeout)
        else:
            await page.uncheck(selector, timeout=timeout)
        
        return {
            "message": f"{'Checked' if checked else 'Unchecked'} element: {selector}"
        }
    except Exception as e:
        logger.error(f"Error checking checkbox: {e}")
        raise


async def hover_element_impl(
    selector: str,
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Hover over an element.
    
    Args:
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        await page.hover(selector, timeout=timeout)
        
        return {
            "message": f"Hovered over element: {selector}"
        }
    except Exception as e:
        logger.error(f"Error hovering element: {e}")
        raise


async def press_key_impl(
    key: str,
    selector: Optional[str] = None,
    timeout: int = 30000
) -> Dict[str, str]:
    """
    Press a key on the keyboard.
    
    Args:
        key: Key to press (e.g., "Enter", "Escape", "a", "Control+A")
        selector: Optional CSS selector to focus before pressing key
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        
        if selector:
            await page.press(selector, key, timeout=timeout)
        else:
            await page.keyboard.press(key)
        
        return {
            "message": f"Pressed key: {key}"
        }
    except Exception as e:
        logger.error(f"Error pressing key: {e}")
        raise


async def get_element_attribute_impl(
    selector: str,
    attribute: str,
    timeout: int = 30000
) -> Dict[str, Optional[str]]:
    """
    Get an attribute value from an element.
    
    Args:
        selector: CSS selector for the element
        attribute: Attribute name
        timeout: Timeout in milliseconds
        
    Returns:
        Dict with attribute value
    """
    try:
        page = await get_page_instance()
        element = await page.wait_for_selector(selector, timeout=timeout)
        value = await element.get_attribute(attribute)
        
        return {
            "selector": selector,
            "attribute": attribute,
            "value": value
        }
    except Exception as e:
        logger.error(f"Error getting element attribute: {e}")
        raise


async def scroll_page_impl(
    direction: str = "down",
    amount: Optional[int] = None
) -> Dict[str, str]:
    """
    Scroll the page.
    
    Args:
        direction: Scroll direction ("up", "down", "left", "right")
        amount: Amount to scroll in pixels (defaults to viewport height)
        
    Returns:
        Dict with success message
    """
    try:
        page = await get_page_instance()
        
        if amount is None:
            viewport = page.viewport_size
            amount = viewport["height"] if direction in ["up", "down"] else viewport["width"]
        
        scroll_map = {
            "down": f"window.scrollBy(0, {amount})",
            "up": f"window.scrollBy(0, -{amount})",
            "right": f"window.scrollBy({amount}, 0)",
            "left": f"window.scrollBy(-{amount}, 0)"
        }
        
        if direction not in scroll_map:
            raise ValueError(f"Invalid direction: {direction}")
        
        await page.evaluate(scroll_map[direction])
        
        return {
            "message": f"Scrolled {direction} by {amount}px"
        }
    except Exception as e:
        logger.error(f"Error scrolling page: {e}")
        raise


async def get_cookies_impl() -> Dict[str, List[Dict]]:
    """
    Get all cookies from the current context.
    
    Returns:
        Dict with list of cookies
    """
    try:
        context = await get_context_instance()
        cookies = await context.cookies()
        
        return {
            "cookies": cookies
        }
    except Exception as e:
        logger.error(f"Error getting cookies: {e}")
        raise


async def set_cookie_impl(
    name: str,
    value: str,
    url: Optional[str] = None,
    domain: Optional[str] = None,
    path: str = "/",
    expires: Optional[float] = None,
    http_only: bool = False,
    secure: bool = False,
    same_site: str = "Lax"
) -> Dict[str, str]:
    """
    Set a cookie in the browser context.
    
    Args:
        name: Cookie name
        value: Cookie value
        url: Optional URL (requires protocol and domain)
        domain: Optional domain
        path: Cookie path
        expires: Optional expiration timestamp
        http_only: HttpOnly flag
        secure: Secure flag
        same_site: SameSite attribute
        
    Returns:
        Dict with success message
    """
    try:
        context = await get_context_instance()
        
        cookie = {
            "name": name,
            "value": value,
            "path": path,
            "httpOnly": http_only,
            "secure": secure,
            "sameSite": same_site
        }
        
        if url:
            cookie["url"] = url
        if domain:
            cookie["domain"] = domain
        if expires:
            cookie["expires"] = expires
        
        await context.add_cookies([cookie])
        
        return {
            "message": f"Cookie '{name}' set successfully"
        }
    except Exception as e:
        logger.error(f"Error setting cookie: {e}")
        raise


async def clear_cookies_impl() -> Dict[str, str]:
    """
    Clear all cookies from the browser context.
    
    Returns:
        Dict with success message
    """
    try:
        context = await get_context_instance()
        await context.clear_cookies()
        
        return {
            "message": "All cookies cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing cookies: {e}")
        raise

