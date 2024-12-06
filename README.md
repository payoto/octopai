# OctopAI Bot

OctopAI is an AI-powered meeting assistant that helps guide conversations and provide relevant information. It joins meetings as a virtual participant and can analyze conversations in real-time.

## Features

The Streamlit UI provides several pages for managing and monitoring the bot:

### Main Page

Start UI before you provide a meeting

![Main page start](docs/screenshots/main_start.png)

Interface as a meeting is running:

![](docs/screenshots/main_conversation.png)

On the left you will find the transcript with the names of the participants and on the
right the actions suggested by OctopAI.


- Create and configure new bot instances
- Monitor live meeting transcripts and bot responses
- Send messages to the meeting chat
- Control bot behavior with toggles for auto-refresh and dummy backend


### Past Conversations

![past conversation UI](docs/screenshots/past_conversations.png)

- Review previous conversations
- Load example conversations
- Upload conversation JSON files

### Backend Monitor (developer)

- View real-time communication between frontend and backend
- Monitor request/response pairs
- Configure refresh intervals
- Check backend connection status

### Chat Messages (developer)

- View raw chat data
- Download chat history

### Raw Transcript Data (developer)

- Access raw transcript data
- Debug session information
- Download transcript data

## Setup Instructions

### Prerequisites

1. System Packages:
```bash
sudo apt install python3 python3-venv build-essential docker-ce docker-ce-cli docker-buildx-plugin docker-compose-plugin
```

2. Account Requirements:
- Recall.ai API key for meeting bot functionality
- Anthropic API key for Claude integration

3. Environment Setup:
```bash
# Clone repository
git clone [repo-url]
cd [repo-name]

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

4. Configuration:
Create `.env` file with:
```
API_KEY=your_recall_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
BACKEND_URL=http://127.0.0.1:8001
```

### Running the Application

1. Start Backend:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Start Frontend:
```bash
cd streamlit
streamlit run main.py
```

## Backend Architecture

The backend follows a modular architecture:

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configurations
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── utils/        # Helper functions
```

Key Components:
- FastAPI for API endpoints
- Anthropic's Claude for conversation analysis
- ChromaDB for vector storage (optional)
- Custom prompt engineering pipeline

Communication Flow:
1. Frontend sends meeting transcripts
2. Backend processes text through prompt pipeline
3. Claude analyzes content and generates responses
4. Processed results returned to frontend

## Action Builder Interface

![Action builder interface](docs/screenshots/task_builder.png)

The Action Builder allows creating new bot behaviors:

1. Start the builder:
```bash
cd backend
streamlit run prompt_builder.py
```

2. Interface features:
- Create/edit action templates
- Define triggers and responses
- Test with sample conversations
- Version control for prompts

3. Action components:
- Description: Action purpose
- Triggers: When to activate
- Response format: Output structure
- Example responses: Good/bad examples

Actions are stored in `app/task_data/` and automatically loaded by the backend.