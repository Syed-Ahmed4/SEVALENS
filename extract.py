"""Rule-based field extraction and validation for scanned ID text."""
import re

DOB_RE = re.compile(r"\b(0[1-9]|[12]\d|3[01])[/-](0[1-9]|1[0-2])[/-]((?:19|20)\d{2})\b")
ID_RE = re.compile(r"\b(\d{4}) ?(\d{4}) ?(\d{4})\b")
PHONE_RE = re.compile(r"\b[6-9]\d{9}\b")
PIN_RE = re.compile(r"\b[1-9]\d{5}\b")


def mask_id(groups):
    """Keep only the last four digits of a 12-digit ID."""
    return "XXXX XXXX " + groups[2]


def extract_fields(lines):
    """Return a dict of fields found in a list of OCR text lines."""
    text = "\n".join(lines)
    fields = {}
    m = DOB_RE.search(text)
    if m:
        fields["date_of_birth"] = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = ID_RE.search(text)
    if m:
        fields["id_number_masked"] = mask_id(m.groups())
    m = PHONE_RE.search(text)
    if m:
        fields["phone"] = m.group(0)
    m = PIN_RE.search(text)
    if m:
        fields["pin_code"] = m.group(0)
    return fields
