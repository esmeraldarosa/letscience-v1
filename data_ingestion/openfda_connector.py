import httpx
from typing import List
from datetime import datetime
from .models import DataSourceConnector, IntelligenceRecord, SourceType

class OpenFDAConnector(DataSourceConnector):
    """
    Connects to OpenFDA API to fetch drug labels.
    """
    BASE_URL = "https://api.fda.gov/drug/label.json"

    def search(self, query: str) -> List[IntelligenceRecord]:
        results = []
        try:
            # Search for brand name
            url = f"{self.BASE_URL}?search=openfda.brand_name:\"{query}\"&limit=1"
            
            response = httpx.get(url, timeout=10)
            data = response.json()
            
            if "results" in data:
                res = data["results"][0]
                
                # Extract fields safely
                description = res.get("description", ["No description available."])[0]
                indications = res.get("indications_and_usage", ["No indications available."])[0]
                side_effects = res.get("adverse_reactions", ["No side effects listed."])[0]
                
                openfda = res.get("openfda", {})
                brand_name = openfda.get("brand_name", [query])[0]
                generic_name = openfda.get("generic_name", ["Unknown"])[0]
                manufacturer = openfda.get("manufacturer_name", ["Unknown"])[0]
                
                # Create a "Label" record
                record = IntelligenceRecord(
                    source_id=res.get("set_id", "Unknown"),
                    source_type="label", # Custom type for our internal use
                    title=f"FDA Label for {brand_name} ({generic_name})",
                    abstract=description[:500] + "...",
                    publication_date=datetime.now(), # Labels don't have a clear single date, using current for now
                    url=f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={res.get('set_id')}",
                    metadata={
                        "brand_name": brand_name,
                        "generic_name": generic_name,
                        "manufacturer": manufacturer,
                        "indications": indications,
                        "side_effects": side_effects
                    }
                )
                results.append(record)
                
        except Exception as e:
            print(f"Error fetching OpenFDA data for {query}: {e}")
            
        return results

    def discover_top_drugs(self, limit: int = 50) -> List[str]:
        """
        Discovers top frequently labeled drugs using OpenFDA aggregation.
        """
        # Ensure httpx is imported - usually redundant if duplicate but safe
        import httpx
        url = f"{self.BASE_URL}?count=openfda.brand_name.exact&limit={limit}"
        try:
            response = httpx.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    return [item["term"] for item in data["results"]]
        except Exception as e:
            print(f"Error discovering top drugs: {e}")
        return []


