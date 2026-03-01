import os
from groq import Groq


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Please configure environment variable."
        )

    return Groq(api_key=api_key)

# prompt builder

def build_prompt(question: str, chunks):

    context_blocks = []

    for chunk in chunks:
        clean_text = " ".join(chunk.chunk_text.split())
        context_blocks.append(clean_text)

    combined_context = "\n\n".join(context_blocks)

    prompt = f"""
You are answering a formal compliance questionnaire.

Rules:
1. Use ONLY the provided reference excerpts.
2. Answer ONLY the question asked.
3. Do NOT add extra details.
4. Do NOT speculate or infer.
5. Do NOT mention references or sources.

If the answer is NOT clearly supported in the reference excerpts,
you MUST respond with exactly:

Not found in references.

Do not modify that sentence.
Do not add explanation to it.

Question:
{question}

Reference Excerpts:
{combined_context}

Provide a clear, professional answer in full sentences.
"""

    return prompt.strip()

# answer generator

def generate_answer(question: str, chunks):
    if not chunks:
        return {
            "answer": "Not found in references.",
            "citations": []
        }

    client = get_groq_client()
    prompt = build_prompt(question, chunks)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1  # Lower = more grounded
    )

    answer_text = response.choices[0].message.content.strip()

    citations = []
    seen = set()

    for c in chunks:
        clean_text = " ".join(c.chunk_text.split())

        snippet = clean_text[:280]
        if len(clean_text) > 280:
            snippet += "..."

        key = (c.document.filename, c.chunk_index)

        if key not in seen:
            seen.add(key)

            citations.append({
                "chunk_index": c.chunk_index,
                "document_name": c.document.filename,
                "snippet": snippet
            })

    return {
        "answer": answer_text,
        "citations": citations
    }