from sqlmodel import Session, create_engine
from backend.models import RegulatoryDocument
import os
from datetime import datetime

# Setup DB path
BASE_DIR = os.path.abspath("backend")
sqlite_file_name = "database.db"
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def debug_insert():
    try:
        with Session(engine) as session:
            doc = RegulatoryDocument(
                product_id=1,
                title="Debug Test",
                type="Protocol",
                status="Pending",
                submission_date=datetime.now(),
                expiry_date=datetime.now()
            )
            print("Attempting to add document...")
            session.add(doc)
            print("Attempting to commit...")
            session.commit()
            print("Successfully added document!")
            session.refresh(doc)
            print(f"Doc ID: {doc.id}")
            
            # Clean up
            session.delete(doc)
            session.commit()
            
    except Exception as e:
        print("CAUGHT EXCEPTION:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_insert()
