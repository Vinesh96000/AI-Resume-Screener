import pdfplumber
import re

# A "God-Tier" Dictionary of standard Technical Skills. 
# This ensures we ONLY flag real technologies, not random English words like "Ideal" or "You".
TECH_SKILLS_DB = {
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "golang", "rust", "swift", "kotlin", "php", "ruby", "scala", "html", "css", "sql", "nosql", "matlab", "r", "bash", "shell", "powershell",
    
    # AI & Machine Learning
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "opencv", "nltk", "spacy", "pandas", "numpy", "matplotlib", "seaborn", "huggingface", "transformers", "bert", "gpt", "llm", "nlp", "computer vision", "generative ai", "langchain", "llama", "deep learning", "machine learning", "neural networks", "reinforcement learning",
    
    # Web Frameworks
    "react", "angular", "vue", "next.js", "django", "flask", "fastapi", "spring", "spring boot", "asp.net", "express", "node.js", "ruby on rails", "laravel", "bootstrap", "tailwind", "jquery",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "circleci", "gitlab ci", "github actions", "terraform", "ansible", "prometheus", "grafana", "linux", "unix", "ubuntu", "nginx", "apache", "serverless", "lambda",
    
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "oracle", "sql server", "firebase", "sqlite",
    
    # Big Data
    "spark", "hadoop", "kafka", "airflow", "snowflake", "databricks", "etl", "bigquery",
    
    # Tools & Concepts
    "git", "github", "gitlab", "jira", "agile", "scrum", "kanban", "rest api", "graphql", "soap", "microservices", "oop", "mvc", "tdd", "ci/cd", "algorithms", "data structures", "system design"
}

# A mapping to fix casing (e.g., "nlp" -> "NLP", "aws" -> "AWS") for professional output
CASING_FIX = {
    "nlp": "NLP", "aws": "AWS", "api": "API", "ci/cd": "CI/CD", "llm": "LLM", "ui/ux": "UI/UX", "sql": "SQL", "ml": "ML", "ai": "AI", "gcp": "GCP", "etl": "ETL", "oop": "OOP", "rest": "REST", "sass": "SaaS", "paas": "PaaS", "iaas": "IaaS"
}

def extract_text_from_pdf(file_bytes):
    """
    Extracts raw text from a PDF file (provided as bytes).
    """
    try:
        with pdfplumber.open(file_bytes) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return clean_text(text)
    except Exception as e:
        return ""

def clean_text(text):
    """
    Cleans the extracted text: removes special characters, extra spaces, etc.
    """
    # Normalize text: Convert to lowercase for matching, but keep formatting for display
    # We replace / with space to handle "CI/CD" correctly later or split strictly
    text = text.replace("/", " ").replace("-", " ")
    text = re.sub(r'[^a-zA-Z0-9\s.+]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_feedback(job_desc, resume_text, score):
    """
    Generates a smart, detailed paragraph and specific missing keywords using the Skill DB.
    """
    # 1. Normalize texts for matching
    jd_lower = job_desc.lower()
    resume_lower = resume_text.lower()
    
    # 2. Extract Skills from JD
    # We scan the JD to see which skills from our DB are mentioned.
    required_skills = set()
    for skill in TECH_SKILLS_DB:
        # We use regex boundry \b to ensure we match "java" but not "javascript" when searching for "java"
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, jd_lower):
            required_skills.add(skill)
            
    # 3. Check what the candidate has
    candidate_skills = set()
    for skill in required_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_lower):
            candidate_skills.add(skill)
            
    # 4. Calculate Missing Skills
    missing_skills = required_skills.difference(candidate_skills)
    
    # 5. Formatting the output (Fix Casing)
    formatted_missing = []
    for skill in missing_skills:
        # Use our casing fix map, or Title Case otherwise (e.g., "python" -> "Python")
        display_name = CASING_FIX.get(skill, skill.title())
        formatted_missing.append(display_name)
    
    # Limit to top 7 missing skills to avoid clutter
    formatted_missing = formatted_missing[:7]
    
    # 6. Generate Natural Language Summary
    summary = ""
    
    if score >= 80:
        summary = (
            f"This candidate is an exceptional match ({score}%), demonstrating strong alignment with the technical requirements. "
            "The resume includes nearly all critical skills mentioned in the job description. "
            "They appear to be a top-tier fit for this role."
        )
        strength = "Top Contender"
    elif score >= 60:
        summary = (
            f"This candidate shows good potential ({score}%) with a solid technical foundation. "
            f"While they match the general profile, the system suggests verifying experience with: {', '.join(formatted_missing[:3]) if formatted_missing else 'specific niche tools'}. "
            "They are likely a strong learner who can adapt quickly."
        )
        strength = "Strong Potential"
    else:
        summary = (
            f"The candidate's profile ({score}%) has limited overlap with the specific stack required. "
            "There is a divergence between the required technical skills and the candidate's listed experience. "
            "Key critical technologies appear to be missing."
        )
        strength = "Low Relevance"

    return {
        "summary": summary,
        "missing_keywords": formatted_missing,
        "strength": strength
    }