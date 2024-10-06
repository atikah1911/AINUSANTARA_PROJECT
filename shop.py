# shop.py
import streamlit as st
import requests

def get_makeup_products(brand=None, product_type=None):
    url = "https://makeup-api.herokuapp.com/api/v1/products.json"
    params = {}

    if brand:
        params["brand"] = brand.lower()
    if product_type:
        params["product_type"] = product_type.lower()

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def filter_shades(product, skin_category, undertone):
    suitable_shades = []
    for shade in product.get('product_colors', []):
        shade_name = shade.get('colour_name', '').lower()

        if (skin_category in shade_name or undertone in shade_name) or ("universal" in shade_name):
            suitable_shades.append(shade)

    return suitable_shades


def display_recommendations(products, skin_category, undertone):
    st.write(f"**Recommended products for {skin_category.replace('_', ' ').title()} skin tone and {undertone} undertone:**")
    for product in products:
        st.write(f"**{product['name']}**")
        st.write(f"**Brand**: {product['brand'].title()}")
        st.write(f"**Price**: {product.get('price', 'Not available')}")
        st.write(f"**Category**: {product.get('category', 'Not available')}")
        st.write(f"**Product Type**: {product['product_type'].title()}")
        st.write(f"**Link**: [Product Page]({product['product_link']})")
        st.image(product.get('image_link', ''))

        suitable_shades = filter_shades(product, skin_category, undertone)
        if suitable_shades:
            st.write("**Recommended Shades for Your Skin Tone**:")
            for shade in suitable_shades:
                st.write(f"- {shade['colour_name'].title()} ({shade['hex_value']})")
                st.markdown(f"<div style='background-color:{shade['hex_value']}; width:50px; height:50px;'></div>",
                            unsafe_allow_html=True)
        else:
            st.write("No specific shade recommendations found.")
        st.write("---")
