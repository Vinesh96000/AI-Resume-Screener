import os
import requests
import time

class ResumeMatcher:
    def __init__(self):
        # We use the API URL for the exact same model we were using locally
        self.api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        # We will get the token from Environment Variables
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
        print("AI Model: Connected to HuggingFace Cloud Inference.")

    def calculate_score(self, job_description: str, resume_text: str):
        """
        Input: Job Description text, Resume text
        Output: A match score between 0 and 100 using Cloud API
        """
        payload = {
            "inputs": {
                "source_sentence": job_description,
                "sentences": [resume_text]
            }
        }
        
        # Retry logic in case the model is "warming up" (common on free tier)
        for attempt in range(3):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                data = response.json()
                
                # Handling "Model Loading" error from HF
                if isinstance(data, dict) and "error" in data:
                    print(f"API Waiting... {data}")
                    time.sleep(2) # Wait for model to load
                    continue
                
                # HF returns a list of scores, e.g., [0.85]
                if isinstance(data, list):
                    match_percentage = round(float(data[0]) * 100, 2)
                    return match_percentage
                    
            except Exception as e:
                print(f"API Error: {e}")
                return 0
                
        return 0