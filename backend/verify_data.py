from sqlmodel import Session, create_engine, select, func
from models import Product, ProductPharmacokinetics, ProductPharmacodynamics, ProductExperimentalModel
import os

sqlite_file_name = "database.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def verify():
    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found at {db_path}")
        return

    with Session(engine) as session:
        # Count Products
        p_count = session.exec(select(func.count(Product.id))).one()
        print(f"Products: {p_count}")
        
        products = session.exec(select(Product)).all()
        for p in products:
            pk_count = session.exec(select(func.count(ProductPharmacokinetics.id)).where(ProductPharmacokinetics.product_id == p.id)).one()
            pd_count = session.exec(select(func.count(ProductPharmacodynamics.id)).where(ProductPharmacodynamics.product_id == p.id)).one()
            model_count = session.exec(select(func.count(ProductExperimentalModel.id)).where(ProductExperimentalModel.product_id == p.id)).one()
            
            print(f"- {p.name}: PK={pk_count}, PD={pd_count}, Models={model_count}")

if __name__ == "__main__":
    verify()
