import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
patient_table = dynamodb.Table(os.environ['PATIENT_TABLE'])

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    query_params = event.get('queryStringParameters') or {}
    patient_id = query_params.get('id')
    name_filter = (query_params.get('name') or "").strip().lower()

    try:
        if patient_id:
            # Direct lookup by patient_id
            logger.info(f"Looking up patient by ID: {patient_id}")
            response = patient_table.get_item(Key={'patient_id': patient_id})
            patient = response.get('Item')
            if patient:
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                        "Access-Control-Allow-Headers": "Content-Type"
                    },
                    "body": json.dumps(patient)
                }
            else:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Patient not found"})
                }
        else:
            # Default behavior: scan all and optionally filter by name
            response = patient_table.scan()
            all_items = response.get('Items', [])

            if name_filter:
                logger.info(f"Filtering for name containing: {name_filter}")
                filtered_items = [
                    item for item in all_items
                    if 'name' in item and name_filter in item['name'].lower()
                ]
            else:
                filtered_items = all_items

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps(filtered_items)
            }

    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
