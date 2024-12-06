import streamlit as st
import json

st.set_page_config(page_title="Transcripts", page_icon="📝", layout="wide")

st.title("📝 Raw Transcript Data")

# Debug information
st.subheader("Debug Info")
st.write("Session State Keys:", list(st.session_state.keys()))
st.write("Bot ID:", st.session_state.get('bot_id'))
st.write("Has Transcripts:", 'transcripts' in st.session_state)
st.write("Transcripts Length:", len(st.session_state.get('transcripts', [])))

if 'transcripts' in st.session_state and st.session_state.transcripts:
    # Direct display of raw transcript data
    st.subheader("Raw Transcript Data")
    st.write(st.session_state.transcripts)

    # Download button for transcript data
    transcript_json = json.dumps(st.session_state.transcripts, indent=2)
    st.download_button(
        label="Download Transcript Data",
        data=transcript_json,
        file_name="transcript_data.json",
        mime="application/json"
    )
else:
    st.info("No transcript data available yet. Start a bot session to see transcripts.")

# Add refresh button
if st.button("🔄 Refresh"):
    st.rerun()