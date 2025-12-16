# Sealmetrics MCP Server

A Model Context Protocol (MCP) server that connects AI assistants like Claude to your Sealmetrics analytics data. Query traffic, conversions, and marketing performance using natural language.

## Features

- **Traffic Analysis**: Query traffic by source, medium, campaign, or country
- **Conversions**: Get sales and conversion data with attribution
- **Microconversions**: Track add-to-cart, signups, and other engagement events
- **Funnel Analysis**: Analyze conversion funnel performance
- **ROAS Evolution**: Track return on ad spend over time
- **Page Performance**: Analyze page views and landing page effectiveness
- **Pixel Generation**: Generate tracking pixels for Google Tag Manager

## Installation

### Using uvx (Recommended)

```bash
uvx sealmetrics-mcp
```

### Using pip

```bash
pip install sealmetrics-mcp
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sealmetrics": {
      "command": "uvx",
      "args": ["sealmetrics-mcp"],
      "env": {
        "SEALMETRICS_API_TOKEN": "your-api-token-here",
        "SEALMETRICS_ACCOUNT_ID": "your-account-id-here"
      }
    }
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SEALMETRICS_API_TOKEN` | Yes* | Your Sealmetrics API token (recommended) |
| `SEALMETRICS_ACCOUNT_ID` | No | Default account ID for queries |
| `SEALMETRICS_EMAIL` | Yes* | Email for login (alternative to token) |
| `SEALMETRICS_PASSWORD` | Yes* | Password for login (alternative to token) |

*Either `SEALMETRICS_API_TOKEN` or both `SEALMETRICS_EMAIL` and `SEALMETRICS_PASSWORD` are required.

## Available Tools

| Tool | Description |
|------|-------------|
| `get_accounts` | List available Sealmetrics accounts |
| `get_traffic_data` | Traffic by source, medium, campaign |
| `get_conversions` | Sales and conversion data |
| `get_microconversions` | Add-to-cart, signups, etc. |
| `get_funnel_data` | Conversion funnel analysis |
| `get_roas_evolution` | ROAS over time |
| `get_pages_performance` | Page views and landing pages |
| `generate_conversion_pixel` | Generate tracking pixel code |

## Example Queries

Once configured, you can ask Claude questions like:

- "How much traffic did we get from Google Ads yesterday?"
- "Show me conversions from organic search this month"
- "What's our ROAS evolution for the last 30 days?"
- "Which landing pages are performing best?"
- "Generate a conversion pixel for newsletter signups"

## Getting Your API Token

1. Log in to your Sealmetrics dashboard
2. Go to Settings > API
3. Generate a new API token
4. Copy the token to your Claude Desktop configuration

## Support

- Documentation: https://sealmetrics.com/docs
- Issues: https://github.com/sealmetrics/mcp-server/issues
- Email: support@sealmetrics.com

## License

MIT License - see LICENSE file for details.
