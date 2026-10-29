import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

print("Creating Gemini client...")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30000
    )
)

print("Sending request...")

start = time.time()

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Say Hello",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            max_output_tokens=10
        )
    )

    print("\nResponse:")
    print(response.text)

    print(f"\nTime taken: {time.time() - start:.2f} seconds")

except Exception as e:
    print("\nERROR:")
    print(type(e).__name__)
    print(e)