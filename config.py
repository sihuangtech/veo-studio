import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    VEO_MODEL_NAME = os.getenv("VEO_MODEL_NAME")
    # Get proxy and strip whitespace, or None if not set
    _proxy = os.getenv("HTTPS_PROXY")
    HTTPS_PROXY = _proxy.strip() if _proxy else None
    
    @staticmethod
    def validate():
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is not set. Please check your .env file.")
        if Config.GOOGLE_API_KEY == "your_api_key_here":
            raise ValueError("Please update .env file with your actual GOOGLE_API_KEY (currently set to placeholder).")
