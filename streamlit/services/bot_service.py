import requests
import streamlit as st

def create_bot(api_key, meeting_url):
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
                "message": "Hello! I'm 🐙 Octopai Bot, I am here to help you."
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 401:
            st.error("Authentication failed. Please check your API key.")
            return None
        response.raise_for_status()
        return response.json()['id']
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating bot: {str(e)}")
        return None

def get_bot_status(api_key, bot_id):
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