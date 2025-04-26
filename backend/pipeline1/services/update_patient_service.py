import boto3
import os

def update_patient(patient_id, updated_data):
    db = boto3.resource('dynamodb')
    table = db.Table(os.environ['TABLE_NAME'])

    item = {
        'patient_id': patient_id,
        **updated_data,
        'status': 'verified'  # We mark it verified after confirmation
    }

    table.put_item(Item=item)
