import os, dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

dotenv.load_dotenv()

# Set your Slack Bot Token (starts with 'xoxb-...')
slack_token = os.environ["SLACK_BOT_TOKEN"]

# Initialize the Slack client
client = WebClient(token=slack_token)

def get_slack_user_profile(user_id):
    """Get Slack user profile by user ID."""
    response = client.users_info(user=user_id)
    user = response["user"]

    payload = {
        "name": user['profile']['real_name'],
        "email": user['profile'].get('email', 'N/A'),
        "timezone": user.get('tz', 'N/A')
    }

    return payload

def get_thread_messages(channel_id: str, thread_ts: str):
    """
    Get all messages in a Slack thread.
    
    Args:
        channel_id: The Slack channel ID where the thread exists
        thread_ts: The thread timestamp (ts) of the parent message
    
    Returns:
        Dictionary with success status and list of messages in the thread
    """

    response = client.conversations_replies(
        channel=channel_id,
        ts=thread_ts
    )
    
    messages = response.get('messages', [])
    
    # Format the messages for easier use
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'ts': msg.get('ts'),
            'user': msg.get('user'),
            'text': msg.get('text'),
            'thread_ts': msg.get('thread_ts'),
            'is_parent': msg.get('ts') == thread_ts,  # True if this is the parent message
            'reply_count': msg.get('reply_count', 0),
            'replies': msg.get('replies', [])
        })
    
    return {
        'success': True,
        'channel': channel_id,
        'thread_ts': thread_ts,
        'message_count': len(messages),
        'messages': formatted_messages
    }

if __name__ == "__main__":
    result = get_slack_user_profile("U01MB9ZKQQ1")
    print(result)