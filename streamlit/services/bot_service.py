import requests
import streamlit as st
from pathlib import Path
import json

import base64
from pathlib import Path



def get_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def set_octopus(bot_id):
    # Get base64 encoded image
    file = Path(__file__).resolve().parents[1] / "octopus_21.jpg"
    octopus_base64 = get_image_as_base64(file)
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/output_video/"

    payload = { "kind": "jpeg",
            "b64_data": octopus_base64}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": st.session_state.api_key.strip()
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to set octopus image: {response.text}")


def create_bot(api_key, meeting_url):
    if Path(meeting_url).exists():
        return meeting_url
    url = "https://us-west-2.recall.ai/api/v1/bot"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key.strip()
    }
    payload = {
        "transcription_options": {
            "provider": "meeting_captions",
            "language": "en"
        },
        "meeting_url": meeting_url,
        "bot_name": "🐙 Octopai Bot",
        "chat": {
            "on_bot_join": {
                "send_to": "everyone",
                "message": """Hi there! I'm OctopAI 🐙 your friendly (and slightly genius) Money Movers assistant! Think of me as your group's secret weapon I'll help guide your conversations, tackle questions, and keep things flowing smoother than a dolphin doing the backstroke 🐬. No financial advice here (that's a no-go 🚫), but I'm great at helping you explore big ideas, find great resources and learn together! Ready to dive in?"""
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 401:
            st.error("Authentication failed. Please check your API key.")
            return None
        response.raise_for_status()
        bot_id = response.json()['id']
        set_octopus(bot_id)
        return bot_id
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating bot: {str(e)}")
        return None

def get_bot_status(api_key, bot_id):
    if Path(bot_id).exists():
        return "Dummy service from file"
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}"
    headers = {
        "accept": "application/json",
        "Authorization": api_key.strip()
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("status_changes", [])[-1]["code"]
    except requests.exceptions.RequestException:
        return None

def fetch_transcripts(api_key, bot_id):
    if Path(bot_id).exists():
        return json.loads(Path(bot_id).read_text())
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/transcript"
    headers = {
        "accept": "application/json",
        "Authorization": api_key.strip()
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching transcripts: {str(e)}")
        return None

def get_chat_messages(api_key, bot_id):
    if Path(bot_id).exists():
        return []
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/chat-messages/"
    headers = {
        "accept": "application/json",
        "Authorization": api_key.strip()
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching chat: {str(e)}")
        return None

def send_message(api_key, bot_id, message):
    if Path(bot_id).exists():
        return True
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/send_chat_message"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key.strip()
    }
    payload = {"message": message}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send message: {str(e)}")
        return False