import re
from collections import Counter

# stopwords

STOPWORDS = {
    "is", "are", "the", "a", "an", "of", "in", "on", "for", "to",
    "and", "or", "with", "by", "as", "at", "from", "that",
    "this", "it", "be", "been", "was", "were", "does", "do",
    "did", "has", "have", "had", "what", "which", "who"
}

# tokenization

def tokenize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


# retrieval function

def retrieve_relevant_chunks(question: str, chunks, top_k=1):

    question_tokens = tokenize(question)

    if not question_tokens:
        return [], 0.0

    question_token_set = set(question_tokens)

    scored = []

    for chunk in chunks:
        chunk_tokens = tokenize(chunk.chunk_text)
        chunk_token_set = set(chunk_tokens)

        overlap = question_token_set & chunk_token_set
        overlap_count = len(overlap)

        # Require minimum overlap
        if overlap_count < 2:
            continue

        # Phrase bonus (strong signal)
        phrase_bonus = 0
        if question.lower() in chunk.chunk_text.lower():
            phrase_bonus = 2

        coverage_ratio = overlap_count / len(question_token_set)

        final_score = coverage_ratio + (phrase_bonus * 0.1)

        scored.append((final_score, overlap_count, chunk))

    if not scored:
        return [], 0.0

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    selected = scored[:top_k]
    selected_chunks = [item[2] for item in selected]

    best_ratio = selected[0][0]

    confidence = round(min(best_ratio * 100, 95.0), 2)

    if confidence < 45:
        return [], 0.0

    return selected_chunks, confidence