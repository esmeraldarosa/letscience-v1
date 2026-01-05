from sqlmodel import Session, create_engine, select, SQLModel
from models import Product, ProductPharmacokinetics, ProductPharmacodynamics, ProductExperimentalModel
import os

sqlite_file_name = "database.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, sqlite_file_name)
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def seed_science():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        
        # Helper to find product
        def get_product(search):
            return next((p for p in products if search.lower() in p.name.lower()), None)

        # Data Definitions
        science_data = {
            "pembrolizumab": {  # Keytruda
                "pk": [
                    {"param": "Cmax", "val": "100 µg/mL", "unit": "µg/mL"},
                    {"param": "Tmax", "val": "Immediate (IV)", "unit": None},
                    {"param": "t1/2", "val": "22 days", "unit": "days"},
                    {"param": "Bioavailability", "val": "100% (IV)", "unit": "%"}
                ],
                "pd": [
                    {"param": "Kd", "val": "29 pM", "unit": "pM", "target": "PD-1"},
                    {"param": "IC50", "val": "0.1-0.3 nM", "unit": "nM", "target": "PD-L1 Binding"}
                ],
                "models": [
                    {"name": "Hu-PBMC Mouse", "type": "In Vivo", "desc": "Humanized mouse model reconstituted with human PBMCs for immunotherapy assessment."}
                ],
                "clinical": [
                    {"nct": "NCT02404441", "title": "KEYNOTE-189: Pemetrexed/Platinum with or without Pembrolizumab in NSCLC", "phase": "Phase 3", "status": "Completed", "sponsor": "Merck Sharp & Dohme Corp."}
                ],
                "synthesis": [
                    {"name": "Recombinant Manufacturing", "desc": "Production in CHO cells followed by Protein A purification.", "img": None}
                ],
                "patents": [
                    {"title": "Anti-PD-1 Antibodies", "source_id": "US8354509", "type": "Composition of Matter", "claims": "Monoclonal antibody that binds PD-1 with high affinity.", "diseases": "Cancer", "url": "https://patents.google.com/patent/US8354509B2/en"}
                ],
                "articles": [
                    {"title": "Safety and Activity of Pembrolizumab in Tumors with MMR Deficiency", "doi": "10.1056/NEJMoa1503093", "authors": "Le et al.", "date": "2015-06-25", "desc": "Pivotal study showing efficacy in MMR-deficient tumors.", "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa1503093"}
                ],
                "conferences": [
                    {"name": "ASCO 2024", "title": "Keynote findings: Long term survival", "date": "2024-06-01", "desc": "5-year survival rates in NSCLC.", "url": "https://conferences.asco.org/"}
                ]
            },
            "adalimumab": { # Humira
                "pk": [
                    {"param": "Cmax", "val": "4.7 µg/mL", "unit": "µg/mL"},
                    {"param": "Tmax", "val": "131 hours", "unit": "hours"},
                    {"param": "t1/2", "val": "14 days", "unit": "days"},
                    {"param": "Bioavailability", "val": "64%", "unit": "%"}
                ],
                "pd": [
                    {"param": "Kd", "val": "0.1 nM", "unit": "nM", "target": "TNF-alpha"},
                    {"param": "Neutralization", "val": ">90%", "unit": "%", "target": "Soluble TNF"}
                ],
                "models": [
                    {"name": "Tg197 Transgenic Mouse", "type": "In Vivo", "desc": "Human TNF-alpha transgenic model developing polyarthritis."}
                ],
                "clinical": [
                    {"nct": "NCT00626028", "title": "Adalimumab Efficacy in Rheumatoid Arthritis", "phase": "Phase 4", "status": "Completed", "sponsor": "AbbVie"}
                ],
                "synthesis": [
                    {"name": "Biologics Production", "desc": "Fermentation in mammalian cell culture.", "img": None}
                ],
                "patents": [
                    {"title": "Human TNF-alpha antibodies", "source_id": "US6090382", "type": "Composition of Matter", "claims": "Isolated human antibody that binds to human TNF-alpha.", "diseases": "Rheumatoid Arthritis", "url": "https://patents.google.com/patent/US6090382A/en"}
                ],
                "articles": [
                    {"title": "Adalimumab for Rheumatoid Arthritis", "doi": "10.1056/NEJMoa021573", "authors": "Weinblatt et al.", "date": "2003-01-01", "desc": "Adalimumab showed significant improvement in RA symptoms.", "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa021573"}
                ],
                "conferences": [
                    {"name": "ACR Annual Meeting", "title": "Sustained remission in RA", "date": "2023-11-12", "desc": "Real-world evidence of sustained remission.", "url": "https://acrabstracts.org/"}
                ]
            },
            "semaglutide": { # Ozempic
                "pk": [
                    {"param": "Cmax", "val": "30 nM", "unit": "nM"},
                    {"param": "Tmax", "val": "1-3 days", "unit": "days"},
                    {"param": "t1/2", "val": "7 days", "unit": "days"},
                    {"param": "Bioavailability", "val": "89%", "unit": "%"}
                ],
                "pd": [
                    {"param": "EC50", "val": "0.3 nM", "unit": "nM", "target": "GLP-1 Receptor"},
                    {"param": "Homology", "val": "94%", "unit": "%", "target": "Native GLP-1"}
                ],
                "models": [
                    {"name": "DIO Mouse", "type": "In Vivo", "desc": "Diet-Induced Obesity model for weight loss efficacy."}
                ],
                "clinical": [
                    {"nct": "NCT01720446", "title": "SUSTAIN 6: CVOT in Type 2 Diabetes", "phase": "Phase 3", "status": "Completed", "sponsor": "Novo Nordisk A/S"}
                ],
                "synthesis": [
                    {"name": "SPPS + Recombinant", "desc": "Yeast expression of backbone + Synthetic addition of fatty acid side chain.", "img": None}
                ],
                "patents": [
                    {"title": "GLP-1 Derivatives", "source_id": "US8129343", "type": "Composition of Matter", "claims": "Acylated GLP-1 analogs with extended half-life.", "diseases": "Diabetes, Obesity", "url": "https://patents.google.com/patent/US8129343B2/en"}
                ],
                "articles": [
                    {"title": "Semaglutide and Cardiovascular Outcomes in Patients with Type 2 Diabetes", "doi": "10.1056/NEJMoa1607141", "authors": "Marso et al.", "date": "2016-11-10", "desc": "Significant reduction in cardiovascular risk.", "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa1607141"}
                ],
                "conferences": []
            },
             "apixaban": { # Eliquis
                "pk": [
                    {"param": "Cmax", "val": "180 ng/mL", "unit": "ng/mL"},
                    {"param": "Tmax", "val": "3-4 hours", "unit": "hours"},
                    {"param": "t1/2", "val": "12 hours", "unit": "hours"},
                    {"param": "Bioavailability", "val": "50%", "unit": "%"}
                ],
                "pd": [], 
                "models": [
                    {"name": "AV Shunt Model", "type": "In Vivo", "desc": "Rabbit Arteriovenous Shunt model for antithrombotic activity."}
                ],
                "clinical": [
                    {"nct": "NCT00412984", "title": "ARISTOTLE: Apixaban for Reduction In Stroke", "phase": "Phase 3", "status": "Completed", "sponsor": "Bristol-Myers Squibb"}
                ],
                "synthesis": [
                    {"name": "Convergent Synthesis", "desc": "Coupling of chloro-lactam intermediate with pyrazole-amine fragment.", "img": "/static/apixaban_synthesis.png", "source_url": "https://go.drugbank.com/drugs/DB06605"}
                ],
                "patents": [
                    {"title": "Factor Xa Inhibitors", "source_id": "US6967208", "type": "Composition of Matter", "claims": "Nitrogen containing heterobicyclic compounds as Factor Xa inhibitors.", "diseases": "Thrombosis", "url": "https://patents.google.com/patent/US6967208B2/en"}
                ],
                "articles": [
                    {"title": "Apixaban versus Warfarin in Patients with Atrial Fibrillation", "doi": "10.1056/NEJMoa1107039", "authors": "Granger et al.", "date": "2011-09-15", "desc": "Superiority of Apixaban over Warfarin in stroke prevention.", "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa1107039"}
                ],
                "conferences": []
            }
        }


        for key, data in science_data.items():
            product = get_product(key)
            if not product:
                print(f"Creating {key}...")
                product = Product(
                    name=key.capitalize(), 
                    target_indication="Various", 
                    development_phase="Approved",
                    description=f"Synthetic data for {key}."
                )
                session.add(product)
                session.commit()
                session.refresh(product)
            
            print(f"Seeding {product.name}...")

            # Seed PK
            existing_pk = session.exec(select(ProductPharmacokinetics).where(ProductPharmacokinetics.product_id == product.id)).all()
            if not existing_pk:
                for item in data["pk"]:
                    session.add(ProductPharmacokinetics(
                        product_id=product.id,
                        parameter=item["param"],
                        value=item["val"],
                        unit=item["unit"]
                    ))
            
            # Seed PD
            existing_pd = session.exec(select(ProductPharmacodynamics).where(ProductPharmacodynamics.product_id == product.id)).all()
            if not existing_pd and data.get("pd"):
                 for item in data["pd"]:
                    session.add(ProductPharmacodynamics(
                        product_id=product.id,
                        parameter=item["param"],
                        value=item["val"],
                        unit=item["unit"],
                        target=item["target"]
                    ))

            # Seed Models
            existing_models = session.exec(select(ProductExperimentalModel).where(ProductExperimentalModel.product_id == product.id)).all()
            if not existing_models and data.get("models"):
                 for item in data["models"]:
                    session.add(ProductExperimentalModel(
                        product_id=product.id,
                        model_name=item["name"],
                        model_type=item["type"],
                        description=item["desc"]
                    ))

            # Seed Clinical Trials (NEW)
            from models import ClinicalTrial
            existing_trials = session.exec(select(ClinicalTrial).where(ClinicalTrial.product_id == product.id)).all()
            if not existing_trials and data.get("clinical"):
                for item in data["clinical"]:
                    session.add(ClinicalTrial(
                        product_id=product.id,
                        nct_id=item["nct"],
                        title=item["title"],
                        phase=item["phase"],
                        status=item["status"],
                        sponsor=item["sponsor"],
                        url=f"https://clinicaltrials.gov/study/{item['nct']}"
                    ))
            
            # Seed Synthesis (NEW)
            from models import ProductSynthesisScheme, Patent, ScientificArticle, Conference
            from datetime import datetime
            
            existing_schemes = session.exec(select(ProductSynthesisScheme).where(ProductSynthesisScheme.product_id == product.id)).all()
            if not existing_schemes and data.get("synthesis"):
                for item in data["synthesis"]:
                    session.add(ProductSynthesisScheme(
                        product_id=product.id,
                        scheme_name=item["name"],
                        scheme_description=item["desc"],
                        scheme_image_url=item["img"],
                        source_url=item.get("source_url")
                    ))
            
            # Seed Patents
            existing_patents = session.exec(select(Patent).where(Patent.product_id == product.id)).all()
            if not existing_patents and data.get("patents"):
                for item in data["patents"]:
                    session.add(Patent(
                        product_id=product.id,
                        title=item["title"],
                        source_id=item["source_id"],
                        patent_type=item["type"],
                        claim_summary=item["claims"],
                        diseases_in_claims=item["diseases"],
                        url=item["url"],
                        status="Active",
                        publication_date=datetime.now() # Mock date
                    ))

            # Seed Articles
            existing_articles = session.exec(select(ScientificArticle).where(ScientificArticle.product_id == product.id)).all()
            if not existing_articles and data.get("articles"):
                for item in data["articles"]:
                    session.add(ScientificArticle(
                        product_id=product.id,
                        title=item["title"],
                        doi=item["doi"],
                        authors=item["authors"],
                        abstract=item["desc"],
                        url=item["url"],
                        publication_date=datetime.strptime(item["date"], "%Y-%m-%d")
                    ))

            # Seed Conferences
            existing_conferences = session.exec(select(Conference).where(Conference.product_id == product.id)).all()
            if not existing_conferences and data.get("conferences"):
                for item in data["conferences"]:
                     session.add(Conference(
                        product_id=product.id,
                        conference_name=item["name"],
                        title=item["title"],
                        abstract=item["desc"],
                        url=item["url"],
                        date=datetime.strptime(item["date"], "%Y-%m-%d")
                    ))

            session.commit()
            print(f"Done {product.name}")

if __name__ == "__main__":
    seed_science()
