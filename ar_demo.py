import streamlit as st
import pandas as pd
from enum import Enum
import tempfile
import os
import requests

# Define the specificity enum
class Specificity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"

def process_video(video_path, prompt, process_audio, specificity):
    """
    This function will process the video based on the inputs.
    Replace this with your actual processing logic.

    Returns:
        list of dicts: Each dict contains event details with keys:
        start_time, end_time, location, description, index
    """
    # API endpoint
    url = "https://api.va.landing.ai/v1/tools/activity-recognition"

    # Headers
    headers = {
        "Authorization": f"Basic {os.environ["VA_KEY"]}"
    }

    # Open and read the video file
    with open(video_path, "rb") as video_file:
        # Send POST request with video file
        files = {
            "video": (os.path.basename(video_path), video_file, "video/mp4")
        }

        data = {
            "prompt": prompt,
            "specificity": specificity,
            "with_audio": process_audio
        }

        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data
        )

    # Check if request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        error_response = {
            "data":
                {
                    "error": response.text,
                    "status_code": response.status_code,
                    "events": []
                }
        }
        return str(error_response)


def main():
    st.title("Activity/Entity Recognition Demo App")

    # File upload
    video_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

    # String prompt
    prompt = st.text_input(
        "Enter prompt for analysis:",
        help="Describe what activities or entities you want to identify in the video. If you have multiple activities separate then by semicolon(;)",
    )

    # Process audio checkbox
    process_audio = st.checkbox("Process audio", value=True)

    # Specificity slider
    specificity = st.select_slider(
        "Specificity",
        options=[s.value for s in Specificity],
        value=Specificity.MEDIUM.value,
        help="Setting this low will give you list of all found events (high recall), Setting this high will give you list of events with high confidence (high precision).",
    )

    # Create a container for video player
    video_container = st.empty()

    # Results container
    results_container = st.container()

    # Initialize session state
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "results" not in st.session_state:
        st.session_state.results = {}
        st.session_state.events = []
    if "temp_video_path" not in st.session_state:
        st.session_state.temp_video_path = None

    # Run button
    if st.button("Run Analysis"):
        if video_file is not None:
            with st.spinner("Processing video..."):
                # Save the uploaded video to a temporary file
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tfile.write(video_file.read())
                video_path = tfile.name
                st.session_state.temp_video_path = video_path

                # Call the processing function
                st.session_state.results = process_video(
                    video_path,
                    prompt,
                    process_audio,
                    specificity
                )

                # Convert to DataFrame for display
                if st.session_state.results:
                    st.session_state.events = st.session_state.results["data"]["events"]
                    st.session_state.current_index = 0
        else:
            st.error("Please upload a video file")

    # Display results if available
    with results_container:
        if st.session_state.events:
            df = pd.DataFrame(st.session_state.events)
            st.subheader("Analysis Results")
            st.dataframe(df)

            # Navigation buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Previous Event"):
                    st.session_state.current_index = max(0, st.session_state.current_index - 1)

            with col2:
                if st.button("Next Event"):
                    st.session_state.current_index = min(
                        len(st.session_state.events) - 1,
                        st.session_state.current_index + 1
                    )

            # Show current event details
            if 0 <= st.session_state.current_index < len(st.session_state.events):
                current = st.session_state.events[st.session_state.current_index]
                st.subheader(f"Event {st.session_state.current_index + 1}/{len(st.session_state.events)}")
                st.write(f"Description: {current['description']}")
                st.write(f"Location: {current['location']}")
                st.write(f"Time: {current['start_time']:.2f}s - {current['end_time']:.2f}s")

                # Display video at current timestamp
                if st.session_state.temp_video_path and os.path.exists(st.session_state.temp_video_path):
                    with video_container:
                        start = int(current["start_time"])
                        end = int(current["end_time"])
                        if start == end:
                            end = start + 1
                        st.video(
                            st.session_state.temp_video_path,
                            start_time=start,
                            end_time=end,
                        )

        # Show the raw json response from the processing function
        st.subheader("Raw JSON Response")
        st.json(st.session_state.results, expanded=True)


if __name__ == "__main__":
    main()
