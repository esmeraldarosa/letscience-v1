import os
from sqlmodel import Session, select, create_engine
from backend.models import Product, RegulatoryDocument, ClinicalBudget

# Setup DB path exactly like main.py
BASE_DIR = os.path.abspath("backend")
sqlite_file_name = "database.db"
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def check_products():
    try:
        with Session(engine) as session:
            print("--- Checking Clinical Budget ---")
            items = session.exec(select(ClinicalBudget)).all()
            print(f"Total Budget Items: {len(items)}")
            for i in items:
                print(f"ID: {i.id} | Site: {i.site_name} | Alloc: {i.allocated_amount} | Spent: {i.spent_amount}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_products()
