import streamlit as st

def display_combined_chat(transcripts, chat_messages):
    if not transcripts and not chat_messages:
        st.info("No messages to display")
        return

    combined_messages = []

    if transcripts and isinstance(transcripts, list):
        current_speaker_message = None
        for transcript in transcripts:
            if isinstance(transcript, dict):
                speaker = transcript.get('speaker', 'Unknown')
                words = transcript.get('words', [])
                if words and isinstance(words, list):
                    text = ' '.join([word.get('text', '') for word in words])
                    if text.strip():
                        if current_speaker_message and current_speaker_message['name'] == speaker:
                            current_speaker_message['text'] += ' ' + text.strip()
                        else:
                            current_speaker_message = {
                                'type': 'transcript',
                                'name': speaker,
                                'text': text.strip()
                            }
                            combined_messages.append(current_speaker_message)

    for msg in combined_messages:
        if msg['type'] == 'chat':
            st.chat_message("user").write(f"**{msg['name']}**: {msg['text']}")
        else:
            st.chat_message("assistant").write(f"**{msg['name']}**: {msg['text']}")