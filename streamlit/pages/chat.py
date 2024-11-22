import streamlit as st
import json

st.set_page_config(page_title="Chat Messages", page_icon="💬", layout="wide")

st.title("💬 Raw Chat Data")

if 'chat_messages' in st.session_state and st.session_state.chat_messages:
    # Direct display of raw chat data
    st.write("Raw Chat Data:", st.session_state.chat_messages)

    # Download button for chat data
    chat_json = json.dumps(st.session_state.chat_messages, indent=2)
    st.download_button(
        label="Download Chat Data",
        data=chat_json,
        file_name="chat_data.json",
        mime="application/json"
    )

else:
    st.info("No chat messages available yet. Start a bot session to see messages.")

# Add refresh button
if st.button("🔄 Refresh Chat"):
    st.rerun()