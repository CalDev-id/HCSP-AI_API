from pdf2image import convert_from_bytes
import cv2
import numpy as np
import easyocr
import re

# OCR Reader (Indonesia + Inggris)
reader = easyocr.Reader(['id', 'en'])

def merge_lines(text: str) -> str:
    lines = text.split("\n")
    merged = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if (not line.endswith(('.', ':'))) and i < len(lines)-1:
            merged.append(line + " ")
        else:
            merged.append(line + "\n")
    return "".join(merged).strip()

def auto_corrections(text: str) -> str:
    corrections = {
        "lperubahan": "/ perubahan",
        "Il ": "II ",
        "IIl": "III",
        "Ill": "III",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text

async def ocr_pdf_easyocr(upload_file) -> list[dict]:
    # Baca bytes dari UploadFile
    pdf_bytes = await upload_file.read()

    # Convert PDF langsung dari bytes
    images = convert_from_bytes(pdf_bytes, dpi=300)

    all_pages = []
    for i, img in enumerate(images, start=1):
        open_cv_image = np.array(img)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR
        result = reader.readtext(thresh, detail=0)
        page_text = "\n".join(result)

        # Bersihkan
        page_text = re.sub(r'\n\s*\n+', '\n', page_text)
        page_text = re.sub(r'[ \t]+', ' ', page_text).strip()
        page_text = merge_lines(page_text)
        page_text = auto_corrections(page_text)

        all_pages.append({
            "page": i,
            "content": page_text
        })

    return all_pages
