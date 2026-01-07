from sqlmodel import Session, select
from backend.main import engine
from backend.models import Product
from backend.analysis import analyze_combination

def test_simulation():
    with Session(engine) as session:
        # Find IDs
        pembro = session.exec(select(Product).where(Product.name == "Pembrolizumab")).first()
        lenv = session.exec(select(Product).where(Product.name == "Lenvatinib")).first()
        
        if not pembro or not lenv:
            print("Error: Could not find products")
            return

        print(f"Testing {pembro.name} (ID {pembro.id}) + {lenv.name} (ID {lenv.id})")
        
        result = analyze_combination(session, pembro.id, lenv.id)
        
        print("\n--- ANALYSIS RESULT ---")
        print(f"Drug A Type: {result['drug_a']['mechanism_type']}") 
        print(f"Drug B Type: {result['drug_b']['mechanism_type']}")
        print(f"Synergy Score: {result['synergy_score']}")
        print(f"Interaction: {result['interaction_type']}")
        print("Analysis:")
        for line in result['analysis']:
            print(f" - {line}")
        print("Warnings:")
        for w in result['safety_warnings']:
            print(f" - {w}")

if __name__ == "__main__":
    test_simulation()
