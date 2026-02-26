# StudyGenie AI ⭐
**Voice-Enabled AI Study Buddy**

StudyGenie AI is a free, local-first web application that transforms video lectures into structured notes, quizzes, and interactive flashcards. It features an AI Study Buddy that answers questions strictly based on the lecture content.

## 🚀 Features
- **Video Processing:** Upload .mp4 or use a public video link.
- **Audio Extraction:** High-quality 16kHz audio extraction.
- **Speech-To-Text:** Powered by OpenAI Whisper (Local).
- **AI Summary:** Structured notes with bullet points.
- **AI Study Buddy:** RAG-based chat restricted to lecture content.
- **Knowledge Checks:** Automated Quiz (MCQs + Short Answers) and Flashcards.
- **History:** Keep track of all your past lectures.

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JavaScript.
- **Backend:** Python, FastAPI.
- **Database:** SQLite (SQLAlchemy).
- **AI Models:** 
  - `openai-whisper` (STT)
  - `facebook/bart-large-cnn` (Summarization)
  - `google/flan-t5-base` (General AI Tasks)

## 📋 Prerequisites
- Python 3.9+
- **FFmpeg** installed on your system path (Required for audio/video processing).

## 💻 Setup Instructions

### 1. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Backend
Start the FastAPI server:
```bash
python run.py
```
The backend will be running at `http://localhost:8000`.

### 3. Run the Frontend
Since it's a static frontend, you can simply open `frontend/index.html` in your browser.
*Tip: For the best experience, use a local server like Live Server (VS Code extension) or run `python -m http.server` in the frontend folder.*

## ⚠️ Important Notes
- **First Run:** The application will download approximately 2-3GB of AI models from HuggingFace on the first run. Please ensure you have a stable internet connection for this.
- **Hardware:** For faster processing, a GPU with CUDA support is recommended, but it will work on CPU as well.
- **FFmpeg:** Ensure FFmpeg is installed. On Windows, you can use `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org).

## 📄 License
MIT Free and Open Source.
