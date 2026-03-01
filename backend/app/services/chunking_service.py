import re


def clean_text(text: str) -> str:
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_words(text: str):
    return text.split()


def chunk_text(text: str, chunk_size: int = 250, overlap: int = 50):
    """
    Splits text into overlapping word chunks.
    chunk_size: number of words per chunk
    overlap: number of words overlapped between chunks
    """

    text = clean_text(text)
    words = split_into_words(text)

    chunks = []
    start = 0
    index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        if not chunk_words:
            break

        chunk = " ".join(chunk_words)

        chunks.append({
            "chunk_index": index,
            "chunk_text": chunk
        })

        index += 1
        start += chunk_size - overlap

    return chunks