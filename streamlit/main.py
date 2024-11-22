import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

# You can now import directly from the packages
from services import (
    create_bot,
    get_bot_status,
    fetch_transcripts,
    get_chat_messages,
    send_message,
    send_to_backend
)
from utils import display_combined_chat
from actions import check_messages, handle_stop_command

load_dotenv(override=True)
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
    if 'backend_url' not in st.session_state:
        st.session_state.backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    if 'meeting_url' not in st.session_state:
        st.session_state.meeting_url = ""
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if 'processed_messages' not in st.session_state:
        st.session_state.processed_messages = set()
    if 'host_name' not in st.session_state:
        st.session_state.host_name = ""

def main():
    init_session_state()

    st.title("🐙 Octopai Bot")

    # Add host name input at the top
    host_name = st.text_input(
        "Host Name",
        value=st.session_state.host_name,
        placeholder="Enter the host's name",
        help="Enter the name of the meeting host"
    )
    st.session_state.host_name = host_name

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
            if api_key and meeting_url and host_name:
                with st.spinner("Creating bot..."):
                    bot_id = create_bot(api_key, meeting_url)
                    if bot_id:
                        st.session_state.bot_id = bot_id
                        # Store meeting URL in session state
                        st.session_state.meeting_url = meeting_url

                        # Fetch initial transcript data
                        transcripts = fetch_transcripts(api_key, bot_id)
                        if transcripts:
                            st.session_state.transcripts = transcripts

                        try:
                            # Send to backend
                            success, message = send_to_backend(
                                st.session_state.backend_url,
                                meeting_url,
                                host_name,
                                transcripts
                            )

                            if success:
                                st.success("Meeting data sent to backend successfully!")
                            else:
                                st.error(f"Failed to send to backend: {message}")

                            st.success(f"Bot created successfully! ID: {bot_id}")

                        except Exception as e:
                            st.error(f"Failed to prepare meeting data: {str(e)}")
                    else:
                        st.error("Failed to create bot")
            else:
                st.error("Please provide API key, meeting URL, and host name")

        if st.session_state.bot_id:
            st.info(f"Current Bot ID: {st.session_state.bot_id}")
            status = get_bot_status(api_key, st.session_state.bot_id)
            if status:
                st.info(f"Status: {status}")

    with col2:
        if st.session_state.bot_id:
            st.header("Send Message")
            chat_message = st.text_input("Type your message")
            col_send, col_action = st.columns(2)

            with col_send:
                if st.button("Send", type="primary"):
                    if chat_message:
                        if send_message(api_key, st.session_state.bot_id, chat_message):
                            st.success("Message sent!")
                            st.rerun()

            with col_action:
                if st.button("example_action1", type="secondary"):
                    if handle_stop_command(api_key, st.session_state.bot_id):
                        st.success("Action triggered!")
                        st.rerun()

            st.divider()
            st.header("Meeting Activity")

            # Controls
            auto_refresh = st.toggle('🔄 Enable Auto-refresh')
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔄 Refresh Transcripts"):
                    transcripts = fetch_transcripts(api_key, st.session_state.bot_id)
                    if transcripts:
                        st.session_state.transcripts = transcripts
                        st.session_state.last_refresh = time.time()
                        # Send updated transcripts to backend
                        try:
                            success, message = send_to_backend(
                                st.session_state.backend_url,
                                meeting_url,
                                st.session_state.host_name,
                                transcripts
                            )
                            if success:
                                st.success("Backend updated successfully!")
                            else:
                                st.error(f"Failed to send to backend: {message}")
                        except Exception as e:
                            st.error(f"Failed to send to backend: {str(e)}")

            with col_b:
                if st.button("🔄 Refresh Chat"):
                    chat_messages = get_chat_messages(api_key, st.session_state.bot_id)
                    if chat_messages:
                        st.session_state.chat_messages = chat_messages
                        check_messages(None, chat_messages, api_key,
                                    st.session_state.bot_id,
                                    st.session_state.processed_messages)

            display_combined_chat(st.session_state.transcripts, st.session_state.chat_messages)

            if auto_refresh:
                if time.time() - st.session_state.last_refresh > 5:
                    transcripts = fetch_transcripts(api_key, st.session_state.bot_id)
                    chat_messages = get_chat_messages(api_key, st.session_state.bot_id)
                    if transcripts:
                        st.session_state.transcripts = transcripts
                    if chat_messages:
                        st.session_state.chat_messages = chat_messages
                        check_messages(None, chat_messages, api_key,
                                    st.session_state.bot_id,
                                    st.session_state.processed_messages)
                    st.session_state.last_refresh = time.time()
                st.rerun()

if __name__ == "__main__":
    main()