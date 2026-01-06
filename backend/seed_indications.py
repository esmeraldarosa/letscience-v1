from sqlmodel import Session, select
from backend.models import Product, ProductIndication
from backend.main import engine

def seed_indications():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        
        for p in products:
            print(f"Seeding indications for {p.name}...")
            if "Pembrolizumab" in p.name:
                inds = [
                    ProductIndication(product_id=p.id, disease_name="Melanoma", approval_status="Approved"),
                    ProductIndication(product_id=p.id, disease_name="NSCLC", approval_status="Approved"),
                    ProductIndication(product_id=p.id, disease_name="Triple-Negative Breast Cancer", approval_status="Approved"),
                ]
                session.add_all(inds)
                p.target_indication = "Melanoma, NSCLC, TNBC"
                session.add(p)
                
            elif "Adalimumab" in p.name:
                inds = [
                    ProductIndication(product_id=p.id, disease_name="Rheumatoid Arthritis", approval_status="Approved"),
                    ProductIndication(product_id=p.id, disease_name="Crohn's Disease", approval_status="Approved"),
                    ProductIndication(product_id=p.id, disease_name="Psoriasis", approval_status="Approved"),
                ]
                session.add_all(inds)
                p.target_indication = "Rheumatoid Arthritis, Crohn's, Psoriasis"
                session.add(p)

            elif "Semaglutide" in p.name:
                inds = [
                    ProductIndication(product_id=p.id, disease_name="Type 2 Diabetes", approval_status="Approved"),
                    ProductIndication(product_id=p.id, disease_name="Obesity", approval_status="Approved"),
                ]
                session.add_all(inds)
                p.target_indication = "Type 2 Diabetes, Obesity"
                session.add(p)
                
            elif "Apixaban" in p.name:
                inds = [
                    ProductIndication(product_id=p.id, disease_name="Atrial Fibrillation", approval_status="Approved"),
                    ProductIndication(product_id=p.id, disease_name="Deep Vein Thrombosis", approval_status="Approved"),
                ]
                session.add_all(inds)
                p.target_indication = "Atrial Fibrillation, DVT"
                session.add(p)
                
        session.commit()
        print("Indications seeded successfully.")

if __name__ == "__main__":
    seed_indications()
