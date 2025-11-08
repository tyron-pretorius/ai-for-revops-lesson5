# MCP Server for RevOps Functions

A simple Model Context Protocol (MCP) server that exposes functions from Gmail, Marketo, Salesforce, and Slack.

## Available Tools

### Gmail Functions
- `send_email` - Send an email using Gmail API

### Marketo Functions
- `lookup_marketo_lead` - Look up a lead in Marketo by email, ID, or other filter
- `get_marketo_activities_for_lead` - Get activities for a specific Marketo lead
- `get_marketo_activity_types` - Get all available activity types from Marketo

### Salesforce Functions
- `find_salesforce_contact_or_lead` - Find if an email belongs to a Contact or Lead
- `update_salesforce_lead` - Update fields on a Salesforce Lead
- `update_salesforce_contact` - Update fields on a Salesforce Contact
- `create_salesforce_lead` - Create a new Lead in Salesforce

### Slack Functions
- `get_slack_user_profile` - Get a Slack user's profile by their user ID

## Running the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the MCP server
python mcp_server.py
```

## Environment Variables Required

Make sure your `.env` file contains:
- `MARKETO_BASE_URL`
- `MARKETO_CLIENT_ID`
- `MARKETO_CLIENT_SECRET`
- `SALESFORCE_USER`
- `SALESFORCE_PASSWORD`
- `SALESFORCE_TOKEN`
- `SLACK_BOT_TOKEN`

## Installation

```bash
pip install -r requirements.txt
```

