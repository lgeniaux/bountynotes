def normalize_text(content: str) -> str:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    return normalized
