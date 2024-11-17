from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/webhook/recall/transcription', methods=['POST'])
def transcription_webhook():
    data = request.json
    print("Received transcription event:")
    print(data)
    return jsonify({"message": "Webhook received!"}), 200

if __name__ == "__main__":
    app.run(port=5000)
