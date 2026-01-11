import httpx
from typing import Dict, Any, Optional

class PubChemConnector:
    """
    Connects to PubChem PUG REST API to fetch chemical properties.
    """
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"

    def get_compound_properties(self, drug_name: str) -> Optional[Dict[str, Any]]:
        # Properties to fetch
        props = "MolecularWeight,MolecularFormula,CanonicalSMILES,IsomericSMILES,IUPACName"
        url = f"{self.BASE_URL}/{drug_name}/property/{props}/JSON"
        
        try:
            # print(f"DEBUG: Fetching PubChem for {drug_name}")
            response = httpx.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "PropertyTable" in data and "Properties" in data["PropertyTable"]:
                    return data["PropertyTable"]["Properties"][0]
        except Exception as e:
            print(f"Error fetching PubChem data for {drug_name}: {e}")
            
        return None
