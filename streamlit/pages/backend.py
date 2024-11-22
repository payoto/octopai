import streamlit as st
import json
from services.bot_service import fetch_transcripts
from services.backend_service import send_to_backend
import time

st.set_page_config(page_title="Backend Monitor", page_icon="🔄", layout="wide")

# Initialize session state for storing request/response history
if 'backend_history' not in st.session_state:
    st.session_state.backend_history = []
if 'last_backend_refresh' not in st.session_state:
    st.session_state.last_backend_refresh = 0

st.title("🔄 Backend Communication Monitor")

# Check for active session
if 'bot_id' in st.session_state and st.session_state.bot_id and 'api_key' in st.session_state:
    # Configuration in sidebar
    st.sidebar.header("Backend Configuration")
    st.sidebar.write("Backend URL:", st.session_state.backend_url)
    st.sidebar.write("Bot ID:", st.session_state.bot_id)
    st.sidebar.write("Meeting URL:", st.session_state.meeting_url)

    # Refresh interval control
    refresh_interval = st.sidebar.slider(
        'Refresh Interval (seconds)',
        min_value=5,
        max_value=60,
        value=10
    )
    st.sidebar.info(f"Refreshing every {refresh_interval} seconds")

    # Main content area
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Latest Request")
    with col2:
        st.subheader("📥 Latest Response")

    # Function to make backend call and update history
    def make_backend_call():
        transcripts = fetch_transcripts(st.session_state.api_key, st.session_state.bot_id)
        if transcripts:
            # Prepare request data
            request_data = {
                "url": st.session_state.meeting_url,
                "host_name": st.session_state.host_name,
                "transcript": transcripts
            }

            try:
                # Make the backend call
                success, response = send_to_backend(
                    st.session_state.backend_url,
                    st.session_state.meeting_url,
                    st.session_state.host_name,
                    transcripts
                )

                # Add to history
                st.session_state.backend_history.insert(0, {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'request': request_data,
                    'response': response,
                    'success': success
                })

                # Keep only last 10 entries
                st.session_state.backend_history = st.session_state.backend_history[:10]

            except Exception as e:
                st.error(f"Error communicating with backend: {str(e)}")

    # Auto-refresh logic
    current_time = time.time()
    if current_time - st.session_state.last_backend_refresh > refresh_interval:
        make_backend_call()
        st.session_state.last_backend_refresh = current_time

    # Display history
    if st.session_state.backend_history:
        for idx, entry in enumerate(st.session_state.backend_history):
            st.write(f"### Communication at {entry['timestamp']}")
            cols = st.columns(2)
            with cols[0]:
                st.write("Request:")
                st.code(json.dumps(entry['request'], indent=2), language='json')
            with cols[1]:
                st.write("Response:")
                if entry['success']:
                    st.success("✅ Success")
                else:
                    st.error("❌ Failed")
                st.code(json.dumps(entry['response'], indent=2), language='json')
            st.divider()
    else:
        st.info("No communication history yet. Waiting for first backend call...")

    # Manual refresh button
    if st.button("🔄 Force Refresh Now"):
        make_backend_call()
        st.rerun()

else:
    st.warning("No active bot session. Please create a bot in the main page first.")

# Add connection status indicator
st.sidebar.markdown("---")
st.sidebar.subheader("Connection Status")
try:
    import requests
    response = requests.get(st.session_state.backend_url)
    if response.status_code == 200:
        st.sidebar.success("✅ Backend is reachable")
    else:
        st.sidebar.warning(f"⚠️ Backend returned status code: {response.status_code}")
except Exception as e:
    st.sidebar.error("❌ Backend is not reachable")
    st.sidebar.write(f"Error: {str(e)}")

# Auto-rerun for continuous updates
time.sleep(1)
st.rerun()