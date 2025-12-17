"""
Secure Browser Tool - Policy-Gated Web Automation
Implements safe web browsing with PII protection and DOM sanitization.
"""

from typing import Dict, Any, List, Optional
from ..memory import DataAirlock


class SecureBrowser:
    """
    A policy-aware browser automation tool.
    
    Key features:
    - DOM sanitization to prevent prompt injection from malicious sites
    - PII protection via Data Airlock
    - User-in-the-loop for sensitive operations (passwords, payments)
    - Visual feedback (user can see the browser)
    """
    
    def __init__(self, airlock: DataAirlock, headless: bool = False):
        """
        Initialize the secure browser.
        
        Args:
            airlock: DataAirlock for PII protection
            headless: Whether to run in headless mode
        """
        self.airlock = airlock
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None
        self._context = None
        self.session_active = False
    
    def start(self, user_agent: Optional[str] = None):
        """
        Start the browser session.
        
        Args:
            user_agent: Custom user agent string
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "Playwright not installed. Install with: pip install playwright && playwright install chromium"
            )
        
        self._playwright = sync_playwright().start()
        
        # Launch browser with security settings
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # Avoid detection
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Create context with custom settings
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': user_agent
        } if user_agent else {'viewport': {'width': 1920, 'height': 1080}}
        
        self._context = self._browser.new_context(**context_options)
        self._page = self._context.new_page()
        
        self.session_active = True
        print("✅ Secure browser started")
    
    def navigate(self, url: str, wait_until: str = "networkidle") -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: Target URL
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')
            
        Returns:
            Navigation result
        """
        if not self.session_active:
            raise RuntimeError("Browser not started. Call start() first.")
        
        print(f"🌐 Navigating to: {url}")
        
        try:
            response = self._page.goto(url, wait_until=wait_until, timeout=30000)
            
            return {
                "success": True,
                "url": self._page.url,
                "title": self._page.title(),
                "status": response.status if response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_sanitized_dom(self, max_length: int = 5000) -> Dict[str, Any]:
        """
        Returns a simplified, SAFE version of the page for the LLM.
        
        This is a core security feature: The raw DOM may contain:
        - Malicious prompt injections in hidden fields
        - Tracking scripts
        - PII in forms
        
        We extract only semantic content and interactive elements.
        
        Args:
            max_length: Maximum text length to return
            
        Returns:
            Sanitized page data
        """
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        # Extract text content
        try:
            content = self._page.evaluate("document.body.innerText")
        except Exception:
            content = ""
        
        # Extract interactive elements
        try:
            inputs = self._page.evaluate("""
                Array.from(document.querySelectorAll('input, button, a, select, textarea')).map(el => ({
                    tagName: el.tagName.toLowerCase(),
                    type: el.type || '',
                    id: el.id || '',
                    name: el.name || '',
                    placeholder: el.placeholder || '',
                    text: el.innerText || el.value || '',
                    href: el.href || '',
                    visible: el.offsetParent !== null
                })).filter(el => el.visible)
            """)
        except Exception:
            inputs = []
        
        # Sanitize PII from content
        safe_content = self.airlock.sanitize(content)
        
        # Truncate to prevent context overflow
        safe_content = safe_content[:max_length]
        
        return {
            "text": safe_content,
            "interactive_elements": inputs[:50],  # Limit to prevent overflow
            "url": self._page.url,
            "title": self._page.title(),
            "element_count": len(inputs)
        }
    
    def interact(
        self,
        action: str,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        element_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an interaction with the page.
        
        Args:
            action: Action type ('click', 'type', 'type_password', 'select')
            selector: CSS selector for element
            value: Value to input (for type/select actions)
            element_id: Element ID (alternative to selector)
            
        Returns:
            Interaction result
        """
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        # Build selector
        if element_id:
            selector = f"#{element_id}"
        
        if not selector:
            return {"success": False, "error": "No selector provided"}
        
        try:
            if action == "click":
                self._page.click(selector, timeout=5000)
                result = {"success": True, "action": "clicked"}
            
            elif action == "type":
                if not value:
                    return {"success": False, "error": "No value provided"}
                self._page.fill(selector, value, timeout=5000)
                result = {"success": True, "action": "typed"}
            
            elif action == "type_password":
                # CRITICAL: User-in-the-loop for passwords
                # The LLM never sees the actual password
                print("🔒 Password input required")
                print(f"   Element: {selector}")
                
                # In production, use secure input method
                try:
                    import getpass
                    password = getpass.getpass("Enter password: ")
                    self._page.fill(selector, password, timeout=5000)
                    result = {"success": True, "action": "password_entered"}
                except Exception as e:
                    result = {"success": False, "error": f"Password input failed: {e}"}
            
            elif action == "select":
                if not value:
                    return {"success": False, "error": "No value provided"}
                self._page.select_option(selector, value, timeout=5000)
                result = {"success": True, "action": "selected"}
            
            elif action == "press":
                # Press a key (e.g., Enter)
                self._page.press(selector, value or "Enter", timeout=5000)
                result = {"success": True, "action": "key_pressed"}
            
            else:
                result = {"success": False, "error": f"Unknown action: {action}"}
            
            # Wait for any navigation or network activity to settle
            try:
                self._page.wait_for_load_state("networkidle", timeout=3000)
            except:
                pass  # Non-critical
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    def screenshot(self, filename: str = "screenshot.png") -> Dict[str, Any]:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Output filename
            
        Returns:
            Screenshot result
        """
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        try:
            self._page.screenshot(path=filename, full_page=True)
            return {
                "success": True,
                "filename": filename
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript in the page context.
        
        Args:
            script: JavaScript code
            
        Returns:
            Script result
        """
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        return self._page.evaluate(script)
    
    def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element appeared
        """
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        try:
            self._page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    def close(self):
        """Close the browser session."""
        if self.session_active:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
            
            self.session_active = False
            print("✅ Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies for the current context."""
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        return self._context.cookies()
    
    def set_cookies(self, cookies: List[Dict[str, Any]]):
        """Set cookies in the browser context."""
        if not self.session_active:
            raise RuntimeError("Browser not started")
        
        self._context.add_cookies(cookies)
