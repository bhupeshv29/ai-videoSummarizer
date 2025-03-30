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
    """Fetches transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text
    except Exception as e:
        return f"Error: {str(e)}"

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
    app.run(debug=True)
