project/
├── create_bot.py         # Script to create the bot
├── webhook_server.py     # Webhook server to handle real-time events
├── requirements.txt      # Dependencies (e.g., Flask, requests)

# How to Set Up and Start the Bot

This guide provides step-by-step instructions to set up and run the Recall AI bot with real-time transcription. Follow these steps carefully to get everything up and running.

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python (3.8 or later)** Download and install Python from python.org.
2. **Pip (Python package manager)** Pip is included with Python. Verify installation with:

```bash
pip --version
```

3. **Basic Tools**:
   * A terminal or command-line interface.
   * An API key for the Recall AI platform (obtained from the Recall Dashboard).

## Step 1: Clone the Repository

If this project is in a repository, clone it to your local machine:

```bash
git clone <repository-url>
cd <repository-name>
```

## Step 2: Install Dependencies

Ensure all required libraries are installed. Install dependencies listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Step 3: Create a `.env` File

Store your sensitive data, such as the API key and meeting URL, in a `.env` file for security.

1. Create a `.env` file in the project root directory:

```bash
touch .env
```

2. Open the `.env` file and add the following:

```plaintext
API_KEY=your-api-key-here
MEETING_URL=https://meet.google.com/your-meeting-url
```

Replace `your-api-key-here` with your Recall AI API key and `https://meet.google.com/your-meeting-url` with a valid Google Meet URL.

## Step 4: Run the Bot Creation Script

The script `create_bot.py` creates a bot and links it to a meeting.

1. Run the script:

```bash
python create_bot.py
```

2. If successful, you will see a message like this:

```plaintext
Bot created successfully! Bot ID: <bot-id>
```

Save the **Bot ID** for future reference.

## Step 5: Set Up a Webhook Server (Optional)

If you want to receive real-time transcription data, set up a webhook server.

1. Open the file `webhook_server.py`.
2. Run the server:

```bash
python webhook_server.py
```

3. Expose the webhook server to the internet using a tool like **ngrok**:

```bash
ngrok http 5000
```

4. Update the `destination_url` in `create_bot.py` to point to your `ngrok` URL.

## Step 6: Test the Setup

1. Start the meeting at the specified `MEETING_URL`.
2. The bot will join the meeting and start recording.
3. If the webhook is set up, transcription data will be logged in real-time.

## Step 7: Fetch Transcription Data

After the meeting ends, fetch the transcription using the Bot ID:

1. Run the following script to fetch the transcript:

```bash
python fetch_transcript.py
```

2. You will see the transcription output, which you can save or process further.

## Common Issues and Troubleshooting

### 1. Bot Not Joining the Meeting
* Ensure the `MEETING_URL` is valid and for a supported platform (e.g., Google Meet, Zoom).
* Verify your API key is correct.

### 2. Webhook Not Receiving Events
* Confirm your webhook server is running and accessible.
* Verify the `destination_url` in `create_bot.py` matches the public URL of your webhook server.

### 3. Missing Dependencies
* Reinstall dependencies:

```bash
pip install -r requirements.txt
```