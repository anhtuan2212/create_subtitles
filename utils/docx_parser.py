### /project-root/utils/docx_parser.py
import re
from docx import Document

def clean_text(text):
    # Remove all punctuation except for quotes
    return re.sub(r"[^\w\s\"']", "", text)

def parse_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(clean_text(para.text.strip()))
    return full_text

