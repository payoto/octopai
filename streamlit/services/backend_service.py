import requests
from typing import Tuple, Dict, Any
import json
import streamlit as st

def send_to_backend(backend_url: str, meeting_url: str, host_name: str, transcripts: list, dummy: bool) -> Tuple[bool, Any]:
    """
    Send meeting data to the backend

    Returns:
        Tuple[bool, Any]: (success, response/error_message)
            - If successful: (True, response_data)
            - If failed: (False, error_message)
    """
    if "_stored_backend_messages" not in st.session_state:
        st.session_state._stored_backend_messages = []
    try:
        payload = {
            "url": meeting_url,
            "host_name": host_name,
            "transcript": transcripts,
            "fake": dummy,
        }

        response = requests.post(
            f"{backend_url}/api/meeting",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )

        response.raise_for_status()
        annotations = []
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                annotations.append(process_chunk(chunk))
        st.session_state._stored_backend_messages.extend(annotations)
        # Try to parse response as JSON
        return True, st.session_state._stored_backend_messages

    except requests.exceptions.RequestException as e:
        return False, {
            "error": str(e),
            "payload_sent": payload
        }

def process_chunk(chunk: bytes):
    # Implement your logic to process each chunk here
    return json.loads(chunk.decode('utf-8'))
