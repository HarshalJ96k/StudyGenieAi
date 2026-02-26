import whisper
from transformers import pipeline
import torch
import json
import re

# Use CPU if GPU not available
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading AI Models on {device}...")
# whisper base is a good compromise between speed and accuracy
stt_model = whisper.load_model("base", device=device)

# Summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if device == "cuda" else -1)

# Task-oriented model (T5 is good for generation tasks)
generator = pipeline("text2text-generation", model="google/flan-t5-base", device=0 if device == "cuda" else -1)

def transcribe_audio(audio_path):
    """Transcribes audio using Whisper."""
    print("Transcribing audio...")
    result = stt_model.transcribe(audio_path)
    return result["text"]

def clean_text(text):
    """Basic cleaning of transcribed text."""
    # Remove excessive filler words (basic implementation)
    fillers = [r'\buhm\b', r'\buh\b', r'\bah\b', r'\ber\b', r'\blike\b']
    for filler in fillers:
        text = re.sub(filler, '', text, flags=re.IGNORECASE)
    # Fix repeated spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_summary(text):
    """Generates a structured summary."""
    print("Generating summary...")
    # Split text if too long (BART has 1024 token limit)
    max_chunk = 1000
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    
    summaries = []
    for chunk in chunks:
        if len(chunk) > 100:
            res = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summaries.append(res[0]['summary_text'])
    
    combined_summary = "\n\n".join(summaries)
    
    # Format into bullet points using T5
    prompt = f"Convert this text into bullet points with headings: {combined_summary}"
    final_notes = generator(prompt, max_length=500)[0]['generated_text']
    return final_notes

def generate_quiz(text):
    """Generates 3 MCQs and 2 short answers."""
    print("Generating quiz...")
    quiz = []
    
    # Generate MCQs
    mcq_prompt = f"Generate 3 multiple choice questions with 4 options and the correct answer based on this text: {text[:2000]}"
    mcq_res = generator(mcq_prompt, max_length=500)[0]['generated_text']
    
    # Generate Short Answers
    sa_prompt = f"Generate 2 short answer questions based on this text: {text[:2000]}"
    sa_res = generator(sa_prompt, max_length=300)[0]['generated_text']
    
    # For a real implementation, we'd parse these better. 
    # For the demo, we'll return the structured text.
    return {
        "mcqs": mcq_res,
        "short_answers": sa_res
    }

def generate_flashcards(text):
    """Generates up to 10 flashcards."""
    print("Generating flashcards...")
    prompt = f"Generate 5 flashcards (Question and Answer) from this text: {text[:2000]}"
    res = generator(prompt, max_length=500)[0]['generated_text']
    return res

def chat_with_buddy(query, context):
    """Answer questions or perform tasks strictly from the lecture context."""
    # Truncate context if too long for T5 (limit around 1500-2000 chars for better quality)
    context_snippet = context[:2000] 
    
    prompt = f"Using ONLY the following lecture content, perform the task or answer the question. If the information is missing, say 'This topic was not clearly explained in the lecture.':\n\nContent: {context_snippet}\n\nTask/Question: {query}"
    
    print(f"Chat Buddy processing: {query[:50]}...")
    res = generator(prompt, max_length=400)[0]['generated_text']
    return res
