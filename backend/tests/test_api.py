import sys, os
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app

client = TestClient(app)

def test_predict_endpoint():
    response = client.post("/symptoms/predict", json={"symptoms": "fever cough"})
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], str)
