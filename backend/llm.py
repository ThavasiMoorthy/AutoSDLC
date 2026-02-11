import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

# Read API Key from environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def set_api_key(key: str):
    global GROQ_API_KEY
    GROQ_API_KEY = key

def get_llm_client():
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)

async def generate_completion(system_prompt: str, user_prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    client = get_llm_client()
    if not client:
        raise ValueError("API Key not set")
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        raise e

async def generate_json(system_prompt: str, user_prompt: str, model: str = "llama-3.3-70b-versatile") -> dict:
    """Helper to get JSON response"""
    client = get_llm_client()
    if not client:
        raise ValueError("API Key not set")

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt + "\nIMPORTANT: Return ONLY valid JSON. No markdown formatting."},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq JSON Error: {e}")
        raise e
