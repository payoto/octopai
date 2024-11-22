from models import TranscriptSegment, Transcript, Word
import json
import sys


def load_transcript(file_path: str) -> Transcript:
    """Load a transcript from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}", file=sys.stderr)
        sys.exit(1)


def format_word_for_llm(word: Word):
    # utterance start: {start_timestamp:.2f}s
    format = """
{text}
    """
    # utterance end: {end_timestamp:.2f}s
    return format.format(**word)


def format_segment_for_llm(segment: TranscriptSegment):
    formatted_segment = f"Speaker: {segment['speaker']}"
    if segment["words"]:
        formatted_segment += f" ({segment['words'][0]['start_timestamp']:.2f}s - {segment['words'][-1]['end_timestamp']:.2f}s)"
    formatted_segment += "\n"
    for word in segment["words"]:
        formatted_segment += format_word_for_llm(word)
    return formatted_segment


def merge_into_user_messages(transcript: Transcript) -> Transcript:
    """Merge neighbouring segments from the same user into a single segment"""
    new_transcript = []
    current_segment = None
    for segment in transcript:
        if current_segment is None:
            current_segment = segment
        elif segment["speaker"] == current_segment["speaker"]:
            current_segment["words"].extend(segment["words"])
        else:
            new_transcript.append(current_segment)
            current_segment = segment
    if current_segment is not None:
        new_transcript.append(current_segment)
    return new_transcript


def format_transcript_for_llm(transcript: Transcript) -> str:
    formatted_transcript = ""
    for segment in transcript:
        formatted_transcript += format_segment_for_llm(segment)
    return formatted_transcript

def extract_last_minutes(
    transcript: Transcript, seconds: float
) -> list[TranscriptSegment]:
    # Truncate the transcript to the last 5mn
    last_timestamp = transcript[-1]["words"][-1]["end_timestamp"]
    last_timestamp -= seconds
    last_segments = []
    for i, segment in enumerate(transcript):
        if segment["words"][-1]["start_timestamp"] >= last_timestamp:
            last_segments.extend(transcript[i:])
            break
    return last_segments
