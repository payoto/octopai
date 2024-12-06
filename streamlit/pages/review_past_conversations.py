import streamlit as st
import json
from pathlib import Path
from utils.display import display_all_messages

st.set_page_config(page_title="Past Conversations", page_icon="📚", layout="wide")

def load_example_conversations():
    example_dir = Path('example_conversations')
    if example_dir.exists():
        return list(example_dir.glob('*.json'))
    return []

st.title("📚 Past Conversations")
st.markdown("Load a past conversations with the bot to review the chat "
             "history and the actions suggested by the bot.")

tab1, tab2 = st.tabs(["Example Conversations", "Upload Conversation"])

with tab1:
    conversations = load_example_conversations()
    if conversations:
        selected_file = st.selectbox(
            "Select conversation",
            conversations,
            format_func=lambda x: x.name
        )

        if selected_file:
            try:
                conversation = json.loads(selected_file.read_text())
                display_all_messages(conversation)
            except Exception as e:
                st.error(f"Error loading conversation: {str(e)}")
    else:
        st.info("No example conversations found in example_conversations/ directory")

with tab2:
    uploaded_file = st.file_uploader("Upload conversation JSON", type=['json'])
    if uploaded_file:
        try:
            conversation = json.load(uploaded_file)
            display_all_messages(conversation)
        except Exception as e:
            st.error(f"Error loading conversation: {str(e)}")