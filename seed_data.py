import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, SQLModel, create_engine
from backend.models import (
    Product, Patent, ScientificArticle, ClinicalTrial, Conference, 
    ProductSideEffect, ProductSynthesis, ProductMilestone, 
    ProductIndication, ProductSynthesisScheme, ProductPharmacokinetics, ProductExperimentalModel
)
from data_ingestion.pubmed_connector import PubMedConnector
from data_ingestion.patent_connector import PatentConnector
from data_ingestion.conference_connector import ConferenceConnector
from backend.nlp_utils import extract_side_effects, extract_synthesis_steps

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///backend/{sqlite_file_name}"

engine = create_engine(sqlite_url)

# --- ENRICHED DATA ---

PRODUCT_DATA = {
    "Keytruda": {
        "description": "Pembrolizumab: A programmed death receptor-1 (PD-1)-blocking antibody.",
        "indication": "Melanoma, NSCLC, Head and Neck Cancer",
        "indication": "Melanoma, NSCLC, Head and Neck Cancer",
        "phase": "Approved",
        "search_term": "Keytruda melanoma",
        "video_url": "https://www.youtube.com/embed/PjmrQyfw3Yg",
        "pharmacokinetics": [
            {"parameter": "Bioavailability", "value": "100%", "unit": "(IV administration)"},
            {"parameter": "Tmax", "value": "Immediate", "unit": ""},
            {"parameter": "Vd", "value": "6.0", "unit": "L"},
            {"parameter": "Half-life (t1/2)", "value": "22", "unit": "days"},
            {"parameter": "Clearance", "value": "0.22", "unit": "L/day"}
        ],
        "experimental_models": [
            {"model_name": "Human PD-1 Knockin Mouse", "type": "In Vivo", "description": "Used to assess anti-tumor efficacy of anti-PD-1 antibodies in syngeneic tumor models."},
            {"model_name": "Mixed Lymphocyte Reaction (MLR)", "type": "In Vitro", "description": "Assesses T-cell activation and cytokine release (IFN-g) upon PD-1 blockade."}
        ],
        "patents": [
            {
                "source_id": "US8168757B2",
                "title": "Humanized anti-PD-1 antibodies and uses thereof",
                "abstract": "The invention provides humanized antibodies that specifically bind to PD-1.",
                "assignee": "Merck Sharp & Dohme LLC",
                "status": "Granted",
                "claim_summary": "Claim 1: An isolated humanized antibody that binds PD-1 with KD<10nM. Claim 5: A pharmaceutical composition comprising the antibody.",
                "diseases_in_claims": "Melanoma, Non-small cell lung cancer, Head and neck squamous cell carcinoma",
                "patent_type": "Product",
                "url": "https://patents.google.com/patent/US8168757B2"
            },
            {
                "source_id": "US9387247B2",
                "title": "Method of treating cancer with PD-1 antibody in combination with chemotherapy",
                "abstract": "Methods for treating cancer using anti-PD-1 antibody in combination with platinum-based chemotherapy.",
                "assignee": "Merck Sharp & Dohme LLC",
                "status": "Granted",
                "claim_summary": "Claim 1: A method of treating NSCLC comprising administering pembrolizumab with carboplatin and pemetrexed.",
                "diseases_in_claims": "Non-small cell lung cancer",
                "patent_type": "Combination",
                "url": "https://patents.google.com/patent/US9387247B2"
            }
        ],
        "trials": [
            {"nct_id": "NCT02362594", "title": "KEYNOTE-024: Pembrolizumab vs Chemotherapy for PD-L1+ NSCLC", "status": "Completed", "phase": "Phase 3", "start_date": datetime(2015, 2, 1), "sponsor": "Merck Sharp & Dohme LLC"},
            {"nct_id": "NCT01866319", "title": "KEYNOTE-006: Pembrolizumab vs Ipilimumab for Advanced Melanoma", "status": "Completed", "phase": "Phase 3", "start_date": datetime(2013, 6, 1), "sponsor": "Merck Sharp & Dohme LLC"},
            {"nct_id": "NCT03142334", "title": "KEYNOTE-789: Pembrolizumab + Chemo for EGFR-mutated NSCLC", "status": "Recruiting", "phase": "Phase 3", "start_date": datetime(2017, 5, 10), "sponsor": "Merck Sharp & Dohme LLC"}
        ],
        "milestones": [
            {"date": datetime(2010, 1, 15), "event": "IND Filed", "phase": "Preclinical"},
            {"date": datetime(2011, 4, 1), "event": "Phase 1 Start", "phase": "Phase 1"},
            {"date": datetime(2013, 6, 1), "event": "Breakthrough Therapy Designation", "phase": "Phase 2"},
            {"date": datetime(2014, 9, 4), "event": "FDA Approval (Melanoma)", "phase": "Approved"},
            {"date": datetime(2016, 10, 24), "event": "FDA Approval (NSCLC 1L)", "phase": "Approved"}
        ],
        "indications": [
            {"disease": "Melanoma", "status": "Approved", "ref_title": "KEYNOTE-006 Trial Results", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/25891173/"},
            {"disease": "Non-small cell lung cancer (NSCLC)", "status": "Approved", "ref_title": "KEYNOTE-024 Trial Results", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/27718847/"},
            {"disease": "Head and Neck Squamous Cell Carcinoma", "status": "Approved", "ref_title": "KEYNOTE-048 Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/31679945/"},
            {"disease": "Triple-negative Breast Cancer", "status": "Phase 3", "ref_title": "KEYNOTE-355", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/33306201/"}
        ],
        "side_effects": ["Fatigue", "Rash", "Pruritus", "Diarrhea", "Nausea", "Hypothyroidism"],
        "synthesis_steps": ["Produced in CHO cell lines via recombinant DNA technology.", "Harvested via centrifugation and depth filtration.", "Purified using Protein A affinity chromatography.", "Final formulation in histidine buffer."]
    },
    "Ozempic": {
        "description": "Semaglutide: A GLP-1 receptor agonist for T2D and obesity.",
        "indication": "Type 2 Diabetes, Obesity",
        "phase": "Approved",
        "search_term": "Semaglutide diabetes",
        "video_url": "https://www.youtube.com/embed/L5J7b2_j1q0",
        "pharmacokinetics": [
            {"parameter": "Bioavailability", "value": "89%", "unit": "(SC administration)"},
            {"parameter": "Tmax", "value": "1-3", "unit": "days"},
            {"parameter": "Half-life (t1/2)", "value": "1 week", "unit": ""},
            {"parameter": "Plasma Protein Binding", "value": ">99%", "unit": "(to albumin)"}
        ],
        "experimental_models": [
            {"model_name": "db/db Mouse Model", "type": "In Vivo", "description": "Used to evaluate glucose lowering and weight loss effects in leptin receptor-deficient mice."},
            {"model_name": "GLP-1 Receptor Binding Assay", "type": "In Vitro", "description": "Measures affinity and potency at the human GLP-1 receptor."}
        ],
        "patents": [
            {
                "source_id": "US8129343B2",
                "title": "GLP-1 analogues with extended half-life",
                "abstract": "Novel peptide analogues of GLP-1 with albumin-binding moiety for once-weekly administration.",
                "assignee": "Novo Nordisk A/S",
                "status": "Granted",
                "claim_summary": "Claim 1: A modified GLP-1 peptide comprising amino acid substitutions and a C18 fatty diacid attached via amino-PEG linker.",
                "diseases_in_claims": "Type 2 diabetes mellitus, Obesity",
                "patent_type": "Product",
                "url": "https://patents.google.com/patent/US8129343B2"
            }
        ],
        "trials": [
            {"nct_id": "NCT02128932", "title": "SUSTAIN-6: CV Outcomes with Semaglutide in T2D", "status": "Completed", "phase": "Phase 3", "start_date": datetime(2014, 5, 1), "sponsor": "Novo Nordisk A/S"},
            {"nct_id": "NCT03548935", "title": "STEP-1: Semaglutide 2.4mg for Obesity", "status": "Completed", "phase": "Phase 3", "start_date": datetime(2018, 6, 1), "sponsor": "Novo Nordisk A/S"}
        ],
        "milestones": [
            {"date": datetime(2012, 3, 1), "event": "Phase 1 Start", "phase": "Phase 1"},
            {"date": datetime(2015, 9, 1), "event": "Phase 3 SUSTAIN Program Start", "phase": "Phase 3"},
            {"date": datetime(2017, 12, 5), "event": "FDA Approval (Ozempic - T2D)", "phase": "Approved"},
            {"date": datetime(2021, 6, 4), "event": "FDA Approval (Wegovy - Obesity)", "phase": "Approved"}
        ],
        "indications": [
            {"disease": "Type 2 Diabetes", "status": "Approved", "ref_title": "SUSTAIN-6 Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/27633186/"},
            {"disease": "Obesity/Weight Management", "status": "Approved", "ref_title": "STEP-1 Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/33567185/"},
            {"disease": "NASH", "status": "Phase 2", "ref_title": "Semaglutide in NASH", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/33185364/"}
        ],
        "side_effects": ["Nausea", "Vomiting", "Diarrhea", "Abdominal pain", "Constipation"],
        "synthesis_steps": ["Solid-phase peptide synthesis (SPPS) of GLP-1 backbone.", "Attachment of C18 fatty diacid via amino-PEG linker.", "HPLC purification.", "Lyophilization or solution formulation."]
    },
    "Humira": {
        "description": "Adalimumab: A TNF-alpha inhibiting anti-inflammatory monoclonal antibody.",
        "indication": "Rheumatoid Arthritis, Crohn's Disease, Psoriasis",
        "phase": "Approved",
        "search_term": "Adalimumab arthritis",
        "patents": [
            {
                "source_id": "US6090382A",
                "title": "Human antibodies that bind human TNFα",
                "abstract": "Isolated human antibodies that bind to human TNFα and neutralize its activity.",
                "assignee": "AbbVie Inc.",
                "status": "Expired",
                "claim_summary": "Claim 1: An isolated human antibody that binds human TNFα with KD of 1×10⁻⁸ M or less.",
                "diseases_in_claims": "Rheumatoid arthritis, Crohn's disease, Psoriasis, Ankylosing spondylitis",
                "patent_type": "Product",
                "url": "https://patents.google.com/patent/US6090382A"
            }
        ],
        "trials": [
            {"nct_id": "NCT00195702", "title": "ARMADA: Adalimumab + MTX in RA", "status": "Completed", "phase": "Phase 3"},
            {"nct_id": "NCT00055497", "title": "CHARM: Adalimumab in Crohn's Disease", "status": "Completed", "phase": "Phase 3"}
        ],
        "milestones": [
            {"date": datetime(1997, 1, 1), "event": "Discovery at BASF/Knoll", "phase": "Preclinical"},
            {"date": datetime(1999, 6, 1), "event": "Phase 3 Start", "phase": "Phase 3"},
            {"date": datetime(2002, 12, 31), "event": "FDA Approval (RA)", "phase": "Approved"},
            {"date": datetime(2007, 2, 1), "event": "FDA Approval (Crohn's)", "phase": "Approved"}
        ],
        "indications": [
            {"disease": "Rheumatoid Arthritis", "status": "Approved", "ref_title": "ARMADA Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/12528101/"},
            {"disease": "Crohn's Disease", "status": "Approved", "ref_title": "CHARM Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/17258735/"},
            {"disease": "Psoriasis", "status": "Approved", "ref_title": "REVEAL Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/18063176/"},
            {"disease": "Ulcerative Colitis", "status": "Approved", "ref_title": "ULTRA 2 Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/23041909/"}
        ],
        "side_effects": ["Injection site reactions", "Upper respiratory infections", "Headache", "Rash", "Nausea"],
        "synthesis_steps": ["Produced in CHO cell culture.", "Harvested via centrifugation.", "Protein A affinity chromatography.", "Ion exchange chromatography.", "Viral inactivation and filtration."]
    },
    "Eliquis": {
        "description": "Apixaban: An oral anticoagulant Factor Xa inhibitor.",
        "indication": "Atrial Fibrillation, DVT, PE",
        "phase": "Approved",
        "search_term": "Apixaban anticoagulant",
        "video_url": "https://www.youtube.com/embed/zH0F6d7hC7Q",
        "pharmacokinetics": [
            {"parameter": "Bioavailability", "value": "~50%", "unit": "(Oral)"},
            {"parameter": "Tmax", "value": "3-4", "unit": "hours"},
            {"parameter": "Half-life (t1/2)", "value": "12", "unit": "hours"},
            {"parameter": "Metabolism", "value": "CYP3A4", "unit": "(Minor contribution)"}
        ],
        "experimental_models": [
            {"model_name": "Rabbit AV Shunt Model", "type": "In Vivo", "description": "Assess antithrombotic efficacy in preventing clot formation in an arteriovenous shunt."},
            {"model_name": "Factor Xa Enzyme Assay", "type": "In Vitro", "description": "Measurement of Ki values against human Factor Xa."}
        ],
        "patents": [
            {
                "source_id": "US6967208B2",
                "title": "Lactam-containing compounds as factor Xa inhibitors",
                "abstract": "Novel lactam compounds with factor Xa inhibitory activity for prevention of thromboembolic disorders.",
                "assignee": "Bristol-Myers Squibb / Pfizer",
                "status": "Granted",
                "claim_summary": "Claim 1: A compound of formula I having factor Xa inhibitory activity with IC50 < 100nM.",
                "diseases_in_claims": "Atrial fibrillation, Deep vein thrombosis, Pulmonary embolism",
                "patent_type": "Product",
                "url": "https://patents.google.com/patent/US6967208B2"
            }
        ],
        "trials": [
            {"nct_id": "NCT00412984", "title": "ARISTOTLE: Apixaban vs Warfarin in AF", "status": "Completed", "phase": "Phase 3", "start_date": datetime(2006, 12, 1), "sponsor": "Bristol-Myers Squibb"},
            {"nct_id": "NCT00643201", "title": "AMPLIFY: Apixaban for VTE Treatment", "status": "Completed", "phase": "Phase 3", "start_date": datetime(2008, 3, 1), "sponsor": "Pfizer"}
        ],
        "milestones": [
            {"date": datetime(2002, 1, 1), "event": "Discovery", "phase": "Preclinical"},
            {"date": datetime(2007, 6, 1), "event": "Phase 3 Start", "phase": "Phase 3"},
            {"date": datetime(2012, 12, 28), "event": "FDA Approval (AF)", "phase": "Approved"},
            {"date": datetime(2014, 8, 21), "event": "FDA Approval (DVT/PE)", "phase": "Approved"}
        ],
        "indications": [
            {"disease": "Atrial Fibrillation", "status": "Approved", "ref_title": "ARISTOTLE Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/21870978/"},
            {"disease": "Deep Vein Thrombosis", "status": "Approved", "ref_title": "AMPLIFY Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/23808982/"},
            {"disease": "Pulmonary Embolism", "status": "Approved", "ref_title": "AMPLIFY Trial", "ref_url": "https://pubmed.ncbi.nlm.nih.gov/23808982/"}
        ],
        "side_effects": ["Bleeding", "Bruising", "Nausea", "Anemia"],
        "synthesis_steps": ["Condensation of substituted pyrazole with lactam precursor.", "Palladium-catalyzed coupling.", "Recrystallization from ethanol/water.", "Tablet formulation with excipients."]
    }
}

def seed():
    # Remove existing DB
    db_path = f"backend/{sqlite_file_name}"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database.")

    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        for product_name, data in PRODUCT_DATA.items():
            print(f"--- Seeding {product_name} ---")
            
            product = Product(
                name=product_name,
                description=data["description"],
                target_indication=data["indication"],
                development_phase=data["phase"],
                moa_video_url=data.get("video_url")
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            
            # Patents with enhanced data
            print("  > Adding enriched patents...")
            for pat in data.get("patents", []):
                session.add(Patent(
                    product_id=product.id,
                    source_id=pat["source_id"],
                    title=pat["title"],
                    abstract=pat["abstract"],
                    assignee=pat["assignee"],
                    status=pat["status"],
                    publication_date=datetime.now() - timedelta(days=365*5),
                    url=pat["url"],
                    claim_summary=pat["claim_summary"],
                    diseases_in_claims=pat["diseases_in_claims"],
                    patent_type=pat["patent_type"]
                ))
            
            # Clinical Trials with full data
            print("  > Adding clinical trials...")
            for trial in data.get("trials", []):
                session.add(ClinicalTrial(
                    product_id=product.id,
                    nct_id=trial["nct_id"],
                    title=trial["title"],
                    status=trial["status"],
                    phase=trial["phase"],
                    start_date=trial.get("start_date"),
                    sponsor=trial.get("sponsor"),
                    url=f"https://clinicaltrials.gov/study/{trial['nct_id']}"
                ))
            
            # Milestones
            print("  > Adding development milestones...")
            for ms in data.get("milestones", []):
                session.add(ProductMilestone(
                    product_id=product.id,
                    date=ms["date"],
                    event=ms["event"],
                    phase=ms["phase"]
                ))
            
            # Indications with references
            print("  > Adding disease indications...")
            for ind in data.get("indications", []):
                session.add(ProductIndication(
                    product_id=product.id,
                    disease_name=ind["disease"],
                    approval_status=ind["status"],
                    reference_title=ind["ref_title"],
                    reference_url=ind["ref_url"]
                ))
            
            # Side effects
            print("  > Adding side effects...")
            for effect in data.get("side_effects", []):
                session.add(ProductSideEffect(product_id=product.id, effect=effect))
            
            # Synthesis steps
            print("  > Adding synthesis steps...")
            for step in data.get("synthesis_steps", []):
                session.add(ProductSynthesis(product_id=product.id, step_description=step))
            
            # Pharmacokinetics
            print("  > Adding pharmacokinetics...")
            for pk in data.get("pharmacokinetics", []):
                session.add(ProductPharmacokinetics(
                    product_id=product.id,
                    parameter=pk["parameter"],
                    value=pk["value"],
                    unit=pk["unit"]
                ))
            
            # Experimental Models
            print("  > Adding experimental models...")
            for model in data.get("experimental_models", []):
                session.add(ProductExperimentalModel(
                    product_id=product.id,
                    model_name=model["model_name"],
                    model_type=model["type"],
                    description=model["description"]
                ))
            
            # Fetch real PubMed articles
            print(f"  > Fetching PubMed articles for {data['search_term']}...")
            try:
                pubmed = PubMedConnector()
                articles = pubmed.search(data['search_term'])
                for a in articles:
                    session.add(ScientificArticle(
                        product_id=product.id,
                        doi=a.source_id,
                        title=a.title,
                        abstract=a.abstract,
                        authors=", ".join(a.authors) if a.authors else "Unknown",
                        publication_date=a.publication_date,
                        url=a.url
                    ))
            except Exception as e:
                print(f"    Warning: PubMed fetch failed: {e}")
            
            # Conference data (mock)
            print("  > Adding conference abstracts...")
            try:
                confs = ConferenceConnector().search(product_name)
                for c in confs:
                    session.add(Conference(
                        product_id=product.id,
                        title=c.title,
                        abstract=c.abstract,
                        conference_name=c.metadata.get("conference_name", "Unknown"),
                        date=c.publication_date,
                        url=c.url
                    ))
            except Exception as e:
                print(f"    Warning: Conference fetch failed: {e}")
            
            session.commit()
        
        print("\n✅ Seeding complete with enriched data!")

if __name__ == "__main__":
    seed()
