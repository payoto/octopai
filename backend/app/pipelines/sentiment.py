""" Classify the sentiment of the conversation.


"""
from typing import TypedDict, List, Optional, Union, Dict
from typing_extensions import NotRequired  # For Python <3.11
import argparse
import json
import sys
from enum import Enum
import time
import anthropic
import os


from enum import Enum
import pandas as pd

from pathlib import Path
import dotenv


current_folder = Path(__file__).resolve().parent
backend_root = current_folder.parents[1]
dotenv.load_dotenv(backend_root / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class Word(TypedDict):
    text: str
    start_timestamp: float
    end_timestamp: float
    language: Optional[str]
    confidence: Optional[float]

class TranscriptSegment(TypedDict):
    words: List[Word]
    speaker: str
    speaker_id: int
    language: str


# Placeholder sentiments
class SentimentLabel(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

Transcript = List[TranscriptSegment]

# Example usage:
"""
transcript: Transcript = {
    "segments": [
        {
            "words": [
                {
                    "text": "So maybe one thing I want to change",
                    "start_timestamp": 120.07850646972656,
                    "end_timestamp": 133.9397430419922,
                    "language": None,
                    "confidence": None
                }
            ],
            "speaker": "Lukas Gabriel",
            "speaker_id": 100,
            "language": "en-us"
        }
    ]
}
"""

def format_word_for_llm(word: Word):
    # utterance start: {start_timestamp:.2f}s
    format = """
{text}
    """
    # utterance end: {end_timestamp:.2f}s
    return format.format(**word)

def format_segment_for_llm(segment: TranscriptSegment):

    formatted_segment = f"Speaker: {segment['speaker']}\n"
    for word in segment["words"]:
        formatted_segment += format_word_for_llm(word)
    return formatted_segment

def extract_last_minutes(transcript: Transcript, seconds: float) -> List[TranscriptSegment]:
    # Truncate the transcript to the last 5mn
    last_timestamp = transcript[-1]["words"][-1]["end_timestamp"]
    last_timestamp -= seconds
    last_segments = []
    for i, segment in enumerate(transcript):
        if segment["words"][-1]["start_timestamp"] >= last_timestamp:
            last_segments.extend(transcript[i:])
            break
    return last_segments





SENTIMENT_DESCRIPTIONS = {
    "disengaged": "The user seems distracted and uninterested in the conversation, their comments might be off-topic.",
    "confused": "The user appears confused and unsure about the topic.",
    "positive": "The user is expressing positive sentiment and satisfaction.",
    "nervous": "The person is unsure, and hesitates.",
    "connected": "The user is feeling understood by the other participants, has a sense of community",
    "conflictual": "The user is expressing disagreement or conflict.",
    "neutral": "The person is not displaying any particular emotion.",
}

class Sentiment(Enum):
    DISCONNECTED = "disconnected"
    CONFUSED = "confused"
    POSITIVE = "positive"
    NERVOUS = "nervous"
    CONNECTED = "connected"
    CONFLICTUAL = "conflictual"
    NEUTRAL = "neutral"

class SentimentClassificationOutput(TypedDict):
    sentiment: Sentiment | None
    model_sentiment: str
    confidence: float
    explanation: str
    usage: Dict[str, Union[int, float]]
    duration: float


def load_sentiment_examples(csv_path: str) -> Dict[str, Dict[str, Union[str, List[str]]]]:
    df = pd.read_csv(csv_path)
    examples = {}

    for sentiment in df['sentiment'].unique():
        examples[sentiment] = {
            'explanation': SENTIMENT_DESCRIPTIONS[sentiment],
            'examples': df[df['sentiment'] == sentiment]['example'].tolist()
        }

    return examples




def format_sentiment_examples_into_prompt(examples: Dict):
    example_str = ""
    for sentiment, data in examples.items():
        example_separator = '- \n'
        example_str += f"""{sentiment.capitalize()}: {data['explanation']}
Examples:
- {example_separator.join(data['examples'])}
"""
    return example_str



class SentimentClassifier:
    def __init__(self, sentiment_csv_path: str):
        self.examples = load_sentiment_examples(sentiment_csv_path)

        self.system_prompt = """We need to analyse sentiment in the conversation.
        To do that you need to classify the sentiment of the last message in the conversation.
        You are receiving transcripts of the conversation. Call the sentiment_tracker with the sentiments you have identified.
        """
        self.user_prompt_format = """
        Here is a conversation transcript, use it as context for what the sentiment of the last message is:
        <transcript>
        {transcript}
        </transcript>
        This is the message you need to classify:
        <message>
        {message}
        </message>
        """
        self.tool_name = "sentiment_tracker"
        self.model = "claude-3-5-haiku-20241022"
        self.tools = [
            {
                "name": self.tool_name,
                "description": "Keeps track of the sentiment of the conversation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "explanation": {"type": "string", "description": "brief explanation of the classification that was made and highlight the key reason why it was chosen"},
                        # TODO make an array
                        "sentiment": {"type": "string", "description": format_sentiment_examples_into_prompt(self.examples)},
                        "confidence": {"type": "number", "description": "Confidence in the sentiment chosen, 0.0-1.0 (inclusive)"}
                    },
                    "required": ['explanation', 'sentiment', 'confidence']
                }
            }
        ]



    def classify_text(self, transcript: str, message: str) -> SentimentClassificationOutput:
        """
        Classify the sentiment of a single text.

        Args:
            text (str): The text to analyze

        Returns:
            dict: Dictionary containing sentiment classification, confidence score, and explanation
        """
        messages = [
            {"role": "user",
             "content": self.user_prompt_format.format(transcript=transcript, message=message)
             }
        ]
        start = time.time()
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            temperature=0.5,
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_choice = {"type": "tool", "name": self.tool_name}
        )

        assert response.content
        assert response.content[0].type == "tool_use"
        assert response.content[0].name == "sentiment_tracker"
        tool_input = response.content[0].input
        raw_sentiment = str(tool_input["sentiment"]).lower()
        try:
            sentiment = Sentiment[raw_sentiment.upper()]
        except KeyError:
            sentiment = None
        return SentimentClassificationOutput(**{
            "sentiment": sentiment,
            "model_sentiment": raw_sentiment,
            "explanation": str(tool_input["explanation"]),
            "confidence": float(tool_input["confidence"]),
            "api_usage": response.usage.to_json(),
            "duration": time.time() - start,
        })



def classify_sentiment(transcript: Transcript):
    classifier = SentimentClassifier(str(current_folder / "sentiments.csv"))
    transcript_str = ""
    for segment in transcript[:-1]:
        transcript_str += format_segment_for_llm(segment)
    message = format_segment_for_llm(transcript[-1])
    classification = classifier.classify_text(transcript_str, message)
    context = {
        "transcript": transcript_str,
        "message": message,
    }
    return classification, context

def classify_transcript_1by1(transcript: Transcript, output_file: Optional[str] = None) -> List[List[str]]:
    classifications = []
    try:
        # classify each as if it was the last one
        for i, _ in enumerate(transcript):
            last_5mn = extract_last_minutes(transcript[:i+1], 300)
            classification, context = classify_sentiment(last_5mn)
            classifications.append([context["message"], classification])
    finally:
        if output_file:
            print(f"Saving classifications to file {output_file}")
            Path(output_file).write_text(json.dumps(classifications, indent=2))
        else:
            print(json.dumps(classifications, indent=2))
    return classifications

def load_transcript(file_path: str) -> Transcript:
    """Load a transcript from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Process conversation transcripts for sentiment analysis',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--input_file',
        default=str(backend_root / "logs/transcripts/transcript_3.json"),
        type=str,
        help='Path to the transcript JSON file'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to save the analysis results (optional)'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format for the analysis results'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()
    if args.output is None:
        args.output = f"{args.input_file}-sentiment.json"
    # Load the transcript
    transcript = load_transcript(args.input_file)

    if args.verbose:
        print(f"Loaded transcript with {len(transcript)} segments")

    return transcript, args



if __name__ == "__main__":
    transcript, args = main()
    classify_transcript_1by1(transcript, args.output)
