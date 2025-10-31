def test_upload_report_with_patient(client):
    # First add patient
    patient_resp = client.post(
        "/cv/add_patient",
        json={"name": "Jane", "age": 35, "gender": "Female"}
    )
    assert patient_resp.status_code == 200
    patient_id = patient_resp.json()["id"]
    
    # Upload REAL minimal image
    with open("tests/test_image.png", "rb") as f:
        files = {"file": ("test_image.png", f, "image/png")}
        response = client.post(
            f"/cv/clean_and_analyze?patient_id={patient_id}",
            files=files
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == patient_id
    assert "log_id" in data