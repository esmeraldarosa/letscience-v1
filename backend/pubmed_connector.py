import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

# Base URL for NCBI E-utilities
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

async def fetch_pubmed_articles(keyword: str, max_results: int = 5) -> List[Dict]:
    """
    Fetches scientific articles from PubMed for a given keyword.
    
    Args:
        keyword: Search term (e.g. "Apixaban")
        max_results: Maximum number of articles to return
        
    Returns:
        List of dictionaries with keys: title, doi, authors, date, desc (abstract/summary), url
    """
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Search (esearch)
            # Use retmode=json for easier parsing
            search_params = {
                "db": "pubmed",
                "term": f"{keyword}[Title/Abstract]", # Search in title/abstract for relevance
                "retmode": "json",
                "retmax": max_results,
                "sort": "date" # Get most recent
            }
            
            search_res = await client.get(f"{BASE_URL}/esearch.fcgi", params=search_params)
            search_res.raise_for_status()
            search_data = search_res.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # Step 2: Summary (esummary)
            # esummary also supports JSON
            ids_str = ",".join(id_list)
            summary_params = {
                "db": "pubmed",
                "id": ids_str,
                "retmode": "json"
            }
            
            summary_res = await client.get(f"{BASE_URL}/esummary.fcgi", params=summary_params)
            summary_res.raise_for_status()
            summary_data = summary_res.json()
            
            articles = []
            result_dict = summary_data.get("result", {})
            
            for uid in id_list:
                if uid not in result_dict:
                    continue
                    
                item = result_dict[uid]
                
                # Extract fields
                title = item.get("title", "No Title")
                
                # Authors
                authors_list = item.get("authors", [])
                authors_str = ", ".join([a.get("name", "") for a in authors_list])
                if len(authors_list) > 3:
                     authors_str = ", ".join([a.get("name", "") for a in authors_list[:3]]) + " et al."
                
                # DOI logic (scan articleids)
                doi = None
                for aid in item.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value")
                        break
                
                # Date
                pub_date_str = item.get("pubdate", "")
                # Convert date if possible, otherwise keep string or default
                # PubMed dates vary widely (e.g. "2023 Dec 1", "2023", "2023 Summer")
                # We'll try to extract YYYY-MM-DD or just use YYYY-01-01
                
                # Link
                url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                
                articles.append({
                    "title": title,
                    "doi": doi or "N/A",
                    "authors": authors_str,
                    "date": pub_date_str, # Client can parse or we can standardize
                    "desc": item.get("source", "") + "; " + (item.get("epubdate") or ""), # Summary usually doesn't have abstract, just source/journal
                    "url": url,
                    "source_id": uid # PubMed ID
                })
                
            return articles

        except Exception as e:
            print(f"Error fetching PubMed data: {e}")
            return []

if __name__ == "__main__":
    # Test script
    async def test():
        results = await fetch_pubmed_articles("Apixaban")
        print(f"Found {len(results)} articles:")
        for r in results:
            print(f"- {r['title']} ({r['date']})")
            
    asyncio.run(test())
