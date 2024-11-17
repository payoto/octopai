import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Replace with your Recall API Key, meeting URL, and destination URL
API_KEY = os.getenv("API_KEY")
MEETING_URL = os.getenv("MEETING_URL")
DESTINATION_URL = os.getenv("DESTINATION_URL")

# API endpoint and headers
url = "https://us-west-2.recall.ai/api/v1/bot"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Token {API_KEY}"
}

# Request payload with destination URL
payload = {
    "real_time_transcription": {
        "partial_results": True,
        "enhanced_diarization": True,
        "destination_url": DESTINATION_URL
    },
    "meeting_url": MEETING_URL
}

# Send the POST request
response = requests.post(url, headers=headers, json=payload)

# Handle the response
if response.status_code in [200, 201]:
    data = response.json()
    print("Bot created successfully!")
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
