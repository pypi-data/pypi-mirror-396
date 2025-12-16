"""
Sealmetrics MCP Server

A Model Context Protocol server that provides access to Sealmetrics analytics data.
Allows AI assistants to query traffic, conversions, sales, and generate tracking pixels.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import httpx
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
import mcp.server.stdio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sealmetrics-mcp")


# Sealmetrics API Configuration
API_BASE_URL = "https://app.sealmetrics.com/api"
TOKEN_CACHE = {"token": None, "expires_at": None}


class SealmetricsError(Exception):
    """Base exception for Sealmetrics-related errors"""
    pass


class AuthenticationError(SealmetricsError):
    """Raised when authentication fails"""
    pass


class RateLimitError(SealmetricsError):
    """Raised when rate limit is exceeded"""
    pass


class APIError(SealmetricsError):
    """Raised when API request fails"""
    pass


class SealmetricsClient:
    """Client for interacting with the Sealmetrics API"""

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize Sealmetrics client with either:
        - email + password (will login to get token)
        - api_token (direct API token from dashboard)
        """
        self.email = email
        self.password = password
        self.api_token = api_token
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def _get_token(self) -> str:
        """Get or refresh authentication token"""
        # If we have a direct API token, use it
        if self.api_token:
            return self.api_token

        # Otherwise, use email/password login
        now = datetime.now()

        # Check if we have a valid cached token
        if TOKEN_CACHE["token"] and TOKEN_CACHE["expires_at"]:
            if now < TOKEN_CACHE["expires_at"]:
                return TOKEN_CACHE["token"]

        # Login to get new token
        try:
            response = await self.http_client.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": self.email, "password": self.password},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            data = response.json()
            token = data["access_token"]
            expires_str = data["expires_at"]

            # Parse expiration and cache token
            expires_at = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            TOKEN_CACHE["token"] = token
            TOKEN_CACHE["expires_at"] = expires_at

            logger.info("Successfully authenticated with Sealmetrics API")
            return token

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Authentication failed: Invalid email or password. "
                    "Please check your SEALMETRICS_EMAIL and SEALMETRICS_PASSWORD credentials."
                )
            elif e.response.status_code == 429:
                raise ValueError(
                    "Rate limit exceeded. Please wait a moment before trying again. "
                    "Check your Sealmetrics plan for API rate limits."
                )
            else:
                raise ValueError(f"Authentication failed with status {e.response.status_code}: {e.response.text}")
        except httpx.TimeoutException:
            raise ValueError(
                "Authentication request timed out. Please check your internet connection "
                "and try again."
            )
        except httpx.NetworkError as e:
            raise ValueError(
                f"Network error during authentication: {str(e)}. "
                "Please check your internet connection and firewall settings."
            )
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated API request with comprehensive error handling"""
        try:
            token = await self._get_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Connection": "keep-alive",
                "Accept-Encoding": "gzip, deflate, br"
            }

            response = await self.http_client.get(
                f"{API_BASE_URL}{endpoint}",
                params=params,
                headers=headers
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "API request unauthorized. Your authentication token may have expired or is invalid. "
                    "Please check your SEALMETRICS_API_TOKEN or login credentials."
                )
            elif e.response.status_code == 403:
                raise ValueError(
                    "Access forbidden. Your account may not have permission to access this endpoint. "
                    "Please check your Sealmetrics plan and account permissions."
                )
            elif e.response.status_code == 404:
                raise ValueError(
                    f"API endpoint not found: {endpoint}. "
                    "This may indicate an invalid account ID or the endpoint is not available."
                )
            elif e.response.status_code == 429:
                raise ValueError(
                    "Rate limit exceeded. Your Sealmetrics plan has reached its API request limit. "
                    "Please wait before making more requests or upgrade your plan."
                )
            elif e.response.status_code >= 500:
                raise ValueError(
                    f"Sealmetrics server error (status {e.response.status_code}). "
                    "The Sealmetrics API may be experiencing issues. Please try again later."
                )
            else:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("message", error_data.get("error", ""))
                except:
                    error_detail = e.response.text[:200]

                raise ValueError(
                    f"API request failed with status {e.response.status_code}: {error_detail}"
                )

        except httpx.TimeoutException:
            raise ValueError(
                f"Request to {endpoint} timed out after 30 seconds. "
                "The Sealmetrics API may be slow or unavailable. Please try again."
            )

        except httpx.NetworkError as e:
            raise ValueError(
                f"Network error accessing Sealmetrics API: {str(e)}. "
                "Please check your internet connection and firewall settings."
            )

        except ValueError:
            # Re-raise ValueError exceptions (our custom error messages)
            raise

        except Exception as e:
            logger.error(f"Unexpected error making API request to {endpoint}: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}")

    async def get_accounts(self) -> Dict[str, str]:
        """Get list of accounts"""
        result = await self._make_request("/auth/accounts", {})
        return result.get("data", {})

    async def get_acquisition_data(
        self,
        account_id: str,
        date_range: str,
        report_type: str = "Source",
        skip: int = 0,
        limit: int = 100,
        auto_paginate: bool = False,
        **filters
    ) -> List[Dict[str, Any]]:
        """Get acquisition/traffic source data"""
        # Limit validation
        if limit > 1000:
            limit = 1000
            logger.warning("Limit exceeds maximum of 1000, setting to 1000")

        if not auto_paginate:
            params = {
                "account_id": account_id,
                "report_type": report_type,
                "date_range": date_range,
                "skip": skip,
                "limit": limit,
                **filters
            }
            result = await self._make_request("/report/acquisition", params)
            return result.get("data", [])

        # Auto-pagination: fetch all results
        all_data = []
        current_skip = 0
        batch_size = min(limit, 1000)

        while True:
            params = {
                "account_id": account_id,
                "report_type": report_type,
                "date_range": date_range,
                "skip": current_skip,
                "limit": batch_size,
                **filters
            }
            result = await self._make_request("/report/acquisition", params)
            batch = result.get("data", [])

            if not batch:
                break

            all_data.extend(batch)

            # If we got less than the batch size, we've reached the end
            if len(batch) < batch_size:
                break

            current_skip += batch_size

            # Safety limit: don't fetch more than 10,000 results
            if len(all_data) >= 10000:
                logger.warning("Auto-pagination reached safety limit of 10,000 results")
                break

        return all_data

    async def get_conversions(
        self,
        account_id: str,
        date_range: str,
        skip: int = 0,
        limit: int = 100,
        auto_paginate: bool = False,
        **filters
    ) -> List[Dict[str, Any]]:
        """Get conversions data"""
        # Limit validation
        if limit > 1000:
            limit = 1000
            logger.warning("Limit exceeds maximum of 1000, setting to 1000")

        if not auto_paginate:
            params = {
                "account_id": account_id,
                "date_range": date_range,
                "skip": skip,
                "limit": limit,
                **filters
            }
            result = await self._make_request("/report/conversions", params)
            return result.get("data", [])

        # Auto-pagination: fetch all results
        all_data = []
        current_skip = 0
        batch_size = min(limit, 1000)

        while True:
            params = {
                "account_id": account_id,
                "date_range": date_range,
                "skip": current_skip,
                "limit": batch_size,
                **filters
            }
            result = await self._make_request("/report/conversions", params)
            batch = result.get("data", [])

            if not batch:
                break

            all_data.extend(batch)

            if len(batch) < batch_size:
                break

            current_skip += batch_size

            if len(all_data) >= 10000:
                logger.warning("Auto-pagination reached safety limit of 10,000 results")
                break

        return all_data

    async def get_microconversions(
        self,
        account_id: str,
        date_range: str,
        skip: int = 0,
        limit: int = 100,
        auto_paginate: bool = False,
        **filters
    ) -> List[Dict[str, Any]]:
        """Get microconversions data"""
        # Limit validation
        if limit > 1000:
            limit = 1000
            logger.warning("Limit exceeds maximum of 1000, setting to 1000")

        if not auto_paginate:
            params = {
                "account_id": account_id,
                "date_range": date_range,
                "skip": skip,
                "limit": limit,
                **filters
            }
            result = await self._make_request("/report/microconversions", params)
            return result.get("data", [])

        # Auto-pagination: fetch all results
        all_data = []
        current_skip = 0
        batch_size = min(limit, 1000)

        while True:
            params = {
                "account_id": account_id,
                "date_range": date_range,
                "skip": current_skip,
                "limit": batch_size,
                **filters
            }
            result = await self._make_request("/report/microconversions", params)
            batch = result.get("data", [])

            if not batch:
                break

            all_data.extend(batch)

            if len(batch) < batch_size:
                break

            current_skip += batch_size

            if len(all_data) >= 10000:
                logger.warning("Auto-pagination reached safety limit of 10,000 results")
                break

        return all_data

    async def get_pages(
        self,
        account_id: str,
        date_range: str,
        skip: int = 0,
        limit: int = 100,
        auto_paginate: bool = False,
        show_utms: bool = False,
        **filters
    ) -> List[Dict[str, Any]]:
        """Get pages performance data"""
        # Limit validation
        if limit > 1000:
            limit = 1000
            logger.warning("Limit exceeds maximum of 1000, setting to 1000")

        if not auto_paginate:
            params = {
                "account_id": account_id,
                "date_range": date_range,
                "skip": skip,
                "limit": limit,
                "show_utms": str(show_utms).lower(),
                **filters
            }
            result = await self._make_request("/report/pages", params)
            return result.get("data", [])

        # Auto-pagination: fetch all results
        all_data = []
        current_skip = 0
        batch_size = min(limit, 1000)

        while True:
            params = {
                "account_id": account_id,
                "date_range": date_range,
                "skip": current_skip,
                "limit": batch_size,
                "show_utms": str(show_utms).lower(),
                **filters
            }
            result = await self._make_request("/report/pages", params)
            batch = result.get("data", [])

            if not batch:
                break

            all_data.extend(batch)

            if len(batch) < batch_size:
                break

            current_skip += batch_size

            if len(all_data) >= 10000:
                logger.warning("Auto-pagination reached safety limit of 10,000 results")
                break

        return all_data

    async def get_funnel(
        self,
        account_id: str,
        date_range: str,
        report_type: str = "Source",
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Dict[str, Any]]:
        """Get funnel data"""
        params = {
            "account_id": account_id,
            "report_type": report_type,
            "date_range": date_range,
            "skip": skip,
            "limit": limit,
            **filters
        }

        result = await self._make_request("/report/funnel", params)
        return result.get("data", [])

    async def get_roas_evolution(
        self,
        account_id: str,
        date_range: str,
        time_unit: str = "daily",
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Dict[str, Any]]:
        """Get ROAS evolution data"""
        params = {
            "account_id": account_id,
            "date_range": date_range,
            "time_unit": time_unit,
            "skip": skip,
            "limit": limit,
            **filters
        }

        result = await self._make_request("/report/roas-evolution", params)
        return result.get("data", [])

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


def validate_date_range(date_range: str) -> bool:
    """
    Validate date range format.

    Accepts:
    - Predefined ranges: "today", "yesterday", "last_7_days", etc.
    - Custom format: "YYYYMMDD,YYYYMMDD"

    Returns True if valid, raises ValueError if invalid.
    """
    # Predefined valid ranges
    valid_ranges = {
        "today", "yesterday",
        "last_7_days", "last_14_days", "last_30_days",
        "last_week", "last_month", "this_month",
        "this_year", "last_year"
    }

    if date_range in valid_ranges:
        return True

    # Check custom format: YYYYMMDD,YYYYMMDD
    if "," in date_range:
        parts = date_range.split(",")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid date range format: '{date_range}'. "
                "Custom ranges must be in format: YYYYMMDD,YYYYMMDD (e.g., '20240101,20240131')"
            )

        start_date, end_date = parts

        # Validate each date is 8 digits
        if not (start_date.isdigit() and len(start_date) == 8):
            raise ValueError(
                f"Invalid start date: '{start_date}'. Must be 8 digits in YYYYMMDD format (e.g., '20240101')"
            )

        if not (end_date.isdigit() and len(end_date) == 8):
            raise ValueError(
                f"Invalid end date: '{end_date}'. Must be 8 digits in YYYYMMDD format (e.g., '20240131')"
            )

        # Validate date values
        try:
            start = datetime.strptime(start_date, "%Y%m%d")
            end = datetime.strptime(end_date, "%Y%m%d")

            if start > end:
                raise ValueError(
                    f"Invalid date range: start date ({start_date}) is after end date ({end_date})"
                )

            # Check if range is too large (more than 1 year)
            if (end - start).days > 365:
                logger.warning(f"Large date range requested: {(end - start).days} days")

            return True

        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError(
                    f"Invalid date format in range: '{date_range}'. "
                    "Dates must be valid calendar dates (e.g., '20240101' not '20240199')"
                )
            raise

    # If we get here, format is invalid
    raise ValueError(
        f"Invalid date range: '{date_range}'. "
        "Use predefined ranges (e.g., 'yesterday', 'last_7_days') "
        "or custom format YYYYMMDD,YYYYMMDD (e.g., '20240101,20240131')"
    )


def parse_date_query(query: str) -> str:
    """
    Parse natural language date queries into Sealmetrics date_range format.

    Examples:
    - "yesterday" -> "yesterday"
    - "last week" -> "last_7_days"
    - "this month" -> "this_month"
    - "last month" -> "last_month"
    """
    query = query.lower().strip()

    # Map common queries to Sealmetrics date ranges
    mappings = {
        "yesterday": "yesterday",
        "today": "today",
        "last 7 days": "last_7_days",
        "last week": "last_7_days",
        "past week": "last_7_days",
        "last 14 days": "last_14_days",
        "last 2 weeks": "last_14_days",
        "last 30 days": "last_30_days",
        "last month": "last_month",
        "this month": "this_month",
        "this year": "this_year",
        "last year": "last_year",
    }

    for key, value in mappings.items():
        if key in query:
            return value

    # Default to last 7 days if no match
    return "last_7_days"


def generate_conversion_pixel(
    account_id: str,
    event_type: str = "conversion",
    label: Optional[str] = None,
    value: Optional[float] = None,
    ignore_pageview: bool = False,
    properties: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a Sealmetrics tracking pixel for conversions or microconversions.

    Args:
        account_id: Your Sealmetrics account ID
        event_type: "conversion" or "microconversion"
        label: Event label (e.g., "sales", "add-to-cart", "newsletter-signup")
        value: Monetary value for the event
        ignore_pageview: Set to True to avoid counting additional pageview
        properties: Optional custom event properties

    Returns:
        HTML snippet ready for Google Tag Manager or direct website embedding
    """
    config_lines = [
        f'  oSm.account = "{account_id}";',
        f'  oSm.event = "{event_type}";'
    ]

    if label:
        config_lines.append(f'  oSm.label = "{label}";')

    if value is not None:
        config_lines.append(f'  oSm.value = {value};')

    if ignore_pageview:
        config_lines.append('  oSm.ignore_pageview = 1;')

    if properties:
        for key, val in properties.items():
            if isinstance(val, str):
                config_lines.append(f'  oSm.{key} = "{val}";')
            else:
                config_lines.append(f'  oSm.{key} = {val};')

    config = '\n'.join(config_lines)

    pixel = f'''<script>
  /* SealMetrics Tracker Code */
  var oSm = window.oSm || {{}};
{config}

  !(function (e) {{
    var t = "//app.sealmetrics.com/tag/tracker";
    window.oSm = oSm;
    if (window.smTrackerLoaded) sm.tracker.track(e.event);
    else
      Promise.all([
        new Promise(function (e) {{
          var n = document.createElement("script");
          n.src = t;
          n.async = !0;
          n.onload = function () {{
            e(t);
          }};
          document.getElementsByTagName("head")[0].appendChild(n);
        }}),
      ]).then(function () {{
        sm.tracker.track(e.event);
      }});
  }})(oSm);
</script>'''

    return pixel


def format_acquisition_summary(
    data: List[Dict[str, Any]],
    source_filter: Optional[str] = None,
    auto_paginated: bool = False,
    total_results: int = 0
) -> str:
    """Format acquisition data into readable summary with enhanced visuals"""
    if not data:
        return (
            "## 📊 Traffic Summary\n\n"
            "╔════════════════════════════════════════╗\n"
            "║   No acquisition data found            ║\n"
            "╚════════════════════════════════════════╝\n\n"
            "**Possible reasons:**\n"
            "- No traffic during this period\n"
            "- Filters are too restrictive\n"
            "- Tracking not yet active"
        )

    total_clicks = sum(item.get("clicks", 0) for item in data)
    total_conversions = sum(item.get("conversions", 0) for item in data)
    total_revenue = sum(item.get("revenue", 0) for item in data)

    summary = "## 📊 Traffic Summary\n\n"

    # Add pagination info if applicable
    if auto_paginated:
        summary += f"*Auto-paginated: Showing all {total_results:,} results*\n\n"
    elif total_results > 0:
        summary += f"*Showing {total_results:,} result(s)*\n\n"

    summary += "╔═══════════════════════════════════════════════════════════╗\n"
    summary += "║                     KEY METRICS                           ║\n"
    summary += "╠═══════════════════════════════════════════════════════════╣\n"
    summary += f"║ 👆 Total Clicks          │ {total_clicks:>27,} ║\n"
    summary += f"║ 🎯 Total Conversions     │ {total_conversions:>27,} ║\n"
    summary += f"║ 💰 Total Revenue         │ ${total_revenue:>26,.2f} ║\n"

    if total_clicks > 0:
        conv_rate = (total_conversions / total_clicks) * 100
        avg_revenue_per_click = total_revenue / total_clicks if total_clicks > 0 else 0
        summary += "╠═══════════════════════════════════════════════════════════╣\n"
        summary += f"║ 📈 Conversion Rate       │ {conv_rate:>26.2f}% ║\n"
        summary += f"║ 💵 Revenue per Click     │ ${avg_revenue_per_click:>26.2f} ║\n"

    if total_conversions > 0:
        avg_order_value = total_revenue / total_conversions
        summary += f"║ 🛒 Average Order Value   │ ${avg_order_value:>26.2f} ║\n"

    summary += "╚═══════════════════════════════════════════════════════════╝\n\n"
    summary += "---\n\n"
    summary += "### 🏆 Top Traffic Sources\n\n"

    # Sort by clicks and show top 10
    sorted_data = sorted(data, key=lambda x: x.get("clicks", 0), reverse=True)[:10]

    if len(data) > 10:
        summary += f"*Showing top 10 of {len(data)} sources*\n\n"

    for idx, item in enumerate(sorted_data, 1):
        source = item.get("name", item.get("utm_source", "Unknown"))
        clicks = item.get("clicks", 0)
        conversions = item.get("conversions", 0)
        revenue = item.get("revenue", 0)

        # Calculate source metrics
        source_conv_rate = (conversions / clicks * 100) if clicks > 0 else 0

        # Add medal emoji for top 3
        medal = ""
        if idx == 1:
            medal = "🥇 "
        elif idx == 2:
            medal = "🥈 "
        elif idx == 3:
            medal = "🥉 "

        summary += f"**{medal}{idx}. {source}**\n"
        summary += f"```\n"
        summary += f"Clicks:       {clicks:>10,}\n"
        summary += f"Conversions:  {conversions:>10,} ({source_conv_rate:.2f}%)\n"
        summary += f"Revenue:      ${revenue:>10,.2f}\n"
        summary += f"```\n\n"

    return summary


def format_conversions_summary(
    data: List[Dict[str, Any]],
    auto_paginated: bool = False,
    total_results: int = 0
) -> str:
    """Format conversions data into readable summary"""
    if not data:
        return (
            "## 💰 Conversions Summary\n\n"
            "╔════════════════════════════════════════╗\n"
            "║   No conversions found                 ║\n"
            "╚════════════════════════════════════════╝\n\n"
        )

    total_conversions = len(data)
    total_revenue = sum(item.get("amount", 0) for item in data)

    summary = "## 💰 Conversions Summary\n\n"

    # Add pagination info if applicable
    if auto_paginated:
        summary += f"*Auto-paginated: Showing all {total_results:,} results*\n\n"
    elif total_results > 0:
        summary += f"*Showing {total_results:,} result(s)*\n\n"

    summary += "╔═══════════════════════════════════════════════════════════╗\n"
    summary += "║                   CONVERSION METRICS                      ║\n"
    summary += "╠═══════════════════════════════════════════════════════════╣\n"
    summary += f"║ 🎯 Total Conversions     │ {total_conversions:>27,} ║\n"
    summary += f"║ 💰 Total Revenue         │ ${total_revenue:>26,.2f} ║\n"

    if total_conversions > 0:
        avg_order_value = total_revenue / total_conversions
        summary += f"║ 🛒 Average Order Value   │ ${avg_order_value:>26.2f} ║\n"

    summary += "╚═══════════════════════════════════════════════════════════╝\n\n"

    # Group by source
    by_source = {}
    for item in data:
        source = item.get("utm_source", "Direct")
        if source not in by_source:
            by_source[source] = {"count": 0, "revenue": 0}
        by_source[source]["count"] += 1
        by_source[source]["revenue"] += item.get("amount", 0)

    summary += "---\n\n"
    summary += "### 📊 By Traffic Source\n\n"

    sorted_sources = sorted(by_source.items(), key=lambda x: x[1]["revenue"], reverse=True)[:10]

    if len(by_source) > 10:
        summary += f"*Showing top 10 of {len(by_source)} sources*\n\n"

    for idx, (source, stats) in enumerate(sorted_sources, 1):
        summary += f"**{idx}. {source}**\n"
        summary += f"```\n"
        summary += f"Conversions:  {stats['count']:>10,}\n"
        summary += f"Revenue:      ${stats['revenue']:>10,.2f}\n"
        summary += f"```\n\n"

    return summary


def format_microconversions_summary(
    data: List[Dict[str, Any]],
    label_filter: Optional[str] = None,
    auto_paginated: bool = False,
    total_results: int = 0
) -> str:
    """Format microconversions data into readable summary"""
    if not data:
        return (
            "## 🎯 Microconversions Summary\n\n"
            "╔════════════════════════════════════════╗\n"
            "║   No microconversions found            ║\n"
            "╚════════════════════════════════════════╝\n\n"
        )

    # Group by label
    by_label = {}
    for item in data:
        label = item.get("label", "unknown")
        if label not in by_label:
            by_label[label] = 0
        by_label[label] += 1

    summary = "## 🎯 Microconversions Summary\n\n"

    # Add pagination info if applicable
    if auto_paginated:
        summary += f"*Auto-paginated: Showing all {total_results:,} results*\n\n"
    elif total_results > 0:
        summary += f"*Showing {total_results:,} result(s)*\n\n"

    summary += "╔═══════════════════════════════════════════════════════════╗\n"
    summary += "║              MICROCONVERSION METRICS                      ║\n"
    summary += "╠═══════════════════════════════════════════════════════════╣\n"
    summary += f"║ 📊 Total Events          │ {len(data):>27,} ║\n"
    summary += f"║ 🏷️  Unique Event Types   │ {len(by_label):>27,} ║\n"
    summary += "╚═══════════════════════════════════════════════════════════╝\n\n"

    summary += "---\n\n"
    summary += "### 📈 By Event Type\n\n"

    sorted_labels = sorted(by_label.items(), key=lambda x: x[1], reverse=True)

    for idx, (label, count) in enumerate(sorted_labels, 1):
        percentage = (count / len(data) * 100) if len(data) > 0 else 0
        summary += f"**{idx}. {label}**\n"
        summary += f"```\n"
        summary += f"Count:        {count:>10,}\n"
        summary += f"Percentage:   {percentage:>10.1f}%\n"
        summary += f"```\n\n"

    return summary


# Initialize MCP server
app = Server("sealmetrics")

# Initialize Sealmetrics client (will be set from environment variables)
client: Optional[SealmetricsClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Sealmetrics tools"""
    return [
        Tool(
            name="get_accounts",
            description="Get list of Sealmetrics accounts available to the authenticated user",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_traffic_data",
            description="Get traffic/acquisition data from Sealmetrics. Answers questions like 'How much traffic from SEO yesterday?' or 'Show me Google Ads performance this month'",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range: 'yesterday', 'today', 'last_7_days', 'last_30_days', 'this_month', 'last_month', or 'YYYYMMDD,YYYYMMDD'"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Report grouping: 'Source', 'Medium', 'Campaign', 'Term'",
                        "default": "Source"
                    },
                    "utm_source": {
                        "type": "string",
                        "description": "Filter by specific source (e.g., 'google', 'facebook', 'seo')"
                    },
                    "utm_medium": {
                        "type": "string",
                        "description": "Filter by medium (e.g., 'organic', 'cpc', 'email')"
                    },
                    "utm_campaign": {
                        "type": "string",
                        "description": "Filter by campaign name"
                    },
                    "country": {
                        "type": "string",
                        "description": "Filter by country code (e.g., 'us', 'es')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100, max: 1000)",
                        "default": 100
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    },
                    "auto_paginate": {
                        "type": "boolean",
                        "description": "Automatically fetch all results across multiple pages (default: false)",
                        "default": False
                    }
                },
                "required": ["date_range"]
            }
        ),
        Tool(
            name="get_conversions",
            description="Get conversion/sales data from Sealmetrics. Answers questions like 'How many sales this month?' or 'Show conversions from Google Ads yesterday'",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range: 'yesterday', 'today', 'last_7_days', 'last_30_days', 'this_month', 'last_month', or 'YYYYMMDD,YYYYMMDD'"
                    },
                    "utm_source": {
                        "type": "string",
                        "description": "Filter by specific source (e.g., 'google', 'facebook')"
                    },
                    "utm_medium": {
                        "type": "string",
                        "description": "Filter by medium (e.g., 'organic', 'cpc')"
                    },
                    "utm_campaign": {
                        "type": "string",
                        "description": "Filter by campaign name"
                    },
                    "country": {
                        "type": "string",
                        "description": "Filter by country code"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100, max: 1000)",
                        "default": 100
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    },
                    "auto_paginate": {
                        "type": "boolean",
                        "description": "Automatically fetch all results across multiple pages (default: false)",
                        "default": False
                    }
                },
                "required": ["date_range"]
            }
        ),
        Tool(
            name="get_microconversions",
            description="Get microconversion data (add-to-cart, signups, etc.) from Sealmetrics. Answers questions like 'How many add to carts from Google Ads yesterday?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range: 'yesterday', 'today', 'last_7_days', 'last_30_days', 'this_month', 'last_month', or 'YYYYMMDD,YYYYMMDD'"
                    },
                    "label": {
                        "type": "string",
                        "description": "Filter by microconversion label (e.g., 'add-to-cart', 'newsletter-signup')"
                    },
                    "utm_source": {
                        "type": "string",
                        "description": "Filter by specific source"
                    },
                    "utm_medium": {
                        "type": "string",
                        "description": "Filter by medium"
                    },
                    "country": {
                        "type": "string",
                        "description": "Filter by country code"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100, max: 1000)",
                        "default": 100
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    },
                    "auto_paginate": {
                        "type": "boolean",
                        "description": "Automatically fetch all results across multiple pages (default: false)",
                        "default": False
                    }
                },
                "required": ["account_id", "date_range"]
            }
        ),
        Tool(
            name="get_funnel_data",
            description="Get funnel analysis showing progression through conversion stages",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Report grouping: 'Source', 'Medium', 'Campaign'",
                        "default": "Source"
                    }
                },
                "required": ["account_id", "date_range"]
            }
        ),
        Tool(
            name="get_roas_evolution",
            description="Get ROAS (Return on Ad Spend) evolution over time with revenue, conversions, and clicks",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range"
                    },
                    "time_unit": {
                        "type": "string",
                        "description": "Time grouping: 'daily', 'weekly', 'monthly'",
                        "default": "daily"
                    },
                    "utm_source": {
                        "type": "string",
                        "description": "Filter by source"
                    },
                    "utm_medium": {
                        "type": "string",
                        "description": "Filter by medium"
                    }
                },
                "required": ["account_id", "date_range"]
            }
        ),
        Tool(
            name="get_pages_performance",
            description="Get page performance metrics including views and entry pages. Can filter by content groups to analyze specific sections of your site (e.g., 'Blog Content', 'Product Catalog', 'Support Pages')",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range: 'yesterday', 'today', 'last_7_days', 'last_30_days', 'this_month', 'last_month', or 'YYYYMMDD,YYYYMMDD'"
                    },
                    "content_grouping": {
                        "type": "string",
                        "description": "Filter by content group name (e.g., 'Blog Content', 'Product Catalog', 'Support Pages', 'Purchase Flow')"
                    },
                    "utm_source": {
                        "type": "string",
                        "description": "Filter by traffic source (e.g., 'google', 'facebook')"
                    },
                    "utm_medium": {
                        "type": "string",
                        "description": "Filter by medium (e.g., 'organic', 'cpc')"
                    },
                    "country": {
                        "type": "string",
                        "description": "Filter by country code (e.g., 'us', 'es')"
                    },
                    "show_utms": {
                        "type": "boolean",
                        "description": "Include UTM breakdown in results",
                        "default": False
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100, max: 1000)",
                        "default": 100
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    },
                    "auto_paginate": {
                        "type": "boolean",
                        "description": "Automatically fetch all results across multiple pages (default: false)",
                        "default": False
                    }
                },
                "required": ["date_range"]
            }
        ),
        Tool(
            name="generate_conversion_pixel",
            description="Generate a Sealmetrics tracking pixel for conversions or microconversions, ready for Google Tag Manager",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Your Sealmetrics account ID (optional if SEALMETRICS_ACCOUNT_ID is set)"
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Event type: 'conversion' or 'microconversion'",
                        "enum": ["conversion", "microconversion"],
                        "default": "conversion"
                    },
                    "label": {
                        "type": "string",
                        "description": "Event label (e.g., 'sales', 'add-to-cart', 'newsletter-signup')"
                    },
                    "value": {
                        "type": "number",
                        "description": "Monetary value for the event (optional)"
                    },
                    "ignore_pageview": {
                        "type": "boolean",
                        "description": "Set to true to avoid counting an additional pageview (use when tracking button clicks on already-tracked pages)",
                        "default": False
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global client

    if client is None:
        return [TextContent(
            type="text",
            text="Error: Sealmetrics client not initialized. Please set SEALMETRICS_API_TOKEN or SEALMETRICS_EMAIL/PASSWORD environment variables."
        )]

    # Get default account ID from environment if not provided in arguments
    default_account_id = os.getenv("SEALMETRICS_ACCOUNT_ID")

    # Helper function to get valid account ID
    def get_account_id(args):
        """Get valid account ID, filtering out invalid values"""
        provided_id = args.get("account_id")

        # If provided ID is invalid (like "sealmetrics"), use default
        if provided_id and len(provided_id) < 20:  # Account IDs are long alphanumeric
            return default_account_id

        # Otherwise use provided or fall back to default
        return provided_id or default_account_id

    try:
        if name == "get_accounts":
            try:
                accounts = await client.get_accounts()
                result = "## Available Sealmetrics Accounts\n\n"

                # If no accounts returned but we have a default account ID, show that
                if not accounts and default_account_id:
                    result += f"**Default Account**\n"
                    result += f"  - ID: `{default_account_id}`\n\n"
                    result += "Note: Using configured account ID from environment.\n"
                else:
                    for account_id, account_name in accounts.items():
                        result += f"**{account_name}**\n"
                        result += f"  - ID: `{account_id}`\n\n"

                return [TextContent(type="text", text=result)]

            except ValueError as e:
                logger.error(f"Error fetching accounts: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching Accounts\n\n{str(e)}\n\n"
                         "**Troubleshooting:**\n"
                         "- Verify your API credentials are correct\n"
                         "- Check your internet connection\n"
                         "- Ensure your Sealmetrics account has API access enabled"
                )]

        elif name == "get_traffic_data":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="## Error: Missing Account ID\n\n"
                         "No account_id was provided and SEALMETRICS_ACCOUNT_ID is not set in your environment.\n\n"
                         "**To fix this:**\n"
                         "1. Add `SEALMETRICS_ACCOUNT_ID` to your Claude Desktop config, or\n"
                         "2. Provide the account_id parameter when calling this tool\n\n"
                         "Use the `get_accounts` tool to find your account ID."
                )]

            # Validate date range
            try:
                validate_date_range(arguments["date_range"])
            except ValueError as e:
                return [TextContent(type="text", text=f"## Error: Invalid Date Range\n\n{str(e)}")]

            try:
                data = await client.get_acquisition_data(
                    account_id=account_id,
                    date_range=arguments["date_range"],
                    report_type=arguments.get("report_type", "Source"),
                    limit=arguments.get("limit", 100),
                    skip=arguments.get("skip", 0),
                    auto_paginate=arguments.get("auto_paginate", False),
                    utm_source=arguments.get("utm_source"),
                    utm_medium=arguments.get("utm_medium"),
                    utm_campaign=arguments.get("utm_campaign"),
                    country=arguments.get("country")
                )

                summary = format_acquisition_summary(
                    data,
                    arguments.get("utm_source"),
                    auto_paginated=arguments.get("auto_paginate", False),
                    total_results=len(data)
                )
                return [TextContent(type="text", text=summary)]

            except ValueError as e:
                logger.error(f"Error fetching traffic data: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching Traffic Data\n\n{str(e)}"
                )]

        elif name == "get_conversions":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="## Error: Missing Account ID\n\n"
                         "No account_id was provided and SEALMETRICS_ACCOUNT_ID is not set in your environment.\n\n"
                         "Use the `get_accounts` tool to find your account ID."
                )]

            # Validate date range
            try:
                validate_date_range(arguments["date_range"])
            except ValueError as e:
                return [TextContent(type="text", text=f"## Error: Invalid Date Range\n\n{str(e)}")]

            try:
                data = await client.get_conversions(
                    account_id=account_id,
                    date_range=arguments["date_range"],
                    limit=arguments.get("limit", 100),
                    skip=arguments.get("skip", 0),
                    auto_paginate=arguments.get("auto_paginate", False),
                    utm_source=arguments.get("utm_source"),
                    utm_medium=arguments.get("utm_medium"),
                    utm_campaign=arguments.get("utm_campaign"),
                    country=arguments.get("country")
                )

                summary = format_conversions_summary(
                    data,
                    auto_paginated=arguments.get("auto_paginate", False),
                    total_results=len(data)
                )
                return [TextContent(type="text", text=summary)]

            except ValueError as e:
                logger.error(f"Error fetching conversions: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching Conversions\n\n{str(e)}"
                )]

        elif name == "get_microconversions":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="## Error: Missing Account ID\n\n"
                         "No account_id was provided and SEALMETRICS_ACCOUNT_ID is not set in your environment.\n\n"
                         "Use the `get_accounts` tool to find your account ID."
                )]

            # Validate date range
            try:
                validate_date_range(arguments["date_range"])
            except ValueError as e:
                return [TextContent(type="text", text=f"## Error: Invalid Date Range\n\n{str(e)}")]

            try:
                # Handle label filter specially
                filters = {
                    "utm_source": arguments.get("utm_source"),
                    "utm_medium": arguments.get("utm_medium"),
                    "country": arguments.get("country")
                }

                data = await client.get_microconversions(
                    account_id=account_id,
                    date_range=arguments["date_range"],
                    limit=arguments.get("limit", 100),
                    skip=arguments.get("skip", 0),
                    auto_paginate=arguments.get("auto_paginate", False),
                    **{k: v for k, v in filters.items() if v is not None}
                )

                # Filter by label in post-processing if specified
                label_filter = arguments.get("label")
                if label_filter:
                    data = [item for item in data if item.get("label") == label_filter]

                summary = format_microconversions_summary(
                    data,
                    label_filter,
                    auto_paginated=arguments.get("auto_paginate", False),
                    total_results=len(data)
                )
                return [TextContent(type="text", text=summary)]

            except ValueError as e:
                logger.error(f"Error fetching microconversions: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching Microconversions\n\n{str(e)}"
                )]

        elif name == "get_funnel_data":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="## Error: Missing Account ID\n\n"
                         "No account_id was provided and SEALMETRICS_ACCOUNT_ID is not set in your environment.\n\n"
                         "Use the `get_accounts` tool to find your account ID."
                )]

            # Validate date range
            try:
                validate_date_range(arguments["date_range"])
            except ValueError as e:
                return [TextContent(type="text", text=f"## Error: Invalid Date Range\n\n{str(e)}")]

            try:
                data = await client.get_funnel(
                    account_id=account_id,
                    date_range=arguments["date_range"],
                    report_type=arguments.get("report_type", "Source")
                )

                result = "## Funnel Analysis\n\n"
                for item in data:
                    source = item.get("name", item.get("utm_source", "Unknown"))
                    result += f"### {source}\n\n"

                    for key, value in item.items():
                        if key not in ["name", "utm_source", "_id"]:
                            result += f"- **{key}:** {value:,}\n"
                    result += "\n"

                return [TextContent(type="text", text=result)]

            except ValueError as e:
                logger.error(f"Error fetching funnel data: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching Funnel Data\n\n{str(e)}"
                )]

        elif name == "get_roas_evolution":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="## Error: Missing Account ID\n\n"
                         "No account_id was provided and SEALMETRICS_ACCOUNT_ID is not set in your environment.\n\n"
                         "Use the `get_accounts` tool to find your account ID."
                )]

            # Validate date range
            try:
                validate_date_range(arguments["date_range"])
            except ValueError as e:
                return [TextContent(type="text", text=f"## Error: Invalid Date Range\n\n{str(e)}")]

            try:
                data = await client.get_roas_evolution(
                    account_id=account_id,
                    date_range=arguments["date_range"],
                    time_unit=arguments.get("time_unit", "daily"),
                    utm_source=arguments.get("utm_source"),
                    utm_medium=arguments.get("utm_medium")
                )

                result = "## ROAS Evolution\n\n"

                for item in data:
                    date = item.get("_id")
                    clicks = item.get("clicks", 0)
                    page_views = item.get("page_views", 0)
                    conversions = item.get("conversions", 0)
                    microconversions = item.get("microconversions", 0)
                    revenue = item.get("revenue", 0)

                    result += f"### {date}\n\n"
                    result += f"- **Clicks:** {clicks:,}\n"
                    result += f"- **Page Views:** {page_views:,}\n"
                    result += f"- **Conversions:** {conversions:,}\n"
                    result += f"- **Microconversions:** {microconversions:,}\n"
                    result += f"- **Revenue:** ${revenue:,.2f}\n\n"

                return [TextContent(type="text", text=result)]

            except ValueError as e:
                logger.error(f"Error fetching ROAS evolution: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching ROAS Evolution\n\n{str(e)}"
                )]

        elif name == "get_pages_performance":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="## Error: Missing Account ID\n\n"
                         "No account_id was provided and SEALMETRICS_ACCOUNT_ID is not set in your environment.\n\n"
                         "Use the `get_accounts` tool to find your account ID."
                )]

            # Validate date range
            try:
                validate_date_range(arguments["date_range"])
            except ValueError as e:
                return [TextContent(type="text", text=f"## Error: Invalid Date Range\n\n{str(e)}")]

            try:
                # Build filters dict
                filters = {}
                if arguments.get("content_grouping"):
                    filters["content_grouping"] = arguments["content_grouping"]
                if arguments.get("utm_source"):
                    filters["utm_source"] = arguments["utm_source"]
                if arguments.get("utm_medium"):
                    filters["utm_medium"] = arguments["utm_medium"]
                if arguments.get("country"):
                    filters["country"] = arguments["country"]

                data = await client.get_pages(
                    account_id=account_id,
                    date_range=arguments["date_range"],
                    limit=arguments.get("limit", 100),
                    skip=arguments.get("skip", 0),
                    auto_paginate=arguments.get("auto_paginate", False),
                    show_utms=arguments.get("show_utms", False),
                    **filters
                )

                result = "## Page Performance\n\n"

                # Add filter summary if filters were applied
                if filters:
                    result += "**Filters Applied:**\n"
                    if filters.get("content_grouping"):
                        result += f"- Content Group: {filters['content_grouping']}\n"
                    if filters.get("utm_source"):
                        result += f"- Source: {filters['utm_source']}\n"
                    if filters.get("utm_medium"):
                        result += f"- Medium: {filters['utm_medium']}\n"
                    if filters.get("country"):
                        result += f"- Country: {filters['country']}\n"
                    result += "\n"

                for item in data[:20]:  # Show top 20 pages
                    url = item.get("url", "Unknown")
                    views = item.get("views", 0)
                    entry = item.get("entry_page", 0)
                    content_group = item.get("content_grouping")

                    result += f"### {url}\n\n"
                    if content_group:
                        result += f"- **Content Group:** {content_group}\n"
                    result += f"- **Views:** {views:,}\n"
                    result += f"- **Entry Pages:** {entry:,}\n\n"

                return [TextContent(type="text", text=result)]

            except ValueError as e:
                logger.error(f"Error fetching pages performance: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"## Error Fetching Pages Performance\n\n{str(e)}"
                )]

        elif name == "generate_conversion_pixel":
            account_id = get_account_id(arguments)
            if not account_id:
                return [TextContent(
                    type="text",
                    text="Error: No account_id provided and SEALMETRICS_ACCOUNT_ID not set in environment."
                )]

            pixel = generate_conversion_pixel(
                account_id=account_id,
                event_type=arguments.get("event_type", "conversion"),
                label=arguments.get("label"),
                value=arguments.get("value"),
                ignore_pageview=arguments.get("ignore_pageview", False)
            )

            result = "## Sealmetrics Tracking Pixel\n\n"
            result += "Copy this code and paste it into Google Tag Manager or your website:\n\n"
            result += f"```html\n{pixel}\n```\n\n"
            result += "### Usage Instructions:\n\n"
            result += "1. **For Google Tag Manager:** Create a new Custom HTML tag and paste this code\n"
            result += "2. **For Direct Website Integration:** Paste this code where you want the conversion to be tracked\n"
            result += "3. **Trigger:** Configure when this pixel should fire (e.g., on purchase, form submission, button click)\n\n"

            if arguments.get("ignore_pageview"):
                result += "**Note:** This pixel has `ignore_pageview = 1`, so it won't count an additional pageview. "
                result += "Use this when tracking events on pages that already have the global tracker installed.\n"

            return [TextContent(type="text", text=result)]

        else:
            logger.warning(f"Unknown tool requested: {name}")
            return [TextContent(
                type="text",
                text=f"## Error: Unknown Tool\n\n"
                     f"The tool '{name}' is not recognized.\n\n"
                     "**Available tools:**\n"
                     "- get_accounts\n"
                     "- get_traffic_data\n"
                     "- get_conversions\n"
                     "- get_microconversions\n"
                     "- get_funnel_data\n"
                     "- get_roas_evolution\n"
                     "- get_pages_performance\n"
                     "- generate_conversion_pixel"
            )]

    except ValueError as e:
        # ValueError exceptions are our user-friendly error messages
        logger.error(f"ValueError in tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"## Error\n\n{str(e)}"
        )]

    except KeyError as e:
        logger.error(f"Missing required parameter in tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"## Error: Missing Required Parameter\n\n"
                 f"The parameter {str(e)} is required but was not provided.\n\n"
                 "Please check the tool documentation for required parameters."
        )]

    except Exception as e:
        logger.exception(f"Unexpected error executing tool {name}")
        return [TextContent(
            type="text",
            text=f"## Unexpected Error\n\n"
                 f"An unexpected error occurred while executing {name}:\n\n"
                 f"{type(e).__name__}: {str(e)}\n\n"
                 "**Troubleshooting:**\n"
                 "- Check the MCP server logs for details\n"
                 "- Verify all parameters are correctly formatted\n"
                 "- Try restarting Claude Desktop\n"
                 "- Contact support if the issue persists"
        )]


async def main():
    """Main entry point with error handling"""
    global client

    try:
        # Get credentials from environment
        # Support both API token and email/password authentication
        api_token = os.getenv("SEALMETRICS_API_TOKEN")
        email = os.getenv("SEALMETRICS_EMAIL")
        password = os.getenv("SEALMETRICS_PASSWORD")

        if api_token:
            # Use direct API token (recommended)
            logger.info("Initializing Sealmetrics client with API token")
            client = SealmetricsClient(api_token=api_token)
        elif email and password:
            # Use email/password login
            logger.info("Initializing Sealmetrics client with email/password")
            client = SealmetricsClient(email=email, password=password)
        else:
            error_msg = (
                "Missing Sealmetrics credentials. "
                "Either SEALMETRICS_API_TOKEN or both SEALMETRICS_EMAIL and SEALMETRICS_PASSWORD must be set in environment variables.\n\n"
                "To fix this, add one of these to your Claude Desktop config:\n"
                "1. SEALMETRICS_API_TOKEN (recommended) - Get this from your Sealmetrics dashboard\n"
                "2. SEALMETRICS_EMAIL and SEALMETRICS_PASSWORD - Your login credentials"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Run MCP server
        logger.info("Starting Sealmetrics MCP server")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        if client:
            await client.close()

    except Exception as e:
        logger.exception(f"Fatal error in MCP server: {str(e)}")
        raise

    finally:
        if client:
            try:
                await client.close()
                logger.info("Sealmetrics client closed")
            except Exception as e:
                logger.error(f"Error closing client: {str(e)}")


def run():
    """Synchronous entry point for the MCP server (used by console_scripts)"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        exit(1)


if __name__ == "__main__":
    run()
