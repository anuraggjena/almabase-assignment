import re
import pdfplumber
import zipfile
import xml.etree.ElementTree as ET


ALLOWED_EXTENSIONS = (".pdf", ".txt", ".docx")


def extract_text_from_file(file, filename: str) -> str:
    filename = filename.lower()

    if not filename.endswith(ALLOWED_EXTENSIONS):
        raise ValueError("Unsupported file type. Allowed: PDF, TXT, DOCX.")

    if filename.endswith(".pdf"):
        raw_text = _extract_pdf(file)

    elif filename.endswith(".txt"):
        raw_text = _extract_txt(file)

    elif filename.endswith(".docx"):
        raw_text = _extract_docx(file)

    else:
        raise ValueError("Unsupported file type.")

    normalized = _normalize_text(raw_text)

    if not normalized.strip():
        raise ValueError("Uploaded file contains no readable text.")

    return normalized


# pdf extraction

def _extract_pdf(file) -> str:
    try:
        text_blocks = []

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_blocks.append(page_text)

        combined = "\n".join(text_blocks)

        if not combined.strip():
            raise ValueError("PDF contains no readable text.")

        return combined

    except Exception:
        raise ValueError("Invalid or corrupted PDF.")


# txt extraction

def _extract_txt(file) -> str:
    try:
        content = file.read().decode("utf-8", errors="ignore")

        if not content.strip():
            raise ValueError("TXT file is empty.")

        return content

    except Exception:
        raise ValueError("Invalid TXT file.")


# docx extraction

def _extract_docx(file) -> str:
    try:
        file.seek(0)
        with zipfile.ZipFile(file) as docx_zip:
            xml_content = docx_zip.read("word/document.xml")

        tree = ET.fromstring(xml_content)

        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

        paragraphs = tree.findall(".//w:p", namespace)

        text_blocks = []
        question_counter = 1

        for para in paragraphs:
            texts = para.findall(".//w:t", namespace)
            line = "".join([t.text for t in texts if t.text]).strip()

            if not line:
                continue

            num_pr = para.find(".//w:numPr", namespace)

            if num_pr is not None:
                text_blocks.append(f"{question_counter}. {line}")
                question_counter += 1
            else:
                text_blocks.append(line)

        combined = "\n".join(text_blocks)

        if not combined.strip():
            raise ValueError("DOCX contains no readable text.")

        return combined

    except Exception:
        raise ValueError("Invalid or corrupted DOCX file.")


# text normalization

def _normalize_text(text: str) -> str:
    """
    Cleans extracted text from PDF, DOCX, TXT.

    Fixes:
    - Broken PDF layout
    - Section bleed
    - Category bleed
    - Multiple questions on same line
    - Extra whitespace
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove Section headers completely
    text = re.sub(
        r"\n?\s*(Section|Part)\s+[IVXLC\d]+.*?\n",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # Fix PDF category bleed:
    text = re.sub(
        r"\?\s+[A-Z][A-Za-z\s&\-]{3,}(?=\n|$)",
        "?",
        text
    )

    # Ensure newline before numbered questions
    text = re.sub(
        r"\s+(Q?\d+[\.\)\:])",
        r"\n\1",
        text
    )

    # Remove duplicate blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()