import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import json
import time
from typing import Optional
import requests
import shutil

from app.pipelines.transcript_processing import (
    format_transcript_for_llm,
    merge_into_user_messages,
    load_transcript
)

def get_next_version_number(task_name: str) -> int:
    """Get the next version number for a task."""
    base_dir = Path("app/task_data")
    versions = [d.name for d in base_dir.iterdir()
               if d.is_dir() and d.name.startswith(f"{task_name}_v")]
    if not versions:
        return 1

    # Extract version numbers and find max
    version_numbers = []
    for v in versions:
        try:
            # Extract number between 'v' and '-'
            num = int(v.split('v')[1].split('-')[0])
            version_numbers.append(num)
        except:
            continue

    return max(version_numbers, default=0) + 1

def get_task_folders() -> list[str]:
    """Get all task folders from the app/task_data directory."""
    task_data_path = Path("app/task_data")
    folders = [d.name for d in task_data_path.iterdir()
              if d.is_dir() and not d.name.startswith((".", "__"))]
    # Filter out version folders
    return [f for f in folders if not any(c.isdigit() for c in f)]

def get_task_versions(task_name: str) -> list[str]:
    """Get all versions of a task."""
    base_dir = Path("app/task_data")
    versions = [d.name for d in base_dir.iterdir()
               if d.is_dir() and d.name.startswith(f"{task_name}_v")]
    return sorted(versions, reverse=True)

def get_task_files(task_folder: str) -> dict:
    """Get all files for a specific task folder."""
    task_path = Path(f"app/task_data/{task_folder}")
    return {
        "answer_format": task_path / "answer_format.txt",
        "description": task_path / "description.txt",
        "good_responses": task_path / "good_responses.txt",
        "bad_responses": task_path / "bad_responses.txt",
        "triggers": task_path / "triggers.txt"
    }

def read_file_content(file_path: Path) -> str:
    """Read content from a file."""
    try:
        return file_path.read_text()
    except:
        return ""

def create_new_task(task_name: str):
    """Create a new task with all required files."""
    base_path = Path(f"app/task_data/{task_name}")
    base_path.mkdir(exist_ok=True)

    # Default content for each file
    default_content = {
        "answer_format.txt": "Provide your answer in a clear and concise format.",
        "description.txt": "Enter task description here.",
        "good_responses.txt": "Example of a good response",
        "bad_responses.txt": "Example of a bad response",
        "triggers.txt": "Example trigger"
    }

    # Create each file with default content
    for file_name, content in default_content.items():
        file_path = base_path / file_name
        file_path.write_text(content)

def save_task_version(task_name: str, file_contents: dict) -> str:
    """Save a new version of the task files."""
    version_num = get_next_version_number(task_name)
    timestamp = datetime.now().strftime("%H%M")
    version_name = f"{task_name}_v{version_num}-{timestamp}"
    version_path = Path(f"app/task_data/{version_name}")

    # Create version directory
    version_path.mkdir(exist_ok=True)

    # Save each file with updated content
    for file_name, content in file_contents.items():
        file_path = version_path / f"{file_name}.txt"
        file_path.write_text(content)

    return version_name

def get_available_transcripts() -> list[str]:
    """Get list of available transcripts in logs/transcripts."""
    transcript_path = Path("logs/transcripts")
    return [f.name for f in transcript_path.glob("*.json")]



def test_with_claude(task_version: str, transcript: str):
    """Test the task with Claude using the backend API."""
    url = "http://localhost:8000/api/test_task"  # You'll need to create this endpoint
    data = {
        "task_version": task_version,
        "transcript": transcript
    }
    try:
        response = requests.post(url, json=data, stream=True)
        return response.iter_lines()
    except Exception as e:
        return f"Error: {str(e)}"



def process_transcript(transcript_path: str) -> Optional[str]:
    """Load and process a transcript file."""
    try:
        transcript = load_transcript(f"logs/transcripts/{transcript_path}")
        # Handle the case where transcript might be empty or invalid
        if not transcript or not isinstance(transcript, list):
            return None
        processed = merge_into_user_messages(transcript)
        return format_transcript_for_llm(processed)
    except Exception as e:
        st.error(f"Error processing transcript: {str(e)}")
        return None

def save_temp_version(task_name: str, file_contents: dict) -> str:
    """Save a temporary version for Claude testing."""
    timestamp = datetime.now().strftime("%H%M%S")  # Include seconds for temp versions
    version_name = f"{task_name}_temp-{timestamp}"
    version_path = Path(f"app/task_data/{version_name}")

    # Create temp directory
    version_path.mkdir(exist_ok=True)

    # Save each file with updated content
    for file_name, content in file_contents.items():
        file_path = version_path / f"{file_name}.txt"
        file_path.write_text(content)

    return version_name

def cleanup_temp_versions(task_name: str):
    """Clean up temporary versions that are older than 1 hour."""
    base_dir = Path("app/task_data")
    current_time = datetime.now()

    for path in base_dir.glob(f"{task_name}_temp-*"):
        try:
            # Get timestamp from directory name
            timestamp_str = path.name.split("-")[1]
            version_time = datetime.strptime(timestamp_str, "%H%M%S")

            # If version is from a different day or more than 1 hour old, remove it
            if (current_time - version_time).total_seconds() > 3600:
                shutil.rmtree(path)
        except (IndexError, ValueError):
            continue

def main():
    st.title("Task Builder Manager")

    # Task Selection or Creation
    tasks = get_task_folders()
    tasks.insert(0, "Create New Task")

    selected_task_option = st.selectbox("Select or Create Task", tasks)

    if selected_task_option == "Create New Task":
        with st.form(key="new_task_form"):
            new_task_name = st.text_input("Enter new task name")
            create_submitted = st.form_submit_button("Create Task")

            if create_submitted and new_task_name:
                create_new_task(new_task_name)
                st.success(f"Created new task: {new_task_name}")
                st.rerun()

    elif selected_task_option:
        # Split the screen into two columns
        col1, col2 = st.columns([6, 4])  # Adjust ratio as needed

        with col1:
            # Version Selection at the top
            versions = get_task_versions(selected_task_option)
            if not versions:
                current_task = selected_task_option
                st.info("No versions yet - editing original task")
            else:
                current_task = st.selectbox(
                    "Select Version to Edit",
                    [selected_task_option] + versions,
                    index=0,
                    help="Select original task or a specific version to edit"
                )

            # Get task files after version selection
            task_files = get_task_files(current_task)

            # Create a container for the editor to ensure proper updating
            editor_container = st.container()

            with editor_container:
                st.subheader("Description")
                description = st.text_area(
                    "Description",
                    value=read_file_content(task_files["description"]),
                    height=100,
                    key=f"description_{current_task}"  # Add version to key
                )

                st.subheader("Answer Format")
                answer_format = st.text_area(
                    "Answer Format",
                    value=read_file_content(task_files["answer_format"]),
                    height=100,
                    key=f"answer_format_{current_task}"
                )

                st.subheader("Good Responses")
                good_responses = st.text_area(
                    "Good Responses",
                    value=read_file_content(task_files["good_responses"]),
                    height=100,
                    key=f"good_responses_{current_task}"
                )

                st.subheader("Bad Responses")
                bad_responses = st.text_area(
                    "Bad Responses",
                    value=read_file_content(task_files["bad_responses"]),
                    height=100,
                    key=f"bad_responses_{current_task}"
                )

                st.subheader("Triggers")
                triggers = st.text_area(
                    "Triggers",
                    value=read_file_content(task_files["triggers"]),
                    height=100,
                    key=f"triggers_{current_task}"
                )

                # Save button at the bottom
                if st.button("Save New Version", type="primary"):
                    file_contents = {
                        "description": description,
                        "answer_format": answer_format,
                        "good_responses": good_responses,
                        "bad_responses": bad_responses,
                        "triggers": triggers
                    }
                    new_version = save_task_version(selected_task_option, file_contents)
                    st.success(f"✅ Successfully saved version: {new_version}")
                    time.sleep(1)
                    st.rerun()

        with col2:
            st.subheader("Test with Claude")

            # Transcript Selection and Testing
            transcript_options = get_available_transcripts()
            selected_transcript = st.selectbox(
                "Select Transcript",
                transcript_options,
                key="transcript_select"
            )

            processed_transcript = None
            if selected_transcript:
                processed_transcript = process_transcript(selected_transcript)
                if processed_transcript:
                    transcript_text = st.text_area(
                        "Edit Processed Transcript",
                        processed_transcript,
                        height=300,
                        key="transcript_edit"
                    )

                    if st.button("Test with Claude", type="primary"):
                        st.subheader("Claude Response")

                        # Get current content
                        file_contents = {
                            "description": description,
                            "answer_format": answer_format,
                            "good_responses": good_responses,
                            "bad_responses": bad_responses,
                            "triggers": triggers
                        }

                        # Save as temporary version
                        cleanup_temp_versions(selected_task_option)
                        temp_version = save_temp_version(selected_task_option, file_contents)

                        response_placeholder = st.empty()
                        full_response = ""

                        try:
                            # Stream the response
                            for chunk in test_with_claude(temp_version, transcript_text):
                                if isinstance(chunk, bytes):
                                    chunk = chunk.decode()
                                full_response += chunk
                                response_placeholder.markdown(full_response)
                        except Exception as e:
                            st.error(f"Error testing with Claude: {str(e)}")
if __name__ == "__main__":
    main()