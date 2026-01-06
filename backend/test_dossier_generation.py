
import sys
import os
from unittest.mock import MagicMock
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from backend.report_generator import create_dossier

def test_dossier_creation():
    # Mock Data
    product = MagicMock()
    product.name = "TestProduct"
    product.development_phase = "Phase 2"
    product.target_indication = "Lung Cancer"
    product.description = "A novel immunotherapy agent."
    
    trial = MagicMock()
    trial.phase = "Phase 2"
    trial.status = "Recruiting"
    trial.title = "A Study of TestProduct in Patients"
    
    patent = MagicMock()
    patent.source_id = "US123456"
    patent.title = "Method of treating cancer"
    patent.patent_type = "Composition"
    patent.status = "Active"
    patent.publication_date = datetime(2023, 1, 1)
    patent.assignee = "Big Pharma Inc."
    patent.url = "http://google.com/patents"
    
    article = MagicMock()
    article.title = "Efficacy of TestProduct"
    article.authors = "Doe J., Smith A."
    article.publication_date = datetime(2024, 5, 15)
    article.url = "http://pubmed.gov"

    milestone = MagicMock()
    milestone.date = datetime(2022, 1, 1)
    milestone.phase = "Phase 1"
    milestone.event = "First Patient Dosed"

    scheme = MagicMock()
    scheme.scheme_name = "Route A"
    scheme.scheme_description = "Convergent synthesis starting from..."
    scheme.source_url = "http://example.com/scheme.png"

    indication = MagicMock()
    indication.disease_name = "NSCLC"
    indication.approval_status = "Investigational"

    # Call generator
    try:
        pdf = create_dossier(
            product, 
            [trial], 
            [patent], 
            [article], 
            [milestone], 
            [scheme], 
            [indication]
        )
        
        # FPDF2 output() returns bytearray by default or bytes depending on method
        pdf_bytes = pdf.output()  
        
        # Save to file for user preview
        with open("dossier_preview.pdf", "wb") as f:
            f.write(pdf_bytes)

        print(f"PDF Generated successfully. Saved to 'dossier_preview.pdf'. Size: {len(pdf_bytes)} bytes")
        
        if len(pdf_bytes) > 1000:
            print("SUCCESS: PDF size is reasonable.")
        else:
            print("FAILURE: PDF too small.")
            
    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dossier_creation()
