import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List
from .models import DataSourceConnector, IntelligenceRecord, SourceType

class PubMedConnector(DataSourceConnector):
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def search(self, query: str) -> List[IntelligenceRecord]:
        results = []
        try:
            # 1. ESearh to get IDs
            search_url = f"{self.BASE_URL}/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax=5"
            response = httpx.get(search_url)
            data = response.json()
            ids = data.get("esearchresult", {}).get("idlist", [])
            
            if not ids:
                return []

            # 2. EFetch to get details
            ids_str = ",".join(ids)
            fetch_url = f"{self.BASE_URL}/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml"
            response = httpx.get(fetch_url)
            
            # Simple XML parsing (robust parsing would use a library)
            root = ET.fromstring(response.content)
            
            for article in root.findall(".//PubmedArticle"):
                title_node = article.find(".//ArticleTitle")
                abstract_node = article.find(".//AbstractText")
                pub_date_node = article.find(".//PubDate/Year")
                
                title = title_node.text if title_node is not None else "No Title"
                abstract = abstract_node.text if abstract_node is not None else "No Abstract"
                year = pub_date_node.text if pub_date_node is not None else str(datetime.now().year)
                
                # Try to find DOI
                doi = "N/A"
                for aid in article.findall(".//ArticleId"):
                    if aid.get("IdType") == "doi":
                        doi = aid.text
                        break

                record = IntelligenceRecord(
                    source_id=doi,
                    source_type=SourceType.ARTICLE,
                    title=title,
                    abstract=abstract,
                    publication_date=datetime(int(year), 1, 1),
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{doi}" if doi != "N/A" else None,
                    metadata={"doi": doi}
                )
                results.append(record)
                
        except Exception as e:
            print(f"Error fetching PubMed data: {e}")
            
        return results
