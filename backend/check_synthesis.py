from sqlmodel import Session, create_engine, select
from models import ProductSynthesisScheme, Product
import os

sqlite_file_name = "database.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def check_synthesis():
    with Session(engine) as session:
        schemes = session.exec(select(ProductSynthesisScheme, Product.name).join(Product)).all()
        print(f"Total Schemes: {len(schemes)}")
        for s, p_name in schemes:
            print(f"- {p_name}: {s.scheme_name}")

if __name__ == "__main__":
    check_synthesis()
