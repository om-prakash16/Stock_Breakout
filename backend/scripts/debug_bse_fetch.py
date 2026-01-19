from src.utils.network import fetch_url
from config.settings import BSE_EQ_API_URL
import json

print(f"Target URL: {BSE_EQ_API_URL}")
print("--- FETCHING ---")

content = fetch_url(BSE_EQ_API_URL, is_json=False)

if not content:
    print("Fetch returned None/Empty")
    exit(1)

text = content.decode('utf-8', errors='ignore')
# print(f"Raw Text: {text[:200]}")

try:
    data = json.loads(text)
    if isinstance(data, list) and len(data) > 0:
        print("\n--- FIRST ITEM KEYS ---")
        print(list(data[0].keys()))
        print("\n--- FIRST ITEM SAMPLE ---")
        print(data[0])
    else:
        print(f"Data is {type(data)}. Is List? {isinstance(data, list)}. Length: {len(data) if isinstance(data, list) else 'N/A'}")
except Exception as e:
    print(f"JSON Parse Error: {e}")
