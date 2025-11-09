# Slack App Setup Instructions

This guide will help you create a Slack app with all the necessary scopes and permissions for the RevOps MCP server.

## Prerequisites

- A Slack workspace where you have permission to install apps
- Admin access to the workspace (for some scopes)

## Step-by-Step Instructions

### Step 1: Create a New Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Fill in:
   - **App Name**: `RevOps MCP Bot` (or any name you prefer)
   - **Pick a workspace**: Select your workspace
5. Click **"Create App"**

### Step 2: Configure Bot Token Scopes

1. In your app settings, go to **"OAuth & Permissions"** in the left sidebar
2. Scroll down to **"Scopes"** > **"Bot Token Scopes"**
3. Add the following scopes (click "Add an OAuth Scope" for each):

   **Required Scopes:**
   - `app_mentions:read` - Listen for app mentions
   - `chat:write` - Send messages
   - `channels:history` - Read messages in public channels
   - `users:read` - View people in the workspace
   - `users:read.email` - View email addresses of people in the workspace

### Step 3: Enable Socket Mode

Socket Mode is required for `slack_listener.py` to work:

1. Go to **"Socket Mode"** in the left sidebar
2. Toggle **"Enable Socket Mode"** to ON
3. Click **"Generate Token"** under **"App-Level Tokens"**
4. Give it a name: `socket-mode-token`
5. Add the scope: `connections:write`
6. Click **"Generate"**
7. **Copy this token** - this is your `SLACK_APP_TOKEN` (starts with `xapp-`)
8. Save it to your `.env` file:
   ```
   SLACK_APP_TOKEN=xapp-your-token-here
   ```

### Step 4: Subscribe to Events

1. Go to **"Event Subscriptions"** in the left sidebar
2. Toggle **"Enable Events"** to ON
3. Under **"Subscribe to bot events"**, click **"Add Bot User Event"**
4. Add the following events:
   - `app_mention` - Listen for when users mention your app

### Step 5: Install the App to Your Workspace

1. Go to **"OAuth & Permissions"** in the left sidebar
2. Scroll to the top
3. Click **"Install to Workspace"**
4. Review the permissions and click **"Allow"**
5. **Copy the "Bot User OAuth Token"** - this is your `SLACK_BOT_TOKEN` (starts with `xoxb-`)
6. Save it to your `.env` file:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```

### Step 6: Configure Environment Variables

Add both tokens to your `.env` file:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

### Step 7: Invite the Bot to Channels

After installing, you need to invite your bot to channels where you want it to respond:

1. In Slack, go to the channel
2. Type `/invite @YourBotName` or click the channel name > **Integrations** > **Add apps**
3. Search for your bot and add it

**Note:** For private channels, the bot must be explicitly invited. For public channels, the bot can join automatically if it has the `channels:join` scope.

## Required Scopes Summary

### Bot Token Scopes (OAuth & Permissions)
- `app_mentions:read` - Required for `slack_listener.py` to receive mentions
- `chat:write` - Required for sending messages
- `channels:history` - Required for reading public channel messages
- `users:read` - Required for `get_slack_user_profile()` function
- `users:read.email` - Required to read user email addresses

### App-Level Token Scopes (Socket Mode)
- `connections:write` - Required for Socket Mode connection

### Event Subscriptions
- `app_mention` - Required to receive mention events

## Testing Your Setup

### Test 1: Verify Bot Token
```python
from slack_sdk import WebClient
import os
from dotenv import load_dotenv

load_dotenv()
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.auth_test()
print(f"Bot User ID: {response['user_id']}")
print(f"Team: {response['team']}")
```

### Test 2: Test User Profile Lookup
```python
from MCP Server.slack_functions import get_slack_user_profile

# Replace with a real user ID
profile = get_slack_user_profile("U1234567890")
print(profile)
```

### Test 3: Test Sending a Message
```python
from MCP Server.slack_functions import send_slack_message

result = send_slack_message(
    channel_id="C1234567890",  # Replace with a real channel ID
    text="Test message"
)
print(result)
```

### Test 4: Test Slack Listener
```bash
cd /Users/tyronpretorius/PycharmProjects/ai-for-revops-lesson5
source venv/bin/activate
python Brain/slack_listener.py
```

Then mention your bot in Slack: `@YourBotName hello`

## Troubleshooting

### Error: "not_in_channel"
- **Solution**: Invite the bot to the channel using `/invite @YourBotName`
- Or ensure the bot has `channels:join` scope and it will auto-join public channels

### Error: "missing_scope"
- **Solution**: Go to OAuth & Permissions and add the missing scope
- Reinstall the app to your workspace after adding scopes

### Error: "invalid_auth" or "account_inactive"
- **Solution**: Verify your `SLACK_BOT_TOKEN` is correct and not expired
- Regenerate the token if needed

### Bot not responding to mentions
- **Solution**: 
  - Verify Socket Mode is enabled
  - Check that `SLACK_APP_TOKEN` is set correctly
  - Ensure `app_mention` event is subscribed
  - Make sure the bot is invited to the channel

### Can't read user email
- **Solution**: Add `users:read.email` scope and reinstall the app

## Security Best Practices

⚠️ **Important Security Notes:**
- **Never commit tokens to git** (they're already in `.gitignore`)
- Store tokens securely in `.env` file
- Rotate tokens if they're ever exposed
- Use the minimum required scopes for your use case
- Regularly review app permissions in your workspace

## Additional Resources

- [Slack API Documentation](https://api.slack.com/)
- [Slack Bolt Framework](https://slack.dev/bolt-python/)
- [Socket Mode Guide](https://api.slack.com/apis/connections/socket)
- [OAuth Scopes Reference](https://api.slack.com/scopes)

