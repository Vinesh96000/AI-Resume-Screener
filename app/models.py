import os
import requests
import time

class ResumeMatcher:
    def __init__(self):
        self.api_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"
        token = os.getenv('HF_TOKEN')
        self.headers = {"Authorization": f"Bearer {token}"}
        print(f"AI Model: Connected to Cloud. Token present: {bool(token)}")

    def calculate_score(self, job_description: str, resume_text: str):
        payload = {
            "inputs": {
                "source_sentence": job_description,
                "sentences": [resume_text]
            }
        }
        
        for attempt in range(1, 6):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                data = response.json()
                
                if isinstance(data, list):
                    raw_score = float(data[0]) * 100
                    
                    # --- CALIBRATION LOGIC ---
                    # Raw AI similarity of 60% is actually very good. 
                    # We boost it slightly to match human expectations (0-100 scale).
                    # Formula: Score * 1.30 (Capped at 98%)
                    final_score = raw_score * 1.30
                    
                    # Cap it at 98% (Nobody is perfect)
                    if final_score > 98: final_score = 98
                    
                    return round(final_score, 2)
                
                if isinstance(data, dict) and "error" in data:
                    print(f"⚠️ Attempt {attempt}: Model loading...")
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                print(f"❌ API Error: {e}")
                time.sleep(1)
        
        return 0