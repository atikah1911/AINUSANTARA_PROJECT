# makeup.py

def get_makeup_looks(face_shape):
    makeup_looks = {
        "oval": [
            ("Natural 'No-Makeup' Makeup", """
            This style focuses on enhancing the skin's natural beauty with minimal products. 
            It typically involves a lightweight foundation or tinted moisturizer, subtle blush, and neutral tones for the eyes and lips, creating an effortless and fresh appearance..""",
            "images/natural_makeup.jpg"),
            ("Soft Glam", """Soft glam is a polished yet natural look that emphasizes glowing skin and blended, neutral eyeshadow shades. It combines light layers of makeup, 
            including shimmer and matte finishes, to achieve a soft, ethereal effect that enhances the wearer’s features without appearing heavy or overdone.""",
            "images/soft_glam.jpg"),
            ("Dewy, Glowy Skin", """The dewy glow makeup style aims for a fresh, hydrated look with luminous skin. It incorporates products like liquid highlighters and 
            hydrating foundations to create a radiant finish. This style often features soft blush and glossy lips to enhance the overall glow.""", "images/dewy_glow.jpg"),
            ("Classic Retro", """Classic retro makeup draws inspiration from past decades, often featuring bold winged eyeliner, defined brows, and red lips. 
            This look emphasizes dramatic eye makeup paired with a flawless complexion, evoking vintage glamour reminiscent of the 1950s and 1960s.""",
            "images/classic_retro.jpg")
        ],
        "square": [
            ("Soft Glam", """Soft glam is a polished yet natural look that emphasizes glowing skin and blended, neutral eyeshadow shades. It combines light layers of makeup, 
                        including shimmer and matte finishes, to achieve a soft, ethereal effect that enhances the wearer’s features without appearing heavy or overdone.""",
             "images/soft_glam.jpg"),
            ("Classic Retro", """Classic retro makeup draws inspiration from past decades, often featuring bold winged eyeliner, defined brows, and red lips. 
                        This look emphasizes dramatic eye makeup paired with a flawless complexion, evoking vintage glamour reminiscent of the 1950s and 1960s.""",
             "images/classic_retro.jpg"),
            ("Smokey Eye", """"The smoky eye is characterized by dark, blended eyeshadow that creates depth and drama around the eyes. 
            This style can range from subtle to bold, often using shades like black, gray, or deep brown to achieve a sultry effect, 
            typically complemented by nude or soft lip colors.""", "images/smokey_eye.jpg"),
            ("Thai Makeup", "Bright colors bring out features while contouring softens the jawline.", "images/thai_makeup.jpg")
        ],
        "round": [
            ("Arabic Makeup", """Arabic makeup is known for its boldness and emphasis on the eyes. 
            It often includes dramatic eyeliner (such as kohl), heavy eyeshadow in rich colors, and full lashes. 
            The lips are usually kept more neutral or lightly colored to balance the striking eye makeup, creating a captivating overall appearance.""",
             "images/arabic_makeup.jpg"),
            ("Smokey Eye", """"The smoky eye is characterized by dark, blended eyeshadow that creates depth and drama around the eyes. 
                        This style can range from subtle to bold, often using shades like black, gray, or deep brown to achieve a sultry effect, 
                        typically complemented by nude or soft lip colors.""", "images/smokey_eye.jpg"),
            ("Dewy, Glowy Skin", """The dewy glow makeup style aims for a fresh, hydrated look with luminous skin. It incorporates products like liquid highlighters and 
                        hydrating foundations to create a radiant finish. This style often features soft blush and glossy lips to enhance the overall glow.""",
            "images/dewy_glow.jpg"),
            ("Soft Glam", """Soft glam is a polished yet natural look that emphasizes glowing skin and blended, neutral eyeshadow shades. It combines light layers of makeup, 
                        including shimmer and matte finishes, to achieve a soft, ethereal effect that enhances the wearer’s features without appearing heavy or overdone.""",
             "images/soft_glam.jpg"),
        ]
    }

    if face_shape.lower() in makeup_looks:
        return makeup_looks[face_shape.lower()]
    else:
        return None
