from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook endpoint for Recall AI transcription
@app.route('/api/webhook/recall/transcription', methods=['POST'])
def transcription_webhook():
    data = request.json
    print("Raw data received:", data)  # Log raw data to terminal

    # Save raw data to a log file for debugging or storage
    with open("transcription_events.log", "a") as file:
        file.write(f"{data}\n")

    # Extract meaningful information (if present in the payload)
    transcript_data = data.get("data", {}).get("transcript", {})
    if transcript_data:
        speaker = transcript_data.get("speaker", "Unknown Speaker")
        words = " ".join([word["text"] for word in transcript_data.get("words", [])])
        print(f"Speaker: {speaker}")
        print(f"Transcript: {words}")

        # Save extracted transcript to a readable file
        with open("transcripts.txt", "a") as file:
            file.write(f"Speaker: {speaker}\n")
            file.write(f"Transcript: {words}\n\n")

    # Respond with a success message to the webhook sender
    return jsonify({"message": "Webhook received!"}), 200

if __name__ == "__main__":
    app.run(port=5000)