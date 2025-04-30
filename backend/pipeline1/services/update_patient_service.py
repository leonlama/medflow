import boto3
import os

def update_patient(patient_id, updated_data):
    db = boto3.resource('dynamodb')
    table = db.Table(os.environ['TABLE_NAME'])

    table.update_item(
        Key={'patient_id': patient_id},
        UpdateExpression="SET #n = :n, birthday = :b, address = :a, allergies = :al, #s = :s",
        ExpressionAttributeNames={
            "#n": "name",
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":n": updated_data.get("name", ""),
            ":b": updated_data.get("birthday", ""),
            ":a": updated_data.get("address", ""),
            ":al": updated_data.get("allergies", ""),
            ":s": "verified"
        }
    )
