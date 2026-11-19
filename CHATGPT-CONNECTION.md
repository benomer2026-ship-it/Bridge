# ChatGPT connection settings

Endpoint: `https://YOUR-SERVICE.onrender.com/mcp`

Authentication:
- Type: API key
- Header name: `Authorization`
- Scheme: `Bearer`
- Credential value: the cloud service's `MCP_ACCESS_TOKEN`

Do not use `ANTHROPIC_API_KEY` as the ChatGPT connection credential. The Anthropic key belongs only in the cloud service's secret environment variables.
