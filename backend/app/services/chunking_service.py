def split_text(text, chunk_size=256, chunk_overlap=20):
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks