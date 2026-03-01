import re


QUESTION_PATTERN = re.compile(
    r"""
    (?:^|\n)
    \s*
    (
        (?:Q?\d{1,3})        # 1, 12, Q1
        |
        (?:[IVXLCDM]+)       # Roman numerals
        |
        (?:[A-Z])            # A, B
        |
        (?:[a-z])            # a, b
    )
    [\.\)\:]
    \s+
    """,
    re.VERBOSE | re.MULTILINE,
)


def parse_numbered_questions(text: str):

    if not text or not text.strip():
        return []

    matches = list(QUESTION_PATTERN.finditer(text))

    if not matches:
        return []

    questions = []

    for i in range(len(matches)):

        start = matches[i].end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        question_text = text[start:end].strip()

        # Collapse internal whitespace
        question_text = " ".join(question_text.split())

        # Safety filter
        if len(question_text) < 10:
            continue

        questions.append({
            "order": len(questions),
            "text": question_text
        })

    return questions