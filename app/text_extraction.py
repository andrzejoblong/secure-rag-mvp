import os
from pypdf import PdfReader
import pdfplumber

def extract_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [f.read()]

def extract_pdf(file_path):
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return pages

def extract_text(file_path):
    ext = file_path.split('.')[-1].lower()
    if ext == 'txt':
        return extract_txt(file_path)
    elif ext == 'pdf':
        return extract_pdf(file_path)
    else:
        raise ValueError('Unsupported file type')
