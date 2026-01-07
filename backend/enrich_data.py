from sqlmodel import Session, select
from backend.models import Product, ProductPharmacodynamics, ProductSideEffect
from backend.main import engine

def enrich_data():
    with Session(engine) as session:
        # 1. Update Existing Products
        pembro = session.exec(select(Product).where(Product.name == "Pembrolizumab")).first()
        if pembro:
            pembro.description = "A programmed death receptor-1 (PD-1)-blocking antibody (checkpoint inhibitor)."
            pembro.target_indication = "Melanoma, NSCLC, TNBC"
            # Add PD target if missing
            if not pembro.pharmacodynamics:
                session.add(ProductPharmacodynamics(product_id=pembro.id, parameter="Ki", value="0.5 nM", target="PD-1"))
            # Side effects
            if not pembro.side_effects:
                 session.add(ProductSideEffect(product_id=pembro.id, effect="Fatigue"))
                 session.add(ProductSideEffect(product_id=pembro.id, effect="Rash"))
            session.add(pembro)
            print("Updated Pembrolizumab")

        adal = session.exec(select(Product).where(Product.name == "Adalimumab")).first()
        if adal:
            adal.description = "A tumor necrosis factor (TNF) blocker (antagonist) that reduces inflammation."
            if not adal.pharmacodynamics:
                session.add(ProductPharmacodynamics(product_id=adal.id, parameter="Kd", value="10 pM", target="TNF-alpha"))
            if not adal.side_effects:
                 session.add(ProductSideEffect(product_id=adal.id, effect="Injection Usage Reaction"))
                 session.add(ProductSideEffect(product_id=adal.id, effect="Fatigue")) # Overlapping
            session.add(adal)
            print("Updated Adalimumab")

        # 2. Add New Products for Synergy Testing
        # Lenvatinib (VEGF inhibitor) -> Synergy with PD-1
        lenv = session.exec(select(Product).where(Product.name == "Lenvatinib")).first()
        if not lenv:
            lenv = Product(
                name="Lenvatinib",
                description="A receptor tyrosine kinase (RTK) inhibitor that inhibits VEGF receptors (angiogenesis inhibitor).",
                target_indication="HCC, Thyroid Cancer",
                development_phase="Approved"
            )
            session.add(lenv)
            session.commit()
            session.refresh(lenv)
            session.add(ProductPharmacodynamics(product_id=lenv.id, parameter="IC50", value="4 nM", target="VEGFR2"))
            session.add(ProductSideEffect(product_id=lenv.id, effect="Hypertension"))
            session.add(ProductSideEffect(product_id=lenv.id, effect="Fatigue")) # Overlapping
            print("Added Lenvatinib")
            
        # Cisplatin (Chemo) -> Synergy with PD-1
        cis = session.exec(select(Product).where(Product.name == "Cisplatin")).first()
        if not cis:
            cis = Product(
                name="Cisplatin",
                description="A platinum-based chemotherapy (cytotoxic) agent that causes DNA crosslinking.",
                target_indication="Various Cancers",
                development_phase="Approved"
            )
            session.add(cis)
            session.commit()
            session.refresh(cis)
            session.add(ProductSideEffect(product_id=cis.id, effect="Nausea"))
            session.add(ProductSideEffect(product_id=cis.id, effect="Fatigue")) # Overlapping
            print("Added Cisplatin")
            
        session.commit()
        print("Data enrichment complete.")

if __name__ == "__main__":
    enrich_data()
