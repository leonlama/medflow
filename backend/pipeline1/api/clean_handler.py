import json
import boto3
import os
import uuid
from utils import upload_parser, s3_utils
from api.response import error_response
from services import textract_service

def success_response(body):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # <-- super wichtig für Frontend
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    try:
        file_content, filename = upload_parser.parse_upload(event)
        bucket = os.environ['UPLOAD_BUCKET_NAME']

        # 1. Generate a new patient_id (UUID)
        patient_id = str(uuid.uuid4())
        today = filename.split('/')[0] if '/' in filename else "2025-04-26"  # fallback fallback
        original_file_path = f"uploads/{today}/{patient_id}.pdf"

        # 2. Upload to S3 with correct patient_id-based filename
        s3_utils.upload_file(bucket, original_file_path, file_content)

        # 3. Start Textract job
        job_id = textract_service.start_textract(bucket, original_file_path)

        # 4. OPTIONAL: Save an initial record to DynamoDB (if you want it immediately)
        db = boto3.resource("dynamodb")
        table = db.Table(os.environ['TABLE_NAME'])
        table.put_item(Item={
            "patient_id": patient_id,
            "original_file": original_file_path,
            "status": "processing",
            "textract_job_id": job_id,
            "upload_time": today,
            # rest of fields (name, birthday, etc) can come later
        })

        # 5. RETURN everything
        return success_response({
            "job_id": job_id,
            "patient_id": patient_id,
            "original_file": original_file_path
        })

    except Exception as e:
        return error_response(str(e))
