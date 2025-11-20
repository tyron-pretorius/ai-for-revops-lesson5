import os, json
from typing import Tuple, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MCP_URL = "https://2e987b531a8a.ngrok-free.app/api/mcp"
MCP_KEY = os.getenv("MCP_API_KEY")   # same key your server expects
MCP_LABEL = "mql_mcp"          # label you referenced in your prompt

CONV_ID_MAPPING_FILE = "conv_id_mapping.json"

def _load_conv_mapping() -> Dict[Tuple[str, str], str]:
    """Load conversation ID mapping from JSON file."""
    if os.path.exists(CONV_ID_MAPPING_FILE):
        try:
            with open(CONV_ID_MAPPING_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to tuples
                return {tuple(k.split('|')): v for k, v in data.items()}
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, return empty dict
            print(f"Warning: Error loading conv_id_mapping.json: {e}")
            return {}
    return {}

def _save_conv_mapping(mapping: Dict[Tuple[str, str], str]) -> None:
    """Save conversation ID mapping to JSON file."""
    # Convert tuple keys to strings for JSON serialization
    data = {f"{k[0]}|{k[1]}": v for k, v in mapping.items()}
    with open(CONV_ID_MAPPING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_or_create_conv_id(channel: str, thread_ts: str) -> str:
    key = (channel, thread_ts)
    
    # Load existing mappings
    _thread_to_conv = _load_conv_mapping()
    
    # Check if mapping already exists
    if key in _thread_to_conv:
        return _thread_to_conv[key]
    
    # Create new conversation
    conv = client.conversations.create()  # returns { id: "conv_..." , ... }
    _thread_to_conv[key] = conv.id
    
    # Save updated mapping to file
    _save_conv_mapping(_thread_to_conv)
    
    return conv.id

MODEL = "gpt-5"
PROMPT_ID = "pmpt_6913fb3c00888190966cb2b14fc7864c02171c00ec70557c"

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