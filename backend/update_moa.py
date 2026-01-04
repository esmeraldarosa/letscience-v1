from sqlmodel import Session, select, create_engine
from backend.models import Product

# Connect to DB
engine = create_engine('sqlite:///backend/database.db')

def update_moa():
    with Session(engine) as session:
        # 1. Keytruda
        p1 = session.get(Product, 1)
        if p1:
            p1.moa_video_url = "/app/assets/moa_keytruda.png"
            session.add(p1)
            print("Updated Keytruda")

        # 2. Ozempic
        p2 = session.get(Product, 2)
        if p2:
            p2.moa_video_url = "/app/assets/moa_ozempic.png"
            session.add(p2)
            print("Updated Ozempic")
        
        # 3. Humira
        p3 = session.get(Product, 3)
        if p3:
            p3.moa_video_url = "/app/assets/moa_humira.png"
            session.add(p3)
            print("Updated Humira")

        # 4. Eliquis
        p4 = session.get(Product, 4)
        if p4:
            p4.moa_video_url = "/app/assets/moa_eliquis.png"
            session.add(p4)
            print("Updated Eliquis")

        session.commit()

if __name__ == "__main__":
    update_moa()
