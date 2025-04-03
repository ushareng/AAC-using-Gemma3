import base64
import os
import mimetypes
import io
from google import genai
from google.genai import types


def generate_flashcard_image(word):
    """Generates a vector image with the given word for flashcards and returns base64-encoded image data."""
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    model = "gemini-2.0-flash-exp-image-generation"
    
    prompt = (
        "Create a vector image for the word given below to be used in flash cards. "
        "Create an image of smaller size. Write the name of the word followed by the image. "
        "The image should be there along with the word, not just a description. "
        "Keep the image dimensions in a 2:3 ratio.DO NOT GENERATE TEXT BASED IMAGES\n"
        f"Word - {word}"
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        response_modalities=["image", "text"],
        #response_mime_type="image/png",  # Ensures image output
    )

    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        if (
            chunk.candidates 
            and chunk.candidates[0].content 
            and chunk.candidates[0].content.parts
        ):
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            if inline_data:
                img_bytes = inline_data.data  

                # Convert binary image data to base64
                return base64.b64encode(img_bytes).decode("utf-8")

    return None  


if __name__ == "__main__":
    word = "Apple" 
   

