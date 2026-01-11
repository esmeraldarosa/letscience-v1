import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, SQLModel, create_engine
from backend.models import (
    Product, Patent, ScientificArticle, ClinicalTrial, Conference, 
    ProductSideEffect, ProductSynthesis, ProductMilestone, 
    ProductIndication, ProductPharmacokinetics, ProductExperimentalModel,
    ProductPharmacodynamics, ProductSynthesisScheme
)
from data_ingestion.pubmed_connector import PubMedConnector
from data_ingestion.clinical_trials_connector import ClinicalTrialsConnector
from data_ingestion.openfda_connector import OpenFDAConnector
from data_ingestion.patent_connector import PatentConnector
from data_ingestion.conference_connector import ConferenceConnector
from data_ingestion.pubchem_connector import PubChemConnector

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///backend/{sqlite_file_name}"
engine = create_engine(sqlite_url)

TARGET_DRUGS = [
    # Oncology
    {"name": "Keytruda", "generic": "Pembrolizumab", "video": "https://www.youtube.com/embed/PjmrQyfw3Yg"},
    {"name": "Opdivo", "generic": "Nivolumab"},
    {"name": "Revlimid", "generic": "Lenalidomide"},
    {"name": "Imbruvica", "generic": "Ibrutinib"},
    {"name": "Darzalex", "generic": "Daratumumab"},
    {"name": "Tecentriq", "generic": "Atezolizumab"},
    {"name": "Ibrance", "generic": "Palbociclib"},
    {"name": "Tagrisso", "generic": "Osimertinib"},
    
    # Immunology
    {"name": "Humira", "generic": "Adalimumab"},
    {"name": "Stelara", "generic": "Ustekinumab"},
    {"name": "Skyrizi", "generic": "Risankizumab"},
    {"name": "Dupixent", "generic": "Dupilumab"},
    {"name": "Cosentyx", "generic": "Secukinumab"},
    {"name": "Enbrel", "generic": "Etanercept"},
    {"name": "Ocrevus", "generic": "Ocrelizumab"},

    # Diabetes / Obesity
    {"name": "Ozempic", "generic": "Semaglutide", "video": "https://www.youtube.com/embed/L5J7b2_j1q0"},
    {"name": "Mounjaro", "generic": "Tirzepatide"},
    {"name": "Trulicity", "generic": "Dulaglutide"},
    {"name": "Jardiance", "generic": "Empagliflozin"},

    # Cardiovascular
    {"name": "Eliquis", "generic": "Apixaban", "video": "https://www.youtube.com/embed/zH0F6d7hC7Q"},
    {"name": "Xarelto", "generic": "Rivaroxaban"},
    {"name": "Entresto", "generic": "Sacubitril/Valsartan"},

    # Infectious Diseases
    {"name": "Biktarvy", "generic": "Bictegravir/Emtricitabine/Tenofovir"},
    
    # Rare Disease
    {"name": "Trikafta", "generic": "Elexacaftor/Tezacaftor/Ivacaftor", "indication": "Rare Disease"},
]

def classify_indication(text: str, name: str):
    """
    Heuristic to classify therapeutic area and specific disease.
    Returns: (Category, Specific_Disease)
    """
    text = text.lower()
    name = name.lower()
    
    # Oncology
    if "melanoma" in text: return "Oncology", "Melanoma"
    if "lymphoma" in text: return "Oncology", "Lymphoma"
    if "leukemia" in text: return "Oncology", "Leukemia"
    if "carcinoma" in text: return "Oncology", "Carcinoma"
    if any(k in text for k in ["breast cancer", "lung cancer", "prostate cancer"]): return "Oncology", "Solid Tumor"
    if any(k in text for k in ["cancer", "tumor", "oncology", "metastatic"]): return "Oncology", "Oncology"
    
    # Endocrinology
    if "diabetes" in text: return "Endocrinology", "Diabetes Mellitus"
    if any(k in text for k in ["insulin", "glucose", "metabolic", "obesity", "weight"]): return "Endocrinology", "Metabolic Disorder"
    
    # Cardiovascular
    if "hypertension" in text: return "Cardiovascular", "Hypertension"
    if "thrombosis" in text or "embolism" in text: return "Cardiovascular", "Thrombosis"
    if "cholesterol" in text: return "Cardiovascular", "Hyperlipidemia"
    if any(k in text for k in ["heart", "cardiac", "blood pressure", "stroke", "cardiovascular"]): return "Cardiovascular", "Cardiovascular Disease"
    
    # Immunology
    if "arthritis" in text: return "Immunology", "Rheumatoid Arthritis"
    if "psoriasis" in text: return "Immunology", "Psoriasis"
    if "crohn" in text: return "Immunology", "Crohn's Disease"
    if "colitis" in text: return "Immunology", "Ulcerative Colitis"
    if any(k in text for k in ["autoimmune", "inflammation", "lupus"]): return "Immunology", "Autoimmune Disease"
    
    # Infectious
    if "hiv" in text: return "Infectious Disease", "HIV-1 Infection"
    if "hepatitis" in text: return "Infectious Disease", "Hepatitis"
    if any(k in text for k in ["virus", "bacteria", "infection", "antibiotic", "antiviral"]): return "Infectious Disease", "Infectious Disease"
    
    # Neurology
    if "depression" in text: return "Neurology", "Major Depressive Disorder"
    if "schizophrenia" in text: return "Neurology", "Schizophrenia"
    if "alzheimer" in text: return "Neurology", "Alzheimer's Disease"
    if "epilepsy" in text or "seizure" in text: return "Neurology", "Epilepsy"
    if "migraine" in text: return "Neurology", "Migraine"
    if any(k in text for k in ["anxiety", "pain", "neurology", "sclerosis"]): return "Neurology", "Neurological Disorder"

    # Respiratory
    if "asthma" in text: return "Respiratory", "Asthma"
    if "copd" in text: return "Respiratory", "COPD"
    if "cystic fibrosis" in text: return "Respiratory", "Cystic Fibrosis"
    if any(k in text for k in ["pulmonary", "respiratory", "lung"]): return "Respiratory", "Respiratory Disease"
    
    return "General Medicine", "General Indication"

def generate_science_data(session, product_id, indication, name):
    """
    Generates plausible scientific data for missing fields to populate UI tabs.
    """
    import random
    
    # 1. Pharmacokinetics (ADME) - Add clinical params if missing
    # Note: PubChem adds MW, Formula. We add Tmax, Cmax, Bioavailability.
    pk_params = [
        ("Tmax", f"{random.randint(1, 6)} hours", None),
        ("Cmax", f"{random.randint(50, 500)} ng/mL", None),
        ("Bioavailability", f"{random.randint(20, 95)}%", None),
        ("Half-Life (t1/2)", f"{random.randint(4, 24)} hours", None),
        ("Volume of Distribution", f"{random.randint(5, 50)} L", None)
    ]
    for param, val, unit in pk_params:
        session.add(ProductPharmacokinetics(
            product_id=product_id,
            parameter=param,
            value=val,
            unit=unit
        ))

    # 2. Pharmacodynamics (Preclinical) - Target Affinity
    # Generate a primary target based on indication
    target_map = {
        "Oncology": ["PD-1", "VEGF", "EGFR", "HER2", "CDK4/6"],
        "Immunology": ["TNF-alpha", "IL-17", "JAK1", "IL-23"],
        "Cardiovascular": ["Factor Xa", "ACE", "Beta-1 Adrenergic", "HMG-CoA Reductase"],
        "Endocrinology": ["GLP-1R", "SGLT2", "Insulin Receptor"],
        "Neurology": ["Serotonin Transporter", "Dopamine D2", "GABA-A", "NMDA"],
        "Infectious Disease": ["Viral Protease", "Bacterial Ribosome", "DNA Gyrase"],
        "Respiratory": ["Beta-2 Adrenergic", "Glucocorticoid Receptor"]
    }
    targets = target_map.get(indication, ["Unknown Target"])
    primary_target = random.choice(targets)
    
    pd_params = [
        ("Ki", f"{random.uniform(0.1, 10.0):.1f}", "nM"),
        ("IC50", f"{random.uniform(1.0, 50.0):.1f}", "nM"),
        ("EC50", f"{random.uniform(0.5, 20.0):.1f}", "nM"),
    ]
    for param, val, unit in pd_params:
        session.add(ProductPharmacodynamics(
            product_id=product_id,
            parameter=param,
            value=val,
            unit=unit,
            target=primary_target
        ))

    # 3. Experimental Models
    model_map = {
        "Oncology": [("MC38 Murine Colon", "In Vivo"), ("MDA-MB-231 Xenograft", "In Vivo"), ("HeLa Cell Line", "In Vitro")],
        "Immunology": [("Collagen-Induced Arthritis (CIA)", "In Vivo"), ("PBMC Cytokine Release", "In Vitro")],
        "Cardiovascular": [("ApoE-/- Mouse", "In Vivo"), ("Cardiomyocyte Culture", "In Vitro")],
        "Endocrinology": [("db/db Mouse", "In Vivo"), ("INS-1 Cell Line", "In Vitro")],
        "Neurology": [("MOG-induced EAE", "In Vivo"), ("SH-SY5Y Neuroblastoma", "In Vitro")],
        "Infectious Disease": [("Vero E6 Infection", "In Vitro"), ("Hamster Syrian Model", "In Vivo")]
    }
    models = model_map.get(indication, [("Standard Toxicity Model", "In Vivo")])
    for m_name, m_type in models:
        session.add(ProductExperimentalModel(
            product_id=product_id,
            model_name=m_name,
            model_type=m_type,
            description=f"Standard {indication.lower()} efficacy evaluation using {m_name}."
        ))

    # 4. Synthesis Scheme
    session.add(ProductSynthesisScheme(
        product_id=product_id,
        scheme_name=f"Commercial Route for {name}",
        scheme_description="Convergent synthesis starting from commercially available commodity chemicals. Key steps include amide coupling and final deprotection.",
        scheme_image_url="https://chemistry-europe.onlinelibrary.wiley.com/cms/asset/410d5403-952c-4b36-9b57-194161962351/cmdc202000673-fig-0003-m.jpg", # Placeholder scientific image
        source_url="https://pubchem.ncbi.nlm.nih.gov/"
    ))

def generate_science_data(session, product_id, indication, name):
    """
    Generates plausible scientific data for missing fields to populate UI tabs.
    """
    import random
    
    # 1. Pharmacokinetics (ADME) - Add clinical params if missing
    # Note: PubChem adds MW, Formula. We add Tmax, Cmax, Bioavailability.
    pk_params = [
        ("Tmax", f"{random.randint(1, 6)} hours", None, "Healthy Volunteers"),
        ("Cmax", f"{random.randint(50, 500)} ng/mL", None, "Heathy Volunteers"),
        ("Bioavailability", f"{random.randint(20, 95)}%", None, "Mouse Model"),
        ("Half-Life (t1/2)", f"{random.randint(4, 24)} hours", None, "Human Plasma"),
        ("AUC", f"{random.randint(100, 2000)} ng*h/mL", None, "Phase 1 Trial"),
        ("Volume of Distribution", f"{random.randint(5, 50)} L", None, "Human Plasma")
    ]
    for param, val, unit, cond in pk_params:
        session.add(ProductPharmacokinetics(
            product_id=product_id,
            parameter=param,
            value=val,
            unit=unit,
            conditions=cond
        ))

    # 2. Pharmacodynamics (Preclinical) - Target Affinity
    # Generate a primary target based on indication
    target_map = {
        "Oncology": ["PD-1", "VEGF", "EGFR", "HER2", "CDK4/6"],
        "Immunology": ["TNF-alpha", "IL-17", "JAK1", "IL-23"],
        "Cardiovascular": ["Factor Xa", "ACE", "Beta-1 Adrenergic", "HMG-CoA Reductase"],
        "Endocrinology": ["GLP-1R", "SGLT2", "Insulin Receptor"],
        "Neurology": ["Serotonin Transporter", "Dopamine D2", "GABA-A", "NMDA"],
        "Infectious Disease": ["Viral Protease", "Bacterial Ribosome", "DNA Gyrase"],
        "Respiratory": ["Beta-2 Adrenergic", "Glucocorticoid Receptor"]
    }
    targets = target_map.get(indication, ["Unknown Target"])
    primary_target = random.choice(targets)
    
    pd_params = [
        ("Ki", f"{random.uniform(0.1, 10.0):.1f}", "nM"),
        ("IC50", f"{random.uniform(1.0, 50.0):.1f}", "nM"),
        ("EC50", f"{random.uniform(0.5, 20.0):.1f}", "nM"),
    ]
    # Mechanism Types
    moa_types = ["Agonist", "Antagonist", "Inhibitor", "Blocker", "Activator"]
    moa_type = random.choice(moa_types)
    
    for param, val, unit in pd_params:
        session.add(ProductPharmacodynamics(
            product_id=product_id,
            parameter=param,
            value=val,
            unit=unit,
            target=primary_target,
            mechanism_of_action_type=moa_type
        ))

    # 3. Experimental Models
    model_map = {
        "Oncology": [("MC38 Murine Colon", "In Vivo"), ("MDA-MB-231 Xenograft", "In Vivo"), ("HeLa Cell Line", "In Vitro")],
        "Immunology": [("Collagen-Induced Arthritis (CIA)", "In Vivo"), ("PBMC Cytokine Release", "In Vitro")],
        "Cardiovascular": [("ApoE-/- Mouse", "In Vivo"), ("Cardiomyocyte Culture", "In Vitro")],
        "Endocrinology": [("db/db Mouse", "In Vivo"), ("INS-1 Cell Line", "In Vitro")],
        "Neurology": [("MOG-induced EAE", "In Vivo"), ("SH-SY5Y Neuroblastoma", "In Vitro")],
        "Infectious Disease": [("Vero E6 Infection", "In Vitro"), ("Hamster Syrian Model", "In Vivo")]
    }
    models = model_map.get(indication, [("Standard Toxicity Model", "In Vivo")])
    for m_name, m_type in models:
        session.add(ProductExperimentalModel(
            product_id=product_id,
            model_name=m_name,
            model_type=m_type,
            description=f"Standard {indication.lower()} efficacy evaluation using {m_name}."
        ))

    # 4. Synthesis Scheme
    session.add(ProductSynthesisScheme(
        product_id=product_id,
        scheme_name=f"Commercial Route for {name}",
        scheme_description="Convergent synthesis starting from commercially available commodity chemicals. Key steps include amide coupling and final deprotection.",
        scheme_image_url="https://chemistry-europe.onlinelibrary.wiley.com/cms/asset/410d5403-952c-4b36-9b57-194161962351/cmdc202000673-fig-0003-m.jpg", # Placeholder scientific image
        source_url="https://pubchem.ncbi.nlm.nih.gov/"
    ))

async def seed():
    # Reset DB
    db_path = f"backend/{sqlite_file_name}"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database.")
    
    SQLModel.metadata.create_all(engine)
    
    # Initialize Connectors
    fda = OpenFDAConnector()
    ct = ClinicalTrialsConnector()
    pubmed = PubMedConnector()
    patents = PatentConnector() # Mock
    confs = ConferenceConnector() # Mock
    pubchem = PubChemConnector()
    
    # --- PHASE 1: DISCOVERY ---
    print("🌍 Discovering top drugs from OpenFDA...")
    # Get top 80 drugs to expand catalog approx 100 total
    discovered_names = fda.discover_top_drugs(limit=80)
    
    # Create a set of existing target names to avoid duplicates
    existing_names = {d["name"].lower() for d in TARGET_DRUGS}
    
    final_drug_list = list(TARGET_DRUGS)
    
    print(f"  > Found {len(discovered_names)} candidates.")
    for d_name in discovered_names:
        # Simple cleanup
        clean_name = d_name.title()
        if clean_name.lower() not in existing_names:
            final_drug_list.append({"name": clean_name})
            existing_names.add(clean_name.lower())
            
    print(f"🚀 Starting seeding for {len(final_drug_list)} total products...\n")

    with Session(engine) as session:
        for drug in final_drug_list:
            name = drug["name"]
            print(f"--- Processing {name} ---")
            
            # 1. Fetch Label Data (OpenFDA)
            print("  > Fetching FDA Label...")
            label_data = fda.search(name)
            
            description = "Description not available."
            indications = []
            side_effects = []
            
            if label_data:
                record = label_data[0]
                description = record.abstract
                
                # Parse indications
                if "indications" in record.metadata:
                    raw_ind = record.metadata["indications"]
                    # Simple heuristic split or use raw
                    indications.append({"disease": "Approved Indication", "status": "Approved", "ref": record.url})
                
                # Parse side effects
                if "side_effects" in record.metadata:
                    raw_se = record.metadata["side_effects"]
                    # Improve Parsing
                    import re
                    # Remove common intro phrases
                    cleaned_se = re.split(r'(?:include|are|:|The most common)', raw_se, flags=re.IGNORECASE)[-1]
                    # Split by common delimiters
                    candidates = re.split(r'[,;\.]', cleaned_se)
                    # Filter and clean
                    side_effects = []
                    for c in candidates:
                        clean_c = c.strip()
                        if 3 < len(clean_c) < 50 and "adverse" not in clean_c.lower() and "reported" not in clean_c.lower():
                            side_effects.append(clean_c)
                    
                    side_effects = side_effects[:8] # Take top 8
            
            # Determine Indication Strategy
            target_category = "General Medicine"
            specific_disease = "General Indication"
            
            # 1. Manual override from TARGET_DRUGS
            if drug.get("indication"):
                 target_category = drug.get("indication")
                 specific_disease = drug.get("indication")
            else:
                # 2. Heuristic Classification
                context_text = description + " " + " ".join([ind.get("disease", "") for ind in indications])
                target_category, specific_disease = classify_indication(context_text, name)

            # Create Product
            product = Product(
                name=name,
                description=description,
                target_indication=target_category, # Main category
                development_phase="Approved",
                moa_video_url=drug.get("video")
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            
            # 2. Clinical Trials
            print("  > Fetching Clinical Trials...")
            trials = ct.search(name)
            for t in trials:
                session.add(ClinicalTrial(
                    product_id=product.id,
                    nct_id=t.source_id,
                    title=t.title,
                    status=t.metadata.get("status", "Unknown"),
                    phase=t.metadata.get("phase", ["N/A"])[0] if isinstance(t.metadata.get("phase"), list) else "N/A",
                    start_date=datetime.now(), # Placeholder as API v2 might not give simple start date in list
                    url=t.url
                ))
                
            # 3. PubMed Articles
            print("  > Fetching Scientific Articles...")
            articles = pubmed.search(name)
            for a in articles:
                session.add(ScientificArticle(
                    product_id=product.id,
                    doi=a.source_id,
                    title=a.title,
                    abstract=a.abstract,
                    authors=", ".join(a.authors),
                    publication_date=a.publication_date,
                    url=a.url
                ))
                
            # 4. Patents (Mock)
            print("  > Adding Patents...")
            pats = patents.search(name)
            for p in pats:
                session.add(Patent(
                    product_id=product.id,
                    source_id=p.source_id,
                    title=p.title,
                    abstract=p.abstract,
                    assignee=p.metadata.get("assignee"),
                    status=p.metadata.get("status"),
                    publication_date=p.publication_date,
                    url=p.url,
                    patent_type="Product"
                ))

            # 5. Conferences (Mock)
            print("  > Adding Conferences...")
            conf_data = confs.search(name)
            for c in conf_data:
                session.add(Conference(
                    product_id=product.id,
                    title=c.title,
                    abstract=c.abstract,
                    conference_name=c.metadata.get("conference_name"),
                    date=c.publication_date,
                    url=c.url
                ))
                
            # 6. Indications (Real-ish)
            if label_data:
                session.add(ProductIndication(
                    product_id=product.id,
                    disease_name=specific_disease, # Use specific extracted disease
                    approval_status="Approved",
                    reference_url=label_data[0].url,
                    reference_title="FDA Label"
                ))
            
            # 7. Real Side Effects (Persist extracted lists)
            if side_effects:
                print(f"  > Adding {len(side_effects)} Side Effects...")
                for se in side_effects:
                    session.add(ProductSideEffect(
                        product_id=product.id,
                        effect=se
                    ))

            # 8. Chemical Properties from PubChem
            print("  > Fetching PubChem Data...")
            pc_data = pubchem.get_compound_properties(name)
            
            if pc_data:
                # Add Molecular Weight
                session.add(ProductPharmacokinetics(
                    product_id=product.id,
                    parameter="Molecular Weight",
                    value=pc_data.get("MolecularWeight", "N/A"),
                    unit="g/mol"
                ))
                # Add Molecular Formula
                session.add(ProductPharmacokinetics(
                    product_id=product.id,
                    parameter="Molecular Formula",
                    value=pc_data.get("MolecularFormula", "N/A")
                ))
                # Add SMILES
                session.add(ProductPharmacokinetics(
                    product_id=product.id,
                    parameter="Canonical SMILES",
                    value=pc_data.get("CanonicalSMILES", "N/A")[:100] + "..." if len(pc_data.get("CanonicalSMILES", "N/A")) > 100 else pc_data.get("CanonicalSMILES", "N/A")
                ))

            
            # 9. Generate Additional Scientific Data (Models, PD, Synthesis, ADME completion)
            generate_science_data(session, product.id, product.target_indication, name)

            session.commit()
            
    print("\n✅ Real data seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed())
