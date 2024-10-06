
import os
import re
from openai import OpenAI
from googleapiclient.discovery import build
import streamlit as st

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_API_KEY'))

def generate_makeup_tutorial(skin_tone, skin_condition, occasion):
    prompt = f"""
    Generate a detailed makeup tutorial for someone with the following characteristics:
    - Skin tone: {skin_tone}
    - Skin condition: {skin_condition}
    - Occasion: {occasion}

    Please include the following sections, with a YouTube search query for each:
    1. Skin Preparation
    2. Foundation and Concealer
    3. Eyes
    4. Cheeks
    5. Lips
    6. Final Touches

    For each section, provide a brief explanation followed by a YouTube search query in the format:
    [YouTube Search: your search query here]

    Ensure that each search query is specific to the step, skin tone, and occasion.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional makeup artist providing tailored tutorials."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def get_youtube_video(query):
    try:
        search_response = youtube.search().list(
            q=query,
            type='video',
            part='id,snippet',
            maxResults=1
        ).execute()

        if 'items' in search_response and search_response['items']:
            video_id = search_response['items'][0]['id']['videoId']
            video_title = search_response['items'][0]['snippet']['title']
            embed_html = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
            return video_title, embed_html
        else:
            return None, None

    except Exception as e:
        st.error(f"Error fetching YouTube video: {str(e)}")
        return None, None

def display_makeup_tutorial(tutorial):
    sections = re.split(r'\d+\.', tutorial)[1:]  # Skip the first empty split
    for section in sections:
        lines = section.strip().split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:])

        st.markdown(f"### {title}")

        search_match = re.search(r'\[YouTube Search: (.*?)\]', content)
        if search_match:
            search_query = search_match.group(1)
            content = re.sub(r'\[YouTube Search: .*?\]', '', content).strip()

            st.write(content)

            video_title, embed_html = get_youtube_video(search_query)
            if video_title and embed_html:
                st.write(f"**Video Tutorial:** {video_title}")
                st.markdown(embed_html, unsafe_allow_html=True)
            else:
                st.write("No relevant video found for this step.")
        else:
            st.write(content)
