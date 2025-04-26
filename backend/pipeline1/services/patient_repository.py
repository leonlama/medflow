import boto3
import os

def create_or_update_patient(summary_data):
    db = boto3.resource("dynamodb")
    table = db.Table(os.environ['TABLE_NAME'])

    patient_id = summary_data.get("patient_id", "unknown")

    table.put_item(Item=summary_data | {"patient_id": patient_id})
