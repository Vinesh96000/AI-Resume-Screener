import os
import requests
import time

class ResumeMatcher:
    def __init__(self):
        # The API URL for the SBERT model
        self.api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        # Get token from environment
        token = os.getenv('HF_TOKEN')
        self.headers = {"Authorization": f"Bearer {token}"}
        print(f"AI Model: Connected to Cloud. Token present: {bool(token)}")

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
        
        # RETRY LOGIC: The free API takes time to "wake up" (Cold Start)
        # We try 5 times, waiting 5 seconds each time (Total 25s wait)
        for attempt in range(1, 6):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                data = response.json()
                
                # Check 1: Did we get a proper list of scores?
                if isinstance(data, list):
                    match_percentage = round(float(data[0]) * 100, 2)
                    return match_percentage
                
                # Check 2: Is the model still loading?
                if isinstance(data, dict) and "error" in data:
                    print(f"⚠️ Attempt {attempt}: Model is loading... ({data['error']})")
                    time.sleep(5) # Wait 5 seconds and try again
                    continue
                    
                # Check 3: Auth Error?
                if response.status_code == 401:
                    print("❌ Error: Authorization Failed. Check HF_TOKEN in Render.")
                    return 0
                    
            except Exception as e:
                print(f"❌ API Error on attempt {attempt}: {e}")
                time.sleep(1)
        
        print("❌ Failed to get score after multiple retries.")
        return 0