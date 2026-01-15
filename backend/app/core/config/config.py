import os

from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
load_dotenv()

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("DB_URL environment variable 'DB_URL' is not set")
