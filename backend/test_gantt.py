
from fastapi.testclient import TestClient
from backend.main import app

def test_gantt_data():
    client = TestClient(app)
    # Fetch comparison data for Keytruda (id=1 probably) and Opdivo (id=2)
    # We need to find valid IDs first or guess.
    # Let's list products first.
    print("Fetching products...")
    res = client.get("/products")
    products = res.json()
    if len(products) < 1:
        print("No products found.")
        return
        
    ids = [p['id'] for p in products[:2]]
    query = "&".join([f"ids={i}" for i in ids])
    
    print(f"Comparing products: {ids}")
    res = client.get(f"/products/compare?{query}")
    data = res.json()
    
    print("\n--- Verifying Timeline Events ---")
    timeline = data.get('timeline_events', [])
    trials = [e for e in timeline if e['type'] == 'Trial Start']
    
    has_end_date = False
    for t in trials:
        print(f"Trial: {t['title']}, Start: {t['date']}, End: {t.get('end_date')}")
        if t.get('end_date'):
            has_end_date = True
            
    if has_end_date:
        print("\nSUCCESS: 'end_date' field present in response.")
    else:
        print("\nFAILURE: No 'end_date' found.")

if __name__ == "__main__":
    test_gantt_data()
