import os
import yt_dlp
from moviepy.editor import VideoFileClip
import uuid

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def download_video(url):
    """Downloads a video from a URL using yt-dlp."""
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': filepath,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return filepath

def extract_audio(video_path):
    """Extracts audio from video and saves as 16kHz wav."""
    audio_path = video_path.replace(".mp4", ".wav")
    video = VideoFileClip(video_path)
    # Convert to 16kHz mono as required by Whisper
    video.audio.write_audiofile(audio_path, fps=16000, nbytes=2, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])
    video.close()
    return audio_path

from .database import supabase

def upload_to_supabase(file_path, bucket_name="lectures"):
    """Uploads a local file to Supabase Storage."""
    if not supabase:
        print("Supabase client not initialized. Skipping upload.")
        return None
        
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_(bucket_name).upload(
                path=file_name,
                file=f,
                file_options={"cache-control": "3600", "upsert": "true"}
            )
            
        # Get public URL
        res = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return res
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

def cleanup_files(*filepaths):
    """Removes temporary files."""
    for path in filepaths:
        if os.path.exists(path):
            os.remove(path)
