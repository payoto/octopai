
# JSON Format for Meeting Caption Transcription

This document describes the JSON format used for meeting caption transcription. It is designed to capture the structure, content, and metadata of conversations. Below is an explanation of the key components:

## JSON Structure

The transcription is represented as an array of objects, where each object corresponds to a segment of speech from a specific speaker. Here is an example JSON structure:

```json
[
  {
    "words": [
      {
        "text": "Luke, I am your father.",
        "end_time": 33.04818725585938,
        "start_time": 22.65240478515625,
        "language": null,
        "confidence": null
      }
    ],
    "speaker": "Darth Vader",
    "speaker_id": 200,
    "language": "en"
  },
  ...
]
```

### Explanation of Fields

- **`words`**: An array containing word-level details of the speech segment.
  - **`text`**: The transcribed text.
  - **`start_time`**: The timestamp (in seconds) when the word starts.
  - **`end_time`**: The timestamp (in seconds) when the word ends.
  - **`language`**: The language of the text (e.g., "en" for English). It can be `null` if not available.
  - **`confidence`**: Confidence score for the transcription accuracy. It can be `null` if not available.

- **`speaker`**: The name or identifier of the speaker (e.g., "Darth Vader").
- **`speaker_id`**: A numeric identifier for the speaker.
- **`language`**: The overall language of the transcription segment.

### Example Explanation

In the given example:
- The text "Luke, I am your father." was spoken by Darth Vader.
- The speech started at 22.65 seconds and ended at 33.05 seconds.
- No specific confidence score or language was provided at the word level.

## Additional Resources

For more information about this transcription format and additional features, please visit the official [Recall.ai Documentation](https://docs.recall.ai/docs/meeting-caption-transcription).

This documentation provides comprehensive details on how to use this format effectively, including advanced use cases and API integration.
