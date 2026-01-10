import requests
from sqlmodel import Session, select, create_engine
from backend.models import Product, DrugInteraction
from backend.analysis import analyze_combination

# Setup Database Connection
sqlite_file_name = "database.db"
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"
engine = create_engine(sqlite_url)

def test_combination_logic():
    print("Testing Combination Analysis Logic...")
    with Session(engine) as session:
        # Fetch two drugs
        products = session.exec(select(Product)).all()
        if len(products) < 2:
            print("SKIP: Not enough products to test.")
            return

        drug_a = products[0]
        drug_b = products[1]
        
        print(f"Testing {drug_a.name} + {drug_b.name}")
        
        result = analyze_combination(session, drug_a.id, drug_b.id)
        
        if "error" in result:
             print(f"FAILURE: {result['error']}")
        else:
             print(f"SUCCESS: Analysis ran. Score: {result['synergy_score']}/10. Type: {result['interaction_type']}")
             # print(result)

if __name__ == "__main__":
    test_combination_logic()
