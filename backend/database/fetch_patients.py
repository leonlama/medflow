import boto3
import json
import argparse

# CONFIG
TABLE_NAME = "Pipeline1Stack-PatientTable7407942F-13S8HRI08Y7G8"  # <-- insert your real table name here

# DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def fetch_all_patients():
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            print("No patient entries found.")
            return

        for idx, item in enumerate(items, 1):
            print(f"\n=== Patient {idx} ===")
            print(json.dumps(item, indent=4))

    except Exception as e:
        print(f"Error fetching patients: {str(e)}")

def fetch_patient_by_id(patient_id):
    try:
        response = table.get_item(Key={"patient_id": patient_id})
        item = response.get('Item')

        if not item:
            print(f"No patient found with ID: {patient_id}")
            return

        print(json.dumps(item, indent=4))

    except Exception as e:
        print(f"Error fetching patient: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch patient records from DynamoDB")
    parser.add_argument("--id", type=str, help="Patient ID to fetch")
    args = parser.parse_args()

    if args.id:
        fetch_patient_by_id(args.id)
    else:
        fetch_all_patients()
