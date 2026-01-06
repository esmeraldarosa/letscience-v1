
from sqlmodel import Session, select
from backend.main import engine
from backend.models import ClinicalTrial
from datetime import datetime

def fix_dates():
    with Session(engine) as session:
        trials = session.exec(select(ClinicalTrial)).all()
        print(f"Found {len(trials)} trials.")
        count = 0
        for t in trials:
            if not t.start_date:
                # Assign a dummy date based on ID to stagger them slightly
                year = 2017 + (t.id % 5)
                t.start_date = datetime(year, 1 + (t.id % 12), 1)
                session.add(t)
                count += 1
        session.commit()
        print(f"Updated {count} trials with start dates.")

if __name__ == "__main__":
    fix_dates()
