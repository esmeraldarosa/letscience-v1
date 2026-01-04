from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class SourceType:
    ARTICLE = "article"
    PATENT = "patent"
    CLINICAL_TRIAL = "clinical_trial"
    CONFERENCE = "conference"

class IntelligenceRecord(BaseModel):
    """
    Unified model for any piece of scientific intelligence.
    """
    source_id: str  # Unique ID in the source system (DOI, Patent No, NCTId)
    source_type: str # One of SourceType constants
    title: str
    abstract: Optional[str] = None
    authors: List[str] = []
    publication_date: Optional[datetime] = None
    url: Optional[str] = None
    
    # Specific fields can be stored in metadata
    metadata: Dict = {}
    
    # Link to a specific product/compound if known at ingestion time
    related_product: Optional[str] = None

class DataSourceConnector:
    """
    Base class for all data connectors.
    """
    def search(self, query: str) -> List[IntelligenceRecord]:
        raise NotImplementedError
