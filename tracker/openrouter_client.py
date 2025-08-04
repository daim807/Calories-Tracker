import requests
import os
from dotenv import load_dotenv

load_dotenv()

def ask_openrouter(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"🔑 Loaded Key: {api_key[:10]}...")  # Optional: for debugging

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost",  # Or your actual domain
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"
