import streamlit as st
from time_stamp_finder import find_word_in_youtube, find_word_in_uploaded_video

st.set_page_config(page_title="Time Stamp Finder", layout="centered")

st.title("Word Finder")
st.markdown("Transcribe or search for specific words in YouTube videos or uploaded files using Whisper ASR.")

option = st.radio("Select Input Method:", ("YouTube URL", "Upload Video File"))

word = st.text_input("Enter the word to search for (leave blank for full transcription):")


st.markdown("### Optional: Select a specific time range to transcribe")

col1, col2 = st.columns(2)
with col1:
    start_min = st.number_input("Start minutes", min_value=0, value=0)
    start_sec = st.number_input("Start seconds", min_value=0, max_value=59, value=0)
with col2:
    end_min = st.number_input("End minutes", min_value=0, value=0)
    end_sec = st.number_input("End seconds", min_value=0, max_value=59, value=30)

start_time = start_min * 60 + start_sec
end_time = end_min * 60 + end_sec


mode = st.selectbox(
    "Select Operation Mode:",
    ["Transcribe (same language)", "Translate to English"],
    index=0
)

if option == "YouTube URL":
    url = st.text_input("Enter YouTube Video URL:")

    if st.button("Process YouTube Video"):
        if not url:
            st.warning("Please provide a YouTube URL.")
        else:
            with st.spinner("Processing YouTube video... this may take a few minutes ⏳"):
                results = find_word_in_youtube(url, word, mode, start_time, end_time)

            if not results:
                st.info("No results found.")
            elif word.strip():
                st.success(f"Found {len(results)} matches for '{word}'!")
                for time, text in results:
                    st.markdown(f"**[{time}]** — {text}")
            else:
                st.success(f"Full transcription for {start_min}:{start_sec:02d} → {end_min}:{end_sec:02d}")
                for time, text in results:
                    st.markdown(f"**[{time}]** — {text}")


elif option == "Upload Video File":
    uploaded_file = st.file_uploader("Upload your video file", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_file and st.button("Process Uploaded Video"):
        with open("uploaded_video.mp4", "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Processing uploaded video... this may take a few minutes ⏳"):
            results = find_word_in_uploaded_video("uploaded_video.mp4", word, mode, start_time, end_time)

        if not results:
            st.info("No results found.")
        elif word.strip():
            st.success(f"Found {len(results)} matches for '{word}'!")
            for time, text in results:
                st.markdown(f"**[{time}]** — {text}")
        else:
            st.success(f"Full transcription for {start_min}:{start_sec:02d} → {end_min}:{end_sec:02d}")
            for time, text in results:
                st.markdown(f"**[{time}]** — {text}")
