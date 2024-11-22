""" Classify the sentiment of the conversation.


"""
from typing import TypedDict, List, Optional, Union
from typing_extensions import NotRequired  # For Python <3.11
import argparse
import json
import sys
from enum import Enum

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


import anthropic
from typing import List, Dict, Union
import os
from enum import Enum
import json
from services.anthropic_service import client

class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

EXAMPLE_SENTIMENTS = {
    "disengaged": {
        "explanation": "The user seems disengaged and uninterested in the conversation.",
        "examples": [
            "I don't care about this.",
            "Sure.",
            "Whatever."
        ]
    },
    "confused": {
        "explanation": "The user appears confused and unsure about the topic.",
        "examples": [
            "I'm not sure what you mean.",
            "Can you explain that again?",
            "I don't understand."
        ]
    },
    "positive": {
        "explanation": "The user is expressing positive sentiment and satisfaction.",
        "examples": [
            "Interesting!",
            "I hadn't thought of that before.",
            "Great idea!",
            "I'll try that",
        ]
    },
    "conflictual": {
        "explanation": "The user is expressing disagreement or conflict.",
        "examples": [
            "That's really not a good idea.",
            "Why would you do that?",
            "That's the stupidest idea I've heard all day. (Dismissive & Belittling)",
            "Let me stop you right there because you're completely wrong. (Aggressive Interruption)",
            "Everyone knows you only got this position because of politics. (Personal Attack)"
            "Oh, look who finally decided to contribute something. (Passive-Aggressive)",
        ]
    }
}

def format_sentiment_examples_into_prompt(examples=EXAMPLE_SENTIMENTS):
    example_str = ""
    for sentiment, data in examples.items():
        example_separator = '- \n'
        example_str += f"""{sentiment.capitalize()}: {data['explanation']}"
Examples:
- {example_separator.join(data['examples'])}
"""



class SentimentClassifier:
    def __init__(self):
        """
        Initialize the sentiment classifier with an Anthropic API key.

        Args:
            api_key (str, optional): Anthropic API key. If not provided, will look for ANTHROPIC_API_KEY env variable.
        """
        # enumerate all sentiments listed in enum
        sentiments = ", ".join(s.value for s in Sentiment)

        self.client = client
        self.system_prompt = """We need to analyse sentiment in the conversation.
        To do that you need to classify the sentiment of the last message in the conversation.
        You are receiving transcripts of the conversation. Call the sentiment_tracker with the sentiments you have identified.
        """

        tools = [
            {
                "name": "sentiment_tracker",
                "description": """Keeps track of the sentiment of the conversation
                """,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "explanation": {"brief explanation of the classification that was made and highlight the key reason why it was chosen"},
                        "sentiment": {"type": "string", "description": format_sentiment_examples_into_prompt(EXAMPLE_SENTIMENTS)},
                        "confidence": {"type": "number", "description": "Confidence in the sentiment chosen, 0.0-1.0 (inclusive)"}
                    },
                    "required": ['explanation', 'sentiment', 'confidence']
                }
            }
        ]



    def classify_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Classify the sentiment of a single text.

        Args:
            text (str): The text to analyze

        Returns:
            dict: Dictionary containing sentiment classification, confidence score, and explanation
        """
        message = f"Analyze the sentiment of the following text: {text}"

        response = self.client.messages.create(
            model="claude-3_-sonnet-20240229",
            max_tokens=1024,
            temperature=0,
            system=self.system_prompt,
            messages=[{"role": "user", "content": message}]
        )

        try:
            result = json.loads(response.content[0].text)
            return result
        except json.JSONDecodeError:
            raise ValueError("Failed to parse API response as JSON")

    def batch_classify(self, texts: List[str], batch_size: int = 10) -> List[Dict[str, Union[str, float]]]:
        """
        Classify sentiment for multiple texts in batches.

        Args:
            texts (List[str]): List of texts to analyze
            batch_size (int): Number of texts to process in each batch

        Returns:
            List[dict]: List of classification results for each text
        """
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = [self.classify_text(text) for text in batch]
            results.extend(batch_results)
        return results

def main2():
    # Example usage
    classifier = SentimentClassifier()

    # Single text classification
    text = "I absolutely love this product! It exceeds all my expectations."
    result = classifier.classify_text(text)
    print(f"\nSingle text classification:")
    print(f"Text: {text}")
    print(f"Result: {json.dumps(result, indent=2)}")

    # Batch classification
    texts = [
        "This is terrible, I want my money back!",
        "The product arrived on time and works as expected.",
        "I'm not sure how I feel about this yet."
    ]
    results = classifier.batch_classify(texts)
    print(f"\nBatch classification results:")
    for text, result in zip(texts, results):
        print(f"\nText: {text}")
        print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()


def classify_sentiment(transcript: Transcript):
    """
    """

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
        'input_file',
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

    # Load the transcript
    transcript = load_transcript(args.input_file)

    if args.verbose:
        print(f"Loaded transcript with {len(transcript['segments'])} segments")

    return transcript, args



if __name__ == "__main__":
    transcript, args = main()
    for segment in extract_last_minutes(transcript, 300):
        print(format_segment_for_llm(segment))