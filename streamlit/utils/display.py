import streamlit as st
from typing import List, Dict, Generator, Any
from streamlit.delta_generator import DeltaGenerator
import random
from pathlib import Path
import requests
import uuid
import time

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

class SideBySideContainers:
    def __init__(self, column_layout, max_rows: int = 100, align: bool = True) -> None:
        self._column_layout = column_layout
        self._rows: list[list[DeltaGenerator]] = []
        self._max_rows = max_rows
        self._align = align

    def safe_iterate(
        self, column_id: int, start_row: int = 0
    ) -> Generator[DeltaGenerator, Any, None]:
        for row in self._rows[start_row:]:
            yield row[column_id]
        for _ in range(self._max_rows - len(self._rows)):
            yield self.next_row()[column_id]

    def next_row(self) -> list[DeltaGenerator]:
        if self._align or not self._rows:
            self._rows.append(st.columns(self._column_layout))
        return self._rows[-1]

    def get_box(self, row_i: int, col_i: int) -> DeltaGenerator:
        if len(self._rows) == 0:
            self.next_row()
        if row_i >= len(self._rows):
            row_i = len(self._rows) - 1
        return self._rows[row_i][col_i]

USER_AVATARS = ["🦊", "🐯", "🦁", "🐼", "🐨", "🐮", "🐷", "🐸", "🦉", "🦋", "🦒", "🦘", "🦫", "🦭", "🦬",
                "🦡", "🦦", "🦥", "🦙", "🦕", "🐳", "🐬", "🦈", "🦜", "🦢", "🦩", "🦃", "🦆", "🐧", "🦅", "🦚"]

def get_speaker_avatar(speaker: str) -> str:
    """Get or create consistent avatar for a speaker"""
    if 'speaker_avatars' not in st.session_state:
        st.session_state.speaker_avatars = {}

    if speaker not in st.session_state.speaker_avatars:
        st.session_state.speaker_avatars[speaker] = random.choice(USER_AVATARS)

    return st.session_state.speaker_avatars[speaker]

def merge_messages_by_timestamp(transcripts: List[Dict], backend_messages: List[Dict]) -> List[Dict]:
    """Merge and sort all messages by timestamp"""
    all_messages = []
    message_buffer = []
    last_speaker = None
    last_timestamp = None

    # Helper function to process and add buffered messages
    def process_buffer():
        nonlocal message_buffer, all_messages
        if message_buffer:
            # Create a single message from the buffer
            combined_text = ' '.join([msg['text'] for msg in message_buffer])
            all_messages.append({
                'type': 'transcript',
                'timestamp': message_buffer[0]['timestamp'],  # Use first timestamp
                'speaker': message_buffer[0]['speaker'],
                'text': combined_text
            })
            message_buffer = []

    # Process transcripts
    for transcript in transcripts:
        if not isinstance(transcript, dict) or 'words' not in transcript:
            continue

        words = transcript.get('words', [])
        if not words or not isinstance(words, list):
            continue

        timestamp = words[0].get('start_timestamp', 0)
        text = ' '.join(word.get('text', '') for word in words)
        speaker = transcript.get('speaker', 'Unknown')

        if text.strip():
            current_message = {
                'type': 'transcript',
                'timestamp': timestamp,
                'speaker': speaker,
                'text': text.strip()
            }

            # If this is a new speaker or too much time has passed
            if speaker != last_speaker:
                # Process any buffered messages before starting new speaker
                process_buffer()
                message_buffer = [current_message]
            else:
                # Same speaker, add to buffer
                message_buffer.append(current_message)

            last_speaker = speaker
            last_timestamp = timestamp

    # Process any remaining buffered messages
    process_buffer()

    # Process backend messages
    if backend_messages:
        for msg in backend_messages:
            timestamp = msg.get('timestamp', 0)

            if msg.get('sentiment'):
                all_messages.append({
                    'type': 'sentiment',
                    'timestamp': timestamp,
                    'content': msg['sentiment']
                })
            elif msg.get('action'):
                all_messages.append({
                    'type': 'action',
                    'timestamp': timestamp,
                    'content': msg['action']
                })
            elif msg.get('bot_message'):
                all_messages.append({
                    'type': 'bot_message',
                    'timestamp': timestamp,
                    'content': msg['bot_message']["content"]
                })
            else:
                st.warning(f"Unknown message type: {msg}")

    # Sort all messages by timestamp
    return sorted(all_messages, key=lambda x: x['timestamp'])

def display_combined_chat(transcripts, chat_messages, backend_messages=None):
    if not any([transcripts, backend_messages]):
        st.info("No messages to display")
        return

    # Get merged and sorted messages
    all_messages = merge_messages_by_timestamp(transcripts or [], backend_messages or [])

    # Initialize side by side containers
    containers = SideBySideContainers([1, 1], align=st.toggle("Align messages", True))

    # Style for boxes
    st.markdown("""
        <style>
        .sentiment-box {
            background-color: #FFE4E1;
            padding: 10px;
            border-radius: 5px;
            color: #333333;
            margin: 5px 0;
        }
        .action-box {
            background-color: #E6E6FA;
            padding: 10px;
            border-radius: 5px;
            color: #333333;
            margin: 5px 0;
        }
        .stChatMessage {
            min-height: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display headers
    col1, col2 = containers.next_row()
    with col1:
        st.subheader("Transcript")
    with col2:
        st.subheader("Octopai Analysis")

    col1, col2 = containers.next_row()

    # Display messages
    for msg in all_messages:
        if msg['type'] == 'transcript':
            col1, col2 = containers.next_row()
            # Get transcript container
            with col1:
                avatar = get_speaker_avatar(msg['speaker'])
                st.chat_message("user", avatar=avatar).markdown(
                    f"**{msg['speaker']}**: {msg['text']}"
                )
        else:
            # Get AI analysis container
            with col2:
                if msg['type'] == 'sentiment':
                    with st.chat_message("assistant", avatar="🐙"):
                        content = msg['content']
                        with st.expander("Sentiment: " + content["sentiment"]):
                            st.markdown(
                                f"""<div class="sentiment-box">
                                <p><strong>🎭 Sentiment Detected:</strong> {content['sentiment']}</p>
                                <p><strong>💭 Explanation:</strong> {content['explanation']}</p>
                                <p><strong>📊 Confidence:</strong> {content['confidence']:.2%}</p>
                                </div>""",
                                unsafe_allow_html=True
                            )
                elif msg['type'] == 'action':
                    with st.chat_message("assistant", avatar="🐙"):
                        content = msg['content']
                        with st.expander("Action: " + content["action"]):
                            st.markdown(
                                f"""<div class="action-box">
                                <p><strong>🎯 Action:</strong> {content['action']}</p>
                                <p><strong>💭 Explanation:</strong> {content['explanation']}</p>
                                <p><strong>📊 Confidence:</strong> {content['confidence']:.2%}</p>
                                </div>""",
                                unsafe_allow_html=True
                            )
                elif msg['type'] == 'bot_message':
                    with st.chat_message("assistant", avatar="🐙"):
                        st.markdown("**Octopai is suggesting:**")
                        text = msg['content']
                        if "<hyde>" in text:
                            reasoning, text = text.split("</hyde>")
                            with st.expander("RAG thinking"):
                                st.markdown(reasoning)
                        st.markdown(text)
                        if st.button("Send to chat", key=msg['content']+str(uuid.uuid4().hex)):
                            success = send_message(
                                st.session_state.api_key,
                                st.session_state.bot_id,
                                text,
                            )
                            if success:
                                st.success("Message sent!" )
                            else:
                                st.error("Failed to send message")
                            time.sleep(1)
