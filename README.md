# Fahmi Claude Bridge

A small, private MCP server that lets a compatible ChatGPT custom-MCP connection call Claude through the owner's Anthropic API account.

## Included tools

- `ask_claude`: sends one prompt to the selected Claude model.
- `list_claude_models`: lists models available to the configured Anthropic API key.

## Security model

- `ANTHROPIC_API_KEY` is stored only as a secret environment variable on the cloud host.
- `MCP_ACCESS_TOKEN` is a separate bearer token protecting the `/mcp` endpoint.
- Do not commit `.env`, API keys, or access tokens.
- Anyone who can use this MCP endpoint can consume the Anthropic API account's quota. Keep the endpoint private and rotate tokens if exposed.

## Deploy to Render

1. Create a private GitHub repository and upload these files, or deploy this folder using a supported Git-connected host.
2. In Render, choose **New > Blueprint** and select the repository containing `render.yaml`.
3. In the service's Environment settings, set `ANTHROPIC_API_KEY` to your Anthropic key. Do not put it in source files.
4. Keep the generated `MCP_ACCESS_TOKEN` secret. Copy it only for the ChatGPT connection's API-key credential field.
5. Deploy. Verify `https://YOUR-SERVICE.onrender.com/health` returns `{"status":"ok",...}`.
6. The MCP endpoint is `https://YOUR-SERVICE.onrender.com/mcp`.

## Connect in ChatGPT

Custom MCP connection availability depends on the ChatGPT plan and workspace permissions. In a supported account:

1. Open **Plugins** (or **Settings > Apps**, depending on the current interface).
2. Choose **Add custom MCP server**.
3. Name: `Fahmi Claude Bridge`.
4. Server URL: `https://YOUR-SERVICE.onrender.com/mcp`.
5. Authentication: API key / custom header using `Authorization` with the `Bearer` scheme. Enter the value of `MCP_ACCESS_TOKEN` (not the Anthropic API key).
6. Review the permissions and create the connection.
7. Test `list_claude_models`, then call `ask_claude`.

## Notes

- The default model in `ask_claude` is `claude-sonnet-4-5`. First call `list_claude_models` and select an exact model ID returned for your account if this default is unavailable.
- The server currently sends one user prompt per call; it does not impersonate Claude's consumer website or inherit a Claude Pro subscription.
- This is a deployable source project, not a hosted service. A public HTTPS URL must exist before the ChatGPT plugin connection can be completed.
