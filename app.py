import streamlit as st
from time_stamp_finder import find_word_in_youtube, find_word_in_uploaded_video


st.set_page_config(page_title="Time Stamp Finder", layout="centered")


st.title("Word Finder")
st.markdown("Find timestamps of specific words in YouTube videos or uploaded files using Whisper ASR.")

option = st.radio("Select Input Method:", ("YouTube URL", "Upload Video File"))
word = st.text_input("Enter the word to search for:")


model_choice = st.selectbox(
    "Select Whisper Model Size:",
    ["tiny", "base", "small", "medium", "large"],
    index=1
)

if option == "YouTube URL":
    url = st.text_input("Enter YouTube Video URL:")
    if st.button("Search YouTube Video"):
        if not url or not word:
            st.warning("Please provide both YouTube URL and the word to search for.")
        else:
            with st.spinner("Processing YouTube video... this might take a few minutes "):
                results = find_word_in_youtube(url, word, model_choice)

            if results:
                st.success(f"Found {len(results)} matches!")
                for time, text in results:
                    st.markdown(f"**[{time}]** — {text}")
            else:
                st.info("No matches found.")

elif option == "Upload Video File":
    uploaded_file = st.file_uploader("Upload your video file", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_file and st.button("Search Uploaded Video"):
        if not word:
            st.warning("Please enter a word to search.")
        else:
            with st.spinner("Processing uploaded video... "):
                with open("uploaded_video.mp4", "wb") as f:
                    f.write(uploaded_file.read())

                results = find_word_in_uploaded_video("uploaded_video.mp4", word)

            if results:
                st.success(f"Found {len(results)} matches!")
                for time, text in results:
                    st.markdown(f"**[{time}]** — {text}")
            else:
                st.info("No matches found.")
