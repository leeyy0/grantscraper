# migrations/create_tables.py
from config.config import DB_URL
from models.models import Base

if __name__ == "__main__":
    # Use direct connection for this

    from sqlalchemy import create_engine

    direct_engine = create_engine(DB_URL)

    Base.metadata.create_all(direct_engine)
    print("Tables created successfully!")
