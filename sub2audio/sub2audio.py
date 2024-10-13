import os
from datetime import datetime
import time
import streamlit as st

def process_srt(file, output_dir, description, model_size):
    progress_bar = st.progress(0)
    for i in range(6):
        progress_bar.progress((i + 1) / 6)
        time.sleep(1)

def process_text(text, output_dir, description, model_size):
    progress_bar = st.progress(0)
    for i in range(1):
        progress_bar.progress((i + 1) / 1)
        time.sleep(6)

def combine_audio_files(input_dir, output_file):
    time.sleep(2)

# Streamlit UI
def main():
    st.title("SRT/Text to Audio Converter App")

    st.sidebar.markdown("""
    This code is a Streamlit application that converts SRT subtitle files or text into audio files using the Parler-TTS model. Here's a brief technical description of what it does and the libraries it uses:

    ## [Original repository](https://github.com/procrastinando/subtitle-to-audio)

    ### Libraries Used
    - **streamlit**: For creating the web application interface.
    - **os**: For directory and file operations.
    - **torch**: For utilizing PyTorch, especially for GPU acceleration.
    - **parler_tts**: For text-to-speech model.
    - **transformers**: For tokenization and feature extraction.
    - **soundfile**: For writing audio files.
    - **subprocess**: For running external processes (e.g., ffmpeg).
    - **pysrt**: For handling SRT subtitle files.
    - **tempfile**: For creating temporary files.
    - **datetime**: For generating timestamps.

    ### Functions
    1. **process_srt(file, output_dir, description, model_size)**:
    - Loads an SRT file and processes each subtitle to generate corresponding audio files.
    - Uses Parler-TTS for text-to-speech conversion.
    - Saves the generated audio files in the specified output directory.

    2. **process_text(text, output_dir, description, model_size)**:
    - Processes a given text input to generate an audio file.
    - Uses Parler-TTS for text-to-speech conversion.
    - Saves the generated audio file in the specified output directory.

    3. **combine_audio_files(input_dir, output_file)**:
    - Combines multiple audio files into a single audio file using ffmpeg.
    - Ensures the audio files are in the correct order.

    ### Streamlit UI
    - Provides a user interface for uploading SRT files or entering text.
    - Allows users to specify voice descriptions and model sizes.
    - Displays progress and plays the generated audio file upon completion.

    ### Required Libraries
    - Lists the required Python libraries and provides installation instructions.

    ### Example Usage
    - Users can upload an SRT file or enter text, specify voice descriptions, and run the conversion process to generate and combine audio files.
    """)

    st.markdown("""
    ## How to Create a Good Description

    1. **Voice Quality**: Use "very clear audio" for high-quality audio or "very noisy audio" for background noise.
    2. **Prosody Control**: Use punctuation (e.g., commas) to add small breaks in speech.
    3. **Speech Features**: Directly control gender, speaking rate, pitch, and reverberation through the prompt.
    4. **Available Voices**: Jon, Lea, Gary, Jenna, Mike, Laura (use these names in your description for consistency)

    **Example**: "Jon's voice is very clear audio, with a slow speaking rate and low pitch. The recording has minimal reverberation."
    """)

    input_type = st.radio("Choose input type:", ["subtitle", "text"])

    if input_type == "subtitle":
        uploaded_file = st.file_uploader("Choose an SRT file", type="srt")
    else:
        text_input = st.text_area("Enter your text:", value='Hello, everyone! This is an example of Text-to-Speech technology. It converts written text into spoken words, making information accessible and engaging. Imagine the possibilities for education, accessibility, and entertainment!', height=200)

    default_description = "A female speaker delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."
    description = st.text_input("Enter voice description:", value=default_description)

    model_size = st.selectbox("Choose model size:", ["mini", "large"])

    if st.button("RUN"):
        # Generate unique output filename based on current date and time
        current_time = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
        output_file = 'sub2audio/out.mp3'
        output_dir = os.path.join("output", current_time)
        
        progress_bar = st.progress(0)
        
        if input_type == "subtitle" and uploaded_file is not None:
            st.write("Processing subtitles...")
            process_srt(uploaded_file, output_dir, description, model_size)
        elif input_type == "text" and text_input:
            st.write("Processing text...")
            process_text(text_input, output_dir, description, model_size)
        else:
            st.error("Please provide input (either upload an SRT file or enter text).")
            st.stop()
        
        # Combine audio files
        st.write("Combining audio files...")
        combine_audio_files(output_dir, output_file)
        
        st.write("Processing complete!")
        
        # Check if the output file exists before trying to play it
        if os.path.exists(output_file):
            st.audio(output_file)
        else:
            st.error(f"Error: The output file {output_file} was not created. Please check the logs for more information.")

if __name__ == "__main__":
    main()
