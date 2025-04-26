from backend.pipeline1.services.summarization_provider import summarize_text
from models.error_classes import SummarizationError

def summarize(text):
    try:
        summary = summarize_text(text)
        return summary
    except Exception as e:
        raise SummarizationError(f"Summarization failed: {e}")
