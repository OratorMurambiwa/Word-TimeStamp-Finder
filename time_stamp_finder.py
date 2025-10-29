import yt_dlp
import whisper
import datetime
import ffmpeg
import os
import numpy as np
import scipy.signal

from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import soundfile as sf


os.environ["PATH"] += os.pathsep + r"C:\ProgramData\chocolatey\bin"


def download_audio(url):
    output_file = "audio.wav"

    
    if os.path.exists(output_file):
        os.remove(output_file)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "temp_audio.%(ext)s",
        "quiet": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

   
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

def transcribe_audio_in_chunks(file_path, chunk_duration=30, mode="Transcribe (same language)", start_time=0, end_time=None):

    model_dir = r"D:\Users\DELL\Desktop\TimestampFinder\whisper-base"

    processor = WhisperProcessor.from_pretrained(model_dir)
    model = WhisperForConditionalGeneration.from_pretrained(model_dir)

    audio, sr = sf.read(file_path)
    if sr != 16000:
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        number_of_samples = round(len(audio) * float(16000) / sr)
        audio = scipy.signal.resample(audio, number_of_samples)
        sr = 16000

    
    start_idx = int(start_time * sr)
    end_idx = int(end_time * sr) if end_time else len(audio)

    
    audio = audio[start_idx:end_idx]
    total_len = len(audio) / sr
    chunk_samples = int(sr * chunk_duration)

    chunks = []
    for i in range(0, len(audio), chunk_samples):
        start_s = i / sr
        end_s = min((i + chunk_samples) / sr, total_len)
        segment = audio[i : i + chunk_samples]

        inputs = processor(segment, sampling_rate=sr, return_tensors="pt")

        generate_kwargs = {}
        if mode == "Translate to English":
            generate_kwargs = {"task": "translate", "language": "en"}

        with torch.no_grad():
            ids = model.generate(**inputs, **generate_kwargs)

        text = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
        chunks.append((start_s + start_time, end_s + start_time, text))

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


def find_word_in_youtube(url, word, mode, start_time=0, end_time=None):
    audio_path = download_audio(url)
    segments = transcribe_audio_in_chunks(audio_path, chunk_duration=30, mode=mode, start_time=start_time, end_time=end_time)
    
    if word.strip():
        return search_word(segments, word)
    else:
        return segments  

def find_word_in_uploaded_video(video_path, word, mode, start_time=0, end_time=None):
    audio_path = extract_audio_from_video(video_path)
    segments = transcribe_audio_in_chunks(audio_path, chunk_duration=30, mode=mode, start_time=start_time, end_time=end_time)
    
    if word.strip():
        return search_word(segments, word)
    else:
        return segments
