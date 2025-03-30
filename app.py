import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
import requests  # Import requests library for making YouTube API calls
from dotenv import load_dotenv
import yt_dlp

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if not GEMINI_API_KEY:
    st.error("API key is missing! Add it to your .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_video_id(url):
    """Extracts the video ID from various YouTube URL formats."""
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None  # Invalid URL

def get_youtube_transcript(video_id):
    """Fetches transcript of a YouTube video with improved error handling using yt_dlp fallback."""
    try:
        # Try fetching transcript using YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception as e:
        # If YouTubeTranscriptApi fails, try yt_dlp
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'writesubtitles': True,
                'subtitleslangs': ['en'],
                'writeautomaticsub': True,
                'outtmpl': '%(id)s.%(ext)s'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                if 'automatic_captions' in info:
                    captions = info['automatic_captions'].get('en', [])
                    if captions:
                        return captions[0]['url']  # Returns the URL to download captions
                return "Error: No transcript found using yt_dlp."
        except Exception as e:
            return f"Error: Failed to retrieve transcript with yt_dlp. {str(e)}"

def summarize_text(text):
    """Summarizes text using Gemini-2.0-Flash."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Summarize this transcript: {text}")
    return response.text if response else "Summarization failed."

# Streamlit UI
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="📺", layout="centered")
st.title("📺 YouTube Video Summarizer")

video_url = st.text_input("Enter YouTube Video URL:")
if st.button("Summarize"):
    if video_url:
        video_id = extract_video_id(video_url)

        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid link.")
        else:
            transcript = get_youtube_transcript(video_id)

            if "Error" in transcript:
                st.error("Could not retrieve transcript. The video may not have subtitles.")
            else:
                st.info("Generating summary... Please wait.")
                summary = summarize_text(transcript)
                st.success("Summary Generated:")
                st.write(summary)
    else:
        st.warning("Please enter a valid YouTube URL.")