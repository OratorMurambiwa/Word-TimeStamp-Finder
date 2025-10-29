# Word Timestamp Finder

A Streamlit app that finds when specific words are spoken in a video — using Hugging Face Whisper models.

## Features
- Accepts YouTube links or uploaded video files
- Extracts audio and transcribes it
- Lets you search for any word
- Shows approximate timestamps (offline mode)
- Fully offline when using Hugging Face model

## Run Locally
```bash
git clone https://github.com/OratorMurambiwa/Word-TimeStamp-Finder.git
cd word-timestamp-finder
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
