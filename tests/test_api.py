from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tax_relief_endpoint():
    request_payload = {
        "profession": "Chef",
        "questions": "I clean my own uniform and buy kitchen knives"
    }
    
    response = client.post("/api/tax-relief", json=request_payload)
    assert response.status_code == 200
    assert "recommendations" in response.json() 