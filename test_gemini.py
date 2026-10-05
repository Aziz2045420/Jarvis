import os
from google import genai

key = os.environ.get("GEMINI_API_KEY")
if not key:
    raise SystemExit("GEMINI_API_KEY is not set in this session")

client = genai.Client(api_key=key)
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Say hi in one short sentence.",
)
print(response.text)