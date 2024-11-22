import requests
from flask import Flask, request
from dotenv import load_dotenv
import os
import time
import json

# Reload environment variables
load_dotenv(override=True)

# Load environment variables
API_KEY = os.getenv("API_KEY")
MEETING_URL = input("Enter the meeting URL: ")

# Debug: Print environment variables
print(f"Loaded API_KEY: {API_KEY}")
print(f"Loaded MEETING_URL: {MEETING_URL}")

# Check for missing variables
if not API_KEY or not MEETING_URL:
    raise ValueError("Missing one or more required environment variables (API_KEY, MEETING_URL).")

#app = Flask(__name__)

#@app.route('/api/webhook/recall/transcription', methods=['POST'])
# def transcription_webhook():
#     """
#     Endpoint to handle transcription events from Recall AI.
#     """
#     data = request.json
#     print("Received transcription event:", data)

#     # Save raw data to a log file
#     with open("transcription_events.log", "a") as file:
#         file.write(f"{data}\n")

#     # Extract meaningful transcription data
#     transcript_data = data.get("data", {}).get("transcript", {})
#     if transcript_data:
#         is_final = transcript_data.get("is_final", False)
#         if is_final:  # Only process final results
#             speaker = transcript_data.get("speaker", "Unknown Speaker")
#             words = " ".join([word["text"] for word in transcript_data.get("words", [])])
#             print(f"FINAL - Speaker: {speaker}")
#             print(f"FINAL - Transcript: {words}")

#             # Save formatted transcription to a readable file
#             with open("final_transcripts.txt", "a") as file:
#                 file.write(f"Speaker: {speaker}\n")
#                 file.write(f"Transcript: {words}\n\n")

#     return jsonify({"message": "Webhook received!"}), 200


#print(response.text)

def create_bot():
    """
    Function to create a bot with meeting captions transcription enabled.
    """
    url = "https://us-west-2.recall.ai/api/v1/bot"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {API_KEY}"
    }
    payload = {
        "transcription_options": {
            "provider": "meeting_captions"  # Use native meeting captions
        },
        "meeting_url": MEETING_URL,
        "bot_name": "octopai",
        "chat": {
            "on_bot_join": {
                "send_to": "everyone",
                "message": "Hello! I'm octpai I am here to help you."
            }
        }
    }

    # Debugging: Log payload
    print("Payload:", payload)

    response = requests.post(url, headers=headers, json=payload)

    # Debugging: Log response
    print("Response status code:", response.status_code)
    print("Response text:", response.text)

    if response.status_code in [200, 201]:
        data = response.json()
        print("Bot created successfully!")
        return data['id']
    else:
        print("Failed to create bot.")
        return None

def send_messages(bot_id, message):
    """
    Function to create a bot with meeting captions transcription enabled.
    """
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/send_chat_message"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {API_KEY}"
    }
    payload = {
        "message": message
    }

    response = requests.post(url, headers=headers, json=payload)

    # Debugging: Log response
    print("Response status code:", response.status_code)

    if response.status_code in [200, 201]:
        data = response.json()
        print("Message sent successfully!")
        return data['id']
    else:
        print("Failed to send a message.")
        return None

def fetch_transcripts(bot_id):
    """
    Function to fetch transcripts for a specific bot ID.
    """
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/transcript"
    headers = {
        "accept": "application/json",
        "Authorization": f"Token {API_KEY}"
    }

    print(f"Fetching transcripts for bot ID: {bot_id}...")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Transcripts fetched successfully!")
        print(data)

        # Save transcripts to a file
        with open("transcripts.json", "w") as file:
            file.write(json.dumps(data))
    else:
        print(f"Failed to fetch transcripts. Status code: {response.status_code}")
        print(response.text)

def get_chat_messages(bot_id):
    """
    Function to get chat for a specific bot ID.
    """

    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/chat-messages/"

    headers = {
        "accept": "application/json",
        "Authorization": f"Token {API_KEY}"
    }

    print(f"Fetching chat for bot ID: {bot_id}...")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Chat fetched successfully!")
        print(data)

        # Save chat to a file
        with open("chat.json", "w") as file:
            file.write(json.dumps(data))
    else:
        print(f"Failed to chat transcripts. Status code: {response.status_code}")
        print(response.text)

def monitor_bot(bot_id):
    """
    Monitor bot status and fetch transcripts after meeting ends.
    """
    url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Token {API_KEY}"
    }
    test_message_sent = False

    print(f"Monitoring bot status for ID: {bot_id}...")
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status_changes", [])[-1]["code"]
            print(f"Current bot status: {status}")

            # Check if meeting has ended
            if status == "in_call_recording" or status == "done":
                print("Meeting ended. Fetching transcripts...")
                print("Fetching chat...")
                fetch_transcripts(bot_id)
                get_chat_messages(bot_id)
                if status == "done":
                    break
                if test_message_sent == False:
                    print("Sending test message...")
                    send_messages(bot_id, "Test message.")
                    test_message_sent = True
        else:
            print(f"Failed to monitor bot. Status code: {response.status_code}")
            print(response.text)
            break

        time.sleep(10)  # Wait before polling again

if __name__ == "__main__":
    print("Creating bot...")
    bot_id = create_bot()
    if bot_id:
        print(f"Bot is running with ID: {bot_id}")

        # Monitor bot and fetch transcripts automatically after meeting ends
        monitor_bot(bot_id)
    else:
        print("Failed to create bot.")
