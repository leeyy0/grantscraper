from config.config import DB_URL
from sqlalchemy import create_engine

# Create the SQLAlchemy engine using the DB_URL from the environment
engine = create_engine(DB_URL)
