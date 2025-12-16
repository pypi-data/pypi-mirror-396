"""
Web Tools

Tools for web operations:
- WebFetch: Fetch and process web page content
- WebSearch: Search the web using DuckDuckGo or Brave Search
- WebScreenshot: Take screenshots of web pages
- ReadImage: Read and analyze images for code generation
"""

import json
import re
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, List, Dict, Any
from html.parser import HTMLParser

from .base import Tool, ToolResult, ToolParameter, ToolPermission


class HTMLToTextParser(HTMLParser):
    """Simple HTML to text converter"""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
        elif tag == "style":
            self.in_style = True
        elif tag in ["p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li"]:
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            self.text_parts.append(data)

    def get_text(self) -> str:
        text = "".join(self.text_parts)
        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()


class WebFetchTool(Tool):
    """Fetch content from a URL"""

    name = "WebFetch"
    description = (
        "Fetch content from a web URL and convert HTML to text. "
        "Use this to read documentation, articles, or any web page."
    )
    category = "web"
    permission = ToolPermission.ASK  # Ask before making web requests

    parameters = [
        ToolParameter(
            name="url",
            description="The URL to fetch",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="prompt",
            description="Optional prompt to focus on specific information from the page",
            type="string",
            required=False,
        ),
    ]

    def execute(self, url: str, prompt: str = None) -> ToolResult:
        """Fetch and process a web page"""

        # Validate URL
        if not url.startswith(("http://", "https://")):
            # Upgrade to https
            url = "https://" + url

        try:
            # Create request with headers
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; NC1709/1.0; +https://github.com/nc1709)",
                "Accept": "text/html,application/xhtml+xml,text/plain",
            }
            req = urllib.request.Request(url, headers=headers)

            # Fetch with timeout
            with urllib.request.urlopen(req, timeout=30) as response:
                # Check content type
                content_type = response.headers.get("Content-Type", "")

                # Read content
                content = response.read()

                # Determine encoding
                encoding = "utf-8"
                if "charset=" in content_type:
                    encoding = content_type.split("charset=")[-1].split(";")[0].strip()

                try:
                    text = content.decode(encoding)
                except UnicodeDecodeError:
                    text = content.decode("utf-8", errors="replace")

                # Convert HTML to text
                if "html" in content_type.lower():
                    parser = HTMLToTextParser()
                    parser.feed(text)
                    text = parser.get_text()

                # Truncate if too long
                max_length = 50000
                if len(text) > max_length:
                    text = text[:max_length] + "\n\n... (content truncated)"

                # Format output
                output = f"Content from {url}:\n\n{text}"

                return ToolResult(
                    success=True,
                    output=output,
                    target=url,
                    data={
                        "url": url,
                        "content_type": content_type,
                        "length": len(text),
                    },
                )

        except urllib.error.HTTPError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"HTTP {e.code}: {e.reason}",
                target=url,
            )
        except urllib.error.URLError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"URL error: {e.reason}",
                target=url,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error fetching URL: {e}",
                target=url,
            )


class WebSearchTool(Tool):
    """Search the web using DuckDuckGo or Brave Search"""

    name = "WebSearch"
    description = (
        "Search the web for information using DuckDuckGo (free) or Brave Search (with API key). "
        "Returns search results with titles, URLs, and snippets."
    )
    category = "web"
    permission = ToolPermission.ASK

    parameters = [
        ToolParameter(
            name="query",
            description="Search query",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="num_results",
            description="Number of results to return (default: 5, max: 10)",
            type="integer",
            required=False,
            default=5,
        ),
        ToolParameter(
            name="search_engine",
            description="Search engine to use: 'duckduckgo' (default, free) or 'brave' (requires API key)",
            type="string",
            required=False,
            default="duckduckgo",
        ),
    ]

    def execute(
        self,
        query: str,
        num_results: int = 5,
        search_engine: str = "duckduckgo",
    ) -> ToolResult:
        """Search the web"""
        num_results = min(max(1, num_results), 10)  # Clamp to 1-10

        if search_engine.lower() == "brave":
            return self._search_brave(query, num_results)
        else:
            return self._search_duckduckgo(query, num_results)

    def _search_duckduckgo(self, query: str, num_results: int) -> ToolResult:
        """Search using DuckDuckGo - tries duckduckgo-search library first, then fallbacks"""
        results = []

        # Method 1: Try ddgs library (most reliable) - newer version
        try:
            from ddgs import DDGS
            ddgs = DDGS()
            search_results = ddgs.text(query, max_results=num_results)
            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
            if results:
                output = self._format_results(query, results)
                return ToolResult(
                    success=True,
                    output=output,
                    target=query,
                    data={"results": results, "query": query, "engine": "duckduckgo"},
                )
        except ImportError:
            # Try old package name
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=num_results):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("href", ""),
                            "snippet": r.get("body", ""),
                        })
                if results:
                    output = self._format_results(query, results)
                    return ToolResult(
                        success=True,
                        output=output,
                        target=query,
                        data={"results": results, "query": query, "engine": "duckduckgo"},
                    )
            except ImportError:
                pass  # Neither library installed
        except Exception as e:
            pass  # Library failed, try fallback

        # Method 2: Try DuckDuckGo Instant Answer API
        try:
            api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; NC1709/1.0)",
            }
            req = urllib.request.Request(api_url, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            # Extract instant answer
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "DuckDuckGo Answer"),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                    "source": data.get("AbstractSource", ""),
                })

            # Extract related topics
            for topic in data.get("RelatedTopics", [])[:num_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                    })

        except Exception:
            pass

        # Method 3: HTML scraping fallback
        if len(results) < num_results:
            try:
                html_results = self._scrape_duckduckgo_html(query, num_results - len(results))
                results.extend(html_results)
            except Exception as e:
                if not results:
                    # All methods failed - provide helpful error
                    return ToolResult(
                        success=False,
                        output="",
                        error=(
                            f"DuckDuckGo search failed. For better results, install: pip install duckduckgo-search\n"
                            f"Error: {e}"
                        ),
                        target=query,
                    )

        if not results:
            return ToolResult(
                success=True,
                output=f"No results found for: {query}\n\nTip: Install duckduckgo-search for better results: pip install duckduckgo-search",
                target=query,
                data={"results": [], "query": query},
            )

        output = self._format_results(query, results[:num_results])

        return ToolResult(
            success=True,
            output=output,
            target=query,
            data={
                "results": results[:num_results],
                "query": query,
                "engine": "duckduckgo",
            },
        )

    def _scrape_duckduckgo_html(self, query: str, num_results: int) -> List[Dict]:
        """Scrape DuckDuckGo HTML lite version"""
        results = []

        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")

        # Parse results from HTML
        # DuckDuckGo HTML version uses class="result__a" for links
        link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>'

        links = re.findall(link_pattern, html)
        snippets = re.findall(snippet_pattern, html)

        for i, (link_url, title) in enumerate(links[:num_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            # Clean up the URL (DuckDuckGo wraps URLs)
            if "uddg=" in link_url:
                try:
                    link_url = urllib.parse.unquote(link_url.split("uddg=")[1].split("&")[0])
                except:
                    pass
            if link_url and not link_url.startswith("/"):
                results.append({
                    "title": title.strip(),
                    "url": link_url,
                    "snippet": snippet.strip(),
                })

        return results

    def _search_brave(self, query: str, num_results: int) -> ToolResult:
        """Search using Brave Search API"""
        import os

        api_key = os.environ.get("BRAVE_SEARCH_API_KEY")
        if not api_key:
            return ToolResult(
                success=False,
                output="",
                error=(
                    "Brave Search requires API key. "
                    "Set BRAVE_SEARCH_API_KEY environment variable. "
                    "Get a free API key at: https://brave.com/search/api/"
                ),
                target=query,
            )

        try:
            url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={num_results}"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            }
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

            results = []
            web_results = data.get("web", {}).get("results", [])

            for item in web_results[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                })

            if not results:
                return ToolResult(
                    success=True,
                    output=f"No results found for: {query}",
                    target=query,
                    data={"results": [], "query": query},
                )

            output = self._format_results(query, results)

            return ToolResult(
                success=True,
                output=output,
                target=query,
                data={
                    "results": results,
                    "query": query,
                    "engine": "brave",
                },
            )

        except urllib.error.HTTPError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Brave Search API error: HTTP {e.code}",
                target=query,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Brave Search failed: {e}",
                target=query,
            )

    def _format_results(self, query: str, results: List[Dict]) -> str:
        """Format search results for output"""
        output_parts = [
            f"Search results for: {query}",
            "=" * 60,
        ]

        for i, result in enumerate(results, 1):
            output_parts.append(f"\n{i}. {result.get('title', 'No title')}")
            if result.get("url"):
                output_parts.append(f"   URL: {result['url']}")
            if result.get("snippet"):
                snippet = result["snippet"][:300]
                if len(result.get("snippet", "")) > 300:
                    snippet += "..."
                output_parts.append(f"   {snippet}")

        output_parts.append(f"\n{'=' * 60}")
        output_parts.append(f"Found {len(results)} result(s)")

        return "\n".join(output_parts)


class WebScreenshotTool(Tool):
    """Take a screenshot of a web page (requires playwright)"""

    name = "WebScreenshot"
    description = (
        "Take a screenshot of a web page. Requires playwright to be installed. "
        "Returns the path to the saved screenshot image."
    )
    category = "web"
    permission = ToolPermission.ASK

    parameters = [
        ToolParameter(
            name="url",
            description="The URL to screenshot",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="output_path",
            description="Path to save the screenshot (default: /tmp/screenshot.png)",
            type="string",
            required=False,
            default="/tmp/nc1709_screenshot.png",
        ),
        ToolParameter(
            name="full_page",
            description="Capture full page instead of viewport only",
            type="boolean",
            required=False,
            default=False,
        ),
    ]

    def execute(
        self,
        url: str,
        output_path: str = "/tmp/nc1709_screenshot.png",
        full_page: bool = False,
    ) -> ToolResult:
        """Take screenshot of web page"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return ToolResult(
                success=False,
                output="",
                error=(
                    "Playwright not installed. Install with:\n"
                    "  pip install playwright\n"
                    "  playwright install chromium"
                ),
                target=url,
            )

        # Validate URL
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.screenshot(path=output_path, full_page=full_page)
                browser.close()

            return ToolResult(
                success=True,
                output=f"Screenshot saved to: {output_path}",
                target=url,
                data={
                    "url": url,
                    "output_path": output_path,
                    "full_page": full_page,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Screenshot failed: {e}",
                target=url,
            )


class ReadImageTool(Tool):
    """Read and analyze images for code generation"""

    name = "ReadImage"
    description = (
        "Read an image file (PNG, JPG, GIF, WebP) and prepare it for analysis. "
        "Use this to analyze UI mockups, screenshots, diagrams, or any visual reference "
        "to generate code. The image will be included in the context for the LLM to see."
    )
    category = "file"
    permission = ToolPermission.AUTO  # Safe to auto-execute

    parameters = [
        ToolParameter(
            name="image_path",
            description="Path to the image file (PNG, JPG, GIF, WebP)",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="prompt",
            description="Optional prompt describing what to look for or generate from the image",
            type="string",
            required=False,
        ),
    ]

    def execute(self, image_path: str, prompt: str = None) -> ToolResult:
        """Read and prepare an image for LLM analysis"""
        try:
            from ...image_input import (
                load_image,
                get_image_info,
                is_image_file,
                format_image_for_api,
            )
        except ImportError:
            return ToolResult(
                success=False,
                output="",
                error="Image input module not available",
                target=image_path,
            )

        from pathlib import Path

        path = Path(image_path).expanduser()

        # Check if file exists
        if not path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Image file not found: {image_path}",
                target=image_path,
            )

        # Check if it's a supported image
        if not is_image_file(str(path)):
            return ToolResult(
                success=False,
                output="",
                error=f"Not a supported image format: {image_path}. Supported: PNG, JPG, GIF, WebP",
                target=image_path,
            )

        # Load the image
        image = load_image(str(path))
        if not image:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to load image: {image_path}",
                target=image_path,
            )

        # Get image info
        info = get_image_info(str(path))

        # Build output description
        output_parts = [
            f"Image loaded: {path.name}",
            f"  Format: {info.get('format', 'unknown').upper()}",
            f"  Size: {info.get('size_human', 'unknown')}",
        ]

        if info.get('width') and info.get('height'):
            output_parts.append(f"  Dimensions: {info['width']}x{info['height']} pixels")

        if prompt:
            output_parts.append(f"\nAnalysis prompt: {prompt}")

        output_parts.append("\n[Image data has been loaded and is ready for analysis]")

        return ToolResult(
            success=True,
            output="\n".join(output_parts),
            target=image_path,
            data={
                "image_path": str(path.absolute()),
                "base64_data": image.base64_data,
                "mime_type": image.mime_type,
                "width": image.width,
                "height": image.height,
                "size_bytes": image.size_bytes,
                "prompt": prompt,
                # Format for API inclusion
                "api_format": format_image_for_api(image, "anthropic"),
            },
        )


class CaptureScreenshotTool(Tool):
    """Capture a screenshot for code generation"""

    name = "CaptureScreenshot"
    description = (
        "Capture a screenshot of a selected area on screen (macOS). "
        "Useful for analyzing UI elements or generating code from visual references."
    )
    category = "file"
    permission = ToolPermission.ASK  # Ask before capturing screen

    parameters = [
        ToolParameter(
            name="prompt",
            description="Optional prompt describing what to analyze in the screenshot",
            type="string",
            required=False,
        ),
    ]

    def execute(self, prompt: str = None) -> ToolResult:
        """Capture a screenshot"""
        try:
            from ...image_input import (
                capture_screenshot,
                load_image,
                get_image_info,
                format_image_for_api,
            )
        except ImportError:
            return ToolResult(
                success=False,
                output="",
                error="Image input module not available",
                target="screenshot",
            )

        import platform
        if platform.system() != 'Darwin':
            return ToolResult(
                success=False,
                output="",
                error="Screenshot capture is currently only supported on macOS",
                target="screenshot",
            )

        # Capture screenshot (interactive selection)
        screenshot_path = capture_screenshot()
        if not screenshot_path:
            return ToolResult(
                success=False,
                output="",
                error="Screenshot cancelled or failed",
                target="screenshot",
            )

        # Load the captured image
        image = load_image(screenshot_path)
        if not image:
            return ToolResult(
                success=False,
                output="",
                error="Failed to load captured screenshot",
                target="screenshot",
            )

        info = get_image_info(screenshot_path)

        output_parts = [
            f"Screenshot captured: {screenshot_path}",
            f"  Size: {info.get('size_human', 'unknown')}",
        ]

        if info.get('width') and info.get('height'):
            output_parts.append(f"  Dimensions: {info['width']}x{info['height']} pixels")

        if prompt:
            output_parts.append(f"\nAnalysis prompt: {prompt}")

        output_parts.append("\n[Screenshot captured and ready for analysis]")

        return ToolResult(
            success=True,
            output="\n".join(output_parts),
            target=screenshot_path,
            data={
                "image_path": screenshot_path,
                "base64_data": image.base64_data,
                "mime_type": image.mime_type,
                "width": image.width,
                "height": image.height,
                "size_bytes": image.size_bytes,
                "prompt": prompt,
                "api_format": format_image_for_api(image, "anthropic"),
            },
        )


def register_web_tools(registry):
    """Register web tools with a registry"""
    registry.register_class(WebFetchTool)
    registry.register_class(WebSearchTool)
    registry.register_class(WebScreenshotTool)
    registry.register_class(ReadImageTool)
    registry.register_class(CaptureScreenshotTool)
