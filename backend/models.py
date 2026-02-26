from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .database import Base, engine

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    video_path = Column(String)
    transcription = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    quizzes = relationship("Quiz", back_populates="lecture")
    flashcards = relationship("Flashcard", back_populates="lecture")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"))
    question = Column(Text)
    options = Column(Text) # JSON string for MCQs
    answer = Column(Text)
    type = Column(String) # MCQ or SHORT

    lecture = relationship("Lecture", back_populates="quizzes")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"))
    front = Column(Text)
    back = Column(Text)

    lecture = relationship("Lecture", back_populates="flashcards")

def init_db():
    Base.metadata.create_all(bind=engine)
