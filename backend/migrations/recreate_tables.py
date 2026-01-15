"""Drop and recreate all database tables.

WARNING: This will DELETE ALL DATA in the database!
Use this script to remigrate your database schema when models change.

Usage:
    uv run migrations/recreate_tables
"""

from app.core.config.config import DB_URL
from app.models.models import Base

if __name__ == "__main__":
    from sqlalchemy import create_engine, inspect, text

    # Safety confirmation
    print("=" * 60)
    print("WARNING: This will DELETE ALL DATA in your database!")
    print("=" * 60)
    print(f"Database URL: {DB_URL.split('@')[1] if '@' in DB_URL else 'hidden'}")
    print()
    confirmation = input("Type 'yes' to continue, anything else to cancel: ")

    if confirmation.lower() != "yes":
        print("Cancelled. No changes made.")
        exit(0)

    print("\nConnecting to database...")
    engine = create_engine(DB_URL)

    # Get inspector to check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if existing_tables:
        print(f"\nFound {len(existing_tables)} existing table(s):")
        for table in existing_tables:
            print(f"  - {table}")

        print("\nDropping all tables...")
        with engine.connect() as conn:
            # Drop all tables with CASCADE to handle foreign key constraints
            # This is safer than dropping in order
            for table_name in existing_tables:
                print(f"  Dropping table: {table_name}")
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
                conn.commit()
        print("All tables dropped successfully.")
    else:
        print("\nNo existing tables found.")

    print("\nCreating new tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

    # Verify tables were created
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    print(f"\nCreated {len(new_tables)} table(s):")
    for table in new_tables:
        print(f"  - {table}")

    print("\n✅ Migration complete!")
