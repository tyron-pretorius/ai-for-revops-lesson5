"""
Simple MCP Server that exposes functions from:
- gmail_functions.py
- marketo_functions.py
- salesforce_functions.py
- slack_functions.py
"""

from fastmcp import FastMCP
import sys, os, secrets
from starlette.responses import JSONResponse, PlainTextResponse
from fastmcp.server.auth.auth import AuthProvider, AccessToken
from dotenv import load_dotenv

load_dotenv()

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all our function modules
import gmail_functions
import marketo_functions
import salesforce_functions
import slack_functions

# ============================================================================
# Simple Bearer (API key) auth provider
# ============================================================================
class StaticApiKeyAuth(AuthProvider):
    """
    Very small auth provider that accepts exactly one API key via
    Authorization: Bearer <API_KEY>.
    """

    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.required_scopes = []  # No scopes

    @staticmethod
    def _normalize(token: str | None) -> str:
        if not token:
            return ""
        parts = token.strip().split()
        # "Bearer <key>" / "Token <key>" / "ApiKey <key>"
        if len(parts) == 2 and parts[0].lower() in ("bearer", "token", "apikey"):
            return parts[1]
        # raw token
        return token.strip()

    
    async def verify_token(self, token: str) -> AccessToken | None:
        presented = self._normalize(token)
        if presented and self.api_key and secrets.compare_digest(presented, self.api_key):
            return AccessToken(
                token=presented,                # the presented bearer token
                client_id="revops-mcp-client",  # any stable id/name for the caller
                scopes=[]                      # you’re not using scopes; keep empty
            )
        return None

# Create the MCP server (we’ll attach auth + routes below)
# NOTE: we pass auth=... to enable Bearer verification on HTTP calls.
mcp = FastMCP(
    "RevOps Functions Server",
    auth=StaticApiKeyAuth(api_key=os.getenv("MCP_API_KEY", "")),
)

# ============================================================================
# Health route
# ============================================================================

@mcp.custom_route("/mcp/", methods=["GET"])
async def mcp_probe(_request):
    return PlainTextResponse("MCP endpoint is at /api/mcp/ (POST/SSE only).")

@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    # Lightweight app health (not tool health)
    return JSONResponse({"status": "ok"})

# ============================================================================
# Gmail Functions
# ============================================================================

@mcp.tool()
def send_email(user_email: str, sender: str, to: str, subject: str, message_text: str, cc: str = "", reply_to: str = "", is_html: bool = False) -> dict:
    """Send an email using Gmail API via service account."""
    service = gmail_functions.get_gmail_service(user_email)
    result = gmail_functions.send_email(service, sender, to, cc, subject, message_text, reply_to, is_html)
    return result

# ============================================================================
# Marketo Functions
# ============================================================================

@mcp.tool()
def lookup_marketo_lead(filter_type: str, filter_values: str, fields: str = None) -> dict:
    """Look up a lead in Marketo by email, ID, or other filter type."""
    token = marketo_functions.checkTokenLife()
    result = marketo_functions.lookupLead(token, filter_type, filter_values, fields)
    return result

@mcp.tool()
def get_marketo_activities_for_lead(lead_id: str, days_in_past: int = 7) -> list:
    """Get activities for a specific Marketo lead ID within a time range."""
    activities = marketo_functions.getActivitiesforLead(lead_id, days_in_past)
    return activities

# ============================================================================
# Salesforce Functions
# ============================================================================

@mcp.tool()
def find_salesforce_contact_or_lead(email: str) -> dict:
    """Find if an email belongs to a Contact or Lead in Salesforce."""
    result = salesforce_functions.find_contact_or_lead_by_email(email)
    return result if result else {"error": "Not found"}

@mcp.tool()
def update_salesforce_lead(lead_id: str, lead_fields: dict) -> dict:
    """Update fields on a Salesforce Lead."""
    result = salesforce_functions.update_lead_fields(lead_id, lead_fields)
    return result

@mcp.tool()
def update_salesforce_contact(contact_id: str, contact_fields: dict) -> dict:
    """Update fields on a Salesforce Contact."""
    result = salesforce_functions.update_contact_fields(contact_id, contact_fields)
    return result

@mcp.tool()
def create_salesforce_lead(fields: dict) -> dict:
    """Create a new Lead in Salesforce."""
    result = salesforce_functions.create_lead(fields)
    return result

@mcp.tool()
def lookup_salesforce_user_by_email(user_email: str) -> dict:
    """Lookup a User by email address and return user information."""
    result = salesforce_functions.lookup_user_email(user_email)
    return result

# ============================================================================
# Slack Functions
# ============================================================================

@mcp.tool()
def get_slack_user_profile(user_id: str) -> dict:
    """Get a Slack user's profile information by their Slack user ID."""
    result = slack_functions.get_slack_user_profile(user_id)
    return result if result else {"error": "User not found"}

@mcp.tool()
def get_slack_thread_messages(channel_id: str, thread_ts: str) -> dict:
    """Get all messages in a Slack thread by channel ID and thread timestamp."""
    result = slack_functions.get_thread_messages(channel_id, thread_ts)
    return result

# ============================================================================
# Run the server
# ============================================================================

if __name__ == "__main__":

    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/api/mcp/")
