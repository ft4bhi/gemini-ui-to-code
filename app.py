import streamlit as st


import pathlib
from PIL import Image

import time
from tenacity import retry, stop_after_attempt, wait_exponential

import google.generativeai as genai

  # Load environment variables from .env file





genai.configure(api_key='AIzaSyATh9SJ-IWVQfWD8zgdfEc6pXlBrrcqjF0')

# Generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Model name
MODEL_NAME = "gemini-1.5-pro-latest"

# Framework selection (e.g., Tailwind, Bootstrap, etc.)
framework = "Regular CSS use flex grid etc"  # Change as needed

# Create the model
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    safety_settings=safety_settings,
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(history=[])

# Function to send a message to the model with retry logic
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def send_message_to_model(message, image_path=None):
    try:
        if image_path:
            image_input = {
                'mime_type': 'image/jpeg',
                'data': pathlib.Path(image_path).read_bytes()
            }
            response = chat_session.send_message([message, image_input])
        else:
            response = chat_session.send_message([message])
        return response.text
    except Exception as e:
        if "429" in str(e):
            st.warning("API rate limit exceeded. Retrying after a short delay...")
            time.sleep(5)  # Delay before retrying
        raise e

# Function to convert HTML to JSX (text-based conversion only)
def convert_to_jsx(html_code):
    prompt = (
        f"Convert the following HTML code into JSX. Ensure the code is clean, uses React best practices, "
        f"and includes necessary imports. Do not include explanations. Only return the JSX code. Here is the HTML:\n\n{html_code}"
    )
    return send_message_to_model(prompt)  # No image input

# Function to convert HTML to TSX (text-based conversion only)
def convert_to_tsx(html_code):
    prompt = (
        f"Convert the following HTML code into TSX. Ensure the code is clean, uses TypeScript and React best practices, "
        f"and includes necessary types and imports. Do not include explanations. Only return the TSX code. Here is the HTML:\n\n{html_code}"
    )
    return send_message_to_model(prompt)  # No image input

# Streamlit app
def main():
    st.title("Gemini 1.5 Pro, UI to Code 👨‍💻")
    st.subheader('Made with ❤️ by [Skirano](https://x.com/skirano)')

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            # Load and display the image
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image.', use_column_width=True)

            # Convert image to RGB mode if it has an alpha channel
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Save the uploaded image temporarily
            temp_image_path = pathlib.Path("temp_image.jpg")
            image.save(temp_image_path, format="JPEG")

            # Ask the user which code they want to generate
            code_choice = st.radio("Which code do you want to generate?", ("HTML", "JSX", "TSX"))

            if st.button("Generate Code"):
                st.write("🧑‍💻 Analyzing the UI... Please wait.")
                time.sleep(2)  # Delay to prevent rate limits

                # Generate UI description using image input for analysis
                prompt = (
                    "Describe this UI in accurate details. When you reference a UI element put its name and bounding box "
                    "in the format: [object name (y_min, x_min, y_max, x_max)]. Also describe the color of the elements."
                )
                description = send_message_to_model(prompt, str(temp_image_path))
                st.write("**Initial Description:**")
                st.write(description)

                st.write("🔍 Refining description with visual comparison...")
                time.sleep(2)
                refine_prompt = (
                    f"Compare the described UI elements with the provided image and identify any missing elements or inaccuracies. "
                    f"Also describe the color of the elements. Provide a refined and accurate description of the UI elements based on this comparison. "
                    f"Here is the initial description: {description}"
                )
                refined_description = send_message_to_model(refine_prompt, str(temp_image_path))
                st.write("**Refined Description:**")
                st.write(refined_description)

                # Process according to the user's choice
                if code_choice == "HTML":
                    st.write("🛠️ Generating HTML...")
                    time.sleep(2)
                    html_prompt = (
                        f"Create an HTML file based on the following UI description, using the UI elements described in the previous response. "
                        f"Include {framework} CSS within the HTML file to style the elements. Make sure the colors used are the same as the original UI. "
                        f"The UI needs to be responsive and mobile-first, matching the original UI as closely as possible. "
                        f"Do not include any explanations or comments. Avoid using ```html. and ``` at the end. ONLY return the HTML code with inline CSS. "
                        f"Here is the refined description: {refined_description}"
                    )
                    initial_html = send_message_to_model(html_prompt, str(temp_image_path))
                    st.code(initial_html, language='html')

                    st.write("🔧 Refining HTML...")
                    time.sleep(2)
                    refine_html_prompt = (
                        f"Validate the following HTML code based on the UI description and image and provide a refined version of the HTML code with {framework} CSS "
                        f"that improves accuracy, responsiveness, and adherence to the original design. ONLY return the refined HTML code with inline CSS. "
                        f"Avoid using ```html. and ``` at the end. Here is the initial HTML: {initial_html}"
                    )
                    refined_html = send_message_to_model(refine_html_prompt, str(temp_image_path))
                    st.code(refined_html, language='html')

                    with open("index.html", "w") as file:
                        file.write(refined_html)
                    st.success("HTML file 'index.html' has been created.")
                    st.download_button(label="Download HTML", data=refined_html, file_name="index.html", mime="text/html")

                elif code_choice == "JSX":
                    st.write("🔄 Converting HTML to JSX...")
                    time.sleep(2)
                    # Generate initial HTML from the refined description
                    html_prompt = (
                        f"Create an HTML file based on the following UI description, using the UI elements described in the previous response. "
                        f"Include {framework} CSS within the HTML file to style the elements. Make sure the colors used are the same as the original UI. "
                        f"The UI needs to be responsive and mobile-first, matching the original UI as closely as possible. "
                        f"Do not include any explanations or comments. Avoid using ```html. and ``` at the end. ONLY return the HTML code with inline CSS. "
                        f"Here is the refined description: {refined_description}"
                    )
                    initial_html = send_message_to_model(html_prompt, str(temp_image_path))
                    refine_html_prompt = (
                        f"Validate the following HTML code based on the UI description and image and provide a refined version of the HTML code with {framework} CSS "
                        f"that improves accuracy, responsiveness, and adherence to the original design. ONLY return the refined HTML code with inline CSS. "
                        f"Avoid using ```html. and ``` at the end. Here is the initial HTML: {initial_html}"
                    )
                    refined_html = send_message_to_model(refine_html_prompt, str(temp_image_path))
                    
                    # Convert the refined HTML to JSX (without image input)
                    jsx_code = convert_to_jsx(refined_html)
                    st.code(jsx_code, language='javascript')
                    st.download_button(label="Download JSX", data=jsx_code, file_name="App.jsx", mime="text/javascript")

                elif code_choice == "TSX":
                    st.write("🔄 Converting HTML to TSX...")
                    time.sleep(2)
                    # Generate initial HTML from the refined description
                    html_prompt = (
                        f"Create an HTML file based on the following UI description, using the UI elements described in the previous response. "
                        f"Include {framework} CSS within the HTML file to style the elements. Make sure the colors used are the same as the original UI. "
                        f"The UI needs to be responsive and mobile-first, matching the original UI as closely as possible. "
                        f"Do not include any explanations or comments. Avoid using ```html. and ``` at the end. ONLY return the HTML code with inline CSS. "
                        f"Here is the refined description: {refined_description}"
                    )
                    initial_html = send_message_to_model(html_prompt, str(temp_image_path))
                    refine_html_prompt = (
                        f"Validate the following HTML code based on the UI description and image and provide a refined version of the HTML code with {framework} CSS "
                        f"that improves accuracy, responsiveness, and adherence to the original design. ONLY return the refined HTML code with inline CSS. "
                        f"Avoid using ```html. and ``` at the end. Here is the initial HTML: {initial_html}"
                    )
                    refined_html = send_message_to_model(refine_html_prompt, str(temp_image_path))
                    
                    # Convert the refined HTML to TSX (without image input)
                    tsx_code = convert_to_tsx(refined_html)
                    st.code(tsx_code, language='typescript')
                    st.download_button(label="Download TSX", data=tsx_code, file_name="App.tsx", mime="text/typescript")

        except Exception as e:
            if "429" in str(e):
                st.error("API quota exhausted. Please try again later or upgrade your plan.")
            else:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
