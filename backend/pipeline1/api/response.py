import json

def success_response(data):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "data": data
        })
    }

def error_response(message, status_code=400):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "success": False,
            "error": message
        })
    }
