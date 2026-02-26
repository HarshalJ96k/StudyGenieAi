import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Database Config (Supabase Postgres)
DATABASE_URL = os.getenv("DATABASE_URL") # Format: postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./study_genie.db" # Fallback for local dev

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Supabase Storage Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
