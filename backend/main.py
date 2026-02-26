from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from backend import database, models, processor, ai_pipeline
from backend.database import get_db

# Initialize database
models.init_db()

app = FastAPI(title="StudyGenie AI Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"

@app.get("/")
def read_root():
    return {"message": "StudyGenie AI API is running"}

@app.post("/process-video/")
async def process_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    db: Session = Depends(get_db)
):
    if not file and not url:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided")

    video_path = ""
    try:
        if file:
            filename = f"{uuid.uuid4()}_{file.filename}"
            video_path = os.path.join(UPLOAD_DIR, filename)
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        else:
            video_path = processor.download_video(url)

        # 1. Extract Audio
        audio_path = processor.extract_audio(video_path)

        # 2. Transcribe
        raw_text = ai_pipeline.transcribe_audio(audio_path)
        clean_text = ai_pipeline.clean_text(raw_text)

        # 3. Generate Summary
        summary = ai_pipeline.generate_summary(clean_text)

        # 4. Generate Quiz & Flashcards
        quiz_data = ai_pipeline.generate_quiz(clean_text)
        flashcards_data = ai_pipeline.generate_flashcards(clean_text)

        # 5. Optional: Upload video/audio to Supabase for persistence
        video_url = processor.upload_to_supabase(video_path)

        # 6. Save to DB
        lecture = models.Lecture(
            title=file.filename if file else "Public Lecture",
            video_path=video_url if video_url else video_path,
            transcription=clean_text,
            summary=summary
        )
        db.add(lecture)
        db.commit()
        db.refresh(lecture)

        # Cleanup audio (keep video for record/history if needed, or cleanup)
        processor.cleanup_files(audio_path)

        return {
            "id": lecture.id,
            "title": lecture.title,
            "summary": summary,
            "transcription": clean_text,
            "quiz": quiz_data,
            "flashcards": flashcards_data
        }

    except Exception as e:
        if video_path:
            processor.cleanup_files(video_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lectures/")
def get_lectures(db: Session = Depends(get_db)):
    return db.query(database.Lecture).all()

@app.get("/lecture/{lecture_id}")
def get_lecture(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.query(database.Lecture).filter(database.Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@app.post("/chat/")
async def chat(lecture_id: int = Form(...), message: str = Form(...), db: Session = Depends(get_db)):
    lecture = db.query(database.Lecture).filter(database.Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    response = ai_pipeline.chat_with_buddy(message, lecture.transcription)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
