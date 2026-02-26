import uvicorn
import os

if __name__ == "__main__":
    # Ensure uploads directory exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    print("Starting StudyGenie AI Backend...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
