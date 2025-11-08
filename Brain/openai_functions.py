import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-5"
PROMPT_ID = "pmpt_690e9aa54260819699501b92b4d0b1020705ee4b0cb2a09c"

def create_openai_response(input: str, conversation_id: str) -> tuple[str, str]:
    """
    Classify a free-text 'How did you hear?' answer.
    Returns (hear_source, hear_source_detail).
    Raises ValueError if the model doesn't return valid JSON.
    """
    resp = client.responses.create(
        model=MODEL,
        prompt={"id": PROMPT_ID},
        input=[{"role": "user", "content": input}],
        conversation=conversation_id,
    )

    raw = resp.output_text
    print(json.dumps(resp.model_dump(), indent=2))
    print(raw)
    data = json.loads(raw)
    return data