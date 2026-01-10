from report_generator import create_patentability_study
from models import Product, Patent
from datetime import datetime

def test_report():
    print("Testing Patentability Report...")
    
    # Mock Data
    p = Product(name="TestDrug", development_phase="Approved", target_indication="Cancer")
    patents = [
        Patent(
            source_id="US123", 
            title="Test Patent 1", 
            patent_type="Composition", 
            status="Active", 
            expiry_date=datetime(2030, 1, 1),
            claim_summary="Claims compound X",
            diseases_in_claims="Cancer"
        ),
        Patent(
            source_id="US456", 
            title="Test Patent 2", 
            patent_type="Method of Use", 
            status="Active", 
            expiry_date=datetime(2035, 5, 20),
            claim_summary="Claims method of treating Y",
            diseases_in_claims="Cancer"
        )
    ]
    
    pdf_bytes = create_patentability_study(p, patents)
    
    filename = "test_patent_report.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
        
    import os
    if os.path.exists(filename) and os.path.getsize(filename) > 1000:
        print(f"SUCCESS: Generated {filename} ({os.path.getsize(filename)} bytes)")
    else:
        print("FAILURE: Report not generated correctly")

if __name__ == "__main__":
    test_report()
