import hmac
import os

import httpx
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODELS_URL = "https://api.anthropic.com/v1/models"
ANTHROPIC_VERSION = os.getenv("ANTHROPIC_VERSION", "2026-10-21")

mcp = FastMCP(
    "Fahmi Claude Bridge",
    stateless_http=True,
    json_response=True,
)

def anthropic_headers() -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("The server owner has not configured ANTHROPIC_API_KEY.")
    return {
        "Authorization": f"Bearer {api_key}",
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

@mcp.tool()
async def list_claude_models() -> str:
    """List Claude models currently available to the configured Anthropic API key."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            ANTHROPIC_MODELS_URL,
            headers=anthropic_headers(),
            params={"limit": 100},
        )
    if response.is_error:
        return f"Anthropic API error ({response.status_code}): {response.text[:1500]}"
    models = response.json().get("data", [])
    if not models:
        return "No models were returned for this API key."
    return "\n".join(
        f"- {item.get('display_name', item.get('id', 'Unknown'))} — {item.get('id', '')}"
        for item in models
    )

@mcp.tool()
async def ask_claude(
    prompt: str,
    model: str = "claude-sonnet-4-5",
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """Send a prompt to Claude through the server owner's Anthropic API account."""
    if not prompt or not prompt.strip():
        return "Please provide a non-empty prompt."
    if max_tokens < 1 or max_tokens > 8192:
        return "max_tokens must be between 1 and 8192."

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system.strip():
        body["system"] = system.strip()

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            ANTHROPIC_API_URL,
            headers=anthropic_headers(),
            json=body,
        )
    if response.is_error:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except Exception:
            detail = response.text
        return f"Anthropic API error ({response.status_code}): {str(detail)[:1500]}"

    payload = response.json()
    text_blocks = [
        block.get("text", "")
        for block in payload.get("content", [])
        if block.get("type") == "text"
    ]
    result = "\n".join(part for part in text_blocks if part).strip()
    return result or "Claude returned no text content."

class Gateway:
    """Adds health reporting and bearer-token protection without changing MCP transport."""
    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.inner_app(scope, receive, send)
            return

        path = scope.get("path", "").rstrip("/")
        if path == "/health" and scope.get("method") == "GET":
            response = JSONResponse({"status": "ok", "service": "Fahmi Claude Bridge"})
            await response(scope, receive, send)
            return

        if path == "/mcp":
            expected = os.getenv("MCP_ACCESS_TOKEN", "")
            headers = dict(scope.get("headers", []))
            authorization = headers.get(b"authorization", b"").decode("latin1")
            supplied = authorization.removeprefix("Bearer ").strip()
            if not expected or not supplied or not hmac.compare_digest(supplied, expected):
                response = JSONResponse({"error": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return

        await self.inner_app(scope, receive, send)

app = Gateway(mcp.streamable_http_app())
