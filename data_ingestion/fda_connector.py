import httpx
from typing import List
from datetime import datetime
from .models import DataSourceConnector, IntelligenceRecord, SourceType

class FDAConnector(DataSourceConnector):
    """
    Connects to ClinicalTrials.gov API v2.
    """
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def search(self, query: str) -> List[IntelligenceRecord]:
        results = []
        try:
            # We filter for recruiting studies related to the query
            params = {
                "query.term": query,
                "pageSize": 5,
                "dataset": "protocolSection,derivedSection" # Not exactly standard params, adjusting to v2 basics
            }
            # Simplified V2 GET
            url = f"{self.BASE_URL}?query.term={query}&pageSize=5"
            
            response = httpx.get(url, timeout=10)
            data = response.json()
            
            studies = data.get("studies", [])
            for study in studies:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design_module = protocol.get("designModule", {})
                
                nct_id = id_module.get("nctId", "Unknown")
                title = id_module.get("officialTitle") or id_module.get("briefTitle", "No Title")
                status = status_module.get("overallStatus", "Unknown")
                phases = design_module.get("phases", ["N/A"])
                
                record = IntelligenceRecord(
                    source_id=nct_id,
                    source_type=SourceType.CLINICAL_TRIAL,
                    title=title,
                    abstract=f"Study Status: {status}. Phases: {', '.join(phases)}",
                    publication_date=None, # Trials are ongoing
                    url=f"https://clinicaltrials.gov/study/{nct_id}",
                    metadata={
                        "phase": phases,
                        "status": status,
                        "conditions": protocol.get("conditionsModule", {}).get("conditions", [])
                    }
                )
                results.append(record)
                
        except Exception as e:
            print(f"Error fetching Clinical Trials: {e}")
            
        return results
