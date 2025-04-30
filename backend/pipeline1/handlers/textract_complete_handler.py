import boto3
import os
import json
import logging
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
textract = boto3.client('textract')

patient_table = dynamodb.Table(os.environ['PATIENT_TABLE'])

def lambda_handler(event, context):
    logger.info(f"Received SNS event: {json.dumps(event)}")

    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        job_id = message['JobId']
        logger.info(f"Processing Textract JobId: {job_id}")

        patient = find_patient_by_job_id(job_id)
        if not patient:
            logger.error(f"No patient found for Textract JobId: {job_id}")
            continue

        patient_id = patient['patient_id']
        response = textract.get_document_analysis(JobId=job_id)
        extracted_fields = extract_fields(response, message)

        logger.info(f"Extracted fields for patient {patient_id}: {extracted_fields}")

        update_patient_record(patient_id, extracted_fields)

    return {
        'statusCode': 200,
        'body': json.dumps('Textract job processed successfully.')
    }

def find_patient_by_job_id(job_id):
    response = patient_table.scan(
        FilterExpression=Attr('textract_job_id').eq(job_id)
    )
    items = response.get('Items', [])
    return items[0] if items else None

def extract_fields(textract_response, message):
    fields = {
        "name": "",
        "birthday": "",
        "address": "",
        "allergies": "",
        "emergency_contact_name": "",
        "emergency_contact_phone": ""
    }

    blocks = textract_response.get('Blocks', [])
    key_map, value_map = {}, {}

    for block in blocks:
        if block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block['EntityTypes']:
                key_map[block['Id']] = block
            elif 'VALUE' in block['EntityTypes']:
                value_map[block['Id']] = block

    relationships = {
        key_id: rel['Ids']
        for key_id, block in key_map.items()
        if 'Relationships' in block
        for rel in block['Relationships']
        if rel['Type'] == 'VALUE'
    }

    for key_id, value_ids in relationships.items():
        key_text = get_text(key_map[key_id], blocks)
        for value_id in value_ids:
            value_text = get_text(value_map[value_id], blocks)
            normalized_key = key_text.lower().strip()

            if 'name' in normalized_key:
                fields['name'] = value_text
            elif 'birth' in normalized_key or 'geburt' in normalized_key:
                fields['birthday'] = value_text
            elif 'address' in normalized_key or 'adresse' in normalized_key:
                fields['address'] = value_text
            elif 'allerg' in normalized_key:
                fields['allergies'] = value_text
            elif 'emergency contact name' in normalized_key:
                fields['emergency_contact_name'] = value_text
            elif 'emergency contact phone' in normalized_key:
                fields['emergency_contact_phone'] = value_text

    fields["status"] = "pending_confirmation"
    fields["pdf_url"] = f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/{message['S3ObjectKey']}"
    return fields

def get_text(block, blocks):
    text = ''
    if 'Relationships' in block:
        for rel in block['Relationships']:
            if rel['Type'] == 'CHILD':
                for child_id in rel['Ids']:
                    child_block = next((b for b in blocks if b['Id'] == child_id), None)
                    if child_block and child_block['BlockType'] == 'WORD':
                        text += child_block['Text'] + ' '
    return text.strip()

def update_patient_record(patient_id, extracted_fields):
    update_expr = "SET "
    attr_values, attr_names = {}, {}

    non_empty = {k: v for k, v in extracted_fields.items() if v or k == "status"}

    for idx, (field, value) in enumerate(non_empty.items()):
        update_expr += f"#f{idx} = :v{idx}, "
        attr_names[f"#f{idx}"] = field
        attr_values[f":v{idx}"] = value

    update_expr = update_expr.rstrip(', ')

    if not attr_values:
        logger.info(f"No fields to update for patient {patient_id}")
        return

    try:
        patient_table.update_item(
            Key={'patient_id': patient_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values
        )
        logger.info(f"Successfully updated patient {patient_id}")
    except Exception as e:
        logger.error(f"Failed to update patient {patient_id}: {e}")
