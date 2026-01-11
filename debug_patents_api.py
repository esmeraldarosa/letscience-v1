import httpx
import json

def test_patentsview(query="pembrolizumab"):
    url = "https://api.patentsview.org/patents/query"
    
    # Query for patents containing the text phrase
    q = {"_text_phrase": query}
    
    # Fields to return
    f = ["patent_number", "patent_title", "patent_abstract", "patent_date", "assignee_organization"]
    
    params = {
        "q": json.dumps(q),
        "f": json.dumps(f),
        "o": json.dumps({"per_page": 5})
    }
    
    print(f"DEBUG: Querying {url} for {query}")
    try:
        response = httpx.get(url, params=params, timeout=20)
        print(f"DEBUG: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # print(json.dumps(data, indent=2))
            
            patents = data.get("patents", [])
            print(f"Found {len(patents)} patents.")
            for p in patents:
                print(f" - {p.get('patent_number')}: {p.get('patent_title')}")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_patentsview()
