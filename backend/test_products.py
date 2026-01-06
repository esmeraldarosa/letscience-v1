
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_products():
    print("Testing /products/ endpoint...")
    response = client.get("/products/")
    
    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        print(response.text)
        return
        
    data = response.json()
    print(f"Products found: {len(data)}")
    if len(data) > 0:
        print("Sample:", data[0])
    else:
        print("WARNING: No products returned.")

if __name__ == "__main__":
    test_products()
