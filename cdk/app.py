from fastapi import FastAPI, HTTPException
import boto3
import os

app = FastAPI()

# ➡️ Connect to DynamoDB only if env var exists (i.e., on AWS)
dynamodb = None
patient_table = None

if "PATIENT_TABLE" in os.environ:
    dynamodb = boto3.resource('dynamodb')
    patient_table = dynamodb.Table(os.environ["PATIENT_TABLE"])

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    if not patient_table:
        # LOCAL TESTING: return a dummy patient
        return {
            "patient_id": patient_id,
            "name": "Test Patient",
            "birthday": "2000-01-01",
            "address": "123 Test Street",
            "allergies": "None",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "123-456-7890",
            "insurance_provider": "Test Insurance",
            "insurance_number": "INS123456789",
            "status": "mock"
        }

    try:
        response = patient_table.get_item(Key={"patient_id": patient_id})
        patient = response.get("Item")
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
