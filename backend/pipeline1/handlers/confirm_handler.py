import json
from services import update_patient_service
from api.response import success_response, error_response

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        patient_id = body.get('patient_id')
        updated_data = body.get('updated_data')

        if not patient_id or not updated_data:
            return error_response("Missing patient_id or updated_data")

        update_patient_service.update_patient(patient_id, updated_data)

        return success_response({"message": "Patient confirmed successfully"})
    except Exception as e:
        return error_response(str(e))
