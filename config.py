import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')

    def save_gemini_api_key(self, key):
        with open(".env", "w") as f:
            f.write(f"GEMINI_API_KEY={key}")
        os.environ['GEMINI_API_KEY'] = key