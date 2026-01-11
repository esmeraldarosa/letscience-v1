import httpx
from typing import List
from datetime import datetime
from .models import DataSourceConnector, IntelligenceRecord, SourceType

class ClinicalTrialsConnector(DataSourceConnector):
    """
    Connects to ClinicalTrials.gov API v2.
    """
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def search(self, query: str) -> List[IntelligenceRecord]:
        results = []
        try:
            # Fallback to curl via subprocess because httpx/requests are blocked (TLS fingerprinting likely)
            import subprocess
            import json
            
            cmd = [
                "curl", "-s", 
                f"{self.BASE_URL}?query.term={query}&pageSize=5",
                "-H", "User-Agent: curl/8.7.1",
                "-H", "Accept: application/json"
            ]
            
            # print(f"DEBUG: Running {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error fetching Clinical Trials (curl failed): {result.stderr}")
                return []
                
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                print(f"Error decoding Clinical Trials JSON from curl: {result.stdout[:100]}")
                return []
            
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
