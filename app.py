from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

def get_youtube_transcript(video_id):
    """Fetches transcript of a YouTube video using proxies."""
    proxies_list = [
        "http://144.217.7.61:3129",
        "http://51.159.115.233:3128",
        "http://195.154.255.118:80",
    ]
    
    for proxy in proxies_list:
        try:
            print(f"Trying proxy: {proxy}")
            proxies = {"http": proxy, "https": proxy}
            transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
            text = " ".join([t["text"] for t in transcript])
            return text
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}")
    
    return "Error: All proxies failed. Try again later."

def summarize_text(text):
    """Summarizes text using Gemini-2.0-Flash."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Summarize this transcript: {text}")
    return response.text if response else "Summarization failed."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    video_url = request.form['video_url']
    video_id = video_url.split("v=")[-1].split("&")[0]
    transcript = get_youtube_transcript(video_id)
    
    if "Error" in transcript:
        return jsonify({"error": transcript})
    
    summary = summarize_text(transcript)
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))