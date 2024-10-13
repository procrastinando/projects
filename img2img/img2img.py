import streamlit as st
import time
from PIL import Image
import os

# Function to load an image with a default fallback
def load_image(image_file, default_file):
    if image_file is not None:
        return Image.open(image_file)
    else:
        return Image.open(default_file)

def main():
    st.title("img2img generator using API App")

    st.sidebar.markdown("""
    ## Code Explanation

    ## [Original repository](https://github.com/procrastinando/img2img-automatic1111-API)

    This Python script performs image inpainting using a web API. It uses the `requests` library to send images as base64 strings to the API and retrieves the processed image.

    ### Key Components

    1. **Image Loading**:
    - `load_image_as_base64(image_path)`: Reads an image file and encodes it in base64.

    2. **File Paths**:
    - `image_path` and `mask_path`: Specify paths for the input image and the mask image.

    3. **Payload Creation**:
    - Constructs a JSON payload with parameters for the inpainting process, including:
        - Input image and mask.
        - Prompts for inpainting and configuration settings (like width, height, steps).

    4. **API Request**:
    - Sends a POST request to the API endpoint for inpainting.

    5. **Response Handling**:
    - Parses the JSON response to extract the generated image.
    - Decodes the image data from base64.

    6. **Output**:
    - Saves the output image to a specified file.

    ### Requirements
    - **Dependencies**: `requests` library.
    - **API Access**: The inpainting API must be running locally on `http://127.0.0.1:7860`.
    - **Input Files**: Ensure that the input image and mask exist at the specified paths.
    - **Output Directory**: The output directory `augmented` should exist to save the processed image.
    """)

    # Define the default API URL
    api_url = st.text_input("WebUI API URL (automatic1111)", value="http://127.0.0.1:7860")
    text_prompt = st.text_input("Text prompt for img2img", value="tree leaves")

    col1, col2 = st.columns(2)

    with col1:
        steps = st.slider("Steps", min_value=1, max_value=150, value=20)
        cfg_scale = st.slider("CFG Scale", min_value=1.0, max_value=30.0, value=7.0, step=0.5)
        width = st.number_input("Width", min_value=64, max_value=2048, value=512, step=64)
        height = st.number_input("Height", min_value=64, max_value=2048, value=512, step=64)

    with col2:
        denoising_strength = st.slider("Denoising Strength", min_value=0.0, max_value=1.0, value=0.75, step=0.05)
        mask_blur = st.slider("Mask Blur", min_value=0, max_value=64, value=4)
        inpainting_mask_invert = st.checkbox("Invert Mask")

    # Upload an image (with default fallback)
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    image = load_image(uploaded_image, "img2img/base.png")
    st.image(image, caption="Base Image", use_column_width=True)

    # Upload a mask (with default fallback)
    uploaded_mask = st.file_uploader("Upload Mask", type=["png", "jpg", "jpeg"])
    mask = load_image(uploaded_mask, "img2img/mask.png")
    st.image(mask, caption="Mask Image", use_column_width=True)

    # Run button
    if st.button("Run"):
        with st.spinner('Processing...'):
            time.sleep(5)  # Simulate waiting for processing

        # Show the resulting image
        if os.path.exists("img2img/img2img.png"):
            result_image = Image.open("img2img/img2img.png")
            st.image(result_image, caption="Result Image (img2img/img2img.png)", use_column_width=True)
        else:
            st.warning("Result image not found.")

if __name__ == "__main__":
    main()