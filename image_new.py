from PIL import Image, ImageFont, ImageDraw
import requests
import io
import base64
import random
import os

def get_font(font_source: str, size: int):
    """Loads a font from a URL or local file with a given size."""
    if font_source.startswith("http"):
        try:
            response = requests.get(font_source, stream=True)
            response.raise_for_status()
            font_bytes = io.BytesIO(response.content)
            return ImageFont.truetype(font_bytes, size)
        except Exception as e:
            print(f" Error loading font from {font_source}: {e}")
            return ImageFont.load_default()
    else:
        try:
            return ImageFont.truetype(font_source, size)
        except Exception as e:
            print(f" Error loading local font {font_source}: {e}")
            return ImageFont.load_default()

def find_best_font_size(text, font_source, card_size, padding=20):
    """Finds the best font size dynamically for a given word."""
    font_size = 400
    steps = [20] * 10 + [10] * 6 + [5] * 8 + [2] * 50
    for step in steps:
        font = get_font(font_source, font_size)
        text_width, text_height = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font)[2:]
        if text_width + padding < card_size[0] and text_height + padding < card_size[1]:
            return font_size
        font_size -= step
    return 50

def create_gradient_bg(size, color1, color2):
    """Creates a gradient background."""
    img = Image.new("RGB", size, color1)
    draw = ImageDraw.Draw(img)
    for i in range(size[1]):
        r = int(color1[0] + (color2[0] - color1[0]) * (i / size[1]))
        g = int(color1[1] + (color2[1] - color1[1]) * (i / size[1]))
        b = int(color1[2] + (color2[2] - color1[2]) * (i / size[1]))
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))
    return img

def generate_flashcard(text: str):
    """Creates a flashcard for a given text with random styling."""
    CARD_SIZE = (600, 400)
    OUTPUT_FOLDER = "flashcards"
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    FONTS = {
    "Berkshire Swash": "https://github.com/google/fonts/raw/main/ofl/berkshireswash/BerkshireSwash-Regular.ttf",
    "Bungee Tint": "https://github.com/google/fonts/raw/main/ofl/bungeetint/BungeeTint-Regular.ttf",
    # "Concert One": "https://github.com/google/fonts/raw/main/ofl/concertone/ConcertOne-Regular.ttf",
    "Cookie": "https://github.com/google/fonts/raw/main/ofl/cookie/Cookie-Regular.ttf",
    "Courgette": "https://github.com/google/fonts/raw/main/ofl/courgette/Courgette-Regular.ttf",
    # "Gravitas One": "GravitasOne-Regular.ttf",
    # "Lilita One": "https://github.com/google/fonts/raw/main/ofl/lilitaone/LilitaOne-Regular.ttf",
    "Protest Riot": "https://github.com/google/fonts/raw/main/ofl/protestriot/ProtestRiot-Regular.ttf",
    "Satisfy": "Satisfy-Regular.ttf",
    "Yatra One": "https://github.com/google/fonts/raw/main/ofl/yatraone/YatraOne-Regular.ttf"
}
    
    font_name, font_source = random.choice(list(FONTS.items()))
    color1 = random.choice([(255, 87, 34), (33, 150, 243), (76, 175, 80)])
    color2 = random.choice([(255, 193, 7), (233, 30, 99), (156, 39, 176)])
    
    img = create_gradient_bg(CARD_SIZE, color1, color2)
    best_font_size = find_best_font_size(text, font_source, CARD_SIZE)
    font = get_font(font_source, best_font_size)
    draw = ImageDraw.Draw(img)
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_baseline = bbox[1]
    
    x = (CARD_SIZE[0] - text_width) // 2
    y = (CARD_SIZE[1] - text_height) // 2 - text_baseline // 2
    draw.text((x, y), text, font=font, fill="white")
    
    # file_path = os.path.join(OUTPUT_FOLDER, f"{text}.png")
    # img.save(file_path)
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    print(f"✅ Flashcard created: font {font_name} and size {best_font_size}")
    
    return img_base64

