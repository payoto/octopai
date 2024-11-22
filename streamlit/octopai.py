import streamlit as st
import requests
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Set page config
st.set_page_config(page_title="🐙 Octopai Bot", page_icon="🐙", layout="wide")

def init_session_state():
    if 'bot_id' not in st.session_state:
        st.session_state.bot_id = None
    if 'transcripts' not in st.session_state:
        st.session_state.transcripts = []
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv("API_KEY", "")
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if 'last_speaker' not in st.session_state:
        st.session_state.last_speaker = None

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
        data = response.json()
        return data['id']
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
        data = response.json()
        return data.get("status_changes", [])[-1]["code"]
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
        transcripts = response.json()

        # Debug information
        st.write("Response Status:", response.status_code)
        st.write("Raw Transcript Data:", transcripts)

        return transcripts
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
        data = response.json()

        # Debug information
        st.write("Chat Response Status:", response.status_code)
        st.write("Raw Chat Data:", data)

        return data
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

def extract_clean_messages(transcripts):
    clean_messages = []

    if isinstance(transcripts, list):
        for transcript in transcripts:
            if isinstance(transcript, dict):
                speaker = transcript.get('speaker', 'Unknown Speaker')

                # Extract text from words array
                words = transcript.get('words', [])
                if words and isinstance(words, list):
                    text = ' '.join([word.get('text', '') for word in words])
                    if text.strip():
                        clean_messages.append({
                            'speaker': speaker,
                            'text': text.strip()
                        })

    return clean_messages

def display_clean_chat(messages):
    st.markdown("### Clean Chat View")

    if not messages:
        st.info("No messages to display")
        return

    for msg in messages:
        speaker = msg['speaker']
        text = msg['text']

        if "Octopai" in speaker:
            st.chat_message("assistant", avatar="🐙").write(f"{text}")
        else:
            st.chat_message("user").write(f"**{speaker}**: {text}")

def main():
    init_session_state()

    st.title("🐙 Octopai Bot")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Connection Settings")

        api_key = st.text_input("API Key",
                               value=st.session_state.api_key,
                               type="password",
                               help="Enter your API key")

        meeting_url = st.text_input("Meeting URL",
                                   placeholder="Enter your meeting URL here",
                                   help="Enter the full meeting URL")

        if st.button("Create Bot", type="primary"):
            if api_key and meeting_url:
                with st.spinner("Creating bot..."):
                    bot_id = create_bot(api_key, meeting_url)
                    if bot_id:
                        st.session_state.bot_id = bot_id
                        st.success(f"Bot created successfully! ID: {bot_id}")
                    else:
                        st.error("Failed to create bot")
            else:
                st.error("Please provide both API key and meeting URL")

        if st.session_state.bot_id:
            st.info(f"Current Bot ID: {st.session_state.bot_id}")
            status = get_bot_status(api_key, st.session_state.bot_id)
            if status:
                st.info(f"Status: {status}")

    with col2:
        if st.session_state.bot_id:
            # Chat input at top
            st.header("Send Message")
            chat_message = st.text_input("Type your message")
            if st.button("Send", type="primary"):
                if chat_message:
                    if send_message(api_key, st.session_state.bot_id, chat_message):
                        st.success("Message sent!")
                        st.rerun()

            st.divider()
            st.header("Meeting Activity")

            # Create tabs for different views
            transcript_tab, chat_tab = st.tabs(["Transcripts", "Chat Messages"])

            with transcript_tab:
                auto_refresh = st.toggle('🔄 Enable Auto-refresh')
                if st.button("🔄 Refresh Transcripts"):
                    with st.spinner("Fetching transcripts..."):
                        transcripts = fetch_transcripts(api_key, st.session_state.bot_id)
                        if transcripts:
                            st.session_state.transcripts = transcripts
                            st.session_state.last_refresh = time.time()

                if st.session_state.transcripts:
                    clean_messages = extract_clean_messages(st.session_state.transcripts)
                    display_clean_chat(clean_messages)

            with chat_tab:
                if st.button("🔄 Refresh Chat"):
                    chat_messages = get_chat_messages(api_key, st.session_state.bot_id)
                    if chat_messages:
                        st.session_state.chat_messages = chat_messages

            if auto_refresh:
                if time.time() - st.session_state.last_refresh > 5:
                    transcripts = fetch_transcripts(api_key, st.session_state.bot_id)
                    chat_messages = get_chat_messages(api_key, st.session_state.bot_id)
                    if transcripts:
                        st.session_state.transcripts = transcripts
                    if chat_messages:
                        st.session_state.chat_messages = chat_messages
                    st.session_state.last_refresh = time.time()
                st.rerun()

if __name__ == "__main__":
    main()