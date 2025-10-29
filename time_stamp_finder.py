import yt_dlp
import whisper
import datetime
import ffmpeg 
import os

from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import soundfile as sf



os.environ["PATH"] += os.pathsep + r"C:\ProgramData\chocolatey\bin"

def download_audio(url, output_file="audio.wav"):
    yddl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "temp_audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": True
    }

    with yt_dlp.YoutubeDL(yddl_opts) as ydl:
        ydl.download([url]) ##############
    if os.path.exists("temp_audio.wav"):
        os.rename("temp_audio.wav", output_file)
    return output_file

def extract_audio_from_video(video_path, output_file="audio.wav"):
    (
        ffmpeg
        .input(video_path)
        .output(output_file, format="wav", acodec='pcm_s16le', ac=1, ar='16k')
        .run(quiet=True, overwrite_output=True)
    )
    try:
        return output_file
    except Exception as e:
        raise RuntimeError(f"Failed to extract audio: {e}")

# def transcribe_audio(audio_path, model_size="base"):
    
#     local_model_path = r"D:\Users\DELL\Desktop\TimestampFinder\pytorch_model.bin"
#     if os.path.exists(local_model_path):
#         print("Using local Whisper model from project folder...")
#         model = whisper.load_model(model_size, download_root=os.path.dirname(local_model_path))
#     else:
#         print("ocal model file not found, attempting to download...")
#         model = whisper.load_model(model_size)

#     result = model.transcribe(file_path)
#     return result["segments"]

def transcribe_audio_in_chunks(file_path, chunk_duration=30):
    
    model_dir = r"D:\Users\DELL\Desktop\TimestampFinder\whisper-base"

    processor = WhisperProcessor.from_pretrained(model_dir)
    model = WhisperForConditionalGeneration.from_pretrained(model_dir)

   
    audio, sr = sf.read(file_path)
    total_len = len(audio) / sr
    chunk_samples = int(sr * chunk_duration)

    chunks = []
    for i in range(0, len(audio), chunk_samples):
        start_s = i / sr
        end_s = min((i + chunk_samples) / sr, total_len)
        segment = audio[i : i + chunk_samples]

        inputs = processor(segment, sampling_rate=sr, return_tensors="pt")

        with torch.no_grad():
            ids = model.generate(**inputs)

        text = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
        chunks.append((start_s, end_s, text))

    return chunks

def search_word(segments, word):
    
    matches = []
    word_lower = word.lower()

    for start, end, text in segments:
        if word_lower in text.lower():
            start_m, end_m = int(start // 60), int(end // 60)
            start_s, end_s = int(start % 60), int(end % 60)
            time_label = f"[{start_m:02d}:{start_s:02d} – {end_m:02d}:{end_s:02d}]"
            matches.append((time_label, text))
    return matches


def find_word_in_youtube(url, word):
    audio_path = download_audio(url)
    segments = transcribe_audio(audio_path)
    matches = search_word(segments, word)
    return search_word(segments, word)

def find_word_in_uploaded_video(video_path, word):
    audio_path = extract_audio_from_video(video_path)
    segments = transcribe_audio_in_chunks(audio_path, chunk_duration=30)
    return search_word(segments, word)




    