from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import io

# Import our custom modules
from app.utils import extract_text_from_pdf, generate_feedback
from app.models import ResumeMatcher

app = FastAPI(title="AI Resume Screener", version="1.0")

# Mount Static files (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Templates (HTML)
templates = Jinja2Templates(directory="templates")

# Initialize the AI Model (Global variable so we load it only once)
ai_matcher = ResumeMatcher()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the Home Page (Frontend)
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_resume(
    request: Request,
    job_description: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """
    Receives Job Desc + Resumes -> Returns Analysis
    """
    results = []
    
    for file in files:
        # 1. Read the PDF file
        file_content = await file.read()
        file_stream = io.BytesIO(file_content)
        
        # 2. Extract Text
        resume_text = extract_text_from_pdf(file_stream)
        
        if not resume_text:
            results.append({
                "filename": file.filename, 
                "score": 0, 
                "feedback": {
                    "summary": "Error: Could not read text from PDF.", 
                    "strength": "Error", 
                    "missing_keywords": []
                }
            })
            continue

        # 3. AI Matching (Get Score)
        score = ai_matcher.calculate_score(job_description, resume_text)
        
        # 4. Generate Detailed Feedback (NOW PASSING SCORE)
        feedback = generate_feedback(job_description, resume_text, score)
        
        results.append({
            "filename": file.filename,
            "score": score,
            "feedback": feedback
        })

    # Sort results by highest score
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # Return the HTML with results injected
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "results": results,
        "job_description": job_description
    })