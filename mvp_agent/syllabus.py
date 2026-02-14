import shutil
import subprocess


def _extract_text_pypdf(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _extract_text_pdftotext(pdf_path):
    if not shutil.which("pdftotext"):
        return ""
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            check=True,
            capture_output=True,
            text=True,
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""


def _extract_text_ocr(pdf_path, max_pages=5):
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        return ""
    images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=max_pages)
    parts = []
    for img in images:
        text = pytesseract.image_to_string(img)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def extract_syllabus_text(pdf_path, min_chars=200, ocr_mode="auto", max_pages=5):
    text = _extract_text_pypdf(pdf_path)
    method = "pypdf"
    if len(text) < min_chars:
        text = _extract_text_pdftotext(pdf_path)
        method = "pdftotext"
    if len(text) < min_chars and ocr_mode in ("auto", "force"):
        text = _extract_text_ocr(pdf_path, max_pages=max_pages)
        method = "ocr"
    if len(text) < min_chars and ocr_mode == "off":
        method = "none"
    return {
        "text": text,
        "method": method,
        "is_scanned": len(text) < min_chars,
    }
