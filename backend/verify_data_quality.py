from sqlmodel import Session, select, create_engine
from backend.models import ProductIndication, ProductSideEffect

sqlite_url = "sqlite:///backend/database.db"
engine = create_engine(sqlite_url)

def verify():
    with Session(engine) as session:
        # Check Indications
        indications = session.exec(select(ProductIndication)).all()
        generic_count = sum(1 for i in indications if i.disease_name == "FDA Approved Usage")
        total_indications = len(indications)
        
        print(f"Total Indications: {total_indications}")
        print(f"Generic 'FDA Approved Usage': {generic_count} ({(generic_count/total_indications)*100:.1f}%)")
        
        print("\nSample Indications:")
        for ind in indications[:10]:
            print(f" - {ind.disease_name}")

        # Check Side Effects
        side_effects = session.exec(select(ProductSideEffect)).all()
        print(f"\nTotal Side Effects: {len(side_effects)}")
        print("Sample Side Effects:")
        for se in side_effects[:10]:
            print(f" - {se.effect}")

if __name__ == "__main__":
    verify()
