from typing import List, Optional
from datetime import datetime
from .models import DataSourceConnector, IntelligenceRecord, SourceType

class PatentConnector(DataSourceConnector):
    """
    Simulates fetching patent data via a public API like EPO OPS or Google Patents.
    For the POC, we return structured mock data relevant to the query.
    """
    def search(self, query: str) -> List[IntelligenceRecord]:
        # deeply convincing mock data for "cancer" or "synthesis" queries
        mock_patents = [
            IntelligenceRecord(
                source_id="WO2025123456A1",
                source_type=SourceType.PATENT,
                title="NOVEL FORMULATION FOR PROTEIN KINASE INHIBITORS",
                abstract="A method for synthesizing a stable crystalline form of compound X for the treatment of solid tumors...",
                authors=["Dr. Jane Doe", "PharmaCorp Inc."],
                publication_date=datetime(2025, 5, 12),
                url="https://patents.google.com/patent/WO2025123456A1",
                metadata={
                    "status": "Granted",
                    "assignee": "PharmaCorp Inc.",
                    "jurisdiction": "WIPO"
                }
            ),
            IntelligenceRecord(
                source_id="US9876543B2",
                source_type=SourceType.PATENT,
                title="METHOD OF TREATING MELANOMA USING MONOCLONAL ANTIBODIES",
                abstract="Disclosed is a method of synthetic preparation of antibody Y targeting PD-1 receptors...",
                authors=["BioTech Solutions LLC"],
                publication_date=datetime(2024, 11, 2),
                url="https://patents.google.com/patent/US9876543B2",
                metadata={
                    "status": "Application",
                    "assignee": "BioTech Solutions LLC",
                    "jurisdiction": "US"
                }
            )
        ]
        
        # In a real scenario:
        # response = requests.get(f"https://ops.epo.org/rest-services/published-data/search?q={query}")
        
        return mock_patents
