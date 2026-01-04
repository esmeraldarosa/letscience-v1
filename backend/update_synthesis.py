from sqlmodel import Session, select, create_engine
from backend.models import Product, ProductSynthesis

# Connect to DB
engine = create_engine('sqlite:///backend/database.db')

def update_synthesis():
    with Session(engine) as session:
        # Eliquis (ID 4)
        product = session.get(Product, 4)
        if product:
            # Clear existing steps
            for step in product.synthesis_steps:
                session.delete(step)
            
            # Add new real steps
            steps = [
                "Formation of the pyrazole-5-carboxamide intermediate from ethyl 2-chloro-2-(2-(4-methoxyphenyl)hydrazono)acetate.",
                "Cycloaddition with a morpholine-enamine derivative to form the piperidin-2-one core.",
                "Ullmann-type coupling with 4-iodo-delta-valerolactam to introduce the lactam ring.",
                "Final amidation of the ester group to yield Apixaban."
            ]
            
            for step_desc in steps:
                step = ProductSynthesis(
                    product_id=product.id,
                    step_description=step_desc
                )
                session.add(step)
            
            session.commit()
            print("Updated Eliquis Synthesis Steps")

if __name__ == "__main__":
    update_synthesis()
