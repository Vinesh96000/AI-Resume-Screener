from sentence_transformers import SentenceTransformer, util
import torch

class ResumeMatcher:
    def __init__(self):
        print("Loading AI Model... (This might take a moment)")
        # Loading the SBERT model for semantic understanding
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("AI Model Loaded Successfully!")

    def calculate_score(self, job_description: str, resume_text: str):
        """
        Input: Job Description text, Resume text
        Output: A match score between 0 and 100
        """
        # 1. Convert text to Vector Embeddings
        embeddings1 = self.model.encode(job_description, convert_to_tensor=True)
        embeddings2 = self.model.encode(resume_text, convert_to_tensor=True)

        # 2. Compute Cosine Similarity
        cosine_score = util.cos_sim(embeddings1, embeddings2)

        # 3. Convert to a percentage
        match_percentage = round(float(cosine_score[0][0]) * 100, 2)
        
        return match_percentage