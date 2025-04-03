import streamlit as st
import random
import string
import io
import os
import base64
from streamlit_extras.stylable_container import stylable_container
import keras_hub
from image_new import generate_flashcard
from gemini_image import generate_flashcard_image
from google.cloud import texttospeech
import tensorflow as tf

st.set_page_config(layout="wide")

client_speech = texttospeech.TextToSpeechClient()
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=1
)

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-O",
)

gemma_model = keras_hub.models.Gemma3CausalLM.from_preset("gemma3_instruct_12b_text")

def get_items(clicked_texts):
    sentence = " ".join(clicked_texts) if clicked_texts else ""

    if not sentence:
        prompt = "Give me 12 common words for an AAC app. Output as a Python list: ['word1', 'word2', ...]"
    else:
        prompt = (
           f"This is an AAC application. Given the sentence: '{sentence}', what are the 12 most likely next words the user might want to pick? "
           "Reply only with a Python list: ['word1', 'word2', ...]"
        ) 

    response = gemma_model.generate(prompt, max_length=100)
    start = response.find('[')
    end = response.find(']')
    word_list = response[start + 1:end].strip().split(',')

    # Clean up the words
    final_words = [word.strip().strip("'\"") for word in word_list]

    next_items = []
    for i, word in enumerate(final_words):
        img_base64 = generate_flashcard_image(word)

        if not img_base64:  # Fallback to generate_flashcard() if no image was generated
            img_base64 = generate_flashcard(word)

        img_url = f"data:image/jpeg;base64,{img_base64}" if img_base64 else ""

        next_items.append({
            "id": i,
            "label": word,
            "image_url": img_url
        })

    return next_items

# Session state for clicked texts
if "clicked_texts" not in st.session_state:
    st.session_state.clicked_texts = []

# Function to handle button clicks
def on_click(label):
    st.session_state.clicked_texts.append(label)


def create_button_grid(items, columns=4):
    rows = len(items) // columns + (len(items) % columns > 0)
    with st.container():
        for row in range(rows):
            cols = st.columns(columns)
            for col in range(columns):
                idx = row * columns + col
                if idx < len(items):
                    item = items[idx]
                    with cols[col]:
                        with st.container(border=True):
                            
                            st.image(item['image_url'], use_container_width=True)
                            st.button(
                                item['label'],
                                key='button_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)),
                                on_click=lambda label=item['label']: on_click(label),
                                use_container_width=True
                            )

def text_to_speech(text):
    tts = gTTS(text)
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio


# Main UI
def main():
    st.title("AAC Tool for  Autism Using Keras Gemma 3")

    # Style
    st.markdown(
        """
        <style>
        textinput, input {
            font-size: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([6, 1])
    with col1:
        st.text_input("Your sentence so far:", value=" ".join(st.session_state.clicked_texts), key="text_bar")
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.clicked_texts = []

    # Display AAC options
    items = get_items(st.session_state.clicked_texts)[:12]  # show only top 12
    if st.button("Genreate Audio of Text", type="primary",use_container_width=True ):
        text = st.session_state.clicked_texts
        if text:
            input_text = texttospeech.SynthesisInput(text=" ".join(text))
            response = client_speech.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )
            st.audio(
                f"data:audio/mp3;base64,{base64.b64encode(response.audio_content).decode()}", format="audio/mp3"
            )
    create_button_grid(items, columns=4)

if __name__ == "__main__":
    main()
