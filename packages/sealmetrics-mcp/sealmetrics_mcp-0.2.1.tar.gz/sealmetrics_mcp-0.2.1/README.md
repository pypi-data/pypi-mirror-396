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

## Installation Options

### Option 1: Claude Desktop (MCP via stdio)

For local AI assistants that support MCP protocol.

### Option 2: HTTP API (N8N, Make, Zapier, ChatGPT)

For automation tools and external integrations via REST API.

---

## Option 1: Claude Desktop Setup

### Using uvx (Recommended)

```bash
uvx sealmetrics-mcp
```

### Using pip

```bash
pip install sealmetrics-mcp
```

### Configuration

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

---

## Option 2: HTTP API (MCP over HTTP)

For N8N, Make, Zapier, ChatGPT Actions, and any HTTP-capable tool.

**Base URL**: `https://mcp.sealmetrics.com`

### Authentication

All endpoints require the `X-API-Key` header with your Sealmetrics API token.

```
X-API-Key: your-sealmetrics-api-token
X-Account-ID: your-account-id (optional, can also be sent as query param)
```

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (no auth required) |
| GET | `/api/accounts` | List available accounts |
| GET | `/api/traffic` | Get traffic/acquisition data |
| GET | `/api/conversions` | Get conversion/sales data |
| GET | `/api/microconversions` | Get microconversion events |

### MCP Protocol Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/tools` | List available MCP tools |
| POST | `/mcp/tools/call` | Call an MCP tool |
| POST | `/mcp/initialize` | Initialize MCP session |
| GET | `/mcp/sse` | SSE streaming endpoint |

---

## N8N Integration

### Step 1: Create HTTP Request Node

1. Add a new **HTTP Request** node
2. Configure:
   - **Method**: GET
   - **URL**: `https://mcp.sealmetrics.com/api/traffic`

### Step 2: Add Headers

```
X-API-Key: your-sealmetrics-api-token
X-Account-ID: your-account-id
```

### Step 3: Add Query Parameters

| Parameter | Example | Description |
|-----------|---------|-------------|
| `date_range` | `yesterday`, `last_7_days`, `last_30_days` | Time period |
| `report_type` | `Source`, `Medium`, `Campaign` | Grouping type |
| `utm_source` | `google-ads` | Filter by source |
| `limit` | `100` | Max results |

### Example: Get Yesterday's Traffic

```
URL: https://mcp.sealmetrics.com/api/traffic?date_range=yesterday&report_type=Source
Headers:
  X-API-Key: your-token
  X-Account-ID: your-account-id
```

### Example Response

```json
{
  "summary": {
    "total_clicks": 194,
    "total_conversions": 2,
    "total_revenue": 121.32,
    "conversion_rate": 1.03
  },
  "data": [
    {
      "name": "google-ads",
      "utm_medium": "cpc",
      "clicks": 67,
      "conversions": 1,
      "revenue": 49.41
    }
  ],
  "total_results": 12
}
```

---

## Make (Integromat) Integration

1. Add **HTTP** module
2. Configure:
   - **URL**: `https://mcp.sealmetrics.com/api/traffic`
   - **Method**: GET
   - **Headers**:
     - `X-API-Key`: your token
     - `X-Account-ID`: your account ID
   - **Query String**:
     - `date_range`: `last_7_days`

---

## Zapier Integration

1. Use **Webhooks by Zapier** (GET request)
2. Configure:
   - **URL**: `https://mcp.sealmetrics.com/api/traffic?date_range=last_7_days`
   - **Headers**:
     - `X-API-Key`: your token
     - `X-Account-ID`: your account ID

---

## ChatGPT Custom GPT / Actions

### OpenAPI Specification

Create a Custom GPT with this action schema:

```yaml
openapi: 3.0.0
info:
  title: Sealmetrics Analytics API
  version: 1.0.0
  description: Query Sealmetrics analytics data
servers:
  - url: https://mcp.sealmetrics.com
paths:
  /api/traffic:
    get:
      operationId: getTrafficData
      summary: Get traffic data by source, medium, or campaign
      parameters:
        - name: date_range
          in: query
          required: true
          schema:
            type: string
            enum: [yesterday, today, last_7_days, last_30_days, this_month, last_month]
          description: Time period for the report
        - name: report_type
          in: query
          schema:
            type: string
            enum: [Source, Medium, Campaign, Term]
            default: Source
          description: How to group the data
        - name: account_id
          in: query
          schema:
            type: string
          description: Sealmetrics account ID
        - name: utm_source
          in: query
          schema:
            type: string
          description: Filter by traffic source
        - name: limit
          in: query
          schema:
            type: integer
            default: 100
          description: Maximum results to return
      responses:
        '200':
          description: Traffic data
  /api/conversions:
    get:
      operationId: getConversions
      summary: Get conversion and sales data
      parameters:
        - name: date_range
          in: query
          required: true
          schema:
            type: string
        - name: account_id
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Conversion data
  /api/microconversions:
    get:
      operationId: getMicroconversions
      summary: Get microconversion events (add-to-cart, signups, etc.)
      parameters:
        - name: date_range
          in: query
          required: true
          schema:
            type: string
        - name: account_id
          in: query
          schema:
            type: string
        - name: label
          in: query
          schema:
            type: string
          description: Filter by event label
      responses:
        '200':
          description: Microconversion data
```

### Authentication Setup

In your Custom GPT:
1. Go to **Configure** → **Actions** → **Authentication**
2. Select **API Key**
3. Set **Auth Type**: Custom Header
4. Set **Header Name**: `X-API-Key`
5. Enter your Sealmetrics API token

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SEALMETRICS_API_TOKEN` | Yes* | Your Sealmetrics API token (recommended) |
| `SEALMETRICS_ACCOUNT_ID` | No | Default account ID for queries |
| `SEALMETRICS_EMAIL` | Yes* | Email for login (alternative to token) |
| `SEALMETRICS_PASSWORD` | Yes* | Password for login (alternative to token) |

*Either `SEALMETRICS_API_TOKEN` or both `SEALMETRICS_EMAIL` and `SEALMETRICS_PASSWORD` are required.

---

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

---

## Query Parameters Reference

### Date Ranges

| Value | Description |
|-------|-------------|
| `yesterday` | Previous day |
| `today` | Current day |
| `last_7_days` | Last 7 days |
| `last_30_days` | Last 30 days |
| `this_month` | Current month |
| `last_month` | Previous month |
| `YYYYMMDD,YYYYMMDD` | Custom date range |

### Report Types

| Value | Description |
|-------|-------------|
| `Source` | Group by traffic source (google-ads, facebook, etc.) |
| `Medium` | Group by medium (cpc, organic, email, etc.) |
| `Campaign` | Group by campaign name |
| `Term` | Group by search term |

---

## Example Queries

Once configured, you can ask AI assistants:

- "How much traffic did we get from Google Ads yesterday?"
- "Show me conversions from organic search this month"
- "What's our ROAS evolution for the last 30 days?"
- "Which landing pages are performing best?"
- "Generate a conversion pixel for newsletter signups"

---

## Getting Your API Token

1. Log in to your Sealmetrics dashboard
2. Go to **Settings** → **API**
3. Generate a new API token
4. Copy the token to your configuration

---

## Support

- Documentation: https://sealmetrics.com/docs
- Issues: https://github.com/sealmetrics/mcp-server/issues
- Email: support@sealmetrics.com

## License

MIT License - see LICENSE file for details.
