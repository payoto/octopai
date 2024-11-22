import requests

def detect_stop_command(text):
    """Check if text contains stop command"""
    return "octopai stop" in text.lower()

def handle_stop_command(api_key, bot_id):
    """Handle stop command by sending response message"""
    response_message = "Why do you want me to stop?"
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/send_chat_message"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key.strip()
    }
    payload = {"message": response_message}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending response: {e}")
        return False

def check_messages(transcripts, chat_messages, api_key, bot_id, processed_messages):
    """Check chat messages for stop command, avoiding duplicates"""
    if chat_messages and isinstance(chat_messages, dict):
        results = chat_messages.get('results', [])
        for msg in results:
            text = msg.get('text', '')
            msg_id = msg.get('created_at', '')  # Using timestamp as unique identifier

            # Only process new messages containing the stop command
            if msg_id not in processed_messages and detect_stop_command(text):
                processed_messages.add(msg_id)
                handle_stop_command(api_key, bot_id)
                return True

    return False