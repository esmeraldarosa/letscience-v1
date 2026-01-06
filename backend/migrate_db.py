
from sqlmodel import Session, create_engine, text
from backend.main import engine

def migrate_db():
    print("Checking database schema...")
    try:
        with Session(engine) as session:
            # Check if column exists
            try:
                session.exec(text("SELECT completion_date FROM clinicaltrial LIMIT 1"))
                print("Column 'completion_date' already exists.")
            except Exception:
                print("Column 'completion_date' missing. Adding it...")
                session.exec(text("ALTER TABLE clinicaltrial ADD COLUMN completion_date DATETIME"))
                session.commit()
                print("Column added successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_db()
