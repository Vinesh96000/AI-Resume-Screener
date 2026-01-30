import pdfplumber
import re

# A "God-Tier" Dictionary of standard Technical Skills. 
TECH_SKILLS_DB = {
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "golang", "rust", "swift", "kotlin", "php", "ruby", "scala", "html", "css", "sql", "nosql", "matlab", "r", "bash", "shell", "powershell",
    
    # AI & Machine Learning
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "opencv", "nltk", "spacy", "pandas", "numpy", "matplotlib", "seaborn", "huggingface", "transformers", "bert", "gpt", "llm", "nlp", "computer vision", "generative ai", "langchain", "llama", "deep learning", "machine learning", "neural networks", "reinforcement learning",
    
    # Web Frameworks
    "react", "angular", "vue", "next.js", "django", "flask", "fastapi", "spring", "spring boot", "asp.net", "express", "node.js", "ruby on rails", "laravel", "bootstrap", "tailwind", "jquery", "streamlit",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "circleci", "gitlab ci", "github actions", "terraform", "ansible", "prometheus", "grafana", "linux", "unix", "ubuntu", "nginx", "apache", "serverless", "lambda", "mlops", "mlflow",
    
    # Databases & Tools
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "oracle", "sql server", "firebase", "sqlite", "git", "github", "gitlab", "jira", "agile", "scrum", "kanban", "rest api", "graphql", "soap", "microservices", "oop", "mvc", "tdd", "ci/cd", "algorithms", "data structures", "system design", "power bi", "tableau"
}

# Fix casing for professional display
CASING_FIX = {
    "nlp": "NLP", "aws": "AWS", "api": "API", "ci/cd": "CI/CD", "llm": "LLM", "ui/ux": "UI/UX", "sql": "SQL", "ml": "ML", "ai": "AI", "gcp": "GCP", "etl": "ETL", "oop": "OOP", "rest": "REST", "sass": "SaaS", "paas": "PaaS", "iaas": "IaaS", "mlops": "MLOps"
}

def extract_text_from_pdf(file_bytes):
    try:
        with pdfplumber.open(file_bytes) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return clean_text(text)
    except Exception as e:
        return ""

def clean_text(text):
    text = text.replace("/", " ").replace("-", " ")
    text = re.sub(r'[^a-zA-Z0-9\s.+]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_feedback(job_desc, resume_text, score):
    jd_lower = job_desc.lower()
    resume_lower = resume_text.lower()
    
    # Extract Skills from JD
    required_skills = set()
    for skill in TECH_SKILLS_DB:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, jd_lower):
            required_skills.add(skill)
            
    # Check what candidate has
    candidate_skills = set()
    for skill in required_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_lower):
            candidate_skills.add(skill)
            
    missing_skills = required_skills.difference(candidate_skills)
    
    formatted_missing = []
    for skill in missing_skills:
        display_name = CASING_FIX.get(skill, skill.title())
        formatted_missing.append(display_name)
    
    # Limit to top 5 missing
    formatted_missing = formatted_missing[:5]
    
    summary = ""
    if score >= 80:
        summary = f"🔥 Top Candidate! Matches {len(candidate_skills)}/{len(required_skills)} required technical skills. Highly recommended."
        strength = "Top Contender"
    elif score >= 60:
        summary = f"✅ Strong Match. Has {len(candidate_skills)}/{len(required_skills)} core skills. Good potential fit."
        strength = "Strong Potential"
    else:
        summary = "⚠️ Low Match. Missing critical technical requirements."
        strength = "Low Relevance"

    return {
        "summary": summary,
        "missing_keywords": formatted_missing,
        "strength": strength
    }