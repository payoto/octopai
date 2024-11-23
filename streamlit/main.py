import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

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
    if 'backend_messages' not in st.session_state:
        st.session_state.backend_messages = []
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
    if "message_input" not in st.session_state:
        st.session_state.message_input = ""

def clear_message():
    st.session_state.message_input = ""

def main():
    init_session_state()

    # Sidebar Controls
    with st.sidebar:
        st.header("Chat Controls")

        # Auto-refresh toggle
        auto_refresh = st.toggle('🔄 Auto-refresh', value=True)

        # Refresh button in sidebar
        if st.button("🔄"):
            transcripts = fetch_transcripts(st.session_state.api_key, st.session_state.bot_id)
            if transcripts:
                st.session_state.transcripts = transcripts
                try:
                    success, response = send_to_backend(
                        st.session_state.backend_url,
                        st.session_state.meeting_url,
                        st.session_state.host_name,
                        transcripts
                    )
                    if success and isinstance(response, list):
                        st.session_state.backend_messages = response
                except Exception as e:
                    st.error(f"Failed to update backend data: {str(e)}")
                st.session_state.last_refresh = time.time()

        # Example action button
        if st.button("Example Action", type="secondary"):
            if handle_stop_command(st.session_state.api_key, st.session_state.bot_id):
                st.success("Action triggered!")
                st.rerun()

        # Add some space
        st.markdown("---")

        # Connection status if bot exists
        if st.session_state.bot_id:
            st.subheader("Connection Status")
            status = get_bot_status(st.session_state.api_key, st.session_state.bot_id)
            if status:
                st.info(f"Bot Status: {status}")

    # Main page content
    st.title("🐙 Octopai Bot")

    # Top section with connection settings
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            host_name = st.text_input(
                "Host Name",
                value=st.session_state.host_name,
                placeholder="Enter the host's name",
                help="Enter the name of the meeting host"
            )
            st.session_state.host_name = host_name

        with col2:
            api_key = st.text_input(
                "API Key",
                value=st.session_state.api_key,
                type="password",
                help="Enter your API key"
            )

        with col3:
            meeting_url = st.text_input(
                "Meeting URL",
                placeholder="Enter your meeting URL here",
                help="Enter the full meeting URL"
            )

    # Create Bot button centered
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Create Bot", type="primary", use_container_width=True):
            if api_key and meeting_url and host_name:
                with st.spinner("Creating bot..."):
                    bot_id = create_bot(api_key, meeting_url)
                    if bot_id:
                        st.session_state.bot_id = bot_id
                        st.session_state.meeting_url = meeting_url

                        transcripts = fetch_transcripts(api_key, bot_id)
                        if transcripts:
                            st.session_state.transcripts = transcripts
                            try:
                                success, response = send_to_backend(
                                    st.session_state.backend_url,
                                    meeting_url,
                                    host_name,
                                    transcripts
                                )
                                if success:
                                    if isinstance(response, list):
                                        st.session_state.backend_messages = response
                                    st.success("Bot created and connected successfully!")
                                else:
                                    st.error(f"Failed to send to backend: {response}")
                            except Exception as e:
                                st.error(f"Failed to prepare meeting data: {str(e)}")
                    else:
                        st.error("Failed to create bot")
            else:
                st.error("Please provide API key, meeting URL, and host name")

    # Divider between settings and chat
    st.divider()

    # Chat section
    if st.session_state.bot_id:
        # Chat display
        with st.container():
            display_combined_chat(
                st.session_state.transcripts,
                st.session_state.chat_messages,
                st.session_state.backend_messages
            )

        # Message input
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        message_col1, message_col2 = st.columns([4, 1])

        with message_col1:
            message = st.text_input(
                "Type your message",
                key="message_input",
                label_visibility="collapsed",
                on_change=clear_message
            )

        with message_col2:
            if st.button("Send", type="primary", use_container_width=True):
                if st.session_state.message_input and st.session_state.message_input.strip():
                    success = send_message(
                        st.session_state.api_key,
                        st.session_state.bot_id,
                        st.session_state.message_input
                    )
                    if success:
                        clear_message()
                        time.sleep(1)  # Small delay to allow message to process
                        st.rerun()
                    else:
                        st.error("Failed to send message")

        # Auto-refresh logic - only for transcripts and backend messages
        if auto_refresh and time.time() - st.session_state.last_refresh > 5:
            update_needed = False

            # Update transcripts
            transcripts = fetch_transcripts(st.session_state.api_key, st.session_state.bot_id)
            if transcripts and transcripts != st.session_state.transcripts:
                st.session_state.transcripts = transcripts
                update_needed = True

                # Process backend messages only if transcripts changed
                try:
                    success, response = send_to_backend(
                        st.session_state.backend_url,
                        st.session_state.meeting_url,
                        st.session_state.host_name,
                        transcripts
                    )
                    if success and isinstance(response, list):
                        st.session_state.backend_messages = response
                        update_needed = True
                except Exception as e:
                    st.error(f"Failed to update backend data: {str(e)}")

            # Update chat messages
            chat_messages = get_chat_messages(st.session_state.api_key, st.session_state.bot_id)
            if chat_messages and chat_messages != st.session_state.chat_messages:
                st.session_state.chat_messages = chat_messages
                update_needed = True

            st.session_state.last_refresh = time.time()

            # Only rerun if updates were made
            if update_needed:
                st.rerun()

if __name__ == "__main__":
    main()