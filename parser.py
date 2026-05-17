import base64
import io
import PyPDF2
import docx

def extract_text(document: str) -> str:
    """
    Extracts text from a document. The document can be:
    - plain text
    - base64 encoded PDF
    - base64 encoded DOCX
    We use heuristics to detect the format or just try parsing.
    """
    document = document.strip()
    # Base64 strings do not contain spaces. If there's a space, it's plain text.
    if " " in document:
        return document

    try:
        decoded = base64.b64decode(document)
        # Check for PDF signature
        if decoded.startswith(b'%PDF'):
            pdf_file = io.BytesIO(decoded)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text.strip()
        # Check for DOCX (zip file signature)
        elif decoded.startswith(b'PK'):
            docx_file = io.BytesIO(decoded)
            doc = docx.Document(docx_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text.strip()
        else:
            # Maybe it's just base64 encoded text
            return decoded.decode('utf-8', errors='ignore')
    except Exception:
        # If it's not base64 or fails to decode, assume it's plain text
        return document
