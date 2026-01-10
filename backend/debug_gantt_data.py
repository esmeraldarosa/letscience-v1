from sqlmodel import Session, select
from backend.models import Product, ClinicalTrial, ProductMilestone
from backend.main import engine
import datetime

def debug_gantt():
    with Session(engine) as session:
        # Get first 2 products
        products = session.exec(select(Product).limit(2)).all()
        if not products:
            print("No products found!")
            return

        ids = [p.id for p in products]
        print(f"Checking products: {[p.name for p in products]}")

        # Check raw trials
        trials = session.exec(select(ClinicalTrial).where(ClinicalTrial.product_id.in_(ids))).all()
        print(f"Found {len(trials)} trials total.")
        for t in trials:
            print(f"  - [{t.product_id}] {t.phase}: {t.start_date} -> {t.completion_date}")

        # Check raw milestones
        milestones = session.exec(select(ProductMilestone).where(ProductMilestone.product_id.in_(ids))).all()
        print(f"Found {len(milestones)} milestones total.")
        
        # Simulate Endpoint Logic
        timeline_events = []
        for t in trials:
            if t.start_date:
                # Logic from main.py
                end = t.completion_date
                if not end:
                    duration_days = 365
                    if "Phase 2" in t.phase: duration_days = 730
                    if "Phase 3" in t.phase: duration_days = 1095
                    end = t.start_date + datetime.timedelta(days=duration_days) # Rough approx locally for script
                
                timeline_events.append({
                    "product_id": t.product_id,
                    "date": t.start_date,
                    "end": end,
                    "title": t.title
                })
        
        print("\n--- Final Timeline Events Payload ---")
        for e in timeline_events:
            print(e)

if __name__ == "__main__":
    debug_gantt()
