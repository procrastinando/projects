import streamlit as st
import os
import sys
import subprocess
import shutil
import tempfile
import time
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# --- Dependency Checks ---
# Wrapped in a function for cleaner startup
def check_dependencies():
    """Checks for necessary libraries and commands."""
    dependencies_ok = True
    try:
        import pysrt
    except ImportError:
        st.error("❌ Error: 'pysrt' library not found. Please install it: `pip install pysrt`")
        dependencies_ok = False

    try:
        from langdetect import detect, LangDetectException, DetectorFactory
        DetectorFactory.seed = 0 # Optional seeding
    except ImportError:
        st.error("❌ Error: 'langdetect' library not found. Please install it: `pip install langdetect`")
        dependencies_ok = False

    try:
        from googletrans import Translator, LANGUAGES
    except ImportError:
        st.error("❌ Error: 'googletrans' library not found. Please install it: `pip install googletrans==4.0.0-rc1`")
        dependencies_ok = False

    if shutil.which("ffmpeg") is None:
        st.error("❌ Error: 'ffmpeg' command not found in PATH.")
        st.error("Please install ffmpeg (https://ffmpeg.org/) and ensure it's added to your system's PATH.")
        dependencies_ok = False

    if not dependencies_ok:
        st.stop() # Stop execution if dependencies are missing

check_dependencies() # Run checks at import time

# --- Constants ---
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv')
TEMP_SUB_DIR_BASE = Path(tempfile.gettempdir()) / "st_sub_extract"
TARGET_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "zh-cn": "Chinese (Simplified)",
    "ru": "Russian",
    "fr": "French",
}
TARGET_LANG_CODES = {v: k for k, v in TARGET_LANGUAGES.items()}
CONFIG_FILE = 'config.yaml'

# --- Helper Functions (Correctly Indented) ---

def find_video_files(directory):
    """Recursively finds video files in a directory."""
    video_files = []
    if not os.path.isdir(directory):
        return [], f"Error: Directory not found: {directory}"
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(VIDEO_EXTENSIONS):
                    video_files.append(os.path.join(root, file))
        if not video_files:
            return [], "Info: No video files found in the specified directory and subdirectories."
        return video_files, f"Found {len(video_files)} video file(s)."
    except Exception as e:
        return [], f"Error: An error occurred while searching for videos: {e}"

def extract_subtitles(video_path, output_dir):
    """Extracts all subtitle tracks from a video file using ffmpeg."""
    os.makedirs(output_dir, exist_ok=True)
    command = [
        'ffmpeg', '-loglevel', 'error', '-i', video_path,
        '-map', '0:s:?', '-c', 'copy', '-vn', '-an',
        os.path.join(output_dir, 'sub%d.srt')
    ]
    extracted_files = []
    error_message = None
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        # Check which files were actually created
        for i in range(20): # Check a reasonable number of potential streams
            potential_file = os.path.join(output_dir, f'sub{i}.srt')
            if os.path.exists(potential_file) and os.path.getsize(potential_file) > 5: # Check size > 5 bytes
                extracted_files.append(potential_file)

        if not extracted_files:
            # Check stderr for clues if no files were extracted
            if "Subtitle codec" in process.stderr and "is not supported for output" in process.stderr:
                error_message = "Warning: Found subtitles, but they might be image-based (like PGS, VOBSUB) and cannot be directly extracted as text (SRT)."
            elif "does not contain any stream" in process.stderr:
                 error_message = "Info: The video file does not appear to contain any embedded subtitle streams."
            else:
                error_message = "Warning: ffmpeg ran, but no subtitle text files were extracted. They might be in an unexpected format."
                # Consider showing ffmpeg output here if needed:
                # st.text_area("ffmpeg output:", process.stderr, height=100)

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr if e.stderr else "No error output captured."
        error_message = f"Error during subtitle extraction with ffmpeg: {stderr_output}"
        # Attempt cleanup
        for i in range(20):
            potential_file = os.path.join(output_dir, f'sub{i}.srt')
            if os.path.exists(potential_file):
                try:
                    os.remove(potential_file)
                except OSError:
                    pass # Ignore removal errors during cleanup
    except Exception as e:
        error_message = f"An unexpected error occurred during extraction: {e}"

    return extracted_files, error_message

def detect_subtitle_language(subtitle_path):
    """Detects the language of an SRT file."""
    try:
        # Need to re-import within function if not guaranteed global after checks
        from langdetect import detect, LangDetectException
        from googletrans import LANGUAGES # Assuming googletrans was imported successfully globally

        subs = pysrt.open(subtitle_path, encoding='utf-8', error_handling='ignore')
        text_sample = " ".join([sub.text.strip() for sub in subs[:50] if sub.text.strip()])
        if not text_sample:
            return "Unknown (empty)"
        lang_code = detect(text_sample)
        lang_name = LANGUAGES.get(lang_code, lang_code)
        return lang_name.capitalize()
    except LangDetectException:
        return "Unknown (detection failed)"
    except FileNotFoundError:
        return "Error: File not found"
    except NameError as ne: # Catch if libraries weren't available
         st.warning(f"Language detection/lookup dependency missing: {ne}")
         return "Error: Lib missing"
    except Exception as e:
        return f"Unknown (error: {type(e).__name__})"

def translate_subtitle(input_srt_path, target_lang_code, output_srt_path, progress_bar=None, status_text=None):
    """Translates an SRT file using Google Translate with progress."""
    try:
        # Need translator inside or ensure it's passed/global
        from googletrans import Translator

        subs = pysrt.open(input_srt_path, encoding='utf-8')
        translator = Translator()
        total_subs = len(subs)
        start_time = time.time()

        if status_text:
            status_text.text(f"Translating 0/{total_subs} lines...")
        if progress_bar:
            progress_bar.progress(0)

        BATCH_SIZE = 10
        translated_count = 0

        for i in range(0, total_subs, BATCH_SIZE):
            batch_subs = subs[i:min(i + BATCH_SIZE, total_subs)]
            texts_to_translate = [sub.text.replace('\n', ' ').strip() for sub in batch_subs if sub.text.strip()]
            original_indices = [idx for idx, sub in enumerate(batch_subs) if sub.text.strip()]

            if not texts_to_translate:
                translated_count += len(batch_subs) # Count skipped empty lines
                continue # Skip empty batches

            try:
                # Add retry logic
                retries = 3
                delay = 1
                translated_batch = None
                last_error = None
                for attempt in range(retries):
                    try:
                        translated_batch = translator.translate(texts_to_translate, dest=target_lang_code)
                        # Minimal check on result structure (list or single object with .text)
                        if isinstance(translated_batch, list):
                             if not all(hasattr(t, 'text') for t in translated_batch):
                                 raise TypeError("Unexpected item format in translated list")
                        elif not hasattr(translated_batch, 'text'):
                             raise TypeError("Unexpected format for single translated item")
                        last_error = None # Reset error on success
                        break # Success
                    except Exception as trans_err_inner:
                        last_error = trans_err_inner
                        if attempt < retries - 1:
                            st.warning(f"Translation attempt {attempt+1} failed: {trans_err_inner}. Retrying in {delay}s...")
                            time.sleep(delay)
                            delay *= 2 # Exponential backoff
                        else:
                            st.error(f"Translation failed after {retries} attempts.")
                            raise last_error # Re-raise the last error

                if last_error: # If loop finished due to errors
                     raise last_error

                # Assign translated text back
                trans_idx = 0
                for batch_idx, sub in enumerate(batch_subs):
                    if batch_idx in original_indices:
                        # Handle list vs single object result from translator
                        current_translation = translated_batch[trans_idx] if isinstance(translated_batch, list) else translated_batch
                        # We already checked for .text attribute above
                        sub.text = current_translation.text
                        trans_idx += 1

                translated_count += len(batch_subs)

                # Update progress
                progress = translated_count / total_subs
                if progress_bar:
                    progress_bar.progress(progress)
                if status_text:
                    elapsed = time.time() - start_time
                    est_total = (elapsed / progress) if progress > 0.01 else 0 # Avoid division by zero early on
                    est_rem = max(0, est_total - elapsed)
                    status_text.text(f"Translating line {translated_count}/{total_subs}... (Est. remaining: {est_rem:.0f}s)")

                # Small delay between batches
                time.sleep(0.3) # 300ms delay per batch

            except Exception as trans_err:
                st.warning(f"Warning: Could not translate batch starting at line {i+1}. Error: {trans_err}. Keeping original text for this batch.")
                # Keep original text for the whole batch on error
                translated_count += len(batch_subs) # Still count as processed for progress
                time.sleep(1) # Longer pause after error

        if progress_bar:
            progress_bar.progress(1.0)
        if status_text:
            status_text.text(f"Translation complete ({total_subs} lines). Saving...")

        subs.save(output_srt_path, encoding='utf-8')
        return True, f"Successfully translated and saved to: {output_srt_path}"

    except FileNotFoundError:
        return False, f"Error: Input subtitle file not found: {input_srt_path}"
    except NameError as ne: # Catch if googletrans wasn't available
         st.error(f"Translation library dependency missing: {ne}")
         return False, "Translation library error."
    except Exception as e:
        # Attempt to remove potentially corrupted output file on error
        if os.path.exists(output_srt_path):
            try:
                os.remove(output_srt_path)
            except OSError:
                pass
        return False, f"An error occurred during translation: {type(e).__name__} - {e}"


# --- Main Application Function ---
def main():
    """Runs the Streamlit application."""
    # --- Authentication ---
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file: # Specify encoding
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        st.error(f"❌ FATAL ERROR: Configuration file '{CONFIG_FILE}' not found.")
        st.info(f"Please create '{CONFIG_FILE}' in the script directory with user credentials.")
        st.stop()
    except yaml.YAMLError as e:
        st.error(f"❌ FATAL ERROR: Error parsing '{CONFIG_FILE}': {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ FATAL ERROR: An unexpected error occurred loading config: {e}")
        st.stop()

    # Basic config validation
    if not isinstance(config, dict) or \
       not all(k in config for k in ['credentials', 'cookie']) or \
       not isinstance(config.get('credentials'), dict) or \
       not isinstance(config['credentials'].get('usernames'), dict) or \
       not isinstance(config.get('cookie'), dict) or \
       not all(k in config['cookie'] for k in ['name', 'key', 'expiry_days']):
           st.error(f"❌ FATAL ERROR: '{CONFIG_FILE}' structure is invalid or missing required keys.")
           st.stop()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Render login form using 'main' location
    authenticator.login('main', fields={'Form name': 'Subtitle Translator Login'})

    # --- Handle Authentication Status ---
    if st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] == None:
        st.warning('Please enter your username and password')
    elif st.session_state["authentication_status"] == True:
        # --- User is Authenticated ---
        # Display Welcome and Logout in Sidebar
        with st.sidebar:
            st.write(f'Welcome, *{st.session_state["name"]}*!') # Use name from authenticator
            authenticator.logout('Logout', 'sidebar', key='logout_button') # Unique key for widget

        # --- Main Application UI ---
        st.title("🎬 Video Subtitle Translator")

        # --- Session State Initialization (for translator logic) ---
        # Initialize if keys don't exist - prevents reset on every rerun within a session
        if 'video_search_path' not in st.session_state: st.session_state.video_search_path = ""
        if 'video_files_list' not in st.session_state: st.session_state.video_files_list = []
        if 'selected_video' not in st.session_state: st.session_state.selected_video = None
        if 'temp_sub_dir' not in st.session_state: st.session_state.temp_sub_dir = None
        if 'extracted_subs_info' not in st.session_state: st.session_state.extracted_subs_info = []
        if 'selected_sub_path' not in st.session_state: st.session_state.selected_sub_path = None
        if 'target_lang_code' not in st.session_state: st.session_state.target_lang_code = None
        if 'translation_running' not in st.session_state: st.session_state.translation_running = False
        if 'last_translated_path' not in st.session_state: st.session_state.last_translated_path = None
        if 'cleanup_done' not in st.session_state: st.session_state.cleanup_done = False

        # --- Step 1: Select Directory ---
        st.header("Step 1: Select Video Directory")
        search_path_input = st.text_input(
            "Enter the full path to the directory containing videos:",
            value=st.session_state.video_search_path,
            placeholder="/path/to/your/videos",
            key="search_path_input" # Unique key
        )

        # Search Button Logic
        if st.button("Search for Videos", key="search_button"):
            # Update state from the input widget *before* using it
            st.session_state.video_search_path = search_path_input
            # Reset downstream state
            st.session_state.video_files_list = []
            st.session_state.selected_video = None
            st.session_state.extracted_subs_info = []
            st.session_state.selected_sub_path = None
            st.session_state.target_lang_code = None
            st.session_state.translation_running = False
            st.session_state.last_translated_path = None
            st.session_state.cleanup_done = False
            # Clean up previous temp dir if exists
            if st.session_state.temp_sub_dir and os.path.exists(st.session_state.temp_sub_dir):
                try:
                    shutil.rmtree(st.session_state.temp_sub_dir)
                    st.toast(f"Cleaned up previous temporary directory: {st.session_state.temp_sub_dir}")
                except OSError as e:
                    st.warning(f"Could not remove previous temp directory {st.session_state.temp_sub_dir}: {e}")
                finally:
                    st.session_state.temp_sub_dir = None # Reset state var

            # Perform the search using the updated path
            if st.session_state.video_search_path and os.path.isdir(st.session_state.video_search_path):
                with st.spinner(f"Searching in '{st.session_state.video_search_path}'..."):
                    videos, message = find_video_files(st.session_state.video_search_path)
                    st.session_state.video_files_list = videos # Store results in state
                    if "Error" in message:
                        st.error(message)
                    elif "Info" in message:
                        st.info(message)
                    else:
                        st.success(message)
                    if not videos:
                        st.warning("No videos found with supported extensions (.mp4, .mkv, .avi, etc.).")
            elif not st.session_state.video_search_path:
                st.warning("Please enter a directory path.")
            else:
                st.error(f"The entered path is not a valid directory: {st.session_state.video_search_path}")
            st.rerun() # Rerun to reflect the changes from the button click


        # --- Step 2: Select Video File ---
        # Only show if videos were found in the previous step
        if st.session_state.video_files_list:
            st.header("Step 2: Select Video File")
            # Prepare options for the selectbox
            sorted_videos = sorted(st.session_state.video_files_list, key=lambda p: os.path.basename(p))
            video_options = {os.path.basename(p): p for p in sorted_videos}
            options_list = list(video_options.keys())

            # Determine the index for the selectbox (try to keep previous selection)
            current_index = 0 # Default to first item
            if st.session_state.selected_video:
                current_basename = os.path.basename(st.session_state.selected_video)
                if current_basename in options_list:
                    try:
                        current_index = options_list.index(current_basename)
                    except ValueError:
                        current_index = 0 # Fallback if name somehow not in list
                else:
                     # If previous selection is no longer in the list, default to 0
                     st.session_state.selected_video = None # Clear invalid selection


            selected_video_basename = st.selectbox(
                "Choose a video file:",
                options=options_list,
                index=current_index,
                key="video_selector" # Unique key
            )

            # Handle selection change
            if selected_video_basename:
                newly_selected_video = video_options[selected_video_basename]
                # Update state and reset downstream if selection changed OR if sub-info is missing
                if newly_selected_video != st.session_state.selected_video or not st.session_state.extracted_subs_info:
                    st.session_state.selected_video = newly_selected_video
                    # Reset subsequent steps' state
                    st.session_state.extracted_subs_info = []
                    st.session_state.selected_sub_path = None
                    st.session_state.target_lang_code = None
                    st.session_state.translation_running = False
                    st.session_state.last_translated_path = None
                    st.session_state.cleanup_done = False
                    # Clean up temp dir from *previous* selection if it exists
                    if st.session_state.temp_sub_dir and os.path.exists(st.session_state.temp_sub_dir):
                        try:
                            shutil.rmtree(st.session_state.temp_sub_dir)
                            st.toast(f"Cleaned previous temp: {st.session_state.temp_sub_dir}")
                        except OSError as e:
                            st.warning(f"Could not remove previous temp dir {st.session_state.temp_sub_dir}: {e}")
                        finally:
                            st.session_state.temp_sub_dir = None # Reset state var
                    st.info(f"Selected video: `{os.path.basename(st.session_state.selected_video)}`")
                    st.rerun() # Rerun to show the next step or update UI

        # --- Step 3: Extract Subtitles and Select Subtitle ---
        # Only show if a video is selected
        if st.session_state.selected_video:
            st.header("Step 3: Extract and Select Subtitle")

            # Button to trigger extraction if not already done for this video
            # And not currently translating
            if not st.session_state.extracted_subs_info and not st.session_state.translation_running:
                if st.button("Extract Subtitles", key="extract_button"):
                    video_filename_stem = Path(st.session_state.selected_video).stem
                    # Ensure temp dir name is filesystem-safe
                    safe_stem = "".join(c for c in video_filename_stem if c.isalnum() or c in (' ', '_', '-')).rstrip()
                    st.session_state.temp_sub_dir = TEMP_SUB_DIR_BASE / safe_stem
                    st.session_state.extracted_subs_info = [] # Clear previous attempts for this step

                    # Perform extraction
                    with st.spinner(f"Extracting from '{os.path.basename(st.session_state.selected_video)}'... (using ffmpeg)"):
                        extracted_files, message = extract_subtitles(st.session_state.selected_video, st.session_state.temp_sub_dir)

                    # Display extraction results
                    if message:
                        if "Error" in message: st.error(message)
                        elif "Warning" in message: st.warning(message)
                        else: st.info(message)

                    # If extraction successful, analyze languages
                    if extracted_files:
                        st.success(f"Found {len(extracted_files)} potential subtitle track(s). Analyzing languages...")
                        subs_info = []
                        # Use st.empty for dynamic progress text is better than progress bar sometimes
                        prog_status = st.empty()
                        for i, sub_file in enumerate(extracted_files):
                             prog_status.text(f"Analyzing subtitle {i+1}/{len(extracted_files)}...")
                             lang = detect_subtitle_language(sub_file)
                             subs_info.append({"path": sub_file, "lang": lang})
                        st.session_state.extracted_subs_info = subs_info # Store results
                        prog_status.empty() # Clear progress text
                        st.rerun() # Rerun to display the selectbox
                    else:
                        # If extraction failed or yielded no files
                        if not message or ("Error" not in message and "Warning" not in message):
                            st.error("Could not extract any text-based subtitle files (e.g., SRT). The video might have no subtitles or only image-based ones.")
                        # Clean up empty temp directory if created and no files extracted
                        if st.session_state.temp_sub_dir and os.path.exists(st.session_state.temp_sub_dir) and not os.listdir(st.session_state.temp_sub_dir):
                            try:
                                shutil.rmtree(st.session_state.temp_sub_dir)
                                st.info("Removed empty temporary directory.")
                            except OSError as e:
                                st.warning(f"Could not remove empty temp dir {st.session_state.temp_sub_dir}: {e}")
                            finally:
                                st.session_state.temp_sub_dir = None # Reset state var

            # Display subtitle selection box if subtitles have been extracted
            if st.session_state.extracted_subs_info:
                sub_options = {}
                display_texts = []
                # Prepare display options
                for i, sub_info in enumerate(st.session_state.extracted_subs_info):
                    try: # Make path relative for display if possible
                        rel_path = Path(sub_info['path']).relative_to(TEMP_SUB_DIR_BASE)
                    except ValueError:
                        rel_path = Path(sub_info['path']).name # Fallback to just filename
                    display_text = f"{i+1}. {rel_path} ({sub_info['lang']})"
                    sub_options[display_text] = sub_info['path'] # Map display text to full path
                    display_texts.append(display_text)

                # Determine index for selectbox (try to maintain selection)
                current_sub_index = 0 # Default to first
                if st.session_state.selected_sub_path:
                    # Find the display text corresponding to the selected path
                    matching_display = [dt for dt, p in sub_options.items() if p == st.session_state.selected_sub_path]
                    if matching_display:
                        try:
                            current_sub_index = display_texts.index(matching_display[0])
                        except ValueError:
                            current_sub_index = 0 # Fallback
                    else:
                         st.session_state.selected_sub_path = None # Clear invalid selection

                selected_sub_display = st.selectbox(
                    "Select the subtitle file to translate:",
                    options=display_texts,
                    index=current_sub_index,
                    key="subtitle_selector" # Unique key
                )

                # Handle subtitle selection change
                if selected_sub_display:
                    newly_selected_sub = sub_options[selected_sub_display]
                    if newly_selected_sub != st.session_state.selected_sub_path:
                        st.session_state.selected_sub_path = newly_selected_sub
                        # Reset only target lang and downstream flags
                        st.session_state.target_lang_code = None
                        st.session_state.translation_running = False
                        st.session_state.last_translated_path = None
                        st.session_state.cleanup_done = False
                        # Get language for info message
                        selected_info = next((info for info in st.session_state.extracted_subs_info if info['path'] == newly_selected_sub), None)
                        selected_lang = selected_info['lang'] if selected_info else "N/A"
                        st.info(f"Selected subtitle: `{Path(st.session_state.selected_sub_path).name}` (Lang: {selected_lang})")
                        st.rerun() # Rerun to show next step

        # --- Step 4: Select Target Language ---
        # Only show if a subtitle file is selected
        if st.session_state.selected_sub_path:
            st.header("Step 4: Select Target Language")
            lang_names_sorted = sorted(list(TARGET_LANGUAGES.values()))

            # Determine index (try to keep selection)
            current_lang_index = None # Means placeholder will show
            if st.session_state.target_lang_code:
                try:
                    current_lang_name = TARGET_LANGUAGES[st.session_state.target_lang_code]
                    current_lang_index = lang_names_sorted.index(current_lang_name)
                except (KeyError, ValueError):
                    st.session_state.target_lang_code = None # Clear invalid state

            target_language_name = st.selectbox(
                "Choose the language to translate to:",
                options=lang_names_sorted,
                index=current_lang_index, # Use index or None
                placeholder="Select target language...", # Shows if index is None
                key="target_lang_selector" # Unique key
            )

            # Handle language selection change
            if target_language_name:
                selected_lang_code = TARGET_LANG_CODES[target_language_name]
                if selected_lang_code != st.session_state.target_lang_code:
                    st.session_state.target_lang_code = selected_lang_code
                    # Reset downstream flags
                    st.session_state.translation_running = False
                    st.session_state.last_translated_path = None
                    st.session_state.cleanup_done = False
                    st.info(f"Target language set to: {target_language_name} ({st.session_state.target_lang_code})")
                    st.rerun() # Rerun to show next step

        # --- Step 5: Translate ---
        # Show button only if all selections made and not currently running
        if st.session_state.target_lang_code and st.session_state.selected_sub_path and not st.session_state.translation_running:
            st.header("Step 5: Translate Subtitle")

            # Get target language name for button label
            target_lang_name = TARGET_LANGUAGES.get(st.session_state.target_lang_code, "Selected Language")

            if st.button(f"Translate to {target_lang_name}", key="translate_button", type="primary"):
                # --- Start Translation Process ---
                st.session_state.translation_running = True
                st.session_state.last_translated_path = None # Clear previous result path
                st.session_state.cleanup_done = False # Reset cleanup flag for this run

                # Prepare paths
                video_path = Path(st.session_state.selected_video)
                original_video_dir = video_path.parent
                video_filename_stem = video_path.stem
                translated_sub_filename = f"{video_filename_stem}-{st.session_state.target_lang_code}.srt"
                final_output_path = original_video_dir / translated_sub_filename

                st.info(f"Starting translation of '{Path(st.session_state.selected_sub_path).name}'...")
                st.info(f"Output file will be: `{final_output_path}`")

                # UI elements for progress
                progress_bar = st.progress(0)
                status_text = st.empty() # Placeholder for status messages

                # Call the translation function
                success, message = translate_subtitle(
                    st.session_state.selected_sub_path,
                    st.session_state.target_lang_code,
                    str(final_output_path), # Ensure path is string
                    progress_bar,
                    status_text
                )

                # Clear progress UI elements
                progress_bar.empty()
                status_text.empty()

                # Display result message
                if success:
                    st.success(message)
                    st.session_state.last_translated_path = str(final_output_path) # Store path on success
                else:
                    st.error(f"Translation Failed: {message}")


                # --- Cleanup Temporary Files ---
                # Happens *after* translation attempt, regardless of success/failure
                if st.session_state.temp_sub_dir and os.path.exists(st.session_state.temp_sub_dir):
                    st.info(f"Cleaning up temporary files from: {st.session_state.temp_sub_dir}")
                    try:
                        shutil.rmtree(st.session_state.temp_sub_dir)
                        st.info("Temporary files removed successfully.")
                    except OSError as e:
                        st.warning(f"Warning: Could not remove temporary directory {st.session_state.temp_sub_dir}: {e}")
                    finally:
                        # Reset temp dir state only after attempting removal
                        st.session_state.temp_sub_dir = None
                        st.session_state.cleanup_done = True # Mark cleanup as done for this round
                else:
                     # If temp dir wasn't set or didn't exist, still mark cleanup as logically done
                     st.session_state.cleanup_done = True


                # --- Reset state for next potential translation ---
                st.session_state.translation_running = False
                # Decide if you want to reset selections after translation or keep them
                # st.session_state.selected_sub_path = None # Uncomment to force re-selection of sub
                # st.session_state.target_lang_code = None # Uncomment to force re-selection of lang
                st.rerun() # Rerun to update UI state (remove button, show results, etc.)


        # --- Display Final Result Link/Info ---
        # Shows if a translation was successfully completed in this session
        if st.session_state.last_translated_path:
            st.markdown("---")
            st.markdown(f"✅ **Last successful translation saved to:** `{st.session_state.last_translated_path}`")
            st.markdown("_(You can find this file in the same folder as the original video.)_")

        # --- Footer Info (inside authenticated block) ---
        st.markdown("---")
        st.caption(f"Logged in as: {st.session_state['username']} | Temp files base: `{TEMP_SUB_DIR_BASE}`")

    # --- End of Authenticated Section (`elif st.session_state["authentication_status"] == True:`) ---

# --- Script Execution Entry Point ---
if __name__ == "__main__":
    main() # Call the main function when the script is run directly