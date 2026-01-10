from sqlmodel import Session, select
from backend.models import Product, ClinicalTrial, ProductMilestone
from backend.main import engine
from datetime import datetime, timedelta
import random

def fix_gantt_data():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        print(f"Fixing data for {len(products)} products...")

        for p in products:
            # 1. Fix Trials
            trials = session.exec(select(ClinicalTrial).where(ClinicalTrial.product_id == p.id)).all()
            base_year = 2020 + (p.id % 5) # Stagger start years
            
            for i, t in enumerate(trials):
                if not t.start_date:
                    month = (i * 3) % 12 + 1
                    t.start_date = datetime(base_year + i, month, 1)
                    duration = 365 * (2 if "Phase 2" in t.phase else 3)
                    t.completion_date = t.start_date + timedelta(days=duration)
                    session.add(t)
                    print(f"  Updated Trial: {t.title} -> {t.start_date.date()}")

            # 2. Add Milestones if missing
            milestones = session.exec(select(ProductMilestone).where(ProductMilestone.product_id == p.id)).all()
            if not milestones:
                m1 = ProductMilestone(
                    product_id=p.id,
                    date=datetime(base_year + 4, 6, 15),
                    event="NDA Submission",
                    phase="Registration"
                )
                m2 = ProductMilestone(
                    product_id=p.id,
                    date=datetime(base_year + 5, 1, 15),
                    event="Expected Approval",
                    phase="Approved"
                )
                session.add(m1)
                session.add(m2)
                print(f"  Added Milestones for {p.name}")

        session.commit()
        print("Done! Data enriched with dates.")

if __name__ == "__main__":
    fix_gantt_data()
