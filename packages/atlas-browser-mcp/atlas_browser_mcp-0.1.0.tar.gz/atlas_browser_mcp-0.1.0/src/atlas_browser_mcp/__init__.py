"""
Atlas Browser MCP Server

Visual web browsing for AI agents via Model Context Protocol.

Features:
- Screenshot-based navigation (visual-first approach)
- Set-of-Mark (SoM) labeling for interactive elements
- Humanized mouse movements and typing patterns
- Multi-click support for CAPTCHA and checkboxes
- Anti-detection measures for bot protection bypass

Usage:
    # As MCP server (for Claude Desktop, etc.)
    atlas-browser-mcp

    # Or programmatically
    from atlas_browser_mcp.browser import VisualBrowser
    browser = VisualBrowser()
    result = browser.execute("navigate", url="https://example.com")
"""

__version__ = "0.1.0"
__author__ = "NotLing"

from .browser import VisualBrowser, BrowserResult

__all__ = ["VisualBrowser", "BrowserResult", "__version__"]