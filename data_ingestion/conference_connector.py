from typing import List
from datetime import datetime, timedelta
from .models import DataSourceConnector, IntelligenceRecord, SourceType

class ConferenceConnector(DataSourceConnector):
    """
    Connects to abstract databases for major conferences (ASCO, ESMO, AACR).
    Data access is usually restricted, so this is a simulation for the prototype.
    """
    def search(self, query: str) -> List[IntelligenceRecord]:
        # Simulated recent conference abstracts
        mock_abstracts = [
            IntelligenceRecord(
                source_id="ASCO-2025-ABS-1001",
                source_type=SourceType.CONFERENCE,
                title=f"Phase 2 results of Novel Agent X in {query} patients",
                abstract="Presented at ASCO 2025. The study demonstrated significant improvement in PFS...",
                authors=["Dr. Oncologist A", "University Hospital Zurich"],
                publication_date=datetime.now() - timedelta(days=60),
                url="https://asco.org/abstracts/1001",
                metadata={
                    "conference_name": "ASCO Annual Meeting 2025",
                    "presentation_type": "Oral Presentation"
                }
            ),
             IntelligenceRecord(
                source_id="ESMO-2024-LBA-5",
                source_type=SourceType.CONFERENCE,
                title=f"Late Breaking Abstract: Survival outcomes in {query}",
                abstract="ESMO Congress 2024. Overall survival data remains immature but promising...",
                authors=["Leading Researcher B", "Global Cancer Center"],
                publication_date=datetime(2024, 9, 15),
                url="https://esmo.org/abstracts/LBA5",
                metadata={
                    "conference_name": "ESMO Congress 2024",
                    "presentation_type": "Poster Discussion"
                }
            )
        ]
        return mock_abstracts
