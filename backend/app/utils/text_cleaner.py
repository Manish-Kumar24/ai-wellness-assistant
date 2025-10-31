import re
import unicodedata

def clean_text(raw_text: str) -> str:
    """
    Basic text normalization:
    - remove non-ASCII chars
    - collapse spaces/newlines
    - standardize units
    - lowercasing for consistency
    """
    # normalize unicode
    text = unicodedata.normalize("NFKD", raw_text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    # replace multiple newlines/tabs with space
    text = re.sub(r"[\r\n\t]+", " ", text)

    # collapse multiple spaces
    text = re.sub(r"\s{2,}", " ", text).strip()

    # standardize common units
    text = re.sub(r"mg\s*/\s*dL", "mg/dL", text, flags=re.I)
    text = re.sub(r"mmol\s*/\s*L", "mmol/L", text, flags=re.I)
    text = re.sub(r"%\s*", "%", text)

    # lowercase for uniformity
    text = text.lower()

    return text


def extract_structured_fields(cleaned_text: str) -> dict:
    """
    Extract common medical fields as key-value JSON
    Example: glucose, cholesterol, hemoglobin, etc.
    """
    structured = {}

    # Glucose
    match = re.search(r"(glucose)\D*(\d+\.?\d*)\s*(mg/dl|mmol/l)?", cleaned_text, re.I)
    if match:
        structured["glucose"] = {
            "value": float(match.group(2)),
            "unit": match.group(3) if match.group(3) else "unknown"
        }

    # Hemoglobin
    match = re.search(r"(hemoglobin|hgb)\D*(\d+\.?\d*)\s*(g/dl)?", cleaned_text, re.I)
    if match:
        structured["hemoglobin"] = {
            "value": float(match.group(2)),
            "unit": match.group(3) if match.group(3) else "unknown"
        }

    # Cholesterol
    match = re.search(r"(cholesterol)\D*(\d+\.?\d*)\s*(mg/dl)?", cleaned_text, re.I)
    if match:
        structured["cholesterol"] = {
            "value": float(match.group(2)),
            "unit": match.group(3) if match.group(3) else "unknown"
        }

    return structured
