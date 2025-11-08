from slack_bolt import App
import os, logging, re, dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai_functions import create_openai_response

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)


def _strip_bot_mention(text: str, bot_user_id: str | None) -> str:
    if not text:
        return ""
    # Remove tokens like "<@U12345>" that mention your app/bot
    if bot_user_id:
        text = text.replace(f"<@{bot_user_id}>", "").strip()
    # Fallback: strip any mention token
    return re.sub(r"<@[^>]+>", "", text).strip()

def create_slack_app():
    """
    Create and return a Slack Bolt App that:
    - listens for app_mention events
    - sends user text to OpenAI Responses API
    - posts the model's reply back in the same Slack thread
    """
    app = App(token=os.environ["SLACK_BOT_TOKEN"])

    # Cache your bot's user_id once so we can strip @mentions from text
    bot_user_id = app.client.auth_test()["user_id"]

    @app.event("app_mention")
    def handle_app_mention(event, say, logger):
        """
        Receives a mention like '@your-app what's the weather?'
        Sends the user's text to OpenAI Responses API with the Slack thread id
        as the conversation id, then replies in-thread with the model output.
        """
        channel = event.get("channel")
        user = event.get("user")
        ts = event.get("ts")  # timestamp of this message
        thread_ts = event.get("thread_ts") or ts  # root thread id
        conv_id = thread_ts.replace(".", "-")

        # Clean the text (remove the @mention token)
        raw_text = event.get("text", "")
        user_text = _strip_bot_mention(raw_text, bot_user_id)
        if not user_text:
            say(text=f"Hi <@{user}> — what can I help with?", thread_ts=thread_ts)
            return

        logger.info(f"Incoming mention from {user} in {channel} (thread {thread_ts}): {user_text}")

        # --- OpenAI Responses API call ---
        try:
            # Use Slack thread_ts as the conversation id to persist context
            # across replies in the same Slack thread.
            reply_text = create_openai_response(user_text, conv_id)

        except Exception as e:
            logger.exception("OpenAI call failed")
            say(text=f"Sorry <@{user}>, I hit an error talking to OpenAI: `{e}`",
                thread_ts=thread_ts)
            return

        # --- Reply back in the SAME Slack thread ---
        say(text=reply_text, thread_ts=thread_ts)

    return app

if __name__ == "__main__":

    app = create_slack_app()
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
