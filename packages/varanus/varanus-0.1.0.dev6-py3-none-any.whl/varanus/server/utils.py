def smart_trim(text: str, max_length: int = 80):
    trimmed = ""
    for word in text.split():
        if len(trimmed) + len(word) + 1 < max_length:
            trimmed = trimmed + " " + word
        else:
            return trimmed + "…"
    return trimmed
