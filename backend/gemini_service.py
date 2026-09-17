# backend/gemini_service.py

import io
import pypdf

def extract_pdf_text(pdf_bytes: bytes, max_chars: int = 15000) -> str:
    """Reads PDF binary bytes using pypdf and returns formatted raw text."""
    if not pdf_bytes:
        return "No PDF binary content received."
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(f"--- PAGE {i+1} ---\n{text.strip()}")
        
        full_text = "\n\n".join(extracted_pages)
        return full_text[:max_chars] if full_text else "PDF loaded successfully, but no extractable text was found."
    except Exception as e:
        return f"Error reading PDF text: {str(e)}"