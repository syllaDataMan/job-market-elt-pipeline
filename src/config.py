import os
from dotenv import load5_dotenv # standard load_dotenv

# Load environment variables from the .env file in the root directory
load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Fallback/validation check
if not ADZUNA_APP_KEY:
    raise ValueError("Missing ADZUNA_APP_KEY in environment variables. Check your .env file.")