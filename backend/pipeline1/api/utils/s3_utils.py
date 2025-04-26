import boto3
import os

def upload_file_to_s3(file_path, file_name):
    try:
        s3 = boto3.client('s3')
        bucket_name = os.environ["BUCKET_NAME"]
        s3.upload_file(file_path, bucket_name, file_name)
        return file_name
    except Exception as e:
        print(f"[ERROR] Failed to upload to S3: {str(e)}")
        raise
