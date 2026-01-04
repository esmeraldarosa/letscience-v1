from sqlmodel import Session, create_engine, select
from models import Product, ProductPharmacodynamics

sqlite_file_name = "database.db"
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

# Force create tables if not exist (migrations are better but this is quick fix for dev)
from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)

def seed_pd_data():
    with Session(engine) as session:
        # Find Eliquis (Apixaban)
        # Note: searching by logic or assuming ID if known. 
        # Safer to search by name partial match
        products = session.exec(select(Product)).all()
        eliquis = next((p for p in products if "apixaban" in p.name.lower() or "eliquis" in p.name.lower()), None)
        
        if eliquis:
            print(f"Found Apixaban: {eliquis.name} (ID: {eliquis.id})")
            
            # Check if PD data already exists to avoid duplicates
            existing = session.exec(select(ProductPharmacodynamics).where(ProductPharmacodynamics.product_id == eliquis.id)).all()
            if not existing:
                pd_data = [
                    ProductPharmacodynamics(
                        product_id=eliquis.id,
                        parameter="Ki (Factor Xa)",
                        value="0.08 nM",
                        unit="nM",
                        target="Factor Xa"
                    ),
                    ProductPharmacodynamics(
                        product_id=eliquis.id,
                        parameter="Selectivity (vs Thrombin)",
                        value="> 30,000x",
                        unit="fold",
                        target="Thrombin"
                    ),
                     ProductPharmacodynamics(
                        product_id=eliquis.id,
                        parameter="IC50 (Human Plasma)",
                        value="1.2 nM",
                        unit="nM",
                        target="Factor Xa"
                    )
                ]
                for pd in pd_data:
                    session.add(pd)
                session.commit()
                print("Added Pharmacodynamics data for Apixaban.")
            else:
                print("PD data already exists for Apixaban.")
        else:
            print("Apixaban not found.")

if __name__ == "__main__":
    seed_pd_data()
