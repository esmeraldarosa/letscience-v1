from sqlmodel import Session, create_engine, select, func
from models import Product, ProductSynthesisScheme
import os

sqlite_file_name = "database.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def check_coverage():
    with Session(engine) as session:
        total_products = session.exec(select(func.count(Product.id))).one()
        products_with_synthesis = session.exec(select(func.count(ProductSynthesisScheme.id))).one()
        
        print(f"Total Products: {total_products}")
        print(f"Products with Synthesis: {products_with_synthesis}")

if __name__ == "__main__":
    check_coverage()
