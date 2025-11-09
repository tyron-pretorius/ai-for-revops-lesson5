import os, json
from typing import Tuple, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MCP_URL = "https://73f9e571a915.ngrok-free.app/api/mcp"
MCP_KEY = os.getenv("MCP_API_KEY")   # same key your server expects
MCP_LABEL = "mql_functions"          # label you referenced in your prompt

_thread_to_conv: Dict[Tuple[str, str], str] = {}

def get_or_create_conv_id(channel: str, thread_ts: str) -> str:
    key = (channel, thread_ts)
    if key in _thread_to_conv:
        return _thread_to_conv[key]
    conv = client.conversations.create()  # returns { id: "conv_..." , ... }
    _thread_to_conv[key] = conv.id
    return conv.id

MODEL = "gpt-5"
PROMPT_ID = "pmpt_690e9aa54260819699501b92b4d0b1020705ee4b0cb2a09c"

def create_openai_response(channel: str, thread_ts: str, input: str, conversation_id: str) -> tuple[str, str]:

    resp = client.responses.create(
        model=MODEL,
        prompt={"id": PROMPT_ID, "variables": {"slack_channel": channel,"slack_thread_ts": thread_ts,"user_message": input}},
        input=[{"role": "user", "content": input}],
        conversation=conversation_id,
        tools=[{
            "type": "mcp",
            "server_label": MCP_LABEL,
            "server_url": MCP_URL,
            "headers": { "Authorization": f"Bearer {MCP_KEY}" },
            "require_approval": "never",
        }],
    )

    raw = resp.output_text
    print(json.dumps(resp.model_dump(), indent=2))
    print(raw)
    return raw