"""
Visual Browser Core

Screenshot-based web browsing with Set-of-Mark labeling and humanized interactions.
"""

import base64
import random
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Playwright 延遲導入
_playwright_available = True
try:
    from playwright.sync_api import sync_playwright, Browser as PWBrowser, Page, BrowserContext
except ImportError:
    _playwright_available = False


@dataclass
class BrowserResult:
    """瀏覽器操作結果"""
    success: bool
    data: dict = None
    error: str = None
    metadata: dict = field(default_factory=dict)


class VisualBrowser:
    """
    Visual Browser - Eyes and hands for AI agents
    
    Core concepts:
    - Visual-first: Understand pages through screenshots, not DOM
    - Set-of-Mark: Label interactive elements with numeric IDs
    - Humanized: Simulate human mouse movements and typing patterns
    """
    
    # === Configuration ===
    VIEWPORT = {"width": 1280, "height": 800}
    SCREENSHOT_QUALITY = 75
    
    def __init__(
        self, 
        headless: bool = False,
        humanize: bool = True,
        workspace: str = None
    ):
        self._headless = headless
        self._humanize = humanize
        self._workspace = Path(workspace) if workspace else Path.cwd() / "workspace"
        self._workspace.mkdir(parents=True, exist_ok=True)
        
        # Browser state
        self._playwright = None
        self._browser: Optional[PWBrowser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # Mouse position tracking (for humanized movement)
        self._mouse_pos = (self.VIEWPORT["width"] // 2, self.VIEWPORT["height"] // 2)
        
        # Element mapping (kept in Python, not sent to LLM)
        self._element_map: dict[int, dict] = {}
    
    def execute(self, action: str, **kwargs) -> BrowserResult:
        """Execute a browser action"""
        if not _playwright_available:
            return BrowserResult(
                success=False,
                error="Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
        
        actions = {
            "navigate": self._navigate,
            "observe": self._observe,
            "click": self._click,
            "multi_click": self._multi_click,
            "type": self._type,
            "scroll": self._scroll,
            "close": self._close
        }
        
        handler = actions.get(action)
        if not handler:
            return BrowserResult(
                success=False,
                error=f"Unknown action: {action}. Available: {list(actions.keys())}"
            )
        
        try:
            return handler(**kwargs)
        except Exception as e:
            return BrowserResult(
                success=False,
                error=f"Browser error: {str(e)}"
            )
    
    # === Browser Lifecycle ===
    
    def _ensure_browser(self):
        """Ensure browser is started with anti-detection configuration"""
        if self._page is not None:
            return
        
        self._playwright = sync_playwright().start()
        
        self._browser = self._playwright.chromium.launch(
            headless=self._headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        self._context = self._browser.new_context(
            viewport=self.VIEWPORT,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
        )
        
        self._page = self._context.new_page()
        
        # Anti-detection script
        self._page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)
    
    def _close(self, **_) -> BrowserResult:
        """Close the browser"""
        if self._browser:
            self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
        
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        
        self._element_map = {}
        self._mouse_pos = (self.VIEWPORT["width"] // 2, self.VIEWPORT["height"] // 2)
        
        return BrowserResult(success=True, data={"message": "Browser closed"})
    
    # === Set-of-Mark Injection ===
    
    SOM_INJECT_SCRIPT = """
    () => {
        // Remove old labels
        document.querySelectorAll('.atlas-som-label').forEach(el => el.remove());
        
        const selectors = [
            'a[href]',
            'button',
            'input:not([type="hidden"])',
            'select',
            'textarea',
            '[role="button"]',
            '[role="link"]',
            '[role="checkbox"]',
            '[role="menuitem"]',
            '[onclick]',
            '[tabindex]:not([tabindex="-1"])'
        ];
        
        const elements = [];
        let labelId = 0;
        
        function markElements(doc, offsetX = 0, offsetY = 0) {
            if (!doc) return;
            
            selectors.forEach(selector => {
                try {
                    doc.querySelectorAll(selector).forEach(el => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        if (
                            rect.width <= 0 || 
                            rect.height <= 0 ||
                            style.visibility === 'hidden' ||
                            style.display === 'none' ||
                            parseFloat(style.opacity) === 0
                        ) {
                            return;
                        }
                        
                        const viewportWidth = window.innerWidth;
                        const viewportHeight = window.innerHeight;
                        
                        if (
                            rect.right < 0 || 
                            rect.bottom < 0 ||
                            rect.left > viewportWidth ||
                            rect.top > viewportHeight
                        ) {
                            return;
                        }
                        
                        const label = document.createElement('div');
                        label.className = 'atlas-som-label';
                        label.textContent = labelId;
                        label.style.cssText = `
                            position: fixed !important;
                            left: ${rect.left + offsetX}px !important;
                            top: ${rect.top + offsetY}px !important;
                            background: #FFFF00 !important;
                            color: #000000 !important;
                            border: 2px solid #FF0000 !important;
                            font-size: 12px !important;
                            font-weight: bold !important;
                            font-family: monospace !important;
                            padding: 1px 4px !important;
                            z-index: 2147483647 !important;
                            pointer-events: none !important;
                            border-radius: 3px !important;
                            line-height: 1.2 !important;
                        `;
                        document.body.appendChild(label);
                        
                        let text = '';
                        if (el.tagName === 'INPUT') {
                            text = el.placeholder || el.value || el.name || '';
                        } else if (el.tagName === 'SELECT') {
                            text = el.options[el.selectedIndex]?.text || '';
                        } else {
                            text = el.innerText || el.textContent || el.getAttribute('aria-label') || '';
                        }
                        text = text.trim().substring(0, 50);
                        
                        elements.push({
                            id: labelId,
                            x: Math.round(rect.left + rect.width / 2 + offsetX),
                            y: Math.round(rect.top + rect.height / 2 + offsetY),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            tag: el.tagName.toLowerCase(),
                            type: el.type || '',
                            text: text
                        });
                        
                        labelId++;
                    });
                } catch (e) {}
            });
            
            try {
                doc.querySelectorAll('iframe').forEach(iframe => {
                    try {
                        const iframeRect = iframe.getBoundingClientRect();
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                        if (iframeDoc) {
                            markElements(
                                iframeDoc, 
                                offsetX + iframeRect.left, 
                                offsetY + iframeRect.top
                            );
                        }
                    } catch (e) {}
                });
            } catch (e) {}
        }
        
        markElements(document);
        return elements;
    }
    """
    
    def __del__(self):
        try:
            self._close()
        except:
            pass
    
    # === Core Actions ===
    
    def _navigate(self, url: str = None, **_) -> BrowserResult:
        """Navigate to URL and return observation"""
        if not url:
            return BrowserResult(success=False, error="URL required")
        
        self._ensure_browser()
        
        try:
            self._page.goto(url, timeout=30000, wait_until="domcontentloaded")
            self._page.wait_for_timeout(1500)
            return self._observe()
            
        except Exception as e:
            return BrowserResult(
                success=False,
                error=f"Navigation failed: {str(e)}"
            )
    
    def _observe(self, **_) -> BrowserResult:
        """Get visual observation of current page"""
        if self._page is None:
            return BrowserResult(success=False, error="No page open. Use navigate first.")
        
        try:
            self._page.wait_for_timeout(500)
            
            elements = self._page.evaluate(self.SOM_INJECT_SCRIPT)
            
            self._element_map = {}
            for el in elements:
                self._element_map[el['id']] = {
                    'x': el['x'],
                    'y': el['y'],
                    'width': el['width'],
                    'height': el['height'],
                    'tag': el['tag'],
                    'type': el['type'],
                    'text': el['text']
                }
            
            screenshot_bytes = self._page.screenshot(
                type="jpeg",
                quality=self.SCREENSHOT_QUALITY
            )
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            elements_for_llm = []
            for el in elements:
                element_info = {
                    'id': el['id'],
                    'tag': el['tag'],
                }
                if el['text']:
                    element_info['text'] = el['text']
                if el['type']:
                    element_info['type'] = el['type']
                elements_for_llm.append(element_info)
            
            return BrowserResult(
                success=True,
                data={
                    'url': self._page.url,
                    'title': self._page.title(),
                    'screenshot': screenshot_base64,
                    'elements': elements_for_llm,
                    'element_count': len(elements)
                },
                metadata={'has_image': True}
            )
            
        except Exception as e:
            return BrowserResult(
                success=False,
                error=f"Observation failed: {str(e)}"
            )
    
    def _click(self, label_id: int = None, **_) -> BrowserResult:
        """Click element by label ID"""
        if label_id is None:
            return BrowserResult(success=False, error="label_id required")
        
        if label_id not in self._element_map:
            available = list(self._element_map.keys())[:10]
            return BrowserResult(
                success=False, 
                error=f"Label [{label_id}] not found. Available: {available}..."
            )
        
        if self._page is None:
            return BrowserResult(success=False, error="No page open")
        
        element = self._element_map[label_id]
        
        try:
            self._page.evaluate("() => document.querySelectorAll('.atlas-som-label').forEach(el => el.remove())")
            
            self._human_click_at(
                element['x'], 
                element['y'], 
                element['width'], 
                element['height']
            )
            
            try:
                self._page.wait_for_load_state("networkidle", timeout=3000)
            except:
                pass
            
            self._page.wait_for_timeout(500)
            return self._observe()
            
        except Exception as e:
            return BrowserResult(
                success=False,
                error=f"Click failed: {str(e)}"
            )
            
    def _multi_click(self, label_ids: list = None, **_) -> BrowserResult:
        """Click multiple elements (for CAPTCHA, checkboxes, etc.)"""
        if not label_ids:
            return BrowserResult(success=False, error="label_ids required (e.g., [1, 5, 8])")
        
        if self._page is None:
            return BrowserResult(success=False, error="No page open")
        
        self._page.evaluate("() => document.querySelectorAll('.atlas-som-label').forEach(el => el.remove())")
        
        results = []
        
        for label_id in label_ids:
            if label_id not in self._element_map:
                results.append({"label_id": label_id, "success": False, "error": "Not found"})
                continue
            
            element = self._element_map[label_id]
            
            try:
                self._human_click_at(
                    element['x'],
                    element['y'],
                    element['width'],
                    element['height']
                )
                results.append({"label_id": label_id, "success": True})
                
                if self._humanize:
                    time.sleep(random.uniform(0.15, 0.35))
                    
            except Exception as e:
                results.append({"label_id": label_id, "success": False, "error": str(e)})
        
        self._page.wait_for_timeout(300)
        
        observe_result = self._observe()
        
        if observe_result.success:
            observe_result.data["clicks"] = results
            observe_result.data["clicked_count"] = sum(1 for r in results if r.get("success"))
        
        return observe_result
    
    def _type(self, text: str = None, submit: bool = False, **_) -> BrowserResult:
        """Type text at current focus"""
        if not text:
            return BrowserResult(success=False, error="text required")
        
        if self._page is None:
            return BrowserResult(success=False, error="No page open")
        
        try:
            self._human_type(text)
            
            if submit:
                if self._humanize:
                    time.sleep(random.uniform(0.1, 0.3))
                self._page.keyboard.press("Enter")
                
                try:
                    self._page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    pass
                self._page.wait_for_timeout(1000)
            else:
                self._page.wait_for_timeout(500)
            
            return self._observe()
            
        except Exception as e:
            return BrowserResult(
                success=False,
                error=f"Type failed: {str(e)}"
            )
    
    def _scroll(self, direction: str = "down", **_) -> BrowserResult:
        """Scroll the page"""
        if self._page is None:
            return BrowserResult(success=False, error="No page open")
        
        if direction not in ["up", "down"]:
            return BrowserResult(success=False, error="direction must be 'up' or 'down'")
        
        try:
            amount = random.randint(250, 400) if self._humanize else 300
            self._human_scroll(direction, amount)
            return self._observe()
            
        except Exception as e:
            return BrowserResult(
                success=False,
                error=f"Scroll failed: {str(e)}"
            )
    
    # === Humanized Helpers ===
    
    def _bezier_curve(self, start: tuple, end: tuple, steps: int = None) -> list[tuple]:
        """Generate Bezier curve path for mouse movement"""
        if steps is None:
            distance = ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
            steps = max(20, min(int(distance / 10), 40))
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        ctrl1_x = start[0] + dx * 0.25 + random.uniform(-abs(dx) * 0.3, abs(dx) * 0.3)
        ctrl1_y = start[1] + dy * 0.25 + random.uniform(-abs(dy) * 0.3, abs(dy) * 0.3)
        ctrl2_x = start[0] + dx * 0.75 + random.uniform(-abs(dx) * 0.3, abs(dx) * 0.3)
        ctrl2_y = start[1] + dy * 0.75 + random.uniform(-abs(dy) * 0.3, abs(dy) * 0.3)
        
        p0 = start
        p1 = (ctrl1_x, ctrl1_y)
        p2 = (ctrl2_x, ctrl2_y)
        p3 = end
        
        points = []
        for i in range(steps + 1):
            t = i / steps
            u = 1 - t
            
            x = (u**3 * p0[0] + 
                 3 * u**2 * t * p1[0] + 
                 3 * u * t**2 * p2[0] + 
                 t**3 * p3[0])
            
            y = (u**3 * p0[1] + 
                 3 * u**2 * t * p1[1] + 
                 3 * u * t**2 * p2[1] + 
                 t**3 * p3[1])
            
            points.append((int(x), int(y)))
        
        return points
    
    def _human_move(self, target: tuple):
        """Move mouse to target with humanized trajectory"""
        if not self._humanize:
            self._page.mouse.move(target[0], target[1])
            self._mouse_pos = target
            return
        
        path = self._bezier_curve(self._mouse_pos, target)
        
        for i, point in enumerate(path):
            progress = i / len(path)
            if progress < 0.2 or progress > 0.8:
                delay = random.uniform(0.008, 0.015)
            else:
                delay = random.uniform(0.003, 0.008)
            
            self._page.mouse.move(point[0], point[1])
            time.sleep(delay)
        
        self._mouse_pos = target
    
    def _human_click_at(self, x: int, y: int, width: int, height: int):
        """Humanized click at position"""
        if self._humanize:
            max_offset_x = min(10, width * 0.15)
            max_offset_y = min(10, height * 0.15)
            offset_x = random.uniform(-max_offset_x, max_offset_x)
            offset_y = random.uniform(-max_offset_y, max_offset_y)
        else:
            offset_x = 0
            offset_y = 0
        
        target_x = int(x + offset_x)
        target_y = int(y + offset_y)
        
        self._human_move((target_x, target_y))
        
        if self._humanize:
            time.sleep(random.uniform(0.1, 0.3))
        
        self._page.mouse.down()
        if self._humanize:
            time.sleep(random.uniform(0.05, 0.12))
        self._page.mouse.up()
        
        if self._humanize:
            time.sleep(random.uniform(0.1, 0.25))
    
    def _human_type(self, text: str):
        """Humanized typing"""
        if not self._humanize:
            self._page.keyboard.type(text)
            return
        
        for i, char in enumerate(text):
            delay = random.uniform(0.05, 0.15)
            
            if random.random() < 0.1:
                delay += random.uniform(0.15, 0.4)
            
            if i > 0 and text[i-1] == ' ':
                delay += random.uniform(0.05, 0.15)
            
            self._page.keyboard.type(char)
            time.sleep(delay)
    
    def _human_scroll(self, direction: str, amount: int = 300):
        """Humanized scrolling with inertia"""
        delta = amount if direction == "down" else -amount
        
        if not self._humanize:
            self._page.mouse.wheel(0, delta)
            return
        
        segments = random.randint(5, 10)
        total_scrolled = 0
        
        for i in range(segments):
            progress = i / segments
            if progress < 0.2 or progress > 0.8:
                segment_ratio = 0.05
            else:
                segment_ratio = 0.15
            
            segment_delta = int(delta * segment_ratio)
            self._page.mouse.wheel(0, segment_delta)
            total_scrolled += segment_delta
            time.sleep(random.uniform(0.02, 0.05))
        
        remaining = delta - total_scrolled
        if abs(remaining) > 10:
            self._page.mouse.wheel(0, remaining)
        
        if random.random() < 0.15:
            time.sleep(random.uniform(0.1, 0.3))
            correction = int(delta * random.uniform(-0.1, -0.05))
            self._page.mouse.wheel(0, correction)
        
        if self._humanize:
            time.sleep(random.uniform(0.3, 0.8))