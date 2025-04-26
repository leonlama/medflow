from services.textract_service import extract_text_from_file
from models.error_classes import ExtractionError

def extract_text(file_path):
    try:
        text = extract_text_from_file(file_path)
        if not text:
            raise ExtractionError("No text extracted from file.")
        return text
    except Exception as e:
        raise ExtractionError(f"Extraction failed: {e}")
