import json
import logging
import re
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cm-docs-mcp-server")

mcp = FastMCP("CM.com Documentation MCP")

BASE_URL = "https://developers.cm.com"


async def _fetch(url: str) -> str | None:
    """Fetch a URL and return its content."""
    logger.info(f"Fetching: {url}")
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Successfully fetched: {url}")
            return response.text
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None


@mcp.tool(annotations=ToolAnnotations(title="List CM.com Products", readOnlyHint=True))
async def list_products() -> str:
    """
    List all available CM.com product documentation sections.
    Call this first to see what products have documentation available.
    """
    html = await _fetch(BASE_URL)
    if not html:
        return "Failed to fetch CM.com developer portal"

    # Extract childrenProjects from meta tag
    match = re.search(r'name="childrenProjects"\s+content="([^"]+)"', html)
    if not match:
        return "Could not find product list"

    # Decode HTML entities and parse JSON
    content = match.group(1).replace("&quot;", '"')
    try:
        projects = json.loads(content)
    except json.JSONDecodeError:
        return "Failed to parse product list"

    result = "# CM.com Developer Documentation\n\n"
    result += "## Available Products\n\n"
    for p in projects:
        result += f"- **{p['name']}**: `/{p['subdomain']}/docs`\n"

    result += "\n\nUse `list_pages(product)` to see available pages for a product."
    return result


@mcp.tool(annotations=ToolAnnotations(title="List Documentation Pages", readOnlyHint=True))
async def list_pages(product: str) -> str:
    """
    List all documentation pages for a specific product.

    Args:
        product: Product subdomain (e.g., 'messaging', 'sign', 'voice')
    """
    if not product or not product.strip():
        return "Error: product parameter is required"
    product = product.strip().lower()
    url = f"{BASE_URL}/{product}/docs"
    html = await _fetch(url)
    if not html:
        return f"Failed to fetch docs for '{product}'. Use list_products() to see available products."

    soup = BeautifulSoup(html, "lxml")

    # Find all doc page links in the sidebar/navigation
    pages = set()
    pattern = re.compile(rf"^/{product}/docs/[\w-]+$")

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if pattern.match(href):
            title = link.get_text(strip=True) or href.split("/")[-1]
            pages.add((href, title))

    if not pages:
        return f"No documentation pages found for '{product}'"

    result = f"# {product.replace('-', ' ').title()} Documentation\n\n"
    result += "## Available Pages\n\n"
    for href, title in sorted(pages):
        result += f"- [{title}]({href})\n"

    result += "\n\nUse `fetch_page(path)` to read a specific page."
    return result


@mcp.tool(annotations=ToolAnnotations(title="Fetch Documentation Page", readOnlyHint=True))
async def fetch_page(path: str) -> str:
    """
    Fetch and read a specific documentation page.

    Args:
        path: Path to the doc page (e.g., '/messaging/docs/introduction')
    """
    if not path or not path.strip():
        return "Error: path parameter is required"
    path = path.strip()

    if path.startswith("http"):
        url = path
    else:
        if not path.startswith("/"):
            path = "/" + path
        url = f"{BASE_URL}{path}"

    html = await _fetch(url)
    if not html:
        return f"Failed to fetch: {url}"

    soup = BeautifulSoup(html, "lxml")

    # Get title
    title_elem = soup.find("h1") or soup.find("title")
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"

    # Find main content
    content_area = (
            soup.find("article") or
            soup.find("main") or
            soup.find(class_="content") or
            soup.body
    )

    if not content_area:
        return f"# {title}\n\nNo content found."

    # Clean up navigation/chrome elements
    for elem in content_area.find_all(["script", "style", "nav", "header", "footer"]):
        elem.decompose()

    content = content_area.get_text(separator="\n", strip=True)

    result = f"# {title}\n\n**Source**: {url}\n\n"
    result += content[:15000]
    if len(content) > 15000:
        result += "\n\n... (truncated)"

    return result


def main():
    mcp.run()


if __name__ == "__main__":
    main()
