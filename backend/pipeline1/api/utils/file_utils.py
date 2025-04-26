import base64

def save_file_to_tmp(base64_content, file_name):
    try:
        decoded_file = base64.b64decode(base64_content)
        tmp_path = f"/tmp/{file_name}"
        with open(tmp_path, "wb") as f:
            f.write(decoded_file)
        return tmp_path
    except Exception as e:
        print(f"[ERROR] Failed to save file to /tmp: {str(e)}")
        raise
