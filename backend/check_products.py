from sqlmodel import Session, select, create_engine
from models import Product

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def check_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        print(f"Total Products: {len(products)}")
        for p in products:
            print(f"ID: {p.id} - Name: {p.name}")

if __name__ == "__main__":
    check_products()
