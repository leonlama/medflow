import base64
import uuid

class UploadError(Exception):
    pass

def parse_upload(event):
    """Parst Multipart-Upload und extrahiert Dateiinhalt und Dateinamen."""
    try:
        body = event['body']
        is_base64 = event.get('isBase64Encoded', False)
        content_type = event.get('headers', {}).get('content-type') or event.get('headers', {}).get('contentType')

        if not content_type:
            raise UploadError("Content-Type header is missing.")

        if is_base64:
            body = base64.b64decode(body)

        # TODO: Sauber Dateiname aus Content-Disposition Header parsen
        # Für jetzt nutzen wir dummy UUID name
        filename = f"{uuid.uuid4()}.pdf"

        return body, filename
    except Exception as e:
        raise UploadError(f"Upload parsing failed: {e}")
