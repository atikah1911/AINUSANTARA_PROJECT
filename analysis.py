
import re
from openai import OpenAI
import os
from PIL import Image, ImageDraw
import io
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def create_color_image(colors, width=400, height=100):
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)

    for i, color in enumerate(colors):
        draw.rectangle([i * (width // len(colors)), 0, (i + 1) * (width // len(colors)), height], fill=color)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr

def get_seasonal_palette(prompt):
    system_prompt = '''
    You are a skin expert, you will be given an undertone of a skin such as cool, neutral and warm undertone.
    Seasonal palette consists of Spring, Autumn, Summer and Winter.
    Suggest a few seasonal palettes that suit the undertone and briefly describe the seasonal palette.'''

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=300,
    )
    seasonal_analysis = response.choices[0].message.content
    seasonal_analysis_lower = seasonal_analysis.lower()
    palette_names = list(set(re.findall(r'(spring|summer|autumn|winter)', seasonal_analysis_lower)))

    seasonal_palettes = {
        "spring": ["#F8E0E0", "#FA8072", "#FFE4C4", "#FFFFE0"],
        "summer": ["#E0FFFF", "#AFEEEE", "#ADD8E6", "#87CEEB"],
        "autumn": ["#F0E68C", "#FFA07A", "#CD853F", "#A0522D"],
        "winter": ["#FFFFFF", "#DCDCDC", "#A9A9A9", "#696969"]
    }

    results = {
        "analysis": seasonal_analysis,
        "palettes": {}
    }

    for palette_name in palette_names:
        colors = seasonal_palettes.get(palette_name, [])
        palette_image = create_color_image(colors)
        results["palettes"][palette_name] = {
            "colors": colors,
            "image": palette_image
        }

    return results


