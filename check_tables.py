from sqlmodel import SQLModel, create_engine, text
from backend.models import RegulatoryDocument, ClinicalBudget
import os

# Setup DB path
BASE_DIR = os.path.abspath("backend")
sqlite_file_name = "database.db"
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def check_and_create_tables():
    print(f"Checking database at: {db_path}")
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='regulatorydocument';"))
            table_exists = result.fetchone()
            
            if table_exists:
                print("Table 'regulatorydocument' ALREADY EXISTS.")
            else:
                print("Table 'regulatorydocument' NOT FOUND. Creating tables...")
                SQLModel.metadata.create_all(engine)
                print("Tables created successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_create_tables()
