import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from openai import OpenAI
from googleapiclient.discovery import build
import re
from analysis import get_seasonal_palette
from tutorial import generate_makeup_tutorial, display_makeup_tutorial
from makeup import get_makeup_looks
from shop import get_makeup_products, display_recommendations, filter_shades

st.set_page_config(page_title="Glossiere: AI Beauty Assistant", layout="wide")

# Initialize API clients
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_API_KEY'))

class ComprehensiveMakeupAdvisor:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def analyze_image(self, image):
        # Convert PIL Image to cv2 format
        cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)

        # Detect face
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None, "No face detected"

        # Analyze the largest face
        x, y, w, h = max(faces, key=lambda x: x[2] * x[3])
        face = cv2_image[y:y + h, x:x + w]

        # Skin tone analysis
        skin_tone, skin_info = self.analyze_skin_tone(face)

        # Face shape analysis
        face_shape = self.analyze_face_shape(w, h)

        # Eye color analysis
        eye_color = self.analyze_eye_color(gray[y:y + h, x:x + w], face)

        return {
            "skin_tone": skin_tone,
            "skin_category": skin_info[0],
            "undertone": skin_info[1],
            "face_shape": face_shape,
            "eye_color": eye_color
        }, "Success"

    def analyze_skin_tone(self, face):
        # Convert to YCrCb color space
        ycrcb_image = cv2.cvtColor(face, cv2.COLOR_BGR2YCrCb)

        # Define skin color bounds
        lower_skin = np.array([0, 135, 85])
        upper_skin = np.array([255, 180, 135])

        # Create and apply skin mask
        skin_mask = cv2.inRange(ycrcb_image, lower_skin, upper_skin)
        skin = cv2.bitwise_and(face, face, mask=skin_mask)

        if np.sum(skin_mask) > 0:
            skin_tone = cv2.mean(skin, mask=skin_mask)[:3]
            rgb_skin_tone = tuple(reversed([int(c) for c in skin_tone]))
            category = self.determine_skin_category(rgb_skin_tone)
            undertone = self.determine_undertone(rgb_skin_tone)
            return rgb_skin_tone, (category, undertone)

        return None, (None, None)

    def determine_skin_category(self, rgb_color):
        luminance = 0.299 * rgb_color[0] + 0.587 * rgb_color[1] + 0.114 * rgb_color[2]
        categories = [
            (200, 'very_light'), (180, 'light'), (160, 'light_medium'),
            (140, 'medium'), (120, 'medium_deep'), (100, 'deep'), (0, 'very_deep')
        ]
        for threshold, category in categories:
            if luminance > threshold:
                return category
        return 'very_deep'

    def determine_undertone(self, rgb_color):
        r, g, b = rgb_color
        if r > g and r > b:
            return 'warm'
        elif b > r and b > g:
            return 'cool'
        return 'neutral'

    def analyze_face_shape(self, width, height):
        face_ratio = width / height
        if face_ratio > 0.95:
            return "Round"
        elif face_ratio < 0.85:
            return "Oval"
        return "Square"

    def analyze_eye_color(self, gray_face, color_face):
        eyes = self.eye_cascade.detectMultiScale(gray_face)
        if len(eyes) > 0:
            ex, ey, ew, eh = eyes[0]
            eye = color_face[ey:ey + eh, ex:ex + ew]
            average_color = np.mean(eye, axis=(0, 1))
            _, g, r = average_color
            return "Brown" if r > g else "Blue/Green"
        return "Unable to detect"

    def suggest_makeup_colors(self, analysis_result):
        skin_category = analysis_result['skin_category']
        undertone = analysis_result['undertone']

        return {
            'foundation': self.adjust_foundation_color(skin_category),
            'blush': self.adjust_blush_color(skin_category, undertone),
            'eyeshadow': self.adjust_eyeshadow_color(skin_category, undertone),
            'lipstick': self.adjust_lipstick_color(skin_category, undertone)
        }

    def adjust_foundation_color(self, category):
        base_colors = {
            'very_light': [(255, 235, 220), (255, 233, 215), (255, 230, 210)],
            'light': [(245, 225, 210), (245, 223, 205), (245, 220, 200)],
            'light_medium': [(235, 215, 200), (235, 213, 195), (235, 210, 190)],
            'medium': [(225, 205, 190), (225, 203, 185), (225, 200, 180)],
            'medium_deep': [(215, 195, 180), (215, 193, 175), (215, 190, 170)],
            'deep': [(205, 185, 170), (205, 183, 165), (205, 180, 160)],
            'very_deep': [(195, 175, 160), (195, 173, 155), (195, 170, 150)]
        }
        return base_colors.get(category, base_colors['medium'])

    def adjust_blush_color(self, category, undertone):
        if undertone == 'warm':
            return [(255, 190, 180), (255, 150, 130), (255, 160, 122)]
        elif undertone == 'cool':
            return [(255, 192, 203), (255, 182, 193), (219, 112, 147)]
        return [(255, 192, 203), (255, 160, 122), (255, 228, 225)]

    def adjust_eyeshadow_color(self, category, undertone):
        if undertone == 'warm':
            return [(255, 222, 173), (210, 180, 140), (188, 143, 143)]
        elif undertone == 'cool':
            return [(230, 230, 250), (216, 191, 216), (221, 160, 221)]
        return [(245, 222, 179), (222, 184, 135), (210, 180, 140)]

    def adjust_lipstick_color(self, category, undertone):
        if undertone == 'warm':
            return [(255, 125, 100), (255, 99, 71), (205, 92, 92)]
        elif undertone == 'cool':
            return [(219, 112, 147), (255, 0, 127), (199, 21, 133)]
        return [(255, 160, 122), (205, 92, 92), (250, 128, 114)]


def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def main():
    # Custom CSS for changing sidebar background and text color
    st.markdown(
        """
        <style>
        /* Change the background color of the sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffc8dd; /* Sidebar background color */
        }

       /* Change the text color in the entire sidebar */
    [data-testid="stSidebar"] * {
        color: #023047 !important; /* Sidebar text color */
    }

        /* Change the color of the header in the sidebar */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #ffafcc; /* Sidebar header text color */
        }

        /* Change selectbox text color in the sidebar */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            color: white; /* Selectbox text color */
        }

        /* Optional: Change the font of the sidebar */
        [data-testid="stSidebar"] {
            font-family: Verdana, Verdana;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Inject CSS to change the selectbox appearance
    st.markdown("""
        <style>
        /* Change selectbox background */
        div[data-baseweb="select"] > div {
            background-color: #ffcccc;
            color: black; /* Text color inside selectbox */
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Glossièrè: AI Beauty Assistant 💄")
    st.image("/Users/nuraziraatikah/Library/Mobile Documents/com~apple~CloudDocs/PART 5/AI NUSANTARA/makeup2.jpg", width=800)
    emoji_text = "Hello! Let's get started with your beauty analysis. 💃"
    st.markdown(emoji_text)
    st.markdown("""
            This tool uses computer vision to analyze your skin tone
            and match it to the most flattering color palette for you. 
            It will then suggest you makeup products and tutorials that suits your face without having to pay!
            """)
    with st.sidebar:
        st.title("Welcome to Glossièrè 💋 ")
        st.header("How It Works")
        st.markdown("""
        This app analyzes your facial features, suggests personalized makeup colors, and provides tutorials!
        1. Upload a photo or use your camera
        2. Select your skin type and occasion
        3. Get personalized seasonal palettes, makeup shades, tutorials, suggestions and products
        """)

        st.header("Tips for Best Results")
        st.markdown("""
        1. Use natural lighting for your photo
        2. Face the camera directly
        3. Remove any makeup before taking the photo
        4. Ensure your face is clearly visible and not obscured
        5. Adjust your camera settings to capture a clear and natural image
        """)

    advisor = ComprehensiveMakeupAdvisor()


    # Image input
    col1, col2 = st.columns(2)
    with col1:
        input_option = st.radio("Choose input method:", ['Upload Image', 'Use Camera'])

    with col2:
        skin_type = st.selectbox("Select your skin type:", ["Normal", "Dry", "Oily", "Combination", "Sensitive"])
        occasion = st.selectbox("Select the occasion:", ["Everyday", "Work", "Date Night", "Wedding", "Party"])

    image = None
    if input_option == 'Upload Image':
        uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
    else:
        camera_image = st.camera_input("Take a picture")
        if camera_image is not None:
            image = Image.open(camera_image)

    if image is not None:
        with st.spinner('Analyzing your features...'):
            # Display original image
            st.subheader("Your Image")
            st.image(image, width=200)

            # Analyze image
            analysis_result, message = advisor.analyze_image(image)

            if analysis_result is not None:
                # Display analysis results
                st.subheader("Analysis Results")
                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"Skin Tone: {analysis_result['skin_category'].replace('_', ' ').title()}")
                col2.write(f"Undertone: {analysis_result['undertone'].title()}")
                col3.write(f"Face Shape: {analysis_result['face_shape']}")
                col4.write(f"Eye Color: {analysis_result['eye_color']}")

                # Create tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs(
                    ["Seasonal Palette", "Make Up Shades", "Tutorials", "Make Up Suggestions", "Shop"])

                with tab1:
                    st.header("Face Analysis")
                    st.subheader("Suitable Seasonal Colour Palette")
                    results = get_seasonal_palette(analysis_result['undertone'])

                    st.write(results["analysis"])

                    for palette_name, palette_data in results["palettes"].items():
                        st.write(f"Colors for {palette_name.capitalize()}:")
                        st.image(palette_data["image"], caption=f"{palette_name.capitalize()} Palette",
                                 use_column_width=True)

                with tab2:
                    # Get and display color palette
                    st.header("Suggested Makeup Palette")
                    makeup_palette = advisor.suggest_makeup_colors(analysis_result)

                    for category, colors in makeup_palette.items():
                        st.write(f"#### {category.title()}")
                        cols = st.columns(len(colors))
                        for idx, color in enumerate(colors):
                            hex_color = rgb_to_hex(color)
                            cols[idx].markdown(f"""
                            <div style="text-align: center;">
                                <div style="background-color: {hex_color}; width: 50px; height: 50px; margin: 0 auto; border: 1px solid black;"></div>
                                <p style="margin: 5px 0;">RGB: {color}</p>
                                <p style="margin: 0;">HEX: {hex_color}</p>
                            </div>
                            """, unsafe_allow_html=True)

                with tab3:
                    st.header("Personalized Makeup Tutorial")

                    # Inputs for makeup tutorial
                    skin_tone = st.selectbox("Select your skin tone:",
                                             ["Very Light", "Light", "Light Medium", "Medium", "Medium Deep", "Deep",
                                              "Very Deep"])
                    skin_condition = st.selectbox("Select your skin condition:",
                                                  ["Normal", "Dry", "Oily", "Combination", "Sensitive"])
                    occasion = st.selectbox("Select the occasion:", ["Everyday", "Work", "Date Night", "Special Event"])

                    if st.button("Generate Makeup Tutorial"):
                        tutorial = generate_makeup_tutorial(skin_tone, skin_condition, occasion)
                        display_makeup_tutorial(tutorial)

                    with tab4:
                        st.title("Makeup Looks by Face Shape")

                        face_shape = st.selectbox("Select your face shape:", ["Oval", "Square", "Round"])

                        if face_shape:
                            looks = get_makeup_looks(face_shape)

                            if looks:
                                st.subheader(f"Suitable Makeup Looks for {face_shape} Face Shape:")
                                for look, description, img_path in looks:
                                    # Create two columns: one for the image and one for the text
                                    col1, col2 = st.columns([1, 2])
                                    # Load the image
                                    try:
                                        image = Image.open(img_path)
                                        # Resize the image
                                        image = image.resize((300, 350))  # Set desired width and height
                                        with col1:
                                            st.image(image, caption=look, use_column_width=False)
                                    except FileNotFoundError:
                                        with col1:
                                            st.write("Image not found. Please check the path.")

                                    with col2:
                                        st.write(f"**{look}**: {description}")

                            else:
                                st.write("Please select a valid face shape.")

                    with tab5:
                        st.header("Recommended Makeup Products")

                        brand = st.selectbox(
                            "Select a brand",
                            options=['Maybelline', 'Revlon', 'L\'Oreal', 'Dior', 'Covergirl', 'Clinique', 'NYX',
                                     'e.l.f.',
                                     'MAC', 'Fenty Beauty'],
                            index=0
                        )
                        product_type = st.selectbox(
                            "Select a product type",
                            options=['lipstick', 'foundation', 'eyeshadow', 'mascara', 'blush', 'bronzer'],
                            index=0
                        )

                        if st.button("Get Product Recommendations"):
                            products = get_makeup_products(brand, product_type)
                            if products:
                                display_recommendations(products, analysis_result['skin_category'],
                                                        analysis_result['undertone'])
                            else:
                                st.write("No products found. Try changing your preferences.")

    st.markdown("---")


if __name__ == "__main__":
    main()


