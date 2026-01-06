from datetime import datetime
from report_generator import create_landscape_dossier
from models import Product, ClinicalTrial, Patent, ProductMilestone

def test_create_landscape_dossier():
    print("Testing Landscape Dossier Generation...")
    
    # Mock Data
    products = [
        Product(id=1, name="Prod A", development_phase="Phase 3", target_indication="Melanoma", description="MAb for Melanoma"),
        Product(id=2, name="Prod B", development_phase="Phase 2", target_indication="Melanoma", description="Small molecule for Melanoma"),
    ]
    
    trials = [
        ClinicalTrial(product_id=1, title="Trial A1", status="Recruiting", phase="Phase 3", nct_id="NCT123"),
        ClinicalTrial(product_id=2, title="Trial B1", status="Completed", phase="Phase 2", nct_id="NCT456"),
    ]
    
    patents = [
        Patent(product_id=1, title="Patent A", assignee="Pharma A", patent_type="Product", source_id="US123"),
    ]
    
    milestones = [
        ProductMilestone(product_id=1, date=datetime(2023, 1, 1), event="Phase 3 Start", phase="Phase 3"),
        ProductMilestone(product_id=2, date=datetime(2022, 6, 1), event="Phase 2 Start", phase="Phase 2"),
    ]
    
    # Generate
    pdf = create_landscape_dossier("Disease", "Melanoma", products, trials, patents, milestones)
    
    # Output to file
    outfile = "landscape_test_melanoma.pdf"
    pdf.output(outfile)
    print(f"Generated {outfile}")
    
    # Verify file exists and has size
    import os
    if os.path.exists(outfile) and os.path.getsize(outfile) > 1000:
        print("SUCCESS: PDF created and valid size.")
    else:
        print("FAILURE: PDF not created or too small.")

if __name__ == "__main__":
    test_create_landscape_dossier()
