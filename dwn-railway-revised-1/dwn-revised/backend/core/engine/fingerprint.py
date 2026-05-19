import hashlib, re

def fingerprint(html: str) -> str:
    normalized = re.sub(r'\s+', ' ', html)
    normalized = re.sub(r'<!--.*?-->', '', normalized, flags=re.DOTALL)
    normalized = re.sub(r'<script.*?</script>', '', normalized, flags=re.DOTALL|re.IGNORECASE)
    return hashlib.sha256(normalized.strip().lower().encode("utf-8","ignore")).hexdigest()
